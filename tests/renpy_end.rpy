# Run only in disposable projects with a temporary save directory.
init 100 python:
    def end_test_exception(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = end_test_exception
    rscript_boot_movies = ()  # Exercise splashscreen without proprietary media.
    def end_test_label(name, abnormal):
        if name == "splashscreen":
            renpy.session["end_test_splash"] = renpy.session.get("end_test_splash", 0) + 1
    config.label_callback = end_test_label

label _0000:
    if renpy.session.get("end_test_restarted", False):
        python:
            assert _r[7110] == _r[7960] == 1
            assert _r[7001] == 0 and _r[7005] == 99
            assert len(renpy.get_return_stack()) == renpy.session["end_test_depth"]
            assert renpy.session.get("end_test_splash", 0) == 1
            print("OK: native end discards nested story calls and retains progress")
            renpy.quit()
    $ renpy.session["end_test_depth"] = len(renpy.get_return_stack())
    _gosub 3662
    $ raise AssertionError("end resumed the boot caller")

label _3662:
    # Match the sister branch: 3677 jumps to 3673, then 3661 ends the run.
    _gosub 3677
    $ raise AssertionError("end entered the next story, 3676")

label _3677:
    $ _r[3677] = 2
    _jump 3673

label _3673:
    _jump 3661

label _3661:
    $ _r[7110] = 1
    $ _r[7960] = 1
    $ _r[7001] = 0
    $ _r[7005] = 99
    $ renpy.session["end_test_restarted"] = True
    _end
    $ raise AssertionError("end fell through")
