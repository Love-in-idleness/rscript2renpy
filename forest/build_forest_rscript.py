#!/usr/bin/env python3
"""Lower LiarsoftTool's current Forest TSC to Jeanne-style rscript RPY."""

from pathlib import Path
import argparse
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import install_base, copy_file, write_scenario  # noqa: E402
from port_resources import (copy_assets, convert_masks, copy_movies,
                            parse_language_options, read_keywords,
                            strip_json_comments, write_language_config,
                            copy_language_assets)  # noqa: E402

from rscript_tsc import E, read_tsc
from tsc_vm import emit_vm, packed
from tsc_patches import (scenario_sources, menu_text,
                         instruction_strings as shared_instruction_strings,
                         scene_strings as shared_scene_strings,
                         language_patch_data as shared_language_patch_data)


COMMANDS = {
    10: "hit", 11: "hitc", 12: "jump", 13: "wait",
    15: "gosub", 16: "return", 17: "backup", 20: "gload", 21: "gcls",
    22: "gmove", 23: "quake", 24: "flash", 26: "queue", 27: "action",
    28: "update", 29: "zupdate", 30: "load", 32: "oload", 33: "move", 34: "movi",
    35: "oaction", 36: "cls", 37: "enabl", 38: "locmode", 39: "draw", 40: "depth",
    41: "group", 42: "tbox", 43: "effect", 44: "effectdep", 45: "tone",
    46: "tonedep", 47: "locgrid", 49: "mode", 50: "backup", 52: "stop",
    55: "makesave", 56: "sysmode", 57: "logflash", 60: "bgm_on",
    61: "bgm_off", 64: "se_off", 65: "movie", 66: "voice",
    67: "voice_off", 68: "se_wait", 69: "voice_wait",
    70: "forest_setclk", 71: "forest_setclksys", 72: "forest_resetclk",
    73: "forest_click", 74: "forest_autoreset", 75: "forest_setlink",
    83: "txcls",
    90: "tboxloc", 91: "texloc",
    92: "tboxback", 93: "cmploc", 94: "tboxcmp", 95: "texcolor",
    96: "texsize", 97: "texfont", 98: "texmode", 99: "texindent", 100: "waitloc",
    103: "waitlod", 104: "waitcol", 120: "osize", 121: "folder", 132: "numenable",
}
PATCH_OVERRIDE_OPCODES = set(COMMANDS) - {
    12, 15, 16, 30, 32, 36, 62, 63, 64, 121,
}


def scene_label(scene: str, offset: int) -> str:
    return "_%s_L_%06x" % (scene, offset)


def instruction_strings(tsc, item):
    return shared_instruction_strings(tsc, item, menu_text)


def scene_strings(source):
    return shared_scene_strings(source, menu_transform=menu_text)


def language_patch_data(base_scr, patch_scr):
    return shared_language_patch_data(
        base_scr, patch_scr, excluded_scenes={"5000.tsc"},
        override_opcodes=PATCH_OVERRIDE_OPCODES, menu_transform=menu_text)


def language_patch_strings(base_scr: Path, patch_scr: Path) -> dict[str, str]:
    replacements, _, _ = language_patch_data(base_scr, patch_scr)
    translations = {}
    for source_name, scene_replacements in replacements.items():
        base = scene_strings(base_scr / source_name)
        for key, new in scene_replacements.items():
            old = base[key]
            previous = translations.get(old)
            if previous is not None and previous != new:
                raise ValueError(
                    "%s translates the same source text inconsistently" %
                    (patch_scr / source_name))
            translations[old] = new
    return translations


def wiki_image_links(entries: list[tuple[str, str, str]]) -> dict[str, str]:
    """Return the links used by Forest's two inline wiki images."""
    anchors = {"keeper": "601", "replay": "603"}
    result = {}
    for _, url, _ in entries:
        anchor = url.rpartition("#")[2]
        number = anchors.get(anchor)
        if number is not None:
            result[number] = url
    return result


def write_language_patch(base: Path, patch: Path, language: str,
                         game: Path) -> None:
    copy_language_assets(patch, language, game)

def patch_text_expression(language_texts, item, kind, default):
    replacements = {
        language: texts[(item.offset, kind)]
        for language, texts in (language_texts or {}).items()
        if (item.offset, kind) in texts
    }
    if not replacements:
        return repr(default), False
    return "%r.get(_preferences.language, %r)" % (replacements, default), True


