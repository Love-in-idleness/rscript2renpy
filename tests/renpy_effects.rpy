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

    def effects_test_pixel(expected):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        actual = image.get_at((20, 20))[:3]
        assert all(abs(a - b) <= 3 for a, b in zip(actual, expected)), (actual, expected)

label _0000:
    window hide
    $ renpy.hide_screen("rscript_compane")
    $ store.layer_anchor[20] = (0.0, 0.0)
    $ store.folder[20] = "grpo"
    $ store.layer_x_grid = store.layer_y_grid = 1
    # Real shader compilation and framebuffer blending, including destination invert.
    show expression Solid("#204060") as effect_test_background
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
