#!/usr/bin/env python3
"""Check shared controls against the installed Ren'Py native actions."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    with TemporaryDirectory(prefix="rscript-touch-") as temporary:
        game = Path(temporary) / "game"
        game.mkdir()
        shutil.copy2(ROOT / "port_template/game/touch_controls.rpy", game)
        shutil.copy2(ROOT / "tests/renpy_touch_controls.rpy", game)
        subprocess.run([str(Path(sys.argv[1]) / "renpy.sh"), temporary,
                        "touchtest"], check=True)


if __name__ == "__main__":
    main()
