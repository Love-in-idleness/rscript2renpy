#!/usr/bin/env python3
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forest"))
from build_forest_rscript import (FOREST_COMPAT, RSCRIPT_OBJECTS, compile_scene,
                                  convert_masks, convert_movies, copy_assets)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("resources", type=Path)
    resources = parser.parse_args().resources.resolve()
    builder_path = ROOT / "forest" / "build_forest_rscript.py"
    builder = builder_path.read_text(encoding="utf-8")
    assert '"                renpy.save_persistent()")' in builder
    assert 'not source.name.startswith("unren-")' in builder
    assert 'game.glob("unren-*.rpy*")' in builder
    assert 'convert_movies(root / "mov", game / "mov")' in builder
    assert "'label splashscreen:\\n'" in builder
    assert ("'    _movie 2\\n'\n"
            "        '    _movie 1\\n'\n"
            "        '    return\\n\\n'\n"
            "        'label main_menu:\\n'" in builder)
    assert ('obsolete.suffix.lower() == ".mpg"' in builder)
    shader = (ROOT / "runtime" / "shaders.rpy").read_text(encoding="utf-8")
    for invalid in ("(1 - v)", "== 1)", "== 2)", "== 4)",
                    "vec3(0)", "1 - gl_FragColor.rgb", "(1 - col.",
                    "alpha1 = 0;", "alpha2 = 0;", "alpha3 = 0;"):
        assert invalid not in shader
    assert "vec3 rscript_grayscale" in shader
    assert "u_colormode == 3.0" in shader
    gfx = (ROOT / "runtime" / "03_rscript_gfx.rpy").read_text(encoding="utf-8")
    assert "args.Colormode in [0, 1, 2, 3, 4]" in gfx
    assert "store.layer_info[CG_LAYER] = shown_img" in gfx
    util = (ROOT / "runtime" / "01_util.rpy").read_text(encoding="utf-8")
    assert "def speed_change(match):" in util
    assert "def size_change(match):" in util
    assert "store.effect_pause = max(store.effect_pause, dur)" in util
    effects = (ROOT / "runtime" / "effects.rpy").read_text(encoding="utf-8")
    assert "if layer not in store.layer_info:" in effects
    assert "if isinstance(num, (int, long, float))" in effects
    assert 'queue_draw(renpy.hide, "layer%d" % num' in effects
    commands = (ROOT / "runtime" / "02_rscript_cmd.rpy").read_text(encoding="utf-8")
    assert "def parse_setclksub(lex):" in commands
    assert "label = label_insub" in commands
    assert "renpy.call(_macros[name], _rscript_macro_args = params)" in commands
    definitions = (ROOT / "runtime" / "01_defines.rpy").read_text(encoding="utf-8")
    assert "def apply_macro_params():" in definitions
    assert "def clear_macro_params():" in definitions
    assert "def unalias_reg(alias):" in definitions
    assert "default text_indent = 174" in definitions
    text_runtime = (ROOT / "runtime" / "05_rscript_text.rpy").read_text(encoding="utf-8")
    assert "def parse_txcls(lex):" in text_runtime
    assert "def parse_texindent(lex):" in text_runtime
    assert "store.text_indent = args.Indent" in text_runtime
    assert "def parse_oload(lex):" in gfx
    assert "store.object_size[args.Layer] = args.Size" in gfx
    assert "move_layer(args.Layer, 0, 0, 9, 4, relative = True)" in gfx
    assert "def parse_oload(lex):" in RSCRIPT_OBJECTS
    assert 'if "def parse_oload(lex):" not in gfx_text:' in builder
    assert 'if "    default object_size = {}" not in definitions_text:' in builder
    with TemporaryDirectory() as temporary:
        target = Path(temporary)
        convert_masks(resources / "grps", target)
        for name in ("ef11.png", "ef12.png"):
            with Image.open(target / name) as mask:
                assert mask.format == "PNG" and mask.size == (800, 600)
        metadata_source = target / "metadata-source"
        metadata_source.mkdir()
        (metadata_source / ".meta.xml").write_text("<Canvas/>", encoding="utf-8")
        copy_assets(metadata_source, ".meta.xml", target / "metadata-target")
        assert (target / "metadata-target" / ".meta.xml").read_text(
            encoding="utf-8") == "<Canvas/>"
        movie_source = target / "movie-source"
        movie_target = target / "movie-target"
        movie_source.mkdir()
        movie_target.mkdir()
        (movie_target / "old.MPG").write_bytes(b"obsolete")
        convert_movies(movie_source, movie_target)
        assert not (movie_target / "old.MPG").exists()
    font = ROOT / "forest" / "fonts" / "NotoSansCJKjp-Regular.otf"
    assert font.is_file() and font.stat().st_size > 1_000_000
    files = sorted((resources / "scr").glob("*.tsc"))
    scenes = [compile_scene(path) for path in files]
    assert len(scenes) == 103
    compiled = "".join(scenes)
    for opcode in (0x20, 0x23, 0x53, 0x63, 0x78):
        assert "unlifted opcode 0x%04x" % opcode not in compiled
    assert compiled.count("    _oload ") == 58
    assert compiled.count("    _oaction ") == 1
    assert compiled.count("    _txcls") == 2
    assert compiled.count("    _texindent ") == 4
    assert compiled.count("    _osize ") == 52
    assert "unlifted opcode 0x0053" not in compiled
    assert "unlifted opcode 0x0063" not in compiled
    assert compiled.count("    menu:\n") == compiled.count(
        "    $ jump_back_point = renpy.game.log.current.identifier\n")
    assert "label _2100:" in scenes[[p.stem for p in files].index("2100")]
    assert all("label _" in scene and "forest_run" not in scene for scene in scenes)
    assert all("_say english" not in scene and "_append english" not in scene for scene in scenes)
    assert all("_say japanese" in scene or "_append japanese" in scene
               for scene in scenes if "_say " in scene or "_append " in scene)
    title = scenes[[p.stem for p in files].index("0001")]
    assert "_forest_click 0 0" in title
    assert 'font "fonts/NotoSansCJKjp-Regular.otf"' in FOREST_COMPAT
    assert 'renpy.music.play(voice_file, channel = \\"rscript_voice\\"' in builder
    assert 'store.forest_last_voice = voice_file' in builder
    assert "who = None" in builder
    assert "_load 11 1001 515 267 0 0" in title
    assert "_se 0 1\n    _se_on 0 1 0 0" in title
    assert "_forest_folder 0 'grpo'" in scenes[[p.stem for p in files].index("0000")]
    assert "'forest_asset_3501':" in scenes[[p.stem for p in files].index("1000")]
    assert "__forest_asset_" not in compiled
    story = scenes[[p.stem for p in files].index("2100")]
    assert "    _oaction 29 4" in story
    assert "_se 0 1008\n    _se_on 0 999 0 0" in story
    assert "_se 999 1008" not in story
    assert "    _voice 91 0 0 0\n    _say japanese '^g005うっわ、くっさぁ" in story
    scene_2500 = scenes[[p.stem for p in files].index("2500")]
    assert "unlifted opcode 0x0009" not in scene_2500
    assert scene_2500.count("renpy.random.randrange(0x8000)") == 7
    assert ("$ _r[6000] = ((renpy.random.randrange(0x8000) % 100) + 1)\n"
            "    if not ((_r[6000] <= 40)):") in scene_2500
    assert "_load 10 -21416" not in scene_2500
    assert "_load 10 44120" not in scene_2500
    assert "_load 10 4416 _r[802] 300 0 0" in scene_2500
    assert ("$ jump_back_point = renpy.game.log.current.identifier\n"
            "    $ forest_choice_prompt = 'お話を聞かせる？'\n"
            "    menu:" in story)
    assert "    menu:\n        'お話を聞かせる？'" not in story
    assert "'いいよ':\n            $ _r[2] = 0\n            jump _2100_L_0000ba" in story
    assert "'いやだ':\n            $ _r[2] = 1\n            jump _2100_L_0000c6" in story
    credits = scenes[[p.stem for p in files].index("5000")]
    assert "    _osize 40 25" in credits
    assert "    _oload 40 400 270 0 0 '企画・原案・シナリオ'" in credits
    assert "screen say(who, what, center=False):" in FOREST_COMPAT
    assert "text_align (0.5 if center else 0.0)" in FOREST_COMPAT
    assert ('background Transform("images/grps/tbox01/back.png", '
            'alpha=persistent.textbox_opacity)' in FOREST_COMPAT)
    assert "xpos text_indent + 1" in FOREST_COMPAT
    assert "xsize 19 * 22" in FOREST_COMPAT
    assert '"images/grps/gf%03d.png" % forest_speaker' in FOREST_COMPAT
    assert 'screen forest_compane():' in FOREST_COMPAT
    assert 'use forest_compane' in FOREST_COMPAT
    assert 'xpos 606\n            ypos 120' in FOREST_COMPAT
    assert 'base_bar "images/grps/compane/bg.png"' in FOREST_COMPAT
    assert 'value FieldValue(persistent, "textbox_opacity", range=1.0)' in FOREST_COMPAT
    assert 'action Rollback()' in FOREST_COMPAT
    assert 'action RollForward()' in FOREST_COMPAT
    assert 'action Skip(fast=True)' in FOREST_COMPAT
    assert 'action Function(forest_replay_voice)' in FOREST_COMPAT
    assert 'insensitive "images/grps/compane/voc_off.png"' in FOREST_COMPAT
    assert 'action HideInterface()' in FOREST_COMPAT
    assert 'config.game_menu_action = Function(forest_open_game_menu)' in FOREST_COMPAT
    assert 'if store.menu_enabled:' in FOREST_COMPAT
    assert 'screen preferences(title_mode=False):' in FOREST_COMPAT
    assert 'if not title_mode:' in FOREST_COMPAT
    assert 'if store.save_enabled:' in FOREST_COMPAT
    save_guard = FOREST_COMPAT.index('if store.save_enabled:')
    assert save_guard < FOREST_COMPAT.index('action ShowMenu("save")', save_guard)
    assert save_guard < FOREST_COMPAT.index('action ShowMenu("load")', save_guard)
    assert 'ShowMenu("preferences", title_mode=not store.menu_enabled)' in FOREST_COMPAT
    assert 'config.overlay_screens.append("forest_touch_controls")' in FOREST_COMPAT
    assert 'if renpy.variant("touch")' in FOREST_COMPAT
    assert 'textbutton "メニュー" action ShowMenu("preferences")' in FOREST_COMPAT
    assert 'config.keymap["game_menu"].append("K_AC_BACK")' in FOREST_COMPAT
    assert 'style forest_volume_bar is bar:' in FOREST_COMPAT
    assert FOREST_COMPAT.count('style "forest_volume_bar"') == 3
    assert 'base_bar Null()' not in FOREST_COMPAT
    assert 'confscrn/bgm_lev.png' not in FOREST_COMPAT
    assert 'confscrn/voc_lev.png' not in FOREST_COMPAT
    assert 'confscrn/sef_lev.png' not in FOREST_COMPAT
    assert '"images/grps/nonbl/%d.png" % page_number' in FOREST_COMPAT
    assert 'text FileCurrentPage()' not in FOREST_COMPAT
    assert 'screen save():' in FOREST_COMPAT and 'screen load():' in FOREST_COMPAT
    assert 'data["forest_dt1"] = int(_r[1])' in FOREST_COMPAT
    assert 'FileJson(slot, key="forest_dt1")' in FOREST_COMPAT
    assert 'images/grps/dt1_%04d.png' in FOREST_COMPAT
    assert 'FileScreenshot' not in FOREST_COMPAT
    assert ('idle "images/grps/confscrn/bgm_on_f.png"\n'
            '            hover "images/grps/confscrn/bgm_on_f.png"\n'
            '            selected_idle "images/grps/confscrn/bgm_on.png"'
            in FOREST_COMPAT)
    assert 'return ShowMenu("load")' in FOREST_COMPAT
    assert 'return Quit(confirm=True)' in FOREST_COMPAT
    assert ('execute=execute_forest_setclksys, lint=lint_undef)'
            in FOREST_COMPAT)
    assert "'label main_menu:\\n'" in builder
    assert "'define config.version = \"1.0\"\\n'" in builder
    print("OK: lowered %d Forest TSC files to rscript RPY" % len(scenes))


if __name__ == "__main__":
    main()
