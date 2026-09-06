python early:





    def parse_voice(lex):
        args = rscript_arguments(lex, ["VoiceNo", "Repeat", "Fade", "Pan"])
        lex.expect_eol()
        return args

    def execute_voice(args):

        voice_file = "voice/%05d.opus" % args.VoiceNo
        repeat = args.Repeat
        fade   = args.Fade
        pan    = args.Pan
        voice(voice_file)

    renpy.register_statement("_voice", parse = parse_voice, execute = execute_voice, lint = lint_undef)



    def parse_voice_off(lex):
        args = rscript_arguments(lex, ["Fade"])
        lex.expect_eol()
        return args

    def execute_voice_off(args):
        fadeout = args.Fade * 0.5

        renpy.pause(1. / 30.)
        renpy.music.stop(channel = "voice", fadeout = fadeout)

    renpy.register_statement("_voice_off", parse = parse_voice_off, execute = execute_voice_off, lint = lint_undef)



    def parse_voice_wait(lex):
        lex.expect_eol()

    def execute_voice_wait(args):
        renpy.pause(1. / 30.)
        wait_audio("voice")

    renpy.register_statement("_voice_wait", parse = parse_voice_wait, execute = execute_voice_wait, lint = lint_undef)





    def parse_bgm_on(lex):
        args = rscript_arguments(lex, ["BgmNo", "Fade", "FadeLen"])
        lex.expect_eol()
        return args

    def execute_bgm_on(args):
        bgm = "bgm/Track%02d.opus" % args.BgmNo
        fadein = args.Fade * args.FadeLen / 1000.

        renpy.music.play(bgm, channel = "music", fadein = fadein, loop = True, if_changed = True)

    renpy.register_statement("_bgm_on", parse = parse_bgm_on, execute = execute_bgm_on, lint = lint_undef)



    def parse_bgm_off(lex):
        args = rscript_arguments(lex, ["Fade", "FadeLen"])
        lex.expect_eol()
        return args

    def execute_bgm_off(args):
        fadeout = args.Fade * args.FadeLen / 1000.

        renpy.pause(1. / 30.)
        renpy.music.stop(channel = "music", fadeout = fadeout)

    renpy.register_statement("_bgm_off", parse = parse_bgm_off, execute = execute_bgm_off, lint = lint_undef)





    def parse_se(lex):
        args = rscript_arguments(lex, ["Channel", "SeNo"])
        lex.expect_eol()
        return args

    def execute_se(args):
        store.se_queue[args.Channel] = args.SeNo

    renpy.register_statement("_se", parse = parse_se, execute = execute_se, lint = lint_undef)



    def parse_se_on(lex):
        args = rscript_arguments(lex, ["Channel", "Repeat", "Fade", "Pan"])
        lex.expect_eol()
        return args

    def execute_se_on(args):
        channel = "se%d" % args.Channel
        se_file = "wav/%04d.opus" % store.se_queue[args.Channel]
        se_file = [se_file] * (args.Repeat + 1)
        fade    = args.Fade * 0.5
        pan     = args.Pan / 100

        renpy.music.set_pan(pan, 0, channel)
        renpy.music.play(se_file, channel, loop = False, fadein = fade, if_changed = False)

    renpy.register_statement("_se_on", parse = parse_se_on, execute = execute_se_on, lint = lint_undef)



    def parse_se_off(lex):
        args = rscript_arguments(lex, ["Channel", "Fade"])
        lex.expect_eol()
        return args

    def execute_se_off(args):
        channel = "se%d" % args.Channel
        fade    = args.Fade * 0.5

        renpy.pause(1. / 30.)
        renpy.music.stop(channel, fadeout = fade)

    renpy.register_statement("_se_off", parse = parse_se_off, execute = execute_se_off, lint = lint_undef)



    def parse_se_wait(lex):
        lex.expect_eol()

    def execute_se_wait(args):
        renpy.pause(1. / 30.)
        wait_audio("se0")

    renpy.register_statement("_se_wait", parse = parse_se_wait, execute = execute_se_wait, lint = lint_undef)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