def compile_scene(source: Path, language: str | None = None,
                  language_texts=None, language_insertions=None,
                  language_operands=None,
                  scene_name: str | None = None) -> str:
    if language and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", language):
        raise ValueError("invalid language name: %s" % language)
    if scene_name and not re.fullmatch(r"[A-Za-z0-9_]+", scene_name):
        raise ValueError("invalid scene name: %s" % scene_name)
    for patch_language in (set(language_texts or {}) |
                           set(language_insertions or {}) |
                           set(language_operands or {})):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", patch_language):
            raise ValueError("invalid language name: %s" % patch_language)
    language_arg = " " + language if language else ""
    tsc = read_tsc(source)
    scene = scene_name or source.stem
    instructions = tsc.instructions()
    targets = {item.operands[0] for item in instructions if item.opcode in (3, 4, 5)}
    for item in instructions:
        if item.opcode == 14:
            for number in range(min(item.operands[0], 5)):
                targets.add(item.operands[2 + number])
    lines = ["# Generated from %s; command offsets are preserved in labels." % source.name,
             "label _%s:" % scene]
    temps: dict[int, str] = {}
    pending_se: str | None = None
    for item in instructions:
        for patch_language, commands in (language_insertions or {}).items():
            added = commands.get(item.offset, ())
            if added:
                lines.append("    if _preferences.language == %r:" %
                             patch_language)
                lines.extend("        " + command for command in added)
        if item.offset in targets:
            lines.extend(("", "label %s:" % scene_label(scene, item.offset)))
        opcode, operands = item.opcode, item.operands
        if opcode & 0xf000:
            lines.extend("    " + line for line in emit_vm(opcode, operands, temps))
            continue
        if opcode == 9:
            temps[operands[0]] = "renpy.random.randrange(0x8000)"
        elif opcode in (3, 4):
            condition = temps.get(0, "0")
            test = "not (%s)" % condition if opcode == 3 else "(%s)" % condition
            lines.extend(("    if %s:" % test, "        jump %s" % scene_label(scene, operands[0])))
        elif opcode == 5:
            lines.append("    jump %s" % scene_label(scene, operands[0]))
        elif opcode == 8:
            lines.append("    return")
        elif opcode == 14:
            count = min(operands[0], 5)
            prompt = menu_text(tsc.string(operands[1]))
            prompt, _ = patch_text_expression(
                language_texts, item, "prompt", prompt)
            result = packed(operands[12])
            lines.append(
                "    $ forest_choice_prompt = rscript_inline_graphics("
                "renpy.translation.translate_string(%s))" %
                prompt)
            choices = []
            for number, index in enumerate(operands[7:7 + count]):
                if index >= len(tsc.strings):
                    continue
                choice = menu_text(tsc.string(index))
                choice, changed = patch_text_expression(
                    language_texts, item, "choice%d" % number, choice)
                if changed or "^g" in choice:
                    variable = "forest_choice_%d" % number
                    lines.append(
                        "    $ %s = rscript_inline_graphics("
                        "renpy.translation.translate_string(%s))" %
                        (variable, choice))
                    caption = "[%s]" % variable
                else:
                    caption = menu_text(tsc.string(index))
                choices.append((number, caption, item.operands[2 + number]))
            lines.append("    menu:")
            for number, caption, branch in choices:
                lines.extend(("        %r:" % caption,
                              "            $ _r[%s] = %d" % (result, number),
                              "            jump %s" % scene_label(scene, branch)))
        elif opcode == 18:
            destination = packed(operands[0])
            for index, value in enumerate(tsc.data(operands[1])):
                lines.append("    $ _r[(%s) + %d] = %d" % (destination, index, value))
        elif opcode == 81:
            name, text = tsc.string(operands[4]), tsc.string(operands[5])
            if re.fullmatch(r"(?:\^c[ygwk])+", name):
                name = ""
            value = (name + "：" if name else "") + text
            value, _ = patch_text_expression(language_texts, item, "say", value)
            if operands[1]:
                lines.append("    _voice %s 0 0 0" % packed(operands[1]))
            lines.append("    _say%s %s" % (language_arg, value))
        elif opcode == 82:
            text = tsc.string(operands[4])
            text, _ = patch_text_expression(language_texts, item, "append", text)
            lines.append("    _append%s %s" % (language_arg, text))
        elif opcode == 32:
            args = " ".join(packed(value) for value in operands[:5])
            text, _ = patch_text_expression(
                language_texts, item, "oload", tsc.string(operands[5]))
            lines.append("    _oload %s %s" % (args, text))
        elif opcode == 121 and operands[1] < len(tsc.strings):
            lines.append("    _forest_folder %s %r" % (packed(operands[0]), tsc.string(operands[1])))
        elif opcode == 15:
            lines.append("    _gosub %s" % packed(operands[0]))
        elif opcode == 16:
            lines.append("    return")
        elif opcode == 12:
            lines.append("    _jump %s" % packed(operands[0]))
        elif opcode == 62:
            pending_se = packed(operands[0])
        elif opcode == 63:
            if pending_se is not None:
                lines.append("    _se 0 %s" % pending_se)
                pending_se = None
            args = " ".join(packed(value) for value in operands)
            lines.append("    _se_on 0 %s" % args)
        elif opcode == 64:
            lines.append("    _se_off 0 %s" % packed(operands[0]))
        elif opcode == 13:
            patched_operands = {
                patch_language: overrides[item.offset]
                for patch_language, overrides in
                (language_operands or {}).items()
                if item.offset in overrides
            }
            if patched_operands:
                for index, (patch_language, values) in enumerate(
                        patched_operands.items()):
                    keyword = "if" if index == 0 else "elif"
                    lines.extend((
                        "    %s _preferences.language == %r:" %
                        (keyword, patch_language),
                        "        _wait %s" % packed(values[0])))
                lines.extend(("    else:",
                              "        _wait %s" % packed(operands[0])))
            else:
                lines.append("    _wait %s" % packed(operands[0]))
        elif opcode in (30, 36):
            values = list(operands)
            # Forest's 2500.tsc contains one mistyped background number. The
            # surrounding loads use 4416 and grpo_bg/4416.png is the asset that
            # exists; 44120 has no corresponding resource.
            if scene == "2500" and item.offset == 0x22366 and values[1] == 44120:
                lines.append(
                    "    # Forest conversion: CG 44120 flattened to 4416 "
                    "because only 4416 exists.")
                values[1] = 4416
            args = " ".join(packed(value) if kind == E else str(value)
                            for kind, value in zip(item.kinds, values))
            lines.append("    _%s %s" % (COMMANDS[opcode], args))
        elif opcode in COMMANDS:
            def statement(values):
                args = " ".join(
                    packed(value) if kind == E else str(value)
                    for kind, value in zip(item.kinds, values))
                return "_%s%s" % (COMMANDS[opcode],
                                   " " + args if args else "")

            patched_operands = {
                patch_language: overrides[item.offset]
                for patch_language, overrides in
                (language_operands or {}).items()
                if item.offset in overrides
            }
            if patched_operands:
                for index, (patch_language, values) in enumerate(
                        patched_operands.items()):
                    keyword = "if" if index == 0 else "elif"
                    lines.extend((
                        "    %s _preferences.language == %r:" %
                        (keyword, patch_language),
                        "        " + statement(values)))
                lines.extend(("    else:", "        " + statement(operands)))
            else:
                lines.append("    " + statement(operands))
        else:
            lines.append("    # unlifted opcode 0x%04x %s" % (opcode, operands))
    for patch_language, commands in (language_insertions or {}).items():
        added = commands.get(tsc.code_size, ())
        if added:
            lines.append("    if _preferences.language == %r:" % patch_language)
            lines.extend("        " + command for command in added)
    emitted = {item.offset for item in instructions}
    for target in sorted(targets - emitted):
        lines.extend(("", "label %s:" % scene_label(scene, target), "    return"))
    lines.append("    return")
    return "\n".join(lines) + "\n"


