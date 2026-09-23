define config.name = "Khime Kusaritop"
define config.version = "0.1"
define config.save_directory = "KhimeKusaritop-rscript2renpy"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True

init -100 python:
    rscript_voice_format = "voice/%04d.ogg"
    rscript_bgm_format = "bgm/Track%02d.ogg"
    rscript_se_format = "wav/%04d.ogg"
    rscript_ctc_x = 747
    rscript_ctc_y = 556
