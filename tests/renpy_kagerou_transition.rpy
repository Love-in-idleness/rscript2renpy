# Real generated 0999 -> 1000, with disposable saves and automatic dismissal.
default kagerou_transition_stage = 0

init python:
    # Exercise real drawing/transitions, not their native duration.
    rscript_update_duration = lambda effect, step, wait: .05
    def kagerou_transition_error(short, full, info):
        raise SystemExit(full)
    config.exception_handler = kagerou_transition_error

    def kagerou_transition_check():
        screen = renpy.get_screen('say')
        if screen is None or not kagerou_page:
            return
        if kagerou_transition_stage == 0:
            assert '霞外籠逗留記' in kagerou_page or '霞外笼逗留记' in kagerou_page
            renpy.end_interaction(True)
        else:
            assert '霞外籠逗留記' not in kagerou_page and '霞外笼逗留记' not in kagerou_page
            assert not kagerou_page_old, repr(kagerou_page_old)
            assert renpy.get_widget('say', 'what').text == [kagerou_page_text()]
            language = _preferences.language or 'jp'
            renpy.screenshot(os.path.join(config.basedir, 'transition-%s.png' % language))
            renpy.quit()

label before_main_menu:
    scene black onlayer black
    python:
        kagerou_init_textbox()
        persistent.rscript_text_cps = 0
        _preferences.language = os.environ.get('KAGEROU_TEST_LANGUAGE') or None
    show screen kagerou_transition_timer
    call _0999
    python:
        assert kagerou_page == kagerou_page_old == kagerou_page_current == ''
        assert last_say is None and last_spk is None
        assert renpy.get_screen('say') is None
        # A retained say scope must not restore the cleared 0999 text.
        renpy.show_screen('say', who=None, what='0999の残った文字')
        renpy.get_screen('say').update()
        assert renpy.get_widget('say', 'what').text == ['']
        renpy.hide_screen('say')
        store.kagerou_transition_stage = 1
    call _1000
    $ renpy.quit()

screen kagerou_transition_timer():
    timer .2 action Function(kagerou_transition_check) repeat True
