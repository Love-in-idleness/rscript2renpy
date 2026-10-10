# Shared CodeX UI. Positions and available sprites come from grps/*/.meta.xml.
default persistent.rscript_textbox_opacity = 1.0
define rscript_grps_language_layouts = {}

init python:
    def rscript_layouts():
        layouts = dict(rscript_grps_layout)
        layouts.update(rscript_ui.get("layouts", {}))
        for folder, patch in rscript_grps_language_layouts.get(_preferences.language, {}).items():
            base = layouts.get(folder, {})
            layouts[folder] = dict(base, **patch)
            for field in ("items", "controls"):
                layouts[folder][field] = dict(base.get(field, {}), **patch.get(field, {}))
        return layouts

    def rscript_ui_image(folder, name):
        source = rscript_layouts().get(folder, {}).get("images", {}).get(name)
        if source is None:
            return rscript_image_path("grps/%s/%s.png" % (folder, name))
        path, crop = source
        image = rscript_image_path(path)
        return Crop(crop, image) if crop else image

    def rscript_ui_action(spec):
        kind, args = spec[0], spec[1:]
        if rscript_ui_sensitive(kind) is False:
            return NullAction()
        if kind == "preference":
            return rscript_preference_action(*args)
        if kind == "effects":
            if _preferences.language in rscript_wiki_keywords:
                return SetField(persistent, "rscript_wiki_mode", args[0])
            return Preference("transitions", "all" if args[0] else "none")
        if kind == "voice_stop":
            return SetField(persistent, "rscript_stop_voice_on_advance", args[0])
        return {
            "choice_back": rscript_rev_action,
            "rollback": Rollback, "rollforward": RollForward,
            "fast_skip": lambda: Skip(fast=True), "skip": Skip,
            "auto": lambda: [Function(rscript_ensure_auto_delay), Preference("auto-forward", "toggle")],
            "hide": HideInterface, "voice": lambda: Function(rscript_replay_voice),
            "save": lambda: ShowMenu("save"), "load": lambda: ShowMenu("load"),
            "quick_save": QuickSave, "quick_load": QuickLoad,
            "preferences": lambda: Function(rscript_open_game_menu),
            "fonts": lambda: Show("rscript_font_picker"), "close": Return,
            "title": rscript_main_menu_action, "quit": rscript_quit_action,
        }[kind]()

    def rscript_ui_sensitive(kind):
        if kind in ("save", "load", "quick_save", "quick_load"):
            return rscript_permission("save")
        if kind in ("rollback", "choice_back"):
            return rscript_permission("roll")
        if kind == "preferences":
            return bool(menu_enabled) and not rscript_touch_locked()
        if kind == "voice":
            return rscript_last_voice is not None
        return None  # Preserve the native action's sensitivity.

    rscript_previous_menu_arguments = config.menu_arguments_callback

    def rscript_menu_arguments(*args, **kwargs):
        # Both game lowerers emit native menus; record the actual menu statement.
        if not renpy.predicting():
            store.jump_back_point = renpy.game.log.current.identifier
        if rscript_previous_menu_arguments is not None:
            return rscript_previous_menu_arguments(*args, **kwargs)
        return args, kwargs

    config.menu_arguments_callback = rscript_menu_arguments

    def rscript_rev_action(enabled=True):
        # The native action also disables expired or missing rollback targets.
        return RollbackToIdentifier(store.jump_back_point if enabled and rscript_permission("roll") else None)

    def rscript_save_json(data):
        data["rscript_dt1"] = int(store._r[1])
        if rscript_ui.get("slot_images"):
            data["rscript_slot_images"] = rscript_ui["slot_images"]
            data["rscript_slot_zoom"] = rscript_ui.get("slot_image_zoom", 1.0)

    config.save_json_callbacks.append(rscript_save_json)

    def rscript_replay_voice():
        if store.rscript_last_voice:
            renpy.music.play(store.rscript_last_voice, channel="rscript_voice",
                             loop=False, if_changed=False)

    def rscript_select_font(path):
        if path not in rscript_fonts():
            return
        persistent.rscript_text_font = path
        renpy.save_persistent()

