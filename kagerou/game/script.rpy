label splashscreen:
    scene onlayer master
    scene black onlayer black
    python:
        if not renpy.session.get("kagerou_boot_movies", False):
            renpy.session["kagerou_boot_movies"] = True
            for number in rscript_boot_movies:
                filename = "mov/%04d.mpg" % number
                if renpy.loadable(filename):
                    renpy.movie_cutscene(filename)
    return

label start:
    scene onlayer master
    scene black onlayer black
    call _0000
    return

label main_menu:
    return
