#!/usr/bin/env python3
"""CannonBall's legacy CodeX dialect on the shared Ren'Py template."""

import argparse
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import assemble_port, validate_resources, install_icon
from port_resources import parse_language_options
from tsc_compiler import compile_overlays
from ui_layout import extract_native_ui, native_layouts


def correct_text_controls(scenes):
    # Correct only confirmed translation typos, not numeric ^g arguments.
    corrections = (
        ("tl/zh/scr/6101.rpy", "^g033宰了弗克斯巴特。^g这次定要宰了她。",
         "^g033宰了弗克斯巴特。^n这次定要宰了她。"),
    )
    for filename, before, after in corrections:
        if filename in scenes:
            old = "    _say %r\n" % before
            new = ("    # CannonBall source typo corrected: %s -> %s\n" %
                   (before, after)) + "    _say %r\n" % after
            scenes[filename] = scenes[filename].replace(old, new)


def build_cannonball(resources, project, force=False, languages=(), exe=None):
    resources, project = Path(resources).resolve(), Path(project).resolve()
    marker, patches = parse_language_options(list(languages))
    for directory in (resources, *(directory for _, directory in patches)):
        if project == directory or project.is_relative_to(directory):
            raise ValueError("output must not be inside original/patch resources")
    validate_resources(resources, directories=("scr", "grpe", "grpo", "grps", "bgm", "voice", "wav"),
                       patterns=("grpe/0901.*", "bgm/Track01.wav", "voice/**/*.ogg"))
    se_directory = "wav" if any((resources / "wav").glob("*.ogg")) else "wav/wav"
    if not any((resources / se_directory).glob("*.ogg")):
        raise FileNotFoundError("converted sound effects missing: %s" % (resources / se_directory))
    scenes = compile_overlays(resources, patches, adapter="pre-codex")
    correct_text_controls(scenes)
    if exe is not None:
        report = extract_native_ui(exe, resources)
        if not report["layouts"]:
            raise ValueError("EXE build not supported for automatic UI extraction; run tools/inspect_rscript_ui.py for references")
        layouts = report["layouts"]
        for message in report["unresolved"]:
            print("NOTE: " + message)
    else:
        layouts = native_layouts(resources)
    with TemporaryDirectory(prefix="cannonball-port-") as temporary:
        temporary = Path(temporary)
        prepared = temporary / "resources"
        prepared.mkdir()
        # Only engine resource directories, never patch backups or native saves.
        for source in resources.iterdir():
            if source.is_dir() and (source.name.startswith("grp") or source.name in
                                    {"scr", "bgm", "voice", "wav", "mov"}):
                (prepared / source.name).symlink_to(source, target_is_directory=True)
        if (resources / "keywords.json").is_file():
            (prepared / "keywords.json").symlink_to(resources / "keywords.json")
        overlay = temporary / "overlay/game"
        overlay.mkdir(parents=True)
        for source in (Path(__file__).parent / "game").glob("*.rpy"):
            (overlay / source.name).symlink_to(source)
        (overlay / "audio_paths.rpy").write_text(
            'init -99 python:\n    rscript_se_format = %r\n' % (se_directory + "/%04d.ogg"),
            encoding="utf-8")
        (overlay / "native_ui.rpy").write_text(
            'init 10 python:\n    rscript_ui["layouts"] = %r\n' % layouts, encoding="utf-8")
        assemble_port(prepared, project, scenes, overlay.parent, marker, patches, force=force)
    install_icon(Path(__file__).parent / "assets/2.ico", project, force)
    print("Wrote %s: %d original scenes, %d language packages" %
          (project, len(list((resources / "scr").glob("*.tsc"))), len(patches)))
    return scenes


def main():
    parser = argparse.ArgumentParser(description="Build CannonBall for Ren'Py 8 from current TSC")
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--exe", type=Path, help="optional read-only native UI extraction and verification")
    parser.add_argument("--language", action="append", default=[], metavar="NAME[=PATCH_DIR]")
    args = parser.parse_args()
    try:
        build_cannonball(args.resources, args.project, args.force, args.language, args.exe)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