def compile_credits_scene(source: Path, language: str | None,
                          language_patches: list[tuple[str, Path]]) -> str:
    patched = [(name, root / "scr" / source.name)
               for name, root in language_patches
               if (root / "scr" / source.name).is_file()]
    lines = [
        "# Forest credits select a complete script for the active language.",
        "label _5000:",
        "    $ forest_previous_rollback = _rollback",
        "    $ renpy.block_rollback()",
        "    $ forest_input_locked = True",
        "    $ _rollback = False",
    ]
    for index, (patch_language, _) in enumerate(patched):
        keyword = "if" if index == 0 else "elif"
        lines.extend((
            "    %s _preferences.language == %r:" % (keyword, patch_language),
            "        call _5000_%s" % patch_language,
        ))
    if patched:
        lines.extend(("    else:", "        call _5000_original"))
    else:
        lines.append("    call _5000_original")
    lines.extend((
        "    $ _rollback = forest_previous_rollback",
        "    $ forest_input_locked = False",
        "    $ renpy.block_rollback()",
        "    return",
        "",
    ))
    result = "\n".join(lines)
    result += compile_scene(source, language, scene_name="5000_original")
    for patch_language, patch_source in patched:
        result += "\n" + compile_scene(
            patch_source, scene_name="5000_%s" % patch_language)
    return result


