# Shared presentation policies; adapters supply only actual game differences.
init offset = -110
define rscript_ui = {}
define rscript_boot_movies = ()

init python:
    def rscript_migrate_ui_preferences():
        if getattr(persistent, "rscript_opacity_migrated", False):
            return
        opacity = getattr(persistent, "textbox_opacity", None)
        if opacity is not None:
            persistent.rscript_textbox_opacity = opacity
        persistent.rscript_opacity_migrated = True
        renpy.save_persistent()

    config.start_callbacks.append(rscript_migrate_ui_preferences)

    def rscript_main_menu_action():
        return Confirm("Return to the main menu? Unsaved progress will be lost.",
                       MainMenu(confirm=False))

    def rscript_quit_action():
        return Confirm("Quit the game? Unsaved progress will be lost.",
                       Quit(confirm=False))

    def rscript_system_action(value, system=True):
        if not system:
            return Return(value)
        if value == 0:
            return rscript_quit_action()
        if value == 1:
            return ShowMenu("save")
        if value == 2:
            return ShowMenu("load")
        if value == 3:
            return ShowMenu("preferences" if store.menu_enabled else
                            "rscript_title_preferences")
        return Return(value)

    def rscript_textbox_background():
        path = "grps/tbox%02d/back.png" % store.cur_textbox
        background = path if renpy.loadable(path) else Solid("#000000d0")
        origin = rscript_layouts().get("tbox%02d" % store.cur_textbox, {}).get("items", {}).get("back", (0, 0))
        return Transform(background, xoffset=origin[0], yoffset=origin[1],
                         alpha=persistent.rscript_textbox_opacity)

    def rscript_choice_asset(caption):
        try:
            if caption.startswith(("rscript_asset_", "forest_asset_")):
                number = store._r[int(caption.split("_", 2)[2])]
            elif rscript_ui.get("numeric_choices", False):
                number = int(caption)
            else:
                return None
        except (TypeError, ValueError, IndexError):
            return None
        path = "grps/sel_a%02d/body.png" % number
        return number if renpy.loadable(path) else None

    def rscript_menu_panel(caption, prefix):
        # KhimeDL_CHS.exe 0x410bb6 / 0x4133e8: <NN> selects a skin,
        # with the remainder drawn as text; it is not an image-only choice.
        caption = renpy.substitute(caption)
        marker = renpy.re.match(r"<([ \t]*-?[0-9]+)>", caption)
        if marker:
            number = int(marker.group(1)) & 0xffff
            caption = caption[marker.end():]
        else:
            number = rscript_choice_asset(caption) if prefix == "sel_a" else None
            if number is not None:
                caption = ""
        folder = "%s%02d" % (prefix, number if number is not None else 0)
        if folder not in rscript_layouts():
            folder = prefix  # Native fallback is the unnumbered archive.
        if "body" not in rscript_layouts().get(folder, {}).get("items", {}):
            folder = None
        return folder, caption

    def rscript_slot_image(slot):
        from collections.abc import Sequence
        # Keep side-story artwork in the save, not the currently active game UI.
        images = FileJson(slot, key="rscript_slot_images")
        if isinstance(images, Sequence) and not isinstance(images, str) and images and all(
                isinstance(path, str) and renpy.loadable(path) for path in images):
            zoom = FileJson(slot, key="rscript_slot_zoom")
            if not isinstance(zoom, (int, float)) or zoom <= 0:
                zoom = 1.0
            return HBox(*(Transform(Image(path), zoom=zoom) for path in images), spacing=0)
        # Keep existing Forest saves readable; all new saves use the shared key.
        number = FileJson(slot, key="rscript_dt1")
        if number is None:
            number = FileJson(slot, key="forest_dt1")
        if isinstance(number, int) and number > 0:
            path = "grps/dt1_%04d.png" % number
            if renpy.loadable(path):
                return path
        return None

    def rscript_page_image(page):
        if not page.isdigit():
            return None
        number = int(page)
        # Khime names page artwork 0..9 (displaying 1..10); Forest uses 1..10.
        if renpy.loadable("grps/nonbl/0.png"):
            number -= 1
        path = "grps/nonbl/%d.png" % number
        return path if renpy.loadable(path) else None

    def rscript_preference_action(setting, value):
        if setting == "text speed":
            return SetField(persistent, "rscript_text_cps", value)
        action = Preference(setting, value)
        if value == "enable" and setting.endswith(" mute"):
            channels = {"music mute": ("music",),
                        "voice mute": ("rscript_voice",),
                        "sound mute": ("se0", "se1", "se2")}
            return [action] + [Stop(channel) for channel in channels[setting]]
        return action

