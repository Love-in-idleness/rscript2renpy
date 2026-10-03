"""Shared converted assets, keyword JSON and language option validation."""

from pathlib import Path
import json
import re
import shutil
from PIL import Image

IMAGE_FOLDERS = ("grpe", "grpf", "grpo", "grpo_bg", "grpo_bu", "grpo_ci",
                 "grpo_f", "grpo_ex", "grpo_tp", "grpp", "grps")


def write_language_config(game: Path, labels, keywords, images=None) -> None:
    (game / "language_config.rpy").write_text(
        "init -90 python:\n"
        "    rscript_languages = %r\n"
        "    rscript_wiki_keywords = %r\n"
        "    rscript_wiki_images = %r\n" % (labels, keywords, images or {}),
        encoding="utf-8")


def copy_language_assets(patch: Path, language: str, game: Path) -> None:
    # This directory is owned by the generated language package, not saves.
    target = game / "tl" / language
    if target.is_dir():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    (target / "rscript_strings.rpy").write_text(
        "translate %s python:\n    pass\n" % language, encoding="utf-8")
    for folder in IMAGE_FOLDERS:
        copy_assets(patch / folder, "*.png", target / "images" / folder)
        copy_assets(patch / folder, ".meta.xml", target / "images" / folder)
    convert_masks(patch / "grps", target / "images" / "grps")
    for source, destination in (("wav", "wav"), ("wav", "audio"),
                                ("bgm", "bgm"), ("voice", "voice")):
        copy_assets(patch / source, "*.ogg", target / destination)
    copy_movies(patch / "mov", target / "mov")
    if (patch / "keywords.json").is_file():
        read_keywords(patch / "keywords.json")
        shutil.copyfile(patch / "keywords.json", target / "keywords.json")

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
        patch = Path(folder).resolve()
        if not patch.is_dir():
            raise FileNotFoundError("language patch directory not found: %s" % patch)
        names.add(language)
        patches.append((language, patch))
    return marker, patches


def copy_assets(source: Path, pattern: str, target: Path) -> None:
    if source.is_dir():
        for asset in source.rglob(pattern):
            output = target / asset.relative_to(source)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(asset, output)


def convert_masks(source: Path, target: Path) -> None:
    for asset in source.rglob("*.msk"):
        output = (target / asset.relative_to(source)).with_suffix(".png")
        output.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(asset) as image:
            image.save(output, "PNG")


def copy_movies(source: Path, target: Path, clear: bool = False) -> None:
    if not source.is_dir():
        return
    target.mkdir(parents=True, exist_ok=True)
    if clear:
        for obsolete in target.iterdir():
            if (obsolete.is_file() and
                    obsolete.suffix.lower() in {".mpg", ".webm"}):
                obsolete.unlink()
    for asset in sorted(source.iterdir()):
        if asset.is_file() and asset.suffix.lower() == ".mpg":
            shutil.copyfile(asset, target / (asset.stem + ".mpg"))
