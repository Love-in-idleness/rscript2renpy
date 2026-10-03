init offset = 10
init -100 python:
    rscript_voice_format = "voice/%04d.ogg"
    rscript_bgm_format = "bgm/Track%02d.ogg"
    rscript_se_format = "wav/%04d.ogg"
    rscript_ctc_x = 747
    rscript_ctc_y = 556

style default:
    font "fonts/NotoSansCJKjp-Regular.otf"

style forest_volume_bar is bar:
    left_bar Solid("#00000000")
    right_bar Solid("#00000000")
    hover_left_bar Solid("#00000000")
    hover_right_bar Solid("#00000000")

default forest_click_links = {}
default forest_click_values = {}
default forest_click_system = {}
default forest_choice_prompt = ""
default forest_input_locked = False
default persistent.textbox_opacity = 1.0
init -90 python:
    rscript_use_speaker_images = True

init python:
    # Old history/overlay displayables may still contain these saved tag names.
    config.self_closing_custom_text_tags["forest_g"] = rscript_g_tag
    config.self_closing_custom_text_tags["forest_a"] = rscript_a_tag

    def forest_migrate_preferences():
        if getattr(persistent, "rscript_forest_preferences_migrated", False):
            return
        for name in ("text_size", "say_line_chars", "oload_line_chars",
                     "line_spacing", "text_cps", "text_font", "wiki_mode",
                     "progress_backup", "previous_default_font"):
            value = getattr(persistent, "forest_" + name, None)
            if value is not None:
                setattr(persistent, "rscript_" + name, value)
        persistent.rscript_forest_preferences_migrated = True
        renpy.save_persistent()

    # Run the migration before the shared default-font upgrade.
    config.start_callbacks.insert(0, forest_migrate_preferences)

    def rscript_touch_locked():
        return store.forest_input_locked

    def forest_save_json(data):
        data["forest_dt1"] = int(_r[1])

    config.save_json_callbacks.append(forest_save_json)

