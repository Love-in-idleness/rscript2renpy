define config.name = "Forest"
define config.save_directory = "Forest-rscript2renpy"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True
init -100 python:
    rscript_colormode_limit = 6
    rscript_move4_timing = "fixed-steps"
