#!/usr/bin/env python3
"""Print native UI evidence as JSON; no source/executable/resource mutation."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "port_template"), str(ROOT / "cannonball")]
from ui_layout import extract_native_ui


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path)
    parser.add_argument("resources", type=Path)
    args = parser.parse_args()
    try:
        report = extract_native_ui(args.exe, args.resources)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
