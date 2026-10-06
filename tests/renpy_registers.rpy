# Run only in disposable projects with a temporary save directory.
init 100 python:
    def registers_test_exception(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = registers_test_exception
    config.autosave_on_choice = False

label _0000:
    window hide
    python:
        persistent._reg = {number: 1 for number in range(6999, 7901)}
        _r[20] = 123
        renpy.session["register_test_saves"] = 0
        register_test_original_save = renpy.save_persistent
        def register_test_save():
            renpy.session["register_test_saves"] += 1
            register_test_original_save()
        renpy.save_persistent = register_test_save
    # The actual lowered 0501 reset: 900 iterations, not an infinite loop.
    $ _r[21] = 7000
label register_test_loop:
    if _r[21] <= 7899:
        jump register_test_clear
    jump register_test_done
label register_test_clear:
    $ _r[_r[21]] = 0
    $ _r[21] = _r[21] + 1
    jump register_test_loop
label register_test_done:
    python:
        assert _r[21] == 7900 and _r[20] == 123
        assert persistent._reg[6999] == persistent._reg[7900] == 1
        assert all(persistent._reg[number] == 0 for number in range(7000, 7900))
        assert renpy.session["register_test_saves"] == 0
        assert RScriptReg._persistent_dirty
    $ renpy.pause(0.01, hard=True)
    python:
        assert renpy.session["register_test_saves"] == 1
        assert not RScriptReg._persistent_dirty
        # No extra disk writes when only local registers changed.
        _r[21] = 0
    $ renpy.pause(0.01, hard=True)
    python:
        assert renpy.session["register_test_saves"] == 1
        import zlib
        from pathlib import Path
        data = (Path(renpy.config.savedir) / "persistent").read_bytes()
        saved = renpy.persistent.loads(zlib.decompress(data))
        assert all(saved._reg[number] == 0 for number in range(7000, 7900))
        assert saved._reg[6999] == saved._reg[7900] == 1
        renpy.save_persistent = register_test_original_save
        print("OK: native bounded register reset and batched persistent disk save")
        renpy.quit()
