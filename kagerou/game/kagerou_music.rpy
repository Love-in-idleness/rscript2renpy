default kagerou_music_track = 1
default kagerou_music_playing = False
default kagerou_music_paused = False
default kagerou_music_started = False
default kagerou_music_volume = 255

init python:
    # 41b5a5 calls the audio backend directly, bypassing the script BGM switch.
    renpy.music.register_channel("kagerou_gallery", mixer=None, loop=False)

    def kagerou_music_tracks():
        items = rscript_layouts()["muscmenu"]["items"]
        return tuple(n for n in range(1, 21) if str(n) in items)

    def kagerou_music_apply_volume():
        # 4512b0: truncate (WORD - 255) * 3000 / 255 toward zero, in 0.01 dB.
        attenuation = -((255 - int(kagerou_music_volume)) * 3000 // 255)
        renpy.music.set_volume(10 ** (attenuation / 2000.0), channel="kagerou_gallery")

    def kagerou_music_stop():
        renpy.music.stop(channel="kagerou_gallery", fadeout=0)
        renpy.music.set_pause(False, channel="kagerou_gallery")
        store.kagerou_music_playing = store.kagerou_music_paused = False
        store.kagerou_music_started = False

    def kagerou_music_begin():
        kagerou_music_stop()
        store.kagerou_music_track = 1
        store.kagerou_music_volume = round(_preferences.volumes.get("music", 1.0) * 255)
        kagerou_music_apply_volume()

    def kagerou_music_play():
        if kagerou_music_playing:
            return
        path = rscript_audio_file("bgm", kagerou_music_track)
        if not renpy.loadable(path):
            renpy.log("Kagerou: missing music gallery track %s" % path)
            return
        renpy.music.play(path, channel="kagerou_gallery", loop=False, fadeout=0)
        store.kagerou_music_playing = True
        store.kagerou_music_started = False

    def kagerou_music_select(track):
        if track not in kagerou_music_tracks():
            return
        play = kagerou_music_playing or track == kagerou_music_track
        if kagerou_music_playing:
            kagerou_music_stop()
        store.kagerou_music_track = track
        if play:
            kagerou_music_play()

    def kagerou_music_pause():
        if kagerou_music_playing:
            store.kagerou_music_paused = not kagerou_music_paused
            renpy.music.set_pause(kagerou_music_paused, channel="kagerou_gallery")

    def kagerou_music_previous():
        tracks = kagerou_music_tracks()
        index = tracks.index(kagerou_music_track)
        if index:
            kagerou_music_select(tracks[index - 1])

    def kagerou_music_next():
        tracks = kagerou_music_tracks()
        index = tracks.index(kagerou_music_track)
        if index + 1 < len(tracks):
            kagerou_music_select(tracks[index + 1])
        else:
            kagerou_music_stop()
            kagerou_music_select(tracks[0])

    def kagerou_music_tick():
        if not kagerou_music_playing or kagerou_music_paused:
            return
        if renpy.music.is_playing(channel="kagerou_gallery"):
            store.kagerou_music_started = True
        elif kagerou_music_started:
            # Do not mistake the asynchronous decoder's startup for completion.
            kagerou_music_next()

    def kagerou_music_gallery():
        kagerou_music_begin()
        try:
            renpy.call_screen("kagerou_music_gallery")
        finally:
            kagerou_music_stop()

    def kagerou_open_music():
        # Stop in the outer context too, so leaving the gallery cannot restore BGM.
        renpy.music.stop(channel="music", fadeout=0)
        renpy.music.stop(channel="rscript_music", fadeout=0)
        store.rscript_bgm_number = 0
        try:
            renpy.invoke_in_new_context(kagerou_music_gallery)
        finally:
            kagerou_music_stop()

    rscript_ui.setdefault("system_actions", {})[7] = Function(kagerou_open_music)

screen kagerou_music_gallery():
    tag menu
    modal True
    key "game_menu" action Return(True)
    key "rollback" action NullAction()
    timer .1 action Function(kagerou_music_tick) repeat True
    $ layout = rscript_layouts()["muscmenu"]
    $ items = layout["items"]
    fixed:
        xysize layout["size"]
        align (0.5, 0.5)
        add rscript_ui_image("muscmenu", "bg") pos items["bg"][:2]
        for track in kagerou_music_tracks():
            if kagerou_music_playing and kagerou_music_track == track:
                add rscript_ui_image("muscmenu", "%d_p" % track) pos items["%d_p" % track][:2]
            else:
                use rscript_grps_button("muscmenu", str(track), Function(kagerou_music_select, track),
                                       selected=(kagerou_music_track == track))
        use rscript_grps_button("muscmenu", "play", Function(kagerou_music_play), selected=kagerou_music_playing)
        use rscript_grps_button("muscmenu", "pause", Function(kagerou_music_pause), selected=kagerou_music_paused)
        use rscript_grps_button("muscmenu", "stop", Function(kagerou_music_stop), selected=(not kagerou_music_playing))
        use rscript_grps_button("muscmenu", "rev", Function(kagerou_music_previous))
        use rscript_grps_button("muscmenu", "fow", Function(kagerou_music_next))
        use rscript_grps_button("muscmenu", "exit", Return(True))
        # 41ac16..41ac89 uses level only for geometry, then releases its bitmap.
        bar:
            style "rscript_volume_bar"
            value VariableValue("kagerou_music_volume", 255, step=1, action=Function(kagerou_music_apply_volume))
            base_bar Solid("#00000000")
            thumb rscript_ui_image("muscmenu", "bar")
            hover_thumb rscript_ui_image("muscmenu", "bar_f")
            pos items["level"][:2]
            xysize items["level"][2:]
