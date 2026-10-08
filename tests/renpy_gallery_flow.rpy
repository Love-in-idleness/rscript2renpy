# Run by test_modern_port.py SDK PREPARED_RESOURCES; never uses formal saves.
python early:
    def check_gallery_flow():
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        renpy.display.scenelists.init_layers()
        renpy.game.context().scene_lists = renpy.display.scenelists.SceneLists(None, renpy.game.context().images)
        renpy.display.screen.prepare_screens()
        class Finished(BaseException):
            pass
        class Failed(BaseException):
            pass
        def fail_fast(traceback):
            raise Failed(str(traceback))
        old_handler = config.exception_handler
        config.exception_handler = fail_fast
        old_screen, old_pause, old_with = renpy.call_screen, renpy.pause, renpy.with_statement
        old_play, old_stop = renpy.music.play, renpy.music.stop
        old_save = renpy.save
        try:
            renpy.pause = lambda *a, **kw: None
            renpy.with_statement = lambda *a, **kw: None
            renpy.music.play = lambda *a, **kw: None
            renpy.music.stop = lambda *a, **kw: None
            renpy.save = lambda *a, **kw: None  # Command mode has no rollback log.
            for scene in ("0201", "0301"):
                for key in range(7000, 20000):
                    _r[key] = 1  # Unlock disposable test thumbnails.
                _r[201] = 0
                _r[100] = 1101
                steps = []
                def click(name, **kwargs):
                    steps.append(name)
                    assert len(steps) <= 6, steps
                    if name == "rscript_locmap_screen":
                        assert store.layer_info.get(CG_LAYER, "").startswith("grpe "), store.layer_info
                        return 1 if steps.count(name) == 1 else 0
                    assert name == "rscript_click_screen", name
                    assert all(renpy.has_image(item[0]) for item in kwargs["previews"].values())
                    values = [item[0] for item in kwargs["options"]]
                    if len(steps) == 1:
                        assert 1 in values, values
                        return 1 if scene == "0201" else 99
                    if scene == "0201" and steps[-2] == "rscript_locmap_screen":
                        assert store.layer_info[CG_LAYER] == "grpe 9001"
                        return 99
                    # Named TOP2 entry reached: title image must be present,
                    # at origin, with no stale opaque numeric layer or tone.
                    assert store.layer_info[CG_LAYER] == "grpe 9101", store.layer_info
                    displayable = renpy.game.context().scene_lists.get_displayable_by_tag(CG_LAYER, CG_TAG)
                    assert displayable is not None
                    placement = displayable.get_placement()
                    assert all(value in (None, 0) for value in placement[:2]), placement
                    assert displayable.alpha == 1.0
                    assert not store.tone_level, store.tone_level
                    assert not ({47, 48, 49} & set(store.layer_info)), store.layer_info
                    assert all(image.startswith("grpo ") for layer, image in store.layer_info.items()
                               if isinstance(layer, int)), store.layer_info
                    assert 6 in values and 7 in values, values  # Extras, not TOP1.
                    raise Finished()
                renpy.call_screen = click
                try:
                    renpy.call_in_new_context("_" + scene)
                except Finished:
                    pass
                else:
                    raise AssertionError("gallery did not return to title")
                assert steps.count("rscript_locmap_screen") == (2 if scene == "0201" else 0), steps
                print("OK: native gallery script flow", scene, steps)
        finally:
            config.exception_handler = old_handler
            renpy.call_screen, renpy.pause, renpy.with_statement = old_screen, old_pause, old_with
            renpy.music.play, renpy.music.stop = old_play, old_stop
            renpy.save = old_save
        return False
    renpy.arguments.register_command("galleryflowtest", check_gallery_flow)
