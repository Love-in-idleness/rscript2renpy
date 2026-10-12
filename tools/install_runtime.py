#!/usr/bin/env python3
"""Install the generic RScript runtime into a Ren'Py project."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
sys.path.insert(0, str(ROOT / "port_template"))
from file_install import copy_file, clear_script_cache, reject_overlap, write_text as write_script

def reject_legacy_paths(game: Path, paths) -> None:
    old = [str(game / path) for path in paths if (game / path).exists()]
    if old:
        raise FileExistsError("legacy layout is not supported; generate into a fresh project:\n- " +
                              "\n- ".join(old))

def install(project: Path, force: bool = False) -> list[Path]:
    reject_overlap(RUNTIME, project)
    game = project / "game"
    if not game.is_dir():
        raise ValueError("Ren'Py game directory not found: %s" % game)

    sources = sorted(path for path in RUNTIME.rglob("*") if path.is_file())
    legacy_paths = [source.relative_to(RUNTIME) for source in sources]
    reject_legacy_paths(game, legacy_paths + [path.with_suffix(".rpyc")
                                            for path in legacy_paths if path.suffix == ".rpy"])
    installed = []
    for source in sources:
        relative = source.relative_to(RUNTIME)
        target = game / "engine" / relative
        copy_file(source, target, force)
        installed.append(target)
    return installed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        installed = install(args.project, args.force)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print("Installed %d runtime files into %s" %
          (len(installed), args.project / "game"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
