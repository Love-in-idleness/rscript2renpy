# SDK command for a disposable fixture project, not a player's game/saves.
python early:
    def check_cannonball_port():
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        renpy.display.scenelists.init_layers()
        renpy.game.context().scene_lists = renpy.display.scenelists.SceneLists(None, renpy.game.context().images)
        renpy.display.screen.prepare_screens()
        assert (config.screen_width, config.screen_height) == (800, 600)
        assert (persistent.rscript_text_size, persistent.rscript_say_line_chars) == (29, 19)
        assert rscript_use_speaker_images
        assert folder[1] == folder[49] == "grpo"
        lex = renpy.lexer.Lexer([("startup-test", 1, "1 2 90 0 0 0", [])])
        lex.advance()
        load = parse_load(lex)
        assert predict_load(load) == ["grpo 0002"]
        execute_load(load)
        assert layer_info[1] == "grpo 0002"
        process_draw_queue()
        assert rscript_layouts()["confscrn"]["size"] == (518, 387)
        assert rscript_layouts()["compane"]["items"]["hide"] == (179, 1, 17, 17)
        for language in (None, "zh"):
            _preferences.language = language
            assert rscript_ui_image("sel_a", "body").crop == (0, 0, 520, 50)
            assert rscript_ui_image("sel_a", "body_f").crop == (0, 50, 520, 50)
            assert rscript_menu_panel("answer", "sel_a") == ("sel_a", "answer")
            renpy.show_screen("preferences")
            renpy.get_screen("preferences").update()
            renpy.hide_screen("preferences")
            renpy.show_screen("rscript_compane")
            renpy.get_screen("rscript_compane").update()
            renpy.hide_screen("rscript_compane")
            sprite = rscript_ui_image("confscrn", "save_f")
            assert sprite.crop == (0, 21, 85, 21)
        _preferences.language = None
        # Each slot uses its saved chapter, not the current chapter's DT1.
        _r[1] = 1
        metadata = {}
        rscript_save_json(metadata)
        assert metadata["rscript_dt1"] == 1
        _r[1] = 2
        old_json, old_loadable, old_time = FileJson, FileLoadable, FileTime
        try:
            store.FileJson = lambda slot, key: metadata.get(key) if slot == 1 else None
            store.FileLoadable = lambda slot: slot == 1
            store.FileTime = lambda *args: "2026/10/09 12:34"
            assert rscript_slot_image(1).lower().startswith("grps/dt1_0001.")
            assert rscript_slot_image(2) is None
            for page in (1, 10):
                FilePage(page)()
                assert rscript_page_image(str(page)).crop == (0, (page - 1) * 34, 38, 34)
                assert bool(FilePagePrevious(max=10, auto=False, quick=False).get_sensitive()) == (page > 1)
                assert FilePageNext(max=10, auto=False, quick=False).get_sensitive() == (page < 10)
                for language in (None, "zh"):
                    _preferences.language = language
                    for mode, action_type in (("save", FileSave), ("load", FileLoad)):
                        renpy.show_screen(mode)
                        screen = renpy.get_screen(mode)
                        screen.update()
                        buttons = []
                        screen.visit_all(lambda d: buttons.append(d) if isinstance(d, renpy.display.behavior.Button)
                                         and isinstance(d.action, action_type) else None)
                        assert len(buttons) == 10, (mode, buttons)
                        assert buttons[0].style.xpos == 125 and buttons[0].style.ypos == 137
                        assert buttons[5].style.xpos == 400 and buttons[5].style.ypos == 137
                        renpy.hide_screen(mode)
        finally:
            store.FileJson, store.FileLoadable, store.FileTime = old_json, old_loadable, old_time
            _preferences.language = None
            FilePage(1)()
        # Native save sensitivity, autosave flag and direct screen key actions.
        store.save_enabled = store.roll_enabled = 1
        rscript_sync_permissions()
        assert config.save and store._autosave and store._rollback
        renpy.show("layer80", what=Solid("#ffffff"), layer=IMAGE_LAYER)
        layer_info[80] = "grpo_r1 0001"
        rscript_sync_permissions()
        assert not config.save and not store._autosave and not store._rollback
        assert not FileSave(1).get_sensitive()
        assert isinstance(rscript_ui_action(("rollback",)), NullAction)
        assert isinstance(rscript_ui_action(("quick_save",)), NullAction)
        assert rscript_rev_action().identifier is None
        assert isinstance(rscript_system_action(1), NullAction)
        renpy.hide("layer80", layer=IMAGE_LAYER)
        rscript_sync_permissions()
        assert config.save and store._autosave and store._rollback
        layer_info.pop(80)
        store.save_enabled = store.roll_enabled = 0
        rscript_sync_permissions()
        assert not config.save and not store._autosave and not store._rollback
        assert isinstance(rscript_system_action(1), NullAction)
        assert isinstance(rscript_system_action(2), ShowMenu)
        store.save_enabled = store.roll_enabled = 1
        rscript_sync_permissions()
        image = renpy.get_registered_image("grps tbox01b")
        image.find_target()
        assert image.raw_target.filename == "grps/TBOX01B.png", image.raw_target
        assert rscript_wait_image().name == ("grps", "tbox_w")
        assert rscript_audio_file("se", 1) == "wav/wav/0001.ogg"
        assert rscript_audio_file("bgm", 1) == "bgm/Track01.wav"
        _r[8] = 3
        lex = renpy.lexer.Lexer([("draw-test", 1, "1 {1:1,2:2}.get(rscript_signed16(_r[8]),0) 50", [])])
        lex.advance()
        execute_draw(parse_draw(lex))
        assert layer_blend[1] == (0, 50)
        # Check real statement parsing and channel scheduling without playing audio.
        from types import SimpleNamespace
        old_play, old_stop, old_pause, old_loadable = renpy.music.play, renpy.music.stop, renpy.pause, renpy.loadable
        calls = []
        try:
            renpy.music.play = lambda file, **kw: calls.append(("play", file, kw))
            renpy.music.stop = lambda channel="music", **kw: calls.append(("stop", channel, kw))
            renpy.pause = lambda *a, **kw: None
            renpy.loadable = lambda file: file in ("bgm/Track01.wav", "bgm/Track02.wav")
            for line, fade in (("1 1 2000", 2.0), ("2 0 2000", 0.0)):
                lex = renpy.lexer.Lexer([("bgm-test", 1, line, [])])
                lex.advance()
                execute_bgm_on(parse_bgm_on(lex))
                assert calls[-2][2]["fadeout"] == fade
                assert calls[-1][2]["fadein"] == fade and calls[-1][2]["fadeout"] == 0
                assert calls[-2][1] != calls[-1][2]["channel"]
                assert calls[-1][2]["if_changed"] is False  # Restart a reused buffer even if its old track is still fading.
            count = len(calls)
            for number in (0, 2, 999):
                execute_bgm_on(SimpleNamespace(BgmNo=number, Fade=1, FadeLen=2000))
            assert len(calls) == count  # zero/same track/missing file don't interrupt.
            _r[7] = 2
            lex = renpy.lexer.Lexer([("bgm-test", 1, "int(bool(rscript_signed16(_r[7]))) 2000", [])])
            lex.advance()
            execute_bgm_off(parse_bgm_off(lex))
            assert calls[-1] == ("stop", "music", {"fadeout": 2.0})
            assert rscript_bgm_number == 0
            # Other dialects keep the single-channel behavior and modern timing.
            store.rscript_bgm_crossfade = False
            execute_bgm_on(SimpleNamespace(BgmNo=1, Fade=1, FadeLen=350))
            assert calls[-1][2]["channel"] == "music" and calls[-1][2]["fadein"] == .35
            assert calls[-1][2]["fadeout"] is None
            stop_audio()
            assert any(call[:2] == ("stop", "rscript_music") for call in calls)
            assert rscript_bgm_channel == "music" and rscript_bgm_number == 0
            actions = rscript_preference_action("music mute", "enable")
            assert {action.channel for action in actions[1:]} == {"music", "rscript_music"}
        finally:
            renpy.music.play, renpy.music.stop, renpy.pause, renpy.loadable = old_play, old_stop, old_pause, old_loadable
            store.rscript_bgm_crossfade = True
        for values, expected in (((-3, 5, 2), -7), ((3, -5, -2), 7), ((65535, 5, 2), -2)):
            assert rscript_muldev(*values) == expected
        def command(text):
            lex = renpy.lexer.Lexer([("numeric-test", 1, text, [])])
            lex.advance()
            execute_rscript_number(parse_rscript_number(lex))
        command("numreng 1 0 100 0 0")
        command("numloc 1 20 16")
        command("numenable 1 1")
        command("num 1 150 1")
        process_draw_queue()
        assert rscript_numbers[1]["Value"] == 100
        assert renpy.showing("rscript_number_1", layer=IMAGE_LAYER)
        command("num 1 -1 0")
        process_draw_queue()
        assert rscript_numbers[1]["Value"] == 100
        command("numenable 1 0")
        process_draw_queue()
        assert not renpy.showing("rscript_number_1", layer=IMAGE_LAYER)
        # Native BarNN fills use numset's bar offset, not the digit offset.
        command("numload 0 0 1 0")
        command("numreng 0 0 500 0 0")
        command("numloc 0 150 64")
        command("numset 0 0 0 16 1")
        command("numenable 0 1")
        command("num 0 250 0")
        process_draw_queue()
        bar = rscript_number_displayable(rscript_numbers[0]).children[0]
        assert bar.crop == (0, 0, 234, 11), bar.crop
        assert (bar.xpos, bar.ypos) == (16, 1)
        # Native eight-slot right alignment, zero suppression, image lookup.
        digits = rscript_number_displayable(dict(Number=99, Value=42, X1=3, Y1=7)).children
        assert [child.crop for child in digits] == [(0, 40, 6, 10), (0, 20, 6, 10)]
        assert [(child.xpos, child.ypos) for child in digits] == [(39, 7), (45, 7)]
        zero = rscript_number_displayable(dict(Number=99, Value=0)).children
        assert len(zero) == 1 and zero[0].crop == (0, 0, 6, 10) and zero[0].xpos == 42
        assert not rscript_number_displayable(dict(Number=98)).children
        assert not rscript_number_displayable(dict(Number=0, Bar=0, Background=0)).children
        frames = rscript_number_frames(0, 10)
        animated, delay = rscript_number_animation(.05, .05, dict(Number=99), frames)
        assert animated.children[-1].crop == (0, 20, 6, 10) and delay == .05
        animated, delay = rscript_number_animation(2, 2, dict(Number=99), frames)
        assert len(animated.children) == 2 and delay is None
        # Test queued animation/wait/final redraw without playing the fixture.
        old_pause = renpy.pause
        pauses = []
        renpy.pause = pauses.append
        try:
            command("numload 3 99 0 0")
            command("numreng 3 0 100 0 0")
            command("numenable 3 1")
            command("num 3 10 1")
            process_draw_queue()
            assert pauses == [.45] and rscript_numbers[3]["Value"] == 10
            assert not store.draw_queue and not store.draw_queue_delayed
            command("num 3 20 0")
            process_draw_queue()
            assert pauses == [.45] and rscript_numbers[3]["Value"] == 20
            command("num 3 -1 1")
            process_draw_queue()
            assert pauses == [.45] and rscript_numbers[3]["Value"] == 20
            command("numenable 3 0")
            process_draw_queue()
        finally:
            renpy.pause = old_pause
        # Clock units/range retention, timeout and early-selection remainder.
        import time
        old_clock = time.monotonic
        clock = [10.0]
        time.monotonic = lambda: clock[0]
        try:
            _r[1000] = 500
            clock_args = RScriptArguments(Timer=1000, Timeout=1, Cancel=0)
            countdown = rscript_click_countdown(clock_args)
            assert rscript_numbers[0]["Maximum"] == 500
            clock[0] = 10.371
            assert rscript_click_remaining(countdown) == 463
            rscript_click_tick(countdown)
            assert rscript_numbers[0]["Value"] == 463
            clock[0] = 15.001
            assert rscript_click_remaining(countdown) == 0
            clock[0] = 15.011
            old_end = renpy.end_interaction
            ended = []
            try:
                renpy.end_interaction = ended.append
                rscript_click_tick(countdown)
                assert ended == [0] and rscript_numbers[0]["Value"] == 0
            finally:
                renpy.end_interaction = old_end
            assert rscript_click_countdown(RScriptArguments(Timer=0)) is None
            _r[1000] = 100
            rscript_click_countdown(RScriptArguments(Timer=1000, Timeout=0))
            assert rscript_numbers[0]["Maximum"] == 100
        finally:
            time.monotonic = old_clock
        # locmode 0 must reset even unloaded actors left centered by dialogue.
        layer_anchor[12] = layer_anchor[30] = (.5, .5)
        execute_locmode(RScriptArguments(Layer=0, Xmode=0, Ymode=0))
        assert layer_anchor[12] == layer_anchor[30] == (0, 0)
        # Moving a lower layer must not sink it behind every other picture.
        layer_zorder[1] = 82
        move_layer(1, 150, 84, 0, 0)
        process_draw_queue()
        assert dict(renpy.game.context().scene_lists.get_zorder_list(IMAGE_LAYER))["layer1"] == 82
        layer_anchor[1] = (.5, .5)
        renpy.show_screen("rscript_click_screen", options=[(7, False, "grpo 0002", "grpo 0002", absolute(150), absolute(84))], layers={0: 1})
        click_screen = renpy.get_screen("rscript_click_screen")
        click_screen.update()
        buttons = []
        click_screen.visit_all(lambda d: buttons.append(d) if isinstance(d, renpy.display.behavior.Button) else None)
        assert buttons[0].style.xanchor == .5 and buttons[0].style.yanchor == .5
        assert isinstance(buttons[0].style.xpos, absolute)
        renpy.hide_screen("rscript_click_screen")
        for language, expected in ((None, "body"), ("zh", "译文")):
            _preferences.language = language
            text = rscript_prepare_text("^g001" + expected)
            assert text == expected and store.rscript_speaker == 1
            parsed, centered = parse_rscript_text(repr("^m^g001" + expected), True)
            assert centered and parsed == expected and store.rscript_speaker == 1
            assert "rscript_g=" not in parsed
            renpy.show_screen("say", who=None, what=text)
            renpy.get_screen("say").update()
            widget = renpy.get_widget("say", "what")
            widget.refresh_settings()
            assert widget.style.size == 29
            renpy.hide_screen("say")
        if getattr(store, "rscript_test_native_title", False):
            old_load, old_clear = store.loadcls, store.execute_gload
            old_pause, old_play, old_stop = renpy.pause, renpy.music.play, renpy.music.stop
            try:
                store.loadcls = lambda *args, **kwargs: None
                store.execute_gload = lambda *args: None
                renpy.pause = lambda *args, **kwargs: False
                renpy.music.play = renpy.music.stop = lambda *args, **kwargs: None
                # The real 1011 loop must finish for shrinking, growing and mixed gauges.
                for language in (None, "zh"):
                    _preferences.language = language
                    for old, target in (((130, 150, 180), (80, 140, 160)),
                                        ((80, 140, 160), (130, 150, 180)),
                                        ((130, 140, 160), (80, 150, 150))):
                        _r[102] = 0
                        for offset, value in enumerate(old):
                            _r[1024 + offset] = value
                        for offset, value in enumerate(target):
                            _r[1021 + offset] = value
                        renpy.call_in_new_context("_1011")
                        actual = tuple(_r[1024 + i] for i in range(3))
                        assert actual == target, (language, old, target, actual)
                        assert all(_r[990 - i] == 0 for i in range(3))  # Native scratch cleanup ran.
                print("OK: actual JP/ZH 1011 decrement/increment/mixed loops terminate")
            finally:
                store.loadcls, store.execute_gload = old_load, old_clear
                renpy.pause, renpy.music.play, renpy.music.stop = old_pause, old_play, old_stop
                _preferences.language = None
            pause, transition, play, call_screen = renpy.pause, renpy.with_statement, renpy.music.play, renpy.call_screen
            exception_handler = config.exception_handler
            def fail(traceback):
                raise SystemExit("Native title regression failed; see traceback above")
            def click(screen, **kwargs):
                assert screen == "rscript_click_screen", screen
                assert layer_info[1] == "grpo 0002" and layer_info[2] == "grpo 0003"
                assert layer_pos[1] == (90, 0) and layer_pos[2] == (255, 9)
                assert kwargs["options"][0][0] == 1
                assert kwargs["options"][0][2] == "grpo 0011"
                assert all("grpo " in option[2] for option in kwargs["options"])
                return 1
            try:
                renpy.pause = lambda *args, **kwargs: False
                renpy.with_statement = lambda *args, **kwargs: None
                renpy.music.play = lambda *args, **kwargs: None
                renpy.call_screen = click
                config.exception_handler = fail
                for language in (None, "zh"):
                    _preferences.language = language
                    renpy.call_in_new_context("_0000")
                    assert _r[0] == 1
                print("OK: actual JP/ZH 0000 -> 0001 -> 0002 -> title click -> 3000, without a window/audio/player saves")
            finally:
                renpy.pause, renpy.with_statement, renpy.music.play, renpy.call_screen = pause, transition, play, call_screen
                config.exception_handler = exception_handler
        print("OK: native legacy parsers, case-sensitive assets, audio paths, numeric state and dialogue screens")
        return False
    renpy.arguments.register_command("cannonballtest", check_cannonball_port)