screen preferences(title_mode=False):
    tag menu
    modal True
    key "game_menu" action Return()

    fixed:
        xysize (518, 420)
        xalign 0.5
        yalign 0.5
        add "images/grps/confscrn/bg.png" xpos 4 ypos 2

        imagebutton:
            idle "images/grps/confscrn/scm_ful_f.png"
            hover "images/grps/confscrn/scm_ful_f.png"
            selected_idle "images/grps/confscrn/scm_ful.png"
            selected_hover "images/grps/confscrn/scm_ful.png"
            action Preference("display", "fullscreen")
            xpos 202 ypos 23
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/scm_wnd_f.png"
            hover "images/grps/confscrn/scm_wnd_f.png"
            selected_idle "images/grps/confscrn/scm_wnd.png"
            selected_hover "images/grps/confscrn/scm_wnd.png"
            action Preference("display", "window")
            xpos 356 ypos 23
            activate_sound "wav/0001.ogg"

        imagebutton:
            idle "images/grps/confscrn/bgm_on_f.png"
            hover "images/grps/confscrn/bgm_on_f.png"
            selected_idle "images/grps/confscrn/bgm_on.png"
            selected_hover "images/grps/confscrn/bgm_on.png"
            action Preference("music mute", "disable")
            xpos 202 ypos 55
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/bgm_off_f.png"
            hover "images/grps/confscrn/bgm_off_f.png"
            selected_idle "images/grps/confscrn/bgm_off.png"
            selected_hover "images/grps/confscrn/bgm_off.png"
            action [Preference("music mute", "enable"), Stop("music")]
            xpos 356 ypos 55
            activate_sound "wav/0001.ogg"
        bar:
            style "forest_volume_bar"
            thumb "images/grps/confscrn/bgm_vol.png"
            hover_thumb "images/grps/confscrn/bgm_vol_f.png"
            value Preference("music volume")
            xpos 234 ypos 87
            xsize 230 ysize 21

        imagebutton:
            idle "images/grps/confscrn/voc_on_f.png"
            hover "images/grps/confscrn/voc_on_f.png"
            selected_idle "images/grps/confscrn/voc_on.png"
            selected_hover "images/grps/confscrn/voc_on.png"
            action Preference("voice mute", "disable")
            xpos 202 ypos 119
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/voc_off_f.png"
            hover "images/grps/confscrn/voc_off_f.png"
            selected_idle "images/grps/confscrn/voc_off.png"
            selected_hover "images/grps/confscrn/voc_off.png"
            action [Preference("voice mute", "enable"), Stop("rscript_voice")]
            xpos 356 ypos 119
            activate_sound "wav/0001.ogg"
        bar:
            style "forest_volume_bar"
            thumb "images/grps/confscrn/voc_vol.png"
            hover_thumb "images/grps/confscrn/voc_vol_f.png"
            value Preference("voice volume")
            xpos 234 ypos 151
            xsize 230 ysize 21

        imagebutton:
            idle "images/grps/confscrn/sef_on_f.png"
            hover "images/grps/confscrn/sef_on_f.png"
            selected_idle "images/grps/confscrn/sef_on.png"
            selected_hover "images/grps/confscrn/sef_on.png"
            action Preference("sound mute", "disable")
            xpos 202 ypos 183
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/sef_off_f.png"
            hover "images/grps/confscrn/sef_off_f.png"
            selected_idle "images/grps/confscrn/sef_off.png"
            selected_hover "images/grps/confscrn/sef_off.png"
            action [Preference("sound mute", "enable"), Stop("se0")]
            xpos 356 ypos 183
            activate_sound "wav/0001.ogg"
        bar:
            style "forest_volume_bar"
            thumb "images/grps/confscrn/sef_vol.png"
            hover_thumb "images/grps/confscrn/sef_vol_f.png"
            value Preference("sound volume")
            xpos 234 ypos 215
            xsize 230 ysize 21

        if _preferences.language in rscript_wiki_keywords:
            if not title_mode:
                imagebutton:
                    idle "images/grps/confscrn/gef_on_f.png"
                    hover "images/grps/confscrn/gef_on_f.png"
                    selected_idle "images/grps/confscrn/gef_on.png"
                    selected_hover "images/grps/confscrn/gef_on.png"
                    action Function(rscript_set_wiki, True)
                    selected persistent.rscript_wiki_mode
                    xpos 202 ypos 247
                    activate_sound "wav/0001.ogg"
                imagebutton:
                    idle "images/grps/confscrn/gef_off_f.png"
                    hover "images/grps/confscrn/gef_off_f.png"
                    selected_idle "images/grps/confscrn/gef_off.png"
                    selected_hover "images/grps/confscrn/gef_off.png"
                    action Function(rscript_set_wiki, False)
                    selected not persistent.rscript_wiki_mode
                    xpos 356 ypos 247
                    activate_sound "wav/0001.ogg"
        else:
            imagebutton:
                idle "images/grps/confscrn/gef_on_f.png"
                hover "images/grps/confscrn/gef_on_f.png"
                selected_idle "images/grps/confscrn/gef_on.png"
                selected_hover "images/grps/confscrn/gef_on.png"
                action Preference("transitions", "all")
                xpos 202 ypos 247
                activate_sound "wav/0001.ogg"
            imagebutton:
                idle "images/grps/confscrn/gef_off_f.png"
                hover "images/grps/confscrn/gef_off_f.png"
                selected_idle "images/grps/confscrn/gef_off.png"
                selected_hover "images/grps/confscrn/gef_off.png"
                action Preference("transitions", "none")
                xpos 356 ypos 247
                activate_sound "wav/0001.ogg"

        imagebutton:
            idle "images/grps/confscrn/msp_slw_f.png"
            hover "images/grps/confscrn/msp_slw_f.png"
            selected_idle "images/grps/confscrn/msp_slw.png"
            selected_hover "images/grps/confscrn/msp_slw.png"
            action Preference("text speed", 25)
            xpos 202 ypos 279
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/msp_nom_f.png"
            hover "images/grps/confscrn/msp_nom_f.png"
            selected_idle "images/grps/confscrn/msp_nom.png"
            selected_hover "images/grps/confscrn/msp_nom.png"
            action Preference("text speed", 75)
            xpos 295 ypos 279
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/msp_now_f.png"
            hover "images/grps/confscrn/msp_now_f.png"
            selected_idle "images/grps/confscrn/msp_now.png"
            selected_hover "images/grps/confscrn/msp_now.png"
            action Preference("text speed", 0)
            xpos 388 ypos 279
            activate_sound "wav/0001.ogg"

        imagebutton:
            idle "images/grps/confscrn/msk_on_f.png"
            hover "images/grps/confscrn/msk_on_f.png"
            selected_idle "images/grps/confscrn/msk_on.png"
            selected_hover "images/grps/confscrn/msk_on.png"
            action Preference("skip", "all")
            xpos 202 ypos 311
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/msk_off_f.png"
            hover "images/grps/confscrn/msk_off_f.png"
            selected_idle "images/grps/confscrn/msk_off.png"
            selected_hover "images/grps/confscrn/msk_off.png"
            action Preference("skip", "seen")
            xpos 356 ypos 311
            activate_sound "wav/0001.ogg"

        if not title_mode:
            if store.save_enabled:
                imagebutton:
                    idle "images/grps/confscrn/save.png"
                    hover "images/grps/confscrn/save_f.png"
                    action ShowMenu("save")
                    xpos 148 ypos 346
                    activate_sound "wav/0001.ogg"
                imagebutton:
                    idle "images/grps/confscrn/load.png"
                    hover "images/grps/confscrn/load_f.png"
                    action ShowMenu("load")
                    xpos 263 ypos 346
                    activate_sound "wav/0001.ogg"
            imagebutton:
                idle "images/grps/confscrn/close.png"
                hover "images/grps/confscrn/close_f.png"
                action Return()
                xpos 115 ypos 372
                activate_sound "wav/0001.ogg"

        imagebutton:
            idle "images/grps/confscrn/title.png"
            hover "images/grps/confscrn/title_f.png"
            action MainMenu()
            xpos 213 ypos 372
            activate_sound "wav/0001.ogg"
        if not title_mode:
            imagebutton:
                idle "images/grps/confscrn/exit.png"
                hover "images/grps/confscrn/exit_f.png"
                action Quit(confirm=True)
                xpos 311 ypos 372
                activate_sound "wav/0001.ogg"

