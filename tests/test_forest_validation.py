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
        for name in ("gui.rpy", "audio.rpy", "character.rpy"):
            (game / name).write_text("", encoding="utf-8")
        for path in (resources / "scr" / "0000.gsc",
                     resources / "grpe" / "9001.png",
                     resources / "bgm" / "Track01.ogg",
                     resources / "wav" / "0001.ogg",
                     resources / "voice" / "0001.ogg",
                     resources / "mov" / "0001.webm",
                     resources / "mov" / "0002.mpg"):
            path.write_bytes(b"fixture")
        validate_inputs(resources, game)
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
