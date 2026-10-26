define config.name = "Khime Kusaritop"
define config.save_directory = "KhimeKusaritop-rscript2renpy"
define config.window_icon = "icon.png"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True

# Install Khime defaults before the shared defaults; retain saved preferences.
init -130 python:
    if persistent.rscript_text_size is None:
        persistent.rscript_text_size = 29
    rscript_say_line_chars_default = 21
    rscript_text_line_spacing_default = -5

init -100 python:
    rscript_base_text_size = 29
    rscript_inline_base_size = 29
    rscript_voice_format = "voice/%04d.ogg"
    rscript_bgm_format = "bgm/Track%02d.ogg"
    rscript_se_format = "wav/%04d.ogg"
    rscript_ctc_x = 729  # 24px wait00, 8px gap before the 39px control panel.
    rscript_ctc_y = 556
