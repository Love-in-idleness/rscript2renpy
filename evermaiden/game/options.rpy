define config.name = "Evermaiden"
define config.save_directory = "Evermaiden-shared-rscript2renpy"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True

init -130 python:
    if persistent.rscript_text_size is None:
        persistent.rscript_text_size = 32
    if persistent.rscript_say_line_chars is None:
        persistent.rscript_say_line_chars = 28

# scr/0500.tsc specifies 32px text and an 898px body area on a 1280x720 canvas.
init -100 python:
    rscript_screen_size = (1280, 720)
    rscript_base_text_size = 32
    rscript_inline_base_size = 32
    rscript_voice_format = "voice/%04d.ogg"
    rscript_voice_groups = True
    rscript_folder_zero_all = True
    rscript_click_grid = True
    rscript_bgm_format = "bgm/Track%02d.ogg"
    rscript_se_format = "wav/%04d.ogg"
    rscript_ctc_x = 1080
    rscript_ctc_y = 638
    rscript_ui = {"show_speaker": True, "speaker_pos": (124, 17),
                  "text_pos": (188, 58), "textbox_size": (1280, 217)}
