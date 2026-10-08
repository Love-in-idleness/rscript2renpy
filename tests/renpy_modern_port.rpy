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
        assert persistent.rscript_line_spacing == -7
        assert rscript_ruby_scale == 13 / 32
        assert rscript_label("0001%REP") == "_g_0001_REP"
        assert parse_rscript_text(repr("|漢字[かんじ]^nnext"), True)[0] == "{rb}漢字{/rb}{rt}かんじ{/rt}\nnext"
        sample, _ = parse_rscript_text(repr("失去了阿德拉这位监督角色，不再有必要继续研习造化术以成为|少女[Ｍａｉｄｅｎ]。直到包围学园的白色荆棘消失为止，现在只要一直等待就好。"), True)
        renpy.show_screen("say", who=None, what=sample)
        renpy.get_screen("say").update()
        sample_text = renpy.get_widget("say", "what")
        sample_text.refresh_settings()
        measured = renpy.text.text.Layout(sample_text, 1280, 720, {}, size_only=True, drawable_res=False)
        assert measured.size[1] <= 694 - 503 - 58, measured.size
        baselines = sorted({g.y for p in measured.paragraph_glyphs for g in p if g.ruby < 2})
        assert len(baselines) == 3 and baselines[1] - baselines[0] == baselines[2] - baselines[1]
        renpy.text.text.textsupport.place_ruby(measured.paragraph_glyphs[0], sample_text.style.ruby_style.yoffset, 0, *measured.size)
        # Check visible ink fits between the previous body row and
        # the annotated row, rather than just checking nominal font boxes.
        normal_bottom = base_top = ruby_top = ruby_bottom = None
        for paragraph in measured.paragraphs:
            for segment, content in paragraph:
                bounds = segment.bounds(segment.glyphs(content, measured), (0, 0, 0, 0), measured)
                if segment.ruby_bottom:
                    base_top = baselines[1] + bounds[1]
                elif segment.ruby_top:
                    glyph = next(g for p in measured.paragraph_glyphs for g in p if g.ruby == 2)
                    ruby_top, ruby_bottom = glyph.y + bounds[1], glyph.y + bounds[3]
                else:
                    normal_bottom = max(normal_bottom or 0, baselines[0] + bounds[3])
        assert normal_bottom <= ruby_top < ruby_bottom <= base_top, (normal_bottom, ruby_top, ruby_bottom, base_top)
        renpy.hide_screen("say")
        print("Evermaiden default dialogue: 3 lines, height", measured.size[1], "ruby inside existing gap")
        def command(parser, executor, text):
            lex = renpy.lexer.Lexer([("layout-test", 1, text, [])])
            lex.advance()
            executor(parser(lex))
        command(parse_tboxloc, execute_tboxloc, "0 0 503")
        command(parse_texloc, execute_texloc, "0 188 58 898 150")
        command(parse_namloc, execute_namloc, "0 124 17 650 65")
        command(parse_cmploc, execute_cmploc, "335 694")
        command(parse_waitloc, execute_waitloc, "0 1080 135")
        command(parse_waitcol, execute_waitcol, "0 255 128 64")
        command(parse_waitlod, execute_waitlod, "0 2")
        command(parse_texsize, execute_texsize, "0 24")
        command(parse_texcolor, execute_texcolor, "0 4")
        command(parse_texruby, execute_texruby, "0 0 13 9")
        assert rscript_compane_position == (335, 694)
        state = rscript_textbox_state()
        assert state["text_rect"] == (188, 58, 898, 150)
        assert state["name_rect"] == (124, 17, 650, 65)
        indicator = Transform()
        rscript_wait_transform(indicator, 0, 0)
        assert (indicator.xpos, indicator.ypos) == (1080, 638)
        assert state["wait_color"] == "#ff8040" and state["wait_image"] == 2
        styled = RScriptText("text")
        styled.refresh_settings()
        assert styled.style.size == 24 and styled.style.color == Color("#FFDE00")
        signature = styled.rscript_settings
        command(parse_texsize, execute_texsize, "0 32")
        command(parse_texcolor, execute_texcolor, "0 1")
        styled.refresh_settings()
        assert styled.style.size == 32 and styled.rscript_settings != signature
        renpy.show_screen("say", who="Alice", what=sample)
        renpy.get_screen("say").update()
        assert renpy.get_widget("say", "window").style.ypos == 503
        assert renpy.get_widget("say", "what").style.xpos == 188
        renpy.hide_screen("say")
        store.rscript_textboxes.clear()
        store.rscript_compane_position = None
        lex = renpy.lexer.Lexer([("test", 1, "1 3 7", [])])
        lex.advance()
        execute_flagset(parse_flagset(lex))
        assert [_r[i] for i in range(1, 4)] == [7, 7, 7]
        execute_dynsel(repr(("Question", 0)))
        for answer in (("Always", 1, 0, 0), ("Once", 2, 5024, 0), ("Unlocked", 3, 5025, 1)):
            execute_dynans(repr(answer))
        from types import SimpleNamespace
        assert rscript_arc_position((0, 0), (100, 0), 0, 1) == (0, 0)
        for direction in (-1, 1):
            middle = rscript_arc_position((0, 0), (100, 0), .5, direction)
            assert abs(middle[0] - 50) < .001 and middle[1] == direction * 50
            end = rscript_arc_position((0, 0), (100, 0), 1, direction)
            assert abs(end[0] - 100) < .001 and abs(end[1]) < .001
        execute_locgrid(RScriptArguments(Xgrid=2, Ygrid=3))
        assert (store.layer_x_grid, store.layer_y_grid) == (2, 3)
        execute_locgrid(RScriptArguments(Xgrid=0, Ygrid=0))
        assert (store.layer_x_grid, store.layer_y_grid) == (1, 1)
        _r[6503] = 6
        captured_args = RScriptArguments(Effect="_r[6503]").resolved()
        _r[6503] = 0
        assert captured_args.Effect == 6
        store.in_queue = True
        _r[6511], _r[904], _r[905] = 0, 40, 3
        execute_effect(RScriptArguments(EffectNo="_r[6511]", Mode=0))
        execute_tone(RScriptArguments(Level="_r[904]", Mode=1))
        execute_tonedep(RScriptArguments(Depth="_r[905]"))
        _r[6511], _r[904], _r[905] = 11, 0, 99
        store.in_queue = False
        process_draw_queue()
        assert store.tone_level == 40 and store.tonedep == 5
        execute_tone(RScriptArguments(Level=0, Mode=0))
        execute_tonedep(RScriptArguments(Depth=0))
        old_info, old_pos, old_groups = store.layer_info, store.layer_pos, store.layer_groups
        old_pause = renpy.pause
        pauses = []
        try:
            store.layer_info = {11: "grpo_map 0009", 12: "grpo_map 0012", CG_LAYER: "grpe 1020"}
            store.layer_pos = {11: (0, 0), 12: (10, 20)}
            store.layer_groups = {}
            execute_group(SimpleNamespace(Layer=11, Group=2))
            execute_group(SimpleNamespace(Layer=0, Group=0))
            assert rscript_selected_layers(102) == [11]
            assert rscript_selected_layers(202) == [11]
            assert rscript_selected_layers(0) == [11, 12]
            store.layer_info.update({0: "black", 102: "black"})
            assert rscript_selected_layers(0) == [11, 12]  # selectors never recurse
            del store.layer_info[0], store.layer_info[102]
            store.in_queue = True
            move_layer(102, 5, 7, 0, 0, relative=True)
            assert store.layer_pos[11] == (5, 7) and store.layer_pos[12] == (10, 20)
            store.in_queue = False
            process_draw_queue()
            renpy.pause = lambda delay, **kwargs: pauses.append(delay)
            for effect, transform in ((5, white_out), (6, black_out), (14, None)):
                store.layer_info[11] = "grpo_map 0009"
                store.in_queue = True
                loadcls(102, effect, clear=True)
                assert 11 not in store.layer_info and 12 in store.layer_info
                shows = [kwargs for fn, args, kwargs in store.draw_queue if fn == rscript_show_layer]
                assert shows
                if transform is not None:
                    assert shows[0]["at_list"][-1] == transform
                assert not any(fn == renpy.hide for fn, args, kwargs in store.draw_queue)
                store.in_queue = False
                process_draw_queue()
            store.layer_info[11] = "grpo_map 0009"
            pauses.clear()
            loadcls(0, 1, clear=True)
            assert pauses == [.5], pauses  # all objects animate together
            assert store.layer_info == {CG_LAYER: "grpe 1020"}
            store.layer_info.update({11: "grpo_map 0009", 12: "grpo_map 0012"})
            store.in_queue = True
            loadcls(0, 3, clear=True)
            transitions = [op for op in store.draw_queue_delayed if op[0] == renpy.with_statement]
            assert len(transitions) == 1, transitions
            store.draw_queue_delayed[:] = [op for op in store.draw_queue_delayed if op[0] != renpy.with_statement]
            store.in_queue = False
            process_draw_queue()
        finally:
            store.in_queue = False
            renpy.pause = old_pause
            store.layer_info, store.layer_pos, store.layer_groups = old_info, old_pos, old_groups
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
        # enabl must preserve a loaded layer, including loads/moves while hidden.
        original_with = renpy.with_statement
        try:
            renpy.with_statement = lambda *args, **kwargs: None
            store.folder[11] = "grpo_map"
            loadcls(11, 0, cg=9, xpos=233, ypos=480)
            original = store.layer_info[11]
            execute_queue(None)
            execute_enabl(SimpleNamespace(Layer=11, Mode=0))
            assert store.layer_enabled.get(11, 1) == 1
            execute_update(SimpleNamespace(Effect=0, Step=0, Wait=0))
            displayable = renpy.game.context().scene_lists.get_displayable_by_tag(IMAGE_LAYER, "layer11")
            displayable.function(displayable, 0, 0)
            assert displayable.alpha == 0 and store.layer_info[11] == original
            loadcls(11, 0, cg=12, xpos=441, ypos=480)
            displayable = renpy.game.context().scene_lists.get_displayable_by_tag(IMAGE_LAYER, "layer11")
            displayable.function(displayable, 0, 0)
            assert displayable.alpha == 0
            execute_enabl(SimpleNamespace(Layer=0, Mode=1))
            displayable.function(displayable, 0, 0)
            assert displayable.alpha == 1 and store.layer_info[11] == "grpo_map 0012"
            assert store.layer_pos[11] == (441, 480)
            loadcls(0, 0, clear=True)
        finally:
            renpy.with_statement = original_with
        # Gallery CG movement and cls 0 must not destroy a newly loaded title.
        original_with, original_pause = renpy.with_statement, renpy.pause
        try:
            renpy.with_statement = lambda *args, **kwargs: None
            renpy.pause = lambda *args, **kwargs: None
            execute_tone(RScriptArguments(Level=100, Mode=0))
            execute_queue(None)
            execute_tone(RScriptArguments(Level=0, Mode=0))
            execute_tonedep(RScriptArguments(Depth=0))
            execute_update(SimpleNamespace(Effect=0, Step=0, Wait=0))
            assert store.tone_level == 0 and not renpy.showing(TONE_TAG, TONE_LAYER)
            execute_queue(None)
            execute_tone(RScriptArguments(Level=50, Mode=1))
            execute_tonedep(RScriptArguments(Depth=20))
            execute_update(SimpleNamespace(Effect=0, Step=0, Wait=0))
            assert (store.tone_level, store.tone_color, store.tonedep) == (50, "white", 39)
            execute_tone(RScriptArguments(Level=0, Mode=0))
            execute_queue(None)
            execute_gload(SimpleNamespace(CGNum=1020, Colormode=0))
            execute_gmove(SimpleNamespace(Effect=0, xLoc=0, yLoc=-608, Speed=0))
            execute_update(SimpleNamespace(Effect=0, Step=0, Wait=0))
            assert store.layer_pos[CG_LAYER] == (0, -608)
            execute_gmove(SimpleNamespace(Effect=1, xLoc=0, yLoc=0, Speed=152))
            for number in (9001, 9101):
                execute_queue(None)
                execute_gcls(SimpleNamespace(Mode=0))
                loadcls(0, 0, clear=True)
                execute_gload(SimpleNamespace(CGNum=number, Colormode=0))
                execute_update(SimpleNamespace(Effect=0, Step=0, Wait=0))
                assert store.layer_info[CG_LAYER] == "grpe %04d" % number
                assert store.layer_pos[CG_LAYER] == (0, 0)
                assert renpy.get_attributes(CG_TAG, CG_LAYER) == ("%04d" % number,)
                assert renpy.game.context().scene_lists.get_displayable_by_tag(CG_LAYER, CG_TAG) is not None
            execute_gcls(SimpleNamespace(Mode=0))
        finally:
            renpy.with_statement, renpy.pause = original_with, original_pause
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
            # Gallery data uses -1 for absent hover/info artwork, not -001.png.
            for layer, sentinel in ((47, -1), (48, 0xffff)):
                for slot in (0, 1):
                    execute_setlink(SimpleNamespace(Layer=layer, HoverCG=sentinel,
                                                   xLoc=layer, yLoc=642, Slot=slot))
                assert layer not in rscript_click_previews
            renpy.call_screen = lambda name, **kwargs: (captured.append(kwargs), 99)[1]
            execute_click(None)
            assert _r[0] == 99
            assert [option[0] for option in captured[0]["options"]] == [91, 92, 99]
            assert all(option[2] == option[3] for option in captured[0]["options"][:2])
            assert set(captured[0]["previews"]) == {2}
            captured.clear()
            # Scene gallery asks for real-numbered optional images which are
            # absent, not just -1. Also validate old/restored preview bindings.
            execute_setclk(SimpleNamespace(Layer=49, Value=99))
            execute_setlink(SimpleNamespace(Layer=49, HoverCG=8501, xLoc=0, yLoc=0, Slot=0))
            store.rscript_click_previews[49] = (8502, 0, 665)
            execute_click(None)
            assert captured[-1]["options"][0][2:4] == ("grpo_ex 0049", "grpo_ex 0049")
            assert not captured[-1]["previews"]
            captured.clear()
            old_mouse_pos = renpy.get_mouse_pos
            try:
                renpy.get_mouse_pos = lambda: (123, 456)
                for result in (1, 0):
                    renpy.call_screen = lambda name, **kwargs: (captured.append((name, kwargs)), result)[1]
                    lex = renpy.lexer.Lexer([("0201-locmap", 1, "31 32 0 0 1", [])])
                    lex.advance()
                    execute_locmap(parse_locmap(lex))
                    assert (_r[0], _r[31], _r[32]) == (result, 123, 456)
                    assert captured[-1] == ("rscript_locmap_screen", {"cancel": True})
            finally:
                renpy.get_mouse_pos = old_mouse_pos
            captured.clear()
            # 0401: playback/lyrics return to the same click without rebinding.
            execute_autoreset(SimpleNamespace(Mode=0))
            for layer, value in ((44, 95), (45, 93), (46, 94), (49, 99)):
                store.folder[layer] = "grpo_ex"
                store.layer_info[layer] = "grpo_ex %04d" % layer
                execute_setclk(SimpleNamespace(Layer=layer, Value=value))
                execute_setlink(SimpleNamespace(Layer=layer, HoverCG=layer + 100,
                                               xLoc=layer, yLoc=644, Slot=0))
            store.layer_enabled[46] = 0
            lex = renpy.lexer.Lexer([("0401-test", 1, "0 0 1", [])])
            lex.advance()
            click = parse_click(lex)
            for result in (93, 95, 0, 99):
                renpy.call_screen = lambda name, result=result, **kwargs: (captured.append(kwargs), result)[1]
                execute_click(click)
                assert _r[0] == result
                assert captured[-1]["cancel"] is True
                assert [option[0] for option in captured[-1]["options"]] == [95, 93, 99]
                assert set(rscript_click_values) == {44, 45, 46, 49}
            store.layer_enabled.pop(46)
            execute_autoreset(SimpleNamespace(Mode=1))
            execute_click(click)
            assert not rscript_click_values
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
            native_layers = captured[0]["layers"]
            for index, layer in native_layers.items():
                loadcls(layer, 0, cg=(9, 12, 13)[index], xpos=options[index][4], ypos=options[index][5])
            # Lyrics/tone must remain above the song-list buttons even while
            # those buttons are focused. Click screens must not redraw them.
            store.folder[40] = "grpo_map"
            loadcls(40, 0, cg=9, xpos=285, ypos=118)
            execute_tonedep(RScriptArguments(Depth=40))
            execute_tone(RScriptArguments(Level=50, Mode=0))
            renpy.show_screen("rscript_click_screen", options=options, previews=previews, layers=native_layers)
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
                    assert isinstance(button.style.focus_mask, renpy.display.image.ImageReference)
                    assert all(button.state_children[state].alpha == 0.0 for state in ("idle_", "hover_"))
                    assert renpy.run(button.action) == options[index][0]
                    renpy.run(button.hovered)
                    renpy.display.screen.updated_screens.discard(screen)
                    screen.update()
                    assert screen.scope["preview"] is None
                    assert renpy.get_widget("rscript_click_screen", "rscript_click_preview") is None
                    scene = renpy.game.context().scene_lists
                    orders = dict(scene.get_zorder_list(IMAGE_LAYER))
                    layer = native_layers[index]
                    assert orders["layer%d" % layer] < orders[TONE_TAG] < orders["layer40"]
                    assert orders["rscript_click_preview"] == orders["layer%d" % layer] + 1
                    assert orders["rscript_click_preview"] < orders["layer40"]
                    displayable = scene.get_displayable_by_tag(IMAGE_LAYER, "layer%d" % layer)
                    refs = []
                    displayable.visit_all(lambda d: refs.append(d.name) if isinstance(d, renpy.display.image.ImageReference) else None)
                    assert tuple(options[index][3].split()) in refs, refs
                    assert store.layer_info[layer] == options[index][2]
                    renpy.run(button.unhovered)
                    renpy.display.screen.updated_screens.discard(screen)
                    screen.update()
                    assert renpy.get_widget("rscript_click_screen", "rscript_click_preview") is None
                    assert "rscript_click_preview" not in dict(scene.get_zorder_list(IMAGE_LAYER))
            finally:
                renpy.display.screen.pop_current_screen()
            renpy.hide_screen("rscript_click_screen")
            # depth changes apply to loaded objects; queue keeps their order.
            execute_queue(None)
            execute_depth(SimpleNamespace(Layer=19, Depth=50))
            assert dict(scene.get_zorder_list(IMAGE_LAYER))["layer19"] == 38
            execute_update(SimpleNamespace(Effect=0, Step=0, Wait=0))
            assert dict(scene.get_zorder_list(IMAGE_LAYER))["layer19"] == 100
            for layer, cg in ((19, 109), (22, 112), (23, 113)):
                execute_setclk(SimpleNamespace(Layer=layer, Value=layer))
                execute_setlink(SimpleNamespace(Layer=layer, HoverCG=cg, xLoc=0, yLoc=0, Slot=0))
            execute_setlink(SimpleNamespace(Layer=19, HoverCG=1090, xLoc=0, yLoc=0, Slot=1))
            def cancel_focused(name, **kwargs):
                assert list(kwargs["layers"].values()) == [22, 23, 19]
                rscript_click_focus(19, "grpo_map 0109", kwargs["previews"][2])
                return 0
            renpy.call_screen = cancel_focused
            execute_click(SimpleNamespace(Cancel=1))
            assert _r[0] == 0
            assert "rscript_click_preview" not in dict(scene.get_zorder_list(IMAGE_LAYER))
            refs = []
            scene.get_displayable_by_tag(IMAGE_LAYER, "layer19").visit_all(
                lambda d: refs.append(d.name) if isinstance(d, renpy.display.image.ImageReference) else None)
            assert ("grpo_map", "0009") in refs and ("grpo_map", "0109") not in refs, refs
            execute_tone(RScriptArguments(Level=0, Mode=0))
            loadcls(0, 0, clear=True)
        finally:
            renpy.call_screen = old_click_screen
            store.folder, store.layer_info = old_folder, old_info
            execute_resetclk(None)
            store.rscript_click_autoreset = True
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
