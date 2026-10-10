# Installed only in a disposable renderer fixture, never in a player project.
init 100 python:
    def modern_ruby_exception(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = modern_ruby_exception
    config.autosave_on_choice = False

label _0000:
    window hide
    $ renpy.hide_screen("rscript_compane")
    $ persistent.rscript_say_line_chars = 2
    $ persistent.rscript_text_size = 32
    _texruby 0 2 13 9
    _texpich 0 11 0
    show expression Solid("#123456") as ruby_background
    $ ruby_probe = RScriptText("{rb}漢字漢字{/rb}{rt}あいうえ{/rt}", slow=False, color="#ffffff")
    show expression ruby_probe as ruby_probe at Transform(xpos=200, ypos=200)
    $ renpy.pause(.1, hard=True)
    python:
        layout = ruby_probe.get_layout()
        assert layout.has_ruby
        glyphs = layout.paragraph_glyphs[0]
        base = [g for g in glyphs if g.ruby == 1]
        reading = [g for g in glyphs if g.ruby == 2]
        assert base[0].y == base[1].y < base[2].y == base[3].y
        assert reading[0].y == reading[1].y < reading[2].y == reading[3].y
        for index, glyph in enumerate(reading):
            body = base[0 if index < 2 else 2]
            assert glyph.y == round(body.y - body.ascent + glyph.ascent - layout.scale(9))
        assert layout.add_top > 0  # First-row annotation has drawable headroom.
        renpy.screenshot("/tmp/rscript-modern-ruby.png")
        print("OK: native modern ruby drawable layout and clipping headroom")
        renpy.quit()
