#!/usr/bin/env python3
"""Assemble a Ren'Py project from prepared RScript-port resources."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from install_runtime import install, clear_script_cache  # noqa: E402
from effect_compat import flatten_unsupported_effects  # noqa: E402
from text_compat import flatten_unsupported_text_controls  # noqa: E402
from grps_layout import collect_layout  # noqa: E402
from port_resources import convert_masks, read_keywords  # noqa: E402


PORT_VERSION = "1.2"
ANDROID_VERSION_CODE = 12


def install_version(project: Path, force: bool = False) -> None:
    destination = project / "game/port_version.rpy"
    content = 'define config.version = "%s"\n' % PORT_VERSION
    if destination.exists() and destination.read_text(encoding="utf-8") != content and not force:
        raise FileExistsError("refusing to overwrite different file: %s" % destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    clear_script_cache(destination)
    android = project / "android.json"
    if android.is_file():
        settings = json.loads(android.read_text(encoding="utf-8"))
        settings["version"] = PORT_VERSION
        settings["numeric_version"] = max(int(settings.get("numeric_version", 1)),
                                          ANDROID_VERSION_CODE)
        android.write_text(json.dumps(settings, indent=4, ensure_ascii=False) + "\n",
                           encoding="utf-8")


def install_android(source: Path, project: Path, force: bool = False) -> None:
    destination = project / "android.json"
    settings = json.loads((source / "android.json").read_text(encoding="utf-8"))
    if destination.is_file():
        # Retain local package/signing/build settings; only versions are shared.
        settings.update(json.loads(destination.read_text(encoding="utf-8")))
    destination.write_text(json.dumps(settings, indent=4, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    install_version(project, force)
    for name in ("android-icon_background.png", "android-icon_foreground.png"):
        copy_file(source / name, project / name, force)


RESOURCE_TARGETS = {
    "grpe": "images/grpe",
    "grpf": "images/grpf",
    "grpo": "images/grpo",
    "grpo_ex": "images/grpo_ex",
    "grpo_tp": "images/grpo_tp",
    "grpp": "images/grpp",
    "grps": "images/grps",
    "bgm": "bgm",
    "voice": "voice",
    "wav": "wav",
    "mov": "mov",
}
ALLOWED_SUFFIXES = {
    "grpe": {".png"},
    "grpf": {".png"},
    "grpo": {".png"},
    "grpo_ex": {".png"},
    "grpo_tp": {".png"},
    "grpp": {".png"},
    "grps": {".png"},
    "bgm": {".ogg", ".wav"},
    "voice": {".ogg", ".wav"},
    "wav": {".ogg", ".wav"},
    "mov": {".mpg"},
}


def copy_file(source: Path, target: Path, force: bool) -> None:
    if target.exists() and source.samefile(target):
        return
    if target.exists() and target.read_bytes() != source.read_bytes() and not force:
        raise FileExistsError("refusing to overwrite different file: %s" % target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    clear_script_cache(target)


def copy_tree(source: Path, target: Path, suffixes: set[str], force: bool) -> int:
    if not source.is_dir():
        return 0
    copied = 0
    for path in sorted(item for item in source.rglob("*") if item.is_file()):
        if path.suffix.lower() not in suffixes:
            continue
        if path.suffix.lower() == ".wav" and path.with_suffix(".ogg").is_file():
            continue  # Embedded Ogg was extracted; copy the playable file only.
        relative = path.relative_to(source)
        if path.suffix.lower() == ".mpg":
            relative = relative.with_suffix(".mpg")
        copy_file(path, target / relative, force)
        copied += 1
    return copied


def write_scenario(content: str, destination: Path, resources: Path,
                   force: bool = False, preserve_dynamic: bool = False) -> None:
    result = flatten_unsupported_effects(content, resources,
                                         preserve_dynamic=preserve_dynamic)
    result = flatten_unsupported_text_controls(result)
    if destination.exists() and destination.read_text(encoding="utf-8") != result and not force:
        raise FileExistsError("refusing to overwrite different file: %s" % destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(result, encoding="utf-8")
    clear_script_cache(destination)


def copy_scenarios(source: Path, target: Path, resources: Path,
                   force: bool) -> int:
    copied = 0
    for path in sorted(source.rglob("*.rpy")):
        destination = target / path.relative_to(source)
        write_scenario(path.read_text(encoding="utf-8"), destination, resources, force)
        copied += 1
    return copied


def install_base(resources: Path, project: Path, force: bool = False,
                 image_folders: tuple[str, ...] = ()) -> tuple[int, int]:
    """Install the shared base; a game's overlay is applied only afterwards."""
    resources = resources.resolve()
    project = project.resolve()
    game = project / "game"
    layout = "define rscript_grps_layout = %r\n" % collect_layout(resources)

    game.mkdir(parents=True, exist_ok=True)
    install_version(project, force)
    installed = install(project, force=force)
    copied = 0
    notice = Path(__file__).parent / "android" / "notice.png"
    for name in ("android-presplash.png", "android-downloading.png"):
        copy_file(notice, project / name, force)
        copied += 1
    for name, destination in RESOURCE_TARGETS.items():
        copied += copy_tree(resources / name, game / destination,
                            ALLOWED_SUFFIXES[name], force)
    for name in image_folders:
        copied += copy_tree(resources / name, game / "images" / name,
                            {".png"}, force)
    # Canvas origins are part of the converted resources, not optional artwork.
    for name in (*RESOURCE_TARGETS, *image_folders):
        if not name.startswith("grp"):
            continue
        for metadata in (resources / name).rglob(".meta.xml"):
            copy_file(metadata, game / "images" / name /
                      metadata.relative_to(resources / name), force)
            copied += 1
    convert_masks(resources / "grps", game / "images" / "grps")
    copied += copy_tree(resources / "wav", game / "audio", {".ogg"}, force)
    keywords = resources / "keywords.json"
    if keywords.is_file():
        read_keywords(keywords)  # Validate before enabling clickable links.
        copy_file(keywords, game / "keywords.json", force)
        copied += 1
    for source in sorted((Path(__file__).parent / "game").glob("*.rpy")):
        copy_file(source, game / source.name, force)
        copied += 1
    for source in sorted((Path(__file__).parent / "fonts").iterdir()):
        if source.is_file():
            copy_file(source, game / "fonts" / source.name, force)
            copied += 1
    destination = game / "grps_layout.rpy"
    if destination.exists() and destination.read_text(encoding="utf-8") != layout and not force:
        raise FileExistsError("refusing to overwrite different file: %s" % destination)
    destination.write_text(layout, encoding="utf-8")
    copied += 1
    return len(installed), copied


def build(resources: Path, project: Path, force: bool = False,
          scenarios: Path | None = None) -> tuple[int, int]:
    scenarios = scenarios or resources / "scenario"
    if not any(scenarios.glob("*.rpy")):
        raise FileNotFoundError(
            "game-specific TSC lowerer produced no scenario/*.rpy files: %s" %
            scenarios)
    installed, copied = install_base(resources, project, force)
    copied += copy_scenarios(scenarios, project / "game" / "scenario",
                            resources, force)
    return installed, copied


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assemble a Ren'Py 8 project from prepared resources")
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        runtime_count, copied = build(args.resources, args.project, args.force)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print("Installed %d runtime files and copied %d prepared files into %s" %
          (runtime_count, copied, args.project / "game"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
