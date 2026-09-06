#!/usr/bin/env python3
"""Validate Forest's GSC corpus when legally extracted resources are present."""

from pathlib import Path
import argparse
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forest"))
from forest_gsc import read_gsc  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("resources", type=Path)
    args = parser.parse_args()

    files = sorted((args.resources / "scr").glob("*.gsc"))
    if not files:
        parser.error("no GSC files found under resources/scr")
    total = 0
    for path in files:
        gsc = read_gsc(path)
        instructions = gsc.instructions()
        assert instructions
        assert instructions[-1].offset + instructions[-1].size == len(gsc.code)
        total += len(instructions)
    print("OK: %d GSC files / %d instructions" % (len(files), total))


if __name__ == "__main__":
    main()
