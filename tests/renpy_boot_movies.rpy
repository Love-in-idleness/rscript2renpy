# Test startup routing without decoding proprietary movies or using player saves.
default persistent.boot_movie_calls = []
init 100 python:
    renpy.movie_cutscene = lambda filename: persistent.boot_movie_calls.append(filename)
    config.end_game_transition = None

label _0000:
    python:
        assert rscript_boot_movies == (2, 1)
        assert persistent.boot_movie_calls == ["mov/0002.mpg", "mov/0001.mpg"], persistent.boot_movie_calls
        if not persistent.boot_return_test:
            persistent.boot_return_test = True
            renpy.full_restart()
        original_loadable = renpy.loadable
        try:
            # Simulate one missing movie, then both; other resources stay loadable.
            for available, expected in (({"mov/0001.mpg"}, ["mov/0001.mpg"]), (set(), [])):
                renpy.loadable = lambda filename, *args, **kwargs: filename in available if filename.startswith("mov/") else original_loadable(filename, *args, **kwargs)
                persistent.boot_movie_calls = []
                renpy.call_in_new_context("splashscreen")
                assert persistent.boot_movie_calls == expected, persistent.boot_movie_calls
        finally:
            renpy.loadable = original_loadable
        print("OK: native startup movies play in order only on launch")
        renpy.quit(save=False)