screen rscript_font_picker():
    modal True
    zorder 200
    key "game_menu" action Hide("rscript_font_picker")
    $ folder = "fontwnd" if "fontwnd" in rscript_layouts() else "fontwnd_ord"
    $ layout = rscript_layouts().get(folder)
    if layout and "bg" in layout["items"]:
        fixed:
            xysize layout["size"]
            xalign 0.5
            yalign 0.5
            $ bg = layout["items"]["bg"]
            add rscript_image_path("grps/%s/bg.png" % folder) pos bg[:2]
            $ row = layout["items"].get("list", (20, 30, 300, 20))
            $ footer = layout["items"].get("exit", (0, layout["size"][1] - 40, 0, 0))
            viewport:
                pos row[:2]
                xsize layout["size"][0] - row[0] - 30
                ysize max(row[3], footer[1] - row[1] - 12)
                mousewheel True
                draggable True
                vbox:
                    spacing 2
                    for path in rscript_fonts():
                        textbutton path.rsplit("/", 1)[-1]:
                            background rscript_image_path("grps/%s/list.png" % folder)
                            hover_background (rscript_image_path("grps/%s/list_f.png" % folder) if "list_f" in layout["items"] else None)
                            selected_background (rscript_image_path("grps/%s/list_f.png" % folder) if "list_f" in layout["items"] else None)
                            text_size min(18, row[3])
                            padding (2, 0)
                            selected path == rscript_current_font()
                            action Function(rscript_select_font, path)
            use rscript_grps_button(folder, "prev", Function(rscript_cycle_font, -1))
            use rscript_grps_button(folder, "next", Function(rscript_cycle_font, 1))
            use rscript_grps_button(folder, "exit", Hide("rscript_font_picker"))
    else:
        frame:
            align (0.5, 0.5)
            vbox:
                for path in rscript_fonts():
                    textbutton path.rsplit("/", 1)[-1] action Function(rscript_select_font, path)
                textbutton "Back" action Hide("rscript_font_picker")

screen rscript_grps_button(folder, name, button_action, enabled=True, selected=None):
    $ items = rscript_layouts().get(folder, {}).get("items", {})
    $ item = items.get(name)
    if item:
        $ idle_image = rscript_ui_image(folder, name)
        $ focused_image = (rscript_ui_image(folder, name + "_f")
                           if name + "_f" in items else idle_image)
        $ focused = items.get(name + "_f", item)
        $ focused_display = Transform(focused_image,
                                      xoffset=focused[0] - item[0],
                                      yoffset=focused[1] - item[1])
        $ plain_selected = (folder in rscript_ui.get("selected_plain_folders", ()) and (name.startswith(("scm_", "msp_", "msk_")) or name.endswith(("_on", "_off"))))
        $ disabled_name = name + ("_off" if name + "_off" in items else "_c")
        $ disabled_image = (rscript_ui_image(folder, disabled_name)
                            if disabled_name in items else idle_image)
        imagebutton:
            idle (focused_display if plain_selected else idle_image)
            hover focused_display
            selected_idle (idle_image if plain_selected else focused_display)
            selected_hover (idle_image if plain_selected else focused_display)
            insensitive disabled_image
            selected selected
            activate_sound rscript_ui.get("activate_sound", {}).get(folder)
            xpos item[0]
            ypos item[1]
            sensitive enabled
            action button_action

style rscript_volume_bar is bar:
    left_bar Solid("#00000000")
    right_bar Solid("#00000000")
    hover_left_bar Solid("#00000000")
    hover_right_bar Solid("#00000000")

