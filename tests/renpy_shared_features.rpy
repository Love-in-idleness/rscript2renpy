# Run on a disposable generated project, never on a player's save directory.
python early:
    def check_shared_port_features():
        assert config.version == "1.2"
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        fields = ("rscript_text_size", "rscript_say_line_chars",
                  "rscript_oload_line_chars", "rscript_line_spacing")
        defaults = (22, 19, 20, 7) if rscript_use_speaker_images else (29, 21, 20, -5)
        assert tuple(getattr(persistent, field) for field in fields) == defaults
        # Native persistent defaults must survive reset and retain user choices.
        for values in ((None,) * 4, (31, 23, 24, -3)):
            for field, value in zip(fields, values):
                setattr(persistent, field, value)
            renpy.execute_default_statement(False)
            assert tuple(getattr(persistent, field) for field in fields) == (
                defaults if values[0] is None else values)
        for field, value in zip(fields, defaults):
            setattr(persistent, field, value)
        original_save = renpy.save_persistent
        original_notify = renpy.notify
        renpy.save_persistent = lambda: None
        renpy.notify = lambda text: None
        persistent.rscript_text_size = rscript_base_text_size
        persistent.rscript_text_font = rscript_default_font
        renpy.run(rscript_preference_action("text speed", 75))
        assert persistent.rscript_text_cps == 75
        assert rscript_preference_action("text speed", 75).get_selected()
        renpy.run(rscript_preference_action("text speed", 0))
        assert persistent.rscript_text_cps == 0
        persistent.rscript_text_cps = 20
        # The new migration must run even if the previous Forest font migration ran.
        persistent.rscript_opacity_migrated = False
        persistent.textbox_opacity = 0.4
        rscript_migrate_ui_preferences()
        assert persistent.rscript_textbox_opacity == 0.4
        persistent.textbox_opacity = 0.9
        rscript_migrate_ui_preferences()
        assert persistent.rscript_textbox_opacity == 0.4
        persistent.rscript_textbox_opacity = 1.0
        lex = renpy.lexer.Lexer([("shared-test", 1, "20 3 0 0", [])])
        lex.advance()
        execute_setclksys(parse_setclksys(lex))
        lex = renpy.lexer.Lexer([("shared-test", 1, "20 707 12 34", [])])
        lex.advance()
        execute_setlink(parse_setlink(lex))
        assert rscript_click_values[20] == (3, True)
        assert rscript_click_links[20] == (707, 12, 34)
        old_screen = renpy.call_screen
        old_folder, old_info = dict(store.folder), dict(store.layer_info)
        old_grid = (layer_x_grid, layer_y_grid)
        captured = []
        try:
            store.folder[20] = "grpo"
            store.layer_info[20] = "idle image"
            store.layer_x_grid, store.layer_y_grid = 2, 3
            renpy.call_screen = lambda name, **kwargs: (captured.append((name, kwargs)), 9)[1]
            execute_click(None)
            assert store._r[0] == 9
            assert not rscript_click_values and not rscript_click_links
            point = captured[0][1]["options"][0]
            assert point[:4] == (3, True, "idle image", "grpo 0707")
            assert point[4:] == ((24, 102) if rscript_click_grid else (12, 34))
            from types import SimpleNamespace
            execute_folder(SimpleNamespace(Layer=0, Folder="grpo_tp"))
            assert all(store.folder[number] == "grpo_tp" for number in range(100))
        finally:
            renpy.call_screen = old_screen
            store.folder, store.layer_info = old_folder, old_info
            store.layer_x_grid, store.layer_y_grid = old_grid
        old_json = store.FileJson
        try:
            store.FileJson = lambda slot, key: 707 if key == "forest_dt1" else None
            assert rscript_slot_image(1) is None  # Missing dt1 does not try to load a missing image.
        finally:
            store.FileJson = old_json
        old_loadable = renpy.loadable
        try:
            for first in (0, 1):
                images = {"images/grps/nonbl/%d.png" % number
                          for number in range(first, first + 10)}
                renpy.loadable = lambda path: path in images
                for page in range(1, 11):
                    assert rscript_page_image(str(page)) == (
                        "images/grps/nonbl/%d.png" % (page - 1 + first))
                assert rscript_page_image("auto") is None
                assert rscript_page_image("11") is None
        finally:
            renpy.loadable = old_loadable
        for raw in ("甲：乙", " 甲   乙 ", "\u3000甲\u00a0乙 ", "^n ^n甲…— "):
            lex = renpy.lexer.Lexer([("shared-test", 1, "jp " + repr(raw), [])])
            lex.advance()
            language, speaker, body = parse_say(lex)
            assert speaker is None and eval(body) == raw, (raw, speaker, body)
        lex = renpy.lexer.Lexer([("shared-test", 1, "jp 'Alice'：' 甲  乙 '", [])])
        lex.advance()
        language, speaker, body = parse_say(lex)
        assert eval(speaker) == "Alice" and eval(body) == " 甲  乙 "
        persistent.rscript_say_line_chars = 19
        persistent.rscript_oload_line_chars = 20
        persistent.rscript_line_spacing = 7
        assert rscript_text_settings("say", 22)[1:] == (rscript_base_text_size, 19, 7)
        assert rscript_text_settings("oload", 22)[1:] == (22, 20, 7)
        persistent.rscript_text_size *= 2
        assert rscript_text_settings("oload", 22)[1] == 44
        persistent.rscript_text_size = rscript_base_text_size
        assert len(rscript_fonts()) >= 4
        rscript_cycle_font(1)
        assert rscript_current_font() != rscript_default_font
        persistent.rscript_text_font = rscript_default_font

        # Confirmed Khime controls are handled through the same shared parser.
        assert rscript_green_color() == ("#7FDFA5" if not rscript_use_speaker_images else "#FFFFFF")
        for control, color in (("CR", "#B73333"), ("CB", "#2020FF"),
                               ("CS", "#79F1F2"), ("CP", "#F8B1EF"),
                               ("CV", "#C187F6"), ("CO", "#FAA25A")):
            parsed, _ = parse_rscript_text(repr("^" + control + "甲^CW乙"), True)
            assert "{color=" + color + "}" in parsed and "^" not in parsed
            plain, _ = parse_rscript_text(repr("^" + control + "甲^CW乙"), False)
            assert plain == "甲乙"
        parsed, centered = parse_rscript_text(repr("^FM甲^CR乙^FG丙^CW丁^V-0129^N^M戊"), True)
        assert centered and "－０１２９" in parsed and "^" not in parsed
        assert "{font=" in parsed
        if not rscript_use_speaker_images:
            assert "{font=fonts/simhei.ttf}" in parsed
        assert "^G707" not in rscript_menu_text("^G707选项")

        try:
            persistent._reg = {7001: 3}
            persistent.seen_cg = {"0001": True}
            rscript_save_progress()
            rscript_clear_progress()
            assert persistent._reg == {} and persistent.seen_cg == {}
            rscript_load_progress()
            assert persistent._reg == {7001: 3}
            assert persistent.seen_cg == {"0001": True}
            if rscript_use_speaker_images:
                persistent.rscript_forest_preferences_migrated = False
                persistent.forest_text_size = 26
                forest_migrate_preferences()
                assert persistent.rscript_text_size == 26
                persistent.forest_text_size = 31
                forest_migrate_preferences()
                assert persistent.rscript_text_size == 26
                persistent.rscript_text_size = rscript_base_text_size
        finally:
            renpy.save_persistent = original_save
            renpy.notify = original_notify

        store._preferences.language = "fixture"
        store.rscript_wiki_keywords = {"fixture": [("甲词乙", "https://example.test/wiki", "词")]}
        persistent.rscript_wiki_mode = False
        parsed, centered = parse_rscript_text(repr("^m甲^cg词^cw乙^n^n"), True)
        assert centered and "#FFFFFF" in parsed and "#D7FFB3" not in parsed
        persistent.rscript_wiki_mode = True
        parsed, centered = parse_rscript_text(repr("^m甲^cg词^cw乙"), True)
        assert centered and "{a=https://example.test/wiki}" in parsed
        assert "#D7FFB3" in parsed
        assert "#FFDE00" in rscript_menu_text("^cy选项^cw")
        assert "^g707" not in rscript_menu_text("^g707选项")
        store._preferences.language = None
        rscript_dialogue_begin()
        rscript_dialogue_end()
        assert not rscript_speaker_visible
        if rscript_use_speaker_images:
            rscript_dialogue_begin()
            parsed, _ = parse_rscript_text(repr("^g707甲^g707乙"), True)
            assert rscript_speaker == 707 and "{rscript_g=707:" in parsed
            rscript_dialogue_end()
            assert not rscript_speaker_visible
        assert renpy.music.channel_defined("rscript_voice")

        # Update native screens to catch missing variables/properties and
        # verify the same controls exist in both games (lint does not do this).
        renpy.display.screen.prepare_screens()
        old_afm_time = _preferences.afm_time
        renpy.show_screen("preferences")
        preference_screen = renpy.get_screen("preferences")
        preference_screen.update()
        auto_bars = []
        preference_screen.visit_all(lambda d: auto_bars.append(d)
                                    if isinstance(d, renpy.display.behavior.Bar) else None)
        assert len(auto_bars) == 1
        auto_bar = auto_bars[0]
        assert not auto_bar.style.bar_invert
        auto_bar.adjustment.change(5)
        fast_delay = _preferences.afm_time
        auto_bar.adjustment.change(20)
        assert 0 < fast_delay < _preferences.afm_time
        _preferences.afm_time = old_afm_time
        renpy.hide_screen("preferences")
        # <NN> chooses the requested skin for both prompts and answers, without
        # discarding translated text or disturbing Forest image-only choices.
        assert rscript_menu_panel("<01> 甲<02>乙 ", "sel_a") == ("sel_a01", " 甲<02>乙 ")
        assert rscript_menu_panel("<02>选项", "sel_a") == ("sel_a02", "选项")
        assert rscript_menu_panel("<01>问题", "sel_q") == ("sel_q01", "问题")
        assert rscript_menu_panel("甲<01>乙", "sel_a") == ("sel_a00", "甲<01>乙")
        assert rscript_menu_panel("<bad>甲", "sel_a") == ("sel_a00", "<bad>甲")
        assert rscript_menu_panel("<99>甲", "sel_a") == ("sel_a", "甲")
        assert rscript_menu_panel("<99>甲", "sel_q") == (None, "甲")
        store._r[5] = 2
        assert rscript_menu_panel("rscript_asset_5", "sel_a") == ("sel_a02", "")
        if rscript_use_speaker_images:
            assert rscript_menu_panel("2", "sel_a") == ("sel_a02", "")
        store.shared_skin_caption = "<02>译文"
        assert rscript_menu_panel("[shared_skin_caption]", "sel_a") == ("sel_a02", "译文")
        renpy.show_screen("rscript_choice", prompt="<01>问题",
                          items=[SimpleNamespace(caption="[shared_skin_caption]", action=Return(7))])
        skin_screen = renpy.get_screen("rscript_choice")
        skin_screen.update()
        skin_texts, skin_images, skin_actions = [], [], []
        def collect_skin(displayable):
            if isinstance(displayable, renpy.text.text.Text):
                skin_texts.append("".join(displayable.text))
            if isinstance(displayable, renpy.display.im.Image):
                skin_images.append(displayable.filename)
            if isinstance(displayable, renpy.display.behavior.Button):
                skin_actions.append(displayable.action)
        skin_screen.visit_all(collect_skin)
        assert "问题" in skin_texts and "译文" in skin_texts, skin_texts
        assert not any("<01>" in text or "<02>" in text for text in skin_texts)
        assert "images/grps/sel_q01/body.png" in skin_images, skin_images
        assert "images/grps/sel_a02/body.png" in skin_images, skin_images
        assert "images/grps/sel_a00/body.png" not in skin_images, skin_images
        assert len(skin_actions) == 1 and skin_actions[0].value == 7, skin_actions
        renpy.hide_screen("rscript_choice")
        # Inspect real native actions: rev targets the recorded choice,
        # while bak remains a one-step rollback. No player progress is changed.
        previous_point = store.jump_back_point
        try:
            for point in (None, 12345):
                store.jump_back_point = point
                renpy.show_screen("rscript_compane")
                panel = renpy.get_screen("rscript_compane")
                panel.update()
                actions = []
                def collect_actions(displayable):
                    if isinstance(displayable, renpy.display.behavior.Button):
                        actions.append(displayable.action)
                panel.visit_all(collect_actions)
                assert len(actions) == 2, actions
                assert sum(isinstance(action, Rollback) for action in actions) == 1
                targets = [action.identifier for action in actions
                           if isinstance(action, RollbackToIdentifier)]
                assert targets == [point], targets
                if point is None:
                    assert not any(action.get_sensitive() for action in actions
                                   if isinstance(action, RollbackToIdentifier))
                assert rscript_rev_action(False).identifier is None
                renpy.hide_screen("rscript_compane")
        finally:
            store.jump_back_point = previous_point
        renpy.show_screen("rscript_text_preferences")
        screen = renpy.get_screen("rscript_text_preferences")
        screen.update()
        captions = []
        texts = []
        def collect(displayable):
            if isinstance(displayable, renpy.display.behavior.Button):
                captions.append("".join(displayable.child.text))
            if isinstance(displayable, renpy.text.text.Text):
                texts.append("".join(displayable.text))
        screen.visit_all(collect)
        assert "Text Speed" not in texts, texts
        for caption in ("Previous Font", "Next Font", "Save Backup",
                        "Load Backup", "Clear Progress", "Back"):
            assert caption in captions, captions
        renpy.hide_screen("rscript_text_preferences")
        renpy.show_screen("say", who=None, what="甲乙。", center=True)
        renpy.get_screen("say").update()
        assert isinstance(renpy.get_widget("say", "what"), RScriptText)
        renpy.hide_screen("say")
        print("OK: shared settings, fonts, progress, Wiki, speaker lifetime and native menus: " + config.name)
        return False
    renpy.arguments.register_command("sharedporttest", check_shared_port_features)
