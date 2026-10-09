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
        image = renpy.get_registered_image("grps tbox01b")
        image.find_target()
        assert image.raw_target.filename == "grps/TBOX01B.png", image.raw_target
        assert rscript_wait_image().name == ("grps", "tbox_w")
        assert rscript_audio_file("se", 1) == "wav/wav/0001.ogg"
        assert rscript_audio_file("bgm", 1) == "bgm/Track01.wav"
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
        for language, expected in ((None, "body"), ("zh", "译文")):
            _preferences.language = language
            text = rscript_prepare_text("^g001" + expected)
            assert text == expected and store.rscript_speaker == 1
            renpy.show_screen("say", who=None, what=text)
            renpy.get_screen("say").update()
            widget = renpy.get_widget("say", "what")
            widget.refresh_settings()
            assert widget.style.size == 29
            renpy.hide_screen("say")
        if getattr(store, "rscript_test_native_title", False):
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
