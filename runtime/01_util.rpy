python early:

    def bgi_parse_arguments(lex):

        from collections import OrderedDict

        args = []
        kwargs = OrderedDict()

        while True:
            if lex.eol():
                break

            arg = lex.match(r"""(?ux)
        ([0-9A-Za-z][\w\_\-\#\uff08\uff09\/\\]*:)?("(?:[^"\\]|\\.)*")|                   # Quoted parameters
        ([A-Za-z][\w\_\-\#\uff08\uff09\/\\]*:)?([\w\_\-\#\uff08\uff09\）\/\\\？\！\　\。\…\・\、\「\」]+)| # Regular parameters
        ([\<\>\^\_]@?[\w\_\-\#\uff08\uff09\/\\]+)+                                       # the bullshit movement params for bustshot
        """)

            if arg is None:
                break

            if ":" in arg:
                name, val = arg.split(":", 1)
                kwargs[name] = val

            else:
                args.append(arg)

        return args, kwargs



    def is_num(s):
        try:
            if "_" in s:
                return False

            int(s)
            return True
        except ValueError:
            return False



    class RScriptArguments(dict):
        def __getattr__(self, name):
            if name in self:
                if isinstance(self[name], (int, float)):
                    return self[name]

                if is_num(self[name]):
                    return int(self[name], 10)
                else:
                    try:
                        return eval(self[name])
                    except:
                        return self[name]
            else:
                raise AttributeError("RScript argument %s not defined." % name)
                return 0

        def __setattr__(self, name, value):
            self[name] = value

        def __delattr__(self, name):
            if name in self:
                del self[name]
            else:
                raise AttributeError("RScript argument %s not defined." % name)

    def rscript_arguments(lex, names = []):
        args = RScriptArguments()
        items = lex.rest().split()

        for i, name in enumerate(names):
            args[name] = items[i] if i < len(items) else "0"

        return args

    # The port template can replace these hooks; a bare runtime remains usable.
    def rscript_prepare_text(text):
        return renpy.translation.translate_string(text)

    def rscript_green_color():
        return getattr(store, "rscript_text_colors", {}).get("g", "#D7FFB3")

    def rscript_dialogue_begin(append=False):
        pass

    def rscript_dialogue_end():
        pass

    def rscript_text_palette():
        colors = {
            "y": "#FFDE00", "g": rscript_green_color(),
            "w": "#FFFFFF", "k": "#000000",
            "r": "#B73333", "b": "#2020FF", "s": "#79F1F2",
            "p": "#F8B1EF", "v": "#C187F6", "o": "#FAA25A",
        }
        colors.update(getattr(store, "rscript_text_colors", {}))
        colors["g"] = rscript_green_color()
        return colors

    def rscript_style_controls(text, color_controls):
        # Close/reopen the active native tags on a change, avoiding crossed
        # font/color/bold spans. Every say/append/object/menu uses this parser.
        colors = rscript_text_palette()
        active = {}
        output = []
        end = 0
        for match in renpy.re.finditer(
                r"\^([bi])|\^f([mg])|\^c([bgkopsrvwy])|\^s([0-9])|\^d([0-9]+)|([<>])", text):
            output.append(text[end:match.start()])
            output.extend("{/%s}" % tag for tag in reversed(active))
            toggle, face, color, size, speed, boundary = match.groups()
            if toggle:
                if toggle in active:
                    del active[toggle]
                else:
                    active[toggle] = "{%s}" % toggle
            elif face:
                font = getattr(store, "rscript_text_fonts", {}).get(face, gui.text_font)
                if not renpy.loadable(font):
                    font = gui.text_font
                active["font"] = "{font=%s}" % font
            elif color and color_controls:
                active["color"] = "{color=%s}" % colors[color]
            elif size is not None:
                delta = (int(size) - 1) * 10
                if delta:
                    active["size"] = "{size=%+d}" % delta
                else:
                    active.pop("size", None)
            elif speed is not None:
                speed = int(speed)
                if speed == 1:
                    active.pop("cps", None)
                else:
                    active["cps"] = "{cps=%s}" % ("0" if speed == 0 else "*%0.2f" % (1.0 / speed))
            elif boundary:
                active.pop("cps", None)
            output.extend(active.values())
            if boundary:
                output.append(boundary)
            end = match.end()
        output.append(text[end:])
        output.extend("{/%s}" % tag for tag in reversed(active))
        return "".join(output)



    def parse_rscript_text(text, color_controls = False):

        if not text:
            return text

        text = eval(text)
        # Both switch tables in Khime accept upper/lowercase controls.
        text = renpy.re.sub(
            r"\^(?:[ag][0-9]{3}|[cf][a-z]|[binm]|[dw][0-9]+|s[0-9]|v[-0-9]+)",
            lambda match: match.group().lower(), text, flags=renpy.re.I)
        text = rscript_prepare_text(text)
        # Shared by say, append, text objects and choices, not just modern TXT.
        text = renpy.re.sub(r"\|([^\[\]|]+)\[([^\[\]]+)\]",
                            lambda m: "{rb}%s{/rb}{rt}%s{/rt}" % m.groups(), text)

        no_wait = text.endswith(("<", ">"))
        if text.endswith("<"):
            text = text[:-1]
        text = renpy.re.sub(r"\^w(\d+)", lambda m: "{w=%f}" % (int(m.group(1)) / 10.), text)
        text = rscript_style_controls(text, color_controls)
        text = renpy.re.sub(r"\^v([-0-9]+)",
                           lambda match: "".join(chr(ord(ch) + 0xfee0)
                                                for ch in match.group(1)), text)


        if no_wait:
            text += "{nw}"

        text = text.replace(">", "{w}")

        text = text.replace("[",  "[[")
        text = text.replace("\\{", "{{")
        text = text.replace("\\n", "\n")
        text = text.replace("^n", "\n")
        text = text.replace("/'", "'")
        text, center = renpy.re.subn(r"\^m", "", text)
        center = bool(center)

        return text, center



    def rscript_label(name):

        sub = None
        if "%" in name:
            name, sub = name.split("%")


        try:
            name = "%04d" % int(name, 10)
        except:
            name = "%04d" % eval(name)

        if sub:
            label = "_g_%s_%s" % (name, sub)

            if not renpy.has_label(label):
                label = "_%s" % name

        else:
            label = "_%s" % name

        return label



    def rscript_label_local(script, name):
        local_scope = [script] + list(_includes)

        for l in local_scope:
            label = "_%s_%s" % (l, name)

            if renpy.has_label(label):
                return label

        return "_%s_%s" % (script, name)



    def rscript_post_label(func, fn, name, count):
        label = "_rscript_{}_{}_{}_{:02d}".format(func, fn, name, count)








        return label



    def current_script():
        filename, _ = renpy.get_filename_line()
        return os.path.basename(os.path.splitext(filename)[0])

    def rscript_filename(lex):
        fn = os.path.splitext(lex.filename)[0]
        fn = fn.replace("/", "_")
        fn = fn.replace("\\", "_")
        return fn



    def hide_window(trans = None):
        if not store._window:
            return

        store._window = False
        if trans:
            renpy.with_statement(trans)

    def show_window(trans = None):
        if store._window:
            return

        store._window = True
        if trans:
            renpy.with_statement(trans)



    def queue_draw(fn, *args, **kwargs):
        store.draw_queue.append((fn, args, kwargs))

    def queue_draw_first(fn, *args, **kwargs):
        store.draw_queue.insert(0, (fn, args, kwargs))

    def queue_draw_delayed(fn, *args, **kwargs):
        store.draw_queue_delayed.append((fn, args, kwargs))

    def queue_draw_extra_delayed(fn, *args, **kwargs):
        store.draw_queue_extra_delayed.append((fn, args, kwargs))

    def unqueue(remove_fn):
        to_delete = []
        for i, (fn, args, kwargs) in enumerate(store.draw_queue):
            if fn == remove_fn:
                to_delete.append(i)
                print("unqueueing", fn)

        for i in sorted(to_delete, reverse = True):
            del store.draw_queue[i]

        to_delete = []
        for i, (fn, args, kwargs) in enumerate(store.draw_queue_delayed):
            if fn == remove_fn:
                to_delete.append(i)
                print("unqueueing", fn)

        for i in sorted(to_delete, reverse = True):
            del store.draw_queue_delayed[i]


    def process_draw_queue():



        if store.in_queue:
            return

        if store.processing_queue:
            return

        store.processing_queue = True






        while store.draw_queue:
            fn, args, kwargs = store.draw_queue.pop(0)
            fn(*args, **kwargs)

        while store.draw_queue_delayed:
            fn, args, kwargs = store.draw_queue_delayed.pop(0)
            fn(*args, **kwargs)

        while store.draw_queue_extra_delayed:
            fn, args, kwargs = store.draw_queue_extra_delayed.pop(0)
            fn(*args, **kwargs)

        store.processing_queue = False

        store.draw_queue = []
        store.draw_queue_delayed = []
        store.draw_queue_extra_delayed = []









    def queue_ef_pause(dur):
        queue_draw(_queue_ef_pause, dur)
        queue_draw_delayed(_execute_ef_pause)

    def _queue_ef_pause(dur):
        store.effect_pause = max(store.effect_pause, dur)

    def _execute_ef_pause():
        if store.effect_pause > 0:
            renpy.pause(store.effect_pause)

        store.effect_pause = 0



    def get_showing_image(tag, layer):
        attrs = renpy.get_attributes(tag, layer)
        if attrs:
            attrs = " ".join(attrs)

        return attrs



    def reshow_scene():
        layers = [
      BG_LAYER,
      BUST_LAYER,
    ]

        for l in layers:
            for tag in renpy.get_showing_tags(l, sort = True):
                attrs = get_showing_image(tag, l)
                img = "%s %s" % (l, attrs)
                renpy.show(img, layer = l, tag = tag)




    def convert_bust_x(x):
        return x + (config.screen_width / 2)

    def convert_bust_y(y):
        return y + (config.screen_height)

    def convert_bg_coords(x, y):
        x = x + (config.screen_width / 2)
        y = y + (config.screen_height / 2)

        return x, y



    def find_audio(name):
        audio_dirs = [
      SE_DIR,
      BGM_DIR,
      VOICE_DIR,
    ]

        for dir in audio_dirs:
            fn = "%s/%s.ogg" % (dir, name)

            if renpy.loadable(fn):
                return fn

        return None



    def wait_audio(channel, hard = False):

        duration = renpy.music.get_duration(channel)
        cur_pos  = renpy.music.get_pos(channel)

        if not duration is None and not cur_pos is None:
            renpy.pause(duration - cur_pos, hard = hard)
            renpy.music.stop(channel)



    VOICE_TAGS = {
  }

    def get_voice_tag(who):
        return VOICE_TAGS.get(who, OTHER_TAG)



default processing_queue = False
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
