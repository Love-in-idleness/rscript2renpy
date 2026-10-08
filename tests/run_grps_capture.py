#!/usr/bin/env python3
"""Render metadata UI in an isolated fixture, never run the source game's script."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import install_base, copy_engine_file


def main():
    sdk, resources, output = (Path(arg).resolve() for arg in sys.argv[1:4])
    fixture = output / "resources"
    fixture.mkdir(parents=True, exist_ok=True)
    grps = fixture / "grps"
    if not grps.exists():
        grps.symlink_to(resources / "grps", target_is_directory=True)
    project = output / "project"
    install_base(fixture, project, force=True)
    copy_engine_file(ROOT / "evermaiden/game/options.rpy", project / "game", True)
    copy_engine_file(ROOT / "tests/renpy_grps_capture.rpy", project / "game", True)
    subprocess.run([str(sdk / "renpy.sh"), str(project), "run", "--savedir", str(output / "saves")],
                   check=True, timeout=45, env=os.environ | {
                       "SDL_AUDIODRIVER": "dummy",
                       "RENPY_RENDERER": "gl2", "RENPY_PATH_TO_SAVES": str(output / "sdk-saves"),
                       "RENPY_SKIP_SPLASHSCREEN": "1", "RENPY_PERFORMANCE_TEST": "0"})


if __name__ == "__main__":
    main()
