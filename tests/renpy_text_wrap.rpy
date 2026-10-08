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
        raw = "|学習装置[インキュナブラ]后"
        parsed, _ = parse_rscript_text(repr(raw), True)
        assert parsed == "{rb}学習装置{/rb}{rt}インキュナブラ{/rt}后"
        for kind in ("say", "oload"):
            for size in (22, 32, 44):
                ruby_text, ruby_layout = shaped(parsed, chars=4, size=size, kind=kind)
                assert lines(ruby_layout) == ["学習装置インキュナブラ", "后"]
                glyphs = ruby_layout.paragraph_glyphs[0]
                base = [g for g in glyphs if g.ruby == 1]
                top = [g for g in glyphs if g.ruby == 2]
                assert all(g.advance == size / 2 for g in top)
                assert ruby_layout.size[0] == size * 4
                ruby_segment = next(segment for paragraph in ruby_layout.paragraphs
                                    for segment, _ in paragraph if segment.ruby_top)
                assert ruby_segment.font == gui.text_font and ruby_segment.size == size / 2
                # Execute the SDK's real ruby placement (size_only normally
                # stops before this), checking geometry without a video device.
                renpy.text.text.textsupport.place_ruby(glyphs, ruby_text.style.ruby_style.yoffset, 0, *ruby_layout.size)
                assert all(g.y - g.ascent >= 0 for g in top), [(g.y, g.ascent) for g in top]
                assert all(g.y < base[0].y for g in top), (size, [(chr(g.character), g.x, g.y, g.ascent, g.descent, g.split, g.ruby) for g in glyphs])
        # An annotation cannot be orphaned by wrapping within its base.
        assert lines(shaped(parsed, chars=2)[1]) == ["学習装置インキュナブラ", "后"]
        tagged, _ = parse_rscript_text(repr("^b^fm^cy|漢字[かんじ]^b^n|字[じ]"), True)
        _, ruby_layout = shaped(tagged, chars=20)
        ruby_segments = [segment for paragraph in ruby_layout.paragraphs
                         for segment, _ in paragraph if segment.ruby_top]
        assert ruby_segments[0].bold and ruby_segments[0].color == Color("#FFDE00")
        inline, _ = parse_rscript_text(repr("{size=44}|漢字[かんじ]{/size}"), True)
        ruby_text, ruby_layout = shaped(inline, chars=20)
        top = [g for g in ruby_layout.paragraph_glyphs[0] if g.ruby == 2]
        assert all(g.advance == 22 for g in top)
        renpy.text.text.textsupport.place_ruby(ruby_layout.paragraph_glyphs[0],
            ruby_text.style.ruby_style.yoffset, 0, *ruby_layout.size)
        assert all(g.y - g.ascent >= 0 for g in top)
        original_font = gui.text_font
        gui.text_font = "fonts/NotoSerifCJK-Regular.ttc"
        ruby_text.refresh_settings()
        ruby_layout = renpy.text.text.Layout(ruby_text, 800, 600, {}, size_only=True, drawable_res=False)
        assert next(segment for paragraph in ruby_layout.paragraphs
                    for segment, _ in paragraph if segment.ruby_top).font == gui.text_font
        gui.text_font = original_font
        visible, _ = parse_rscript_text(repr("[literal] |incomplete[  "), True)
        assert lines(shaped(visible, chars=100)[1]) == ["[literal] |incomplete[  "]
        original_faces = getattr(store, "rscript_text_fonts", None)
        try:
            store.rscript_text_fonts = {"m": "fonts/NotoSerifCJK-Regular.ttc",
                                        "g": "fonts/NotoSansCJKjp-Regular.otf"}
            parsed, centered = parse_rscript_text(
                repr("^FM甲^CR乙^B丙^FG丁^I戊^CW己^B庚^I辛^V-0129^N^M壬"), True)
            assert centered and "{font=fonts/NotoSerifCJK-Regular.ttc}" in parsed
            assert "{color=#B73333}" in parsed
            assert lines(shaped(parsed, chars=100)[1]) == ["甲乙丙丁戊己庚辛－０１２９", "壬"]
            plain, _ = parse_rscript_text(repr("^CR甲^CW乙"), False)
            assert plain == "甲乙"
            for raw in ("^d0^fm甲^cr乙^fg丙^cw丁", "^s2甲^fm乙^cr丙^s1丁",
                        "^b甲^i乙^b丙^i丁", "^d3甲>^fm乙^cr丙<"):
                parsed, _ = parse_rscript_text(repr(raw), True)
                expected = "甲乙丙丁" if raw.endswith("丁") else "甲乙丙"
                assert "".join(lines(shaped(parsed, chars=100)[1])) == expected
                if raw.endswith("<"):
                    assert parsed.endswith("{nw}")
        finally:
            if original_faces is None:
                del store.rscript_text_fonts
            else:
                store.rscript_text_fonts = original_faces
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
        assert lines(linked) == ["甲乙", "丙"], lines(linked)
        assert linked.hyperlink_targets[1] == "https://example.test"
        sample = "之后，我俩跑到{color=#D7FFB3}Royal Host餐厅{/color}，就桃色电影\n高谈阔论，一直聊到第二天黎明时分，才在乌鸦的喧闹声中作别。"
        sample_lines = []
        for wiki in (False, True):
            value = sample.replace("{color=#D7FFB3}", "{a=https://example.test}{color=#D7FFB3}").replace("{/color}", "{/color}{/a}") if wiki else sample
            _, diagnostic = shaped(value, chars=19)
            sample_lines.append(lines(diagnostic))
        assert sample_lines[0] == sample_lines[1]
        assert sample_lines[0] == ["之后，我俩跑到Royal Host餐厅，就桃色电影",
                                  "高谈阔论，一直聊到第二天黎明时分，才在", "乌鸦的喧闹声中作别。"]
        assert len(lines(shaped(sample, chars=20)[1])) == 3
        original_settings = store.rscript_text_settings
        try:
            # Forest's default spacing and fixed dialog height: this scene
            # now fits without changing the panel or discarding its ^n.
            store.rscript_text_settings = lambda kind, size: (gui.text_font, size, 19, 7)
            _, forest_sample = shaped(sample, chars=19)
            assert lines(forest_sample) == sample_lines[0]
            assert forest_sample.size[1] + 8 <= 138, forest_sample.size
        finally:
            store.rscript_text_settings = original_settings
        for tagged in ("Wi甲乙", "{size=44}Wi甲乙{/size}",
                       "{font=DejaVuSans.ttf}Wi甲乙{/font}",
                       "{b}{i}{k=3}Wi甲乙{/k}{/i}{/b}"):
            plain = shaped(tagged)[1]
            linked = shaped("{a=https://example.test}" + tagged + "{/a}")[1]
            assert lines(linked) == lines(plain)
            assert [g.advance for p in linked.paragraph_glyphs for g in p] == [g.advance for p in plain.paragraph_glyphs for g in p]
            linked = shaped(tagged.replace("Wi甲乙", "{a=https://example.test}Wi甲乙{/a}"))[1]
            assert lines(linked) == lines(plain)
            assert [g.advance for p in linked.paragraph_glyphs for g in p] == [g.advance for p in plain.paragraph_glyphs for g in p]
        image = Null(width=37, height=22)
        _, objects = shaped(builtins.list(("甲", image, "乙")))
        image_glyph = next(g for g in objects.paragraph_glyphs[0]
                           if g.character == 0xfffc)
        assert image_glyph.advance == 37
        assert lines(objects) == ["甲\ufffc", "乙"]
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
        # Original Windows font: auto hinting widens two sample letters.
        gui.text_font = "fonts/simhei.ttf"
        _, simhei = shaped("WiRoyal Host甲乙", chars=40)
        gs = simhei.paragraph_glyphs[0]
        assert [g.advance for g in gs[:-2]] == [11, 11, 11, 11, 11, 11,
                                              12, 11, 11, 11, 11, 12]
        assert all(g.advance == 22 for g in gs[-2:])
        widths = {"NotoSansCJKjp-Regular.otf": 106.703125,
                  "NotoSansCJK-Light.ttc": 105.796875,
                  "NotoSerifCJK-Regular.ttc": 114.6875, "simhei.ttf": 112.0}
        for name, expected_width in widths.items():
            gui.text_font = "fonts/" + name
            _, measured = shaped("Royal Host甲", chars=40)
            advances = [g.advance for g in measured.paragraph_glyphs[0]]
            assert sum(advances[:-1]) == expected_width, (name, advances)
            assert advances[-1] == 22
            _, measured = shaped(sample, chars=19)
            if name.startswith("NotoSans"):
                assert lines(measured) == sample_lines[0], (name, lines(measured))
            else:
                assert len(lines(measured)) == 4, (name, lines(measured))
        print("Default Noto Sans 22px / 19 cells:", sample_lines[0])
        gui.text_font = "fonts/simhei.ttf"
        assert "".join(lines(shaped("甲Я。A")[1])) == "甲Я。A"
        original_settings = store.rscript_text_settings
        try:
            store.rscript_text_settings = lambda kind, size: (gui.text_font, size, 19, 7)
            _, simhei_sample = shaped(sample, chars=19)
            assert simhei_sample.size[1] + 8 <= 138, simhei_sample.size
            print("SimHei 22px / 19 cells:", lines(simhei_sample), simhei_sample.size)
        finally:
            store.rscript_text_settings = original_settings
            gui.text_font = "fonts/NotoSansCJKjp-Regular.otf"
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
