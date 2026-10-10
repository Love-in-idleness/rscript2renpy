default kagerou_page = ""
default kagerou_text_clear_mode = 0
default kagerou_scene_replay = False
default kagerou_choice_prompt = None

python early:
    def kagerou_parse_words(lex):
        return rscript_arguments(lex, ["Mode", "Slot", "CG", "KeepFocus", "Unused"])

    def kagerou_excmd(args):
        from engine.kagerou_native import excmd_calls
        values = tuple(int(getattr(args, name)) & 65535
                       for name in ("Mode", "Slot", "CG", "KeepFocus", "Unused"))
        calls = excmd_calls(values, x=store.kagerou_character_x.get(values[1]),
                            inactive_style=False, queued=store.in_queue)
        for call in calls:
            address = call[0]
            if address == "register":
                store._r[call[1]] = call[2]
            elif address == 0x41dda0:
                _, layer, cg, effect, x, y, color = call
                loadcls(layer, effect, cg=cg, xpos=x, ypos=y, color=color)
            elif address == 0x41e020:
                layer = call[1]
                if layer == 0:
                    # EXCMD clear(0) is one layer; shared cls(0) clears all objects.
                    store.layer_info.pop(0, None)
                    store.layer_pos.pop(0, None)
                    queue_draw(renpy.hide, "layer0", layer=IMAGE_LAYER)
                elif layer < 100:
                    loadcls(layer, 0, clear=True)
            elif address == 0x41f940:
                execute_depth(RScriptArguments(Layer=call[1], Depth=call[2]))
            elif address == 0x41f7f0:
                # shortcut: mode 4's pixel algorithm is unverified; keep normal pixels
                # until 408ea6 -> internal mode 3 has been independently reconstructed.
                execute_draw(RScriptArguments(Layer=call[1], Mode=0, Level=0))
            elif address == 0x41dd30:
                process_draw_queue()

    def kagerou_clear_page():
        store.kagerou_page = ""
        store.last_say = None
        store.last_spk = None
        renpy.hide_screen("say")

    def kagerou_txcls(value):
        # 41ecd0 -> 41e590 -> 42d9d0, followed by queue-conditional refresh.
        queue_draw(kagerou_clear_page)
        process_draw_queue()

    def kagerou_tclsmode(value):
        store.kagerou_text_clear_mode = int(eval(value)) & 65535

    def kagerou_text(body, wait, append=False):
        parsed, center = parse_rscript_text(repr(body), True)
        previous = "" if not append and store.kagerou_text_clear_mode == 1 else store.kagerou_page
        separator = ""
        if previous and wait and not append:
            # 42d81a appends ^n; 42d86c adds U+3000,^n before a 【 speaker line.
            separator = "\n" + ("\u3000\n" if body.startswith("【") else "")
        combined = previous + ("{fast}" if previous else "") + separator + parsed
        # 42d8d1: append; on failed append, clear and retry the current paragraph.
        sample = RScriptText(combined, size=persistent.rscript_text_size,
                             font=rscript_current_font(), slow_cps=0)
        sample.refresh_settings()
        height = renpy.text.text.Layout(sample, 646, 480, {}, size_only=True,
                                       drawable_res=False).size[1]
        if previous and height > 480:
            combined = parsed
        store.kagerou_page = combined
        execute_say((None, None, repr(combined)), interact=bool(wait))

    def kagerou_say(value):
        ignored_name, body, wait = eval(value)
        # 41c9ae discards the first string; the visible name is already in body.
        kagerou_text(body, wait)

    def kagerou_append(value):
        body, wait = eval(value)
        kagerou_text(body, wait, append=True)

    def kagerou_tbox(args):
        execute_tbox(args)
        process_draw_queue()

    def kagerou_locmode(args):
        # 41f890/41e310 accept four operands; scripts use origin modes 0 or 1.
        layer, x, y = args.Layer, args.X, args.Y
        for selected in (range(1, 100) if layer == 0 else [layer]):
            store.layer_anchor[selected] = (0.0 if x == 0 else 0.5,
                                             0.0 if y == 0 else 0.5)

    def kagerou_parse_locmode(lex):
        return rscript_arguments(lex, ["Layer", "X", "Y", "Mode"])

    def kagerou_endscene(value):
        # 41cb25 tests replay WORD 4821f8; normal play falls through.
        if store.kagerou_scene_replay:
            renpy.return_statement()

    renpy.register_statement("_kagerou_excmd", parse=kagerou_parse_words, execute=kagerou_excmd)
    renpy.register_statement("_kagerou_say", parse=parse_rscript_expression, execute=kagerou_say)
    renpy.register_statement("_kagerou_append", parse=parse_rscript_expression, execute=kagerou_append)
    renpy.register_statement("_kagerou_txcls", parse=parse_rscript_expression, execute=kagerou_txcls)
    renpy.register_statement("_kagerou_tclsmode", parse=parse_rscript_expression, execute=kagerou_tclsmode)
    renpy.register_statement("_kagerou_tbox", parse=parse_tbox, execute=kagerou_tbox)
    renpy.register_statement("_kagerou_locmode", parse=kagerou_parse_locmode, execute=kagerou_locmode)
    renpy.register_statement("_kagerou_endscene", parse=parse_rscript_expression, execute=kagerou_endscene)
    register_rscript_ui_aliases("kagerou")

screen say(who, what, center=False):
    window:
        id "window"
        pos (0, 0)
        xysize (800, 600)
        padding (0, 0)
        background rscript_textbox_background()
        rscript_text what:
            id "what"
            pos (114, 30)
            font rscript_current_font()
            size persistent.rscript_text_size
            color "#ffffff"
            slow_cps persistent.rscript_text_cps
            line_spacing persistent.rscript_line_spacing

screen choice(items):
    use rscript_choice(items, kagerou_choice_prompt)
