# Shared text, fonts, Wiki links and persistent progress for RScript ports.
init offset = -120
define rscript_base_text_size = 22
define rscript_inline_base_size = 22
define rscript_use_speaker_images = False
default rscript_speaker_images_override = False
default persistent.rscript_text_size = rscript_base_text_size
default persistent.rscript_line_spacing = 7
default persistent.rscript_text_cps = 20
define rscript_default_font = "fonts/NotoSansCJKjp-Regular.otf"
default persistent.rscript_text_font = rscript_default_font
default persistent.rscript_previous_default_font = "fonts/simhei.ttf"
default persistent.rscript_wiki_mode = False
default persistent.rscript_progress_backup = None
define rscript_languages = [(None, "Original")]
define rscript_wiki_keywords = {}
define rscript_wiki_images = {}

init offset = 0
default rscript_speaker = None
default rscript_speaker_visible = False

init python:
    def rscript_prepare_text(text):
        text = renpy.translation.translate_string(text)
        text = rscript_prepare_wiki_text(text)
        if rscript_use_speaker_images or rscript_speaker_images_override:
            speaker = renpy.re.match(r"^\^g(\d{3})", text, flags=renpy.re.I)
            if speaker:
                store.rscript_speaker = int(speaker.group(1))
                text = text[speaker.end():]
        return rscript_inline_graphics(text)

    def rscript_green_color():
        if _preferences.language not in rscript_wiki_keywords:
            return getattr(store, "rscript_text_colors", {}).get("g", "#FFFFFF")
        return ("#D7FFB3" if persistent.rscript_wiki_mode and
                _preferences.language in rscript_wiki_keywords else "#FFFFFF")

    def rscript_menu_text(text):
        # A menu's leading ^g is inline artwork, not a dialogue nameplate.
        text = rscript_inline_graphics(renpy.substitute(text))
        return parse_rscript_text(repr(text), True)[0]

    def rscript_dialogue_begin(append=False):
        if not append:
            store.rscript_speaker = None
        store.rscript_speaker_visible = True

    def rscript_dialogue_end():
        store.rscript_speaker_visible = False

    def rscript_open_game_menu():
        if store.menu_enabled and not rscript_touch_locked():
            renpy.run(ShowMenu("preferences"))

    config.game_menu_action = Function(rscript_open_game_menu)
