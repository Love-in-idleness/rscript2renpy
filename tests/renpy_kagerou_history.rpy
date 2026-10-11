# Real dialogue and Back overlay, with disposable saves and automated dismissal.
default kagerou_history_test_stage = 0

init python:
    def kagerou_history_test_error(short, full, info):
        raise SystemExit(full)
    config.exception_handler = kagerou_history_test_error

    def kagerou_history_test_tick():
        if kagerou_history_test_stage == 0:
            renpy.end_interaction(True)
        elif kagerou_history_test_stage == 1:
            assert len(_history_list) == 2
            assert '二番目' in _history_list[-1].what
            store.kagerou_history_test_page = (kagerou_page, kagerou_page_old, kagerou_page_current)
            store.kagerou_history_test_registers = (dict(_reg), dict(persistent._reg))
            renpy.run(Show('kagerou_history'))
            store.kagerou_history_test_stage = 2
        elif kagerou_history_test_stage == 2:
            viewport = renpy.get_widget('kagerou_history', 'history_viewport')
            assert viewport.width >= 700, viewport.width  # Was 0, with a full-width scrollbar.
            close_text = renpy.get_widget('kagerou_history', 'history_close')
            assert close_text.style.font == rscript_current_font()
            for index in range(len(_history_list)):
                text = renpy.get_widget('kagerou_history', 'history_%d' % index)
                assert text.style.font == rscript_current_font()
                assert text.get_layout().size[0] <= viewport.width
                assert all(segment.font == rscript_current_font()
                           for paragraph in text.get_layout().paragraphs
                           for segment, content in paragraph if segment.ruby_top)
            assert viewport.yadjustment.value <= viewport.yadjustment.range
            renpy.screenshot(os.path.join(config.basedir, 'history.png'))
            # Close through the actual button action; this must not advance the story.
            actions = []
            renpy.get_screen('kagerou_history').visit_all(lambda d: actions.append(d.action)
                if isinstance(d, renpy.display.behavior.Button) and isinstance(d.action, Hide) else None)
            assert len(actions) == 1
            renpy.run(actions[0])
            store.kagerou_history_test_stage = 3
        else:
            assert renpy.get_screen('kagerou_history') is None
            assert renpy.get_screen('say') is not None
            assert (kagerou_page, kagerou_page_old, kagerou_page_current) == kagerou_history_test_page
            assert (dict(_reg), dict(persistent._reg)) == kagerou_history_test_registers
            renpy.screenshot(os.path.join(config.basedir, 'history-closed.png'))
            print('OK: Back opens readable history; close preserves dialogue and registers')
            renpy.quit()

label before_main_menu:
    scene black onlayer black
    python:
        # before_main_menu is a menu context; enable the game's history behavior.
        _history = True
        kagerou_init_textbox()
        persistent.rscript_text_cps = 0
        textbox_panel = 1
    show screen kagerou_history_test_timer
    $ kagerou_text('【女】最初の記録。抉[えぐ]られた傷痕。', 1)
    $ kagerou_history_test_stage = 1
    $ kagerou_text('【男】二番目の記録。返回后应保持这句话。', 1)

screen kagerou_history_test_timer():
    zorder 200
    timer .2 action Function(kagerou_history_test_tick) repeat True
