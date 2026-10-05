init offset = 10
init -100 python:
    rscript_voice_format = "voice/%04d.ogg"
    rscript_bgm_format = "bgm/Track%02d.ogg"
    rscript_se_format = "wav/%04d.ogg"
    rscript_ctc_x = 747
    rscript_ctc_y = 556

style default:
    font "fonts/NotoSansCJKjp-Regular.otf"

default forest_choice_prompt = ""
default forest_input_locked = False
init -90 python:
    rscript_use_speaker_images = True
    rscript_folder_zero_all = True
    rscript_click_grid = True

init python:
    # Aliases retained for history and older generated scripts.
    config.self_closing_custom_text_tags["forest_g"] = rscript_g_tag
    config.self_closing_custom_text_tags["forest_a"] = rscript_a_tag

    rscript_boot_movies = (2, 1)
    rscript_ui.update({
        "selected_plain_folders": ("confscrn",),
        "activate_sound": {"confscrn": "wav/0001.ogg", "savescrn": "wav/0001.ogg"},
        "title_wiki": False,
        "numeric_choices": True,
        "compane_hide_auto": True,
        "compane_invert": True,
        "compane_track": (4, 2, 75, 14),
        "compane_bar_background": True,
        "slot_size": (257, 62),
        "slot_date_pos": (114, 38),
        "slot_date_color": "#3b2410",
        "choice_size": (505, 82),
        "choice_spacing": -4,
        "choice_yalign": 0.4,
        "choice_text_pos": (48, 0),
        "choice_text_yalign": 0.46,
        "choice_text_size": 21,
        "choice_outlines": [(2, "#18220d", 0, 0)],
        "prompt_size": (505, 48),
        "prompt_text_pos": (35, 0),
        "prompt_text_yalign": 0.45,
        "prompt_text_size": 20,
        "prompt_text_color": "#2a2015",
        "choice_center_art": True,
    })

    def forest_migrate_preferences():
        if getattr(persistent, "rscript_forest_preferences_migrated", False):
            return
        for name in ("text_size", "say_line_chars", "oload_line_chars",
                     "line_spacing", "text_cps", "text_font", "wiki_mode",
                     "progress_backup", "previous_default_font"):
            value = getattr(persistent, "forest_" + name, None)
            if value is not None:
                setattr(persistent, "rscript_" + name, value)
        persistent.rscript_forest_preferences_migrated = True
        renpy.save_persistent()

    # Run the migration before the shared default-font upgrade.
    config.start_callbacks.insert(0, forest_migrate_preferences)

    def rscript_touch_locked():
        return store.forest_input_locked

screen forest_title_preferences():
    tag menu
    use rscript_title_preferences

screen choice(items):
    use rscript_choice(items, forest_choice_prompt)

python early:
    register_rscript_ui_aliases("forest")
