python early:

    def rscript_textbox_state(box=None):
        if box is None:
            box = getattr(store, "rscript_active_box", 0)
        return getattr(store, "rscript_textboxes", {}).get(box, {})

    def rscript_set_textbox(box, **values):
        state = dict(rscript_textbox_state(box))
        state.update(values)
        store.rscript_textboxes[box] = state

    def rscript_set_text_style(box, **values):
        # 42a410/42a460/42aad0: nonzero selects all three auxiliary boxes.
        boxes = (1, 2, 3) if box and getattr(store, "rscript_native_text_metrics", False) else (box,)
        for selected in boxes:
            rscript_set_textbox(selected, **values)

    def rscript_wait_transform(trans, st, at):
        state = rscript_textbox_state()
        pos = state.get("wait_pos")
        if pos is None:
            pos = (store.rscript_ctc_x, store.rscript_ctc_y)
        else:
            # waitloc is relative to tboxloc, not the screen.
            boxpos = state.get("box_pos", (0, config.screen_height -
                getattr(store, "rscript_ui", {}).get("textbox_size", (800, 138))[1]))
            pos = (boxpos[0] + pos[0], boxpos[1] + pos[1])
        trans.xpos, trans.ypos = map(absolute, pos)
        trans.matrixcolor = TintMatrix(state.get("wait_color", "#ffffff"))
        return .1





    def parse_say(lex):
        lang = lex.word()
        # A colon inside a quoted body is not a speaker delimiter.
        # Match the raw Python literal, not lex.string(): the latter collapses
        # spaces and rewrites escapes. The delimiter must be outside quotes.
        who = lex.match(r'''(?:'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z0-9_]*)(?=\s*：)''')
        if who is not None:
            lex.match(r"\s*：")

        what = lex.rest()
        return lang, who, what

    def execute_say(o, interact=True):
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

        # A new unvoiced line must not replay the preceding dialogue's voice.
        if not store.rscript_voice_pending:
            store.rscript_last_voice = None
        store.rscript_voice_pending = False
        rscript_dialogue_begin()
        what, center = parse_rscript_text(what, True)

        if "{nw}" in what:
            store.blank_say = True

        else:
            store.blank_say = False

        store.last_say = what
        store.last_spk = who
        store.last_center = center

        queue_draw(show_window)
        process_draw_queue()
        renpy.say(who, what, interact = interact, show_center = center)
        if interact:
            rscript_dialogue_end()
        if interact and persistent.rscript_stop_voice_on_advance:
            renpy.music.stop(channel = "voice")
            renpy.music.stop(channel = "rscript_voice")

        if store.jump_back_point is None:
            store.jump_back_point = renpy.game.log.current.identifier

    def lint_say(o):
        pass

    renpy.register_statement("_say", parse = parse_say, execute = execute_say, lint = lint_undef)



    def parse_append(lex):
        lang = lex.word()
        what = lex.rest()
        return lang, what

    def execute_append(o, interact=True):
        lang, what = o

        who  = store.last_spk
        store.rscript_voice_pending = False
        rscript_dialogue_begin(append=True)
        what, center = parse_rscript_text(what, True)

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
        renpy.say(who, what, interact = interact, show_center = center)
        if interact:
            rscript_dialogue_end()
        if interact and persistent.rscript_stop_voice_on_advance:
            renpy.music.stop(channel = "voice")
            renpy.music.stop(channel = "rscript_voice")

    renpy.register_statement("_append", parse = parse_append, execute = execute_append, lint = lint_undef)



    def parse_hit(lex):
        lex.expect_eol()

    def execute_hit(o):
        renpy.pause()
        rscript_dialogue_end()

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
        rscript_set_textbox(args.Layer, name_rect=(args.xPos, args.yPos, args.Width, args.Height))

    renpy.register_statement("_namloc", parse = parse_namloc, execute = execute_namloc, lint = lint_undef)



    def parse_tbox(lex):
        args = rscript_arguments(lex, ["boxNo", "mode"])
        lex.expect_eol()
        return args

    def execute_tbox(args):
        store.rscript_active_box = args.boxNo
        store.cur_textbox = rscript_textbox_state().get("background", store.cur_textbox)
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
        rscript_set_textbox(args.boxNo, background=args.Num)
        if args.boxNo == store.rscript_active_box:
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
        return rscript_arguments(lex, ["Box", "X", "Y"])

    def execute_tboxloc(args):
        rscript_set_textbox(args.Box, box_pos=(args.X, args.Y))

    renpy.register_statement("_tboxloc", parse = parse_tboxloc, execute = execute_tboxloc, lint = lint_undef)



    def parse_texcolor(lex):
        return rscript_arguments(lex, ["Box", "Color"])

    def execute_texcolor(args):
        # Modern 43b6d0: numeric palette, matching the engine's text colors.
        colors = ("#000000", "#FFFFFF", "#79F1F2", "#B73333", "#FFDE00",
                  "#F8B1EF", "#7FDFA5", "#C187F6", "#FAA25A")
        color = colors[args.Color] if 0 <= args.Color < len(colors) else colors[0]
        rscript_set_text_style(args.Box, color=color)

    renpy.register_statement("_texcolor", parse = parse_texcolor, execute = execute_texcolor, lint = lint_undef)



    def parse_texfont(lex):
        return rscript_arguments(lex, ["Box", "Slot"])

    def execute_texfont(args):
        rscript_set_text_style(args.Box, font_slot=args.Slot)

    renpy.register_statement("_texfont", parse = parse_texfont, execute = execute_texfont, lint = lint_undef)



    def parse_texloc(lex):
        return rscript_arguments(lex, ["Box", "X", "Y", "Width", "Height"])

    def execute_texloc(args):
        rscript_set_textbox(args.Box, text_rect=(args.X, args.Y, args.Width, args.Height))

    renpy.register_statement("_texloc", parse = parse_texloc, execute = execute_texloc, lint = lint_undef)



    def parse_texmode(lex):
        return rscript_arguments(lex, ["Box", "Mode"])

    def execute_texmode(args):
        # 456c5a/456ce9: 1 centers, 2 right-aligns; other values left-align.
        rscript_set_text_style(args.Box, alignment={1: 0.5, 2: 1.0}.get(args.Mode, 0.0))

    renpy.register_statement("_texmode", parse = parse_texmode, execute = execute_texmode, lint = lint_undef)



    def parse_texpich(lex):
        return rscript_arguments(lex, ["Box", "LinePitch", "CharPitch"])

    def execute_texpich(args):
        rscript_set_text_style(args.Box, pitch=(args.LinePitch, args.CharPitch))

    renpy.register_statement("_texpich", parse = parse_texpich, execute = execute_texpich, lint = lint_undef)



    def parse_texruby(lex):
        return rscript_arguments(lex, ["Box", "FontSlot", "Size", "Offset"])

    def execute_texruby(args):
        # 46ad7e/46a1e8: the first ruby operand selects a font, not alignment.
        rscript_set_text_style(args.Box, ruby=(args.FontSlot, args.Size, args.Offset))

    renpy.register_statement("_texruby", parse = parse_texruby, execute = execute_texruby, lint = lint_undef)



    def parse_texsize(lex):
        return rscript_arguments(lex, ["Box", "Size"])

    def execute_texsize(args):
        rscript_set_text_style(args.Box, size=max(1, args.Size))

    renpy.register_statement("_texsize", parse = parse_texsize, execute = execute_texsize, lint = lint_undef)



    def parse_cmploc(lex):
        return rscript_arguments(lex, ["X", "Y"])

    def execute_cmploc(args):
        store.rscript_compane_position = (args.X, args.Y)

    renpy.register_statement("_cmploc", parse = parse_cmploc, execute = execute_cmploc, lint = lint_undef)



    def parse_waitcol(lex):
        return rscript_arguments(lex, ["Box", "R", "G", "B"])

    def execute_waitcol(args):
        color = "#%02x%02x%02x" % tuple(max(0, min(255, v)) for v in (args.R, args.G, args.B))
        rscript_set_textbox(args.Box, wait_color=color)

    renpy.register_statement("_waitcol", parse = parse_waitcol, execute = execute_waitcol, lint = lint_undef)



    def parse_waitloc(lex):
        return rscript_arguments(lex, ["Box", "X", "Y"])

    def execute_waitloc(args):
        rscript_set_textbox(args.Box, wait_pos=(args.X, args.Y))

    renpy.register_statement("_waitloc", parse = parse_waitloc, execute = execute_waitloc, lint = lint_undef)



    def parse_waitlod(lex):
        return rscript_arguments(lex, ["Box", "Number"])

    def execute_waitlod(args):
        rscript_set_textbox(args.Box, wait_image=args.Number)

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
