# Disposable mouse/pixel test; never installed into the player's project.
default khime_click_stage = 0

init 100 python:
    def khime_click_error(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = khime_click_error
    config.autosave_on_choice = False
    renpy.image("grpo_ex 9991", Solid("#204060", xsize=100, ysize=40))
    renpy.image("grpo_ex 9992", Solid("#0000ff", xsize=60, ysize=30))
    renpy.image("grpo_ex 9993", Solid("#00ff00", xsize=60, ysize=30))

    def khime_click_mouse(click=False, outside=False):
        import pygame_sdl2 as pygame
        pos = (0, 590) if outside else ((350, 525), (560, 180), (560, 135))[khime_click_stage]
        renpy.set_mouse_pos(*pos)
        pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)))
        if click:
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1))

    def khime_click_pixels(outside=False):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        scene = renpy.game.context().scene_lists
        point = ((350, 525), (560, 180), (560, 135))[khime_click_stage]
        if outside:
            assert scene.get_displayable_by_tag(IMAGE_LAYER, "rscript_click_preview") is None
            assert scene.get_displayable_by_tag(IMAGE_LAYER, "rscript_click_preview1") is None
            samples = [(point, (32, 64, 96))]
        elif khime_click_stage < 2:
            assert scene.get_displayable_by_tag(IMAGE_LAYER, "rscript_click_preview") is None
            samples = [(point, (32, 64, 96))]
        else:
            # Mode 3 omits only the body; both cards retain their own positions.
            samples = [(point, (16, 32, 48)), ((200, 215), (0, 0, 255)), ((320, 415), (0, 255, 0))]
            assert scene.get_displayable_by_tag(IMAGE_LAYER, "rscript_click_preview1") is not None
        for point, color in samples:
            actual = image.get_at(point)[:3]
            assert max(abs(a - b) for a, b in zip(actual, color)) <= 2, (point, actual, color)

init offset = 20
screen rscript_click_extra(options):
    timer .15 action Function(khime_click_mouse)
    timer .3 action Function(khime_click_mouse)
    timer .5 action Function(khime_click_pixels)
    timer .6 action Function(khime_click_mouse, outside=True)
    timer .8 action Function(khime_click_pixels, outside=True)
    timer .9 action Function(khime_click_mouse)
    timer 1.1 action Function(khime_click_mouse, True)

label _0000:
    $ assert rscript_click_link_is_preview and rscript_click_native_effects
    $ renpy.pause(.05, hard=True)
    _khime_folder 0 'grpo_ex'
    _khime_locmode 0 0 0
    _autoreset 0
    $ renpy.show("test_background", what=Solid("#102030"), layer=IMAGE_LAYER, zorder=-10)
    # Seed the former extras/gallery bindings, then reproduce 0501's reuse.
    _load 41 9991 253 342 0 0
    _khime_setclk 41 11 3 0
    _khime_setlink 41 9992 180 200 0
    _khime_setlink 41 9993 300 400 1
    _queue
    _cls 41 0
    _load 41 9991 152 330 0 0
    _load 42 9991 332 508 0 0
    _update 0 0 0
    _khime_setclk 42 21 0 0
    $ renpy.set_mouse_pos(0, 590)
    _khime_click 0 0 0
    $ assert _r[0] == 21 and 41 not in rscript_click_values
    _cls 0 0
    $ khime_click_stage = 1
    # 0401 songs register only setclk; no link/old portrait is required.
    _load 6 9991 531 160 0 0
    _khime_setclk 6 6 0 0
    $ renpy.set_mouse_pos(0, 590)
    _khime_click 0 0 0
    $ assert _r[0] == 6
    _cls 0 0
    $ khime_click_stage = 2
    # 0301: both cards appear away from the body's real hit rectangle.
    _load 12 9991 531 117 0 0
    _khime_setclk 12 12 3 0
    _khime_setlink 12 9992 180 200 0
    _khime_setlink 12 9993 300 400 1
    $ renpy.set_mouse_pos(0, 590)
    _khime_click 0 0 0
    $ assert _r[0] == 12
    $ assert renpy.game.context().scene_lists.get_displayable_by_tag(IMAGE_LAYER, "rscript_click_preview1") is None
    $ print("OK: native Khime menu binding cleanup, song hit coordinates and two hover cards")
    $ renpy.quit()
