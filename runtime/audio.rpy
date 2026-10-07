init python:
    import os

    def rscript_audio_file(kind, number):
        template = getattr(store, "rscript_%s_format" % kind)
        path = template % number
        if kind == "voice" and rscript_voice_groups:
            group, item = divmod(number, 10000)
            path = "voice/%s%04d.ogg" % (("%d/" % group) if group else "", item)
        if renpy.loadable(path):
            return path
        # LiarsoftTool retains genuine PCM WAV rather than re-encoding it.
        stem, extension = os.path.splitext(path)
        for extension in (".ogg", ".wav"):
            candidate = stem + extension
            if renpy.loadable(candidate):
                return candidate
        return path

    def stop_audio():
        renpy.music.stop("music")
        renpy.music.stop("sound")
        renpy.music.stop("voice")
        renpy.music.stop("rscript_voice")
        renpy.music.stop("se0")
        renpy.music.stop("se1")
        renpy.music.stop("se2")

    renpy.music.register_channel(name = "rscript_voice", mixer = "voice", tight = True, loop = False)
    renpy.music.register_channel(name = "se0", mixer = "sfx", tight = True, loop = False)
    renpy.music.register_channel(name = "se1", mixer = "sfx", tight = True, loop = False)
    renpy.music.register_channel(name = "se2", mixer = "sfx", tight = True, loop = False)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
