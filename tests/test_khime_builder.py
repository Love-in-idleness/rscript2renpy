#!/usr/bin/env python3
"""Smoke-check a converted Khime resource set without copying its assets."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "khime"))
from khime_tsc import compile_scene  # noqa: E402


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
    assert "_cls 1 19\n    _load 1 5043 400 300 19 0" in effect
    print("OK: compiled %d Khime TSC files and title click flow" % len(sources))


if __name__ == "__main__":
    main()
