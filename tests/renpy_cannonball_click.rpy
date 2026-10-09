# Disposable graphical regression; never installed into a player's project.
default cannonball_test_select = False
default cannonball_choice_index = 0

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

    def cannonball_click_motion():
        import pygame_sdl2 as pygame
        pos = pygame.mouse.get_pos()
        # Xvfb warping changes position without reliably emitting mouse motion.
        pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)))

    def cannonball_click_select():
        import pygame_sdl2 as pygame
        cannonball_click_motion()
        pos = pygame.mouse.get_pos()
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1))

    def cannonball_choice_move():
        point = ((160, 200), (410, 200), (660, 200), (265, 367), (535, 367))[cannonball_choice_index - 1]
        renpy.set_mouse_pos(*point)

    def cannonball_choice_capture(check=False):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        portraits = tuple(image.get_at((x, y))[:3] for y in range(0, 470, 8) for x in range(0, 800, 8))
        if not check:
            store.cannonball_choice_portraits = portraits
            return
        # Inserting a card can split the raster batch and change edge sampling.
        # A replaced portrait would change most of this full-scene sample.
        changed = sum(max(abs(a - b) for a, b in zip(before, after)) > 20
                      for before, after in zip(store.cannonball_choice_portraits, portraits))
        assert changed < 100, (cannonball_choice_index, changed)
        scene = renpy.game.context().scene_lists
        preview = scene.get_displayable_by_tag(IMAGE_LAYER, "rscript_click_preview")
        assert preview is not None and preview.get_placement()[:2] == (205, 490), (preview, cannonball_choice_index)
        screen = renpy.get_screen("rscript_click_screen")
        buttons = []
        screen.visit_all(lambda d: buttons.append(d) if isinstance(d, renpy.display.behavior.Button) else None)
        points = [(int(d.style.xpos), int(d.style.ypos)) for d in buttons]
        assert points == [(160, 200), (410, 200), (660, 200), (265, 367), (535, 367)], points
        if cannonball_choice_index == 5:
            renpy.screenshot("/tmp/cannonball-3160-choice-fixed.png")

screen rscript_click_extra(options):
    if cannonball_choice_index:
        timer .3 action Function(cannonball_choice_capture)
        timer .5 action Function(cannonball_choice_move)
        timer .65 action Function(cannonball_click_motion)
        timer .9 action Function(cannonball_choice_capture, True)
        timer 1.0 action Function(cannonball_click_select)
    elif cannonball_test_select:
        timer .15 action Function(cannonball_click_position)
        timer .25 action Function(cannonball_click_select)
    timer 3.0 action Function(renpy.quit, status=1)

label before_main_menu:
    scene black onlayer black
    $ rscript_click_link_is_preview = False
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
    if renpy.has_image("grpo_cl 1401", exact=True):
        call cannonball_choice_3160
    $ renpy.quit()

label cannonball_choice_3160:
    $ cannonball_test_select = False
    $ rscript_click_link_is_preview = True
    _cls 0 0
    _gload 404 0
    $ _preferences.language = "zh"
    $ folder.update({number: "grpo_cl" for number in range(20, 25)})
    _locmode 20 1 1
    _locmode 21 1 1
    _locmode 22 1 1
    _locmode 23 1 1
    _locmode 24 1 1
    # The actual 3160.tsc loads and links, including the independent text card.
    _load 20 1401 160 200 0 0
    _load 21 1801 410 200 0 0
    _load 22 741 660 200 0 0
    _load 23 201 265 367 0 0
    _load 24 601 535 367 0 0
    $ cannonball_choice_index = 1
    while cannonball_choice_index <= 5:
        $ renpy.set_mouse_pos(0, 590)
        _setclk 20 1 2 0
        _setclk 21 2 2 0
        _setclk 22 3 2 0
        _setclk 23 4 2 0
        _setclk 24 5 2 0
        _setlink 20 6 205 490
        _setlink 21 7 205 490
        _setlink 22 8 205 490
        _setlink 23 9 205 490
        _setlink 24 10 205 490
        _click 0 0
        $ assert _r[0] == cannonball_choice_index, (_r[0], cannonball_choice_index)
        $ assert not renpy.showing("rscript_click_preview", layer=IMAGE_LAYER)
        $ cannonball_choice_index += 1
    $ cannonball_choice_index = 0
    $ print("OK: real 3160 artwork, five portrait hit areas and independent hover cards")
    return
