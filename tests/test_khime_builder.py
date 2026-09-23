#!/usr/bin/env python3
"""Smoke-check a converted Khime resource set without copying its assets."""

from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "khime"))
from khime_tsc import compile_scene  # noqa: E402
from build_khime_rscript import build_khime  # noqa: E402


def main() -> None:
    sources = sorted((Path(sys.argv[1]) / "scr").glob("*.tsc"))
    assert sources, "Khime TSC files missing"
    for source in sources:
        output = compile_scene(source)
        assert output.startswith("# Generated from ")
        assert "label _%s:" % source.stem in output
    title = compile_scene(next(path for path in sources if path.stem == "0101"))
    assert "_khime_folder 0 'grpo_tp'" in title
    assert "_khime_setclk 41 1 3 0" in title
    assert "_khime_click 0 0 0" in title
    setup = compile_scene(next(path for path in sources if path.stem == "0111"))
    assert "_khime_locmode 0 1 1" in setup
    effect = compile_scene(next(path for path in sources if path.stem == "1102"))
    assert "# Khime conversion: _cls effect 19 flattened to 0" in effect
    assert "_cls 1 0" in effect
    assert "# Khime conversion: _load effect 19 flattened to 0" in effect
    assert "_load 1 5043 400 300 0 0" in effect
    credits = compile_scene(next(path for path in sources if path.stem == "1110"))
    assert "# Khime conversion: _oload effect 4 flattened to 0" in credits
    assert "_oload 20 400 188 0 0 '^fm企画・シナリオ'" in credits
    with TemporaryDirectory() as temporary:
        resources = Path(temporary) / "resources"
        project = Path(temporary) / "project"
        (resources / "scr").mkdir(parents=True)
        shutil.copy2(next(path for path in sources if path.stem == "1110"),
                     resources / "scr" / "1110.tsc")
        for folder in ("grpe", "grpf", "grpo", "grpo_ex", "grpo_tp",
                       "grpp", "grps", "bgm", "voice", "wav", "mov"):
            (resources / folder).mkdir()
        build_khime(resources, project)
        script = (project / "game" / "script.rpy").read_text(encoding="utf-8")
        assert "scene onlayer master\n    scene black onlayer black" in script
    print("OK: compiled %d Khime TSC files and title click flow" % len(sources))


if __name__ == "__main__":
    main()
