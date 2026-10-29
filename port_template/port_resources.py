"""Shared converted assets, keyword JSON and language option validation."""

from pathlib import Path
from fnmatch import fnmatch
import json
import re
import shutil
from grps_layout import collect_layout, IMAGE_SUFFIXES
from file_install import copy_file, reject_overlap, write_text

RESOURCE_PATTERNS = (*("*" + suffix for suffix in IMAGE_SUFFIXES),
                     "*.ogg", "*.wav", "*.mpg", ".meta.xml")


def write_language_config(game: Path, labels, keywords, images=None) -> None:
    write_text(
        "init -90 python:\n"
        "    rscript_languages = %r\n"
        "    rscript_wiki_keywords = %r\n"
        "    rscript_wiki_images = %r\n" % (labels, keywords, images or {}),
        game / "engine/language_config.rpy", force=True)


def copy_language_assets(patch: Path, language: str, game: Path, base: Path | None = None) -> None:
    # This directory is owned by the generated language package, not saves.
    reject_overlap(patch, game.parent)
    target = game / "tl" / language
    if target.is_dir():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    write_text("translate %s python:\n    pass\n" % language, target / "rscript_strings.rpy")
    write_text(
        "init 1 python:\n    rscript_grps_language_layouts[%r] = %r\n" %
        (language, collect_layout(patch, fallback=base)), target / "grps_layout.rpy")
    for folder in sorted(path for path in patch.iterdir() if path.is_dir()):
        if folder.name in {"engine", "scr", "scenario", "saves", "tl"} or folder.name.startswith("."):
            continue
        output = target / folder.name
        copy_assets(folder, RESOURCE_PATTERNS, output)
    if (patch / "keywords.json").is_file():
        read_keywords(patch / "keywords.json")
        copy_file(patch / "keywords.json", target / "keywords.json", force=True, metadata=False)

def strip_json_comments(text: str) -> str:
    """Remove // comments without touching // inside JSON strings."""
    result = []
    index = 0
    in_string = escaped = False
    while index < len(text):
        char = text[index]
        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
        elif char == '"':
            in_string = True
            result.append(char)
            index += 1
        elif char == "/" and index + 1 < len(text) and \
                text[index + 1] == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
        else:
            result.append(char)
            index += 1
    return "".join(result)


def read_keywords(source: Path) -> list[tuple[str, str, str]]:
    """Read and validate a Forest patch's commented keywords.json."""
    if not source.is_file():
        return []
    try:
        data = json.loads(strip_json_comments(
            source.read_text(encoding="utf-8-sig")))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("invalid keywords file %s: %s" % (source, error)) \
            from error
    if not isinstance(data, list):
        raise ValueError("%s must contain a JSON array" % source)
    result = []
    for index, entry in enumerate(data, 1):
        if not (isinstance(entry, list) and len(entry) == 3 and
                all(isinstance(value, str) and value for value in entry)):
            raise ValueError(
                "%s entry %d must be three non-empty strings" %
                (source, index))
        sentence, url, link_text = entry
        if link_text not in sentence:
            raise ValueError(
                "%s entry %d link text is not in its sentence" %
                (source, index))
        result.append((sentence, url, link_text))
    return result


def parse_language_options(specs: list[str]) -> tuple[str | None,
                                                       list[tuple[str, Path]]]:
    marker = None
    patches = []
    names = set()
    for spec in specs:
        if "=" not in spec:
            if marker is not None:
                raise ValueError("only one plain --language marker is allowed")
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", spec):
                raise ValueError("invalid language name: %s" % spec)
            marker = spec
            continue
        language, folder = spec.split("=", 1)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", language):
            raise ValueError("invalid language name: %s" % language)
        if language in names:
            raise ValueError("duplicate language patch: %s" % language)
        if not folder:
            raise ValueError("language patch directory is empty: %s" % language)
        patch = Path(folder).resolve()
        if not patch.is_dir():
            raise FileNotFoundError("language patch directory not found: %s" % patch)
        names.add(language)
        patches.append((language, patch))
    if marker in names:
        raise ValueError("original language and patch use the same name: %s" % marker)
    return marker, patches


def copy_assets(source: Path, pattern: str | tuple[str, ...], target: Path, *,
                force: bool = True, metadata: bool = False) -> int:
    """Copy one or several filename patterns with a single directory walk."""
    if not source.is_dir():
        return 0
    patterns = (pattern,) if isinstance(pattern, str) else pattern
    patterns = tuple(item.lower() for item in patterns)
    assets = sorted(asset for asset in source.rglob("*")
                    if asset.is_file() and any(fnmatch(asset.name.lower(), item)
                                              for item in patterns))
    ogg = {(asset.parent, asset.stem.lower()) for asset in assets
           if asset.suffix.lower() == ".ogg"}
    copied = 0
    for asset in assets:
        if asset.suffix.lower() == ".wav" and (asset.parent, asset.stem.lower()) in ogg:
            continue
        output = target / asset.relative_to(source)
        check_native_image(asset, output)
        copy_file(asset, output, force=force, metadata=metadata)
        copied += 1
    return copied


def check_native_image(asset: Path, output: Path) -> None:
    """Fail clearly on unprepared CodeX BMPs and obsolete converted outputs."""
    if asset.suffix.lower() not in (".bmp", ".msk"):
        return
    if asset.suffix.lower() == ".bmp":
        with asset.open("rb") as source:
            header = source.read(54)
        if (len(header) >= 54 and header[:2] == b"BM" and
                int.from_bytes(header[14:18], "little") == 40 and
                int.from_bytes(header[28:30], "little") == 32 and
                int.from_bytes(header[30:34], "little") == 0):
            raise ValueError("CodeX BMP needs LiarsoftTool --unpack-only first "
                             "(use a resource working copy): %s" % asset)
    png_name = (asset.stem + ".png").lower()
    old_png = next((path for path in output.parent.glob("*")
                    if path.is_file() and path.name.lower() == png_name), None)
    if old_png and not any(path.is_file() and path.name.lower() == png_name
                           for path in asset.parent.iterdir()):
        raise ValueError("obsolete converted PNG shadows %s: %s; use a fresh "
                         "output project or remove that old generated PNG" % (asset, old_png))


def copy_movies(source: Path, target: Path, clear: bool = False) -> None:
    if not source.is_dir():
        return
    reject_overlap(source, target)
    target.mkdir(parents=True, exist_ok=True)
    if clear:
        for obsolete in target.iterdir():
            if (obsolete.is_file() and
                    obsolete.suffix.lower() in {".mpg", ".webm"}):
                obsolete.unlink()
    for asset in sorted(source.iterdir()):
        if asset.is_file() and asset.suffix.lower() == ".mpg":
            copy_file(asset, target / asset.name, force=True, metadata=False)
