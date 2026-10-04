# Automated gameplay regression, only installed in a disposable Khime fixture.
init 100 python:
    def rev_test_exception(info):
        print("".join(info.format()))
        renpy.quit(status=1)
    config.exception_handler = rev_test_exception
    config.auto_choice_delay = 0.05
    config.autosave_on_choice = False
    config.overlay_screens.append("rev_test_driver")
    renpy.session["rev_test_stage"] = "dismiss"

    def rev_test_advance():
        screen = renpy.get_screen("say")
        if screen is None:
            return
        if renpy.session["rev_test_stage"] == "rollback":
            actions = []
            def collect(displayable):
                if isinstance(displayable, renpy.display.behavior.Button):
                    if isinstance(displayable.action, RollbackToIdentifier):
                        actions.append(displayable.action)
            screen.visit_all(collect)
            assert len(actions) == 1, actions
            action = actions[0]
            assert action.identifier == renpy.session["rev_test_target"]
            assert action.get_sensitive(), "latest choice is not rollback-accessible"
            renpy.session["rev_test_stage"] = "returned"
            action()
            raise AssertionError("rev did not initiate rollback")
        assert renpy.session["rev_test_stage"] != "returned", "rev passed the latest choice"
        renpy.end_interaction(True)

define rev_test_narrator = Character(None, ctc=None)

screen rev_test_driver():
    timer 0.05 repeat True action Function(rev_test_advance)

label _0000:
    rev_test_narrator "Before first choice."
    menu:
        "First choice":
            pass
    $ first_choice = jump_back_point
    rev_test_narrator "Between choices."
    menu:
        "Second choice":
            pass
    python:
        assert jump_back_point is not None and jump_back_point != first_choice
        if renpy.session["rev_test_stage"] == "returned":
            # Re-executing the menu creates a fresh rollback identifier.
            assert renpy.get_identifier_checkpoints(jump_back_point) is not None
            print("OK: native menu updates rev target and rev returns to latest choice")
            renpy.quit()
        renpy.session["rev_test_target"] = jump_back_point
        renpy.session["rev_test_stage"] = "rollback"
    rev_test_narrator "After second choice: the driver clicks the real rev action."
    $ raise AssertionError("rev dismissed dialogue instead of returning to choice")
