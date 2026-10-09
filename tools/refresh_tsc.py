#!/usr/bin/env python3
"""Explicit GSC preprocessing; builders remain independent of LiarsoftTool."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "port_template"))
from rscript_tsc import read_tsc


def refresh_tsc(resources, tool, encoding, dialect, force=False):
    sources = []
    for root in resources:
        scripts = Path(root).resolve() / "scr"
        files = sorted(p for p in scripts.iterdir() if p.suffix.lower() == ".gsc" and p.is_file())
        if not files:
            raise ValueError("no GSC files in " + str(scripts))
        if not force and any(p.with_suffix(".tsc").exists() for p in files):
            raise ValueError("TSC already exists; use --force to overwrite: " + str(scripts))
        sources.append(files)
    changed = 0
    with TemporaryDirectory(prefix="rscript-tsc-") as directory:
        prepared = []
        for index, files in enumerate(sources):
            output = Path(directory) / str(index)
            output.mkdir()
            target = output / files[0].with_suffix(".tsc").name if len(files) == 1 else output
            result = subprocess.run([str(tool), "--gsc-to-tsc", "-e", encoding,
                                     "-o", str(target), *map(str, files)],
                                    capture_output=True, text=True)
            if result.returncode:
                raise ValueError("GSC conversion failed: " + (result.stderr or result.stdout).strip())
            if result.stderr:
                print(result.stderr.rstrip(), file=sys.stderr)
            for source in files:
                staged = output / source.with_suffix(".tsc").name
                try:
                    read_tsc(staged, dialect)  # Reject raw fallback before any overwrite.
                except ValueError as error:
                    reason = next((line for line in staged.read_text(encoding="utf-8").splitlines()
                                   if line.startswith("; decompilation unavailable:")), str(error))
                    raise ValueError("%s: %s" % (source, reason)) from error
                prepared.append((staged, source.with_suffix(".tsc")))
        for staged, target in prepared:
            if target.exists() and target.read_bytes() == staged.read_bytes():
                os.utime(target, ns=(staged.stat().st_atime_ns, staged.stat().st_mtime_ns))
                continue
            with NamedTemporaryFile(dir=target.parent, prefix=".tsc-", delete=False) as temporary:
                temporary_path = Path(temporary.name)
            try:
                shutil.copy2(staged, temporary_path)
                os.replace(temporary_path, target)
            finally:
                temporary_path.unlink(missing_ok=True)
            changed += 1
    return sum(map(len, sources)), changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resources", type=Path, nargs="+")
    parser.add_argument("--liarsofttool", required=True, type=Path)
    parser.add_argument("--encoding", required=True, choices=("cp932", "gbk", "cp1251"))
    parser.add_argument("--dialect", required=True, choices=("forest", "khime", "modern", "legacy"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        count, changed = refresh_tsc(args.resources, args.liarsofttool, args.encoding, args.dialect, args.force)
        print("Validated %d GSC -> TSC files; replaced/created %d" % (count, changed))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
