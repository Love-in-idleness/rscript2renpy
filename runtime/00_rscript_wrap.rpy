default persistent.rscript_say_line_chars = 19
default persistent.rscript_oload_line_chars = 20

python early:
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
    _rscript_layout_stack = []

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
            signature = (settings, _preferences.language,
                         getattr(persistent, "rscript_wiki_mode", False))
            if signature != self.rscript_settings:
                self.rscript_settings = signature
                font, size, chars, spacing = settings
                # Anonymous styles cache resolved properties too. Replacing
                # this instance's style avoids a global style.rebuild() and
                # prevents an existing _oload from retaining its old font.
                prefix = self.style.prefix
                self.style = self.rscript_style.copy()
                self.style.font = font
                self.style.size = size
                self.style.line_spacing = spacing
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
            _rscript_layout_stack.append((self, text))
            try:
                if (isinstance(text, RScriptText) and splits_from is None and
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
                        leading = math.ceil(max(g.ascent + g.descent for g in top))
                        ascent = max((g.ascent for g in glyphs if g.ruby == 1), default=0)
                        offset = -math.ceil(ascent + max(g.descent for g in top))
                        base_leading = text.rscript_style.line_leading
                        ruby_style = text.style.ruby_style.copy()
                        ruby_style.yoffset = offset
                        new_style = text.style.copy()
                        new_style.line_leading = base_leading + leading
                        new_style.ruby_style = ruby_style
                        text.style = new_style
                super(RScriptLayout, self).__init__(text, width, height, renders,
                    size_only=size_only, splits_from=splits_from, drawable_res=drawable_res)
            finally:
                _rscript_layout_stack.pop()

    class RScriptTextSegment(_rscript_native_segment):
        rscript_native = _rscript_native_segment
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
                self.size = max(layout.scale(1), self.size / 2)
                self.kerning /= 2
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
        for index in rscript_wrap.glyph_breaks(glyphs, limit):
            glyphs[index].split = 1

    renpy.text.text.Layout = RScriptLayout
    renpy.text.text.TextSegment = RScriptTextSegment
    rscript_linebreak.rscript_native = _rscript_native_nobreak
    renpy.text.text.textsupport.linebreak_nobreak = rscript_linebreak
    renpy.register_sl_displayable("rscript_text", RScriptText, "text",
                                  scope=True, replaces=True) \
        .add_property("kind") \
        .add_property("base_size").copy_properties("text")
