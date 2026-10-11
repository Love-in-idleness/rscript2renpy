# Actual Back and wheel rollback, without running a real route or player saves.
init 100 python:
    config.label_overrides['start'] = '_kagerou_rollback_test'
    renpy.session['kagerou_rollback_stage'] = 'first'

    def kagerou_rollback_error(short, full, info):
        raise SystemExit(full)
    config.exception_handler = kagerou_rollback_error

    def kagerou_rollback_tick():
        screen = renpy.get_screen('say')
        if screen is None or not kagerou_page_current:
            return
        stage = renpy.session['kagerou_rollback_stage']
        if stage == 'first':
            assert kagerou_page_current == '最初の対話。' and _r[123] == 1
            renpy.session['kagerou_rollback_stage'] = 'second'
            renpy.end_interaction(True)
        elif stage == 'second':
            assert kagerou_page_current == '二番目の対話。' and _r[123] == 2
            actions = []
            screen.visit_all(lambda d: actions.append(d.action)
                if isinstance(d, renpy.display.behavior.Button) and isinstance(d.action, Rollback) else None)
            assert len(actions) == 1 and actions[0].get_sensitive()
            renpy.session['kagerou_rollback_stage'] = 'returned'
            if os.environ['KAGEROU_ROLLBACK_INPUT'] == 'back':
                renpy.run(actions[0])
            else:
                renpy.queue_event('rollback')  # The event bound to mousedown_4.
        else:
            assert kagerou_page_current == '最初の対話。' and _r[123] == 1
            assert renpy.get_screen('kagerou_history') is None
            mode = os.environ['KAGEROU_ROLLBACK_INPUT']
            renpy.screenshot(os.path.join(config.basedir, 'rollback-%s.png' % mode))
            print('OK: %s returns to the preceding dialogue and local registers' % mode)
            renpy.quit()

    config.periodic_callback = kagerou_rollback_tick

label _kagerou_rollback_test:
    python:
        roll_enabled = _rollback = True
        textbox_panel = 1
        persistent.rscript_text_cps = 0
        kagerou_init_textbox()
        renpy.block_rollback()
    $ _r[123] = 1
    $ kagerou_text('最初の対話。', 1)
    $ _r[123] = 2
    $ kagerou_text('二番目の対話。', 1)
    $ raise AssertionError('Back dismissed the dialogue instead of rolling back')
