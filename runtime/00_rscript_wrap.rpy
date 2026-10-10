default persistent.rscript_say_line_chars = 19
default persistent.rscript_oload_line_chars = 20

python early:
    import builtins
    import math
    from engine import rscript_wrap

    # Ren'Py 8.5.3 text.py: Layout shapes glyphs before linebreak_nobreak,
    # then copies the virtual layout's splits to the drawable layout. This
    # small internal adapter is opt-in; ordinary Ren'Py text keeps its layout.
    _rscript_native_layout = getattr(renpy.text.text.Layout,
                                    "rscript_native", renpy.text.text.Layout)
    _rscript_native_nobreak = getattr(
        renpy.text.text.textsupport.linebreak_nobreak, "rscript_native",
        renpy.text.text.textsupport.linebreak_nobreak)
    _rscript_native_segment = getattr(renpy.text.text.TextSegment,
                                     "rscript_native", renpy.text.text.TextSegment)
    _rscript_native_ruby = getattr(renpy.text.text.textsupport.place_ruby,
                                  "rscript_native", renpy.text.text.textsupport.place_ruby)
    _rscript_layout_stack = []

    def rscript_native_ruby_enabled(text):
        return (isinstance(text, RScriptText) and text.rscript_kind == "say" and
                getattr(store, "rscript_native_text_metrics", False) and
                "ruby" in rscript_textbox_state())

    def rscript_place_ruby(glyphs, ruby_offset, altruby_offset, width, height):
        _rscript_native_ruby(glyphs, ruby_offset, altruby_offset, width, height)
        if _rscript_layout_stack:
            layout, text = _rscript_layout_stack[-1]
            if rscript_native_ruby_enabled(text):
                box = rscript_textbox_state()
                scale = persistent.rscript_text_size / float(store.rscript_base_text_size)
                rscript_wrap.place_native_ruby(glyphs, layout.scale(box["ruby"][2] * scale),
                    layout.rscript_ruby_advances)

    def rscript_text_settings(kind, base_size):
        return (gui.text_font, base_size,
                getattr(persistent, "rscript_%s_line_chars" % kind), 0)

    class RScriptText(renpy.text.text.Text):
        def __init__(self, text, kind="say", base_size=None, **properties):
            self.rscript_kind = kind
            self.rscript_base_size = base_size
            self.rscript_settings = None
            properties["layout"] = "nobreak"
            properties["language"] = "anywhere"
            super(RScriptText, self).__init__(text, **properties)
            self.rscript_style = self.style

        def update(self):
            super(RScriptText, self).update()
            ts = renpy.text.text.textsupport
            self.tokens = rscript_wrap.normalize_boundaries(
                self.tokens, ts.TEXT, ts.PARAGRAPH, ts.DISPLAYABLE)

        def refresh_settings(self):
            base = self.rscript_base_size or self.style.size
            settings = rscript_text_settings(self.rscript_kind, base)
            box = rscript_textbox_state() if self.rscript_kind == "say" else {}
            signature = (settings, _preferences.language,
                         getattr(persistent, "rscript_wiki_mode", False), tuple(sorted(box.items())))
            if signature != self.rscript_settings:
                self.rscript_settings = signature
                font, size, chars, spacing = settings
                # Anonymous styles cache resolved properties too. Replacing
                # this instance's style avoids a global style.rebuild() and
                # prevents an existing _oload from retaining its old font.
                prefix = self.style.prefix
                self.style = self.rscript_style.copy()
                self.style.font = font
                slot_font = getattr(store, "rscript_font_slots", {}).get(box.get("font_slot"))
                if slot_font and renpy.loadable(slot_font):
                    self.style.font = slot_font
                self.style.size = size
                self.style.line_spacing = (spacing - getattr(store, "rscript_line_spacing_default", 7)
                    if "pitch" in box and getattr(store, "rscript_native_text_metrics", False) else spacing)
                if "alignment" in box and not self.rscript_style.text_align:
                    self.style.text_align = box["alignment"]
                    rect = box.get("text_rect")
                    if rect and box["alignment"]:
                        self.style.min_width = rect[2]
                if "color" in box:
                    self.style.color = box["color"]
                if prefix is not None:
                    self.style.set_prefix(prefix)
                self.update()
                renpy.redraw(self, 0)

        def per_interact(self):
            self.refresh_settings()
            super(RScriptText, self).per_interact()

        def render(self, width, height, st, at):
            self.refresh_settings()
            return super(RScriptText, self).render(width, height, st, at)

    class RScriptLayout(_rscript_native_layout):
        rscript_native = _rscript_native_layout
        def __init__(self, text, width, height, renders, size_only=False,
                     splits_from=None, drawable_res=True):
            self.rscript_ruby_advances = {}
            _rscript_layout_stack.append((self, text))
            try:
                if (isinstance(text, RScriptText) and not rscript_native_ruby_enabled(text) and splits_from is None and
                        any(kind == renpy.TEXT_TAG and value == "rt"
                            for kind, value in text.tokens)):
                    # Measure with the native shaper first. Resolved anonymous
                    # styles cache all properties: install a fresh copy BEFORE
                    # the real layout, never mutate an already resolved style.
                    # ponytail: two shaping passes for ruby blocks; cache only if profiling warrants it.
                    super(RScriptLayout, self).__init__(text, width, height, renders,
                                                       size_only=True, drawable_res=False)
                    glyphs = [g for paragraph in self.paragraph_glyphs for g in paragraph]
                    top = [g for g in glyphs if g.ruby == 2]
                    if top:
                        # Use visible ink, not the font's ascender padding.
                        # Ruby belongs in the existing gap; it must not move
                        # body baselines or add leading to any line.
                        bottom_bounds, top_bounds = [], []
                        for paragraph in self.paragraphs:
                            for segment, content in paragraph:
                                if (getattr(segment, "ruby_bottom", False) or
                                        getattr(segment, "ruby_top", False)):
                                    bounds = segment.bounds(segment.glyphs(content, self),
                                                            (0, 0, 0, 0), self)
                                    (top_bounds if segment.ruby_top else bottom_bounds).append(bounds)
                        ascent = max((-b[1] for b in bottom_bounds),
                                     default=text.style.size)
                        offset = -math.ceil(ascent + max(b[3] for b in top_bounds))
                        ruby_style = text.style.ruby_style.copy()
                        ruby_style.yoffset = offset
                        new_style = text.style.copy()
                        new_style.ruby_style = ruby_style
                        text.style = new_style
                super(RScriptLayout, self).__init__(text, width, height, renders,
                    size_only=size_only, splits_from=splits_from, drawable_res=drawable_res)
                if size_only and self.has_ruby and rscript_native_ruby_enabled(text):
                    rscript_place_ruby(builtins.list(g for p in self.paragraph_glyphs for g in p),
                        self.scale_int(text.style.ruby_style.yoffset),
                        self.scale_int(text.style.altruby_style.yoffset), *self.size)
            finally:
                _rscript_layout_stack.pop()

    class RScriptTextSegment(_rscript_native_segment):
        rscript_native = _rscript_native_segment
        def glyphs(self, s, layout, level=0):
            glyphs = super(RScriptTextSegment, self).glyphs(s, layout, level)
            text = _rscript_layout_stack[-1][1] if _rscript_layout_stack else None
            if text is not None and rscript_native_ruby_enabled(text):
                # The SDK replaces end-of-line advances with Glyph.width.
                # Retain the shaped cell advance before that and char pitch.
                layout.rscript_ruby_advances.update((id(g), g.advance) for g in glyphs if g.ruby == 1)
            if (isinstance(text, RScriptText) and text.rscript_kind == "say" and
                    getattr(store, "rscript_native_text_metrics", False) and "pitch" in rscript_textbox_state()):
                line, char = rscript_textbox_state()["pitch"]
                scale = persistent.rscript_text_size / float(store.rscript_base_text_size)
                for glyph in glyphs:
                    if glyph.ruby < 2:
                        # 457062/457086: advance + char pitch; size + line pitch.
                        glyph.advance += layout.scale(char * scale)
                        glyph.line_spacing = max(1, math.ceil(self.size + layout.scale(line * scale)))
            return glyphs

        def take_style(self, style, layout, context=None):
            # Native hyperlink_text inherits the default font, not the
            # surrounding text. Wiki links must only add link presentation;
            # keep the active font/style/tag metrics and typewriter timing.
            shared = (_rscript_layout_stack and
                      isinstance(_rscript_layout_stack[-1][1], RScriptText))
            linked = shared and context == "A hyperlink style"
            ruby = shared and context == "The ruby style"
            if linked or ruby:
                names = ("font", "size", "bold", "italic", "kerning",
                         "hinting", "antialias", "shaper", "axis",
                         "instance", "features", "cps")
                metrics = {name: getattr(self, name) for name in names}
                color = self.color
            super(RScriptTextSegment, self).take_style(style, layout, context)
            if linked or ruby:
                for name, value in metrics.items():
                    setattr(self, name, value)
            if ruby:
                scale = getattr(store, "rscript_ruby_scale", 0.5)
                if _rscript_layout_stack[-1][1].rscript_kind == "say":
                    box = rscript_textbox_state()
                    if "ruby" in box:
                        scale = box["ruby"][1] / float(box.get("size", getattr(store, "rscript_base_text_size", 22)))
                        slot_font = getattr(store, "rscript_font_slots", {}).get(box["ruby"][0])
                        if slot_font and renpy.loadable(slot_font):
                            self.font = slot_font
                self.size = max(layout.scale(1), self.size * scale)
                self.kerning *= scale
                self.color = color

    def rscript_linebreak(glyphs):
        _rscript_native_nobreak(glyphs)
        if not _rscript_layout_stack:
            return
        layout, text = _rscript_layout_stack[-1]
        if not isinstance(text, RScriptText):
            return
        ts = renpy.text.text.TextSegment()
        ts.take_style(text.style, layout)
        fullwidth = sum(g.advance for g in ts.glyphs("\u3000", layout))
        chars = text.rscript_settings[0][2]
        limit = (fullwidth or layout.scale(text.style.size)) * chars
        if text.rscript_kind == "say":
            rect = rscript_textbox_state().get("text_rect")
            if rect and rect[2] > 0:
                limit = min(limit, layout.scale(rect[2]))
        for index in rscript_wrap.glyph_breaks(glyphs, limit,
                ruby_atomic=not rscript_native_ruby_enabled(text)):
            glyphs[index].split = 1

    renpy.text.text.Layout = RScriptLayout
    renpy.text.text.TextSegment = RScriptTextSegment
    rscript_linebreak.rscript_native = _rscript_native_nobreak
    renpy.text.text.textsupport.linebreak_nobreak = rscript_linebreak
    rscript_place_ruby.rscript_native = _rscript_native_ruby
    renpy.text.text.textsupport.place_ruby = rscript_place_ruby
    renpy.register_sl_displayable("rscript_text", RScriptText, "text",
                                  scope=True, replaces=True) \
        .add_property("kind") \
        .add_property("base_size").copy_properties("text")
