"""Read-only PE32 UI evidence. Never load or execute the inspected program."""
import hashlib
from pathlib import Path
import re
import struct
import subprocess


def inspect_exe(path, resources):
    path, resources = Path(path), Path(resources)
    data = path.read_bytes()
    try:
        pe = struct.unpack_from("<I", data, 60)[0]
        if data[:2] != b"MZ" or data[pe:pe + 4] != b"PE\0\0":
            raise ValueError("not a PE executable")
        machine, count = struct.unpack_from("<HH", data, pe + 4)
        optional = pe + 24
        if machine != 0x14c or struct.unpack_from("<H", data, optional)[0] != 0x10b:
            raise ValueError("UI inspector requires PE32 x86")
        base = struct.unpack_from("<I", data, optional + 28)[0]
        optional_size = struct.unpack_from("<H", data, pe + 20)[0]
        sections = optional + optional_size
        if not 0 < count <= 96 or optional_size < 96 or sections + count * 40 > len(data):
            raise ValueError("invalid PE section table")
        strings = {}
        for index in range(count):
            section = sections + 40 * index
            va, size, offset = struct.unpack_from("<III", data, section + 12)
            if offset + size > len(data):
                raise ValueError("PE section exceeds file")
            for match in re.finditer(rb"[\x20-\x7e]{3,}\x00", data[offset:offset + size]):
                strings[base + va + match.start()] = match.group()[:-1].decode("ascii")
    except struct.error as error:
        raise ValueError("truncated PE header") from error
    try:
        disassembly = subprocess.run(["objdump", "-d", "-Mintel", str(path.resolve())],
                                     capture_output=True, text=True, check=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError) as error:
        raise ValueError("UI static inspection requires working objdump: %s" % error) from error
    instructions = []
    for line in disassembly.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*([a-z].*)", line)
        if match:
            instructions.append((int(match[1], 16), re.sub(r"\s+", " ", match[2])))
    files = {p.stem.lower() for p in (resources / "grps").rglob("*") if p.is_file()}
    references = {}
    for address, instruction in instructions:
        match = re.fullmatch(r"push 0x([0-9a-f]+)", instruction)
        name = strings.get(int(match[1], 16), "") if match else ""
        pattern = re.sub(r"%0?\d*[diu]", "[0-9]+", re.escape(name.lower()).replace(r"\%", "%"))
        if name.lower() in files or name.lower().startswith(("con_", "tbox_c")) or ("%" in name and any(re.fullmatch(pattern, file) for file in files)):
            references.setdefault(name.lower(), []).append(address)
    report = {"sha256": hashlib.sha256(data).hexdigest(), "resource_references": references,
              "unresolved": [], "layouts": {}}
    return report, strings, instructions


def constant_positions(instructions, start, end):
    """Verified x86 thiscall SetPos(x,y): object load, two pushes, vcall +78."""
    result, field, arguments, pointers = {}, None, [], {}
    for address, instruction in instructions:
        if not start <= address < end:
            continue
        match = re.fullmatch(r"lea ([a-z]+),\[esi\+0x([0-9a-f]+)\]", instruction)
        if match:
            pointers[match[1]] = int(match[2], 16)
        match = re.fullmatch(r"mov eax,DWORD PTR \[([a-z]+)\]", instruction)
        if match and match[1] in pointers:
            field, arguments = pointers[match[1]], []
        match = re.fullmatch(r"mov eax,DWORD PTR \[esi\+0x([0-9a-f]+)\]", instruction)
        if match:
            field, arguments = int(match[1], 16), []
        match = re.fullmatch(r"push 0x([0-9a-f]+)", instruction)
        if match:
            arguments.append(int(match[1], 16))
        elif instruction.startswith("push "):
            arguments.append(None)
        if instruction.startswith("call "):
            if instruction.endswith("+0x78]") and field is not None and len(arguments) == 2 and None not in arguments:
                result[field] = tuple(reversed(arguments))
            field, arguments = None, []
    return result
