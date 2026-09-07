#!/usr/bin/env python3
"""Check the editable TSC boundary against an installed LiarsoftTool 2.0."""

from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forest"))
from build_forest_rscript import compile_scene  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("liarsofttool", type=Path)
    parser.add_argument("gsc", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory() as temporary:
        tsc = Path(temporary) / (args.gsc.stem + ".tsc")
        subprocess.run([
            str(args.liarsofttool.resolve()), "--gsc-to-tsc", "-o", str(tsc),
            str(args.gsc.resolve()),
        ], check=True)
        direct = compile_scene(args.gsc.resolve())
        through_tsc = compile_scene(tsc, args.liarsofttool.resolve())
        assert direct.splitlines()[1:] == through_tsc.splitlines()[1:]
        lines = tsc.read_text(encoding="utf-8").splitlines()
        dialogue = next(index for index, line in enumerate(lines)
                        if line.startswith("\\"))
        lines[dialogue] += "[rscript2renpy-edit]"
        tsc.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert "[rscript2renpy-edit]" in compile_scene(
            tsc, args.liarsofttool.resolve())
    print("OK: LiarsoftTool 2.0 TSC round-trip and readable edits")


if __name__ == "__main__":
    main()
