init:

    image rscript_ctc:
        xpos 1191
        ypos 639

        contains:
            "grps wait00 body"
        contains:

            "grps wait00 grow"
            alpha 0.0
            additive 0.0
            linear 35.0 / 30.0 alpha 1.0
            linear 35.0 / 30.0 alpha 0.0
            repeat

    define rscript_adv = ADVCharacter(kind = adv, ctc = "rscript_ctc", ctc_position = "fixed")
    define rscript_nvl = ADVCharacter(kind = rscript_adv)

    define narrator = ADVCharacter(kind = rscript_adv)
    define narrator_nvl = ADVCharacter(kind = rscript_adv)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
