python early:





    def parse_load(lex):
        args = rscript_arguments(lex, ["Layer", "CGNum", "xLoc", "yLoc", "Effect", "Colormode"])
        lex.expect_eol()
        return args

    def execute_load(args):
        loadcls(args.Layer, args.Effect, cg = args.CGNum, xpos = args.xLoc, ypos = args.yLoc, color = args.Colormode)

    def predict_load(args):
        img = "%s %04d" % (folder[args.Layer], args.CGNum)
        return [img]

    def lint_load(args):
        if not isinstance(args.Colormode, (int, float)):
            return

        if not args.Colormode in [0, 1, 2, 3, 4]:
            print("Unhandled colormode for load/clear effect", args.Colormode)

    renpy.register_statement("_load", parse = parse_load, execute = execute_load, predict = predict_load, lint = lint_load)



    def parse_oload(lex):
        args = RScriptArguments()
        for name in ("Layer", "xLoc", "yLoc", "Effect", "Colormode", "Text"):
            args[name] = lex.simple_expression()
        lex.expect_eol()
        return args

    def execute_oload(args):
        if args.Effect != 0:
            raise Exception("Unhandled object load effect %d" % args.Effect)

        layer = args.Layer
        xpos = args.xLoc * store.layer_x_grid
        ypos = args.yLoc * store.layer_y_grid
        anchor = store.layer_anchor.get(layer, (0.0, 0.0))
        tag = "layer%d" % layer
        text_value, _ = parse_rscript_text(repr(args.Text), True)
        font_size = store.object_size.get(layer, gui.text_size)
        text = Text(text_value, font = gui.text_font,
                    size = font_size, color = "#FFFFFF",
                    xmaximum = font_size * 19)
        trans = Transform(
            xpos = xpos,
            ypos = ypos,
            anchor = anchor,
            shader = "rscript.colormode",
            u_colormode = args.Colormode,
        )

        store.layer_info[layer] = text
        store.layer_pos[layer] = (xpos, ypos)
        queue_draw(renpy.show, tag, what = text, at_list = [trans],
                   zorder = store.layer_zorder.get(layer, layer * 2),
                   layer = IMAGE_LAYER)
        process_draw_queue()

    renpy.register_statement("_oload", parse = parse_oload, execute = execute_oload, lint = lint_undef)



    def parse_osize(lex):
        args = rscript_arguments(lex, ["Layer", "Size"])
        lex.expect_eol()
        return args

    def execute_osize(args):
        store.object_size[args.Layer] = args.Size

    renpy.register_statement("_osize", parse = parse_osize, execute = execute_osize, lint = lint_undef)



    def parse_oaction(lex):
        args = rscript_arguments(lex, ["Layer", "Action"])
        lex.expect_eol()
        return args

    def execute_oaction(args):
        if args.Action == 4:
            move_layer(args.Layer, 0, 0, 9, 4, relative = True)
        else:
            raise Exception("Unhandled object action %d" % args.Action)

    renpy.register_statement("_oaction", parse = parse_oaction, execute = execute_oaction, lint = lint_undef)



    def parse_cls(lex):
        args = rscript_arguments(lex, ["Layer", "Effect"])
        lex.expect_eol()
        return args

    def execute_cls(args):
        loadcls(args.Layer, args.Effect, clear = True)

    renpy.register_statement("_cls", parse = parse_cls, execute = execute_cls, lint = lint_undef)



    def parse_gload(lex):
        args = rscript_arguments(lex, ["CGNum", "Colormode"])
        lex.expect_eol()
        return args

    def execute_gload(args):

        img = "grpe %04d" % args.CGNum
        shown_img = img
        if not persistent.widescreen_cg and renpy.has_image(img + "_o"):
            shown_img += "_o"

        at_list = [Transform(shader = "rscript.colormode", u_colormode = args.Colormode)]

        queue_draw(renpy.scene, layer = CG_LAYER)
        queue_draw(renpy.show, shown_img, tag = CG_TAG, layer = CG_LAYER, at_list = at_list)
        process_draw_queue()

        store.layer_info[CG_LAYER] = shown_img
        store.layer_pos[CG_LAYER] = (0, 0)



        persistent.seen_cg[img] = True
        _r[9000 + args.CGNum] = 1

    def predict_gload(args):
        img = "grpe %04d" % args.CGNum
        return [img]

    def lint_gload(args):
        lint_load(args)

    renpy.register_statement("_gload", parse = parse_gload, execute = execute_gload, predict = predict_gload, lint = lint_gload)



    def parse_gcls(lex):
        args = rscript_arguments(lex, ["Mode"])
        lex.expect_eol()
        return args

    def execute_gcls(args):

        if args.Mode == 0:
            img = "black"
        else:
            img = "white"

        queue_draw(renpy.scene, layer = CG_LAYER)
        queue_draw(renpy.show, img, tag = CG_TAG, layer = CG_LAYER)
        process_draw_queue()

        store.layer_info.pop(CG_LAYER, None)
        store.layer_pos.pop(CG_LAYER, None)

    def predict_gcls(args):
        if args.Mode == 0:
            img = "black"
        else:
            img = "white"

        return [img]

    renpy.register_statement("_gcls", parse = parse_gcls, execute = execute_gcls, lint = lint_undef)





    def parse_move(lex):
        args = rscript_arguments(lex, ["Layer", "xLoc", "yLoc", "Effect", "Speed"])
        lex.expect_eol()
        return args

    def execute_move(args):
        move_layer(args.Layer, args.xLoc, args.yLoc, args.Effect, args.Speed, relative = False)

    renpy.register_statement("_move", parse = parse_move, execute = execute_move, lint = lint_undef)



    def parse_movi(lex):
        args = rscript_arguments(lex, ["Layer", "xDef", "yDef", "Effect", "Speed"])
        lex.expect_eol()
        return args

    def execute_movi(args):
        move_layer(args.Layer, args.xDef, args.yDef, args.Effect, args.Speed, relative = True)

    renpy.register_statement("_movi", parse = parse_movi, execute = execute_movi, lint = lint_undef)



    def parse_gmove(lex):
        args = rscript_arguments(lex, ["Effect", "xLoc", "yLoc", "Speed"])
        lex.expect_eol()
        return args

    def execute_gmove(args):
        move_layer(CG_LAYER, args.xLoc, args.yLoc, args.Effect, args.Speed, relative = False)

    renpy.register_statement("_gmove", parse = parse_gmove, execute = execute_gmove, lint = lint_undef)





    def parse_queue(lex):
        lex.expect_eol()

    def execute_queue(args):
        store.in_queue = True

    renpy.register_statement("_queue", parse = parse_queue, execute = execute_queue, lint = lint_undef)



    def parse_action(lex):
        lex.expect_eol()

    def execute_action(args):
        store.in_queue = False

        process_draw_queue()

    renpy.register_statement("_action", parse = parse_action, execute = execute_action, lint = lint_undef)



    def parse_update(lex):
        args = rscript_arguments(lex, ["Effect", "Step", "Wait"])
        lex.expect_eol()
        return args

    def execute_update(args):
        effect = args.Effect
        step   = args.Step
        wait   = args.Wait


        ef_time = step * wait / 1000.
        trans = None

        if effect == 0:
            trans = None

        elif effect == 1:
            trans = Dissolve(ef_time)

        elif effect == 2:
            trans = Pixellate(ef_time, step / 2)

        elif effect == 3:
            trans = Fade(ef_time, 0.0, ef_time, color = "#FFFFFF")

        elif effect == 4:
            trans = Fade(ef_time, 0.0, ef_time, color = "#000000")

        elif effect >= 11:
            trans = rscript_ef(effect, step, wait)


        queue_draw_delayed(renpy.with_statement, trans)

        store.in_queue = False
        process_draw_queue()

    renpy.register_statement("_update", parse = parse_update, execute = execute_update, lint = lint_undef)



    def parse_zupdate(lex):
        args = rscript_arguments(lex, ["Effect", "Locate"])
        lex.expect_eol()
        return args

    def execute_zupdate(args):
        anchors = {
      0: (0.5, 0.5),
      1: (0.0, 1.0),
      2: (0.5, 1.0),
      3: (1.0, 1.0),
      4: (0.0, 0.5),
      5: (0.5, 0.5),
      6: (1.0, 0.5),
      7: (0.0, 0.0),
      8: (0.5, 0.0),
      9: (1.0, 0.0),
    }

        anchor = anchors.get(args.Locate, (0.5, 0.5))

        if args.Effect == 1:
            queue_draw(renpy.with_statement, zupdate_in(new_anchor = anchor))

        else:
            raise Exception("zupdate effect %d not defined." % args.Effect)

        store.in_queue = False
        process_draw_queue()

    renpy.register_statement("_zupdate", parse = parse_zupdate, execute = execute_zupdate, lint = lint_undef)





    def parse_group(lex):
        args = rscript_arguments(lex, ["Layer", "Group"])
        lex.expect_eol()
        return args


    def execute_group(args):
        pass

    renpy.register_statement("_group", parse = parse_group, execute = execute_group, lint = lint_undef)



    def parse_mode(lex):
        args = rscript_arguments(lex, ["Layer", "Mode"])
        lex.expect_eol()
        return args



    def execute_mode(args):
        pass

    renpy.register_statement("_mode", parse = parse_mode, execute = execute_mode, lint = lint_undef)



    def parse_depth(lex):
        args = rscript_arguments(lex, ["Layer", "Depth"])
        lex.expect_eol()
        return args

    def execute_depth(args):
        layer_zorder[args.Layer] = args.Depth * 2

    renpy.register_statement("_depth", parse = parse_depth, execute = execute_depth, lint = lint_undef)



    def parse_draw(lex):
        args = rscript_arguments(lex, ["Layer", "Mode", "Level"])
        lex.expect_eol()
        return args

    def execute_draw(args):
        layer_blend[args.Layer] = (args.Mode, args.Level)

    def lint_draw(args):
        if args.Mode == 3:
            print("[Lint] Unhandled blend mode:", args.Mode)

    renpy.register_statement("_draw", parse = parse_draw, execute = execute_draw, lint = lint_draw)



    def parse_effect(lex):
        args = rscript_arguments(lex, ["EffectNo", "Mode"])
        lex.expect_eol()
        return args

    def execute_effect(args):
        queue_draw(_execute_effect, args)
        process_draw_queue()





    def _execute_effect(args):

        if args.EffectNo == 0:
            renpy.hide(EFFECT_TAG, layer = IMAGE_LAYER)


        elif args.EffectNo >= 11:
            img = "grps es%03d" % args.EffectNo
            at_list = [Transform(shader = "rscript.effect", u_effectmode = args.Mode)]
            renpy.show(img, zorder = store.effect_zorder, tag = EFFECT_TAG, layer = IMAGE_LAYER, at_list = at_list)
            renpy.pause(1. / 120.)

        else:
            raise Exception("Effect %d not defined." % args.EffectNo)

    renpy.register_statement("_effect", parse = parse_effect, execute = execute_effect, lint = lint_undef)



    def parse_effectdep(lex):
        args = rscript_arguments(lex, ["Depth"])
        lex.expect_eol()
        return args

    def execute_effectdep(args):
        store.effect_zorder = args.Depth * 2

    renpy.register_statement("_effectdep", parse = parse_effectdep, execute = execute_effectdep, lint = lint_undef)



    def parse_enabl(lex):
        args = rscript_arguments(lex, ["Layer", "Mode"])
        lex.expect_eol()
        return args

    def execute_enabl(args):
        layer_enabled[args.Layer] = args.Mode

    renpy.register_statement("_enabl", parse = parse_enabl, execute = execute_enabl, lint = lint_undef)



    def parse_flash(lex):
        args = rscript_arguments(lex, ["Repeat", "Effect"])
        lex.expect_eol()
        return args

    def execute_flash(args):
        dur = 1 / 30.
        count = args.Repeat
        color = "#0000"
        ef = flash
        time = dur * count * 2

        if args.Effect == 0:
            color = "#FFFFFF"



        elif args.Effect == 1:
            ef = flash_multi
            time = dur * count * 2 * 6

        elif args.Effect == 2:
            color = "#CE0101"

        elif args.Effect == 3:
            color = "#FFF000"

        else:
            raise Exception("Flash color %d not defined." % args.Effect)

        hide_window(Dissolve(0.5))
        renpy.show("nothing", layer = FLASH_LAYER, at_list = [ef(color, dur, count)], tag = FLASH_TAG)
        renpy.pause(time)
        renpy.hide(FLASH_TAG, layer = FLASH_LAYER)

    renpy.register_statement("_flash", parse = parse_flash, execute = execute_flash, lint = lint_undef)



    def parse_folder(lex):
        args = rscript_arguments(lex, ["Layer", "Folder"])
        lex.expect_eol()
        return args

    def execute_folder(args):
        store.folder[args.Layer] = args.Folder

    renpy.register_statement("_folder", parse = parse_folder, execute = execute_folder, lint = lint_undef)



    def parse_locgrid(lex):
        args = rscript_arguments(lex, ["Xgrid", "Ygrid"])
        lex.expect_eol()
        return args

    def execute_locgrid(args):
        layer_x_grid = args.Xgrid or 1
        layer_y_grid = args.Ygrid or 1

    renpy.register_statement("_locgrid", parse = parse_locgrid, execute = execute_locgrid, lint = lint_undef)



    def parse_locmode(lex):
        args = rscript_arguments(lex, ["Layer", "Xmode", "Ymode"])
        lex.expect_eol()
        return args

    def execute_locmode(args):
        store.layer_anchor[args.Layer] = (
        0.0 if args.Xmode == 0 else 0.5,
        0.0 if args.Ymode == 0 else 0.5
      )

    renpy.register_statement("_locmode", parse = parse_locmode, execute = execute_locmode, lint = lint_undef)



    def parse_locmap(lex):
        rscript_arguments(lex)
        lex.expect_eol()
        return args


    def execute_locmap(args):
        pass

    renpy.register_statement("_locmap", parse = parse_locmode, execute = execute_locmode, lint = lint_undef)



    def parse_movie(lex):
        args = rscript_arguments(lex, ["MovieNo"])
        lex.expect_eol()
        return args

    def execute_movie(args):
        renpy.movie_cutscene("mov/%04d.webm" % args.MovieNo)

    renpy.register_statement("_movie", parse = parse_movie, execute = execute_movie, lint = lint_undef)



    def parse_quake(lex):
        args = rscript_arguments(lex, ["Repeat", "Effect"])
        lex.expect_eol()
        return args

    def execute_quake(args):
        count = args.Repeat
        dur = 0.064 * count * 2
        x_range = 96
        y_range = 72


        if args.Effect == 0:
            quake(dur, x = x_range, y = 0)


        elif args.Effect == 1:
            quake(dur, x = 0, y = y_range)

        else:
            quake(dur, x_range, y_range)

    renpy.register_statement("_quake", parse = parse_quake, execute = execute_quake, lint = lint_undef)



    def parse_tone(lex):
        args = rscript_arguments(lex, ["Level", "Mode"])
        lex.expect_eol()
        return args

    def execute_tone(args):
        queue_draw(_execute_tone, args)
        process_draw_queue()





    def _execute_tone(args):

        if args.Level == 0:
            renpy.hide(TONE_TAG, layer = TONE_LAYER)
            store.tone_color = None
            store.tone_level = 0

        else:
            img = "black" if args.Mode == 0 else "white"
            trans = Transform(alpha = args.Level / 100.)

            store.tone_color = img
            store.tone_level = args.Level
            renpy.show(img, tag = TONE_TAG, layer = TONE_LAYER, at_list = [trans], zorder = store.tonedep)

    renpy.register_statement("_tone", parse = parse_tone, execute = execute_tone, lint = lint_undef)



    def parse_tonedep(lex):
        args = rscript_arguments(lex, ["Depth"])
        lex.expect_eol()
        return args

    def execute_tonedep(args):

        store.tonedep = args.Depth * 2 - 1

        if renpy.showing(TONE_TAG, TONE_LAYER) and store.tone_color:
            args.Mode = 0 if store.tone_color == "black" else 1
            args.Level = store.tone_level

            queue_draw(_execute_tone, args)



    renpy.register_statement("_tonedep", parse = parse_tonedep, execute = execute_tonedep, lint = lint_undef)



    def parse_numenable(lex):
        args = rscript_arguments(lex, ["NumLayerNo", "Mode"])
        lex.expect_eol()
        return args


    def execute_numenable(args):
        pass

    renpy.register_statement("_numenable", parse = parse_numenable, execute = execute_numenable, lint = lint_undef)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
