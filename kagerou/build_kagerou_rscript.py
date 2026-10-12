#!/usr/bin/env python3
"""Build Kagerou from current TSC and an audited, read-only native executable."""

import argparse
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import assemble_port, validate_resources
from port_resources import parse_language_options
from tsc_compiler import compile_overlays
from rscript_tsc import read_tsc
from native import NativeImage
from file_install import copy_file, reject_overlap, write_text


BONUS_SCENES = ("0059", "0201", "0301", "0302", *("%04d" % n for n in range(1501, 1512)))


def validate_edition(resources):
    missing = [name for name in BONUS_SCENES if not (resources / "scr" / (name + ".tsc")).is_file()]
    if missing:
        raise ValueError("Kagerou requires ハチポチ特典; missing TSC scenes: " + ", ".join(missing))


def missing_voices(resources, patches=()):
    missing = set()
    for directory in (resources, *(p for _, p in patches)):
        for source in (directory / "scr").glob("*.tsc"):
            for item in read_tsc(source, "kagerou").instructions():
                if item.opcode == 81 and item.operands[1]:
                    group, number = divmod(item.operands[1], 10000)
                    stem = Path("voice/%d/%04d" % (group, number))
                    if not any((root / stem.with_suffix(ext)).is_file()
                               for root in (directory, resources) for ext in (".ogg", ".wav")):
                        missing.add(str(stem))
    return sorted(missing)


def build_kagerou(resources, project, force=False, languages=(), exe=None):
    resources, project = Path(resources).resolve(), Path(project).resolve()
    marker, patches = parse_language_options(list(languages))
    for directory in (resources, *(p for _, p in patches)):
        reject_overlap(directory, project)
    validate_edition(resources)
    validate_resources(resources,
        directories=("scr", "grpe", "grpo", "grpo_bu", "grpo_ex", "grps", "bgm", "voice", "wav"),
        files=("grps/tbox01/back.png", "grps/muscmenu/.meta.xml", "grps/muscmenu/bg.png",
               *("grps/wait%02d/.meta.xml" % n for n in (12, 16, 18, 24))),
        patterns=("grpe/9001.png", "bgm/*.ogg", "voice/*/*.ogg", "wav/*.ogg"))
    image = NativeImage(exe or resources / "kagerou.exe")
    # Fresh-process layout preset 0; persisted native CFG is not imported.
    positions = {slot: image.character_x(slot, layout=0, alternate=False)
                 for slot in range(1, 8)}
    character_layouts = [[{slot: image.character_x(slot, layout=layout, alternate=alternate)
                           for slot in range(1, 8)} for layout in range(9)]
                         for alternate in (False, True)]
    scenes = compile_overlays(resources, patches, adapter="kagerou")
    warnings = ["Bonus-script and music galleries require playthrough verification.",
                "Native transition fidelity and saved CFG layout require manual verification."]
    absent_voices = missing_voices(resources, patches)
    if absent_voices:
        warnings.append("Unresolved voice resources (.ogg/.wav): " + ", ".join(absent_voices))
    for number in (2, 1):
        if not (resources / ("mov/%04d.mpg" % number)).is_file():
            warnings.append("Missing startup movie mov/%04d.mpg; skipped, not replaced." % number)
    with TemporaryDirectory(prefix="kagerou-port-") as temporary:
        temporary = Path(temporary)
        prepared = temporary / "resources"
        prepared.mkdir()
        for source in resources.iterdir():
            if source.is_dir() and (source.name.startswith("grp") or source.name in
                                    {"scr", "bgm", "voice", "wav", "mov"}):
                (prepared / source.name).symlink_to(source, target_is_directory=True)
        overlay = temporary / "overlay/game"
        overlay.mkdir(parents=True)
        for source in (Path(__file__).parent / "game").glob("*.rpy"):
            (overlay / source.name).symlink_to(source)
        (overlay / "native_positions.rpy").write_text(
            'define kagerou_character_x = %r\n'
            'define kagerou_character_layouts = %r\n' % (positions, character_layouts), encoding="utf-8")
        # A new project's own base files are replaced by this adapter's overlay.
        assemble_port(prepared, project, scenes, overlay.parent, marker, patches,
                      force=force or not project.exists())
    copy_file(Path(__file__).parent / "native.py", project / "game/engine/kagerou_native.py", force=True)
    write_text(json.dumps({
        "adapter": "kagerou", "edition": "ハチポチ特典", "exe_sha256": image.sha256,
        "original_scenes": len(list((resources / "scr").glob("*.tsc"))),
        "languages": [name for name, _ in patches],
        "character_x": positions, "warnings": warnings,
    }, ensure_ascii=False, indent=2) + "\n", project / "kagerou-build.json", force=True)
    for message in warnings:
        print("NOTE: " + message)
    print("Wrote %s: %d original scenes, %d language packages" %
          (project, len(list((resources / "scr").glob("*.tsc"))), len(patches)))
    return scenes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--exe", type=Path, help="audited EXE when using a resource-only working copy")
    parser.add_argument("--language", action="append", default=[], metavar="NAME[=PATCH_DIR]")
    args = parser.parse_args()
    try:
        build_kagerou(args.resources, args.project, args.force, args.language, args.exe)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
