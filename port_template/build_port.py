#!/usr/bin/env python3
"""Assemble a Ren'Py project from prepared RScript-port resources."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from install_runtime import install  # noqa: E402
from effect_compat import flatten_unsupported_effects  # noqa: E402


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
    "bgm": {".ogg"},
    "voice": {".ogg"},
    "wav": {".ogg"},
    "mov": {".mpg"},
}


def copy_file(source: Path, target: Path, force: bool) -> None:
    if target.exists() and target.read_bytes() != source.read_bytes() and not force:
        raise FileExistsError("refusing to overwrite different file: %s" % target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_tree(source: Path, target: Path, suffixes: set[str], force: bool) -> int:
    if not source.is_dir():
        return 0
    copied = 0
    for path in sorted(item for item in source.rglob("*") if item.is_file()):
        if path.suffix.lower() not in suffixes:
            continue
        copy_file(path, target / path.relative_to(source), force)
        copied += 1
    return copied


def copy_scenarios(source: Path, target: Path, resources: Path,
                   force: bool) -> int:
    copied = 0
    for path in sorted(source.rglob("*.rpy")):
        destination = target / path.relative_to(source)
        result = flatten_unsupported_effects(path.read_text(encoding="utf-8"),
                                             resources)
        if destination.exists() and destination.read_text(encoding="utf-8") != result and not force:
            raise FileExistsError("refusing to overwrite different file: %s" % destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(result, encoding="utf-8")
        copied += 1
    return copied


def build(resources: Path, project: Path, force: bool = False,
          scenarios: Path | None = None) -> tuple[int, int]:
    resources = resources.resolve()
    project = project.resolve()
    game = project / "game"
    scenarios = scenarios or resources / "scenario"
    if not any(scenarios.glob("*.rpy")):
        raise FileNotFoundError(
            "game-specific TSC lowerer produced no scenario/*.rpy files: %s" %
            scenarios)

    game.mkdir(parents=True, exist_ok=True)
    installed = install(project, force=force)
    copied = 0
    for name, destination in RESOURCE_TARGETS.items():
        copied += copy_tree(resources / name, game / destination,
                            ALLOWED_SUFFIXES[name], force)
    copied += copy_scenarios(scenarios, game / "scenario", resources, force)
    for source in sorted((Path(__file__).parent / "game").glob("*.rpy")):
        copy_file(source, game / source.name, force)
        copied += 1
    return len(installed), copied


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
