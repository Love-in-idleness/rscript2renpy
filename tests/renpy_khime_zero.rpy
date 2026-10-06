# Use only in an isolated fixture project with a temporary save directory.
python early:
    def check_khime_zero():
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        renpy.display.scenelists.init_layers()
        renpy.game.context().scene_lists = renpy.display.scenelists.SceneLists(None, renpy.game.context().images)
        renpy.display.screen.prepare_screens()
        assert khime_zero_available
        options = [(0, True, "grpo_tp 9006", "grpo_tp 9106", 253, 552)]
        _r[7901] = 0
        assert not khime_zero_unlocked()
        renpy.show_screen("rscript_click_screen", options=options)
        renpy.get_screen("rscript_click_screen").update()
        assert renpy.get_widget("rscript_click_screen", "khime_zero_entry") is None
        locked_buttons = []
        renpy.get_screen("rscript_click_screen").visit_all(
            lambda d: locked_buttons.append(d) if isinstance(d, renpy.display.behavior.Button)
            and isinstance(d.action, Jump) else None)
        assert not locked_buttons
        renpy.hide_screen("rscript_click_screen")
        _r[7901] = 1
        assert khime_zero_unlocked()
        assert RScriptArguments(yLoc="517+35*khime_zero_unlocked()").yLoc == 552
        renpy.show_screen("rscript_click_screen", options=options)
        renpy.get_screen("rscript_click_screen").update()
        buttons = []
        renpy.get_screen("rscript_click_screen").visit_all(
            lambda d: buttons.append(d) if isinstance(d, renpy.display.behavior.Button)
            and isinstance(d.action, Jump) else None)
        assert len(buttons) == 1, buttons
        entry = buttons[0]
        assert entry.style.xpos == 273 and entry.style.ypos == 517
        assert entry.action.label == "khime_zero_start"
        renpy.hide_screen("rscript_click_screen")
        for tag in ("khime_zero grpe 0655", "khime_zero grpo_bu 1902"):
            image = renpy.get_registered_image(tag)
            assert image.zoom == 1.25
        assert rscript_text_image_path("gf008") == "images/grps/gf008.png"
        main_ui = rscript_ui
        registers = dict(persistent._reg)
        khime_zero_begin()
        assert main_ui is not rscript_ui and "text_image_root" not in main_ui
        assert rscript_text_image_path("gf008") == "images/khime_zero/grps/gf008.png"
        assert rscript_speaker_images_override and not rscript_use_speaker_images
        assert layer_x_grid == layer_y_grid == 1.25
        assert folder[21] == "khime_zero grpo_bu"
        assert rscript_se_format == "khime_zero/wav/%04d.ogg"
        loadcls(21, 0, cg=1902, xpos=320, ypos=240)
        assert layer_pos[21] == (400, 300)
        assert isinstance(layer_pos[21][0], absolute)
        assert isinstance(layer_pos[21][1], absolute)
        assert layer_info[21] == "khime_zero grpo_bu 1902"
        khime_zero_gload(RScriptArguments(CGNum=655, Colormode=0))
        assert layer_info[CG_LAYER] == "khime_zero grpe 0655"
        assert dict(persistent._reg) == registers
        rscript_dialogue_begin()
        parsed, center = parse_rscript_text(repr("^g008body"), True)
        assert rscript_speaker == 8 and parsed == "body"
        renpy.show_screen("say", who=None, what=parsed, center=False)
        renpy.get_screen("say").update()
        text = renpy.get_widget("say", "what")
        assert isinstance(text.style.xpos, absolute), text.style.xpos
        assert 0 < text.style.xpos < 800
        renpy.hide_screen("say")
        print("OK: native Khime Zero unlock, image entry, scale, names and isolated CG flags")
        return False
    renpy.arguments.register_command("khimezerotest", check_khime_zero)

# Exercise the actual image-menu Jump -> say interaction -> end/restart path.
init 100 python:
    def zero_display_exception(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = zero_display_exception
    config.overlay_screens.append("zero_display_probe")
    def zero_display_probe():
        text = renpy.get_widget("say", "what")
        assert text is not None and isinstance(text.style.xpos, absolute)
        assert 0 < text.style.xpos < 800
        assert rscript_speaker == 8
        renpy.screenshot(config.basedir + "/zero-dialogue.png")
        renpy.session["zero_display_done"] = True
        renpy.end_interaction(True)

screen zero_display_probe():
    if rscript_speaker_images_override and renpy.get_screen("say"):
        timer 0.3 action Function(zero_display_probe)
    elif not rscript_speaker_images_override and renpy.get_screen("rscript_click_screen"):
        timer 0.1 action Jump("khime_zero_start")

label _0000:
    if renpy.session.get("zero_display_done", False):
        python:
            assert not rscript_speaker_images_override
            assert "text_image_root" not in rscript_ui
            assert rscript_se_format == "wav/%04d.ogg"
            assert _r[7901] == 1 and _r[9655] == 0
            print("OK: native Zero dialogue interaction and clean return to title")
            renpy.quit()
    $ _r[7901] = 1
    $ menu_enabled = 0
    $ renpy.call_screen("rscript_click_screen", options=[(0, True, "grpo_tp 9006", "grpo_tp 9106", 253, 552)])
    $ raise AssertionError("entry failed to jump into the side story")
