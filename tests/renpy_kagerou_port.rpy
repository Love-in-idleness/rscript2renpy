python early:
    def check_kagerou_port():
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        renpy.display.scenelists.init_layers()
        renpy.game.context().scene_lists = renpy.display.scenelists.SceneLists(None, renpy.game.context().images)
        renpy.display.screen.prepare_screens()
        kagerou_init_textbox()
        assert (config.screen_width, config.screen_height) == (800, 600)
        assert persistent.rscript_text_size == 24 and persistent.kagerou_direction == 1
        assert rscript_textbox_state()['text_rect'] == (114, 30, 646, 480)
        assert rscript_compane_position == (585, 572)
        assert all(renpy.has_label(name) for name in ('_0000', '_0059', '_0201', '_0301', '_0302', '_g_0001_TOP2'))
        assert renpy.loadable(rscript_audio_file('voice', 40002))
        assert rscript_click_link_is_preview
        assert rscript_folder_zero_all
        def command(parser, executor, text):
            lex = renpy.lexer.Lexer([('kagerou-test', 1, text, [])])
            lex.advance()
            executor(parser(lex))
        command(parse_folder, execute_folder, "1 'grpo_bu'")
        command(kagerou_parse_locmode, kagerou_locmode, '1 1 0 0')
        assert layer_anchor[1] == (.5, 0)
        store.in_queue = True
        command(kagerou_parse_words, kagerou_excmd, '0 1 3011 0 0')
        assert _r[20] == 1 and layer_zorder[1] == 16
        assert layer_zorder[6] == 12
        assert layer_pos[1] == (200, 0)
        assert draw_queue and not renpy.showing('layer1', layer=IMAGE_LAYER)
        store.in_queue = False
        process_draw_queue()
        assert renpy.showing('layer1', layer=IMAGE_LAYER)
        command(kagerou_parse_words, kagerou_excmd, '1 0 0 0 0')
        assert renpy.showing('layer1', layer=IMAGE_LAYER)
        command(kagerou_parse_words, kagerou_excmd, '1 1 0 0 0')
        assert not renpy.showing('layer1', layer=IMAGE_LAYER)
        # 0099's real choice cards use setclk without any setlink.
        command(parse_load, execute_load, '21 8011 232 130 0 0')
        command(parse_load, execute_load, '22 8012 399 130 0 0')
        process_draw_queue()
        command(parse_setclk, execute_setclk, '21 1 2 0')
        command(parse_setclk, execute_setclk, '22 2 2 0')
        old_call_screen = renpy.call_screen
        captured = []
        try:
            renpy.call_screen = lambda name, **kwargs: captured.append((name, kwargs)) or 2
            command(parse_click, execute_click, '0 0 0')
            assert [item[:2] for item in captured[-1][1]['options']] == [(1, False), (2, False)]
            assert _r[0] == 2 and not rscript_click_values
        finally:
            renpy.call_screen = old_call_screen
        # Bonus galleries reset both folders and anchors before loading thumbnails.
        command(parse_folder, execute_folder, "0 'grpo_ex'")
        command(kagerou_parse_locmode, kagerou_locmode, '0 0 0 0')
        command(parse_load, execute_load, '1 1 40 70 0 0')
        assert layer_info[1] == 'grpo_ex 0001' and layer_pos[1] == (40, 70)
        assert layer_anchor[1] == (0, 0)
        command(parse_folder, execute_folder, "1 'grpo_bu'")
        old_say = renpy.say
        calls = []
        try:
            renpy.say = lambda who, what, **kwargs: calls.append((what, kwargs['interact']))
            store.jump_back_point = 'test'
            kagerou_say(repr(('ignored', '【女】^n本文', 1)))
            assert calls[-1] == ('【女】\n本文', True)
            kagerou_say(repr(('', '^n次の段落', 1)))
            assert '本文{fast}\n' in calls[-1][0] and calls[-1][0].endswith('次の段落')
            kagerou_append(repr(('追加', 0)))
            assert calls[-1][0].endswith('次の段落{fast}追加') and not calls[-1][1]
            kagerou_say(repr(('', '【女】^n台詞', 1)))
            assert '追加{fast}\n\u3000\n{/alpha}【女】\n台詞' in calls[-1][0]
            assert calls[-1][0].startswith('{alpha=0.5019607843}')
            kagerou_set_text_setting('text_focus', 1)
            assert '{alpha=' not in kagerou_page_text()
            kagerou_set_text_setting('text_focus', 0)
            kagerou_tclsmode('1')
            kagerou_say(repr(('', '単独', 1)))
            assert calls[-1][0] == '単独'
            kagerou_tclsmode('2')
            store.kagerou_page = '\n'.join(['旧段落'] * 40)
            kagerou_say(repr(('', '新しい頁', 1)))
            assert calls[-1][0] == '新しい頁'
        finally:
            renpy.say = old_say
        kagerou_txcls('0')
        assert store.kagerou_page == ''
        # 0999 -> 1000: tbox 0 0 ends the title page even without txcls.
        store.kagerou_page = store.kagerou_page_current = '0999の文字'
        store.in_queue = True
        command(parse_tbox, kagerou_tbox, '0 0')
        assert store.kagerou_page == '0999の文字'
        store.in_queue = False
        process_draw_queue()
        assert store.kagerou_page == store.kagerou_page_old == store.kagerou_page_current == ''
        assert renpy.get_screen('say') is None
        command(parse_tbox, kagerou_tbox, '0 1')
        try:
            renpy.say = lambda who, what, **kwargs: calls.append((what, kwargs['interact']))
            kagerou_say(repr(('', '1000の文字', 1)))
            assert calls[-1][0] == '1000の文字'
        finally:
            renpy.say = old_say
        kagerou_txcls('0')
        ruby, _ = parse_rscript_text(repr('|寂寞[じゃくまく]'), True)
        renpy.show_screen('say', who=None, what=ruby)
        renpy.get_screen('say').update()
        window = renpy.get_widget('say', 'window')
        assert window.style.xminimum == window.style.xmaximum == 800
        text = renpy.get_widget('say', 'what')
        text.refresh_settings()
        assert text.style.xpos == 760 and text.style.ypos == 30
        assert text.style.vertical and text.style.xanchor == 1.0
        assert text.style.outlines
        kagerou_set_text_setting('shadow', 1)
        text.refresh_settings()
        assert not text.style.outlines
        kagerou_set_text_setting('shadow', 0)
        text.refresh_settings()
        assert text.style.outlines
        # Real native shaping: vertical columns use the rectangle's height as their limit.
        sample = RScriptText('甲乙丙丁' * 30, size=24, vertical=True)
        sample.refresh_settings()
        layout = renpy.text.text.Layout(sample, 480, 646, {}, size_only=True,
                                       drawable_res=False)
        assert layout.size[0] <= 504 and layout.size[1] < 646, layout.size
        assert sample.style.shaper == 'harfbuzz'
        box = rscript_textbox_state()
        assert box['wait_image'] == 24
        assert len(rscript_layouts()['wait24']['items']) == 60
        assert kagerou_wait_position(layout, box)[1] <= box['text_rect'][1] + box['text_rect'][3] + 24
        assert all(segment.vertical for paragraph in layout.paragraphs
                   for segment, content in paragraph)
        # Check ink bounds, not just advances: opening brackets used to draw
        # inside the following glyph despite having a full 24px advance.
        for index, size in enumerate((24, 18, 12)):
            kagerou_set_text_setting('size', index)
            brackets = RScriptText('『甲「乙【丙】丁』戊', size=size)
            brackets.refresh_settings()
            assert brackets.style.size == size
            bracket_layout = renpy.text.text.Layout(brackets, 480, 646, {},
                size_only=True, drawable_res=False)
            segment = bracket_layout.paragraphs[0][0][0]
            for glyph in bracket_layout.paragraph_glyphs[0]:
                if chr(glyph.character) in '『「【':
                    left, _, right, _ = segment.bounds([glyph],
                        (10000, 10000, -10000, -10000), bracket_layout)
                    assert 0 <= left - glyph.x < right - glyph.x <= glyph.advance + 1, (size, glyph.character, left, right)
        kagerou_set_text_setting('size', 0)
        kagerou_set_text_setting('direction', 0)
        renpy.get_screen('say').update()
        text = renpy.get_widget('say', 'what')
        text.refresh_settings()
        assert text.style.xpos == 400 and not text.style.vertical and text.style.size == 24, (text.style.xpos, text.style.vertical, text.style.size, rscript_textbox_state())
        kagerou_set_text_setting('direction', 1)
        for size, expected in enumerate((24, 18, 12)):
            kagerou_set_text_setting('size', size)
            for direction in (0, 1, 0):
                kagerou_set_text_setting('direction', direction)
                text.refresh_settings()
                assert persistent.rscript_text_size == text.style.size == expected
                assert rscript_textbox_state()['size'] == expected
                assert rscript_textbox_state()['wait_image'] == ((18, 16, 12) if direction == 0 else (24, 18, 12))[size]
        kagerou_set_text_setting('direction', 1)
        kagerou_set_text_setting('size', 2)
        assert persistent.rscript_text_size == 12
        assert rscript_textbox_state()['text_rect'] == (418, 30, 342, 240)
        kagerou_set_text_setting('snap', 8)
        assert rscript_textbox_state()['text_rect'] == (20, 270, 342, 240)
        kagerou_set_text_setting('size', 0)
        kagerou_set_text_setting('snap', 0)
        renpy.hide_screen('say')
        for screen_name in ('kagerou_compane', 'kagerou_excompane', 'kagerou_history'):
            renpy.show_screen(screen_name)
            renpy.get_screen(screen_name).update()
            renpy.hide_screen(screen_name)
        renpy.call_in_new_context('_kagerou_test_call')
        assert store.kagerou_test_returned
        # Only inspect the entry sequence: this command never plays movies or enters start.
        assert renpy.has_label('splashscreen') and rscript_boot_movies == (2, 1)
        node = renpy.game.script.lookup('splashscreen')
        while not isinstance(node, renpy.ast.Python):
            node = node.next
        movies = []
        old_movie = renpy.movie_cutscene
        try:
            renpy.movie_cutscene = lambda filename: movies.append(filename)
            renpy.session.pop('kagerou_boot_movies', None)
            renpy.python.py_exec_bytecode(node.code.bytecode)
            renpy.python.py_exec_bytecode(node.code.bytecode)
            assert movies == ['mov/0002.mpg']
        finally:
            renpy.movie_cutscene = old_movie
        print('OK: Kagerou call operands, resources, EXCMD, vertical presets, text focus and panes')
        return False
    renpy.arguments.register_command('kageroutest', check_kagerou_port)

label _kagerou_test_call:
    $ _r[10] = 8765
    _gosub _r[10] 0 0 0 0 0 0 0 0 0 0
    $ store.kagerou_test_returned = True
    return

label _8765:
    $ assert _r[10] == 0
    _return 0
