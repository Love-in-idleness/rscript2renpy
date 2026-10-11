# Disposable fixture: neither enter the story nor use the real project's saves.
default kagerou_capture_stage = 0

init python:
    def kagerou_capture_error(short, full, info):
        raise SystemExit(full)
    config.exception_handler = kagerou_capture_error

    def kagerou_capture():
        name = ('vertical.png', 'horizontal.png', 'preferences-jp.png',
                'preferences-zh.png')[kagerou_capture_stage]
        renpy.screenshot(os.path.join(config.basedir, name))
        if kagerou_capture_stage == 3:
            renpy.quit()
        store.kagerou_capture_stage += 1
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
        store.kagerou_page_current = '【女】\n『甲乙』「丙丁」【戊己】。横排的文字与等待图标。'
        store.kagerou_page = kagerou_page_current
        renpy.show_screen('say', who=None, what=kagerou_page_text())
        renpy.restart_interaction()

label before_main_menu:
    scene expression 'grpe/1001.png' onlayer master
    python:
        kagerou_init_textbox()
        persistent.rscript_text_cps = 0
        store.textbox_panel = 1
        store.kagerou_page_old = '先の段落です。旧段落の濃さを確かめます。{fast}\n'
        store.kagerou_page_current = '【女】\n『甲乙』「丙丁」【戊己】。横排と竖排を切り替え、文字と操作パネルの位置を確認します。' * 5
        store.kagerou_page = kagerou_page_old + kagerou_page_current
        renpy.show_screen('say', who=None, what=kagerou_page_text())
    show screen kagerou_capture_timer
    $ renpy.pause()

screen kagerou_capture_timer():
    if kagerou_capture_stage < 2:
        add "rscript_ctc"
    timer 1.0 action Function(kagerou_capture) repeat True
