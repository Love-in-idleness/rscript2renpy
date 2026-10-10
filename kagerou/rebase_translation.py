#!/usr/bin/env python3
"""Rebase translated dialogue through LiarsoftTool TXT, retaining updated GSC code."""
import argparse
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
from tempfile import TemporaryDirectory, mkdtemp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "port_template"))
from rscript_tsc import STRING_OPERANDS, read_tsc


def run(tool, *args):
    result = subprocess.run([str(tool), *map(str, args)], capture_output=True, text=True)
    if result.returncode:
        raise ValueError("LiarsoftTool exit %d (%s): %s" %
                         (result.returncode, args[-1], (result.stderr or result.stdout).strip()))


def exported_strings(path):
    sections = []
    current = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith(("#", ">")):
            if current is not None:
                sections.append(current)
            current = [line[0], line[1:]]
        elif current is not None:
            current[1] += "\n" + line
        else:
            raise ValueError("invalid TXT section: " + str(path))
    if current is not None:
        sections.append(current)
    if len(sections) % 2 or any(sections[i][0] != "#" or sections[i + 1] != [">", ""]
                               for i in range(0, len(sections), 2)):
        raise ValueError("expected unedited LiarsoftTool TXT export: " + str(path))
    return [text.replace("\\", "^").replace("^t", "\u3000").replace("\n", "^n")
            for marker, text in sections[::2]]


def translation_txt(strings):
    lines = []
    for text in strings:
        text.encode("gbk", errors="strict")
        external = text.replace("\u3000", "^t").replace("^", "\\").replace("\\n", "\n")
        if any(line.startswith(("#", ">", " ")) for line in external.split("\n")) or "\r" in external:
            raise ValueError("text cannot round-trip through the TXT section syntax")
        lines.append("#\n>" + external + "\n")
    return "".join(lines)


def gsc_parts(path):
    data = path.read_bytes()
    if len(data) < 36:
        raise ValueError("truncated GSC: " + str(path))
    length, header, commands, declarations, definitions = struct.unpack_from("<5I", data)
    end = header + commands + declarations + definitions
    if header != 36 or length != len(data) or end > len(data):
        raise ValueError("expected complete modern-36 GSC: " + str(path))
    return data[20:header], data[header:header + commands], data[end:]


def dialogue_strings(base, donor, code, original, translated):
    # GSC index 0 is the empty sentinel, omitted from LiarsoftTool's TXT export.
    original = ["", *original]
    donor_text = ["", *translated[0]]
    before = [i for i in base.instructions() if i.opcode in (81, 82)]
    after = [i for i in donor.instructions() if i.opcode in (81, 82)]
    if len(before) != len(after):
        raise ValueError("%s: dialogue count changed; manual alignment required" % base.path.name)
    replacements = {}
    for left, right in zip(before, after):
        if int.from_bytes(code[left.offset:left.offset + 2], 'little') != left.opcode:
            raise ValueError("TSC/GSC dialogue opcode disagrees")
        slots = STRING_OPERANDS[left.opcode]
        if left.opcode != right.opcode or left.kinds != right.kinds or any(
                a != b for n, (a, b) in enumerate(zip(left.operands, right.operands)) if n not in slots):
            raise ValueError("%s: dialogue metadata changed; manual alignment required" % base.path.name)
        for n in sorted(slots):
            offset = 2 + sum(2 if k in "HS" else 4 for k in left.kinds[:n])
            index = struct.unpack_from("<I", code, left.offset + offset)[0]
            donor_index = struct.unpack_from("<I", translated[1], right.offset + offset)[0]
            if index >= len(original) or donor_index >= len(donor_text):
                raise ValueError("GSC dialogue string index outside TXT export")
            if left.opcode == 81 and n == 4 and index == 0:
                if donor.string(right.operands[n]):
                    raise ValueError("speaker sentinel changed")
                continue
            if original[index] != base.string(left.operands[n]):
                raise ValueError("%s: TSC is stale relative to GSC" % base.path.name)
            text = donor_text[donor_index]
            if text != donor.string(right.operands[n]):
                raise ValueError("donor TXT and TSC disagree")
            if index in replacements and replacements[index] != text:
                raise ValueError("shared GSC string has conflicting translations")
            replacements[index] = text
    result = list(original)
    for index, text in replacements.items():
        result[index] = text
    return result[1:], sum(original[n] != text for n, text in replacements.items())


