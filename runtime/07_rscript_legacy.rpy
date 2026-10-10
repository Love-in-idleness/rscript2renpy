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

    def rscript_number_frames(previous, target):
        # 42d450: signed difference / 5, truncated toward zero, at least one.
        frames = [previous]
        while previous != target:
            distance = target - previous
            previous += (1 if distance > 0 else -1) * max(1, abs(distance) // 5)
            frames.append(previous)
        return tuple(frames)

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
        if state.get("Enabled", False):
            frames = (rscript_number_frames(previous, state["Value"])
                      if command == "num" and args.Animate and
                      (state.get("Number", 0) or state.get("Bar", 0)) else ())
            rscript_number_show(args.Layer, state, frames)
            if len(frames) > 1:
                # 42b800/42b920: the native visual update timer is 50 ms.
                queue_ef_pause((len(frames) - 1) * .05)
                # A click/Skip can end the wait early; never leave a stale value.
                queue_draw_delayed(rscript_number_show, args.Layer, state)
        else:
            renpy.hide("rscript_number_%d" % args.Layer, layer=IMAGE_LAYER)

    def rscript_number_show(layer, state, frames=()):
        image = (DynamicDisplayable(rscript_number_animation, state, frames)
                 if frames else rscript_number_displayable(state))
        renpy.show("rscript_number_%d" % layer, what=image,
                   layer=IMAGE_LAYER, zorder=100,
                   at_list=[Transform(pos=(absolute(state.get("X", 0)), absolute(state.get("Y", 0))))])

    def rscript_number_animation(st, at, state, frames):
        frame = min(len(frames) - 1, int(st / .05 + 1e-9))
        visible = dict(state, Value=frames[frame])
        return rscript_number_displayable(visible), (.05 if frame < len(frames) - 1 else None)

    def rscript_number_displayable(state):
        artwork = []
        background = state.get("Background", 0)
        background_path = rscript_image_path("grps/Fix%02d.png" % background)
        if background and renpy.loadable(background_path):
            artwork.append(renpy.displayable(background_path))
        number = state.get("Number", 0)
        path = rscript_image_path("grps/Num%02d.png" % number)
        if number and renpy.loadable(path):
            width, height = renpy.image_size(path)
            # 42d0b0/428160: ten vertically stacked frames, eight digit slots.
            height //= 10
            if height:
                value = max(0, state.get("Value", 0))
                digits = str(value)[-8:]
                for index, digit in enumerate(digits):
                    artwork.append(Transform(path, crop=(0, int(digit) * height, width, height),
                        pos=(absolute(state.get("X1", 0) + (8 - len(digits) + index) * width),
                             absolute(state.get("Y1", 0)))))
        bar = state.get("Bar", 0)
        path = rscript_image_path("grps/BAR%02d.png" % bar)
        if bar and renpy.loadable(path):
            width, height = renpy.image_size(path)
            minimum, maximum = state.get("Minimum", 0), state.get("Maximum", 1)
            fraction = max(0.0, min(1.0, (state.get("Value", minimum) - minimum) / float(max(1, maximum - minimum))))
            artwork.append(Transform(path, crop=(0, 0, int(width * fraction), height),
                                     pos=(absolute(state.get("X2", 0)), absolute(state.get("Y2", 0)))))
        return Fixed(*artwork)

    def execute_rscript_number(value):
        command, args = value
        queue_draw(rscript_number_apply, command, args.resolved())

    renpy.register_statement("_rscript_number", parse=parse_rscript_number,
                             execute=execute_rscript_number)
