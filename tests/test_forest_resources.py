#!/usr/bin/env python3
"""Validate current command-based Forest TSC files when resources are present."""

from pathlib import Path
import argparse
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forest"))
from forest_tsc import read_tsc  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("resources", type=Path)
    args = parser.parse_args()

    files = sorted((args.resources / "scr").glob("*.tsc"))
    if not files:
        parser.error("no TSC files found under resources/scr")
    total = 0
    for path in files:
        tsc = read_tsc(path)
        instructions = tsc.instructions()
        assert instructions
        assert instructions[-1].offset + instructions[-1].size == tsc.code_size
        total += len(instructions)
    print("OK: %d TSC files / %d instructions" % (len(files), total))

if __name__ == "__main__":
    main()
