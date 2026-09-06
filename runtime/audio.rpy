init python:

    def stop_audio():
        renpy.music.stop("music")
        renpy.music.stop("sound")
        renpy.music.stop("voice")
        renpy.music.stop("se0")
        renpy.music.stop("se1")
        renpy.music.stop("se2")

    renpy.music.register_channel(name = "se0", mixer = "sfx", tight = True, loop = False)
    renpy.music.register_channel(name = "se1", mixer = "sfx", tight = True, loop = False)
    renpy.music.register_channel(name = "se2", mixer = "sfx", tight = True, loop = False)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
