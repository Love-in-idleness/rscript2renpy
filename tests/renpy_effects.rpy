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
    renpy.image("grps es103", Solid("#4080c0", xsize=100, ysize=80))
    renpy.image("grpo 9980", Solid("#ff0000", xsize=100, ysize=80))
    renpy.image("grpo 9981", Solid("#0000ff", xsize=100, ysize=80))
    renpy.image("grpo 9982", Solid("#00ff00", xsize=100, ysize=80))
    renpy.image("missing_dynamic", DynamicImage("grps/nonexistent-dynamic.png"))

    class EffectsTimeProbe(renpy.Displayable):
        def __init__(self, child, when):
            super(EffectsTimeProbe, self).__init__()
            self.child, self.when = child, when
        def render(self, width, height, st, at):
            return renpy.render(self.child, width, height, self.when, self.when)
        def visit(self):
            return [self.child]

    def effects_test_pixel(expected, pos=(20, 20)):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        actual = image.get_at(pos)[:3]
        assert all(abs(a - b) <= 3 for a, b in zip(actual, expected)), (actual, expected)

    def effects_test_native_exit(when, effect=31):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        samples = ([(220, 280, (255, 0, 0)), (270, 280, (255, 0, 0))] if when == 0 else
                   [(220, 430, (116, 40, 60)), (270, 130, (116, 40, 60)), (220, 280, (32, 64, 96))] if when == .5 else
                   [(220, 430, (32, 64, 96)), (270, 130, (32, 64, 96))])
        if effect == 34:
            offset = rscript_clear_frame(34, int(when / .05 + 1e-9))[1]
            samples = [(250, 290 + offset, (255, 0, 0) if when < 1.1 else (32, 64, 96))]
        for x, y, expected in samples:
            actual = image.get_at((x, y))[:3]
            if not all(abs(a - b) <= 3 for a, b in zip(actual, expected)):
                pygame.image.save(image, "/tmp/rscript-native-exit.png")
            assert all(abs(a - b) <= 3 for a, b in zip(actual, expected)), (when, x, y, actual, expected)

    def effects_test_missing_images():
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        renpy.screenshot("/tmp/rscript-missing-images.png")
        for y in range(8, 160, 8):
            for x in range(8, 792, 8):
                actual = image.get_at((x, y))[:3]
                assert all(abs(a - b) <= 3 for a, b in zip(actual, (32, 64, 96))), (x, y, actual)

    def effects_test_grid(level, vertical=False):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        for y in range(32):
            for x in range(32):
                visible = x % 16 > level // 16 if vertical else (y % 16 > level // 16 and (x + y) % 16 > level // 16)
                expected = (255, 0, 0) if visible else (32, 64, 96)
                actual = image.get_at((x, y))[:3]
                assert all(abs(a - b) <= 3 for a, b in zip(actual, expected)), (level, x, y, actual, expected)

    def effects_test_ordered(mask):
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        assert renpy.get_physical_size() == (800, 600), renpy.get_physical_size()
        # Compare a precomputed native bitmap through the same SDK filtering.
        renpy.show('ordered_probe', what=Image('ordered-%04x.png' % mask))
        renpy.pause(.05, hard=True)
        reference = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes((800, 600))))
        for y in range(32):
            for x in range(32):
                expected = reference.get_at((x, y))[:3]
                actual = image.get_at((x, y))[:3]
                # The SDK framebuffer may round a solid 255 channel to 254.
                assert all(abs(a - b) <= 1 for a, b in zip(actual, expected)), (mask, x, y, actual, expected)

    def effects_test_ordered_scale(ordered, when):
        import io
        import pygame_sdl2 as pygame
        mask = ordered.mask_at(when)
        assert mask == 0x0810
        for size in ((700, 525), (1000, 750)):
            renpy.set_physical_size(size)
            renpy.show('ordered_probe', what=EffectsTimeProbe(ordered, when))
            renpy.pause(.2, hard=True)
            actual = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes(None)))
            renpy.show('ordered_probe', what=Image('ordered-%04x.png' % mask))
            renpy.pause(.2, hard=True)
            expected = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes(None)))
            assert actual.get_size() == expected.get_size() == size
            for y in range(80, 112):
                for x in range(80, 112):
                    a, b = actual.get_at((x, y))[:3], expected.get_at((x, y))[:3]
                    assert all(abs(i - j) <= 2 for i, j in zip(a, b)), (size, mask, x, y, a, b)
        renpy.hide('ordered_probe')
        renpy.set_physical_size((800, 600))
        renpy.pause(.2, hard=True)

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
    _effect 103 0
    $ renpy.pause(.1, hard=True)
    $ effects_test_pixel((16, 64, 176))
    _effect 0 0
    $ renpy.show("white_probe", what=Solid("#204060", xsize=100, ysize=80), at_list=[Transform(shader="rscript.white", u_rscript_white=1.0)])
    $ renpy.pause(0.1, hard=True)
    $ effects_test_pixel((255, 255, 255))
    $ renpy.hide("white_probe")
    python:
        # Native CMath byte tables and Level/Night constants, not HSV tinting.
        expected_colors = ((0, 0, 0), (223, 191, 159), (64, 64, 64),
            (70, 35, 9), (36, 30, 70), (129, 65, 0), (28, 57, 87),
            (10, 16, 48), (14, 24, 96), (32, 23, 60), (35, 60, 88),
            (32, 40, 36), (88, 48, 48))
        for mode, expected in enumerate(expected_colors, 1):
            renpy.show("color_probe", what=Solid("#204060", xsize=100, ysize=80),
                       at_list=[Transform(shader="rscript.colormode", u_colormode=mode)])
            renpy.pause(.05, hard=True)
            effects_test_pixel(expected)
        renpy.hide("color_probe")
        # Expected bytes from the independently executed, reviewed Power routine.
        for source, expected in (("#ff0000", (255, 1, 1)),
                                 ("#00ff00", (7, 255, 1)),
                                 ("#0000ff", (255, 192, 1)),
                                 ("#ff00ff", (255, 1, 240)),
                                 ("#00f6ff", (1, 228, 255)),
                                 ("#00f0ff", (1, 186, 255))):
            renpy.show("color_probe", what=Solid(source, xsize=100, ysize=80),
                       at_list=[Transform(shader="rscript.colormode", u_colormode=15)])
            renpy.pause(.05, hard=True)
            effects_test_pixel(expected)
        renpy.hide("color_probe")
        store.layer_mode[20] = 1
        assert rscript_colormode(15, 20) == 0
        store.layer_mode[20] = 0
        assert rscript_colormode(65536) == 0
        assert rscript_colormode(-65535) == 1
        assert rscript_colormode(999) == 0
        original_limit = store.rscript_colormode_limit
        store.rscript_colormode_limit = 5
        assert rscript_colormode(6) == 0
        store.rscript_colormode_limit = original_limit
    _load 20 9990 0 0 0 5
    _move 20 0 0 0 0
    $ renpy.pause(.05, hard=True)
    $ effects_test_pixel((36, 30, 70))
    python:
        # Check the active movement, before its final transform is restored.
        store.in_queue = True
        move_layer(20, 0, 0, 1, 16)
        store.in_queue = False
        moving = store.draw_queue.pop(0)
        moving[0](*moving[1], **moving[2])
        store.draw_queue.clear()
        store.draw_queue_delayed.clear()
        store.draw_queue_extra_delayed.clear()
    $ renpy.pause(.05, hard=True)
    $ effects_test_pixel((36, 30, 70))
    _oaction 20 4
    $ renpy.pause(.05, hard=True)
    $ effects_test_pixel((36, 30, 70))
    _cls 20 0
    $ assert 20 not in store.layer_color
    _load 20 9990 0 0 0 0
    _draw 20 3 50
    $ renpy.pause(.1, hard=True)
    $ effects_test_pixel((8, 32, 72))
    $ rscript_show_layer("layer20", what=Solid("#204060", xsize=100, ysize=80))
    $ renpy.pause(.1, hard=True)
    $ effects_test_pixel((8, 32, 72))
    _draw 20 4 50
    $ renpy.pause(.1, hard=True)
    $ effects_test_pixel((16, 32, 48))
    _draw 20 5 50
    $ renpy.pause(.1, hard=True)
    $ effects_test_pixel((143, 159, 175))
    _draw 20 0 0
    $ renpy.pause(.1, hard=True)
    $ effects_test_pixel((32, 64, 96))
    _cls 20 0
    python:
        print("OK: native colors and draw 3/4/5", flush=True)
        for level in (-1, 0, 128, 255):
            renpy.show("grid_probe", what=Solid("#ff0000", xsize=100, ysize=80),
                       at_list=[Transform(mesh=True, shader="rscript.grid_wipe", u_rscript_grid=level)])
            renpy.pause(0.1, hard=True)
            effects_test_grid(level)
            renpy.show("grid_probe", what=Solid("#ff0000", xsize=100, ysize=80),
                       at_list=[Transform(mesh=True, shader="rscript.column_wipe", u_rscript_grid=level)])
            renpy.pause(.05, hard=True)
            effects_test_grid(level, vertical=True)
        renpy.hide("grid_probe")
        for effect, corner in ((11, (-100, -80)), (12, (800, -80)),
                               (13, (-100, 600)), (14, (800, 600))):
            path = rscript_diagonal_path(effect, (100, 80), (250, 190), (.5, .5), False)
            assert path[0] == corner and path[1] == (200, 150), path
            assert rscript_dynamic_position(path, 0) == corner
            assert rscript_dynamic_position(path, (path[2] + 1) * rscript_dynamic_tick) == (200, 150)
            reverse = rscript_diagonal_path(effect, (100, 80), (250, 190), (.5, .5), True)
            assert reverse[:2] == ((200, 150), corner)
        path = rscript_diagonal_path(11, (100, 80), (250, 190), (.5, .5), False)
        assert path[2] == 15
        assert rscript_dynamic_position(path, 8 * rscript_dynamic_tick) == (101, 74)
        assert rscript_diagonal_path(11, (1, 1), (0, 0), (0, 0), False)[:2] == ((-1, -1), (-1, -1))
        motion = RScriptDiagonal(Solid("#ff0000", xsize=100, ysize=80), 11, (250, 190), (.5, .5), False)
        for tick, pos, expected in ((0, (20, 20), (32, 64, 96)),
                                    (8, (120, 94), (255, 0, 0)),
                                    (16, (220, 170), (255, 0, 0))):
            renpy.show("diagonal_probe", what=EffectsTimeProbe(motion, tick * rscript_dynamic_tick))
            renpy.pause(.05, hard=True)
            effects_test_pixel(expected, pos)
        renpy.hide("diagonal_probe")
        print("OK: native diagonal path frames and stripe pixels", flush=True)
        old_timing = store.rscript_move4_timing
        old_grid = (store.layer_x_grid, store.layer_y_grid)
        old_anchor = dict(store.layer_anchor)
        try:
            for timing, steps in (("fixed-steps", 15), ("fixed-speed", 10), ("script", 10)):
                store.rscript_move4_timing = timing
                path = rscript_wave_path((150, 200), (450, 200), 10)
                assert path[2] == steps
                for tick in (0, steps // 2, steps + 1):
                    center = rscript_wave_position(path, tick * rscript_dynamic_tick)
                    image = Transform(Solid("#ff0000", xsize=100, ysize=80), alpha=1.,
                                      function=renpy.curry(rscript_wave_move)(path, (.5, .5), (1, 1)))
                    canvas = Fixed(image, xysize=(800, 600))
                    renpy.show("wave_probe", what=EffectsTimeProbe(canvas, tick * rscript_dynamic_tick))
                    renpy.pause(.05, hard=True)
                    effects_test_pixel((255, 0, 0), (center[0], center[1] - 30))
                    effects_test_pixel((32, 64, 96), (center[0] - 60, center[1]))
            renpy.hide("wave_probe")
            store.rscript_move4_timing = "fixed-speed"
            store.layer_info[20] = "grpo 9990"
            store.layer_pos[20] = (150, 200)
            store.layer_color[20] = 5
            store.layer_anchor[20] = (.5, .5)
            store.in_queue = True
            move_layer(20, 450, 200, 4, 99)
            assert store.layer_pos[20] == (450, 200)
            motion = store.draw_queue[0][2]["at_list"][0]
            assert motion.u_colormode == 5
            assert (_queue_ef_pause, (11 * rscript_dynamic_tick,), {}) in store.draw_queue
            motion.function(motion, .25, .25)
            assert motion.anchor == (.5, .5)
            assert motion.pos == rscript_wave_position(rscript_wave_path((150, 200), (450, 200), 99), .25)
            store.draw_queue.clear()
            store.draw_queue_delayed.clear()
            store.draw_queue_extra_delayed.clear()
            # Short CannonBall moves do not activate CMath, even with afterimages.
            for effect in (4, 104, 204):
                move_layer(20, 1, 0, effect, 0, relative=True)
                assert store.layer_pos[20] == (450, 200)
                store.draw_queue.clear()
                store.draw_queue_delayed.clear()
                store.draw_queue_extra_delayed.clear()
            # Resource coordinates must stay native in the scaled Khime Zero overlay.
            store.layer_x_grid = store.layer_y_grid = 1.25
            store.layer_pos[20] = (187.5, 250)
            move_layer(20, 450, 200, 4, 0)
            motion = store.draw_queue[0][2]["at_list"][0]
            motion.function(motion, .25, .25)
            native = rscript_wave_position(rscript_wave_path((150, 200), (450, 200), 0), .25)
            assert motion.pos == (native[0] * 1.25, native[1] * 1.25)
        finally:
            store.rscript_move4_timing = old_timing
            store.layer_x_grid, store.layer_y_grid = old_grid
            store.layer_anchor.clear()
            store.layer_anchor.update(old_anchor)
            store.in_queue = False
            store.draw_queue.clear()
            store.draw_queue_delayed.clear()
            store.draw_queue_extra_delayed.clear()
        print("OK: native move 4 timing, wave frames, anchors and color", flush=True)
        for amplitude, steps in ((40, 4), (100, 10), (300, 15)):
            for tick in (0, steps // 2, steps + 1):
                y = 400 + rscript_bounce_offset(amplitude, steps, tick)
                image = Transform(Solid("#ff0000", xsize=40, ysize=40), alpha=1.,
                    function=renpy.curry(rscript_bounce_move)((400, 400), (.5, .5), amplitude, steps, 1))
                renpy.show("bounce_probe", what=EffectsTimeProbe(Fixed(image, xysize=(800, 600)), tick * rscript_dynamic_tick))
                renpy.pause(.05, hard=True)
                effects_test_pixel((255, 0, 0), (400, y))
            renpy.hide("bounce_probe")
        print("OK: native bounce frames return to the original position", flush=True)
    _load 20 9990 0 0 15 0
    $ renpy.pause(0.1, hard=True)
    $ effects_test_pixel((32, 64, 96))
    _cls 20 15
    $ assert 20 not in store.layer_info and 20 not in store.layer_pos
    # Native draw changes the already shown image, without replacing its position/effects.
    _load 20 9980 0 0 0 0
    $ assert isinstance(renpy.game.context().scene_lists.get_displayable_by_tag(IMAGE_LAYER, "layer20").function, RScriptRasterVisibility)
    _draw 20 1 50
    $ renpy.pause(.1, hard=True)
    $ effects_test_pixel((144, 32, 48))
    _draw 20 2 50
    $ renpy.pause(.1, hard=True)
    $ effects_test_pixel((160, 64, 96))
    _draw 20 0 0
    $ renpy.pause(.1, hard=True)
    $ effects_test_pixel((255, 0, 0))
    _queue
    _draw 20 1 100
    $ assert store.layer_blend[20] == (0, 0)
    _action
    $ renpy.pause(.1, hard=True)
    $ effects_test_pixel((32, 64, 96))
    _draw 20 0 0
    _cls 20 0
    _queue
    _load 20 9990 0 0 19 0
    $ assert store.in_queue and store.draw_queue
    _action
    _cls 20 10
    $ assert 20 not in store.layer_info and 20 not in store.layer_pos
    python:
        assert rscript_clear_frame(31, 0) == (1, 0, 0, 1)
        assert rscript_clear_frame(31, 1)[1] == 0
        assert rscript_clear_frame(31, 10) == (.375, 150, 0, 1)
        assert rscript_clear_frame(31, 16)[0] == 0
        assert rscript_clear_frame(34, 0) == (1, 0, 0, 1)
        assert rscript_clear_frame(34, 1) == (1, 12, -340.3125, .94)
        assert rscript_clear_frame(34, 21) == (1, 0, -2.8125, .01)
        assert rscript_clear_frame(34, 22)[0] == 0
        for when in (0, .5, .8):
            probe = RScriptClearExit(Solid("#ff0000", xsize=100, ysize=80), 31, (250, 290), (.5, .5))
            renpy.show("clear_probe", what=EffectsTimeProbe(probe, when))
            renpy.pause(.1, hard=True)
            effects_test_native_exit(when)
        renpy.hide("clear_probe")
        for when in (0, .5, 1.1):
            probe = RScriptClearExit(Solid("#ff0000", xsize=100, ysize=80), 34, (250, 290), (.5, .5))
            renpy.show("clear_probe", what=EffectsTimeProbe(probe, when))
            renpy.pause(.1, hard=True)
            effects_test_native_exit(when, 34)
        renpy.hide("clear_probe")
        for effect, samples in ((30, ((210, 300), (285, 280), (220, 255))),
                                 (32, ((150, 175), (220, 310), (220, 260))),
                                 (35, ((270, 270), (180, 310), (220, 270)))):
            probe = RScriptClearExit(Solid("#ff0000", xsize=100, ysize=80), effect, (250, 290), (.5, .5))
            renpy.show("clear_probe", what=EffectsTimeProbe(probe, 5 * rscript_dynamic_tick))
            renpy.pause(.1, hard=True)
            for pos in samples[:2]:
                effects_test_pixel((194, 17, 26) if effect != 35 else (185, 20, 30), pos)
            effects_test_pixel((32, 64, 96), samples[2])
            renpy.hide("clear_probe")
        assert rscript_clear_frame(33, 1) == (1, 12, 0, .06)
        assert rscript_clear_frame(33, 21)[0] == 0
        # Lim/Anim affine slots are stubs: no cuts or rotation/resize.
        for effect in (30, 32, 35, 33, 34):
            probe = RScriptClearExit(Solid("#ff0000", xsize=100, ysize=80), effect,
                                    (250, 290), (.5, .5), full=False)
            renpy.show("clear_probe", what=EffectsTimeProbe(probe, 5 * rscript_dynamic_tick))
            renpy.pause(.1, hard=True)
            if effect in (33, 34):
                effects_test_pixel((255, 0, 0), (210, 290 + rscript_bounce_offset(250, 20, 5)))
            else:
                effects_test_pixel((185, 20, 30) if effect == 35 else (194, 17, 26),
                                   {30: (210, 340), 32: (220, 280), 35: (300, 280)}[effect])
            renpy.hide("clear_probe")
        store.layer_mode[20] = 1
        for effect in range(30, 36):
            loadcls(20, 0, cg=9990)
            store.in_queue = True
            loadcls(20, effect, clear=True)
            assert (_queue_ef_pause, (rscript_clear_duration(effect),), {}) in store.draw_queue
            assert 20 not in store.layer_info and 20 not in store.layer_pos
            store.in_queue = False
            process_draw_queue()
            assert not renpy.showing("layer20", layer=IMAGE_LAYER)
        store.layer_mode[20] = 0
        assert rscript_clear_duration(34, False) == 21 * rscript_dynamic_tick
    python:
        renpy.set_physical_size((800, 600))
        renpy.pause(.2, hard=True)
        masks = (0xffdf, 0xefdf, 0x6fdf, 0x6fd7, 0x6bd7, 0x6bd6, 0x6b56, 0x6a56,
                 0x2a56, 0x2a52, 0x0a52, 0x0a12, 0x0812, 0x0810, 0x0800, 0)
        assert RScriptOrderedDissolve.masks == masks
        for steps in (1, 3, 10, 16, 32):
            ordered = RScriptOrderedDissolve((steps - 1) * .05, steps,
                old_widget=Solid('#f00', xsize=800, ysize=600),
                new_widget=Solid('#00f', xsize=800, ysize=600))
            for frame in range(steps - 1):
                when = frame * .05 + .001
                expected = masks[((steps - frame) * 255 // steps) >> 4]
                assert ordered.mask_at(when) == expected
                renpy.show('ordered_probe', what=EffectsTimeProbe(ordered, when))
                renpy.pause(.05, hard=True)
                effects_test_ordered(expected)
            renpy.show('ordered_probe', what=EffectsTimeProbe(ordered, ordered.delay))
            renpy.pause(.05, hard=True)
            effects_test_ordered(65535)
            renpy.hide('ordered_probe')
        effects_test_ordered_scale(ordered, .201)
        single = RScriptOrderedDissolve(1, 1,
            old_widget=Solid('#f00'), new_widget=Solid('#00f'))
        assert single.mask_at(0) == 65535
        renpy.render(single, 800, 600, 0, 0)
        for steps in (0, -1):
            try:
                RScriptOrderedDissolve(1, steps)
            except ValueError:
                pass
            else:
                raise AssertionError('invalid ordered dissolve accepted')
        for effect, phase in ((116, .155), (216, .205)):
            zoom = RScriptCompoundZoom(effect,
                old_widget=Solid("#f00", xsize=800, ysize=600),
                new_widget=Solid("#00f", xsize=800, ysize=600))
            for when, expected in ((0, (255, 0, 0)), (phase - .005, (255, 0, 0)),
                                   (phase, (0, 0, 255)), (zoom.delay, (0, 0, 255))):
                renpy.show("zoom_probe", what=EffectsTimeProbe(zoom, when))
                renpy.pause(.1, hard=True)
                effects_test_pixel(expected)
            renpy.hide("zoom_probe")
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
        for effect in (0, 2, 3, 4, 9, 11, 12, 13, 14, 15, 17, 18, 19, 24, 28):
            lex = renpy.lexer.Lexer([("effects-test", 1,
                "20 200 100 %d 0 'object'" % effect, [])])
            lex.advance()
            execute_oload(parse_oload(lex))
            assert isinstance(store.layer_info[20], RScriptText)
            assert store.layer_pos[20] == (200, 100)
            execute_cls(type("Args", (), {"Layer": 20, "Effect": effect})())
            assert 20 not in store.layer_info and 20 not in store.layer_pos
        assert not store.in_queue and not store.draw_queue and not store.draw_queue_delayed
        print("OK: native object effects, queued execution, white fade, 16-pixel grid wipe and mask inversion")
        renpy.quit()
