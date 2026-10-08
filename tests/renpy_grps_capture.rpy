# Disposable test only: do not copy into a real game.
default grps_capture_stage = 0
init python:
    # Render/setup errors must fail the check, not loop in a headless error UI.
    def grps_capture_error(short, full, info):
        raise SystemExit(full)
    config.exception_handler = grps_capture_error
    def grps_capture():
        paths = ("preferences.png", "compane.png", "font-picker.png")
        renpy.screenshot(os.path.join(config.basedir, paths[grps_capture_stage]))
        store.grps_capture_stage += 1
        if grps_capture_stage == 1:
            renpy.hide_screen("preferences")
            renpy.show_screen("rscript_compane")
        elif grps_capture_stage == 2:
            renpy.hide_screen("rscript_compane")
            renpy.show_screen("preferences")
            renpy.show_screen("rscript_font_picker")
        else:
            renpy.quit()
        renpy.restart_interaction()

label before_main_menu:
    $ persistent.rscript_text_size = 32
    $ persistent.rscript_text_font = rscript_default_font
    show screen preferences
    show screen grps_capture_timer
    $ renpy.pause()

screen grps_capture_timer():
    timer 1.0 action Function(grps_capture) repeat True

label _0000:
    $ renpy.quit()