screen forest_title_preferences():
    tag menu
    use rscript_text_preferences(wiki=False)

screen save():
    tag menu
    use forest_file_slots("save")

screen load():
    tag menu
    use forest_file_slots("load")

screen forest_file_slots(mode):
    modal True
    key "game_menu" action Return()
    add ("images/grps/savescrn/bg_%s.png" % mode) xpos -501 ypos -89

    $ slot_positions = [(106, 137), (106, 204), (106, 271), (106, 338), (106, 405), (421, 137), (421, 204), (421, 271), (421, 338), (421, 405)]
    for index, position in enumerate(slot_positions):
        $ slot = index + 1
        $ slot_action = FileSave(slot) if mode == "save" else FileLoad(slot)
        $ dt1 = FileJson(slot, key="forest_dt1")
        button:
            xpos position[0]
            ypos position[1]
            xsize 257
            ysize 62
            background None
            hover_background Solid("#ffffff18")
            action slot_action
            fixed:
                if dt1:
                    add ("images/grps/dt1_%04d.png" % int(dt1))
                    text FileTime(slot, "%Y/%m/%d %H:%M"):
                        xpos 114 ypos 38
                        size 12
                        color "#3b2410"

    imagebutton:
        idle "images/grps/savescrn/prev.png"
        hover "images/grps/savescrn/prev_f.png"
        insensitive "images/grps/savescrn/prev_c.png"
        action FilePagePrevious(max=10, wrap=True, auto=False, quick=False)
        xpos 563 ypos 544
        activate_sound "wav/0001.ogg"
    $ page_name = FileCurrentPage()
    $ page_number = min(10, max(1, int(page_name))) if page_name.isdigit() else 1
    $ page_x = (14, 8, 8, 8, 8, 8, 8, 8, 9, 5)[page_number - 1]
    fixed:
        xpos 599 ypos 537
        xsize 38 ysize 34
        add ("images/grps/nonbl/%d.png" % page_number) xpos page_x ypos 2
    imagebutton:
        idle "images/grps/savescrn/next.png"
        hover "images/grps/savescrn/next_f.png"
        insensitive "images/grps/savescrn/next_c.png"
        action FilePageNext(max=10, wrap=True, auto=False, quick=False)
        xpos 636 ypos 544
        activate_sound "wav/0001.ogg"
    imagebutton:
        idle "images/grps/savescrn/exit.png"
        hover "images/grps/savescrn/exit_f.png"
        action Return()
        xpos 707 ypos 538
        activate_sound "wav/0001.ogg"

