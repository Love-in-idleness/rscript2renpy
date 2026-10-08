init:

    image rscript_ctc:
        function rscript_wait_transform

        contains:
            ("grps wait%02d body" % rscript_textbox_state().get("wait_image", 0))
            xpos (rscript_layouts().get("wait%02d" % rscript_textbox_state().get("wait_image", 0), {}).get("items", {}).get("body", (4, 5))[0] if hasattr(store, "rscript_layouts") else 4)
            ypos (rscript_layouts().get("wait%02d" % rscript_textbox_state().get("wait_image", 0), {}).get("items", {}).get("body", (4, 5))[1] if hasattr(store, "rscript_layouts") else 5)
        contains:

            ("grps wait%02d grow" % rscript_textbox_state().get("wait_image", 0))
            xpos (rscript_layouts().get("wait%02d" % rscript_textbox_state().get("wait_image", 0), {}).get("items", {}).get("grow", (0, 0))[0] if hasattr(store, "rscript_layouts") else 0)
            ypos (rscript_layouts().get("wait%02d" % rscript_textbox_state().get("wait_image", 0), {}).get("items", {}).get("grow", (0, 0))[1] if hasattr(store, "rscript_layouts") else 0)
            alpha 0.0
            additive 1.0
            linear 35.0 / 30.0 alpha 1.0
            linear 35.0 / 30.0 alpha 0.0
            repeat

    define rscript_adv = ADVCharacter(kind = adv, ctc = "rscript_ctc", ctc_position = "fixed")
    define rscript_nvl = ADVCharacter(kind = rscript_adv)

    define narrator = ADVCharacter(kind = rscript_adv)
    define narrator_nvl = ADVCharacter(kind = rscript_adv)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
