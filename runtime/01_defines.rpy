python early:

    _includes = set()
init offset = -150
init:

    define OTHER_TAG = "other"

    define IMAGE_LAYER = "master"

    define CG_LAYER = "cg"
    define CG_TAG = CG_LAYER

    define FLASH_LAYER = "flash"
    define FLASH_TAG = FLASH_LAYER

    define TONE_LAYER = IMAGE_LAYER
    define TONE_TAG = "tone"

    define EFFECT_TAG = "effect"

    define QUAKE_LAYERS = [
    CG_LAYER,
    IMAGE_LAYER,
    "transient",
    "screens",
  ]

    define GLOBAL_START = 7000
    define MAX_INDEX = 9999
    define MAX_SAVE_PAGE = 100
    define MACRO_FN = "<macro>"

    define FRAME = 1 / 60.

    default in_queue = False
    default draw_queue = []
    default draw_queue_delayed = []
    default draw_queue_extra_delayed = []
    default se_queue = [0] * 3
    default nvl_mode = False
    default quakeex_params = None
    default jump_back_point = None

    default folder = {}
    default layer_zorder = {}
    default layer_enabled = {}
    default layer_info = {}
    default layer_pos = {}
    default layer_alpha = {}
    default layer_blend = {}
    default layer_anchor = {}
    default object_size = {}
    default layer_x_grid = 1
    default layer_y_grid = 1

    default tonedep = 0
    default tone_color = None
    default tone_level = 0

    default effect_zorder = 50
    default effect_pause = 0

    default menu_enabled = 1
    default save_enabled = 1
    default warp_enabled = 1
    default roll_enabled = 1
    default resm_enabled = 1

    default cur_textbox = 1
    default textbox_panel = 1
    default text_indent = 174

    default last_say = None
    default last_spk = None
    default last_center = False
    default blank_say = False

    default persistent.save_page = 1
    default persistent.load_page = 1
    default persistent.config_page = 0
    default persistent.widescreen_cg = True
    default persistent.seen_cg = {}



init python:

    from collections import defaultdict

    class RScriptReg:
        def get(self, key, default = 0):
            key, val = eval_key(key)
            if val is not None:
                return val
            if key < GLOBAL_START:
                return store._reg.get(key, default)
            return persistent._reg.get(key, default)

        def __getitem__(self, key):
            return self.get(key, 0)

        def __setitem__(self, key, value):
            key, val = eval_key(key)
            if val is not None:
                raise Exception("Trying to assign value to constant @%s." % key)

            if key < GLOBAL_START:
                store._reg[key] = value
            else:
                persistent._reg[key] = value

        def __contains__(self, key):
            key, val = eval_key(key)
            return key < MAX_INDEX or val is not None

        def update(self, data):
            for key in data:
                self[key] = data[key]

    def eval_key(key):
        if isinstance(key, basestring):
            if not key in persistent._defs:
                raise Exception("Key name \"%s\" not defined." % key)

            val = persistent._defs[key]


            if val.startswith("@"):
                return int(val[1:], 10), None


            else:
                return key, int(val, 10)

        else:
            return key, None

    def unalias_reg(alias):
        return eval_key(alias)

    def compile_macro(name, macro):
        macro = renpy.re.sub(ur"\^\_", ur" ", macro)
        macro = renpy.re.sub(ur"\^\/", ur"\n", macro)
        macro = renpy.re.sub(ur"^=", ur"_queue", macro)
        macro = renpy.re.sub(ur"\*", ur"_", macro)

        source = ("$ apply_macro_params()\n" + macro +
                  "\n$ clear_macro_params()\nreturn")
        return renpy.load_string(source, MACRO_FN + "/" + name)

    def apply_macro_params():
        store._macro_params = ["0"] * 10
        if store._kwargs and "_rscript_macro_args" in store._kwargs:
            params = store._kwargs["_rscript_macro_args"].split()
            store._macro_params[:len(params[:10])] = params[:10]

    def clear_macro_params():
        store._macro_params = None

init:

    default _r = RScriptReg()
    default _reg = {}
    default persistent._reg = {}
    default persistent._defs = {}
    default _macro_params = None
    define _macros = {}
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
