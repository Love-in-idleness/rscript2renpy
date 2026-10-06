# Optional side story. Only generated zero_config.rpy enables this overlay.
define khime_zero_available = False

init python:
    def khime_zero_unlocked():
        # 0101.tsc enables 9005/9105 after 7003.tsc sets this persistent flag.
        return khime_zero_available and _r[7901] == 1

    def khime_zero_begin():
        renpy.block_rollback()
        for channel in ("music", "voice", "rscript_voice", "se0", "se1", "se2"):
            renpy.music.stop(channel=channel)
        for layer in (IMAGE_LAYER, CG_LAYER, FLASH_LAYER):
            renpy.scene(layer=layer)
        store.in_queue = False
        store.draw_queue = []
        store.draw_queue_delayed = []
        store.draw_queue_extra_delayed = []
        store.layer_info = {}
        store.layer_pos = {}
        store.layer_alpha = {}
        store.layer_blend = {}
        store.layer_zorder = {}
        store.layer_enabled = {n: 1 for n in range(50)}
        store.layer_anchor = {n: (0.5, 0.5) for n in range(11, 31)}
        store.folder = {n: "khime_zero " + ("grpe" if n < 10 else
                         "grpo" if n < 20 else "grpo_bu" if n < 30 else "grps")
                        for n in range(1, 50)}
        store.layer_x_grid = store.layer_y_grid = 1.25
        store.object_size = {}
        store.rscript_voice_format = "khime_zero/voice/%04d.ogg"
        store.rscript_bgm_format = "khime_zero/bgm/Track%02d.ogg"
        store.rscript_se_format = "khime_zero/wav/%04d.ogg"
        store.rscript_speaker_images_override = True
        store.rscript_ui = dict(rscript_ui, text_image_root="images/khime_zero/grps",
                               speaker_zoom=1.25, inline_zoom=1.25, speaker_pos=(6, 15))
        store.text_indent = 97 * 1.25
        store.cur_textbox = 1
        store.khime_face_number = 0
        store.rscript_click_values = {}
        store.rscript_click_links = {}
        store.menu_enabled = store.save_enabled = store.warp_enabled = 1
        store.roll_enabled = store.resm_enabled = 1
        store.last_say = store.last_spk = None
        store.rscript_speaker = None
        store.rscript_speaker_visible = False
        store.jump_back_point = None
        store.tonedep = 0
        store.tone_color = None
        store.tone_level = 0

# Register the side story's 640x480 images as 800x600 displayables.
init 5 python:
    for path in renpy.list_files():
        if path.startswith("images/khime_zero/") and path.endswith(".png"):
            tag = " ".join(path[7:-4].lower().split("/"))
            renpy.image(tag, Transform(Image(path), zoom=1.25))

python early:
    def khime_zero_gload(args):
        image = "khime_zero grpe %04d" % args.CGNum
        queue_draw(renpy.scene, layer=CG_LAYER)
        queue_draw(renpy.show, image, tag=CG_TAG, layer=CG_LAYER,
                   at_list=[Transform(shader="rscript.colormode", u_colormode=args.Colormode)])
        process_draw_queue()
        store.layer_info[CG_LAYER] = image
        store.layer_pos[CG_LAYER] = (0, 0)
        # Never turn the external CG number into a main-game unlock register.

    def khime_zero_bgm_on(args):
        path = "khime_zero/bgm/Track%02d.ogg" % args.BgmNo
        if not renpy.loadable(path):
            path = "khime_zero/bgm/Track%02d.wav" % args.BgmNo
        renpy.music.play(path, channel="music", loop=True, if_changed=True)

    renpy.register_statement("_khime_zero_gload", parse=parse_gload,
                             execute=khime_zero_gload, lint=lint_undef)
    renpy.register_statement("_khime_zero_bgm_on", parse=parse_bgm_on,
                             execute=khime_zero_bgm_on, lint=lint_undef)

label khime_zero_start:
    if not khime_zero_unlocked():
        $ renpy.full_restart()
    $ khime_zero_begin()
    jump expression "_khime_zero_2001"

# Extend only the ordinary title's 9106 menu, not the alternate extras menu.
init offset = 10
screen rscript_click_extra(options):
    if khime_zero_unlocked() and any(hover == "grpo_tp 9106" for _, _, _, hover, _, _ in options):
        imagebutton:
            id "khime_zero_entry"
            idle "khime_zero grpo 0001"
            hover "khime_zero grpo 0101"
            focus_mask True
            xpos config.screen_width // 2
            xanchor 0.5
            ypos 517
            action Jump("khime_zero_start")