screen say(who, what, center=False):
    window:
        id "window"
        background Transform("images/grps/tbox01/back.png", alpha=persistent.textbox_opacity)
        xpos 0
        ypos 462
        xsize 800
        ysize 138
        if rscript_speaker_visible and rscript_speaker is not None:
            $ speaker_image = "images/grps/gf%03d.png" % rscript_speaker
            if renpy.loadable(speaker_image):
                add speaker_image xpos 0 ypos 7
        elif rscript_speaker_visible and who:
            text who:
                id "who"
                font rscript_current_font()
                size 22
                color "#ffffff"
                xpos 0
                ypos 7
        if center:
            rscript_text what:
                id "what"
                font rscript_current_font()
                size persistent.rscript_text_size
                color "#ffffff"
                slow_cps persistent.rscript_text_cps
                ypos 8
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
                ypos 8
                xpos text_indent + 1
                line_spacing persistent.rscript_line_spacing

        use forest_compane

screen forest_compane():
    zorder 100
    if not _preferences.afm_enable:
        fixed:
            xpos 606
            ypos 120
            xsize 194
            ysize 18

            bar:
                thumb "images/grps/compane/slide.png"
                hover_thumb "images/grps/compane/slide_f.png"
                base_bar "images/grps/compane/bg.png"
                thumb_offset 2
                value FieldValue(persistent, "textbox_opacity", range=1.0)
                xpos 4
                ypos 2
                xsize 75
                ysize 14
                bar_invert True

            imagebutton:
                idle "images/grps/compane/rev.png"
                hover "images/grps/compane/rev_f.png"
                selected_idle "images/grps/compane/rev.png"
                action If(jump_back_point, RollbackToIdentifier(jump_back_point), NullAction())
                sensitive jump_back_point is not None and not forest_input_locked
                xpos 88
                ypos 2
                focus_mask True
            imagebutton:
                idle "images/grps/compane/bak.png"
                hover "images/grps/compane/bak_f.png"
                selected_idle "images/grps/compane/bak.png"
                action Rollback()
                sensitive not forest_input_locked
                xpos 105
                ypos 2
                focus_mask True
            imagebutton:
                idle "images/grps/compane/fow.png"
                hover "images/grps/compane/fow_f.png"
                selected_idle "images/grps/compane/fow.png"
                action RollForward()
                xpos 122
                ypos 2
                focus_mask True
            imagebutton:
                idle "images/grps/compane/next.png"
                hover "images/grps/compane/next_f.png"
                selected_idle "images/grps/compane/next.png"
                action Skip(fast=True)
                xpos 139
                ypos 2
                focus_mask True
            imagebutton:
                idle "images/grps/compane/voc.png"
                hover "images/grps/compane/voc_f.png"
                selected_idle "images/grps/compane/voc.png"
                insensitive "images/grps/compane/voc_off.png"
                action Function(rscript_replay_voice)
                sensitive rscript_last_voice is not None
                xpos 155
                ypos 1
                focus_mask True
            imagebutton:
                idle "images/grps/compane/hide.png"
                hover "images/grps/compane/hide_f.png"
                selected_idle "images/grps/compane/hide.png"
                action HideInterface()
                xpos 173
                ypos 2
                focus_mask True

screen choice(items):
    modal True
    $ options = [item for item in items if item.action is not None]
    vbox:
        xalign 0.5
        yalign 0.4
        spacing -4
        if forest_choice_prompt:
            fixed:
                xsize 505
                ysize 48
                add "images/grps/sel_q00/body.png"
                text rscript_menu_text(forest_choice_prompt):
                    font rscript_current_font()
                    size 20
                    color "#2a2015"
                    xpos 35
                    yalign 0.45
        for item in options:
            $ asset = forest_choice_asset(item.caption)
            $ stem = "sel_a%02d" % asset if asset is not None else "sel_a00"
            fixed:
                xsize 505
                ysize 82
                imagebutton:
                    idle "images/grps/%s/body.png" % stem
                    hover "images/grps/%s/body_f.png" % stem
                    focus_mask True
                    xalign 0.5
                    yalign 0.5
                    action item.action
                if asset is None:
                    text rscript_menu_text(item.caption):
                        font rscript_current_font()
                        size 21
                        color "#ffffff"
                        outlines [(2, "#18220d", 0, 0)]
                        xpos 48
                        yalign 0.46

