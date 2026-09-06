#!/usr/bin/env python3
"""Install the generic RScript runtime into a Ren'Py project."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"


def install(project: Path, force: bool = False) -> list[Path]:
    game = project / "game"
    if not game.is_dir():
        raise ValueError("Ren'Py game directory not found: %s" % game)

    installed = []
    for source in sorted(RUNTIME.glob("*.rpy")):
        target = game / source.name
        if target.exists() and target.read_bytes() != source.read_bytes() and not force:
            raise FileExistsError("refusing to overwrite different file: %s" % target)
        shutil.copy2(source, target)
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
