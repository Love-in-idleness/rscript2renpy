#!/usr/bin/env python3
"""Evermaiden: modern shared template plus native canvas/presentation defaults."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import assemble_port, validate_resources, install_icon
from tsc_compiler import compile_overlays
from port_resources import parse_language_options

IMAGE_FOLDERS = ("grpo_bg", "grpo_bu0", "grpo_bu1", "grpo_cu", "grpo_ef",
                 "grpo_map")


def build_evermaiden(resources, project, force=False, languages=()):
    resources, project = Path(resources).resolve(), Path(project).resolve()
    marker, patches = parse_language_options(list(languages))
    validate_resources(resources, directories=(
        "scr", "grpe", "grpo", "grpo_ex", "grps", "bgm", "voice", "wav", *IMAGE_FOLDERS))
    # Validate every script before touching the generated project.
    scenes = compile_overlays(resources, patches)
    assemble_port(resources, project, scenes, Path(__file__).parent,
                  marker, patches, force=force)
    install_icon(Path(__file__).parent / "assets/L42_EM.ico", project, force)
    print("Wrote %s: %d original scenes, %d language packages" %
          (project, len(list((resources / "scr").glob("*.tsc"))), len(patches)))
    return scenes


def main():
    parser = argparse.ArgumentParser(description="Build Evermaiden for Ren'Py 8 from current TSC")
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--language", action="append", default=[], metavar="NAME[=PATCH_DIR]")
    args = parser.parse_args()
    try:
        build_evermaiden(args.resources, args.project, args.force, args.language)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
