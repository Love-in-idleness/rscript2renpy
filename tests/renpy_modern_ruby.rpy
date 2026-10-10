# Installed only in a disposable renderer fixture, never in a player project.
init 100 python:
    def modern_ruby_exception(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = modern_ruby_exception
    config.autosave_on_choice = False
    modern_dynamic_page = 0

    def modern_dynamic_pick():
        global modern_dynamic_page
        menu = renpy.get_screen("choice")
        if menu is None:
            return
        items = menu.scope["items"]
        expected = (["0", "1", "2", "3", "Next"] if modern_dynamic_page == 0 else ["4", "5", "Next"])
        assert [item.caption for item in items] == expected, (modern_dynamic_page, [item.caption for item in items])
        positions = rscript_dynamic_geometry(items, rscript_choice_prompt)
        assert positions[0] == (250, 125 if modern_dynamic_page == 0 else 180), positions
        assert positions[1] == (280, 180 if modern_dynamic_page == 0 else 235), positions
        if modern_dynamic_page == 0:
            renpy.screenshot("/tmp/rscript-modern-choice.png")
        modern_dynamic_page += 1
        return renpy.run(items[-1 if modern_dynamic_page == 1 else 0].action)

screen modern_dynamic_driver():
    timer .05 repeat True action Function(modern_dynamic_pick)

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
    _dynsel ("Pages", 0)
    _dynnext "Next"
    python:
        for number in range(6):
            execute_dynans(repr((str(number), number, 0, 0)))
    show screen modern_dynamic_driver
    _dyndo 2 0 1
    hide screen modern_dynamic_driver
    python:
        assert _r[0] == 4 and modern_dynamic_page == 2
        assert rscript_dynamic_skin is None and rscript_choice_prompt is None
        print("OK: native dynamic-choice paging through real menu actions")
        renpy.quit()
