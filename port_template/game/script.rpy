# Generic CodeX/RScript entry point. Replace this file only when the source
# game uses a different boot scene.
label start:
    scene onlayer master
    scene black onlayer black
    call _0000
    return

label main_menu:
    jump start
