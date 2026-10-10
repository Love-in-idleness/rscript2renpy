default khime_choice_prompt = None
default khime_face_number = 0
default khime_face_x = 0
default khime_face_y = 273
default khime_face_depth = 1
default khime_number_state = {}

# KhimeDL_CHS.exe 0x44132d: native green. The patched font names at
# 0x46e194 and 0x46d110 both decode to SimHei (黑体).
define rscript_text_colors = {"g": "#7FDFA5"}
define rscript_text_fonts = {"m": "fonts/simhei.ttf", "g": "fonts/simhei.ttf"}

python early:
    def khime_parse(lex):
        value = lex.rest()
        lex.expect_eol()
        return value

    def khime_say(value):
        raw = eval(value)
        execute_say((None, None, repr(raw)))

    def khime_append(value):
        execute_append((None, repr(eval(value))))

    def khime_face(value):
        number = int(eval(value.split()[0]))
        store.khime_face_number = number
        if not number:
            renpy.hide("khime_face", layer=IMAGE_LAYER)
            return
        path = rscript_image_path("grpf/%04d.png" % number)
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

    def khime_locmode(value):
        layer, xmode, ymode = (int(eval(part)) for part in value.split()[:3])
        anchor = (0.0 if xmode == 0 else 0.5,
                  0.0 if ymode == 0 else 0.5)
        if layer == 0:
            for number in range(100):
                store.layer_anchor[number] = anchor
        else:
            store.layer_anchor[layer] = anchor

    renpy.register_statement("_khime_say", parse=khime_parse,
                             execute=khime_say)
    renpy.register_statement("_khime_append", parse=khime_parse,
                             execute=khime_append)
    renpy.register_statement("_khime_face", parse=khime_parse,
                             execute=khime_face)
    renpy.register_statement("_khime_faceloc", parse=khime_parse,
                             execute=khime_faceloc)
    renpy.register_statement("_khime_facedep", parse=khime_parse,
                             execute=khime_facedep)
    for name in ("num", "numload", "numloc", "numreng", "numset"):
        renpy.register_statement("_khime_" + name, parse=khime_parse,
                                 execute=khime_number)
    renpy.register_statement("_khime_locmode", parse=khime_parse,
                             execute=khime_locmode)
    register_rscript_ui_aliases("khime")

init -100 python:
    rscript_folder_zero_all = True
    # KhimeDL_CHS.exe 40a000: links are separate cards, not hit coordinates.
    rscript_click_link_is_preview = True
    rscript_click_native_effects = True

init python:
    rscript_ui.update({"textbox_size": (800, 163)})

screen choice(items):
    use rscript_choice(items, khime_choice_prompt)
