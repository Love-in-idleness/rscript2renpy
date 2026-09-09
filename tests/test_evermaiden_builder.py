#!/usr/bin/env python3
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evermaiden"))
from build_evermaiden_rscript import COMPAT, compile_scene


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("resources", type=Path)
    resources = parser.parse_args().resources.resolve()
    files = sorted((resources / "scr").glob("*.tsc"))
    scenes = [compile_scene(path) for path in files]
    compiled = "".join(scenes)
    assert len(scenes) == 208
    assert compiled.count("    _say chinese ") == 14014
    assert compiled.count("    _append chinese ") == 167
    assert "_say japanese" not in compiled
    assert "unsupported opcode" not in compiled
    assert "$ _r[0] = 1" in scenes[[path.stem for path in files].index("4330")]
    assert 'return "%s %s" % (folder_name, stem)' in COMPAT
    assert "return path\n        renpy.log(\"Evermaiden: missing image" not in COMPAT
    print("OK: 208 Evermaiden scenes, Chinese text, all opcodes lifted")


if __name__ == "__main__":
    main()
