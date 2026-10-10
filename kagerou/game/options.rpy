define config.name = "KagerouTouryuuki"
define config.save_directory = "KagerouTouryuuki-rscript2renpy"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True

init -130 python:
    for key, value in (("rscript_text_size", 24), ("rscript_say_line_chars", 26),
                       ("rscript_line_spacing", 10)):
        if getattr(persistent, key, None) is None:
            setattr(persistent, key, value)

init -100 python:
    # 430311..430343, 43045c..4304bc: horizontal layout-0/font-preset-0.
    rscript_base_text_size = 24
    rscript_inline_base_size = 24
    rscript_native_text_metrics = True
    rscript_initial_folders = dict.fromkeys(range(100), "grpo")
    rscript_voice_groups = True
    rscript_voice_format = "voice/%05d.ogg"
    rscript_bgm_format = "bgm/Track%02d.ogg"
    rscript_se_format = "wav/%04d.ogg"
    rscript_ctc_x = 752
    rscript_ctc_y = 552

init python:
    rscript_ui.update({"textbox_size": (800, 600)})
    def kagerou_init_textbox():
        rscript_set_textbox(0, box_pos=(0, 0), text_rect=(114, 30, 646, 480),
                           size=24, pitch=(10, 0), ruby=(0, 9, 9))
    config.start_callbacks.append(kagerou_init_textbox)
