default kagerou_page = ""
default kagerou_page_old = ""
default kagerou_page_current = ""
default kagerou_text_clear_mode = 0
default kagerou_scene_replay = False
default kagerou_choice_prompt = None

python early:
    def kagerou_apply_text_settings():
        from engine.kagerou_native import text_geometry
        geometry = text_geometry(persistent.kagerou_direction, persistent.kagerou_size,
                                 persistent.kagerou_snap)
        # Keep the chosen font size when rotating; native rectangle presets still apply.
        geometry["size"] = text_geometry(1, persistent.kagerou_size,
                                         persistent.kagerou_snap)["size"]
        persistent.rscript_text_size = geometry["size"]
        store.rscript_base_text_size = geometry["size"]
        persistent.rscript_say_line_chars = 1000  # The audited pixel rectangle is the limit.
        persistent.rscript_line_spacing = geometry["pitch"][0]
        geometry["outlines"] = ((1, "#000000", 1, 1),) if persistent.kagerou_shadow == 0 else ()
        rscript_set_textbox(0, box_pos=(0, 0), **geometry)

    def kagerou_set_text_setting(name, value):
        setattr(persistent, "kagerou_" + name, value)
        kagerou_apply_text_settings()
        positions = store.kagerou_character_layouts[persistent.kagerou_character_focus][persistent.kagerou_snap]
        for layer in range(1, 8):
            if layer in store.layer_info and layer in store.layer_pos:
                execute_move(RScriptArguments(Layer=layer, xLoc=positions[layer], yLoc=0,
                                             Effect=0, Speed=0))
        process_draw_queue()
        renpy.save_persistent()

    def kagerou_page_text():
        previous = store.kagerou_page_old
        if previous and persistent.kagerou_text_focus == 0:
            # 430f40 -> 455b90: preceding paragraph images use opacity 128/255.
            previous = "{alpha=0.5019607843}" + previous + "{/alpha}"
        return previous + store.kagerou_page_current

    def kagerou_parse_words(lex):
        return rscript_arguments(lex, ["Mode", "Slot", "CG", "KeepFocus", "Unused"])

    def kagerou_excmd(args):
        from engine.kagerou_native import excmd_calls
        values = tuple(int(getattr(args, name)) & 65535
                       for name in ("Mode", "Slot", "CG", "KeepFocus", "Unused"))
        positions = store.kagerou_character_layouts[persistent.kagerou_character_focus][persistent.kagerou_snap]
        calls = excmd_calls(values, x=positions.get(values[1]),
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
        store.kagerou_page_old = ""
        store.kagerou_page_current = ""
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
        box = rscript_textbox_state()
        rect = box["text_rect"]
        sample = RScriptText(combined, size=persistent.rscript_text_size,
                             font=rscript_current_font(), slow_cps=0,
                             vertical=box["vertical"])
        sample.refresh_settings()
        width, height = rect[2:]
        if box["vertical"]:
            width, height = height, width
        used = renpy.text.text.Layout(sample, width, height, {}, size_only=True,
                                       drawable_res=False).size[1]
        if previous and used > height:
            combined = parsed
            previous = ""
        if not previous:
            store.kagerou_page_old, store.kagerou_page_current = "", parsed
        elif append:
            store.kagerou_page_current += "{fast}" + parsed
        else:
            store.kagerou_page_old = previous + "{fast}" + separator
            store.kagerou_page_current = parsed
        store.kagerou_page = combined
        execute_say((None, None, repr(kagerou_page_text())), interact=bool(wait))

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
        rscript_text (kagerou_page_text() if kagerou_page else what):
            id "what"
            font rscript_current_font()
            size persistent.rscript_text_size
            color "#ffffff"
            slow_cps persistent.rscript_text_cps
            line_spacing persistent.rscript_line_spacing
        if textbox_panel:
            use kagerou_compane
            use kagerou_excompane

screen choice(items):
    use rscript_choice(items, kagerou_choice_prompt)

screen kagerou_compane():
    # Native bak enters the text log, not a state-rewinding rollback.
    use rscript_compane
    fixed:
        pos (585, 572)
        xysize (205, 18)
        use rscript_grps_button("compane", "bak", Show("kagerou_history"))

screen kagerou_history():
    modal True
    zorder 100
    key "game_menu" action Hide("kagerou_history")
    add Solid("#000000dd")
    viewport:
        pos (30, 30)
        xysize (740, 510)
        mousewheel True
        draggable True
        scrollbars "vertical"
        yinitial 1.0
        vbox:
            spacing 20
            for entry in _history_list:
                text entry.what:
                    font rscript_current_font()
                    size persistent.rscript_text_size
                    color "#ffffff"
                    substitute False
    textbutton "戻る / 返回" action Hide("kagerou_history") align (0.5, 0.95)

screen kagerou_ex_button(name, action, selected=False, enabled=True):
    $ items = rscript_layouts()["excompane"]["items"]
    $ item = items[name]
    $ idle = name + "_l" if selected and name + "_l" in items else name
    $ disabled = name + "_c" if name + "_c" in items else name
    imagebutton:
        idle rscript_ui_image("excompane", idle)
        hover rscript_ui_image("excompane", idle if idle.endswith("_l") else name + "_f")
        insensitive rscript_ui_image("excompane", disabled)
        pos item[:2]
        action action
        sensitive enabled

screen kagerou_excompane():
    fixed:
        # 42bfce..42bfe3: parent origin (0,550); child origins are LWG metadata.
        pos (0, 550)
        xysize (300, 50)
        for index in range(9):
            use kagerou_ex_button("snap_%d" % index,
                                  Function(kagerou_set_text_setting, "snap", index),
                                  selected=persistent.kagerou_snap == index)
        for index in range(3):
            use kagerou_ex_button("size_%d" % index,
                                  Function(kagerou_set_text_setting, "size", index),
                                  selected=persistent.kagerou_size == index)
        for prefix, field in (("dir", "direction"), ("shdw", "shadow"),
                              ("tfcs", "text_focus"), ("lfcs", "character_focus")):
            $ value = getattr(persistent, "kagerou_" + field)
            $ icon = 1 - value if field == "direction" else value
            use kagerou_ex_button("%s_%d" % (prefix, icon),
                                  Function(kagerou_set_text_setting, field, 1 - value))
        use kagerou_ex_button("font_0", Show("rscript_font_picker"))
        # shortcut: native lctr changes the unverified inactive-pixel algorithm.
        # Enable this control once EXCMD draw(4,50) is implemented.
        use kagerou_ex_button("lctr_0", NullAction(), enabled=False)

init 10 python:
    rscript_ui.setdefault("layouts", {})["compane"] = dict(
        rscript_grps_layout["compane"], controls={name: spec for name, spec in
            rscript_grps_layout["compane"]["controls"].items() if name != "bak"})
    # Kagerou's log is opened by its native bak control, not a quick-menu substitute.
    config.overlay_screens = [name for name in config.overlay_screens if name != "quick_menu"]