screen rscript_title_preferences():
    tag menu
    use rscript_text_preferences(wiki=rscript_ui.get("title_wiki", True))

screen choice(items):
    use rscript_choice(items, rscript_choice_prompt)

screen rscript_locmap_screen(cancel=False):
    modal True
    key "dismiss" action Return(1)
    key "game_menu" action (Return(0) if cancel else NullAction())

screen rscript_click_screen(options, previews=None, cancel=False):
    default preview = None
    modal True
    key "game_menu" action (Return(0) if cancel else Function(rscript_open_game_menu))
    key "rollback" action Rollback()
    for index, (value, system, idle_image, hover_image, x, y) in enumerate(options):
        imagebutton:
            idle idle_image
            hover hover_image
            focus_mask True
            xpos x
            ypos y
            hovered SetScreenVariable("preview", (previews or {}).get(index))
            unhovered SetScreenVariable("preview", None)
            action rscript_system_action(value, system)
    if preview is not None:
        add preview[0] pos (preview[1], preview[2]) id "rscript_click_preview"
    use rscript_click_extra(options)

# Game overlays can extend the native picture menu without copying it.
screen rscript_click_extra(options):
    pass

screen rscript_speaker(who):
    if rscript_speaker_visible and rscript_speaker is not None:
        $ path = rscript_text_image_path("gf%03d" % rscript_speaker)
        if renpy.loadable(path):
            add Transform(path, zoom=rscript_ui.get("speaker_zoom", 1.0)) pos rscript_ui.get("speaker_pos", (0, 7))
    elif rscript_speaker_visible and who:
        text who:
            id "who"
            font rscript_current_font()
            size rscript_base_text_size
            color "#ffffff"
            pos rscript_ui.get("speaker_pos", (0, 7))

screen say(who, what, center=False):
    $ textbox = rscript_layouts().get("tbox%02d" % cur_textbox, {})
    $ textpos = textbox.get("items", {}).get("text", (34, 12))
    $ textpos = rscript_ui.get("text_pos", textpos)
    if rscript_use_speaker_images or rscript_speaker_images_override:
        $ textpos = (absolute(text_indent + 1), 8)
    window:
        id "window"
        background rscript_textbox_background()
        xalign 0.5
        yalign 1.0
        xsize textbox.get("size", rscript_ui.get("textbox_size", (800, 138)))[0]
        ysize textbox.get("size", rscript_ui.get("textbox_size", (800, 138)))[1]
        if "front" in textbox.get("items", {}):
            add "grps/tbox%02d/front.png" % cur_textbox:
                pos textbox["items"]["front"][:2]
                alpha persistent.rscript_textbox_opacity
        if rscript_use_speaker_images or rscript_speaker_images_override or rscript_ui.get("show_speaker", False):
            use rscript_speaker(who)
        if center:
            rscript_text what:
                id "what"
                font rscript_current_font()
                size persistent.rscript_text_size
                color "#ffffff"
                slow_cps persistent.rscript_text_cps
                ypos textpos[1]
                xalign 0.5
                text_align 0.5
                line_spacing persistent.rscript_line_spacing
        else:
            rscript_text what:
                id "what"
                font rscript_current_font()
                size persistent.rscript_text_size
                color "#ffffff"
                slow_cps persistent.rscript_text_cps
                pos textpos[:2]
                line_spacing persistent.rscript_line_spacing
        use rscript_compane
