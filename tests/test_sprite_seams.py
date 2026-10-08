#!/usr/bin/env python3
"""Prove split-sprite resampling artifacts using an isolated GL2 framebuffer."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import shutil
import subprocess
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import install_base, copy_engine_file


def main():
    sdk = Path(sys.argv[1]).resolve()
    with TemporaryDirectory(prefix="sprite-seams-") as temp:
        temp = Path(temp)
        resources, project = temp / "resources", temp / "project"
        resources.mkdir()
        install_base(resources, project, force=True)
        copy_engine_file(ROOT / "tests/renpy_sprite_seams.rpy", project / "game", True)
        for name, top in (("split_top", True), ("split_bottom", False)):
            image = Image.new("RGBA", (800, 600))
            for x in range(100, 700):
                boundary = 301 if x < 400 else 303
                for y in range(100, 500):
                    if (y < boundary) == top:
                        image.putpixel((x, y), (255, 255, 255, 255))
            image.save(project / "game" / (name + ".png"))
        command = [str(sdk / "renpy.sh"), str(project), "run", "--savedir", str(temp / "saves")]
        environment = os.environ | {"SDL_AUDIODRIVER": "dummy", "RENPY_RENDERER": "gl2",
                                    "RENPY_PATH_TO_SAVES": str(temp / "sdk-saves"),
                                    "RENPY_SKIP_SPLASHSCREEN": "1", "RENPY_SKIP_MAIN_MENU": "1",
                                    "RENPY_PERFORMANCE_TEST": "0"}
        if shutil.which("xvfb-run"):
            command = ["xvfb-run", "-a", *command]
            environment["SDL_VIDEODRIVER"] = "x11"
        result = subprocess.run(command, timeout=45, text=True, capture_output=True,
                                env=environment)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "OK: split sprite seam native framebuffer" in result.stdout, result.stdout
        print(result.stdout.strip())


if __name__ == "__main__":
    main()
