# Synthetic audio and temporary saves; never enter a real story or gallery save.
default kagerou_music_test_phase = 0
default kagerou_music_test_ticks = 0

init python:
    def kagerou_music_test_error(short, full, info):
        raise SystemExit(full)
    config.exception_handler = kagerou_music_test_error
    kagerou_test_original_audio_file = rscript_audio_file
    def kagerou_test_audio_file(kind, number):
        if kind == 'bgm':
            return 'short.wav' if number == 1 else 'long.wav'
        return kagerou_test_original_audio_file(kind, number)
    rscript_audio_file = kagerou_test_audio_file
    kagerou_test_original_gallery = kagerou_music_gallery
    def kagerou_test_gallery():
        renpy.show_screen('kagerou_music_test_timer')
        try:
            kagerou_test_original_gallery()
        finally:
            renpy.hide_screen('kagerou_music_test_timer')
    kagerou_music_gallery = kagerou_test_gallery

    def kagerou_music_test_tick():
        store.kagerou_music_test_ticks += 1
        assert kagerou_music_test_ticks < 100, 'Gallery did not complete within 10 seconds'
        phase = kagerou_music_test_phase
        if phase == 0:
            renpy.screenshot(os.path.join(config.basedir, 'music-jp.png'))
            assert kagerou_music_track == 1 and not kagerou_music_playing
            kagerou_music_play()
            store.kagerou_music_test_phase = 1
        elif phase == 1 and kagerou_music_track == 2:
            assert kagerou_music_playing
            assert renpy.music.get_playing('rscript_music') is None
            kagerou_music_pause()
            store.kagerou_music_volume = 128
            kagerou_music_apply_volume()
            _preferences.language = 'zh'
            store.kagerou_music_test_phase = 2
        elif phase == 2:
            assert kagerou_music_track == 2 and kagerou_music_paused
            assert renpy.music.get_pause('kagerou_gallery')
            renpy.screenshot(os.path.join(config.basedir, 'music-zh.png'))
            kagerou_music_pause()
            store.kagerou_music_test_phase = 3
            return renpy.run(Return(True))

    def kagerou_music_test_open():
        renpy.run(rscript_system_action(7))
        assert kagerou_music_test_phase == 3
        assert not kagerou_music_playing and not kagerou_music_paused
        return 47

label before_main_menu:
    python:
        _preferences.language = None
        renpy.music.play('long.wav', channel='rscript_music', loop=True)
        original_volumes = dict(_preferences.volumes)
        result = renpy.call_screen('kagerou_music_test_outer')
        assert result == 47  # Gallery Return must not consume the title's click result.
        renpy.pause(.3, hard=True)
        assert renpy.music.get_playing('rscript_music') is None
        assert renpy.music.get_playing('kagerou_gallery') is None
        assert dict(_preferences.volumes) == original_volumes
        renpy.quit()

screen kagerou_music_test_outer():
    timer .2 action Function(kagerou_music_test_open)

screen kagerou_music_test_timer():
    zorder 200
    timer .1 action Function(kagerou_music_test_tick) repeat True
