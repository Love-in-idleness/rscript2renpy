#!/usr/bin/env python3
"""Generate a Khime Ren'Py 8 project from converted resources and TSC."""

from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import build, install_android, copy_file, clear_script_cache  # noqa: E402
from port_resources import (parse_language_options, read_keywords,
                            copy_language_assets, write_language_config)  # noqa: E402
from khime_tsc import compile_scene  # noqa: E402
from zero import prepare_zero, install_zero  # noqa: E402


def build_khime(resources: Path, project: Path, force: bool = False,
                languages: list[str] | None = None,
                zero_resources: Path | None = None,
                zero_languages: list[str] | None = None) -> int:
    resources = resources.resolve()
    project = project.resolve()
    scripts = sorted((resources / "scr").glob("*.tsc"))
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
    if not scripts:
        raise FileNotFoundError("current command TSC files missing: %s" %
                                (resources / "scr" / "*.tsc"))
    for folder in ("grpe", "grpf", "grpo", "grpo_ex", "grpo_tp", "grpp",
                   "grps", "bgm", "voice", "wav", "mov"):
        if not (resources / folder).is_dir():
            raise FileNotFoundError("converted resource directory missing: %s" %
                                    (resources / folder))

    # Compile all scripts before writing into the destination.
    with TemporaryDirectory() as temporary:
        scenario = Path(temporary)
        for source in scripts:
            (scenario / (source.stem + ".rpy")).write_text(
                compile_scene(source, patches=patches,
                              zero_title=zero_resources is not None), encoding="utf-8")
        build(resources, project, force=force, scenarios=scenario)

    game = project / "game"
    install_android(Path(__file__).parent / "android", project, force)
    assets = Path(__file__).parent / "assets"
    copy_file(assets / "icon.ico", project / "icon.ico", force)
    copy_file(assets / "icon.png", game / "icon.png", force)
    for source in (Path(__file__).parent / "game").glob("*.rpy"):
        copy_file(source, game / source.name, force)
    keywords = {None: read_keywords(resources / "keywords.json")}
    for language, patch in patches:
        copy_language_assets(patch, language, game)
        keywords[language] = read_keywords(patch / "keywords.json")
    labels = [(None, marker or "Original")] + [(name, name) for name, _ in patches]
    if zero_resources is not None:
        install_zero(zero_resources, zero_patches, game, zero_content, force)
        for language, _ in zero_patches:
            if language not in {name for name, _ in labels}:
                labels.append((language, language))
                target = game / "tl" / language / "rscript_strings.rpy"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("translate %s python:\n    pass\n" % language, encoding="utf-8")
    (game / "zero_config.rpy").write_text(
        "init 1 python:\n    khime_zero_available = %r\n" % (zero_resources is not None),
        encoding="utf-8")
    clear_script_cache(game / "zero_config.rpy")
    write_language_config(game, labels,
                          {name: entries for name, entries in keywords.items()
                           if entries})

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