screen preferences(title_mode=False):
    tag menu
    modal True
    key "game_menu" action Return()
    $ layout = rscript_layouts().get("confscrn")
    if layout and layout.get("background_dim", 0):
        add Solid("#000000") alpha layout["background_dim"]
    if rscript_ui.get("game_text_settings", True):
        textbutton "Text Settings":
            xalign 0.5
            yalign 0.97
            action ShowMenu("rscript_text_preferences")
    if layout and "bg" in layout["items"]:
        fixed:
            xysize layout["size"]
            xalign 0.5
            yalign 0.5
            $ bg = layout["items"]["bg"]
            add rscript_ui_image("confscrn", "bg") xpos bg[0] ypos bg[1]

            for name, spec in layout.get("controls", {}).items():
                if not (title_mode and spec[0] in ("save", "load", "close", "quit")):
                    if not (title_mode and spec[0] == "effects" and _preferences.language in rscript_wiki_keywords):
                        use rscript_grps_button("confscrn", name, rscript_ui_action(spec),
                                                 enabled=rscript_ui_sensitive(spec[0]))
            if "font" in layout["items"]:
                $ field = layout["items"].get("font_txt", layout["items"]["font"])
                text rscript_font_name():
                    pos field[:2]
                    xsize field[2]
                    size min(18, field[3])
                    color "#ffffff"
                    layout "nobreak"

            for prefix, setting in (("bgm", "music volume"),
                                    ("sef", "sound volume"),
                                    ("voc", "voice volume"),
                                    ("auto", "auto-forward time")):
                $ track = layout["items"].get(prefix + "_lev")
                $ thumb = layout["items"].get(prefix + "_vol")
                if track and thumb:
                    bar:
                        style "rscript_volume_bar"
                        value Preference(setting)
                        base_bar Solid("#00000000")
                        thumb rscript_ui_image("confscrn", prefix + "_vol")
                        hover_thumb (rscript_ui_image("confscrn", prefix + "_vol_f")
                                     if prefix + "_vol_f" in layout["items"] else
                                     rscript_ui_image("confscrn", prefix + "_vol"))
                        xpos track[0]
                        ypos track[1]
                        xsize track[2]
                        ysize track[3]
                        # AFM is a delay: left is fast, right is slow.
                        bar_invert False

    else:
        frame:
            xalign 0.5
            yalign 0.5
            vbox:
                textbutton "Music" action Preference("music mute", "toggle")
                textbutton "Sound" action Preference("sound mute", "toggle")
                textbutton "Voice" action Preference("voice mute", "toggle")
                textbutton "Save" action rscript_ui_action(("save",)) sensitive rscript_permission("save")
                textbutton "Load" action rscript_ui_action(("load",)) sensitive rscript_permission("save")
                textbutton "Main Menu" action rscript_main_menu_action()
                textbutton "Quit" action rscript_quit_action()
                textbutton "Back" action Return()

screen rscript_compane():
    $ layout = rscript_layouts().get("compane")
    $ boxpos = rscript_textbox_state().get("box_pos", (0, config.screen_height - rscript_ui.get("textbox_size", (800, 138))[1]))
    if layout and not (rscript_ui.get("compane_hide_auto", False) and _preferences.afm_enable):
        fixed:
            xysize layout["size"]
            if rscript_compane_position is not None:
                anchor (0.0, 0.0)
                # cmploc is in screen coordinates; this pane is inside say.
                pos (rscript_compane_position[0] - boxpos[0], rscript_compane_position[1] - boxpos[1])
            else:
                xalign 1.0
                yalign 1.0
            $ items = layout["items"]
            if "bg" in items and not rscript_ui.get("compane_bar_background", False):
                $ bg = items["bg"]
                add rscript_ui_image("compane", "bg") xpos bg[0] ypos bg[1]
            $ track = rscript_ui.get("compane_track", items.get("slide_lev"))
            if track and "slide" in items:
                if track[3] > track[2]:
                    vbar:
                        style "rscript_volume_bar"
                        value FieldValue(persistent, "rscript_textbox_opacity", range=1.0)
                        base_bar (rscript_image_path("grps/compane/bg.png") if rscript_ui.get("compane_bar_background", False) else Solid("#00000000"))
                        thumb rscript_ui_image("compane", "slide")
                        hover_thumb rscript_ui_image("compane", "slide_f" if "slide_f" in items else "slide")
                        thumb_offset (2 if rscript_ui.get("compane_bar_background", False) else 0)
                        bar_invert rscript_ui.get("compane_invert", False)
                        xpos track[0]
                        ypos track[1]
                        xsize track[2]
                        ysize track[3]
                else:
                    bar:
                        style "rscript_volume_bar"
                        value FieldValue(persistent, "rscript_textbox_opacity", range=1.0)
                        base_bar (rscript_image_path("grps/compane/bg.png") if rscript_ui.get("compane_bar_background", False) else Solid("#00000000"))
                        thumb rscript_ui_image("compane", "slide")
                        hover_thumb rscript_ui_image("compane", "slide_f" if "slide_f" in items else "slide")
                        thumb_offset (2 if rscript_ui.get("compane_bar_background", False) else 0)
                        bar_invert rscript_ui.get("compane_invert", False)
                        xpos track[0]
                        ypos track[1]
                        xsize track[2]
                        ysize track[3]
            for name, spec in layout.get("controls", {}).items():
                if spec[0] != "voice" or rscript_ui_sensitive("voice"):
                    use rscript_grps_button("compane", name, rscript_ui_action(spec),
                                             enabled=rscript_ui_sensitive(spec[0]))

