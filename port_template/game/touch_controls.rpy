# Shared Android/touch controls. Game adapters may override the lock predicate.
init -1 python:
    import os

    def rscript_touch_locked():
        return False

    def rscript_ensure_auto_delay():
        # Ren'Py's default zero means infinite wait, even with AFM enabled.
        # Keep any nonzero timing selected in the preferences screen.
        if _preferences.afm_time == 0:
            renpy.run(Preference("auto-forward time", 10))
        renpy.run(Preference("wait for voice", "enable"))

    rscript_native_afm_callback = config.afm_callback

    def rscript_auto_ready():
        # Forest bypasses Ren'Py's voice statement on its own voice channel.
        # Only gate Auto: clicks, wheel, Skip and scripted waits stay unchanged.
        for channel in ("voice", "rscript_voice"):
            if renpy.music.channel_defined(channel) and renpy.music.is_playing(channel=channel):
                return False
        return rscript_native_afm_callback is None or rscript_native_afm_callback()

    config.afm_callback = rscript_auto_ready

    if "K_AC_BACK" in config.keymap["rollback"]:
        config.keymap["rollback"].remove("K_AC_BACK")
    if "K_AC_BACK" not in config.keymap["game_menu"]:
        config.keymap["game_menu"].append("K_AC_BACK")
    config.overlay_screens.append("rscript_touch_controls")

    if not renpy.android:
        config.screenshot_pattern = os.path.join(
            config.savedir, "screenshots", "screenshot%04d.png")

    def rscript_publish_screenshot(data, name):
        from jnius import autoclass, cast
        activity = autoclass("org.renpy.android.PythonSDLActivity").mActivity
        resolver = activity.getContentResolver()
        images = autoclass("android.provider.MediaStore$Images$Media")
        modern = autoclass("android.os.Build$VERSION").SDK_INT >= 29
        values = autoclass("android.content.ContentValues")()
        values.put("_display_name", name)
        values.put("mime_type", "image/png")
        if modern:
            integer = autoclass("java.lang.Integer")
            values.put("relative_path", "Pictures/RScript")
            values.put("is_pending", integer(1))
        uri = resolver.insert(images.EXTERNAL_CONTENT_URI, values)
        if uri is None:
            raise IOError("Gallery rejected screenshot")
        try:
            output = resolver.openOutputStream(uri)
            if output is None:
                raise IOError("Cannot open gallery output stream")
            try:
                cast("java.io.OutputStream", output).write(
                    bytearray(data), pass_by_reference=False)
            finally:
                output.close()
            if modern:
                values.clear()
                values.put("is_pending", integer(0))
                if resolver.update(uri, values, None, None) != 1:
                    raise IOError("Cannot publish gallery screenshot")
        except Exception:
            # Remove only this incomplete image, never an existing screenshot.
            resolver.delete(uri, None, None)
            raise
        return str(uri)

    def rscript_android_screenshot():
        from datetime import datetime
        try:
            data = renpy.screenshot_to_bytes(None)
            if not data:
                raise IOError("No rendered frame available")
            name = "screenshot-%s.png" % datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            uri = rscript_publish_screenshot(data, name)
        except Exception as error:
            renpy.log("RScript screenshot failed: %r" % error)
            renpy.notify("Screenshot failed. No image was saved.")
        else:
            renpy.log("RScript screenshot saved to gallery: %s" % uri)
            renpy.notify("Screenshot saved to Gallery / Pictures / RScript.")

    def rscript_take_screenshot():
        if renpy.android:
            renpy.run(config.pre_screenshot_actions)
            renpy.invoke_in_main_thread(rscript_android_screenshot)
        else:
            renpy.run(Screenshot())

screen rscript_touch_controls():
    zorder 200
    if renpy.variant("touch") and not _menu:
        hbox:
            style_prefix "rscript_touch"
            spacing 2
            xalign 0.995
            yalign 0.01

            textbutton "Back" action Rollback() sensitive roll_enabled and not rscript_touch_locked()
            textbutton "Skip" action Skip()
            textbutton "Auto" action [Function(rscript_ensure_auto_delay), Preference("auto-forward", "toggle")]
            textbutton "Hide" action HideInterface()
            textbutton "Screenshot" action Function(rscript_take_screenshot)
            textbutton "Menu" action ShowMenu("preferences") sensitive menu_enabled and not rscript_touch_locked()

style rscript_touch_button:
    xminimum 90
    yminimum 44
    padding (8, 4)
    background Solid("#000000a0")
    hover_background Solid("#586b44d0")
    selected_background Solid("#586b44d0")
    insensitive_background Solid("#00000060")

style rscript_touch_button_text:
    font gui.interface_text_font
    size 17
    color "#ffffff"
    insensitive_color "#888888"
    text_align 0.5
    xalign 0.5
    yalign 0.5
