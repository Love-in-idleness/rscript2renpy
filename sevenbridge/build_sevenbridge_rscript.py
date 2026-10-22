#!/usr/bin/env python3
"""Build the Japanese SevenBridge on the shared Ren'Py 8 template."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import assemble_port, validate_resources
from tsc_compiler import compile_overlays


def build_sevenbridge(resources, project, force=False):
    resources, project = Path(resources).resolve(), Path(project).resolve()
    validate_resources(resources, directories=(
        "scr", "grpe", "grpo", "grpo_bu", "grpo_ex", "grps", "bgm", "voice", "wav"),
        files=("grpe/3001.png",),
        alternatives=(("bgm/Track01.ogg", "bgm/Track01.wav"),))
    scenes = compile_overlays(resources, adapter="sevenbridge")
    assemble_port(resources, project, scenes, Path(__file__).parent,
                  marker="日本語", force=force)
    print("Wrote %s: %d Japanese scenes" % (project, len(scenes)))
    return scenes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resources", type=Path, help="prepared Japanese game resources with current TSC")
    parser.add_argument("project", type=Path, help="output Ren'Py project")
    parser.add_argument("--force", action="store_true", help="replace differing generated files")
    args = parser.parse_args()
    try:
        build_sevenbridge(args.resources, args.project, args.force)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
