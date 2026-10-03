# Forest-specific boot movies and original scripted title, on the shared base.
label splashscreen:
    scene onlayer master
    scene black onlayer black
    _movie 2
    _movie 1
    return

label main_menu:
    return

label start:
    scene onlayer master
    scene black onlayer black
    call _0000
    return
