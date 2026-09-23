#!/usr/bin/env python3
"""Generate a Khime Ren'Py 8 project from converted resources and TSC."""

from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import build, copy_file  # noqa: E402
from khime_tsc import compile_scene  # noqa: E402


def build_khime(resources: Path, project: Path, force: bool = False) -> int:
    resources = resources.resolve()
    project = project.resolve()
    scripts = sorted((resources / "scr").glob("*.tsc"))
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
                compile_scene(source), encoding="utf-8")
        build(resources, project, force=force, scenarios=scenario)

    game = project / "game"
    for source in (Path(__file__).parent / "game").glob("*.rpy"):
        copy_file(source, game / source.name, force)
    copy_file(ROOT / "forest" / "gui.rpy", game / "gui.rpy", force)
    for name in ("NotoSansCJKjp-Regular.otf", "NotoSansCJK-Light.ttc",
                 "NotoSerifCJK-Regular.ttc", "NotoSans.txt"):
        copy_file(ROOT / "forest" / "fonts" / name,
                  game / "fonts" / name, force)

    print("Wrote %s: %d Khime scenes" % (project, len(scripts)))
    return len(scripts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Khime for Ren'Py 8")
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        build_khime(args.resources, args.project, args.force)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