screen forest_click_screen(options):
    modal True
    for value, system, idle_image, hover_image, xpos, ypos in options:
        $ click_action = forest_system_action(value) if system else Return(value)
        imagebutton:
            idle idle_image
            hover hover_image
            focus_mask True
            xpos xpos
            ypos ypos
            action click_action

python early:
    def forest_choice_asset(caption):
        try:
            if caption.startswith("forest_asset_"):
                number = store._r[int(caption[13:])]
            else:
                number = int(caption)
        except (TypeError, ValueError):
            return None
        stem = "images/grps/sel_a%02d/body.png" % number
        return number if renpy.loadable(stem) else None

    def parse_forest_folder(lex):
        args = rscript_arguments(lex, ["Layer", "Folder"])
        lex.expect_eol()
        return args

    def execute_forest_folder(args):
        if args.Layer == 0:
            for layer in range(100):
                store.folder[layer] = args.Folder
        else:
            store.folder[args.Layer] = args.Folder

    renpy.register_statement("_forest_folder", parse=parse_forest_folder,
        execute=execute_forest_folder, lint=lint_undef)

    def parse_forest_setclk(lex):
        args = rscript_arguments(lex, ["Layer", "Value", "Mode", "Unknown"])
        lex.expect_eol()
        return args

    def execute_forest_setclk(args):
        store.forest_click_values[args.Layer] = args.Value
        store.forest_click_system.pop(args.Layer, None)

    def execute_forest_setclksys(args):
        store.forest_click_values[args.Layer] = args.Value
        store.forest_click_system[args.Layer] = True

    renpy.register_statement("_forest_setclk", parse=parse_forest_setclk,
        execute=execute_forest_setclk, lint=lint_undef)
    renpy.register_statement("_forest_setclksys", parse=parse_forest_setclk,
        execute=execute_forest_setclksys, lint=lint_undef)

    def forest_system_action(value):
        if value == 0:
            return Quit(confirm=True)
        if value == 1:
            return ShowMenu("save")
        if value == 2:
            return ShowMenu("load")
        if value == 3:
            if store.menu_enabled:
                return ShowMenu("preferences")
            return ShowMenu("forest_title_preferences")
        return Return(value)

    def parse_forest_setlink(lex):
        args = rscript_arguments(lex, ["Layer", "HoverCG", "xLoc", "yLoc"])
        lex.expect_eol()
        return args

    def execute_forest_setlink(args):
        store.forest_click_links[args.Layer] = (args.HoverCG, args.xLoc, args.yLoc)

    renpy.register_statement("_forest_setlink", parse=parse_forest_setlink,
        execute=execute_forest_setlink, lint=lint_undef)

    def parse_forest_click(lex):
        args = rscript_arguments(lex, ["Unknown1", "Unknown2"])
        lex.expect_eol()
        return args

    def execute_forest_click(args):
        options = []
        for layer in sorted(store.forest_click_values):
            if layer not in store.forest_click_links or layer not in store.layer_info:
                continue
            hover_cg, xpos, ypos = store.forest_click_links[layer]
            folder_name = store.folder.get(layer, store.folder.get(0))
            if not folder_name:
                continue
            options.append((
                store.forest_click_values[layer],
                store.forest_click_system.get(layer, False),
                store.layer_info[layer],
                "%s %04d" % (folder_name, hover_cg),
                xpos * store.layer_x_grid,
                ypos * store.layer_y_grid,
            ))
        if options:
            store._r[0] = renpy.call_screen("forest_click_screen", options=options)
        else:
            renpy.notify("Forest: click instruction has no active regions")
            store._r[0] = 0
        store.forest_click_links.clear()
        store.forest_click_values.clear()
        store.forest_click_system.clear()

    renpy.register_statement("_forest_click", parse=parse_forest_click,
        execute=execute_forest_click, lint=lint_undef)

    def parse_forest_noargs(lex):
        lex.rest()
        lex.expect_eol()

    def execute_forest_resetclk(args):
        store.forest_click_links.clear()
        store.forest_click_values.clear()
        store.forest_click_system.clear()

    renpy.register_statement("_forest_resetclk", parse=parse_forest_noargs,
        execute=execute_forest_resetclk, lint=lint_undef)
    renpy.register_statement("_forest_autoreset", parse=parse_forest_noargs,
        execute=lambda args: None, lint=lint_undef)
