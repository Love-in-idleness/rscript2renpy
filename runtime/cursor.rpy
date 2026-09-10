init -999 python:
    if renpy.loadable("gui/rscript_cursor.png"):
        config.mouse = {
            "default": [("gui/rscript_cursor.png", 0, 0)],
        }
