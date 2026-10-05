# Generic CodeX/RScript entry point. Replace this file only when the source
# game uses a different boot scene.
label splashscreen:
    scene onlayer master
    scene black onlayer black
    python:
        for number in rscript_boot_movies:
            renpy.movie_cutscene("mov/%04d.mpg" % number)
    return

label start:
    scene onlayer master
    scene black onlayer black
    call _0000
    return

label main_menu:
    # Returning lets Ren'Py enter start in the game context, with rollback enabled.
    return
