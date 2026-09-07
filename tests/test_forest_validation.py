#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forest"))
from build_forest_rscript import validate_inputs  # noqa: E402


def main() -> None:
    with TemporaryDirectory() as temporary:
        base = Path(temporary)
        resources, game = base / "resources", base / "project" / "game"
        for name in ("scr", "grpe", "grpo", "grpo_bg", "grpo_bu",
                     "grpo_ci", "grpo_f", "grps", "wav", "bgm",
                     "voice", "mov"):
            (resources / name).mkdir(parents=True)
        game.mkdir(parents=True)
        (game / "gui.rpy").write_text("", encoding="utf-8")
        (resources / "scr" / "0000.tsc").write_text(
            ";@gsc-structure-v1 size=0 fnv1a64=0\n", encoding="utf-8")
        for path in (resources / "grpe" / "9001.png",
                     resources / "bgm" / "Track01.ogg",
                     resources / "wav" / "0001.ogg",
                     resources / "voice" / "0001.ogg",
                     resources / "mov" / "0001.webm",
                     resources / "mov" / "0002.mpg"):
            path.write_bytes(b"fixture")
        validate_inputs(resources, game)
        (resources / "scr" / "0000.tsc").unlink()
        (resources / "scr" / "0000.gsc").write_bytes(b"not accepted")
        try:
            validate_inputs(resources, game)
        except FileNotFoundError as error:
            assert "scr/*.tsc" in str(error)
        else:
            raise AssertionError("GSC-only input was accepted")
        (resources / "scr" / "0000.gsc").unlink()
        (resources / "scr" / "0000.tsc").write_text(
            ";@gsc-structure-v1 size=0 fnv1a64=0\n", encoding="utf-8")
        (resources / "voice" / "0001.ogg").unlink()
        try:
            validate_inputs(resources, game)
        except FileNotFoundError as error:
            assert "voice/*.ogg" in str(error)
        else:
            raise AssertionError("missing converted voice was accepted")
    print("OK: Forest input validation")


if __name__ == "__main__":
    main()
