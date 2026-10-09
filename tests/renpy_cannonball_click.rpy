# Disposable graphical regression; never installed into a player's project.
default cannonball_test_select = False
default cannonball_choice_index = 0
default cannonball_timed_caption_test = False
default cannonball_effect_test = False
default cannonball_effect_mode = 0
default cannonball_dim_test = False

init 100 python:
    def cannonball_click_error(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = cannonball_click_error
    config.autosave_on_choice = False
    renpy.image("grpo 9995", Solid("#ff0000", xsize=100, ysize=50))
    renpy.image("grpo 9996", Solid("#0000ff", xsize=100, ysize=50))
    renpy.image("grpo 9997", Solid("#00ff00", xsize=100, ysize=50))
    renpy.image("grpo 9994", Solid("#204060", xsize=100, ysize=100))

    def cannonball_effect_capture(restored=False):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        expected = ((32, 64, 96) if restored else
                    ((32, 64, 96), (223, 191, 159), (88, 112, 136), (16, 24, 32))[cannonball_effect_mode])
        actual = image.get_at((350, 250))[:3]
        assert all(abs(a - b) <= 2 for a, b in zip(actual, expected)), (cannonball_effect_mode, restored, actual, expected)
        outside = image.get_at((290, 190))[:3]
        assert all(abs(a - b) <= 2 for a, b in zip(outside, (16, 24, 32))), outside

    def cannonball_dim_capture():
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        expected = (26, 32, 39) if cannonball_dim_test else (128, 160, 192)
        actual = image.get_at((20, 20))[:3]
        assert all(abs(a - b) <= 2 for a, b in zip(actual, expected)), (actual, expected)
        if renpy.get_screen("preferences") is not None:
            panel = tuple(image.get_at((x, 130))[:3] for x in range(200, 250, 10))
            if cannonball_dim_test:
                # The menu itself is translucent; only its underlying scene darkens.
                artwork = pygame.image.load(renpy.file(rscript_ui_image("confscrn", "bg")))
                for x, before, after in zip(range(200, 250, 10), store.cannonball_dim_panel, panel):
                    alpha = sum(artwork.get_at((x - 141, y))[3] for y in (23, 24)) / 510.
                    expected_panel = tuple(c + (dim - bg) * (1 - alpha)
                                           for c, dim, bg in zip(before, (26, 32, 39), (128, 160, 192)))
                    assert all(abs(a - b) <= 3 for a, b in zip(after, expected_panel)), (after, expected_panel)
                renpy.screenshot("/tmp/cannonball-menu-dim.png")
            else:
                store.cannonball_dim_panel = panel

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

    def cannonball_timed_captions(hover=False):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        counts = [sum(min(image.get_at((x, y))[:3]) > 180
                      for y in range(top, top + 30) for x in range(170, 450))
                  for top in (95, 140)]
        renpy.screenshot("/tmp/cannonball-2122-captions.png")
        assert all(count > 100 for count in counts), (counts, layer_pos[42], layer_pos[44])
        if not hover:
            renpy.set_mouse_pos(180, 145)

    def cannonball_menu_frame(hover=False):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        # Two 520x50 cropped frames centered at x=140, y=210 and y=260.
        renpy.screenshot("/tmp/cannonball-2121-choice-frames.png")
        for y in (214, 264):
            assert image.get_at((160, y))[2] > 90, image.get_at((160, y))
        pixel = image.get_at((600, 280))[:3]
        expected = (0, 0, 0) if not hover else (0, 108, 128)
        assert all(abs(a - b) <= 3 for a, b in zip(pixel, expected)), (pixel, expected)
        if hover:
            renpy.screenshot("/tmp/cannonball-2121-choice-frames.png")
        else:
            renpy.set_mouse_pos(600, 280)

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
        # Only the focused portrait changes; it is not replaced by its card.
        changed = sum(max(abs(a - b) for a, b in zip(before, after)) > 20
                      for before, after in zip(store.cannonball_choice_portraits, portraits))
        assert 100 < changed < 2600, (cannonball_choice_index, changed)
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

    def cannonball_choice_restored():
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        portraits = tuple(image.get_at((x, y))[:3] for y in range(0, 470, 8) for x in range(0, 800, 8))
        changed = sum(max(abs(a - b) for a, b in zip(before, after)) > 20
                      for before, after in zip(store.cannonball_choice_portraits, portraits))
        assert changed < 100, (cannonball_choice_index, changed)
        assert not renpy.showing("rscript_click_preview", layer=IMAGE_LAYER)

screen rscript_click_extra(options):
    if cannonball_effect_test:
        timer .2 action Function(renpy.set_mouse_pos, 350, 250)
        timer .3 action Function(cannonball_click_motion)
        timer .5 action Function(cannonball_effect_capture)
        timer .6 action Function(renpy.set_mouse_pos, 0, 590)
        timer .7 action Function(cannonball_click_motion)
        timer .9 action Function(cannonball_effect_capture, True)
        timer 1.0 action Return(7)
    elif cannonball_timed_caption_test:
        timer .6 action Function(cannonball_timed_captions)
        timer .75 action Function(cannonball_click_motion)
        timer .9 action Function(cannonball_timed_captions, True)
        timer 1.0 action Function(cannonball_click_select)
    elif cannonball_choice_index:
        timer .3 action Function(cannonball_choice_capture)
        timer .5 action Function(cannonball_choice_move)
        timer .65 action Function(cannonball_click_motion)
        timer .9 action Function(cannonball_choice_capture, True)
        timer 1.0 action Function(renpy.set_mouse_pos, 0, 590)
        timer 1.1 action Function(cannonball_click_motion)
        timer 1.3 action Function(cannonball_choice_restored)
        timer 1.4 action Function(cannonball_choice_move)
        timer 1.5 action Function(cannonball_click_select)
    elif cannonball_test_select:
        timer .15 action Function(cannonball_click_position)
        timer .25 action Function(cannonball_click_select)
    timer 3.0 action Function(renpy.quit, status=1)

screen cannonball_menu_test(items):
    use rscript_choice(items)
    timer .3 action Function(cannonball_menu_frame)
    timer .5 action Function(cannonball_click_motion)
    timer .7 action Function(cannonball_menu_frame, True)
    timer .8 action Function(cannonball_click_select)
    timer 3.0 action Function(renpy.quit, status=1)

screen cannonball_dim_timer():
    zorder 100
    timer .3 action Function(cannonball_dim_capture)
    timer .4 action Return(True)

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
        call cannonball_choice_2122
        call cannonball_choice_2121
    call cannonball_hover_effects
    call cannonball_menu_dim
    $ renpy.quit()

label cannonball_hover_effects:
    _cls 0 0
    _rscript_number numenable 0 0
    scene onlayer cg
    scene onlayer master
    scene expression Solid("#101820", xsize=800, ysize=600) onlayer black
    $ rscript_click_link_is_preview = True
    $ cannonball_effect_test = True
    $ cannonball_test_select = False
    $ folder[41] = "grpo"
    _load 41 9994 300 200 0 0
    while cannonball_effect_mode <= 3:
        $ renpy.set_mouse_pos(0, 590)
        # Both regular and system registrations must retain the effect operand.
        if cannonball_effect_mode % 2:
            _setclksys 41 7 cannonball_effect_mode 0
        else:
            _setclk 41 7 cannonball_effect_mode 0
        _click 0 0
        $ assert _r[0] == 7 and not rscript_click_modes
        $ cannonball_effect_mode += 1
    $ cannonball_effect_test = False
    $ print("OK: native hover modes 0/1/2/3, alpha mask, mouse exit and reset")
    return

label cannonball_menu_dim:
    _cls 0 0
    $ process_draw_queue()
    scene onlayer cg
    scene onlayer master
    scene expression Solid("#80a0c0", xsize=800, ysize=600) onlayer black
    $ cannonball_dim_layout = rscript_layouts()["confscrn"]
    $ cannonball_dim_strength = cannonball_dim_layout["background_dim"]
    $ cannonball_dim_layout["background_dim"] = 0
    show screen cannonball_dim_timer
    call screen preferences
    hide screen cannonball_dim_timer
    $ cannonball_dim_layout["background_dim"] = cannonball_dim_strength
    $ cannonball_dim_test = True
    show screen cannonball_dim_timer
    call screen preferences
    hide screen cannonball_dim_timer
    $ cannonball_dim_test = False
    $ renpy.pause(.1, hard=True)
    $ cannonball_dim_capture()
    $ print("OK: native background dim, unchanged menu artwork and close restoration")
    return

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

label cannonball_choice_2122:
    $ rscript_click_link_is_preview = True
    $ cannonball_timed_caption_test = True
    _cls 0 0
    _locmode 0 0 0
    $ folder.update({number: "grpo_r1" for number in range(35, 46)})
    $ cannonball_caption_languages = [None, "zh"]
    while cannonball_caption_languages:
        $ _preferences.language = cannonball_caption_languages.pop(0)
        $ renpy.set_mouse_pos(0, 590)
        $ _r[1001] = 200
        $ _r[1002] = 2
        $ _r[1014] = -1
        _gosub 1071
        _oload 44 171 95 0 0 {'zh': '笔直往前冲！'}.get(_preferences.language, 'このままつっこむ！')
        _oload 42 171 95 0 0 {'zh': '躲开太空垃圾'}.get(_preferences.language, 'デブリをかわす')
        _gosub 1072
        _click 0 0
        $ assert _r[0] == 2, _r[0]
    $ cannonball_timed_caption_test = False
    $ print("OK: real JP/ZH 1071/1072 moving choices keep both captions visible, including hover")
    return

label cannonball_choice_2121:
    _cls 0 0
    _rscript_number numenable 0 0
    $ process_draw_queue()
    $ renpy.set_mouse_pos(0, 590)
    $ cannonball_menu_languages = [None, "zh"]
    while cannonball_menu_languages:
        $ _preferences.language = cannonball_menu_languages.pop(0)
        python:
            from types import SimpleNamespace
            captions = (("听从弗克茜的指示", "一口气加速") if _preferences.language == "zh" else
                        ("フォクシィの指示に従う", "一気に加速する"))
            items = [SimpleNamespace(caption=caption, action=Return(index)) for index, caption in enumerate(captions)]
        call screen cannonball_menu_test(items)
        $ assert _return == 1, _return
        $ renpy.set_mouse_pos(0, 590)
    $ print("OK: JP/ZH 2121 text choices render native frame crops, hover and click")
    return
