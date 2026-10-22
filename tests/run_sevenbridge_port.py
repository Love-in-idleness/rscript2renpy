#!/usr/bin/env python3
"""Run SevenBridge SDK checks using disposable scripts and isolated saves."""
import os
import argparse
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("sdk", type=Path)
    parser.add_argument("--capture", type=Path, help="also run isolated UI captures into this directory")
    args = parser.parse_args()
    source, sdk = args.project.resolve(), args.sdk.resolve()
    with TemporaryDirectory(prefix="sevenbridge-sdk-") as temporary:
        project = Path(temporary)
        game = project / "game"
        game.mkdir()
        for path in (source / "game").iterdir():
            if path.name in ("cache", "saves"):
                continue
            if path.name in ("engine", "scr", "tl"):
                shutil.copytree(path, game / path.name,
                                ignore=shutil.ignore_patterns("*.rpyc", "__pycache__"))
            elif path.is_dir():
                (game / path.name).symlink_to(path, target_is_directory=True)
        shutil.copyfile(Path(__file__).with_name("renpy_sevenbridge_port.rpy"),
                        game / "sevenbridge_test.rpy")
        environment = os.environ | {"SDL_AUDIODRIVER": "dummy",
                                   "RENPY_PATH_TO_SAVES": str(project / "sdk-saves")}
        subprocess.run([str(sdk / "renpy.sh"), str(project), "lint"],
                       check=True, env=environment, timeout=120)
        subprocess.run([str(sdk / "renpy.sh"), str(project), "sevenbridgetest",
                        "--savedir", str(project / "test-saves")],
                       check=True, env=environment, timeout=120)
        if args.capture:
            destination = args.capture.resolve()
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(Path(__file__).with_name("renpy_sevenbridge_capture.rpy"),
                            game / "sevenbridge_capture.rpy")
            subprocess.run([str(sdk / "renpy.sh"), str(project), "run",
                            "--savedir", str(project / "capture-saves")],
                           check=True, timeout=60, env=environment | {
                               "SEVENBRIDGE_CAPTURE": str(destination),
                               "RENPY_SKIP_SPLASHSCREEN": "1", "RENPY_PERFORMANCE_TEST": "0"})
            for name in ("title.png", "dialogue.png", "preferences.png", "save.png", "load.png"):
                if not (destination / name).is_file():
                    raise AssertionError("missing capture: " + name)


if __name__ == "__main__":
    main()
