# Disposable SDK command; original EXEs and player saves are never used.
python early:
    def check_sevenbridge_port():
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        renpy.display.scenelists.init_layers()
        renpy.game.context().scene_lists = renpy.display.scenelists.SceneLists(None, renpy.game.context().images)
        renpy.display.screen.prepare_screens()
        sevenbridge_initial_textbox()
        assert (config.screen_width, config.screen_height) == (800, 600)
        assert persistent.rscript_text_size == 24
        assert rscript_voice_groups and rscript_folder_zero_all
        assert rscript_boot_movies == (2, 1)
        for number in (2, 3, 4):
            assert renpy.loadable("mov/%04d.mpg" % number)
        assert cur_textbox == 0 and text_indent == 146
        assert rscript_ui["text_pos"] == (147, 11)
        assert not rscript_ui["game_text_settings"]
        renpy.show_screen("rscript_compane")
        panel = renpy.get_screen("rscript_compane")
        panel.update()
        bars = []
        panel.visit_all(lambda d: bars.append(d) if isinstance(d, renpy.display.behavior.Bar) else None)
        assert len(bars) == 1 and bars[0].style.bar_vertical
        renpy.hide_screen("rscript_compane")
        assert "_0001" not in config.label_overrides
        store.menu_enabled = 0
        assert rscript_system_action(3).screen == "rscript_title_preferences"
        store.menu_enabled = 1
        assert rscript_system_action(3).screen == "preferences"
        store.menu_enabled = 0
        assert rscript_audio_file("voice", 1001) == "voice/1001.ogg"
        assert renpy.loadable(rscript_audio_file("voice", 11001))
        for page in range(1, 11):
            page_image = rscript_page_image(str(page))
            assert page_image is not None
            assert (page_image.style.xminimum, page_image.style.yminimum) == (46, 36)
            name = str(page) if page == 10 else chr(ord("０") + page)
            assert page_image.children[0].get_placement()[:2] == rscript_layouts()["nonbl"]["items"][name][:2]
        metadata = {}
        _r[2] = 1
        rscript_save_json(metadata)
        assert metadata["rscript_dt2"] == 1
        old_json = store.FileJson
        try:
            store.FileJson = lambda slot, key: metadata.get(key)
            assert rscript_slot_image(1) == "grps/dt2_0001.png"
        finally:
            store.FileJson = old_json
        from types import SimpleNamespace
        _r[0] = 7
        execute_getflag(SimpleNamespace(Flag=65535, Mark=1))
        assert _r[0] == 7
        execute_getflag(SimpleNamespace(Flag=65535, Mark=0))
        assert _r[0] == 1
        execute_getflag(SimpleNamespace(Flag=65534, Mark=0))
        assert _r[0] == 0
        execute_gload(SimpleNamespace(CGNum=1, Colormode=0))
        execute_getflag(SimpleNamespace(Flag=1, Mark=0))
        assert _r[0] == 1 and persistent.seen_cg["grpe 0001"]
        execute_gload(SimpleNamespace(CGNum=3001, Colormode=0))
        assert not _r[12001] and persistent.seen_cg["grpe 3001"]
        renpy.show_screen("preferences")
        renpy.get_screen("preferences").update()
        renpy.hide_screen("preferences")
        for name in ("save", "load"):
            renpy.show_screen(name)
            renpy.get_screen(name).update()
            renpy.hide_screen(name)
        print("OK: SevenBridge canvas, voices, progress flags and menu screens")

        class Finished(BaseException):
            pass
        class Failed(BaseException):
            pass
        def fail_fast(traceback):
            raise Failed(str(traceback))
        old_handler = config.exception_handler
        old_pause, old_with = renpy.pause, renpy.with_statement
        old_screen, old_say = renpy.call_screen, renpy.say
        old_play, old_stop = renpy.music.play, renpy.music.stop
        old_restart = renpy.full_restart
        old_movie = renpy.movie_cutscene
        old_language = _preferences.language
        old_label_callbacks = config.label_callbacks[:]
        calls, voices, movies, labels = [], [], [], []
        try:
            config.exception_handler = fail_fast
            renpy.pause = lambda *a, **kw: None
            renpy.with_statement = lambda *a, **kw: None
            renpy.music.play = lambda filename, *a, **kw: voices.append((filename, kw))
            renpy.music.stop = lambda *a, **kw: None
            renpy.full_restart = lambda *a, **kw: (_ for _ in ()).throw(Finished())
            def movie(filename):
                assert renpy.loadable(filename), filename
                movies.append(filename)
            renpy.movie_cutscene = movie
            config.label_callbacks.append(lambda name, abnormal: labels.append(name))
            # Command mode has no menu context; run only the splashscreen's Python.
            node = renpy.game.script.lookup("splashscreen")
            while not isinstance(node, renpy.ast.Python):
                node = node.next
            renpy.python.py_exec_bytecode(node.code.bytecode)
            assert movies == ["mov/%04d.mpg" % number for number in (2, 1)
                              if renpy.loadable("mov/%04d.mpg" % number)], movies
            movies.clear()
            for number in (2, 3, 4):
                execute_movie(SimpleNamespace(MovieNo=number))
            assert movies == ["mov/0002.mpg", "mov/0003.mpg", "mov/0004.mpg"]
            movies.clear()
            def click(name, **kwargs):
                assert name == "rscript_click_screen", name
                options = kwargs["options"]
                calls.append([item[0] for item in options])
                assert len(calls) < 20, calls
                assert 1 in calls[-1], calls
                return 1
            def say(who, what, **kwargs):
                assert ("跨过去吧" if selected_language == "zh" else "越えてゆけ") in what, what
                assert store.rscript_speaker == 3
                assert any(file == "voice/1001.ogg" for file, args in voices), voices
                if selected_language is None and any(name == "zh" for name, _ in rscript_languages):
                    voice_count, label_count = len(voices), len(labels)
                    renpy.show_screen("say", who=None, what=what)
                    for language, phrase in (("zh", "跨过去吧"), (None, "越えてゆけ")):
                        renpy.run(Language(language))
                        renpy.show_screen("say", who=None, what=what)
                        renpy.get_screen("say").update()
                        actual = "".join(renpy.get_widget("say", "what").text)
                        assert phrase in actual, (language, actual, store.rscript_dialogue_language,
                                                  store.rscript_speaker_visible, store.rscript_dialogue_sources)
                        assert store.rscript_speaker == 3
                        assert (len(voices), len(labels)) == (voice_count, label_count)
                    renpy.hide_screen("say")
                raise Finished()
            renpy.call_screen, renpy.say = click, say
            languages = [None] + (["zh"] if any(name == "zh" for name, _ in rscript_languages) else [])
            for selected_language in languages:
                renpy.change_language(selected_language)
                calls.clear()
                voices.clear()
                labels.clear()
                for path in ("grps/dt2_0001.png", "grps/confscrn/close.png", "grps/gf001.png"):
                    expected = ("tl/zh/" if selected_language == "zh" else "") + path
                    assert renpy.loadable(expected, tl=False), expected
                    assert rscript_image_path(path) == expected, (path, rscript_image_path(path))
                if selected_language == "zh":
                    for page in range(1, 11):
                        name = str(page) if page == 10 else chr(ord("０") + page)
                        path = "grps/nonbl/%s.png" % name
                        assert rscript_image_path(path) == "tl/zh/" + path, path
                assert rscript_image_path("grpe/3001.png") == "grpe/3001.png"
                try:
                    renpy.call_in_new_context("_0000")
                except Finished:
                    pass
                else:
                    raise AssertionError("native title did not reach the opening scene")
                assert calls, "title choice was not executed"
                assert "_2001" in labels, labels
                print("OK: SevenBridge script 0000 -> title -> opening, name and voice", selected_language, calls)
            print("OK: SevenBridge boot and scenario movie paths are loadable")
            for scene, choice, exit_value in (("0201", 1, 13), ("0301", 5001, 20), ("0400", 1, 49)):
                persistent.seen_cg.update(("grpe %04d" % number, True) for number in range(1, 3301))
                for key in range(8000, 8030):
                    _r[key] = 1
                _r[7999] = 1
                steps, dialogue = [], []
                labels.clear()
                store.jump_back_point = "sdk-gallery"  # Command mode has no rollback log.
                def gallery_click(name, **kwargs):
                    assert name == "rscript_click_screen", name
                    options = [item[0] for item in kwargs["options"]]
                    steps.append(options)
                    assert len(steps) <= 4, (scene, steps)
                    if len(steps) == 1:
                        assert choice in options, (scene, options)
                        return choice
                    if len(steps) == 2:
                        assert exit_value in options, (scene, options)
                        if scene == "0400":
                            assert any(path.startswith("bgm/Track01.") for path, kw in voices)
                        return exit_value
                    assert store.layer_info[CG_LAYER] == "grpe 3001", store.layer_info
                    assert all(path.startswith("grpo ") for layer, path in store.layer_info.items()
                               if isinstance(layer, int) and isinstance(path, str)), store.layer_info
                    raise Finished()
                renpy.call_screen = gallery_click
                renpy.say = lambda who, what, **kw: dialogue.append(what)
                try:
                    renpy.call_in_new_context("_" + scene)
                except Finished:
                    pass
                else:
                    raise AssertionError(("gallery did not return to title", scene, steps, dict(store.layer_info)))
                assert len(steps) == 3, (scene, steps)
                assert "_" + scene in labels, (scene, labels)
                if scene == "0201":
                    assert "sevenbridge_cg_body" in labels, labels
                    assert not any(name.startswith("_rscript_variant") for name in labels), labels
                if scene == "0301":
                    assert dialogue, "scene replay did not execute dialogue"
                    assert "_5001" in labels, labels
                print("OK: SevenBridge gallery return", selected_language, scene, len(dialogue), "dialogue lines")
        finally:
            config.exception_handler = old_handler
            renpy.pause, renpy.with_statement = old_pause, old_with
            renpy.call_screen, renpy.say = old_screen, old_say
            renpy.music.play, renpy.music.stop = old_play, old_stop
            renpy.full_restart = old_restart
            renpy.movie_cutscene = old_movie
            config.label_callbacks = old_label_callbacks
            renpy.change_language(old_language)
        return False
    renpy.arguments.register_command("sevenbridgetest", check_sevenbridge_port)
