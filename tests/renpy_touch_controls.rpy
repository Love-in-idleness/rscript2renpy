define gui.interface_text_font = "DejaVuSans.ttf"
default roll_enabled = 1
default menu_enabled = 1

python early:
    def check_touch_controls():
        import os
        renpy.execute_default_statement(True)
        renpy.game.context().init_phase = False
        assert config.overlay_screens.count("rscript_touch_controls") == 1
        assert "K_AC_BACK" not in config.keymap["rollback"]
        assert "K_AC_BACK" in config.keymap["game_menu"]
        assert config.screenshot_pattern == os.path.join(
            config.savedir, "screenshots", "screenshot%04d.png")

        original_variant = renpy.variant
        renpy.variant = lambda name: name == "touch"
        def widget(name):
            renpy.hide_screen("rscript_touch_controls")
            renpy.show_screen("rscript_touch_controls")
            screen = renpy.get_screen("rscript_touch_controls")
            screen.update()
            buttons = {}
            def collect(displayable):
                if isinstance(displayable, renpy.display.behavior.Button):
                    buttons["".join(displayable.child.text).lower()] = displayable
            screen.visit_all(collect)
            return buttons.get(name)
        try:
            for name in ("back", "skip", "auto", "hide", "screenshot", "menu"):
                assert widget(name) is not None, name
            assert widget("back").is_sensitive()
            assert widget("menu").is_sensitive()
            store.roll_enabled = store.menu_enabled = 0
            assert not widget("back").is_sensitive()
            assert not widget("menu").is_sensitive()
            store.roll_enabled = store.menu_enabled = 1
            store.rscript_touch_locked = lambda: True
            assert not widget("back").is_sensitive()
            assert not widget("menu").is_sensitive()
            assert widget("screenshot").is_sensitive()
            store._preferences.afm_enable = False
            auto = widget("auto").action
            assert not auto.get_selected()
            auto()
            assert store._preferences.afm_enable and auto.get_selected()
            auto()
            assert not store._preferences.afm_enable
            store._menu = True
            assert widget("auto") is None
            store._menu = False
            renpy.variant = lambda name: False
            assert widget("auto") is None
        finally:
            renpy.variant = original_variant
            renpy.hide_screen("rscript_touch_controls")

        # Run the native action and file naming code, mock only pixel capture.
        original_capture = renpy.screenshot
        original_invoke = renpy.invoke_in_main_thread
        original_notify = renpy.notify
        captured, notices = [], []
        def capture(path):
            captured.append(path)
            with open(path, "wb") as output:
                output.write(b"test capture, not image pixels")
            return True
        try:
            renpy.screenshot = capture
            renpy.invoke_in_main_thread = lambda fn: fn()
            renpy.notify = notices.append
            Screenshot()()
            Screenshot()()
            assert captured == [config.screenshot_pattern % n for n in (1, 2)], captured
            assert len(notices) == 2
        finally:
            renpy.screenshot = original_capture
            renpy.invoke_in_main_thread = original_invoke
            renpy.notify = original_notify
        print("OK: touch buttons, menu/scene locks, Auto, native screenshot action and paths")
        return False
    renpy.arguments.register_command("touchtest", check_touch_controls)

label start:
    return
