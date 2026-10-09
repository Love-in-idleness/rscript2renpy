define config.name = "CannonBall"
define config.save_directory = "CannonBall-rscript2renpy"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True

init -130 python:
    if persistent.rscript_text_size is None:
        persistent.rscript_text_size = 29
    if persistent.rscript_line_spacing is None:
        persistent.rscript_line_spacing = -5

# scr/0101.tsc: 29px body, nameplate indent 200, textbox starts at y=465.
init -100 python:
    rscript_initial_folders = {number: "grpo" for number in range(100)}
    rscript_screen_size = (800, 600)
    rscript_base_text_size = 29
    rscript_inline_base_size = 29
    rscript_use_speaker_images = True
    rscript_voice_format = "voice/%04d.ogg"
    rscript_voice_groups = True
    # Cannonball.exe 41096e: click clock register counts 10 ms ticks.
    rscript_click_timer_unit = .01
    rscript_locmode_zero_all = True
    rscript_bgm_format = "bgm/Track%02d.wav"
    rscript_ctc_x, rscript_ctc_y = 770, 555
    rscript_ui = {"show_speaker": True, "speaker_pos": (0, 7),
                  "textbox_size": (800, 135),
                  "textbox_background": "grps/TBOX%02dB.png",
                  "game_text_settings": False,
                  "restricted_image_folders": ("grpo_r1", "grpo_rc"),
                  "wait_image": "grps tbox_w"}
