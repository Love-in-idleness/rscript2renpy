#!/usr/bin/env python3
"""Render metadata UI in an isolated fixture, never run the source game's script."""
from pathlib import Path
import argparse
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import install_base, copy_engine_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sdk", type=Path)
    parser.add_argument("resources", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--game", choices=("evermaiden", "cannonball"), default="evermaiden")
    args = parser.parse_args()
    sdk, resources, output = (p.resolve() for p in (args.sdk, args.resources, args.output))
    fixture = output / "resources"
    fixture.mkdir(parents=True, exist_ok=True)
    grps = fixture / "grps"
    if not grps.exists():
        grps.symlink_to(resources / "grps", target_is_directory=True)
    project = output / "project"
    install_base(fixture, project, force=True)
    copy_engine_file(ROOT / args.game / "game/options.rpy", project / "game", True)
    if args.game == "cannonball":
        sys.path.insert(0, str(ROOT / "cannonball"))
        from ui_layout import extract_native_ui
        report = extract_native_ui(resources / "Cannonball.exe", resources)
        assert report["layouts"], report["unresolved"]
        (project / "game/engine/native_ui.rpy").write_text(
            'init 10 python:\n    rscript_ui["layouts"] = %r\n' % report["layouts"])
    copy_engine_file(ROOT / "tests/renpy_grps_capture.rpy", project / "game", True)
    subprocess.run([str(sdk / "renpy.sh"), str(project), "run", "--savedir", str(output / "saves")],
                   check=True, timeout=45, env=os.environ | {
                       "SDL_AUDIODRIVER": "dummy",
                       "RENPY_RENDERER": "gl2", "RENPY_PATH_TO_SAVES": str(output / "sdk-saves"),
                       "RENPY_SKIP_SPLASHSCREEN": "1", "RENPY_PERFORMANCE_TEST": "0"})


if __name__ == "__main__":
    main()
