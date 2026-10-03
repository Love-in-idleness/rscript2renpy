#!/usr/bin/env python3
"""Exercise real Ren'Py font shaping/layout without opening a game window."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    sdk = Path(sys.argv[1])
    with TemporaryDirectory(prefix="rscript-wrap-") as temporary:
        game = Path(temporary) / "game"
        (game / "fonts").mkdir(parents=True)
        for name in ("00_debug.rpy", "00_rscript_wrap.rpy", "01_util.rpy", "05_rscript_text.rpy",
                     "rscript_wrap.py"):
            shutil.copy2(ROOT / "runtime" / name, game / name)
        shutil.copy2(ROOT / "tests" / "renpy_text_wrap.rpy", game)
        shutil.copy2(ROOT / "forest/fonts/NotoSansCJKjp-Regular.otf", game / "fonts")
        shutil.copy2(ROOT / "forest/fonts/simhei.ttf", game / "fonts")
        subprocess.run([str(sdk / "renpy.sh"), temporary, "wraptest"], check=True)


if __name__ == "__main__":
    main()
