# Disposable project command: real Ren'Py parsers/screens, no game save data.
python early:
    def check_modern_port():
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        renpy.display.scenelists.init_layers()
        renpy.game.context().scene_lists = renpy.display.scenelists.SceneLists(None, renpy.game.context().images)
        renpy.display.screen.prepare_screens()
        assert (config.screen_width, config.screen_height) == (1280, 720)
        assert persistent.rscript_text_size == 32
        assert rscript_label("0001%REP") == "_g_0001_REP"
        assert rscript_modern_text("|漢字[かんじ]^nnext") == "{rb}漢字{/rb}{rt}かんじ{/rt}^nnext"
        lex = renpy.lexer.Lexer([("test", 1, "1 3 7", [])])
        lex.advance()
        execute_flagset(parse_flagset(lex))
        assert [_r[i] for i in range(1, 4)] == [7, 7, 7]
        execute_dynsel(repr(("Question", 0)))
        for answer in (("Always", 1, 0, 0), ("Once", 2, 5024, 0), ("Unlocked", 3, 5025, 1)):
            execute_dynans(repr(answer))
        from types import SimpleNamespace
        args = SimpleNamespace(Effect=2, Layout=0, Mode=1)
        old_menu = renpy.display_menu
        captured = []
        try:
            renpy.display_menu = lambda options: (captured.append(options), options[0][1])[1]
            execute_dyndo(args)
            assert captured[-1] == [("Always", 1), ("Once", 2)] and _r[0] == 1
            _r[5024] = _r[5025] = 1
            execute_dyndo(args)
            assert captured[-1] == [("Always", 1), ("Unlocked", 3)]
            execute_dynsel(repr(("Reset", 0)))
            assert not rscript_dynamic_answers
            execute_dynnext(repr("Next"))
            try:
                execute_dyndo(args)
            except Exception as error:
                assert "pagination" in str(error)
            else:
                raise AssertionError("pagination must not silently lose answers")
        finally:
            renpy.display_menu = old_menu
        old_loadable = renpy.loadable
        try:
            renpy.loadable = lambda path: path in {"voice/1/0001.wav", "wav/0033.wav"}
            assert rscript_audio_file("voice", 10001) == "voice/1/0001.wav"
            assert rscript_audio_file("se", 33) == "wav/0033.wav"
        finally:
            renpy.loadable = old_loadable
        execute_rscript_locmode(SimpleNamespace(Layer=0, XMode=1, YMode=1, Mode=0))
        assert all(layer_anchor[i] == (0.5, 0.5) for i in range(100))
        assert renpy.has_image("grpo_ex 9999")
        calls = []
        old_say = renpy.say
        old_queue = store.queue_draw
        old_process = store.process_draw_queue
        try:
            store.queue_draw = lambda *args, **kwargs: None
            store.process_draw_queue = lambda: None
            renpy.say = lambda who, what, **kwargs: calls.append((who.name, what, kwargs['interact']))
            store.jump_back_point = 1  # No rollback log exists in command-mode tests.
            execute_rscript_say(repr(("Alice", "|漢字[かんじ]^nnext", 1)))
            assert calls[-1][0] == "Alice" and "{rb}漢字{/rb}" in calls[-1][1]
            parsed = calls[-1][1]
            rscript_dialogue_begin()
            renpy.show_screen("say", who="Alice", what=parsed)
            renpy.get_screen("say").update()
            assert renpy.get_widget("say", "what").text == [parsed]
            assert renpy.get_widget("say", "who").text == ["Alice"]
            renpy.hide_screen("say")
            execute_rscript_say(repr(("Alice", "nonblocking", 0)))
            assert calls[-1] == ("Alice", "nonblocking", False)
            execute_rscript_append(repr((" plus", 0)))
            assert calls[-1][2] is False and "nonblocking{fast} plus" in calls[-1][1]
        finally:
            renpy.say = old_say
            store.queue_draw = old_queue
            store.process_draw_queue = old_process
        print("OK: native modern choices, registers, voices, canvas, names and ruby")
        return False
    renpy.arguments.register_command("modernporttest", check_modern_port)
