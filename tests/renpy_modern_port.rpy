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
        assert parse_rscript_text(repr("|漢字[かんじ]^nnext"), True)[0] == "{rb}漢字{/rb}{rt}かんじ{/rt}\nnext"
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
        # 0511: each icon has two independent setlink slots. Slot 1 must not
        # replace the slot-0 hit position or become a huge button at (0, 0).
        old_click_screen = renpy.call_screen
        old_folder, old_info = dict(store.folder), dict(store.layer_info)
        captured = []
        try:
            execute_resetclk(None)
            # 0201/0301/0351 disable locked thumbnails individually. The
            # navigation buttons must survive even when every thumbnail locks.
            for layer, value in ((12, 12), (47, 91), (48, 92), (49, 99)):
                store.folder[layer] = "grpo_ex"
                store.layer_info[layer] = "grpo_ex %04d" % layer
                execute_setclk(SimpleNamespace(Layer=layer, Value=value))
                execute_setlink(SimpleNamespace(Layer=layer, HoverCG=layer + 100,
                                               xLoc=layer, yLoc=642, Slot=0))
                execute_setlink(SimpleNamespace(Layer=layer, HoverCG=layer + 200,
                                               xLoc=0, yLoc=665, Slot=1))
            _r[31] = 12
            for expression in ("0", "_r[31]", "_r[31]"):
                lex = renpy.lexer.Lexer([("0201-test", 1, expression, [])])
                lex.advance()
                execute_resetclk(parse_resetclk(lex))
                if expression == "0":
                    assert set(rscript_click_values) == {12, 47, 48, 49}
            for bindings in (rscript_click_values, rscript_click_links, rscript_click_previews):
                assert set(bindings) == {47, 48, 49}
            renpy.call_screen = lambda name, **kwargs: (captured.append(kwargs), 99)[1]
            execute_click(None)
            assert _r[0] == 99
            assert [option[0] for option in captured[0]["options"]] == [91, 92, 99]
            captured.clear()
            for layer, cg, hover, value, x, y in ((19, 9, 109, 1090, 569, 420),
                                                  (22, 12, 112, 1070, 450, 227),
                                                  (23, 13, 113, 1080, 639, 200)):
                store.folder[layer] = "grpo_map"
                store.layer_info[layer] = "grpo_map %04d" % cg
                for text, parse, execute in (
                    ("%d %d %d %d 0" % (layer, hover, x, y), parse_setlink, execute_setlink),
                    ("%d %d 0 0 1" % (layer, value), parse_setlink, execute_setlink),
                    ("%d %d 3 1" % (layer, value), parse_setclk, execute_setclk)):
                    lex = renpy.lexer.Lexer([("0511-test", 1, text, [])])
                    lex.advance()
                    execute(parse(lex))
            renpy.call_screen = lambda name, **kwargs: (captured.append(kwargs), 1070)[1]
            execute_click(None)
            assert _r[0] == 1070
            assert not rscript_click_links and not rscript_click_previews
            options, previews = captured[0]["options"], captured[0]["previews"]
            assert [option[4:] for option in options] == [(569, 420), (450, 227), (639, 200)]
            assert previews == {0: ("grpo_map 1090", 0, 0), 1: ("grpo_map 1070", 0, 0), 2: ("grpo_map 1080", 0, 0)}
            renpy.show_screen("rscript_click_screen", options=options, previews=previews)
            screen = renpy.get_screen("rscript_click_screen")
            screen.update()
            buttons = []
            screen.visit_all(lambda d: buttons.append(d) if isinstance(d, renpy.display.behavior.ImageButton) else None)
            assert len(buttons) == 3
            # ScreenDisplayable.event/focus normally supplies this context.
            renpy.display.screen.push_current_screen(screen)
            try:
                for index, button in enumerate(buttons):
                    assert (button.style.xpos, button.style.ypos) == options[index][4:]
                    assert button.style.focus_mask is True
                    assert renpy.run(button.action) == options[index][0]
                    renpy.run(button.hovered)
                    renpy.display.screen.updated_screens.discard(screen)
                    screen.update()
                    assert screen.scope["preview"] == previews[index]
                    assert renpy.get_widget("rscript_click_screen", "rscript_click_preview") is not None
                    renpy.run(button.unhovered)
                    renpy.display.screen.updated_screens.discard(screen)
                    screen.update()
                    assert renpy.get_widget("rscript_click_screen", "rscript_click_preview") is None
            finally:
                renpy.display.screen.pop_current_screen()
            renpy.hide_screen("rscript_click_screen")
        finally:
            renpy.call_screen = old_click_screen
            store.folder, store.layer_info = old_folder, old_info
            execute_resetclk(None)
        native_buttons = rscript_grps_layout["compane"]["controls"]
        assert set(native_buttons) == {"rev", "bak", "fow", "next", "skip", "auto", "save", "load", "qsave", "qload", "voc", "menu", "hide"}
        for spec in native_buttons.values():
            assert rscript_ui_action(spec) is not None
        settings = rscript_grps_layout["confscrn"]["controls"]
        original_background_audio = _preferences.audio_when_unfocused
        original_voice_stop = persistent.rscript_stop_voice_on_advance
        try:
            for name, expected in (("bgr_off", False), ("bgr_on", True)):
                action = rscript_ui_action(settings[name])
                action()
                assert _preferences.audio_when_unfocused is expected
                assert action.get_selected()
                other = "bgr_on" if name == "bgr_off" else "bgr_off"
                assert not rscript_ui_action(settings[other]).get_selected()
            for name, expected in (("vocst_off", True), ("vocst_on", False)):
                action = rscript_ui_action(settings[name])
                action()
                assert persistent.rscript_stop_voice_on_advance is expected
                assert action.get_selected()
        finally:
            _preferences.audio_when_unfocused = original_background_audio
            persistent.rscript_stop_voice_on_advance = original_voice_stop
        for screen_name in ("rscript_compane", "preferences", "rscript_font_picker", "save", "load"):
            renpy.show_screen(screen_name)
            screen = renpy.get_screen(screen_name)
            screen.update()
            if screen_name == "rscript_compane":
                buttons = []
                screen.visit_all(lambda d: buttons.append(d) if isinstance(d, renpy.display.behavior.ImageButton) else None)
                assert len(buttons) == 13, len(buttons)
            renpy.hide_screen(screen_name)
        original_newest = store.FileNewest
        try:
            store.FileNewest = lambda slot: slot == 1
            renpy.show_screen("save")
            renpy.get_screen("save").update()
            renpy.hide_screen("save")
        finally:
            store.FileNewest = original_newest
        original_language = _preferences.language
        _preferences.language = "zh"
        assert rscript_layouts()["compane"]["items"]["qload"][:2] == (9, 4)
        assert rscript_grps_layout["compane"]["items"]["qload"][:2] != (9, 4)
        assert len(rscript_layouts()["compane"]["controls"]) == 13
        _preferences.language = original_language
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
            execute_rscript_append(repr((" |追加[ついか]", 0)))
            assert "{fast} {rb}追加{/rb}{rt}ついか{/rt}" in calls[-1][1]
            old_loadcls = store.loadcls
            objects = []
            try:
                store.loadcls = lambda *args, **kwargs: objects.append(kwargs["displayable"])
                lex = renpy.lexer.Lexer([("ruby-object-test", 1, "21 0 0 0 0 '|字幕[ルビ]'", [])])
                lex.advance()
                execute_oload(parse_oload(lex))
                assert objects[0].text == ["{rb}字幕{/rb}{rt}ルビ{/rt}"]
                assert objects[0].rscript_kind == "oload"
            finally:
                store.loadcls = old_loadcls
        finally:
            renpy.say = old_say
            store.queue_draw = old_queue
            store.process_draw_queue = old_process
        print("OK: native modern choices, registers, voices, canvas, names and ruby")
        return False
    renpy.arguments.register_command("modernporttest", check_modern_port)
