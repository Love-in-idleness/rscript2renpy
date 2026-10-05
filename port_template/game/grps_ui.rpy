# Shared CodeX UI. Positions and available sprites come from grps/*/.meta.xml.
default persistent.rscript_textbox_opacity = 1.0
default rscript_last_voice = None

init python:
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
        return RollbackToIdentifier(store.jump_back_point if enabled else None)

    def rscript_save_json(data):
        data["rscript_dt1"] = int(store._r[1])

    config.save_json_callbacks.append(rscript_save_json)

    def rscript_replay_voice():
        if store.rscript_last_voice:
            renpy.music.play(store.rscript_last_voice, channel="rscript_voice",
                             loop=False, if_changed=False)

screen rscript_grps_button(folder, name, button_action, enabled=True, selected=None):
    $ items = rscript_grps_layout.get(folder, {}).get("items", {})
    $ item = items.get(name)
    if item:
        $ idle_image = "images/grps/%s/%s.png" % (folder, name)
        $ focused_image = ("images/grps/%s/%s_f.png" % (folder, name)
                           if name + "_f" in items else idle_image)
        $ focused = items.get(name + "_f", item)
        $ focused_display = Transform(focused_image,
                                      xoffset=focused[0] - item[0],
                                      yoffset=focused[1] - item[1])
        $ plain_selected = (folder in rscript_ui.get("selected_plain_folders", ()) and (name.startswith(("scm_", "msp_", "msk_")) or name.endswith(("_on", "_off"))))
        $ disabled_name = name + ("_off" if name + "_off" in items else "_c")
        $ disabled_image = ("images/grps/%s/%s.png" % (folder, disabled_name)
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
    $ layout = rscript_grps_layout.get("confscrn")
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
            add "images/grps/confscrn/bg.png" xpos bg[0] ypos bg[1]

            for name, setting, value in (
                    ("scm_ful", "display", "fullscreen"),
                    ("scm_wnd", "display", "window"),
                    ("bgm_on", "music mute", "disable"),
                    ("bgm_off", "music mute", "enable"),
                    ("sef_on", "sound mute", "disable"),
                    ("sef_off", "sound mute", "enable"),
                    ("voc_on", "voice mute", "disable"),
                    ("voc_off", "voice mute", "enable"),
                    ("msp_slw", "text speed", 25),
                    ("msp_nom", "text speed", 75),
                    ("msp_now", "text speed", 0),
                    ("msk_on", "skip", "all"),
                    ("msk_off", "skip", "seen")):
                use rscript_grps_button("confscrn", name,
                                         rscript_preference_action(setting, value))
            if _preferences.language in rscript_wiki_keywords:
                if not title_mode:
                    use rscript_grps_button("confscrn", "gef_on",
                        Function(rscript_set_wiki, True), selected=persistent.rscript_wiki_mode)
                    use rscript_grps_button("confscrn", "gef_off",
                        Function(rscript_set_wiki, False), selected=not persistent.rscript_wiki_mode)
            else:
                use rscript_grps_button("confscrn", "gef_on", Preference("transitions", "all"))
                use rscript_grps_button("confscrn", "gef_off", Preference("transitions", "none"))
            use rscript_grps_button("confscrn", "vocst_on",
                                     SetField(persistent, "rscript_stop_voice_on_advance", True))
            use rscript_grps_button("confscrn", "vocst_off",
                                     SetField(persistent, "rscript_stop_voice_on_advance", False))

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
                        thumb "images/grps/confscrn/%s_vol.png" % prefix
                        hover_thumb ("images/grps/confscrn/%s_vol_f.png" % prefix
                                     if prefix + "_vol_f" in layout["items"] else
                                     "images/grps/confscrn/%s_vol.png" % prefix)
                        xpos track[0]
                        ypos track[1]
                        xsize track[2]
                        ysize track[3]
                        bar_invert prefix == "auto"

            if not title_mode:
                use rscript_grps_button("confscrn", "save", ShowMenu("save"), save_enabled)
                use rscript_grps_button("confscrn", "load", ShowMenu("load"), save_enabled)
            use rscript_grps_button("confscrn", "title", MainMenu(confirm=False))
            if not title_mode:
                use rscript_grps_button("confscrn", "exit", Quit(confirm=rscript_ui.get("quit_confirm", True)))
                use rscript_grps_button("confscrn", "close", Return())
    else:
        frame:
            xalign 0.5
            yalign 0.5
            vbox:
                textbutton "Music" action Preference("music mute", "toggle")
                textbutton "Sound" action Preference("sound mute", "toggle")
                textbutton "Voice" action Preference("voice mute", "toggle")
                textbutton "Save" action ShowMenu("save")
                textbutton "Load" action ShowMenu("load")
                textbutton "Back" action Return()

screen rscript_compane():
    $ layout = rscript_grps_layout.get("compane")
    if layout and not (rscript_ui.get("compane_hide_auto", False) and _preferences.afm_enable):
        fixed:
            xysize layout["size"]
            xalign 1.0
            yalign 1.0
            $ items = layout["items"]
            if "bg" in items and not rscript_ui.get("compane_bar_background", False):
                $ bg = items["bg"]
                add "images/grps/compane/bg.png" xpos bg[0] ypos bg[1]
            $ track = rscript_ui.get("compane_track", items.get("slide_lev"))
            if track and "slide" in items:
                if track[3] > track[2]:
                    vbar:
                        value FieldValue(persistent, "rscript_textbox_opacity", range=1.0)
                        base_bar ("images/grps/compane/bg.png" if rscript_ui.get("compane_bar_background", False) else Solid("#00000000"))
                        thumb "images/grps/compane/slide.png"
                        hover_thumb ("images/grps/compane/slide_f.png" if "slide_f" in items else "images/grps/compane/slide.png")
                        thumb_offset (2 if rscript_ui.get("compane_bar_background", False) else 0)
                        bar_invert rscript_ui.get("compane_invert", False)
                        xpos track[0]
                        ypos track[1]
                        xsize track[2]
                        ysize track[3]
                else:
                    bar:
                        value FieldValue(persistent, "rscript_textbox_opacity", range=1.0)
                        base_bar ("images/grps/compane/bg.png" if rscript_ui.get("compane_bar_background", False) else Solid("#00000000"))
                        thumb "images/grps/compane/slide.png"
                        hover_thumb ("images/grps/compane/slide_f.png" if "slide_f" in items else "images/grps/compane/slide.png")
                        thumb_offset (2 if rscript_ui.get("compane_bar_background", False) else 0)
                        bar_invert rscript_ui.get("compane_invert", False)
                        xpos track[0]
                        ypos track[1]
                        xsize track[2]
                        ysize track[3]
            use rscript_grps_button("compane", "rev", rscript_rev_action(not rscript_touch_locked()), enabled=None)
            use rscript_grps_button("compane", "bak", Rollback(), enabled=roll_enabled and not rscript_touch_locked())
            use rscript_grps_button("compane", "fow", RollForward())
            use rscript_grps_button("compane", "next", Skip(fast=True))
            use rscript_grps_button("compane", "auto", [Function(rscript_ensure_auto_delay), Preference("auto-forward", "toggle")])
            use rscript_grps_button("compane", "hide", HideInterface())
            use rscript_grps_button("compane", "voc", Function(rscript_replay_voice),
                                     rscript_last_voice is not None)

screen rscript_choice(items, prompt=None):
    modal True
    key "game_menu" action Function(rscript_open_game_menu)
    key "rollback" action Rollback()
    $ answer_folder = next((name for name in sorted(rscript_grps_layout)
                            if name.startswith("sel_a")), None)
    $ prompt_folder = next((name for name in sorted(rscript_grps_layout)
                            if name.startswith("sel_q")), None)
    vbox:
        xalign 0.5
        yalign rscript_ui.get("choice_yalign", 0.42)
        spacing rscript_ui.get("choice_spacing", 4)
        if prompt:
            if prompt_folder:
                $ question = rscript_grps_layout[prompt_folder]
                fixed:
                    xysize rscript_ui.get("prompt_size", question["size"])
                    $ body = question["items"]["body"]
                    $ textpos = rscript_ui.get("prompt_text_pos", question["items"].get("text", (20, 10)))
                    add "images/grps/%s/body.png" % prompt_folder:
                        xpos (0 if rscript_ui.get("choice_center_art", False) else body[0])
                        ypos (0 if rscript_ui.get("choice_center_art", False) else body[1])
                    text rscript_menu_text(prompt):
                        xpos textpos[0]
                        ypos rscript_ui.get("prompt_text_yalign", textpos[1])
                        yanchor rscript_ui.get("prompt_text_yalign", 0.0)
                        color rscript_ui.get("prompt_text_color", "#ffffff")
                        font rscript_current_font()
                        size rscript_ui.get("prompt_text_size", gui.text_size)
            else:
                text rscript_menu_text(prompt) xalign 0.5 color "#ffffff" font rscript_current_font()
        for item in items:
            if item.action is not None:
                $ asset = rscript_choice_asset(item.caption)
                $ selected_folder = "sel_a%02d" % asset if asset is not None else answer_folder
                if selected_folder:
                    $ answer = rscript_grps_layout[selected_folder]
                    fixed:
                        xysize rscript_ui.get("choice_size", answer["size"])
                        $ body = answer["items"]["body"]
                        $ textpos = rscript_ui.get("choice_text_pos", answer["items"].get("text", (20, 10)))
                        imagebutton:
                            idle "images/grps/%s/body.png" % selected_folder
                            hover ("images/grps/%s/body_f.png" % selected_folder
                                   if "body_f" in answer["items"] else
                                   "images/grps/%s/body.png" % selected_folder)
                            focus_mask True
                            xpos (0.5 if rscript_ui.get("choice_center_art", False) else body[0])
                            ypos (0.5 if rscript_ui.get("choice_center_art", False) else body[1])
                            xanchor (0.5 if rscript_ui.get("choice_center_art", False) else 0.0)
                            yanchor (0.5 if rscript_ui.get("choice_center_art", False) else 0.0)
                            action item.action
                        if asset is None:
                            text rscript_menu_text(item.caption):
                                xpos textpos[0]
                                ypos rscript_ui.get("choice_text_yalign", textpos[1])
                                yanchor rscript_ui.get("choice_text_yalign", 0.0)
                                color "#ffffff"
                                font rscript_current_font()
                                size rscript_ui.get("choice_text_size", gui.text_size)
                                outlines rscript_ui.get("choice_outlines", [])
                else:
                    textbutton rscript_menu_text(item.caption) action item.action text_font rscript_current_font()

screen save():
    tag menu
    use rscript_file_slots("save")

screen load():
    tag menu
    use rscript_file_slots("load")

screen rscript_file_slots(mode):
    modal True
    key "game_menu" action Return()
    $ layout = rscript_grps_layout.get("savescrn")
    if layout and "bg_" + mode in layout["items"]:
        fixed:
            xysize layout["size"]
            xalign 0.5
            yalign 0.5
            $ items = layout["items"]
            $ bg = items["bg_" + mode]
            add "images/grps/savescrn/bg_%s.png" % mode xpos bg[0] ypos bg[1]
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
                        action slot_action
                        $ dt1_image = rscript_slot_image(slot)
                        if dt1_image:
                            add dt1_image
                        elif FileLoadable(slot):
                            add FileScreenshot(slot):
                                xpos 4
                                ypos 4
                                xsize 92
                                ysize item[3] - 8
                        if FileLoadable(slot):
                            text FileTime(slot, "%Y/%m/%d %H:%M"):
                                xpos rscript_ui.get("slot_date_pos", (0.98, 0.98))[0]
                                ypos rscript_ui.get("slot_date_pos", (0.98, 0.98))[1]
                                xanchor (0.0 if "slot_date_pos" in rscript_ui else 0.98)
                                yanchor (0.0 if "slot_date_pos" in rscript_ui else 0.98)
                                color rscript_ui.get("slot_date_color", "#ffffff")
                                size 12
                                outlines ([] if "slot_date_pos" in rscript_ui else [(1, "#000000", 0, 0)])
            use rscript_grps_button("savescrn", "prev",
                                     FilePagePrevious(max=10, wrap=True, auto=False, quick=False))
            use rscript_grps_button("savescrn", "next",
                                     FilePageNext(max=10, wrap=True, auto=False, quick=False))
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
