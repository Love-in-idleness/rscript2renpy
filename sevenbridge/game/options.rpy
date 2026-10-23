define config.name = "SevenBridge"
define config.save_directory = "SevenBridge-jp-rscript2renpy"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True

init -100 python:
    # SBridge_jp.exe APINI 469740, dispatcher 41cc40 and voice path 41b5b0.
    rscript_screen_size = (800, 600)
    rscript_base_text_size = 24
    rscript_inline_base_size = 24
    rscript_use_speaker_images = True
    rscript_initial_folders = dict.fromkeys(range(100), "grpo")
    rscript_folder_zero_all = True
    rscript_locmode_zero_all = True
    rscript_click_link_is_preview = True
    rscript_click_native_effects = True
    rscript_update_timing = "codex-ms"
    rscript_voice_format = "voice/%04d.ogg"
    rscript_voice_groups = True
    rscript_bgm_format = "bgm/Track%02d.ogg"
    # 41fcc0 records CGs >=1000 only in the separate progress bit bank.
    rscript_cg_register_limit = 1000
    rscript_se_format = "wav/%04d.ogg"
    rscript_ctc_x, rscript_ctc_y = 690, 572
    rscript_ui = {"show_speaker": True, "speaker_pos": (0, 11),
                  "text_pos": (147, 11), "textbox_size": (800, 130),
                  "textbox_opacity": 128 / 255.0,
                  "selected_plain_folders": ("confscrn",)}

init -130 python:
    if persistent.rscript_text_size is None:
        persistent.rscript_text_size = 24
    if persistent.rscript_say_line_chars is None:
        persistent.rscript_say_line_chars = 22

init python:
    def sevenbridge_initial_textbox():
        # tbox00 metadata: 800x130 canvas, text at (0,11), 146px gf nameplate.
        store.cur_textbox = 0
        store.text_indent = 146
    config.start_callbacks.append(sevenbridge_initial_textbox)
