#!/usr/bin/env python3
"""Install the generic RScript runtime into a Ren'Py project."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"

def clear_script_cache(path: Path) -> None:
    if path.suffix == ".rpy":
        path.with_suffix(".rpyc").unlink(missing_ok=True)

def retire_legacy(path: Path, replacement: Path, force: bool) -> None:
    """Remove only a known generated old path, after its replacement exists."""
    if path == replacement:
        return
    if path.is_file():
        if path.read_bytes() != replacement.read_bytes() and not force:
            raise FileExistsError("refusing to remove different legacy file: %s" % path)
        path.unlink()
    clear_script_cache(path)

def install(project: Path, force: bool = False) -> list[Path]:
    game = project / "game"
    if not game.is_dir():
        raise ValueError("Ren'Py game directory not found: %s" % game)

    installed = []
    for source in sorted(path for path in RUNTIME.rglob("*") if path.is_file()):
        relative = source.relative_to(RUNTIME)
        target = game / "engine" / relative
        legacy = game / relative
        if legacy.is_file() and legacy.read_bytes() != source.read_bytes() and not force:
            raise FileExistsError("refusing to overwrite different legacy file: %s" % legacy)
        if target.exists() and target.read_bytes() != source.read_bytes() and not force:
            raise FileExistsError("refusing to overwrite different file: %s" % target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        clear_script_cache(target)
        retire_legacy(legacy, target, force)
        installed.append(target)
    gui = game / "gui"
    if gui.is_dir() and not any(gui.iterdir()):
        gui.rmdir()
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
