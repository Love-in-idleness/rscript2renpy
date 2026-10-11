python early:
    def check_kagerou_port():
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        renpy.display.scenelists.init_layers()
        renpy.game.context().scene_lists = renpy.display.scenelists.SceneLists(None, renpy.game.context().images)
        renpy.display.screen.prepare_screens()
        kagerou_init_textbox()
        assert persistent.rscript_text_cps == 25
        controls = rscript_layouts()['confscrn']['controls']
        assert rscript_ui_action(controls['msp_slw']).get_selected()
        assert not rscript_ui_action(controls['msp_nom']).get_selected()
        assert not rscript_ui_action(controls['msp_now']).get_selected()
        for speed in (75, 0):
            persistent.rscript_text_cps = speed
            kagerou_init_textbox()
            assert persistent.rscript_text_cps == speed
        persistent.rscript_text_cps = 25
        assert kagerou_music_tracks() == tuple(range(1, 16))
        assert rscript_system_action(7) is rscript_ui['system_actions'][7]
        assert isinstance(rscript_system_action(7, False), Return)
        music_methods = ('play', 'stop', 'set_pause', 'set_volume', 'is_playing')
        original_music = {name: getattr(renpy.music, name) for name in music_methods}
        audio_calls, backend_playing = [], [False]
        original_volume = dict(_preferences.volumes)
        try:
            for name in music_methods[:-1]:
                setattr(renpy.music, name, lambda *args, _name=name, **kwargs:
                        audio_calls.append((_name, args, kwargs)))
            renpy.music.is_playing = lambda **kwargs: backend_playing[0]
            kagerou_music_begin()
            assert kagerou_music_track == 1 and not kagerou_music_playing
            kagerou_music_pause()
            assert not kagerou_music_paused
            kagerou_music_select(2)
            assert kagerou_music_track == 2 and not kagerou_music_playing
            kagerou_music_select(2)
            assert kagerou_music_playing and audio_calls[-1][0] == 'play'
            kagerou_music_tick()
            assert kagerou_music_track == 2  # Decoder startup is not completion.
            kagerou_music_pause()
            count = len(audio_calls)
            kagerou_music_play()
            kagerou_music_tick()
            assert kagerou_music_paused and len(audio_calls) == count
            kagerou_music_select(3)
            assert kagerou_music_track == 3 and not kagerou_music_paused
            backend_playing[0] = True
            kagerou_music_tick()
            backend_playing[0] = False
            kagerou_music_tick()
            assert kagerou_music_track == 4 and kagerou_music_playing
            kagerou_music_select(15)
            kagerou_music_next()
            assert kagerou_music_track == 1 and not kagerou_music_playing
            count = len(audio_calls)
            kagerou_music_previous()
            kagerou_music_select(21)
            assert kagerou_music_track == 1 and len(audio_calls) == count
            for volume in (0, 128, 255):
                store.kagerou_music_volume = volume
                kagerou_music_apply_volume()
                expected = 10 ** (-((255 - volume) * 3000 // 255) / 2000.)
                assert audio_calls[-1] == ('set_volume', (expected,), {'channel': 'kagerou_gallery'})
            assert dict(_preferences.volumes) == original_volume
            old_screen = renpy.call_screen
            try:
                def close_gallery(name):
                    assert name == 'kagerou_music_gallery'
                    kagerou_music_play()
                    kagerou_music_pause()
                renpy.call_screen = close_gallery
                kagerou_open_music()
                assert not kagerou_music_playing and not kagerou_music_paused
            finally:
                renpy.call_screen = old_screen
        finally:
            for name, method in original_music.items():
                setattr(renpy.music, name, method)
        assert (config.screen_width, config.screen_height) == (800, 600)
        assert persistent.rscript_text_size == 24 and persistent.kagerou_direction == 1
        assert rscript_textbox_state()['text_rect'] == (114, 30, 646, 480)
        assert rscript_compane_position == (585, 572)
        assert all(renpy.has_label(name) for name in ('_0000', '_0059', '_0201', '_0301', '_0302', '_g_0001_TOP2'))
        assert renpy.loadable(rscript_audio_file('voice', 40002))
        # Native pvNN gates playback by number // 10000, not the active portrait.
        controls = rscript_layouts()['confscrn']['controls']
        assert all(controls['pv%02d_%s' % (group, state)] == ('voice_group', group, enabled)
                   for group in range(1, 6) for state, enabled in (('on', True), ('off', False)))
        assert not rscript_layouts()['confscrn'].get('unhandled')
        original_play, original_stop = renpy.music.play, renpy.music.stop
        audio_calls = []
        try:
            renpy.music.play = lambda *args, **kwargs: audio_calls.append(('play', args, kwargs))
            renpy.music.stop = lambda *args, **kwargs: audio_calls.append(('stop', args, kwargs))
            assert all(rscript_voice_enabled(group * 10000 + 1) for group in range(10))
            execute_voice(RScriptArguments(VoiceNo=40002, Repeat=0, Fade=0, Pan=0))
            assert len(audio_calls) == 1 and audio_calls[0][0] == 'play'
            assert rscript_last_voice_number == 40002
            off = rscript_ui_action(controls['pv04_off'])
            renpy.run(off)
            assert off.get_selected() and not rscript_voice_enabled(40002)
            assert not rscript_ui_sensitive('voice')
            rscript_replay_voice()
            assert len(audio_calls) == 1  # No replay or interruption of an existing clip.
            execute_voice(RScriptArguments(VoiceNo=40002, Repeat=0, Fade=0, Pan=0))
            assert len(audio_calls) == 1 and rscript_last_voice is None and rscript_voice_pending
            execute_voice(RScriptArguments(VoiceNo=10002, Repeat=0, Fade=0, Pan=0))
            assert len(audio_calls) == 2 and rscript_last_voice_number == 10002
            renpy.run(rscript_ui_action(controls['pv04_on']))
            execute_voice(RScriptArguments(VoiceNo=40002, Repeat=0, Fade=0, Pan=0))
            rscript_replay_voice()
            assert len(audio_calls) == 4 and rscript_ui_sensitive('voice')
            assert all(item[0] == 'play' for item in audio_calls)
        finally:
            renpy.music.play, renpy.music.stop = original_play, original_stop
            persistent.rscript_voice_group_enabled.clear()
            store.rscript_voice_pending = False
            store.rscript_last_voice = store.rscript_last_voice_number = None
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
        store.kagerou_page = store.kagerou_page_current = ruby
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
        original_font = persistent.rscript_text_font
        try:
            for font in ('NotoSansCJKjp-Regular.otf', 'NotoSansCJK-Light.ttc',
                         'NotoSerifCJK-Regular.ttc', 'simhei.ttf'):
                persistent.rscript_text_font = 'fonts/' + font
                dashes = RScriptText('甲————\n\u3000\n——————乙―', size=24)
                for direction in (1, 0, 1):
                    kagerou_set_text_setting('direction', direction)
                    dashes.refresh_settings()
                    dash_layout = renpy.text.text.Layout(dashes, 480, 646, {},
                        size_only=True, drawable_res=False)
                    glyphs = [g for p in dash_layout.paragraph_glyphs for g in p]
                    assert dashes.text == ['甲————\n\u3000\n——————乙―']
                    if direction:
                        assert ''.join(chr(g.character) for g in glyphs) == '甲————\u3000——————乙―', [(g.character, g.advance) for g in glyphs]
                    for paragraph in dash_layout.paragraphs:
                        for segment, value in paragraph:
                            for glyph in segment.glyphs(value, dash_layout):
                                if chr(glyph.character) in '—―':
                                    left, top, right, bottom = segment.bounds([glyph],
                                        (10000, 10000, -10000, -10000), dash_layout)
                                    # Horizontal ink before the SDK's final 90-degree
                                    # rotation becomes a vertical dash on the screen.
                                    assert right - left > bottom - top, (font, direction, glyph.character, (left, top, right, bottom))
        finally:
            persistent.rscript_text_font = original_font
            kagerou_set_text_setting('direction', 1)
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
        for screen_name in ('kagerou_compane', 'kagerou_excompane', 'kagerou_history', 'preferences'):
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
