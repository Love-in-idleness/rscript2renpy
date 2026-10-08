# Isolated renderer regression, never installed into a player's project.
define config.physical_width = 700
define config.physical_height = 525
init 100 python:
    def sprite_seam_exception(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = sprite_seam_exception
    config.autosave_on_choice = False

    def sprite_seam_capture(name):
        import io
        import pygame_sdl2 as pygame
        data = renpy.screenshot_to_bytes(None)
        image = pygame.image.load(io.BytesIO(data))
        pygame.image.save(image, os.path.join(config.basedir, name + ".png"))
        w, h = image.get_size()
        # Both halves form an opaque white rectangle; no gray seam is valid.
        values = [image.get_at((x, y))[0]
                  for x in range(int(200 * w / 800), int(600 * w / 800))
                  for y in range(int(299 * h / 600), int(304 * h / 600) + 1)]
        if name.startswith("after") and w != 800:
            # Only internal sampling is nearest; final window scaling is smooth.
            edge = [image.get_at((x, int(200 * h / 600)))[0]
                    for x in range(int(100 * w / 800) - 2, int(100 * w / 800) + 3)]
            assert any(0 < value < 255 for value in edge), edge
        return min(values)

label _0000:
    window hide
    scene black onlayer black
    show expression "split_top.png" as top
    show expression "split_bottom.png" as bottom
    $ sprite_seam_transforms = config.layer_transforms.get(None, [])
    $ config.layer_transforms[None] = []
    $ renpy.pause(0.2, hard=True)
    $ seam_before = sprite_seam_capture("before")
    $ assert rscript_native_canvas in sprite_seam_transforms
    $ config.layer_transforms[None] = sprite_seam_transforms
    $ renpy.pause(0.2, hard=True)
    $ seam_after = sprite_seam_capture("after")
    $ assert seam_before < 250, (seam_before, seam_after)
    $ assert seam_after >= 250, (seam_before, seam_after)
    $ print("OK: split sprite seam native framebuffer %d -> %d" % (seam_before, seam_after))
    python:
        for size in ((800, 600), (1000, 750)):
            renpy.set_physical_size(size)
            renpy.pause(0.2, hard=True)
            value = sprite_seam_capture("after-%d" % size[0])
            assert value >= 250, (size, value)
        print("OK: native canvas at 1:1 and enlarged window; final scaling remains smooth")
    hide top
    hide bottom
    show expression Solid("#204060") as scene_background onlayer cg
    show expression Transform(Solid("#000000"), shader="rscript.effect_invert", blend="rscript_invert") as scene_invert
    $ renpy.pause(0.2, hard=True)
    python:
        import io
        import pygame_sdl2 as pygame
        image = pygame.image.load(io.BytesIO(renpy.screenshot_to_bytes(None)))
        actual = image.get_at((20, 20))[:3]
        assert all(abs(a - b) <= 3 for a, b in zip(actual, (223, 191, 159))), actual
        print("OK: native canvas preserves destination inversion across CG/master layers")
    $ renpy.quit()
