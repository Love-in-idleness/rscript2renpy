# Run with tests/run_native_text_wrap.py (no graphical session).
define gui.text_font = "fonts/NotoSansCJKjp-Regular.otf"

python early:
    def check_rscript_native_layout():
        import builtins
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        def shaped(value, chars=2, size=22, kind="say", **properties):
            setattr(persistent, "rscript_%s_line_chars" % kind, chars)
            text = RScriptText(value, kind=kind, base_size=size,
                               size=size, **properties)
            text.refresh_settings()
            text.update()
            # Null.render supplies a real sized Render without a video device.
            renders = {d: d.render(800, size, 0, 0)
                       for d in text.displayables}
            layout = renpy.text.text.Layout(text, 800, 600, renders,
                                           drawable_res=False, size_only=True)
            return text, layout
        def lines(layout):
            result = []
            for paragraph in layout.paragraph_glyphs:
                current = ""
                for g in paragraph:
                    if g.split and current:
                        result.append(current)
                        current = ""
                    current += chr(g.character)
                result.append(current)
            return result
        text, layout = shaped("甲乙。！")
        assert lines(layout) == ["甲乙。", "！"], lines(layout)
        assert layout.size[0] >= 66  # overflow glyph is not clipped
        assert lines(shaped("甲（乙")[1]) == ["甲", "（乙"]
        assert lines(shaped("甲（")[1]) == ["甲（"]
        assert lines(shaped("甲（。")[1]) == ["甲（。"]
        raw = "^n^n 甲 ^n^cy^n\u3000乙 …─–― ^n^n"
        parsed, _ = parse_rscript_text(repr(raw), True)
        assert "…─–― " in parsed and " 甲 " in parsed
        assert lines(shaped(parsed, chars=100)[1]) == [" 甲 ", "\u3000乙 …─–― "]
        visible, _ = parse_rscript_text(repr("50% [甲] "), True)
        assert lines(shaped(visible, chars=100)[1]) == ["50% [甲] "]
        tagged = "{b}甲{color=#f00}乙{size=44}丙{/size}{/color}{/b}{w=1}丁"
        _, tagged_layout = shaped(tagged)
        gs = [g for p in tagged_layout.paragraph_glyphs for g in p]
        assert gs[2].advance > gs[0].advance
        assert "".join(lines(tagged_layout)) == "甲乙丙丁"
        _, proportion = shaped("WiWiWi")
        gs = proportion.paragraph_glyphs[0]
        assert gs[0].advance != gs[1].advance
        for properties in ({"bold": True}, {"italic": True}, {"kerning": 3}):
            _, sample = shaped("Wi甲乙", **properties)
            assert sample.paragraph_glyphs[0]
        _, spaced = shaped("甲乙", kerning=3)
        assert spaced.paragraph_glyphs[0][0].advance == 25
        _, switched = shaped("W{font=DejaVuSans.ttf}W{/font}", chars=20)
        assert switched.paragraph_glyphs[0][0].advance != switched.paragraph_glyphs[0][1].advance
        for char in "\u3000\u00a0っ»—":
            _, sample = shaped("甲乙" + char + "丙")
            assert lines(sample) == ["甲乙" + char, "丙"], lines(sample)
        assert lines(shaped("甲乙“")[1]) == ["甲乙“"]
        assert lines(shaped("甲乙“丙")[1]) == ["甲乙", "“丙"]
        # Explicit breaks reset hanging, and nested links retain token order.
        assert lines(shaped("甲乙。\n\n{a=https://example.test}{b}甲乙。{/b}{/a}")[1]) == ["甲乙。", "甲乙。"]
        _, linked = shaped("{a=https://example.test}{color=#0f0}甲乙丙{/color}{/a}")
        assert "".join(lines(linked)) == "甲乙丙", lines(linked)
        assert linked.hyperlink_targets[1] == "https://example.test"
        image = Null(width=37, height=22)
        _, objects = shaped(builtins.list(("甲", image, "乙")))
        image_glyph = next(g for g in objects.paragraph_glyphs[0]
                           if g.character == 0xfffc)
        assert image_glyph.advance == 37
        assert lines(objects) == ["甲", "\ufffc", "乙"]
        obj, _ = shaped("甲乙{fast}丙", kind="oload")
        persistent.rscript_oload_line_chars = 1
        obj.refresh_settings()
        changed_object = renpy.text.text.Layout(obj, 800, 600, {},
                                               drawable_res=False, size_only=True)
        assert lines(changed_object) == ["甲", "乙", "丙"]
        obj.rscript_base_size = 44
        obj.refresh_settings()
        larger = renpy.text.text.Layout(obj, 800, 600, {},
                                       drawable_res=False, size_only=True)
        assert obj.style.size == 44 and larger.paragraph_glyphs[0][0].advance == 44
        assert lines(shaped("甲乙{fast}丙")[1]) == ["甲乙", "丙"]
        # Re-use one text object after changing configuration, not a new object.
        persistent.rscript_say_line_chars = 1
        text.refresh_settings()
        changed = renpy.text.text.Layout(text, 800, 600, {},
                                        drawable_res=False, size_only=True)
        assert lines(changed) == ["甲", "乙。", "！"], lines(changed)
        # The same object is invalidated when the font or language changes.
        old_signature = text.rscript_settings
        gui.text_font = "DejaVuSans.ttf"
        text.refresh_settings()
        assert text.rscript_settings != old_signature
        assert text.style.font == "DejaVuSans.ttf", (text.rscript_settings, text.style.font)
        old_signature = text.rscript_settings
        _preferences.language = "ru"
        text.refresh_settings()
        assert text.rscript_settings != old_signature
        gui.text_font = "fonts/NotoSansCJKjp-Regular.otf"
        _preferences.language = None
        text.refresh_settings()
        for language in (None, "jp", "en", "ru", "zh"):
            _preferences.language = language
            assert lines(shaped("甲乙。Ж")[1]) == ["甲乙。", "Ж"]
        _preferences.language = None
        # Test the actual append executor, not just a preassembled fast tag.
        class Speaker:
            def do_extend(self):
                pass
        narrator = Speaker()
        store.narrator = narrator
        store.nvl_mode = False
        store.jump_back_point = "test"
        persistent.rscript_stop_voice_on_advance = False
        store.queue_draw = lambda *args, **kwargs: None
        store.process_draw_queue = lambda: None
        captured = []
        original_say = renpy.say
        try:
            renpy.say = lambda who, what, **kwargs: captured.append(what)
            execute_say((None, None, repr("甲乙")))
            execute_append((None, repr("丙。")))
        finally:
            renpy.say = original_say
        assert captured == ["甲乙", "甲乙{fast}丙。"], captured
        assert lines(shaped(captured[-1])[1]) == ["甲乙", "丙。"]
        for source in ("", "\n\n", "甲\n\n", "\n甲", "\u3000\u00a0"):
            shaped(source)
        print("OK: Ren'Py shaped advances, tags, image, object, append and reflow")
        return False
    renpy.arguments.register_command("wraptest", check_rscript_native_layout)

label start:
    return
