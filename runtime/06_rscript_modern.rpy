# Shared modern CodeX instructions. Khime keeps its legacy statement aliases.
default rscript_choice_prompt = None
default rscript_dynamic_answers = []
default rscript_dynamic_next = None
default rscript_dynamic_skin = None

python early:
    def parse_rscript_expression(lex):
        value = lex.rest()
        lex.expect_eol()
        return value

    def execute_rscript_say(value):
        name, body, wait = eval(value)
        execute_say((None, repr(name) if name else None,
                     repr(body)), interact=bool(wait))

    def execute_rscript_append(value):
        body, wait = eval(value)
        execute_append((None, repr(body)), interact=bool(wait))

    def parse_flagset(lex):
        args = rscript_arguments(lex, ["First", "Last", "Value"])
        lex.expect_eol()
        return args

    def execute_flagset(args):
        # startup_jp.exe 0x43d960: inclusive range, bounded to 0..9999.
        first, last, value = args.First, args.Last, args.Value
        if 0 <= first <= last:
            for key in range(first, min(last, 9999) + 1):
                store._r[key] = value

    def execute_dynsel(value):
        prompt, append = eval(value)
        if not append:
            store.rscript_dynamic_answers.clear()
            store.rscript_dynamic_next = None
        store.rscript_choice_prompt = prompt

    def execute_dynans(value):
        # 0x43d550 -> 0x4099a9: third operand is a register key, not its value.
        caption, result, flag, inverted = eval(value)
        # 43d559: the native answer table has 100 entries.
        if len(store.rscript_dynamic_answers) < 100:
            store.rscript_dynamic_answers.append((caption, result, flag, inverted))

    def execute_dynnext(value):
        store.rscript_dynamic_next = eval(value)

    def parse_dyndo(lex):
        args = rscript_arguments(lex, ["Effect", "Layout", "Mode"])
        lex.expect_eol()
        return args

    def execute_dyndo(args):
        options = [(caption, result) for caption, result, flag, inverted
                   in store.rscript_dynamic_answers
                   if not flag or bool(store._r[flag]) == bool(inverted)]
        # 409750: up to five answers, otherwise four + next, wrapping at the end.
        next_page = ("rscript_dynamic_next",)
        page = 0
        store.rscript_dynamic_skin = args.Layout
        try:
            while options:
                visible = options if len(options) <= 5 else options[page:page + 4] + [
                    (store.rscript_dynamic_next or "次へ", next_page)]
                result = renpy.display_menu(visible)
                if result != next_page:
                    store._r[0] = result
                    break
                page = page + 4 if page + 4 < len(options) else 0
            else:
                store._r[0] = 0
        finally:
            store.rscript_dynamic_skin = None
            store.rscript_choice_prompt = None

    def parse_rscript_locmode(lex):
        args = rscript_arguments(lex, ["Layer", "XMode", "YMode", "Mode"])
        lex.expect_eol()
        return args

    def execute_rscript_locmode(args):
        anchor = (0.0 if args.XMode == 0 else 0.5,
                  0.0 if args.YMode == 0 else 0.5)
        for layer in (range(100) if args.Layer == 0 else (args.Layer,)):
            store.layer_anchor[layer] = anchor

    renpy.register_statement("_rscript_say", parse=parse_rscript_expression,
                             execute=execute_rscript_say)
    renpy.register_statement("_rscript_append", parse=parse_rscript_expression,
                             execute=execute_rscript_append)
    renpy.register_statement("_rscript_locmode", parse=parse_rscript_locmode,
                             execute=execute_rscript_locmode)
    renpy.register_statement("_flagset", parse=parse_flagset, execute=execute_flagset)
    renpy.register_statement("_dynsel", parse=parse_rscript_expression, execute=execute_dynsel)
    renpy.register_statement("_dynans", parse=parse_rscript_expression, execute=execute_dynans)
    renpy.register_statement("_dynnext", parse=parse_rscript_expression, execute=execute_dynnext)
    renpy.register_statement("_dyndo", parse=parse_dyndo, execute=execute_dyndo)
    register_rscript_ui_aliases("rscript")
