python early:
    def check_kagerou_port():
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        renpy.display.scenelists.init_layers()
        renpy.game.context().scene_lists = renpy.display.scenelists.SceneLists(None, renpy.game.context().images)
        renpy.display.screen.prepare_screens()
        kagerou_init_textbox()
        assert (config.screen_width, config.screen_height) == (800, 600)
        assert persistent.rscript_text_size == 24
        assert persistent.rscript_say_line_chars == 26
        assert rscript_textbox_state()['text_rect'] == (114, 30, 646, 480)
        assert renpy.has_label('_0000') and renpy.has_label('_g_0001_omakemenu')
        assert renpy.loadable(rscript_audio_file('voice', 40002))
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
            assert '追加{fast}\n\u3000\n【女】\n台詞' in calls[-1][0]
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
        ruby, _ = parse_rscript_text(repr('|寂寞[じゃくまく]'), True)
        renpy.show_screen('say', who=None, what=ruby)
        renpy.get_screen('say').update()
        window = renpy.get_widget('say', 'window')
        assert window.style.xminimum == window.style.xmaximum == 800
        assert renpy.get_widget('say', 'what').style.xpos == 114
        assert renpy.get_widget('say', 'what').style.ypos == 30
        renpy.hide_screen('say')
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
        print('OK: Kagerou entry, resources, EXCMD queue/depth/clear, whole-page TXT/TXA and screen')
        return False
    renpy.arguments.register_command('kageroutest', check_kagerou_port)