init python:
    def rscript_update_default_font():
        # Upgrade the old default once; retain other user font choices.
        if persistent.rscript_previous_default_font != rscript_default_font:
            if persistent.rscript_text_font == persistent.rscript_previous_default_font:
                persistent.rscript_text_font = rscript_default_font
            persistent.rscript_previous_default_font = rscript_default_font
            renpy.save_persistent()

    config.start_callbacks.append(rscript_update_default_font)

    def rscript_text_settings(kind, base_size):
        size = (persistent.rscript_text_size if kind == "say" else
                max(1, base_size * persistent.rscript_text_size // rscript_base_text_size))
        return (rscript_current_font(), size,
                getattr(persistent, "rscript_%s_line_chars" % kind),
                persistent.rscript_line_spacing)

    def rscript_text_image_path(name):
        return "%s/%s.png" % (rscript_ui.get("text_image_root", "images/grps"), name)

    def rscript_g_tag(tag, argument):
        try:
            number, text_size = argument.split(":", 1)
            zoom = persistent.rscript_text_size / float(rscript_inline_base_size)
            zoom *= rscript_ui.get("inline_zoom", 1.0)
        except (AttributeError, TypeError, ValueError):
            return []
        path = rscript_text_image_path("gf%s" % number)
        if not renpy.loadable(path):
            renpy.log("RScript: missing inline name image gf%s" % number)
            return []
        image = Transform(path, zoom=zoom)
        return [(renpy.TEXT_DISPLAYABLE, image)]

    def rscript_a_tag(tag, argument):
        try:
            number, text_size = argument.split(":", 1)
            zoom = persistent.rscript_text_size / float(rscript_inline_base_size)
            zoom *= rscript_ui.get("inline_zoom", 1.0)
        except (AttributeError, TypeError, ValueError):
            return []
        wiki_enabled = (persistent.rscript_wiki_mode and
                        _preferences.language in rscript_wiki_keywords)
        prefix = "gg" if wiki_enabled else "gf"
        path = rscript_text_image_path(prefix + number)
        if not renpy.loadable(path):
            renpy.log("RScript: missing inline Wiki image %s%s" % (prefix, number))
            return []
        image = Transform(path, zoom=zoom)
        if wiki_enabled:
            url = rscript_wiki_images.get(
                _preferences.language, {}).get(number)
            if url:
                image = renpy.display.behavior.ImageButton(
                    image, image, clicked=OpenURL(url), focus_mask=True)
        return [(renpy.TEXT_DISPLAYABLE, image)]

    def rscript_inline_graphics(text):
        text = renpy.re.sub(
            r"\^g(\d{3})",
            lambda match: "{rscript_g=%s:%d}" %
            (match.group(1), persistent.rscript_text_size), text, flags=renpy.re.I)
        return renpy.re.sub(
            r"\^a(\d{3})",
            lambda match: "{rscript_a=%s:%d}" %
            (match.group(1), persistent.rscript_text_size), text, flags=renpy.re.I)

    config.self_closing_custom_text_tags["rscript_g"] = rscript_g_tag
    config.self_closing_custom_text_tags["rscript_a"] = rscript_a_tag

    def rscript_adjust_text(name, delta, low, high):
        value = max(low, min(high, getattr(persistent, name) + delta))
        setattr(persistent, name, value)
        renpy.save_persistent()

    def rscript_fonts():
        return sorted(name for name in renpy.list_files()
                      if name.startswith("fonts/") and
                      name.lower().endswith((".ttf", ".otf", ".ttc")))

    def rscript_current_font():
        fonts = rscript_fonts()
        if persistent.rscript_text_font in fonts:
            return persistent.rscript_text_font
        if rscript_default_font in fonts:
            return rscript_default_font
        return fonts[0] if fonts else gui.text_font

    def rscript_font_name():
        return rscript_current_font().rsplit("/", 1)[-1]

    def rscript_cycle_font(step):
        fonts = rscript_fonts()
        if not fonts:
            return
        try:
            index = fonts.index(persistent.rscript_text_font)
        except ValueError:
            index = -1 if step > 0 else 0
        persistent.rscript_text_font = fonts[(index + step) % len(fonts)]
        renpy.save_persistent()

    def rscript_set_wiki(enabled):
        persistent.rscript_wiki_mode = enabled
        renpy.save_persistent()

    def rscript_wiki_plain(text):
        text = renpy.re.sub(r"\^g\d{3}", "", text)
        text = renpy.re.sub(r"\^a\d{3}", "", text)
        text = renpy.re.sub(r"\^c[bgkopsrvwy]|\^f[mg]", "", text, flags=renpy.re.I)
        text = text.replace("^n", "")
        return renpy.re.sub(r"\^[bisdmw]\d*", "", text)

    def rscript_prepare_wiki_text(text):
        if not persistent.rscript_wiki_mode:
            return text
        entries = rscript_wiki_keywords.get(_preferences.language, ())
        if not entries:
            return text
        plain = rscript_wiki_plain(text)

        def link_green(match):
            marked = match.group(1)
            visible = rscript_wiki_plain(marked)
            for sentence, url, link_text in entries:
                if visible and sentence in plain and (link_text in visible or
                                                      visible in link_text):
                    linked = "{a=%s}{color=#D7FFB3}%s{/color}{/a}" % \
                        (url, marked)
                    return "^cg" + linked
            return match.group(0)

        return renpy.re.sub(
            r"\^cg(.*?)(?=\^c[ygwk]|$)", link_green, text)

    def rscript_save_progress():
        persistent.rscript_progress_backup = {
            "reg": dict(persistent._reg),
            "seen_cg": dict(persistent.seen_cg),
        }
        renpy.save_persistent()
        renpy.notify("Progress backup saved.")

    def rscript_load_progress():
        data = persistent.rscript_progress_backup
        if data is None:
            renpy.notify("No progress backup is available.")
            return
        persistent._reg = dict(data["reg"])
        persistent.seen_cg = dict(data["seen_cg"])
        renpy.save_persistent()
        renpy.notify("Progress backup restored.")

    def rscript_clear_progress():
        persistent._reg = {}
        persistent.seen_cg = {}
        renpy.save_persistent()
        renpy.notify("Persistent progress cleared (backup kept).")

    config.say_menu_text_filter = renpy.translation.translate_string

screen rscript_text_preferences(wiki=True):
    tag menu
    modal True
    key "game_menu" action Return()

    add Solid("#000000b0")
    frame:
        background Solid("#080808e8")
        xalign 0.5
        yalign 0.5
        xsize 640
        xpadding 32
        ypadding 14
        vbox:
            xfill True
            spacing 3
            text "Text Display":
                size 26
                xalign 0.5
            fixed:
                xfill True
                ysize 34
                text "Text Size" yalign 0.5
                hbox:
                    xalign 1.0
                    yalign 0.5
                    spacing 10
                    text "[persistent.rscript_text_size]":
                        min_width 48
                        text_align 0.5
                    textbutton "-" action Function(
                        rscript_adjust_text, "rscript_text_size", -1, 14, 40)
                    textbutton "+" action Function(
                        rscript_adjust_text, "rscript_text_size", 1, 14, 40)
            fixed:
                xfill True
                ysize 34
                text "Dialogue Characters per Line" yalign 0.5
                hbox:
                    xalign 1.0
                    yalign 0.5
                    spacing 10
                    text "[persistent.rscript_say_line_chars]":
                        min_width 48
                        text_align 0.5
                    textbutton "-" action Function(
                        rscript_adjust_text, "rscript_say_line_chars", -1, 10, 40)
                    textbutton "+" action Function(
                        rscript_adjust_text, "rscript_say_line_chars", 1, 10, 40)
            fixed:
                xfill True
                ysize 34
                text "Overlay Characters per Line" yalign 0.5
                hbox:
                    xalign 1.0
                    yalign 0.5
                    spacing 10
                    text "[persistent.rscript_oload_line_chars]":
                        min_width 48
                        text_align 0.5
                    textbutton "-" action Function(
                        rscript_adjust_text, "rscript_oload_line_chars", -1, 10, 40)
                    textbutton "+" action Function(
                        rscript_adjust_text, "rscript_oload_line_chars", 1, 10, 40)
            fixed:
                xfill True
                ysize 34
                text "Line Spacing" yalign 0.5
                hbox:
                    xalign 1.0
                    yalign 0.5
                    spacing 10
                    text "[persistent.rscript_line_spacing]":
                        min_width 48
                        text_align 0.5
                    textbutton "-" action Function(
                        rscript_adjust_text, "rscript_line_spacing", -1, -10, 30)
                    textbutton "+" action Function(
                        rscript_adjust_text, "rscript_line_spacing", 1, -10, 30)
            vbox:
                xfill True
                spacing 4
                text "Font" xalign 0.5
                text "[rscript_font_name()]":
                    size 18
                    xalign 0.5
                hbox:
                    xalign 0.5
                    spacing 16
                    textbutton "Previous Font" action Function(rscript_cycle_font, -1)
                    textbutton "Next Font" action Function(rscript_cycle_font, 1)

            if len(rscript_languages) > 1:
                text "Language" xalign 0.5
                hbox:
                    xalign 0.5
                    spacing 14
                    for language, label in rscript_languages:
                        textbutton label:
                            action Language(language)
                            selected _preferences.language == language

            if wiki and _preferences.language in rscript_wiki_keywords:
                hbox:
                    xalign 0.5
                    spacing 14
                    text "Wiki"
                    textbutton "On" action Function(rscript_set_wiki, True) selected persistent.rscript_wiki_mode
                    textbutton "Off" action Function(rscript_set_wiki, False) selected not persistent.rscript_wiki_mode

            text "Persistent Progress" xalign 0.5
            hbox:
                xalign 0.5
                spacing 14
                textbutton "Save Backup" action Function(rscript_save_progress)
                textbutton "Load Backup" action Function(rscript_load_progress)
                textbutton "Clear Progress":
                    action Confirm(
                        "Clear persistent progress? The backup will be kept.",
                        Function(rscript_clear_progress))
            textbutton "Back":
                xalign 0.5
                action Return()

screen confirm(message, yes_action, no_action):
    modal True
    add Solid("#000000a0")
    frame:
        xalign 0.5
        yalign 0.5
        xpadding 36
        ypadding 26
        vbox:
            spacing 20
            text message:
                substitute False
                xalign 0.5
                text_align 0.5
                color "#ffffff"
            hbox:
                xalign 0.5
                spacing 50
                textbutton "Yes" action yes_action substitute False
                textbutton "No" action no_action substitute False
