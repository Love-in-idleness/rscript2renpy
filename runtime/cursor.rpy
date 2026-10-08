init -999 python:
    if renpy.loadable("engine/gui/rscript_cursor.png"):
        config.mouse = {
            "default": [("engine/gui/rscript_cursor.png", 0, 0)],
        }
