# Only installed in disposable shared-port fixtures, never in a player project.
init 100 python:
    def effects_test_exception(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = effects_test_exception
    config.autosave_on_choice = False
    renpy.image("grpo 9990", Solid("#204060", xsize=100, ysize=80))
    renpy.image("grps es101", Solid("#000000", xsize=100, ysize=80))
    renpy.image("grps es102", Solid("#808080", xsize=100, ysize=80))
    renpy.image("grpo 9980", Solid("#ff0000", xsize=100, ysize=80))
    renpy.image("grpo 9981", Solid("#0000ff", xsize=100, ysize=80))
    renpy.image("grpo 9982", Solid("#00ff00", xsize=100, ysize=80))
    renpy.image("missing_dynamic", DynamicImage("grps/nonexistent-dynamic.png"))

    def effects_test_pixel(expected):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        actual = image.get_at((20, 20))[:3]
        assert all(abs(a - b) <= 3 for a, b in zip(actual, expected)), (actual, expected)

    def effects_test_missing_images():
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        renpy.screenshot("/tmp/rscript-missing-images.png")
        for y in range(8, 160, 8):
            for x in range(8, 792, 8):
                actual = image.get_at((x, y))[:3]
                assert all(abs(a - b) <= 3 for a, b in zip(actual, (32, 64, 96))), (x, y, actual)

screen effects_test_wakeup():
    # A modal click screen blocks the pause behavior underneath it.
    timer .1 repeat True action Function(renpy.end_interaction, True)

label _0000:
    window hide
    $ renpy.hide_screen("rscript_compane")
    $ store.layer_anchor[20] = (0.0, 0.0)
    $ store.folder[20] = "grpo"
    $ store.layer_x_grid = store.layer_y_grid = 1
    # Real shader compilation and framebuffer blending, including destination invert.
    show expression Solid("#204060") as effect_test_background
    # Cover raw references too, not only images loaded by RScript commands.
    show grpo_r1 0520 as missing_reference
    show expression renpy.displayable("grpo_r1 0521") as missing_displayable
    show expression Image("grps/nonexistent.png") as missing_file
    show missing_dynamic
    $ assert rscript_missing_image("engine/gui/rscript_cursor.png") is None
    $ renpy.pause(0.1, hard=True)
    $ effects_test_missing_images()
    hide missing_reference
    hide missing_displayable
    hide missing_file
    hide missing_dynamic
    _effect 101 1
    $ renpy.pause(0.1, hard=True)
    $ effects_test_pixel((223, 191, 159))
    _effect 0 0
    _effect 102 0
    $ renpy.pause(0.1, hard=True)
    $ effects_test_pixel((32, 64, 96))
    _effect 0 0
    $ renpy.show("white_probe", what=Solid("#204060", xsize=100, ysize=80), at_list=[Transform(shader="rscript.white", u_rscript_white=1.0)])
    $ renpy.pause(0.1, hard=True)
    $ effects_test_pixel((255, 255, 255))
    $ renpy.hide("white_probe")
    _load 20 9990 0 0 15 0
    $ renpy.pause(0.1, hard=True)
    $ effects_test_pixel((32, 64, 96))
    _cls 20 15
    $ assert 20 not in store.layer_info and 20 not in store.layer_pos
    _queue
    _load 20 9990 0 0 19 0
    $ assert store.in_queue and store.draw_queue
    _action
    _cls 20 10
    $ assert 20 not in store.layer_info and 20 not in store.layer_pos
    # Same ordering as music list < tone < lyrics. Check actual framebuffer,
    # not only scene metadata; screens must contain transparent hit masks.
    $ store.folder[11] = store.folder[40] = "grpo"
    $ store.layer_anchor[11] = store.layer_anchor[40] = (0.0, 0.0)
    _load 11 9980 0 0 0 0
    _load 40 9982 0 0 0 0
    _tonedep 40
    _tone 50 0
    show screen effects_test_wakeup
    show screen rscript_click_screen(options=[(1, False, "grpo 9980", "grpo 9981", 0, 0)], layers={0: 11})
    $ renpy.pause(0.1, hard=True)
    $ effects_test_pixel((0, 255, 0))
    $ rscript_click_focus(11, "grpo 9981", ("grpo 9980", 0, 0))
    $ renpy.pause(0.1, hard=True)
    $ effects_test_pixel((0, 255, 0))
    _depth 11 50
    $ renpy.pause(0.1, hard=True)
    $ effects_test_pixel((0, 0, 255))
    $ rscript_click_focus(11)
    $ renpy.pause(0.1, hard=True)
    $ effects_test_pixel((255, 0, 0))
    hide screen rscript_click_screen
    hide screen effects_test_wakeup
    _tone 0 0
    _cls 11 0
    _cls 40 0
    python:
        for effect in (0, 2, 3, 4, 15, 19, 24, 28):
            lex = renpy.lexer.Lexer([("effects-test", 1,
                "20 200 100 %d 0 'object'" % effect, [])])
            lex.advance()
            execute_oload(parse_oload(lex))
            assert isinstance(store.layer_info[20], RScriptText)
            assert store.layer_pos[20] == (200, 100)
            execute_cls(type("Args", (), {"Layer": 20, "Effect": effect})())
            assert 20 not in store.layer_info and 20 not in store.layer_pos
        assert not store.in_queue and not store.draw_queue and not store.draw_queue_delayed
        print("OK: native object effects, queued execution, white fade and mask inversion")
        renpy.quit()
