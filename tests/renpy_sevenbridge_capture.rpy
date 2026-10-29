# Disposable visual check; the runner isolates both saves and generated scripts.
default sevenbridge_capture_stage = 0
default sevenbridge_drag_stage = 0
default sevenbridge_drag_dialogue = None
default sevenbridge_language_stage = 0

init python:
    def sevenbridge_capture_error(short, full, info):
        raise SystemExit(full)
    config.exception_handler = sevenbridge_capture_error
    config.overlay_screens.append("sevenbridge_capture_timer")

    def sevenbridge_capture_tick():
        stage = store.sevenbridge_capture_stage
        if stage == 0 and (not renpy.get_screen("rscript_click_screen") or
                           store.layer_info.get(CG_LAYER) != "grpe 3001"):
            return
        if stage == 1 and not store.last_say:
            return
        if stage == 1:
            step = store.sevenbridge_drag_stage
            if step == 0:
                store.sevenbridge_drag_dialogue = store.last_say
            if store.sevenbridge_language_stage == 0:
                assert store.last_say == store.sevenbridge_drag_dialogue, "opacity drag advanced dialogue"
            if step == 3:
                assert persistent.rscript_textbox_opacity < .05, persistent.rscript_textbox_opacity
            if step < 6:
                import pygame_sdl2 as pygame
                focus = next(f for f in renpy.display.focus.focus_list
                             if isinstance(f.widget, renpy.display.behavior.Bar))
                assert focus.widget.style.bar_vertical
                x = int(focus.x + focus.w / 2)
                y = int(focus.y + (focus.h / 2 if step == 0 else
                                  focus.h - 1 if step < 4 else 1))
                renpy.set_mouse_pos(x, y)
                pos = renpy.display.draw.untranslate_point(x, y)
                pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=pos,
                                  rel=(0, 0), buttons=(1 if step in (1, 4) else 0, 0, 0)))
                if step in (0, 2, 3, 5):
                    event = pygame.MOUSEBUTTONDOWN if step in (0, 3) else pygame.MOUSEBUTTONUP
                    pygame.event.post(pygame.event.Event(event, pos=pos, button=1))
                store.sevenbridge_drag_stage += 1
                return
            assert persistent.rscript_textbox_opacity > .95
            print("OK: SevenBridge opacity drags down/up without advancing dialogue")
            if any(language == "zh" for language, _ in rscript_languages):
                language_step = store.sevenbridge_language_stage
                if language_step < 2:
                    if language_step == 1:
                        assert "越えてゆけ" in "".join(renpy.get_widget("say", "what").text)
                    store.sevenbridge_language_stage += 1
                    renpy.run(Language(None if language_step == 0 else "zh"))
                    return
                assert "跨过去吧" in "".join(renpy.get_widget("say", "what").text)
                print("OK: displayed dialogue switches Japanese/Chinese without advancing")
        destination = os.environ["SEVENBRIDGE_CAPTURE"]
        names = ("title.png", "dialogue.png", "preferences.png", "save.png", "load.png")
        renpy.screenshot(os.path.join(destination, names[stage]))
        store.sevenbridge_capture_stage += 1
        if stage == 0:
            renpy.hide_screen("rscript_click_screen")
            renpy.jump("_0100")
        elif stage == 1:
            renpy.show_screen("preferences")
        elif stage == 2:
            renpy.hide_screen("preferences")
            renpy.take_screenshot()
            FilePage(1)()
            FileSave(1, confirm=False)()
            assert FileJson(1, key="rscript_dt2") == 1
            assert rscript_slot_image(1) == rscript_image_path("grps/dt2_0001.png")
            renpy.show_screen("save")
        elif stage == 3:
            renpy.hide_screen("save")
            renpy.show_screen("load")
        else:
            renpy.quit()
        renpy.restart_interaction()

screen sevenbridge_capture_timer():
    zorder 500
    timer 3.0 repeat True action Function(sevenbridge_capture_tick)