screen rscript_choice(items, prompt=None):
    modal True
    key "game_menu" action Function(rscript_open_game_menu)
    key "rollback" action rscript_ui_action(("rollback",))
    vbox:
        xalign 0.5
        yalign rscript_ui.get("choice_yalign", 0.42)
        spacing rscript_ui.get("choice_spacing", 4)
        if prompt:
            $ prompt_folder, prompt_text = rscript_menu_panel(prompt, "sel_q", rscript_dynamic_skin)
            if prompt_folder:
                $ question = rscript_layouts()[prompt_folder]
                fixed:
                    xysize rscript_ui.get("prompt_size", question["size"])
                    $ body = question["items"]["body"]
                    $ textpos = rscript_ui.get("prompt_text_pos", question["items"].get("text", (20, 10)))
                    add rscript_ui_image(prompt_folder, "body"):
                        xpos (0 if rscript_ui.get("choice_center_art", False) else body[0])
                        ypos (0 if rscript_ui.get("choice_center_art", False) else body[1])
                    text rscript_menu_text(prompt_text):
                        xpos textpos[0]
                        ypos rscript_ui.get("prompt_text_yalign", textpos[1])
                        yanchor rscript_ui.get("prompt_text_yalign", 0.0)
                        color rscript_ui.get("prompt_text_color", "#ffffff")
                        font rscript_current_font()
                        size rscript_ui.get("prompt_text_size", gui.text_size)
            else:
                text rscript_menu_text(prompt_text) xalign 0.5 color "#ffffff" font rscript_current_font()
        for item in items:
            if item.action is not None:
                $ selected_folder, caption = rscript_menu_panel(item.caption, "sel_a", rscript_dynamic_skin)
                if selected_folder:
                    $ answer = rscript_layouts()[selected_folder]
                    fixed:
                        xysize rscript_ui.get("choice_size", answer["size"])
                        $ body = answer["items"]["body"]
                        $ textpos = rscript_ui.get("choice_text_pos", answer["items"].get("text", (20, 10)))
                        imagebutton:
                            idle rscript_ui_image(selected_folder, "body")
                            hover (rscript_ui_image(selected_folder, "body_f")
                                   if "body_f" in answer["items"] else
                                   rscript_ui_image(selected_folder, "body"))
                            focus_mask True
                            xpos (0.5 if rscript_ui.get("choice_center_art", False) else body[0])
                            ypos (0.5 if rscript_ui.get("choice_center_art", False) else body[1])
                            xanchor (0.5 if rscript_ui.get("choice_center_art", False) else 0.0)
                            yanchor (0.5 if rscript_ui.get("choice_center_art", False) else 0.0)
                            action item.action
                        if caption:
                            text rscript_menu_text(caption):
                                xpos textpos[0]
                                ypos rscript_ui.get("choice_text_yalign", textpos[1])
                                yanchor rscript_ui.get("choice_text_yalign", 0.0)
                                color "#ffffff"
                                font rscript_current_font()
                                size rscript_ui.get("choice_text_size", gui.text_size)
                                outlines rscript_ui.get("choice_outlines", [])
                else:
                    textbutton rscript_menu_text(caption) action item.action text_font rscript_current_font()

