#!/usr/bin/env python3
"""Evermaiden: modern shared template plus native canvas/presentation defaults."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import install_base, install_icon, copy_engine_file, write_scenario, clear_script_cache
from modern_tsc import compile_overlays
from port_resources import (parse_language_options, copy_language_assets,
                            write_language_config, read_keywords)

IMAGE_FOLDERS = ("grpo_bg", "grpo_bu0", "grpo_bu1", "grpo_cu", "grpo_ef",
                 "grpo_map")


def build_evermaiden(resources, project, force=False, languages=()):
    resources, project = Path(resources).resolve(), Path(project).resolve()
    marker, patches = parse_language_options(list(languages))
    for folder in ("scr", "grpe", "grpo", "grpo_ex", "grps", "bgm", "voice", "wav",
                   *IMAGE_FOLDERS):
        if not (resources / folder).is_dir():
            raise FileNotFoundError("converted resource directory missing: %s" % (resources / folder))
    # Validate every script before touching the generated project.
    scenes = compile_overlays(resources, patches)
    install_base(resources, project, force)
    install_icon(Path(__file__).parent / "assets/L42_EM.ico", project, force)
    game = project / "game"
    for source in (Path(__file__).parent / "game").glob("*.rpy"):
        copy_engine_file(source, game, force)
    keywords = {None: read_keywords(resources / "keywords.json")}
    for language, patch in patches:
        copy_language_assets(patch, language, game, base=resources)
        keywords[language] = read_keywords(patch / "keywords.json")
    for name, content in scenes.items():
        write_scenario(content, game / name, resources, force)
    write_language_config(game, [(None, marker or "Original")] +
                          [(language, language) for language, _ in patches],
                          {language: value for language, value in keywords.items() if value})
    clear_script_cache(game / "engine/language_config.rpy")
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
