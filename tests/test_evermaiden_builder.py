#!/usr/bin/env python3
from pathlib import Path
import argparse
import re
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
    title_scene = scenes[[path.stem for path in files].index("0001")]
    assert "    _folder 0 grpo" in title_scene
    assert "    _folder 1 grpe" in title_scene
    for path, scene in zip(files, scenes):
        for target in re.findall(r"^    _insub (\d+)", scene, re.MULTILINE):
            assert "label _%s_%s:" % (path.stem, target) in scene
    assert 'return "%s %s" % (folder_name, stem)' in COMPAT
    assert "return path\n        renpy.log(\"Evermaiden: missing image" not in COMPAT
    builder = (ROOT / "evermaiden" / "build_evermaiden_rscript.py").read_text()
    assert "'    scene onlayer master\\n'" in builder
    assert "'    scene black onlayer black\\n'" in builder
    print("OK: 208 Evermaiden scenes, Chinese text, all opcodes lifted")


if __name__ == "__main__":
    main()
