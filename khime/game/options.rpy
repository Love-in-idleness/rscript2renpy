define config.name = "Khime Kusaritop"
define config.version = "0.1"
define config.save_directory = "KhimeKusaritop-rscript2renpy"
define config.window_icon = "icon.png"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True

# Install Khime defaults before the shared defaults; retain saved preferences.
init offset = -130
default persistent.rscript_text_size = 29
default persistent.rscript_say_line_chars = 21
default persistent.rscript_line_spacing = -5
init offset = 0

init -100 python:
    rscript_base_text_size = 29
    rscript_inline_base_size = 29
    rscript_voice_format = "voice/%04d.ogg"
    rscript_bgm_format = "bgm/Track%02d.ogg"
    rscript_se_format = "wav/%04d.ogg"
    rscript_ctc_x = 729  # 24px wait00, 8px gap before the 39px control panel.
    rscript_ctc_y = 556