def rebase(base, patch, tool, apply=False):
    base, patch, tool = (Path(p).resolve() for p in (base, patch, tool))
    if base == patch or base.is_relative_to(patch) or patch.is_relative_to(base):
        raise ValueError("original and patch must be separate directories")
    sources = sorted((base / "scr").glob("[0-9][0-9][0-9][0-9].tsc"))
    if not sources or not (patch / "scr").is_dir():
        raise ValueError("original and patch scr directories are required")
    report = {"edition": "ハチポチ特典", "scenes": [], "untranslated_scenes": []}
    with TemporaryDirectory(prefix=".kagerou-rebase-", dir=patch) as directory:
        work = Path(directory)
        staged = work / "scr"
        staged.mkdir()
        for source in sources:
            name = source.stem
            reference = source.with_suffix(".gsc")
            native = read_tsc(source, "kagerou")
            parts = gsc_parts(reference)
            if len(parts[1]) != native.code_size:
                raise ValueError("TSC/GSC command sizes disagree: " + str(source))
            original_txt = work / "original.txt"
            run(tool, "-e", "cp932", "-o", original_txt, reference)
            original = exported_strings(original_txt)
            if not original:
                shutil.copy2(reference, staged / reference.name)
                shutil.copy2(source, staged / source.name)
                report["scenes"].append({"scene": name, "translated_strings": 0})
                continue
            # Explicit edited translations take precedence; they remain in the backup.
            donor_path = patch / "scr" / (name + "_zh.tsc")
            if not donor_path.exists():
                donor_path = patch / "scr" / source.name
            changed = 0
            text = original
            dialogue = [i for i in native.instructions() if i.opcode in (81, 82)]
            if dialogue and not donor_path.exists():
                report["untranslated_scenes"].append(name)
                continue
            if donor_path.exists():
                donor = read_tsc(donor_path, "kagerou")
                donor_dialogue = [i for i in donor.instructions() if i.opcode in (81, 82)]
                if len(dialogue) == len(donor_dialogue) and all(
                        left.opcode == right.opcode and all(
                            native.string(left.operands[n]) == donor.string(right.operands[n])
                            for n in STRING_OPERANDS[left.opcode])
                        for left, right in zip(dialogue, donor_dialogue)) and dialogue:
                    report["untranslated_scenes"].append(name)
                    continue
                donor_gsc, donor_txt = work / "donor.gsc", work / "donor.txt"
                run(tool, "-e", "gbk", "-o", donor_gsc, donor_path)
                run(tool, "-e", "gbk", "-o", donor_txt, donor_gsc)
                text, changed = dialogue_strings(native, donor, parts[1], original,
                    (exported_strings(donor_txt), gsc_parts(donor_gsc)[1]))
            if not changed and dialogue:
                report["untranslated_scenes"].append(name)
            injection = work / "injection.txt"
            injection.write_text(translation_txt(text), encoding="utf-8")
            output = staged / (name + ".gsc")
            run(tool, "-e", "gbk", "-r", reference, "-o", output, injection)
            if gsc_parts(output) != parts:
                raise ValueError("non-text GSC bytes changed: " + name)
            check = work / "check.txt"
            run(tool, "-e", "gbk", "-o", check, output)
            if exported_strings(check) != text:
                raise ValueError("TXT import changed text: " + name)
            run(tool, "--gsc-to-tsc", "-e", "gbk", "-o", staged / source.name, output)
            rebuilt = read_tsc(staged / source.name, "kagerou")
            if rebuilt.data_blocks != native.data_blocks or rebuilt.named_entries != native.named_entries:
                raise ValueError("data blocks or named entries changed: " + name)
            report["scenes"].append({"scene": name, "translated_strings": changed})
        if apply:
            backup = Path(mkdtemp(prefix="kagerou-rebase-backup-", dir=patch))
            os.replace(patch / "scr", backup / "scr")
            try:
                os.replace(staged, patch / "scr")
            except OSError:
                os.replace(backup / "scr", patch / "scr")
                raise
            report["backup"] = str(backup)
            (backup / "rebase-report.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("patch", type=Path)
    parser.add_argument("--liarsofttool", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="install only after all checks; back up old scr")
    args = parser.parse_args()
    try:
        print(json.dumps(rebase(args.original, args.patch, args.liarsofttool, args.apply),
                         ensure_ascii=False, indent=2))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
