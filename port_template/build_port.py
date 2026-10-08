#!/usr/bin/env python3
"""Assemble a Ren'Py project from prepared RScript-port resources."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from install_runtime import install, clear_script_cache, reject_legacy_paths  # noqa: E402
from effect_compat import flatten_unsupported_effects  # noqa: E402
from text_compat import flatten_unsupported_text_controls  # noqa: E402
from grps_layout import collect_layout  # noqa: E402
from port_resources import (convert_masks, convert_bmp_assets, read_keywords,
                            copy_language_assets, write_language_config)  # noqa: E402
from tsc_patches import scenario_sources  # noqa: E402


PORT_VERSION = "1.3"
ANDROID_VERSION_CODE = 13


def validate_resources(root, *, directories=(), files=(), patterns=(), alternatives=()):
    missing = [str(root / name) for name in directories if not (root / name).is_dir()]
    missing.extend(str(root / name) for name in files if not (root / name).is_file())
    if not scenario_sources(root / "scr"):
        missing.append(str(root / "scr/*.tsc"))
    missing.extend(str(root / pattern) for pattern in patterns if not any(root.glob(pattern)))
    missing.extend(str(root / names[0]) for names in alternatives
                   if not any((root / name).is_file() for name in names))
    if missing:
        raise FileNotFoundError("resources must be unpacked and converted first; missing:\n- " +
                                "\n- ".join(missing))


def assemble_port(resources, project, scenes, overlay, marker=None, patches=(), *,
                  force=False, wiki_images=None, android=None, extra_languages=()):
    """Install already compiled scenes using the same resource/overlay path."""
    if not scenes:
        raise ValueError("no compiled scenes")
    labels = [(None, marker or "Original")] + [(name, name) for name, _ in patches]
    labels.extend((name, name) for name in extra_languages
                  if name not in {language for language, _ in labels})
    keywords, images = {}, {}
    for language, directory in [(None, resources), *patches]:
        entries = read_keywords(directory / "keywords.json")
        if entries:
            keywords[language] = entries
            if wiki_images and (links := wiki_images(entries)):
                images[language] = links
        # Invalid patch metadata must fail before replacing a language package.
        if language is not None:
            collect_layout(directory, fallback=resources)
    install_base(resources, project, force)
    game = project / "game"
    if android:
        install_android(android, project, force)
    for source in (overlay / "game").glob("*.rpy"):
        copy_engine_file(source, game, force)
    for language, patch in patches:
        copy_language_assets(patch, language, game, base=resources)
    for name, content in scenes.items():
        write_scenario(content, game / name, resources, force)
    write_language_config(game, labels, keywords, images)


def install_version(project: Path, force: bool = False) -> None:
    reject_legacy_paths(project / "game", ("port_version.rpy", "port_version.rpyc"))
    destination = project / "game/engine/port_version.rpy"
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



def copy_file(source: Path, target: Path, force: bool) -> None:
    if target.exists() and source.samefile(target):
        return
    if target.exists() and target.read_bytes() != source.read_bytes() and not force:
        raise FileExistsError("refusing to overwrite different file: %s" % target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    clear_script_cache(target)


def install_icon(source: Path, project: Path, force: bool = False) -> None:
    """Use one ICO source for Ren'Py's desktop, mobile and web icon inputs."""
    from PIL import Image

    with Image.open(source) as original:
        icon = original.convert("RGBA")
    copy_file(source, project / "icon.ico", force)
    with TemporaryDirectory(prefix="port-icons-") as temporary:
        temporary = Path(temporary)
        large = icon.resize((1024, 1024), Image.Resampling.LANCZOS)
        foreground = Image.new("RGBA", (432, 432))
        foreground.paste(icon.resize((288, 288), Image.Resampling.LANCZOS), (72, 72))
        ios = Image.new("RGB", (1024, 1024), "black")
        ios.paste(large, mask=large.getchannel("A"))
        for name, image in (("game/icon.png", icon), ("icon.icns", large),
                            ("web-icon.png", icon.resize((512, 512), Image.Resampling.LANCZOS)),
                            ("ios-icon.png", ios),
                            ("android-icon_foreground.png", foreground),
                            ("android-icon_background.png", Image.new("RGB", (432, 432), "black"))):
            generated = temporary / Path(name).name
            image.save(generated)
            copy_file(generated, project / name, force)


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
        copy_file(path, target / relative, force)
        copied += 1
    return copied


def copy_engine_file(source: Path, game: Path, force: bool) -> None:
    destination = game / "engine" / source.name
    reject_legacy_paths(game, (source.name, source.with_suffix(".rpyc").name))
    copy_file(source, destination, force)


def write_scenario(content: str, destination: Path, resources: Path,
                   force: bool = False, preserve_dynamic: bool = True) -> None:
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


def install_base(resources: Path, project: Path, force: bool = False) -> tuple[int, int]:
    """Install the shared base; a game's overlay is applied only afterwards."""
    resources = resources.resolve()
    project = project.resolve()
    game = project / "game"
    layout = "define rscript_grps_layout = %r\n" % collect_layout(resources)

    game.mkdir(parents=True, exist_ok=True)
    reject_legacy_paths(game, ("images", "scenario", "audio", "grps_layout.rpy",
                               "grps_layout.rpyc", "language_config.rpy", "language_config.rpyc"))
    install_version(project, force)
    installed = install(project, force=force)
    copied = 0
    notice = Path(__file__).parent / "android" / "notice.png"
    for name in ("android-presplash.png", "android-downloading.png"):
        copy_file(notice, project / name, force)
        copied += 1
    # Discover converted resources, retaining every relative directory/name.
    # No fixed list of grp* folders, and no duplicate images/ or audio/ tree.
    for folder in sorted(path for path in resources.iterdir() if path.is_dir()):
        if folder.name in {"engine", "scr", "scenario", "saves", "tl"} or folder.name.startswith("."):
            continue
        output = game / folder.name
        copied += copy_tree(folder, output, {".png", ".jpg", ".webp", ".ogg", ".wav", ".mpg"}, force)
        for metadata in folder.rglob(".meta.xml"):
            copy_file(metadata, output / metadata.relative_to(folder), force)
            copied += 1
        convert_bmp_assets(folder, output)
        convert_masks(folder, output)
    keywords = resources / "keywords.json"
    if keywords.is_file():
        read_keywords(keywords)  # Validate before enabling clickable links.
        copy_file(keywords, game / "keywords.json", force)
        copied += 1
    for source in sorted((Path(__file__).parent / "game").glob("*.rpy")):
        copy_engine_file(source, game, force)
        copied += 1
    for source in sorted((Path(__file__).parent / "fonts").iterdir()):
        if source.is_file():
            copy_file(source, game / "fonts" / source.name, force)
            copied += 1
    destination = game / "engine/grps_layout.rpy"
    if destination.exists() and destination.read_text(encoding="utf-8") != layout and not force:
        raise FileExistsError("refusing to overwrite different file: %s" % destination)
    destination.write_text(layout, encoding="utf-8")
    clear_script_cache(destination)
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
    copied += copy_scenarios(scenarios, project / "game" / "scr",
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
