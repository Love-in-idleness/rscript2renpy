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
        (game / "engine").mkdir()
        shutil.copy2(ROOT / "runtime/__init__.py", game / "engine/__init__.py")
        for name in ("00_debug.rpy", "00_rscript_wrap.rpy", "01_util.rpy", "05_rscript_text.rpy",
                     "rscript_wrap.py"):
            shutil.copy2(ROOT / "runtime" / name, game / "engine" / name)
        shutil.copy2(ROOT / "tests" / "renpy_text_wrap.rpy", game)
        for name in ("NotoSansCJKjp-Regular.otf", "NotoSansCJK-Light.ttc",
                     "NotoSerifCJK-Regular.ttc", "simhei.ttf"):
            shutil.copy2(ROOT / "port_template/fonts" / name, game / "fonts")
        subprocess.run([str(sdk / "renpy.sh"), temporary, "wraptest"], check=True)


if __name__ == "__main__":
    main()