screen save():
    tag menu
    use rscript_file_slots("save")

screen load():
    tag menu
    use rscript_file_slots("load")

screen rscript_file_slots(mode):
    modal True
    key "game_menu" action Return()
    $ layout = rscript_layouts().get("savescrn")
    if layout and "bg_" + mode in layout["items"]:
        fixed:
            xysize layout["size"]
            xalign 0.5
            yalign 0.5
            $ items = layout["items"]
            $ bg = items["bg_" + mode]
            $ slot_config = rscript_layouts().get("saveconf", {})
            $ slot_layout = slot_config.get("items", {})
            add rscript_ui_image("savescrn", "bg_" + mode) xpos bg[0] ypos bg[1]
            for index in range(10):
                $ item = items.get(str(index))
                if item:
                    $ slot = index + 1
                    $ slot_action = FileSave(slot) if mode == "save" else FileLoad(slot)
                    button:
                        xpos item[0]
                        ypos item[1]
                        xsize rscript_ui.get("slot_size", item[2:])[0]
                        ysize rscript_ui.get("slot_size", item[2:])[1]
                        background None
                        hover_background Solid("#ffffff20")
                        padding (0, 0)
                        action slot_action
                        if "icon" in slot_layout:
                            add rscript_ui_image("saveconf", "icon") pos slot_layout["icon"][:2]
                        if "new" in slot_layout and FileNewest(slot):
                            add rscript_ui_image("saveconf", "new") pos slot_layout["new"][:2]
                        $ dt1_image = rscript_slot_image(slot)
                        if dt1_image:
                            add dt1_image
                        elif FileLoadable(slot):
                            $ preview = slot_layout.get("thmb", (4, 4, 92, item[3] - 8))
                            add FileScreenshot(slot):
                                pos preview[:2]
                                xysize preview[2:]
                        if FileLoadable(slot):
                            $ date_pos = rscript_ui.get("slot_date_pos", slot_layout.get("date", (0.98, 0.98)))
                            text FileTime(slot, slot_config.get("date_format", "%Y/%m/%d %H:%M")):
                                xpos date_pos[0]
                                ypos date_pos[1]
                                xanchor (0.0 if "slot_date_pos" in rscript_ui or "date" in slot_layout else 0.98)
                                yanchor (0.0 if "slot_date_pos" in rscript_ui or "date" in slot_layout else 0.98)
                                color rscript_ui.get("slot_date_color", "#ffffff")
                                size slot_config.get("date_size", 12)
                                outlines slot_config.get("date_outlines", [] if "slot_date_pos" in rscript_ui else [(1, "#000000", 0, 0)])
            use rscript_grps_button("savescrn", "prev",
                                     FilePagePrevious(max=10, wrap=layout.get("page_wrap", True), auto=False, quick=False))
            use rscript_grps_button("savescrn", "next",
                                     FilePageNext(max=10, wrap=layout.get("page_wrap", True), auto=False, quick=False))
            if "number" in items:
                $ number = items["number"]
                $ page = FileCurrentPage()
                $ page_image = rscript_page_image(page)
                if page_image:
                    fixed:
                        pos number[:2]
                        xysize number[2:]
                        add page_image xalign 0.5 yalign 0.5
                else:
                    text page xpos number[0] ypos number[1] color "#ffffff"
            use rscript_grps_button("savescrn", "exit", Return())
    else:
        frame:
            xalign 0.5
            yalign 0.5
            vbox:
                for slot in range(1, 11):
                    $ slot_action = FileSave(slot) if mode == "save" else FileLoad(slot)
                    textbutton ("Save %d" % slot if mode == "save" else "Load %d" % slot):
                        action slot_action
                textbutton "Back" action Return()
