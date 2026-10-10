# Run only in disposable projects with a temporary save directory.
init 100 python:
    def save_permissions_test_exception(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = save_permissions_test_exception
    config.autosave_on_choice = False

label _0000:
    window hide
    $ menu_enabled = save_enabled = roll_enabled = 1
    $ rscript_sync_permissions()
    $ FilePage(1)()
    $ renpy.pause(0.01, hard=True)
    $ renpy.save("1-1", include_screenshot=False)
    if renpy.session.get("save_permissions_stage", 0) == 0:
        $ renpy.session["save_permissions_stage"] = 1
        $ menu_enabled = save_enabled = roll_enabled = 0
        $ rscript_sync_permissions()
        python:
            assert config.save and not _autosave and not _rollback
            assert not FileSave(1).get_sensitive()
            assert not rscript_ui_sensitive("preferences")
            assert FileLoad(1).get_sensitive()
            rscript_open_game_menu()
            assert renpy.get_screen("preferences") is None
        show screen load
        $ renpy.pause(0.01, hard=True)
        $ FileLoad(1, confirm=False)()
        $ raise AssertionError("title load did not restore the saved script")
    elif renpy.session["save_permissions_stage"] == 1:
        python:
            assert menu_enabled == save_enabled == roll_enabled == 1
            rscript_sync_permissions()
            assert config.save and _autosave and _rollback
            assert FileSave(1).get_sensitive()
            renpy.session["save_permissions_stage"] = 2
            assert rscript_ui_sensitive("preferences")
            renpy.show_screen("preferences")
            assert renpy.get_screen("preferences") is not None
        show screen load
        $ renpy.pause(0.01, hard=True)
        $ FileLoad(1, confirm=False)()
        $ raise AssertionError("in-game load did not restore the saved script")
    else:
        $ assert menu_enabled == save_enabled == roll_enabled == 1
        $ rscript_sync_permissions()
        $ assert config.save and _autosave and _rollback
        $ print("OK: native title and in-game loads preserve save permissions")
        $ renpy.quit()
