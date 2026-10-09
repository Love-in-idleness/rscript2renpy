# Disposable graphical regression; never installed into a player's project.
default cannonball_test_select = False

init 100 python:
    def cannonball_click_error(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = cannonball_click_error
    config.autosave_on_choice = False
    renpy.image("grpo 9995", Solid("#ff0000", xsize=100, ysize=50))
    renpy.image("grpo 9996", Solid("#0000ff", xsize=100, ysize=50))
    renpy.image("grpo 9997", Solid("#00ff00", xsize=100, ysize=50))

    def cannonball_click_position():
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        actual = (image.get_at((170, 100))[:3], image.get_at((170, 140))[:3])
        assert all(abs(a - b) <= 2 for pixel, expected in zip(actual, ((0, 0, 255), (0, 255, 0)))
                   for a, b in zip(pixel, expected)), actual
        renpy.set_mouse_pos(170, 140)

    def cannonball_click_select():
        import pygame_sdl2 as pygame
        pos = pygame.mouse.get_pos()
        # Xvfb warping changes position without reliably emitting mouse motion.
        pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)))
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1))

screen rscript_click_extra(options):
    if cannonball_test_select:
        timer .15 action Function(cannonball_click_position)
        timer .25 action Function(cannonball_click_select)
    timer 3.0 action Function(renpy.quit, status=1)

label before_main_menu:
    scene black onlayer black
    $ folder[41] = folder[42] = folder[43] = "grpo"
    $ layer_anchor[41] = layer_anchor[42] = (.5, .5)
    _locmode 0 0 0
    _load 41 9995 150 84 0 0
    _load 42 9997 150 84 0 0
    _load 43 9996 150 84 0 0
    _movi 41 0 45 0 0
    _movi 42 0 45 0 0
    _rscript_number numload 0 0 1 0
    _rscript_number numreng 0 0 100 0 0
    _rscript_number numloc 0 150 64
    _rscript_number numset 0 0 0 16 1
    _rscript_number numenable 0 1
    $ _r[1000] = 5
    _setclk 41 2 3 0
    _setlink 41 9996 150 129
    _click 1000 1
    $ assert _r[0] == 0 and rscript_numbers[0]["Value"] == 0
    # Real hit testing at the moved second option, while text stays above it.
    $ cannonball_test_select = True
    $ _r[1000] = 100
    _setclk 41 2 3 0
    _setlink 41 9996 150 129
    _click 1000 1
    $ assert _r[0] == 2 and 0 < _r[1000] < 100, (_r[0], _r[1000])
    # Untimed choices remain clickable and do not start another countdown.
    _setclk 41 2 3 0
    _setlink 41 9996 150 129
    _click 0 0
    $ assert _r[0] == 2
    $ print("OK: native timed click expires, early mouse selection retains time, moved hit areas/depth and zero-width bar render")
    $ renpy.quit()
