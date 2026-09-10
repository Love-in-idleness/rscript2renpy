#!/usr/bin/env python3
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forest"))
from build_forest_rscript import (FOREST_COMPAT, RSCRIPT_OBJECTS, compile_scene,
                                  convert_masks, convert_movies, copy_assets,
                                  language_patch_data, language_patch_strings, menu_text,
                                  scene_strings)
from forest_tsc import read_tsc


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
    assert "if isinstance(num, (int, float))" in effects
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
    assert "_say japanese" not in compiled
    assert "_append japanese" not in compiled
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
    story_source = files[[p.stem for p in files].index("2100")]
    story_tsc = read_tsc(story_source)
    assert "    _oaction 29 4" in story
    assert "_se 0 1008\n    _se_on 0 999 0 0" in story
    assert "_se 999 1008" not in story
    assert "    _voice 91 0 0 0\n    _say " in story
    japanese_story = compile_scene(
        story_source, language="japanese")
    assert "    _voice 91 0 0 0\n    _say japanese " in japanese_story
    scene_2500 = scenes[[p.stem for p in files].index("2500")]
    assert "unlifted opcode 0x0009" not in scene_2500
    assert scene_2500.count("renpy.random.randrange(0x8000)") == 7
    assert ("$ _r[6000] = ((renpy.random.randrange(0x8000) % 100) + 1)\n"
            "    if not ((_r[6000] <= 40)):") in scene_2500
    assert "_load 10 -21416" not in scene_2500
    assert "_load 10 44120" not in scene_2500
    assert "_load 10 4416 _r[802] 300 0 0" in scene_2500
    first_select = next(item for item in story_tsc.instructions()
                        if item.opcode == 14)
    prompt = menu_text(story_tsc.string(first_select.operands[1]))
    assert ("$ jump_back_point = renpy.game.log.current.identifier\n"
            "    $ forest_choice_prompt = "
            "renpy.translation.translate_string(%r)\n" % prompt in story)
    for number, index in enumerate(first_select.operands[7:9]):
        choice = menu_text(story_tsc.string(index))
        target = first_select.operands[2 + number]
        assert ("%r:\n            $ _r[2] = %d\n"
                "            jump _2100_L_%06x" %
                (choice, number, target)) in story
    credits = scenes[[p.stem for p in files].index("5000")]
    credits_tsc = read_tsc(files[[p.stem for p in files].index("5000")])
    assert "    _osize 40 25" in credits
    credit_text = next(credits_tsc.string(item.operands[5])
                       for item in credits_tsc.instructions()
                       if item.opcode == 32 and item.operands[0] == 40)
    assert "    _oload 40 400 270 0 0 %r" % credit_text in credits
    assert 'color = "#C8AF00"' in RSCRIPT_OBJECTS
    assert "font = forest_current_font()" in RSCRIPT_OBJECTS
    assert "xmaximum = font_size * persistent.forest_line_chars" in RSCRIPT_OBJECTS
    assert "persistent.forest_text_size // 22" in RSCRIPT_OBJECTS
    assert "parse_rscript_text(repr(args.Text), True)" in RSCRIPT_OBJECTS
    assert "screen say(who, what, center=False):" in FOREST_COMPAT
    assert "text_align (0.5 if center else 0.0)" in FOREST_COMPAT
    assert ('background Transform("images/grps/tbox01/back.png", '
            'alpha=persistent.textbox_opacity)' in FOREST_COMPAT)
    assert "xpos text_indent + 1" in FOREST_COMPAT
    assert "xsize persistent.forest_line_chars * persistent.forest_text_size" in FOREST_COMPAT
    assert "screen forest_title_preferences():" in FOREST_COMPAT
    assert "default persistent.forest_progress_backup = None" in FOREST_COMPAT
    assert ('default persistent.forest_text_font = '
            '"fonts/NotoSansCJKjp-Regular.otf"' in FOREST_COMPAT)
    assert "def forest_fonts():" in FOREST_COMPAT
    assert "def forest_cycle_font(step):" in FOREST_COMPAT
    assert 'text "字体 [forest_font_name()]"' in FOREST_COMPAT
    assert FOREST_COMPAT.count("font forest_current_font()") == 4
    assert "forest_save_progress()" in FOREST_COMPAT
    assert "forest_load_progress()" in FOREST_COMPAT
    assert "forest_clear_progress()" in FOREST_COMPAT
    assert 'return ShowMenu("forest_title_preferences")' in FOREST_COMPAT
    assert '"images/grps/gf%03d.png" % forest_speaker' in FOREST_COMPAT
    assert "default forest_speaker_visible = False" in FOREST_COMPAT
    assert "if forest_speaker_visible and forest_speaker is not None:" in FOREST_COMPAT
    assert "elif forest_speaker_visible and who:" in FOREST_COMPAT
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
    assert 'return ShowMenu("preferences")' in FOREST_COMPAT
    assert 'return ShowMenu("forest_title_preferences")' in FOREST_COMPAT
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
    assert '"gui/rscript_cursor.png", 0, 0' in (
        ROOT / "runtime" / "cursor.rpy").read_text(encoding="utf-8")
    with Image.open(ROOT / "runtime" / "gui" / "rscript_cursor.png") as cursor:
        assert cursor.format == "PNG" and cursor.size == (32, 32)
        assert cursor.getbbox() is not None
    assert ('execute=execute_forest_setclksys, lint=lint_undef)'
            in FOREST_COMPAT)
    assert "'label main_menu:\\n'" in builder
    assert "'define config.version = \"1.0\"\\n'" in builder
    with TemporaryDirectory() as temporary:
        patch_scr = Path(temporary) / "scr"
        patch_scr.mkdir()
        source = resources / "scr" / "2100.tsc"
        patched = source.read_text(encoding="utf-8")
        first = next(line for line in patched.splitlines()
                     if line.startswith("*TXT "))
        changed = first.rsplit('"', 2)
        changed[-2] = "^g999TRANSLATED"
        (patch_scr / source.name).write_text(
            patched.replace(first, '"'.join(changed), 1), encoding="utf-8")
        old = next(value for (key, value) in scene_strings(source).items()
                   if key[1] == "say")
        assert language_patch_strings(resources / "scr", patch_scr)[old] == \
            "^g999TRANSLATED"
        first_voice = next(line for line in patched.splitlines()
                           if line.startswith("*voice "))
        first_voice_wait = next(line for line in patched.splitlines()
                                if line == "*voice_wait")
        fonts = "\n".join(
            '*font %d 175 50 0 0 "%sAdded subtitle"' %
            (layer, "^cy" if layer == 49 else "^ck")
            for layer in range(45, 50))
        clears = "\n".join("*cls %d 0" % layer for layer in range(45, 50))
        subtitle_patch = patched.replace(
            first_voice, first_voice + "\n" + fonts, 1).replace(
                first_voice_wait,
                first_voice_wait + "\n" + clears + "\n*wait 20", 1)
        subtitle_patch = subtitle_patch.replace(first, '"'.join(changed), 1)
        (patch_scr / source.name).write_text(subtitle_patch, encoding="utf-8")
        replacements, insertions = language_patch_data(resources / "scr",
                                                        patch_scr)
        commands = [command
                    for group in insertions[source.name].values()
                    for command in group]
        assert sum(command.startswith("_oload ") for command in commands) == 5
        assert sum(command.startswith("_cls ") for command in commands) == 5
        assert commands.count("_wait 20") == 1
        compiled_patch = compile_scene(
            source,
            language_texts={"english": replacements[source.name]},
            language_insertions={"english": insertions[source.name]})
        assert "{'english': '^g999TRANSLATED'}.get(_preferences.language" in \
            compiled_patch
        assert "if _preferences.language == 'english':" in compiled_patch
        assert "_oload 49 175 50 0 0 '^cyAdded subtitle'" in compiled_patch
        invalid_patch = subtitle_patch.replace(
            first_voice, first_voice + "\n*voice 999 0 0 0", 1)
        (patch_scr / source.name).write_text(invalid_patch, encoding="utf-8")
        try:
            language_patch_data(resources / "scr", patch_scr)
        except ValueError as error:
            assert "changes scenario structure" in str(error)
        else:
            raise AssertionError("language patch added a gameplay instruction")
    print("OK: lowered %d Forest TSC files to rscript RPY" % len(scenes))


if __name__ == "__main__":
    main()
