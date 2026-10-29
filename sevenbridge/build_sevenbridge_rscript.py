#!/usr/bin/env python3
"""Build SevenBridge and optional language patches on the shared Ren'Py 8 template."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import assemble_port, validate_resources
from file_install import reject_overlap
from port_resources import parse_language_options
from tsc_compiler import compile_scene
from tsc_patches import language_patch_data, menu_text, scenario_sources


def build_sevenbridge(resources, project, force=False, languages=()):
    resources, project = Path(resources).resolve(), Path(project).resolve()
    marker, patches = parse_language_options(list(languages))
    for directory in (resources, *(directory for _, directory in patches)):
        reject_overlap(directory, project)
    validate_resources(resources, directories=(
        "scr", "grpe", "grpo", "grpo_bu", "grpo_ex", "grps", "bgm", "voice", "wav"),
        files=("grpe/3001.png",),
        alternatives=(("bgm/Track01.ogg", "bgm/Track01.wav"),))
    patch_data = {language: language_patch_data(
        resources / "scr", directory / "scr", dialect="modern", menu_transform=menu_text)
        for language, directory in patches}
    scenes = {}
    for source in scenario_sources(resources / "scr"):
        texts, insertions = ({language: data[index][source.name]
                              for language, data in patch_data.items() if source.name in data[index]}
                             for index in (0, 1))
        scenes["scr/%s.rpy" % source.stem] = compile_scene(
            source, adapter="sevenbridge", language_texts=texts, language_insertions=insertions)
    if "scr/0210.rpy" in scenes:
        # Enter the CG body without re-entering the gallery return override.
        scenes["scr/0210.rpy"] = scenes["scr/0210.rpy"].replace(
            "label _0210:\n", "label _0210:\nlabel sevenbridge_cg_body:\n", 1)
    assemble_port(resources, project, scenes, Path(__file__).parent,
                  marker=marker or "日本語", patches=patches, force=force)
    print("Wrote %s: %d generated scripts, %d language packages" %
          (project, len(scenes), len(patches)))
    return scenes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resources", type=Path, help="prepared Japanese game resources with current TSC")
    parser.add_argument("project", type=Path, help="output Ren'Py project")
    parser.add_argument("--force", action="store_true", help="replace differing generated files")
    parser.add_argument("--language", action="append", default=[], metavar="NAME[=PATCH_DIR]",
                        help="original language label or prepared language patch directory")
    args = parser.parse_args()
    try:
        build_sevenbridge(args.resources, args.project, args.force, args.language)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
