python early:





    def parse_define(lex):
        name   = lex.match(r"(?u)[\*\@][\w\d_]+")
        target = lex.rest()
        lex.expect_eol()

        return name, target

    def execute_define(o):
        name, target = o


        if name.startswith("*"):
            name = name[1:]
            _macros[name] = compile_macro(name, target)


        elif name.startswith("@"):
            name = name[1:]
            persistent._defs[name] = target

    renpy.register_statement("_define", parse = parse_define, execute = execute_define, lint = lint_undef, init = True, init_priority = -100)



    _m1_02_rscript_cmd__MACRO_COUNT = {}

    def parse_macro(lex):
        name = lex.match(r"[^\s]+")
        params = lex.rest()
        lex.expect_eol()

        fn = rscript_filename(lex)
        if not fn in _m1_02_rscript_cmd__MACRO_COUNT:
            _m1_02_rscript_cmd__MACRO_COUNT[fn] = 0

        else:
            _m1_02_rscript_cmd__MACRO_COUNT[fn] += 1

        loc = (fn, _m1_02_rscript_cmd__MACRO_COUNT[fn])

        return name, params, loc

    def execute_macro(o):
        name, params, loc = o

        renpy.call(_macros[name], _rscript_macro_args = params)

    def label_macro(o):
        name, params, loc = o
        fn, count = loc
        return rscript_post_label("macro_pre", fn, name, count)

    def post_label_macro(o):
        name, params, loc = o
        fn, count = loc
        return rscript_post_label("macro", fn, name, count)

    renpy.register_statement("_macro",
    parse = parse_macro,
    execute = execute_macro,
    label = label_macro,
    post_label = post_label_macro,
    lint = lint_undef)



    _m1_02_rscript_cmd__INCLUDE_COUNT = {}

    def parse_include(lex):
        global _m1_02_rscript_cmd__INCLUDE_COUNT

        name = lex.match(r"(?u)[\w\d_]+")
        dot  = lex.match(r"\.")
        ext  = lex.word()
        lex.expect_eol()

        fn = rscript_filename(lex)
        if not fn in _m1_02_rscript_cmd__INCLUDE_COUNT:
            _m1_02_rscript_cmd__INCLUDE_COUNT[fn] = 0

        else:
            _m1_02_rscript_cmd__INCLUDE_COUNT[fn] += 1

        loc = (fn, _m1_02_rscript_cmd__INCLUDE_COUNT[fn])

        return name, loc

    def execute_include(o):
        name, loc = o
        renpy.call("_%s" % name)

    def execute_include_init(o):
        name, loc = o
        fn, count = loc
        _includes.add(name)

    def post_label_include(o):
        name, loc = o
        fn, count = loc
        return rscript_post_label("include", fn, name, count)

    renpy.register_statement("_include",
    parse = parse_include,
    execute = execute_include,
    execute_init = execute_include_init,
    init_priority = -90,
    post_label = post_label_include,
    lint = lint_undef)



    def parse_jump(lex):
        name = lex.match(r"[^\s]+")
        lex.expect_eol()
        return name

    def execute_jump(o):
        name = o
        renpy.jump(rscript_label(name))

    renpy.register_statement("_jump", parse = parse_jump, execute = execute_jump, lint = lint_undef)



    def parse_goto(lex):
        name = lex.match(r"[^\s]+")
        lex.expect_eol()
        return name

    def execute_goto(o):
        name = o
        script = current_script()
        renpy.jump(rscript_label_local(script, name))

    renpy.register_statement("_goto", parse = parse_goto, execute = execute_goto, lint = lint_undef)



    _m1_02_rscript_cmd__GOSUB_COUNT = {}

    def parse_gosub(lex):
        global _m1_02_rscript_cmd__GOSUB_COUNT

        name = lex.match(r"[^\s]+")
        items = lex.rest().split()

        params = []
        for i in range(10):
            params.append(items[i] if i < len(items) else "0")

        lex.expect_eol()

        fn = rscript_filename(lex)
        if not fn in _m1_02_rscript_cmd__GOSUB_COUNT:
            _m1_02_rscript_cmd__GOSUB_COUNT[fn] = 0

        else:
            _m1_02_rscript_cmd__GOSUB_COUNT[fn] += 1

        loc = (fn, _m1_02_rscript_cmd__GOSUB_COUNT[fn])

        return name, params, loc

    def execute_gosub(o):
        name, params, loc = o

        if store._macro_params:
            params = store._macro_params


        for i, param in enumerate(params):
            _r[10 + i] = eval(param)

        renpy.call(rscript_label(name))

    def post_label_gosub(o):
        name, params, loc = o
        fn, count = loc
        return rscript_post_label("gosub", fn, name, count)

    renpy.register_statement("_gosub",
    parse = parse_gosub,
    execute = execute_gosub,
    post_label = post_label_gosub,
    lint = lint_undef)



    _m1_02_rscript_cmd__INSUB_COUNT = {}

    def parse_insub(lex):
        global _m1_02_rscript_cmd__INSUB_COUNT

        name = lex.match(r"[^\s]+")
        items = lex.rest().split()

        params = []
        for i in range(10):
            params.append(items[i] if i < len(items) else "0")

        lex.expect_eol()

        fn = rscript_filename(lex)
        if not fn in _m1_02_rscript_cmd__INSUB_COUNT:
            _m1_02_rscript_cmd__INSUB_COUNT[fn] = 0

        else:
            _m1_02_rscript_cmd__INSUB_COUNT[fn] += 1

        loc = (fn, _m1_02_rscript_cmd__INSUB_COUNT[fn])

        return name, params, loc

    def execute_insub(o):
        name, params, loc = o
        script = current_script()

        if store._macro_params:
            params = store._macro_params


        for i, param in enumerate(params):
            _r[10 + i] = eval(param)

        renpy.call(name if name.startswith("_") and renpy.has_label(name)
                   else rscript_label_local(script, name))

    def label_insub(o):
        name, params, loc = o
        fn, count = loc
        return rscript_post_label("insub_pre", fn, name, count)

    def post_label_insub(o):
        name, params, loc = o
        fn, count = loc
        return rscript_post_label("insub", fn, name, count)

    renpy.register_statement("_insub",
    parse = parse_insub,
    execute = execute_insub,
    label = label_insub,
    post_label = post_label_insub,
    lint = lint_undef)



    def parse_return(lex):
        retval = lex.rest() or "0"
        lex.expect_eol()

        return retval

    def execute_return(retval):
        _r[0] = eval(retval)
        renpy.return_statement()

    renpy.register_statement("_return", parse = parse_return, execute = execute_return, lint = lint_undef)



    def parse_end(lex):
        lex.expect_eol()

    def execute_end(args):
        renpy.full_restart()

    renpy.register_statement("_end", parse = parse_end, execute = execute_end, lint = lint_undef)



    def parse_data(lex):
        params = lex.rest().split()
        start = params[0]
        data  = params[1:]

        return start, data

    def execute_data(o):
        start, data = o

        start = eval(start)
        for i in range(len(data)):
            _r[start + i] = eval(data[i])

    renpy.register_statement("_data", parse = parse_data, execute = execute_data, lint = lint_undef)



    def parse_backup(lex):
        lex.expect_eol()

    def execute_backup(o):
        renpy.save("backup")

    renpy.register_statement("_backup", parse = parse_backup, execute = execute_backup, lint = lint_undef)



    def parse_wait(lex):
        args = rscript_arguments(lex, ["Wait"])
        lex.expect_eol()
        return args

    def execute_wait(args):
        delay = args.Wait or 10
        renpy.pause(delay / 10.)

    renpy.register_statement("_wait", parse = parse_wait, execute = execute_wait, lint = lint_undef)



    def parse_stop(lex):
        lex.expect_eol()

    def execute_stop(o):
        config.skipping = None

    renpy.register_statement("_stop", parse = parse_stop, execute = execute_stop, lint = lint_undef)



    def parse_sysmode(lex):
        args = rscript_arguments(lex, ["menu", "save", "warp", "roll", "resm"])
        lex.expect_eol()
        return args

    def execute_sysmode(args):
        store.menu_enabled = eval(args["menu"])
        store.save_enabled = eval(args["save"])
        store.warp_enabled = eval(args["warp"])
        store.roll_enabled = eval(args["roll"])
        store.resm_enabled = eval(args["resm"])

    renpy.register_statement("_sysmode", parse = parse_sysmode, execute = execute_sysmode, lint = lint_undef)



    def parse_logflash(lex):
        lex.expect_eol()

    def execute_logflash(args):
        _history_list.clear()

    renpy.register_statement("_logflash", parse = parse_logflash, execute = execute_logflash, lint = lint_undef)







    def parse_makesave(lex):
        lex.expect_eol()

    def execute_makesave(o):
        pass

    renpy.register_statement("_makesave", parse = parse_makesave, execute = execute_makesave, lint = lint_undef)



    def parse_autoreset(lex):
        args = rscript_arguments(lex, ["Mode"])
        lex.expect_eol()
        return args

    def execute_autoreset(o):
        store.rscript_click_autoreset = bool(o.Mode)

    renpy.register_statement("_autoreset", parse = parse_autoreset, execute = execute_autoreset, lint = lint_undef)



    def parse_break(lex):
        return (lex.rest(),)

    def execute_break(o):
        pass

    renpy.register_statement("_break", parse = parse_break, execute = execute_break, lint = lint_undef)



    def parse_continue(lex):
        return (lex.rest(),)

    def execute_continue(o):
        pass

    renpy.register_statement("_continue", parse = parse_continue, execute = execute_continue, lint = lint_undef)



    def parse_click(lex):
        args = rscript_arguments(lex, ["Timer", "Timeout", "Cancel"])
        lex.expect_eol()
        return args

    def execute_click(o):
        options = []
        previews = {}
        layers = {}
        for layer, (value, system) in sorted(store.rscript_click_values.items(),
                key=lambda item: (store.layer_zorder.get(item[0], item[0] * 2), item[0])):
            if not store.layer_enabled.get(layer, 1):
                continue
            if layer not in store.layer_info:
                continue
            link = store.rscript_click_links.get(layer)
            if link is None and not store.rscript_click_link_is_preview:
                continue
            if store.rscript_click_link_is_preview:
                x, y = store.layer_pos.get(layer, (0, 0))
                hover = None
            else:
                hover, x, y = link
            folder = store.folder.get(layer, store.folder.get(0))
            if not folder:
                continue
            if store.rscript_click_grid and not store.rscript_click_link_is_preview:
                x *= store.layer_x_grid
                y *= store.layer_y_grid
            idle = store.layer_info[layer]
            hover_image = "%s %04d" % (folder, hover) if hover is not None else idle
            if store.rscript_click_native_effects:
                mode = store.rscript_click_modes.get(layer, 0)
                # Native 405cb0: invert, wash toward white (LUT row 64), or omit the body.
                if mode == 1:
                    hover_image = Transform(idle, matrixcolor=InvertMatrix(1.0))
                elif mode == 2:
                    hover_image = Transform(idle, matrixcolor=Matrix([
                        .75, 0, 0, 64 / 255., 0, .75, 0, 64 / 255.,
                        0, 0, .75, 64 / 255., 0, 0, 0, 1]))
                elif mode == 3:
                    hover_image = Transform(idle, alpha=0.0)
            # Native optional setlink artwork may be absent (not only -1).
            # Missing idle artwork stays blank under the shared image policy.
            options.append((value, system, idle,
                            hover_image if not isinstance(hover_image, str) or renpy.has_image(hover_image, exact=True) else idle,
                            absolute(x), absolute(y)))
            layers[len(options) - 1] = layer
            preview = (link if store.rscript_click_link_is_preview else
                       store.rscript_click_previews.get(layer))
            if preview is not None:
                cg, px, py = preview
                if store.rscript_click_grid:
                    px *= store.layer_x_grid
                    py *= store.layer_y_grid
                image = "%s %04d" % (folder, cg)
                if renpy.has_image(image, exact=True):
                    previews[len(options) - 1] = (image, px, py)
        if not options:
            raise Exception("RScript click has no active image regions")
        countdown = rscript_click_countdown(o)
        try:
            store._r[0] = renpy.call_screen("rscript_click_screen", options=options,
                                           previews=previews, layers=layers,
                                           countdown=countdown,
                                           cancel=bool(o.Cancel) if o is not None else False)
        finally:
            if countdown is not None:
                store._r[countdown["register"]] = rscript_click_remaining(countdown) & 65535
            for layer in layers.values():
                rscript_click_focus(layer)
        if store.rscript_click_autoreset:
            execute_resetclk(None)

    def rscript_click_countdown(o):
        if o is None or not o.Timer or not store.rscript_click_timer_unit:
            return None
        import time
        initial = rscript_signed16(store._r[o.Timer])
        args = RScriptArguments(Layer=0, Value=initial, Animate=0)
        # Native click's second operand retains num0's existing range when set.
        if not o.Timeout:
            rscript_number_apply("numreng", RScriptArguments(
                Layer=0, Minimum=0, Maximum=initial, Mode=4, Digits=0))
        rscript_number_apply("num", args)
        return {"register": o.Timer, "initial": initial, "started": time.monotonic(),
                "unit": store.rscript_click_timer_unit}

    def rscript_click_remaining(countdown):
        import time
        return countdown["initial"] - int((time.monotonic() - countdown["started"]) / countdown["unit"])

    def rscript_click_tick(countdown):
        remaining = rscript_click_remaining(countdown)
        rscript_number_apply("num", RScriptArguments(Layer=0, Value=max(0, remaining), Animate=0))
        if remaining < 0:
            # Native 4109b5: expiration selects r0=0, not the cancel action.
            renpy.end_interaction(0)

    def rscript_click_focus(layer, image=None, preview=None):
        # Input lives on screens; native artwork stays in the master scene.
        # Re-showing the same tag retains its transforms/position and depth.
        tag = "layer%d" % layer
        scene = renpy.game.context().scene_lists
        depth = dict(scene.get_zorder_list(IMAGE_LAYER)).get(tag,
                    store.layer_zorder.get(layer, layer * 2))
        if ((not store.rscript_click_link_is_preview or store.rscript_click_native_effects) and layer in store.layer_info
                and scene.get_displayable_by_tag(IMAGE_LAYER, tag) is not None):
            renpy.show(tag, what=renpy.displayable(image or store.layer_info[layer]),
                       layer=IMAGE_LAYER, zorder=depth)
        renpy.hide("rscript_click_preview", layer=IMAGE_LAYER)
        if preview is not None and store.layer_enabled.get(layer, 1):
            image, x, y = preview
            renpy.show("rscript_click_preview", what=renpy.displayable(image),
                       layer=IMAGE_LAYER, zorder=depth + 1,
                       at_list=[Transform(pos=(absolute(x), absolute(y)), anchor=(0.0, 0.0))])

    renpy.register_statement("_click", parse = parse_click, execute = execute_click, lint = lint_undef)



    def parse_resetclk(lex):
        args = rscript_arguments(lex, ["Layer"])
        lex.expect_eol()
        return args

    def execute_resetclk(o):
        # None is an internal full reset; the script command targets one layer.
        # Native resetclk 0 is a no-op, not a request to clear all regions.
        layer = None if o is None else o.Layer
        for bindings in (store.rscript_click_values, store.rscript_click_links,
                         store.rscript_click_previews, store.rscript_click_modes):
            if layer is None:
                bindings.clear()
            elif layer != 0:
                bindings.pop(layer, None)

    renpy.register_statement("_resetclk", parse = parse_resetclk, execute = execute_resetclk, lint = lint_undef)



    def parse_setclk(lex):
        args = rscript_arguments(lex, ["Layer", "Value", "Mode", "Unknown"])
        lex.expect_eol()
        return args

    def execute_setclk(o):
        store.rscript_click_values[o.Layer] = (o.Value, False)
        store.rscript_click_modes[o.Layer] = getattr(o, "Mode", 0)

    renpy.register_statement("_setclk", parse = parse_setclk, execute = execute_setclk, lint = lint_undef)



    def parse_setclksub(lex):
        return (lex.rest(),)

    def execute_setclksub(o):
        pass

    renpy.register_statement("_setclksub", parse = parse_setclksub, execute = execute_setclksub, lint = lint_undef)



    def parse_setclksys(lex):
        return parse_setclk(lex)

    def execute_setclksys(o):
        store.rscript_click_values[o.Layer] = (o.Value, True)
        store.rscript_click_modes[o.Layer] = getattr(o, "Mode", 0)

    renpy.register_statement("_setclksys", parse = parse_setclksys, execute = execute_setclksys, lint = lint_undef)



    def parse_setlink(lex):
        args = rscript_arguments(lex, ["Layer", "HoverCG", "xLoc", "yLoc", "Slot"])
        lex.expect_eol()
        return args

    def execute_setlink(o):
        # Slot 1 is an independent hover information card, not the icon/hit region.
        if o.Slot == 0:
            links = store.rscript_click_links
        elif o.Slot == 1:
            links = store.rscript_click_previews
        else:
            raise Exception("RScript setlink slot %s is not implemented" % o.Slot)
        if o.Slot == 1 and o.HoverCG in (-1, 0xffff):
            links.pop(o.Layer, None)
        else:
            links[o.Layer] = (o.HoverCG, o.xLoc, o.yLoc)

    renpy.register_statement("_setlink", parse = parse_setlink, execute = execute_setlink, lint = lint_undef)

    def register_rscript_ui_aliases(prefix):
        # Keep generated scripts and existing saves using the old names valid.
        for name in ("folder", "setclk", "setclksys", "setlink", "resetclk", "click", "autoreset"):
            renpy.register_statement("_" + prefix + "_" + name,
                parse=globals()["parse_" + name],
                execute=globals()["execute_" + name], lint=lint_undef)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
