default khime_choice_prompt = None
default khime_face_number = 0
default khime_face_x = 0
default khime_face_y = 273
default khime_face_depth = 1
default khime_number_state = {}
default khime_click_values = {}
default khime_click_links = {}

python early:
    def khime_textbox_background():
        path = "images/grps/tbox%02d/back.png" % store.cur_textbox
        return path if renpy.loadable(path) else Solid("#000000d0")

    def khime_parse(lex):
        value = lex.rest()
        lex.expect_eol()
        return value

    def khime_say(value):
        raw = eval(value)
        text, center = parse_rscript_text(repr(raw), True)
        queue_draw(show_window)
        process_draw_queue()
        renpy.say(narrator, text, interact=True, show_center=center)

    def khime_face(value):
        number = int(eval(value.split()[0]))
        store.khime_face_number = number
        if not number:
            renpy.hide("khime_face", layer=IMAGE_LAYER)
            return
        path = "images/grpf/%04d.png" % number
        if renpy.loadable(path):
            renpy.show("khime_face", what=Image(path), layer=IMAGE_LAYER,
                       at_list=[Transform(xpos=store.khime_face_x,
                                          ypos=store.khime_face_y)],
                       zorder=store.khime_face_depth)

    def khime_faceloc(value):
        x, y = value.split()[:2]
        store.khime_face_x = int(eval(x))
        store.khime_face_y = int(eval(y))
        if store.khime_face_number:
            khime_face(str(store.khime_face_number))

    def khime_facedep(value):
        store.khime_face_depth = int(eval(value))

    def khime_number(value):
        # The original number widget still needs game-specific visual matching.
        store.khime_number_state[str(len(store.khime_number_state))] = value

    def khime_folder(value):
        layer, name = value.split(None, 1)
        layer, name = int(eval(layer)), eval(name)
        if layer == 0:
            for number in range(100):
                store.folder[number] = name
        else:
            store.folder[layer] = name

    def khime_locmode(value):
        layer, xmode, ymode = (int(eval(part)) for part in value.split()[:3])
        anchor = (0.0 if xmode == 0 else 0.5,
                  0.0 if ymode == 0 else 0.5)
        if layer == 0:
            for number in range(100):
                store.layer_anchor[number] = anchor
        else:
            store.layer_anchor[layer] = anchor

    def khime_setclk(value, system=False):
        layer, result = (int(eval(part)) for part in value.split()[:2])
        store.khime_click_values[layer] = (result, system)

    def khime_setlink(value):
        layer, image, x, y = (int(eval(part)) for part in value.split()[:4])
        store.khime_click_links[layer] = (image, x, y)

    def khime_resetclk(value):
        store.khime_click_values.clear()
        store.khime_click_links.clear()

    def khime_click(value):
        options = []
        for layer, (result, system) in sorted(store.khime_click_values.items()):
            if layer not in store.khime_click_links or layer not in store.layer_info:
                continue
            hover, x, y = store.khime_click_links[layer]
            folder = store.folder.get(layer)
            if folder:
                options.append((result, system, store.layer_info[layer],
                                "%s %04d" % (folder, hover), x, y))
        if not options:
            raise Exception("Khime click has no active image regions")
        store._r[0] = renpy.call_screen("khime_click_screen", options=options)
        khime_resetclk("")

    def khime_click_action(result, system):
        if not system:
            return Return(result)
        if result == 0:
            return Quit(confirm=False)
        if result == 1:
            return ShowMenu("save")
        if result == 2:
            return ShowMenu("load")
        if result == 3:
            return ShowMenu("preferences")
        return Return(result)

    renpy.register_statement("_khime_say", parse=khime_parse,
                             execute=khime_say)
    renpy.register_statement("_khime_append", parse=khime_parse,
                             execute=khime_say)
    renpy.register_statement("_khime_face", parse=khime_parse,
                             execute=khime_face)
    renpy.register_statement("_khime_faceloc", parse=khime_parse,
                             execute=khime_faceloc)
    renpy.register_statement("_khime_facedep", parse=khime_parse,
                             execute=khime_facedep)
    for name in ("num", "numload", "numloc", "numreng", "numset"):
        renpy.register_statement("_khime_" + name, parse=khime_parse,
                                 execute=khime_number)
    renpy.register_statement("_khime_folder", parse=khime_parse,
                             execute=khime_folder)
    renpy.register_statement("_khime_locmode", parse=khime_parse,
                             execute=khime_locmode)
    renpy.register_statement("_khime_setclk", parse=khime_parse,
                             execute=khime_setclk)
    renpy.register_statement("_khime_setclksys", parse=khime_parse,
                             execute=lambda value: khime_setclk(value, True))
    renpy.register_statement("_khime_setlink", parse=khime_parse,
                             execute=khime_setlink)
    renpy.register_statement("_khime_resetclk", parse=khime_parse,
                             execute=khime_resetclk)
    renpy.register_statement("_khime_click", parse=khime_parse,
                             execute=khime_click)

screen khime_click_screen(options):
    modal True
    for result, system, idle_image, hover_image, x, y in options:
        imagebutton:
            idle idle_image
            hover hover_image
            focus_mask True
            xpos x
            ypos y
            action khime_click_action(result, system)

screen say(who, what, center=False):
    window:
        id "window"
        background khime_textbox_background()
        xalign 0.5
        yalign 1.0
        xsize 800
        ysize 163

        text what:
            id "what"
            font "fonts/NotoSansCJKjp-Regular.otf"
            size 30
            color "#ffffff"
            xpos 34
            ypos 12
            xsize 732
            text_align (0.5 if center else 0.0)

screen choice(items):
    modal True
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 8
        if khime_choice_prompt:
            text khime_choice_prompt xalign 0.5 color "#ffffff" size 24
        for item in items:
            if item.action is not None:
                textbutton item.caption action item.action

screen game_menu():
    tag menu
    modal True
    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            spacing 12
            textbutton "Return" action Return()
            textbutton "Save" action ShowMenu("save")
            textbutton "Load" action ShowMenu("load")
            textbutton "Title" action MainMenu(confirm=False)
            textbutton "Quit" action Quit(confirm=False)

screen save():
    tag menu
    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            for slot in range(1, 11):
                textbutton "Save [slot]" action FileSave(slot)
            textbutton "Back" action ShowMenu("game_menu")

screen load():
    tag menu
    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            for slot in range(1, 11):
                textbutton "Load [slot]" action FileLoad(slot)
            textbutton "Back" action ShowMenu("game_menu")

screen preferences():
    tag menu
    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            textbutton "Music" action Preference("music mute", "toggle")
            textbutton "Sound" action Preference("sound mute", "toggle")
            textbutton "Voice" action Preference("voice mute", "toggle")
            textbutton "Back" action Return()
