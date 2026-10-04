#!/usr/bin/env python3
"""Generate a Khime Ren'Py 8 project from converted resources and TSC."""

from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import struct
import sys

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import build, copy_file  # noqa: E402
from port_resources import (parse_language_options, read_keywords,
                            copy_language_assets, write_language_config)  # noqa: E402
from khime_tsc import compile_scene  # noqa: E402


def copy_khime_bmp_titles(patch: Path, target: Path) -> None:
    source_dir = patch / "grpo_tp"
    if not source_dir.is_dir():
        return
    for source in sorted(source_dir.iterdir()):
        if not source.is_file() or source.suffix.lower() != ".bmp":
            continue
        data = source.read_bytes()
        if (len(data) < 54 or data[:2] != b"BM" or
                struct.unpack_from("<H", data, 28)[0] != 32 or
                struct.unpack_from("<I", data, 30)[0] != 0 or
                struct.unpack_from("<i", data, 22)[0] <= 0):
            raise ValueError("unsupported Khime title BMP: %s" % source)
        with Image.open(source) as bmp:
            offset = struct.unpack_from("<I", data, 10)[0]
            image = Image.frombytes("RGBA", bmp.size, data[offset:],
                                    "raw", "BGRA", 0, -1)
        image.putalpha(ImageOps.invert(image.getchannel("A")))
        target.mkdir(parents=True, exist_ok=True)
        image.save(target / (source.stem + ".png"), "PNG")


def build_khime(resources: Path, project: Path, force: bool = False,
                languages: list[str] | None = None) -> int:
    resources = resources.resolve()
    project = project.resolve()
    scripts = sorted((resources / "scr").glob("*.tsc"))
    marker, patches = parse_language_options(languages or [])
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
                compile_scene(source, patches=patches), encoding="utf-8")
        build(resources, project, force=force, scenarios=scenario)

    game = project / "game"
    for source in (Path(__file__).parent / "game").glob("*.rpy"):
        copy_file(source, game / source.name, force)
    keywords = {None: read_keywords(resources / "keywords.json")}
    for language, patch in patches:
        copy_language_assets(patch, language, game)
        copy_khime_bmp_titles(patch, game / "tl" / language / "images" / "grpo_tp")
        keywords[language] = read_keywords(patch / "keywords.json")
    write_language_config(game, [(None, marker or "Original")] +
                          [(name, name) for name, _ in patches],
                          {name: entries for name, entries in keywords.items()
                           if entries})

    print("Wrote %s: %d Khime scenes" % (project, len(scripts)))
    return len(scripts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Khime for Ren'Py 8")
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--language", metavar="NAME[=PATCH_DIR]",
                        action="append", default=[])
    args = parser.parse_args(argv)
    try:
        build_khime(args.resources, args.project, args.force, args.language)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
