#!/usr/bin/env python3
"""Audit prepared Kagerou resources without modifying or executing them."""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from native import AUDITED_EXES, NativeImage


def inspect_scripts(directory):
    sources = sorted(directory.glob("*.tsc"))
    if not sources:
        raise ValueError("no current TSC scripts in %s" % directory)
    commands = Counter()
    schemas = Counter()
    excmd_modes = Counter()
    movies = Counter()
    for source in sources:
        contents = source.read_text(encoding="utf-8-sig")
        if contents.count(";@gsc-byte-format modern-36") != 1:
            raise ValueError("%s: expected current modern-36 TSC" % source)
        schema = re.findall(r"^;@gsc-schema (\S+)$", contents, re.M)
        if len(schema) != 1 or schema[0] not in ("modern", "rscript19"):
            raise ValueError("%s: unverified schema" % source)
        schemas[schema[0]] += 1
        for number, line in enumerate(contents.splitlines(), 1):
            match = re.match(r"^\*(\w+)\b", line)
            if not match:
                continue
            command = match[1]
            commands[command] += 1
            if command == "excmd":
                try:
                    operands = [int(value, 0) for value in line.split()[1:]]
                except ValueError as error:
                    raise ValueError("%s:%s: unresolved EXCMD operands" % (source, number)) from error
                if len(operands) != 5 or any(not 0 <= n <= 65535 for n in operands):
                    raise ValueError("%s:%s: invalid EXCMD operands" % (source, number))
                excmd_modes[str(operands[0])] += 1
            elif command == "movie":
                movies[line.split()[1]] += 1
    return dict(scenes=len(sources), schemas=dict(schemas), commands=dict(sorted(commands.items())),
                excmd_modes=dict(excmd_modes), movie_operands=dict(movies))


def inspect(root, patch=None):
    image = NativeImage(root / "kagerou.exe")
    startup = ("0002.mpg", "0001.mpg")
    # Read both native string operands, not the other games' movie configuration.
    for address, name in zip((0x47ecf8, 0x47ece8), startup):
        expected = (".\\mov\\" + name + "\0").encode("ascii")
        if image.read(address, len(expected)) != expected:
            raise ValueError("native startup movie string changed")
    report = dict(
        executable=dict(sha256=image.sha256, build=AUDITED_EXES[image.sha256]),
        scripts=inspect_scripts(root / "scr"),
        startup_movies=[dict(path="mov/" + name, exists=(root / "mov" / name).is_file())
                        for name in startup],
        handlers={"0x%02x" % opcode: "0x%x" % image.handler(opcode)
                  for opcode in (0x14, 0x1a, 0x1c, 0x51, 0x52, 0x5c, 0x66, 0xff)},
        configuration_defaults_confirmed=False,
        renderer_implemented=False,
    )
    if patch is not None:
        patched = NativeImage(patch / "kagerou_gbk.exe")
        original_text = next(section for section in image.sections if section[0] == ".text")
        rva, size = original_text[1], original_text[3]
        before = image.read(image.base + rva, size)
        after = patched.read(patched.base + rva, size)
        report["patch"] = dict(
            executable=dict(sha256=patched.sha256, build=AUDITED_EXES[patched.sha256]),
            text_byte_changes=[dict(address="0x%x" % (image.base + rva + i), before=a, after=b)
                               for i, (a, b) in enumerate(zip(before, after)) if a != b],
            scripts=inspect_scripts(patch / "scr"),
            fallback_scenes=sorted({p.name for p in (root / "scr").glob("*.tsc")} -
                                   {p.name for p in (patch / "scr").glob("*.tsc")}),
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resources", type=Path)
    parser.add_argument("--patch", type=Path)
    args = parser.parse_args()
    try:
        report = inspect(args.resources, args.patch)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
