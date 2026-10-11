define config.name = "KagerouTouryuuki"
define config.save_directory = "KagerouTouryuuki-rscript2renpy"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True

default persistent.kagerou_direction = 1
default persistent.kagerou_size = 0
default persistent.kagerou_snap = 0
default persistent.kagerou_shadow = 0
default persistent.kagerou_text_focus = 0
default persistent.kagerou_character_focus = 0
default persistent.kagerou_inactive_style = 0
default persistent.kagerou_opacity_migrated = False

init -100 python:
    # 41e5b0 / 450630: native update loops use millisecond waits.
    rscript_update_timing = "codex-ms"
    rscript_base_text_size = 24
    rscript_inline_base_size = 24
    rscript_native_text_metrics = True
    rscript_initial_folders = dict.fromkeys(range(100), "grpo")
    # 41fbaf..41fbc8: folder 0 changes the resource directory of every object.
    rscript_folder_zero_all = True
    rscript_voice_groups = True
    # 41e800 -> 405cb0 binds the loaded object's hit region independently of setlink.
    rscript_click_link_is_preview = True
    rscript_voice_format = "voice/%05d.ogg"
    rscript_bgm_format = "bgm/Track%02d.ogg"
    rscript_se_format = "wav/%04d.ogg"

init python:
    # 42fd4c -> 431070: the reading pane starts at opacity 128, not 255.
    rscript_ui.update({"textbox_size": (800, 600), "game_text_settings": False,
                       "textbox_opacity": 128 / 255.0})
    # 4042ac keeps new's origin; 404a1c loads dat_new rather than the placeholder.
    rscript_grps_layout["saveconf"].setdefault("images", {})["new"] = ("grps/dat_new.png", None)
    def kagerou_init_textbox():
        if not persistent.kagerou_opacity_migrated:
            if persistent.rscript_textbox_opacity == 1.0:
                persistent.rscript_textbox_opacity = rscript_ui["textbox_opacity"]
            persistent.kagerou_opacity_migrated = True
            renpy.save_persistent()
        kagerou_apply_text_settings()
        # 42c2be..42c2d6: the reading pane's screen origin.
        store.rscript_compane_position = (585, 572)
    config.start_callbacks.append(kagerou_init_textbox)
