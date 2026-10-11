# Disposable fixture: neither enter the story nor use the real project's saves.
default kagerou_capture_stage = 0

init python:
    def kagerou_capture_error(short, full, info):
        raise SystemExit(full)
    config.exception_handler = kagerou_capture_error

    def kagerou_capture():
        name = ('vertical.png', 'horizontal.png', 'preferences-jp.png',
                'preferences-zh.png', 'save-jp.png', 'load-zh.png')[kagerou_capture_stage]
        if kagerou_capture_stage < 2:
            # Exercise the real drawable layout, not only its size-only shaping pass.
            for kind in ('say', 'oload'):
                probe = RScriptText('{rb}漢字{/rb}{rt}かんじ{/rt}後', kind=kind,
                                   slow=True, slow_cps=10)
                renpy.display.render.render(probe, 800, 600, .15, .15)
                glyphs = [g for paragraph in probe.get_layout().paragraph_glyphs for g in paragraph]
                body = [g for g in glyphs if g.ruby == 1]
                reading = [g for g in glyphs if g.ruby == 2]
                assert [g.time for g in reading] == [body[0].time, body[0].time, body[1].time]
                assert 0 < body[0].time < body[1].time
        renpy.screenshot(os.path.join(config.basedir, name))
        if kagerou_capture_stage == 5:
            renpy.quit()
        store.kagerou_capture_stage += 1
        if kagerou_capture_stage >= 4:
            renpy.hide_screen('preferences')
            renpy.hide_screen('save')
            _preferences.language = None if kagerou_capture_stage == 4 else 'zh'
            store.FileJson = lambda slot, key: 1000 if slot == 1 and key == 'rscript_dt1' else None
            store.FileLoadable = lambda slot: slot == 1
            store.FileTime = lambda *args: '2026/10/11 12:34'
            store.FileNewest = lambda slot: slot == 1
            FilePage(1 if kagerou_capture_stage == 4 else 10)()
            renpy.show_screen('save' if kagerou_capture_stage == 4 else 'load')
            renpy.restart_interaction()
            return
        if kagerou_capture_stage >= 2:
            renpy.hide_screen('say')
            persistent.rscript_text_cps = 25
            if kagerou_capture_stage == 3:
                _preferences.language = 'zh'
                renpy.run(rscript_ui_action(('voice_group', 4, False)))
            renpy.show_screen('preferences')
            renpy.restart_interaction()
            return
        kagerou_set_text_setting('direction', 0)
        store.kagerou_page_old = ''
        store.kagerou_page_current = parse_rscript_text(repr('【女】\n『甲乙』「丙丁」【戊己】。横排的文字与等待图标。————――\n抉[えぐ]られた傷痕めいて、熱く熾[おこ]った。'), True)[0]
        store.kagerou_page = kagerou_page_current
        renpy.show_screen('say', who=None, what=kagerou_page_text())
        renpy.restart_interaction()

label before_main_menu:
    scene expression 'grpe/1001.png' onlayer master
    python:
        kagerou_init_textbox()
        persistent.rscript_text_cps = 0
        store.textbox_panel = 1
        store.kagerou_page_old = '　\n　——于这寂寥如荒原的风景之隙，\n　借我此身，{fast}\n'
        store.kagerou_page_current = parse_rscript_text(repr('　―――ジジ……ジッ、と。焦げる音が、銀の小さな火皿の中であえかに鳴き、火口はさながら抉[えぐ]られた傷痕めいて、熱く熾[おこ]った。'), True)[0]
        store.kagerou_page = kagerou_page_old + kagerou_page_current
        renpy.show_screen('say', who=None, what=kagerou_page_text())
    show screen kagerou_capture_timer
    $ renpy.pause()

screen kagerou_capture_timer():
    if kagerou_capture_stage < 2:
        add "rscript_ctc"
    timer 1.0 action Function(kagerou_capture) repeat True
