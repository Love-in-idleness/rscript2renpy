# Real title -> 0050 -> 0999 -> 1000; disposable saves, no player progress.
default kagerou_portrait_title_seen = False
default kagerou_portrait_ready = False

init python:
    rscript_update_duration = lambda effect, step, wait: .01
    def kagerou_portrait_error(short, full, info):
        raise SystemExit(full)
    config.exception_handler = kagerou_portrait_error

    def kagerou_portrait_check():
        if rscript_click_values:
            assert 1 in [value for value, system in rscript_click_values.values() if not system]
            store.kagerou_portrait_title_seen = True
            renpy.end_interaction(1)
            return
        if layer_info.get(1) == 'grpo_bu 3011':
            assert kagerou_portrait_title_seen
            assert layer_anchor[1] == (.5, 0)
            assert layer_pos[1] == (200, 0)
            image = renpy.get_registered_image('grpo_bu 3011')
            image.find_target()
            assert renpy.loadable(image.raw_target.filename)
            assert renpy.showing('layer1', layer=IMAGE_LAYER)
            if not kagerou_portrait_ready:
                store.kagerou_portrait_ready = True
                renpy.restart_interaction()
                return
            language = _preferences.language or 'jp'
            renpy.screenshot(os.path.join(config.basedir, 'portrait-%s.png' % language))
            renpy.quit()
        if renpy.get_screen('say'):
            renpy.end_interaction(True)

label before_main_menu:
    scene black onlayer black
    python:
        kagerou_init_textbox()
        persistent.rscript_text_cps = 0
        _preferences.language = os.environ.get('KAGEROU_TEST_LANGUAGE') or None
    show screen kagerou_portrait_timer
    call _0000
    $ renpy.quit()

screen kagerou_portrait_timer():
    timer .1 action Function(kagerou_portrait_check) repeat True