FOREST_COMPAT = (Path(__file__).parent / "game" / "forest_compat.rpy").read_text(
    encoding="utf-8")


def validate_inputs(root: Path) -> None:
    required_dirs = (
        "scr", "grpe", "grpo", "grpo_bg", "grpo_bu", "grpo_ci",
        "grpo_f", "grps", "wav", "bgm", "voice", "mov",
    )
    missing = [str(root / name) for name in required_dirs
               if not (root / name).is_dir()]
    required_assets = (
        root / "grpe" / "9001.png",
        root / "bgm" / "Track01.ogg",
    )
    missing.extend(str(path) for path in required_assets if not path.is_file())
    if not scenario_sources(root / "scr"):
        missing.append(str(root / "scr" / "*.tsc"))
    for folder in ("wav", "voice"):
        if not list((root / folder).glob("*.ogg")):
            missing.append(str(root / folder / "*.ogg"))
    for movie in ("0001", "0002"):
        if not any((root / "mov" / (movie + suffix)).is_file()
                   for suffix in (".mpg", ".MPG")):
            missing.append(str(root / "mov" / (movie + ".mpg")))
    if missing:
        raise FileNotFoundError(
            "resources must be unpacked and converted first; missing:\n- " +
            "\n- ".join(missing))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Build a Forest Ren'Py project from converted resources")
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument(
        "--language", metavar="NAME[=PATCH_DIR]", action="append", default=[],
        help="plain NAME marks _say/_append; NAME=DIR adds a translated patch")
    args = parser.parse_args(argv[1:])
    language_marker, language_patches = parse_language_options(args.language)
    root = args.resources.resolve()
    target = args.project.resolve()
    here = Path(__file__).resolve().parents[1]
    android_source = here / "forest" / "android"
    game = target / "game"
    validate_inputs(root)
    install_base(root, target, force=True,
                 image_folders=("grpo_bg", "grpo_bu", "grpo_ci", "grpo_f"))
    scenario = game / "scenario"
    scenario.mkdir(parents=True, exist_ok=True)
    for name in ("android.json", "android-icon_background.png",
                 "android-icon_foreground.png"):
        shutil.copyfile(android_source / name, target / name)
    language_labels = [(None, language_marker or "Original")]
    language_labels.extend((name, name) for name, _ in language_patches)
    wiki_keywords = {}
    wiki_images = {}
    base_keywords = read_keywords(root / "keywords.json")
    if base_keywords:
        wiki_keywords[None] = base_keywords
        links = wiki_image_links(base_keywords)
        if links:
            wiki_images[None] = links
    for language, patch in language_patches:
        entries = read_keywords(patch / "keywords.json")
        if entries:
            wiki_keywords[language] = entries
            links = wiki_image_links(entries)
            if links:
                wiki_images[language] = links
    write_language_config(game, language_labels, wiki_keywords, wiki_images)
    for overlay in (Path(__file__).parent / "game").glob("*.rpy"):
        copy_file(overlay, game / overlay.name, force=True)
    patch_texts = {}
    patch_insertions = {}
    patch_operands = {}
    for language, patch in language_patches:
        replacements, insertions, overrides = language_patch_data(
            root / "scr", patch / "scr")
        patch_texts[language] = replacements
        patch_insertions[language] = insertions
        patch_operands[language] = overrides
        write_language_patch(root, patch, language, game)
    sources = scenario_sources(root / "scr")
    for source in sources:
        if source.name == "5000.tsc":
            content = compile_credits_scene(
                source, language_marker, language_patches)
            write_scenario(content, scenario / "5000.rpy", root,
                           force=True, preserve_dynamic=True)
            continue
        scene_texts = {
            language: replacements[source.name]
            for language, replacements in patch_texts.items()
            if source.name in replacements
        }
        scene_insertions = {
            language: insertions[source.name]
            for language, insertions in patch_insertions.items()
            if source.name in insertions
        }
        scene_operands = {
            language: overrides[source.name]
            for language, overrides in patch_operands.items()
            if source.name in overrides
        }
        write_scenario(compile_scene(source, language_marker, scene_texts,
                                     scene_insertions, scene_operands),
                       scenario / (source.stem + ".rpy"), root,
                       force=True, preserve_dynamic=True)
    print("Wrote %s: %d rscript scenes" % (target, len(sources)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
