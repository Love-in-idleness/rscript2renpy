python early:





    def parse_say(lex):
        lang = lex.word()
        who = lex.match(r"(.*?)：")

        what = lex.rest()
        return lang, who, what

    def execute_say(o):
        lang, who, what = o

        if who:
            who = who.strip(u"：")
            who = eval(who)

            voice_tag = get_voice_tag(who)


            if not store.nvl_mode:
                who = Character(who, kind = rscript_adv, voice_tag = voice_tag)
            else:
                who = CharacterNVL(who, kind = rscript_nvl, voice_tag = voice_tag)

        else:
            if not store.nvl_mode:
                who = narrator
            else:
                who = nvl_narrator

        what, center = parse_rscript_text(what)

        if "{nw}" in what:
            store.blank_say = True

        else:
            store.blank_say = False

        store.last_say = what
        store.last_spk = who
        store.last_center = center

        queue_draw(show_window)
        process_draw_queue()
        renpy.say(who, what, interact = True, show_center = center)

        if store.jump_back_point is None:
            store.jump_back_point = renpy.game.log.current.identifier

    def lint_say(o):
        pass

    renpy.register_statement("_say", parse = parse_say, execute = execute_say, lint = lint_undef)



    def parse_append(lex):
        lang = lex.word()
        what = lex.rest()
        return lang, what

    def execute_append(o):
        lang, what = o

        who  = store.last_spk
        what, center = parse_rscript_text(what)

        if "{nw}" in what:
            store.blank_say = True

        else:
            store.blank_say = False

        what = store.last_say + "{fast}" + what
        center = store.last_center or center

        store.last_say = what
        store.last_spk = who
        store.last_center = center

        queue_draw(show_window)
        process_draw_queue()

        who.do_extend()
        renpy.say(who, what, interact = True, show_center = center)

    renpy.register_statement("_append", parse = parse_append, execute = execute_append, lint = lint_undef)



    def parse_hit(lex):
        lex.expect_eol()

    def execute_hit(o):
        renpy.pause()

    renpy.register_statement("_hit", parse = parse_hit, execute = execute_hit, lint = lint_undef)



    def parse_hitc(lex):
        lex.expect_eol()

    def execute_hitc(o):
        renpy.pause()
        store.blank_say = False

        store.last_say = None
        store.last_spk = None

    renpy.register_statement("_hitc", parse = parse_hitc, execute = execute_hitc, lint = lint_undef)



    def parse_prompt(lex):
        msg = lex.string()
        lex.require(":")
        lex.expect_eol()
        lex.expect_block("Block expected for prompt function.")


        sub = lex.subblock_lexer()

        choices = [msg]
        blocks = [None]

        while sub.advance():
            sub.require("_option")
            choice = sub.string()
            sub.require(":")
            sub.expect_eol()

            block = sub.subblock_lexer().renpy_block()

            choices.append(choice)
            blocks.append(block)

        return choices, blocks

    def execute_prompt(o):
        store.jump_back_point = renpy.game.log.current.identifier

        choices, blocks = o

        items = []
        for i, choice in enumerate(choices):
            block = blocks[i]
            if block:
                items.append((choice, i))
            else:
                items.append((choice, None))

        result = renpy.display_menu(items, interact = True, screen = "choice")
        renpy.pause(1.0)

        if not result is None:
            renpy.jump(blocks[result])

    renpy.register_statement("_prompt", parse = parse_prompt, execute = execute_prompt, lint = lint_undef, block = True)




















    def parse_namloc(lex):
        args = rscript_arguments(lex, ["Layer", "xPos", "yPos", "Width", "Height"])
        lex.expect_eol()
        return args


    def execute_namloc(args):
        pass

    renpy.register_statement("_namloc", parse = parse_namloc, execute = execute_namloc, lint = lint_undef)



    def parse_tbox(lex):
        args = rscript_arguments(lex, ["boxNo", "mode"])
        lex.expect_eol()
        return args

    def execute_tbox(args):
        if args.mode == 0:
            queue_draw(hide_window)

        else:
            queue_draw(show_window)

    renpy.register_statement("_tbox", parse = parse_tbox, execute = execute_tbox, lint = lint_undef)



    def parse_tboxback(lex):
        args = rscript_arguments(lex, ["boxNo", "Num"])
        lex.expect_eol()
        return args

    def execute_tboxback(args):
        store.cur_textbox = args.Num

    renpy.register_statement("_tboxback", parse = parse_tboxback, execute = execute_tboxback, lint = lint_undef)



    def parse_tboxcmp(lex):
        args = rscript_arguments(lex, ["Mode"])
        lex.expect_eol()
        return args

    def execute_tboxcmp(args):
        store.textbox_panel = args.Mode

    renpy.register_statement("_tboxcmp", parse = parse_tboxcmp, execute = execute_tboxcmp, lint = lint_undef)



    def parse_tboxloc(lex):
        return (lex.rest(),)

    def execute_tboxloc(o):
        pass

    renpy.register_statement("_tboxloc", parse = parse_tboxloc, execute = execute_tboxloc, lint = lint_undef)



    def parse_texcolor(lex):
        return (lex.rest(),)

    def execute_texcolor(o):
        pass

    renpy.register_statement("_texcolor", parse = parse_texcolor, execute = execute_texcolor, lint = lint_undef)



    def parse_texfont(lex):
        return (lex.rest(),)

    def execute_texfont(o):
        pass

    renpy.register_statement("_texfont", parse = parse_texfont, execute = execute_texfont, lint = lint_undef)



    def parse_texloc(lex):
        return (lex.rest(),)

    def execute_texloc(o):
        pass

    renpy.register_statement("_texloc", parse = parse_texloc, execute = execute_texloc, lint = lint_undef)



    def parse_texmode(lex):
        return (lex.rest(),)

    def execute_texmode(o):
        pass

    renpy.register_statement("_texmode", parse = parse_texmode, execute = execute_texmode, lint = lint_undef)



    def parse_texpich(lex):
        return (lex.rest(),)

    def execute_texpich(o):
        pass

    renpy.register_statement("_texpich", parse = parse_texpich, execute = execute_texpich, lint = lint_undef)



    def parse_texruby(lex):
        return (lex.rest(),)

    def execute_texruby(o):
        pass

    renpy.register_statement("_texruby", parse = parse_texruby, execute = execute_texruby, lint = lint_undef)



    def parse_texsize(lex):
        return (lex.rest(),)

    def execute_texsize(o):
        pass

    renpy.register_statement("_texsize", parse = parse_texsize, execute = execute_texsize, lint = lint_undef)



    def parse_cmploc(lex):
        return (lex.rest(),)

    def execute_cmploc(o):
        pass

    renpy.register_statement("_cmploc", parse = parse_cmploc, execute = execute_cmploc, lint = lint_undef)



    def parse_waitcol(lex):
        return (lex.rest(),)

    def execute_waitcol(o):
        pass

    renpy.register_statement("_waitcol", parse = parse_waitcol, execute = execute_waitcol, lint = lint_undef)



    def parse_waitloc(lex):
        return (lex.rest(),)

    def execute_waitloc(o):
        pass

    renpy.register_statement("_waitloc", parse = parse_waitloc, execute = execute_waitloc, lint = lint_undef)



    def parse_waitlod(lex):
        return (lex.rest(),)

    def execute_waitlod(o):
        pass

    renpy.register_statement("_waitlod", parse = parse_waitlod, execute = execute_waitlod, lint = lint_undef)



    def parse_txcls(lex):
        args = rscript_arguments(lex, ["boxNo"])
        lex.expect_eol()
        return args

    def execute_txcls(o):
        store.blank_say = False
        store.last_say = None
        store.last_spk = None

    renpy.register_statement("_txcls", parse = parse_txcls, execute = execute_txcls, lint = lint_undef)



    def parse_texindent(lex):
        args = rscript_arguments(lex, ["boxNo", "Mode", "Indent"])
        lex.expect_eol()
        return args

    def execute_texindent(args):
        store.text_indent = args.Indent

    renpy.register_statement("_texindent", parse = parse_texindent, execute = execute_texindent, lint = lint_undef)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
