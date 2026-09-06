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

        renpy.call(rscript_label_local(script, name))

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
        return (lex.rest(),)

    def execute_autoreset(o):
        pass

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
        return (lex.rest(),)

    def execute_click(o):
        pass

    renpy.register_statement("_click", parse = parse_click, execute = execute_click, lint = lint_undef)



    def parse_resetclk(lex):
        return (lex.rest(),)

    def execute_resetclk(o):
        pass

    renpy.register_statement("_resetclk", parse = parse_resetclk, execute = execute_resetclk, lint = lint_undef)



    def parse_setclk(lex):
        return (lex.rest(),)

    def execute_setclk(o):
        pass

    renpy.register_statement("_setclk", parse = parse_setclk, execute = execute_setclk, lint = lint_undef)



    def parse_setclksub(lex):
        return (lex.rest(),)

    def execute_setclksub(o):
        pass

    renpy.register_statement("_setclksub", parse = parse_setclksub, execute = execute_setclksub, lint = lint_undef)



    def parse_setclksys(lex):
        return (lex.rest(),)

    def execute_setclksys(o):
        pass

    renpy.register_statement("_setclksys", parse = parse_setclksys, execute = execute_setclksys, lint = lint_undef)



    def parse_setlink(lex):
        return (lex.rest(),)

    def execute_setlink(o):
        pass

    renpy.register_statement("_setlink", parse = parse_setlink, execute = execute_setlink, lint = lint_undef)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
