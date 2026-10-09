# Older CodeX numeric widgets. State and range semantics are shared; skins are not.
default rscript_numbers = {}
default rscript_vm_temps = {}

python early:
    def rscript_muldev(left, right, divisor):
        # Cannonball.exe 0x417f40: signed 16-bit inputs and truncation toward zero.
        signed = lambda value: ((value + 32768) & 65535) - 32768
        numerator = signed(left) * signed(right)
        divisor = signed(divisor)
        quotient = abs(numerator) // abs(divisor)
        return signed(-quotient if (numerator < 0) != (divisor < 0) else quotient)

    def parse_rscript_number(lex):
        fields = {
            "numload": ["Layer", "Background", "First", "Second"],
            "numreng": ["Layer", "Minimum", "Maximum", "Mode", "Digits"],
            "numenable": ["Layer", "Enabled"],
            "numloc": ["Layer", "X", "Y"],
            "numset": ["Layer", "X1", "Y1", "X2", "Y2"],
            "num": ["Layer", "Value", "Animate"],
        }
        command = lex.match(r"\w+")
        args = rscript_arguments(lex, fields[command])
        lex.expect_eol()
        return command, args

    def rscript_number_apply(command, args):
        state = dict(store.rscript_numbers.get(args.Layer, {}))
        previous = state.get("Value", state.get("Minimum", 0))
        state.update({key: getattr(args, key) for key in args if key != "Layer"})
        if command == "numreng":
            state["Value"] = max(0, args.Minimum)
        if command == "num":
            minimum, maximum = state.get("Minimum", 0), state.get("Maximum", 32767)
            # 0x42d3b0: values below the minimum leave the previous value intact.
            state["Value"] = min(args.Value, maximum) if args.Value >= minimum else previous
        store.rscript_numbers[args.Layer] = state
        tag = "rscript_number_%d" % args.Layer
        if state.get("Enabled", False):
            # shortcut: native NumNN skins/animated counters are not decoded;
            # use readable values until those widget resources are reconstructed.
            renpy.show(tag, what=Text(str(state.get("Value", 0)), size=24, color="#ffffff"),
                       layer=IMAGE_LAYER, zorder=100,
                       at_list=[Transform(pos=(state.get("X", 0), state.get("Y", 0)))])
        else:
            renpy.hide(tag, layer=IMAGE_LAYER)

    def execute_rscript_number(value):
        command, args = value
        queue_draw(rscript_number_apply, command, args.resolved())

    renpy.register_statement("_rscript_number", parse=parse_rscript_number,
                             execute=execute_rscript_number)
