#!/usr/bin/env python3
"""Generate a Khime Ren'Py 8 project from converted resources and TSC."""

from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import (assemble_port, validate_resources, copy_file,
                        clear_script_cache, reject_legacy_paths)  # noqa: E402
from port_resources import parse_language_options  # noqa: E402
from tsc_patches import scenario_sources  # noqa: E402
from khime_tsc import compile_scene  # noqa: E402
from zero import prepare_zero, install_zero  # noqa: E402


def build_khime(resources: Path, project: Path, force: bool = False,
                languages: list[str] | None = None,
                zero_resources: Path | None = None,
                zero_languages: list[str] | None = None) -> int:
    resources = resources.resolve()
    project = project.resolve()
    reject_legacy_paths(project / "game", ("zero_config.rpy", "zero_config.rpyc"))
    scripts = scenario_sources(resources / "scr")
    marker, patches = parse_language_options(languages or [])
    zero_marker, zero_patches = parse_language_options(zero_languages or [])
    if zero_marker:
        raise ValueError("--khime-zero-language requires NAME=PATCH_DIR")
    if zero_patches and zero_resources is None:
        raise ValueError("--khime-zero-language requires --khime-zero")
    zero_content = None
    if zero_resources is not None:
        zero_resources = zero_resources.resolve()
        zero_content = prepare_zero(zero_resources, zero_patches)
    validate_resources(resources, directories=(
        "grpe", "grpf", "grpo", "grpo_ex", "grpo_tp", "grpp",
        "grps", "bgm", "voice", "wav", "mov"))
    scenes = {"scr/%s.rpy" % source.stem: compile_scene(
        source, patches=patches, zero_title=zero_resources is not None)
        for source in scripts}
    assemble_port(resources, project, scenes, Path(__file__).parent,
                  marker, patches, force=force,
                  android=Path(__file__).parent / "android",
                  extra_languages=[name for name, _ in zero_patches])

    game = project / "game"
    assets = Path(__file__).parent / "assets"
    copy_file(assets / "icon.ico", project / "icon.ico", force)
    copy_file(assets / "icon.png", game / "icon.png", force)
    if zero_resources is not None:
        install_zero(zero_resources, zero_patches, game, zero_content, force)
        for language, _ in zero_patches:
            if language not in {name for name, _ in patches}:
                target = game / "tl" / language / "rscript_strings.rpy"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("translate %s python:\n    pass\n" % language, encoding="utf-8")
    (game / "engine/zero_config.rpy").write_text(
        "init 1 python:\n    khime_zero_available = %r\n" % (zero_resources is not None),
        encoding="utf-8")
    clear_script_cache(game / "engine/zero_config.rpy")

    print("Wrote %s: %d Khime scenes%s" %
          (project, len(scripts), " + Khime Zero 2001" if zero_content else ""))
    return len(scripts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Khime for Ren'Py 8")
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--language", metavar="NAME[=PATCH_DIR]",
                        action="append", default=[])
    parser.add_argument("--khime-zero", type=Path, metavar="RESOURCE_DIR",
                        help="include Khime Zero scr/2001.tsc after unlocking 9105")
    parser.add_argument("--khime-zero-language", metavar="NAME=PATCH_DIR",
                        action="append", default=[])
    args = parser.parse_args(argv)
    try:
        build_khime(args.resources, args.project, args.force, args.language,
                    args.khime_zero, args.khime_zero_language)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
