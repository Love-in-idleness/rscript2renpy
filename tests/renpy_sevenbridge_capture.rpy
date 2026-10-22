# Disposable visual check; the runner isolates both saves and generated scripts.
default sevenbridge_capture_stage = 0

init python:
    def sevenbridge_capture_error(short, full, info):
        raise SystemExit(full)
    config.exception_handler = sevenbridge_capture_error
    config.overlay_screens.append("sevenbridge_capture_timer")

    def sevenbridge_capture_tick():
        stage = store.sevenbridge_capture_stage
        if stage == 0 and (not renpy.get_screen("rscript_click_screen") or
                           store.layer_info.get(CG_LAYER) != "grpe 3001"):
            return
        if stage == 1 and not store.last_say:
            return
        destination = os.environ["SEVENBRIDGE_CAPTURE"]
        names = ("title.png", "dialogue.png", "preferences.png", "save.png", "load.png")
        renpy.screenshot(os.path.join(destination, names[stage]))
        store.sevenbridge_capture_stage += 1
        if stage == 0:
            renpy.hide_screen("rscript_click_screen")
            renpy.jump("_0100")
        elif stage == 1:
            renpy.show_screen("preferences")
        elif stage == 2:
            renpy.hide_screen("preferences")
            renpy.take_screenshot()
            FilePage(1)()
            FileSave(1, confirm=False)()
            assert FileJson(1, key="rscript_dt2") == 1
            assert rscript_slot_image(1) == "grps/dt2_0001.png"
            renpy.show_screen("save")
        elif stage == 3:
            renpy.hide_screen("save")
            renpy.show_screen("load")
        else:
            renpy.quit()
        renpy.restart_interaction()

screen sevenbridge_capture_timer():
    zorder 500
    timer 3.0 repeat True action Function(sevenbridge_capture_tick)
