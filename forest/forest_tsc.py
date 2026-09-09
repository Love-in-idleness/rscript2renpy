"""Reader for structured Forest TSC files produced by LiarsoftTool 2.0."""

from dataclasses import dataclass
from pathlib import Path
import re
import struct


E = "E"


@dataclass(frozen=True)
class Instruction:
    offset: int
    opcode: int
    kinds: tuple[str, ...]
    operands: tuple[int, ...]
    size: int


@dataclass(frozen=True)
class ForestTsc:
    path: Path
    code_size: int
    strings: tuple[bytes, ...]
    data_blocks: tuple[tuple[int, ...], ...]
    decoded_instructions: tuple[Instruction, ...]
    text_edits: dict[int, str]
    encoding: str

    def string(self, index: int) -> str:
        return self.strings[index].decode(self.encoding)

    def data(self, index: int) -> tuple[int, ...]:
        return self.data_blocks[index]

    def instructions(self) -> list[Instruction]:
        return list(self.decoded_instructions)


def read_tsc(path: str | Path) -> ForestTsc:
    path = Path(path)
    sections: dict[str, bytearray] = {}
    instructions = []
    text_edits = {}
    byte_format = None
    encoding = None
    in_structure = False
    complete = False
    pending_text = None

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(";@gsc-structure-v1 "):
            if in_structure or complete:
                raise ValueError(f"{path}: duplicate structured TSC metadata")
            in_structure = True
            continue
        if in_structure and line == ";@gsc-structure-end":
            in_structure = False
            complete = True
            continue
        if in_structure and line.startswith(";@gsc-section "):
            fields = line.split()
            if len(fields) != 3:
                raise ValueError(f"{path}: malformed TSC section")
            name, value = fields[1], fields[2]
            section = sections.setdefault(name, bytearray())
            if value != "-":
                try:
                    section.extend(bytes.fromhex(value))
                except ValueError as error:
                    raise ValueError(f"{path}: malformed TSC section bytes") from error
            continue
        if in_structure and line.startswith(";@gsc-instruction "):
            fields = line.split()
            if len(fields) < 4:
                raise ValueError(f"{path}: malformed TSC instruction")
            kinds = () if fields[3] == "-" else tuple(fields[3])
            try:
                offset = int(fields[1], 16)
                opcode = int(fields[2], 16)
                operands = tuple(int(value) for value in fields[4:])
            except ValueError as error:
                raise ValueError(f"{path}: malformed TSC instruction value") from error
            if len(kinds) != len(operands) or any(
                    kind not in "HSDE" for kind in kinds):
                raise ValueError(f"{path}: invalid TSC instruction operands")
            size = 2 + sum(2 if kind in "HS" else 4 for kind in kinds)
            instructions.append(Instruction(offset, opcode, kinds, operands, size))
            continue
        if line.startswith(";@gsc-byte-format "):
            if byte_format is not None:
                raise ValueError(f"{path}: duplicate TSC byte format")
            byte_format = line.removeprefix(";@gsc-byte-format ")
            continue
        if line.startswith(";@gsc-text-encoding "):
            if encoding is not None:
                raise ValueError(f"{path}: duplicate TSC text encoding")
            encoding = line.removeprefix(";@gsc-text-encoding ")
            continue
        if not complete:
            continue
        marker = re.fullmatch(r"; @([0-9a-fA-F]{6})", line)
        if marker:
            pending_text = int(marker.group(1), 16)
            continue
        if pending_text is not None and line.startswith("\\"):
            text_edits[pending_text] = line
        pending_text = None

    if in_structure or not complete:
        raise ValueError(
            f"{path}: not a structured TSC; regenerate it with LiarsoftTool 2.0")
    if byte_format != "legacy-28":
        raise ValueError(f"{path}: Forest requires ;@gsc-byte-format legacy-28")
    if not encoding:
        raise ValueError(f"{path}: missing TSC text encoding")
    try:
        header = bytes(sections["header"])
        declaration = bytes(sections["declaration"])
        string_data = bytes(sections["strings"])
        data_index = bytes(sections["data-index"])
        data = bytes(sections["data"])
    except KeyError as error:
        raise ValueError(f"{path}: missing structured TSC section {error.args[0]}") from error
    if len(header) != 28:
        raise ValueError(f"{path}: malformed Forest TSC header")
    _, header_size, code_size, declaration_size, string_size, index_size, words = \
        struct.unpack("<7I", header)
    if (header_size != 28 or len(declaration) != declaration_size or
            len(string_data) != string_size or len(data_index) != index_size or
            len(data) != words * 2 or declaration_size % 4 or index_size % 4):
        raise ValueError(f"{path}: structured TSC section sizes do not match")

    cursor = 0
    for instruction in instructions:
        if instruction.offset != cursor:
            raise ValueError(f"{path}: non-contiguous TSC instructions")
        cursor += instruction.size
    if cursor != code_size:
        raise ValueError(f"{path}: TSC instructions do not fill the code section")

    strings = []
    for (offset,) in struct.iter_unpack("<I", declaration):
        end = string_data.find(b"\0", offset)
        if offset >= len(string_data) or end < 0:
            raise ValueError(f"{path}: malformed TSC string table")
        strings.append(string_data[offset:end])

    data_words = struct.unpack(f"<{words}H", data) if words else ()
    blocks = []
    for (offset,) in struct.iter_unpack("<I", data_index):
        if offset >= len(data_words):
            raise ValueError(f"{path}: data block starts outside its table")
        count = data_words[offset]
        if offset + 1 + count > len(data_words):
            raise ValueError(f"{path}: truncated TSC data block")
        blocks.append(tuple(value - 0x10000 if value & 0x8000 else value
                            for value in data_words[offset + 1:offset + 1 + count]))

    return ForestTsc(path, code_size, tuple(strings), tuple(blocks),
                     tuple(instructions), text_edits, encoding)
