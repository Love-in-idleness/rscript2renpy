# The gallery body remains compiled TSC; only its UI return path is adapted.
init python:
    config.label_overrides["_0210"] = "sevenbridge_cg_viewer"

label sevenbridge_cg_viewer:
    call _rscript_variant0_0210
    # The native UI returns to the originating thumbnail page after the last CG.
    _jump _r[299]
