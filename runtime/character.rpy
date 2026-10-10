init python:
    def rscript_wait_image(glow=False):
        tag = "grps wait%02d %s" % (rscript_textbox_state().get("wait_image", 0), "grow" if glow else "body")
        if renpy.has_image(tag):
            return tag
        if glow:
            return Null()
        return renpy.displayable(getattr(store, "rscript_ui", {}).get("wait_image", Text("▼", size=22, color="#ffffff")))

init:

    image rscript_ctc:
        contains:
            rscript_wait_image()
            xpos (rscript_layouts().get("wait%02d" % rscript_textbox_state().get("wait_image", 0), {}).get("items", {}).get("body", (4, 5))[0] if hasattr(store, "rscript_layouts") else 4)
            ypos (rscript_layouts().get("wait%02d" % rscript_textbox_state().get("wait_image", 0), {}).get("items", {}).get("body", (4, 5))[1] if hasattr(store, "rscript_layouts") else 5)
        contains:

            rscript_wait_image(True)
            xpos (rscript_layouts().get("wait%02d" % rscript_textbox_state().get("wait_image", 0), {}).get("items", {}).get("grow", (0, 0))[0] if hasattr(store, "rscript_layouts") else 0)
            ypos (rscript_layouts().get("wait%02d" % rscript_textbox_state().get("wait_image", 0), {}).get("items", {}).get("grow", (0, 0))[1] if hasattr(store, "rscript_layouts") else 0)
            alpha 0.0
            additive 1.0
            linear 35.0 / 30.0 alpha 1.0
            linear 35.0 / 30.0 alpha 0.0
            repeat

        # The repeating position callback must not block installing the children.
        function rscript_wait_transform

    define rscript_adv = ADVCharacter(kind = adv, ctc = "rscript_ctc", ctc_position = "fixed")
    define rscript_nvl = ADVCharacter(kind = rscript_adv)

    define narrator = ADVCharacter(kind = rscript_adv)
    define narrator_nvl = ADVCharacter(kind = rscript_adv)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
