#!/usr/bin/env python3
"""Forest policies on top of the shared early CodeX compiler and template."""

from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import assemble_port, validate_resources  # noqa: E402
from port_resources import parse_language_options  # noqa: E402
from tsc_compiler import compile_scene as compile_tsc, EARLY_PATCH_OPCODES  # noqa: E402
from tsc_patches import (scenario_sources, menu_text,
                         language_patch_data as shared_language_patch_data)  # noqa: E402


def language_patch_data(base_scr, patch_scr):
    return shared_language_patch_data(
        base_scr, patch_scr, excluded_scenes={"5000.tsc"},
        override_opcodes=EARLY_PATCH_OPCODES, menu_transform=menu_text)


def wiki_image_links(entries):
    anchors = {"keeper": "601", "replay": "603"}
    return {anchors[anchor]: url for _, url, _ in entries
            if (anchor := url.rpartition("#")[2]) in anchors}


def forest_operands(scene, item, args, lines):
    # The source typo refers to a nonexistent resource; adjacent loads use 4416.
    if scene == "2500" and item.offset == 0x22366 and item.operands[1] == 44120:
        lines.append("    # Forest conversion: CG 44120 flattened to 4416 because only 4416 exists.")
        args[1] = "4416"
    return args


def compile_scene(source, language=None, language_texts=None,
                  language_insertions=None, language_operands=None,
                  scene_name=None):
    return compile_tsc(
        source, adapter="early", statement_prefix="forest", language=language,
        scene_name=scene_name,
        language_texts=language_texts, language_insertions=language_insertions,
        language_operands=language_operands, operand_patch=forest_operands)


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


def validate_inputs(root):
    validate_resources(
        root, directories=("scr", "grpe", "grpo", "grpo_bg", "grpo_bu",
                           "grpo_ci", "grpo_f", "grps", "wav", "bgm", "voice", "mov"),
        files=("grpe/9001.png", "bgm/Track01.ogg"),
        patterns=("wav/*.ogg", "voice/*.ogg"),
        alternatives=tuple(("mov/%s.mpg" % name, "mov/%s.MPG" % name)
                           for name in ("0001", "0002")))


def main(argv):
    parser = argparse.ArgumentParser(
        description="Build a Forest Ren'Py project from converted resources")
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument(
        "--language", metavar="NAME[=PATCH_DIR]", action="append", default=[],
        help="plain NAME marks _say/_append; NAME=DIR adds a translated patch")
    args = parser.parse_args(argv[1:])
    marker, patches = parse_language_options(args.language)
    root, target = args.resources.resolve(), args.project.resolve()
    validate_inputs(root)
    patch_data = {language: language_patch_data(root / "scr", patch / "scr")
                  for language, patch in patches}
    scenes = {}
    for source in scenario_sources(root / "scr"):
        if source.name == "5000.tsc":
            content = compile_credits_scene(source, marker, patches)
        else:
            text, insertions, operands = (
                {language: data[index][source.name]
                 for language, data in patch_data.items() if source.name in data[index]}
                for index in range(3))
            content = compile_scene(source, marker, text, insertions, operands)
        scenes["scr/%s.rpy" % source.stem] = content
    assemble_port(root, target, scenes, Path(__file__).parent,
                  marker, patches, force=True, wiki_images=wiki_image_links,
                  android=Path(__file__).parent / "android")
    print("Wrote %s: %d rscript scenes" % (target, len(scenes)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
