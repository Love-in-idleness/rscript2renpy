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
            store._preferences.afm_time = 0
            store._preferences.wait_voice = False
            auto = widget("auto").action
            assert not renpy.is_selected(auto)
            renpy.run(auto)
            assert store._preferences.afm_enable and renpy.is_selected(auto)
            assert store._preferences.afm_time == 10
            assert store._preferences.wait_voice

            # Exercise the real native timer, not just the toggle state.
            import pygame_sdl2 as pygame
            behavior = renpy.display.behavior.SayBehavior(afm="sample dialogue")
            event = pygame.event.Event(renpy.display.core.TIMEEVENT, modal=False)
            old_callback = store.rscript_native_afm_callback
            old_playing = renpy.music.is_playing
            playing = set()
            try:
                assert config.afm_callback == rscript_auto_ready
                store.rscript_native_afm_callback = lambda: True
                renpy.music.is_playing = lambda channel="music": channel in playing
                assert not renpy.music.channel_defined("rscript_voice")
                assert behavior.event(event, 0, 0, 0) is None
                assert behavior.event(event, 0, 0, 100) is True
                playing.add("voice")
                assert behavior.event(event, 0, 0, 100) is None
                playing.clear()
                renpy.game.context().init_phase = True
                try:
                    renpy.music.register_channel("rscript_voice", mixer="voice", loop=False)
                finally:
                    renpy.game.context().init_phase = False
                playing.add("rscript_voice")  # Forest's separate channel.
                assert behavior.event(event, 0, 0, 100) is None
                playing.clear()
                playing.add("music")  # Looping BGM must not block dialogue.
                assert behavior.event(event, 0, 0, 100) is True
                store.rscript_native_afm_callback = lambda: False
                assert behavior.event(event, 0, 0, 100) is None
                store.rscript_native_afm_callback = lambda: True
                renpy.run(auto)
                assert behavior.event(event, 0, 0, 100) is None
            finally:
                store.rscript_native_afm_callback = old_callback
                renpy.music.is_playing = old_playing
            assert not store._preferences.afm_enable
            store._preferences.afm_time = 7
            renpy.run(auto)
            assert store._preferences.afm_time == 7  # Preserve user timing.
            renpy.run(auto)
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
            rscript_take_screenshot()
            rscript_take_screenshot()
            assert captured == [config.screenshot_pattern % n for n in (1, 2)], captured
            assert len(notices) == 2
        finally:
            renpy.screenshot = original_capture
            renpy.invoke_in_main_thread = original_invoke
            renpy.notify = original_notify

        # Check the MediaStore transaction; this is NOT an Android JNI/device test.
        import sys, types, io
        class Values(dict):
            def put(self, key, value):
                self[key] = value
        class Resolver:
            failure = None
            def insert(self, collection, values):
                self.inserted = dict(values)
                self.deleted = False
                self.published = False
                return None if self.failure == "insert" else "content://test/1"
            def openOutputStream(self, uri):
                self.output = Output()
                return None if self.failure == "open" else self.output
            def update(self, uri, values, selection, args):
                assert self.output.closed
                assert values == {"is_pending": 0}
                self.published = True
                return 0 if self.failure == "update" else 1
            def delete(self, uri, selection, args):
                assert uri == "content://test/1"
                self.deleted = True
        resolver = Resolver()
        class Output(io.BytesIO):
            def write(self, data, pass_by_reference=True):
                assert isinstance(data, bytearray) and not pass_by_reference
                if resolver.failure == "write":
                    raise IOError("test write error")
                return super().write(data)
            def close(self):
                if not self.closed:
                    resolver.data = self.getvalue()
                super().close()
        version = types.SimpleNamespace(SDK_INT=29)
        data = b"\x89PNG\r\n\x1a\n\x00\x80\xfftest in-memory capture"
        classes = {
            "org.renpy.android.PythonSDLActivity": types.SimpleNamespace(
                mActivity=types.SimpleNamespace(getContentResolver=lambda: resolver)),
            "android.provider.MediaStore$Images$Media": types.SimpleNamespace(
                EXTERNAL_CONTENT_URI="content://test"),
            "android.os.Build$VERSION": version,
            "android.content.ContentValues": Values,
            "java.lang.Integer": int,
        }
        old_jnius = sys.modules.get("jnius")
        old_android = renpy.android
        old_bytes_capture = renpy.screenshot_to_bytes
        sys.modules["jnius"] = types.SimpleNamespace(autoclass=classes.__getitem__, cast=lambda name, obj: obj)
        try:
            assert rscript_publish_screenshot(data, "test.png") == "content://test/1"
            assert resolver.data == data
            assert resolver.inserted["is_pending"] == 1
            assert resolver.inserted["relative_path"] == "Pictures/RScript"
            assert resolver.published and not resolver.deleted
            for failure in ("insert", "open", "write", "update"):
                resolver.failure = failure
                try:
                    rscript_publish_screenshot(data, "test.png")
                    assert False, failure
                except IOError:
                    pass
                assert resolver.deleted == (failure != "insert")
                if failure in ("write", "update"):
                    assert resolver.output.closed
            renpy.notify = notices.append
            renpy.android = True
            renpy.screenshot_to_bytes = lambda size: data
            def forbid_disk_capture(filename):
                raise AssertionError("Android must not call file-based Screenshot")
            renpy.screenshot = forbid_disk_capture
            renpy.invoke_in_main_thread = lambda fn: fn()
            before = set(os.listdir(os.path.join(config.savedir, "screenshots")))
            rscript_take_screenshot()
            assert "No image was saved" in notices[-1]
            resolver.failure = None
            rscript_take_screenshot()
            assert "saved to Gallery" in notices[-1]
            assert resolver.data == data
            assert before == set(os.listdir(os.path.join(config.savedir, "screenshots")))
            renpy.screenshot_to_bytes = lambda size: None
            rscript_take_screenshot()
            assert "No image was saved" in notices[-1]
            version.SDK_INT = 28
            assert rscript_publish_screenshot(data, "test.png") == "content://test/1"
            assert "relative_path" not in resolver.inserted
            assert "is_pending" not in resolver.inserted
            assert resolver.data == data
        finally:
            renpy.android = old_android
            renpy.screenshot_to_bytes = old_bytes_capture
            renpy.screenshot = original_capture
            renpy.invoke_in_main_thread = original_invoke
            renpy.notify = original_notify
            if old_jnius is None:
                del sys.modules["jnius"]
            else:
                sys.modules["jnius"] = old_jnius
        print("OK: touch/Auto, screenshot action/paths, gallery transaction/cleanup/notifications")
        return False
    renpy.arguments.register_command("touchtest", check_touch_controls)

label start:
    scene expression Solid("#234567")
    show text "Native screenshot pixel capture test"
    $ renpy.pause(0.2, hard=True)
    $ rscript_take_screenshot()
    $ renpy.pause(0.5, hard=True)
    python:
        filename = config.screenshot_pattern % 1
        with open(filename, "rb") as captured:
            assert captured.read(8) == b"\x89PNG\r\n\x1a\n"
        assert os.path.getsize(filename) > 100
        import pygame_sdl2 as pygame
        import io
        pixels = pygame.image.load(filename)
        assert tuple(pixels.get_at((10, 10)))[:3] == (35, 69, 103)
        data = renpy.screenshot_to_bytes(None)
        memory_pixels = pygame.image.load(io.BytesIO(data), "capture.png")
        assert tuple(memory_pixels.get_at((10, 10)))[:3] == (35, 69, 103)
        print("OK: real renderer -> native Screenshot -> PNG file (%d bytes)" % os.path.getsize(filename))
    $ renpy.quit()
