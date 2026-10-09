# Older CodeX word arithmetic and numeric widgets.
default rscript_numbers = {}
default rscript_vm_temps = {}

python early:
    def rscript_signed16(value):
        return ((value + 32768) & 65535) - 32768

    def rscript_div16(left, right, remainder=False):
        left, right = rscript_signed16(left), rscript_signed16(right)
        quotient = abs(left) // abs(right)
        if (left < 0) != (right < 0):
            quotient = -quotient
        return left - quotient * right if remainder else quotient

    def rscript_muldev(left, right, divisor):
        # Cannonball.exe 0x417f40: signed 16-bit inputs and truncation toward zero.
        numerator = rscript_signed16(left) * rscript_signed16(right)
        divisor = rscript_signed16(divisor)
        quotient = abs(numerator) // abs(divisor)
        return rscript_signed16(-quotient if (numerator < 0) != (divisor < 0) else quotient)

    def parse_rscript_number(lex):
        fields = {
            "numload": ["Layer", "Number", "Bar", "Background"],
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
            renpy.show(tag, what=rscript_number_displayable(state),
                       layer=IMAGE_LAYER, zorder=100,
                       at_list=[Transform(pos=(absolute(state.get("X", 0)), absolute(state.get("Y", 0))))])
        else:
            renpy.hide(tag, layer=IMAGE_LAYER)

    def rscript_number_displayable(state):
        artwork = []
        background = state.get("Background", 0)
        if background:
            artwork.append(renpy.displayable(rscript_image_path("grps/Fix%02d.png" % background)))
        bar = state.get("Bar", 0)
        if bar:
            path = rscript_image_path("grps/BAR%02d.png" % bar)
            width, height = renpy.image_size(path)
            minimum, maximum = state.get("Minimum", 0), state.get("Maximum", 1)
            fraction = max(0.0, min(1.0, (state.get("Value", minimum) - minimum) / float(max(1, maximum - minimum))))
            artwork.append(Transform(path, crop=(0, 0, int(width * fraction), height),
                                     pos=(absolute(state.get("X2", 0)), absolute(state.get("Y2", 0)))))
        if state.get("Number", 0) or not artwork:
            # shortcut: Num digit atlases/counting animation need native reconstruction;
            # retain readable digits until a game provides those resources.
            artwork.append(Transform(Text(str(state.get("Value", 0)), size=24, color="#ffffff"),
                                     pos=(absolute(state.get("X1", 0)), absolute(state.get("Y1", 0)))))
        return Fixed(*artwork)

    def execute_rscript_number(value):
        command, args = value
        queue_draw(rscript_number_apply, command, args.resolved())

    renpy.register_statement("_rscript_number", parse=parse_rscript_number,
                             execute=execute_rscript_number)
