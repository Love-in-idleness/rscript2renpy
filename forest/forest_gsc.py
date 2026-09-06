"""Decoder for Forest's 2004 CodeX GSC dialect.

The operand layouts are transcribed from Forest.exe's dispatch routine at
0x41a210.  Ordinary operands use the engine's packed 32-bit expression form.
"""

from dataclasses import dataclass
from pathlib import Path
import struct


E, U16, U32 = "E", "U16", "U32"

# opcode: operand kinds, in the exact order consumed by Forest.exe.
_COUNTS = {
    8: 0, 9: 0, 10: 0, 11: 0, 12: 1, 13: 1, 15: 1, 16: 1, 17: 0,
    18: 1, 19: 1, 20: 2, 21: 0, 22: 4, 23: 2, 24: 2, 25: 0,
    26: 0, 27: 0, 28: 3, 29: 2, 30: 6, 32: 5, 33: 5, 34: 5,
    35: 2, 36: 2, 37: 2, 38: 3, 39: 3, 40: 2, 41: 2, 42: 2,
    43: 2, 44: 1, 45: 2, 46: 1, 47: 2, 48: 2, 49: 2, 50: 0,
    51: 0, 52: 0, 53: 1, 55: 0, 56: 5, 57: 0, 58: 0, 59: 4,
    60: 2, 61: 1, 62: 1, 63: 3, 64: 1, 65: 1, 66: 4, 67: 1,
    68: 0, 69: 0, 70: 4, 71: 4, 72: 1, 73: 2, 74: 1, 75: 4,
    77: 4, 80: 1, 83: 1, 90: 3, 91: 5, 92: 2, 93: 2, 94: 1,
    95: 2, 96: 2, 97: 2, 98: 2, 99: 3, 100: 3, 101: 2, 102: 1,
    103: 2, 104: 4, 110: 3, 111: 3, 112: 1, 113: 2, 120: 2,
    130: 4, 131: 5, 132: 2, 134: 3, 135: 5, 136: 3, 152: 2,
    153: 2, 154: 2, 155: 2,
}

SCHEMAS = {opcode: (E,) * count for opcode, count in _COUNTS.items()}
SCHEMAS.update({
    3: (U32,), 4: (U32,), 5: (U32,), 9: (U16,), 18: (E, U32),
    # Forest.exe 0x41a709: count, prompt/layout/choice strings, then VM refs.
    14: (U16,) + (U32,) * 11 + (E, E, E),
    25: (U32,), 32: (E,) * 5 + (U32,),
    81: (E, E, E, E, U32, U32, E),
    82: (E, E, E, E, U32, E),
    121: (E, U32), 150: (E, U32), 151: (E, U32),
})


@dataclass(frozen=True)
class Instruction:
    offset: int
    opcode: int
    kinds: tuple[str, ...]
    operands: tuple[int, ...]
    size: int


@dataclass(frozen=True)
class ForestGsc:
    path: Path
    code: bytes
    strings: tuple[bytes, ...]
    data_blocks: tuple[tuple[int, ...], ...]

    def string(self, index: int, encoding: str = "cp932") -> str:
        return self.strings[index].decode(encoding)

    def data(self, index: int) -> tuple[int, ...]:
        return self.data_blocks[index]

    def instructions(self) -> list[Instruction]:
        result = []
        pos = 0
        while pos < len(self.code):
            opcode = struct.unpack_from("<H", self.code, pos)[0]
            high = opcode & 0xF000
            if high:
                kinds = (U16, U16, U16) if high != 0xF000 else (U16, U16)
            else:
                try:
                    kinds = SCHEMAS[opcode]
                except KeyError as error:
                    raise ValueError(f"{self.path}: unknown opcode 0x{opcode:04x} at 0x{pos:x}") from error
            cursor = pos + 2
            values = []
            for kind in kinds:
                size = 2 if kind == U16 else 4
                if cursor + size > len(self.code):
                    raise ValueError(f"{self.path}: truncated opcode 0x{opcode:04x} at 0x{pos:x}")
                values.append(struct.unpack_from("<H" if kind == U16 else "<I", self.code, cursor)[0])
                cursor += size
            result.append(Instruction(pos, opcode, kinds, tuple(values), cursor - pos))
            pos = cursor
        return result


def read_gsc(path: str | Path) -> ForestGsc:
    path = Path(path)
    data = path.read_bytes()
    if len(data) < 28:
        raise ValueError(f"{path}: shorter than legacy GSC header")
    (_, header_size, code_size, declaration_size, string_size,
     data_index_size, data_word_count) = struct.unpack_from("<7I", data)
    if header_size != 28 or declaration_size % 4:
        raise ValueError(f"{path}: not a Forest legacy GSC")
    code_start = header_size
    declaration_start = code_start + code_size
    strings_start = declaration_start + declaration_size
    if strings_start + string_size > len(data):
        raise ValueError(f"{path}: truncated legacy GSC")
    offsets = struct.unpack_from(f"<{declaration_size // 4}I", data, declaration_start)
    raw = data[strings_start:strings_start + string_size]
    strings = []
    for offset in offsets:
        end = raw.find(b"\0", offset)
        if end < 0:
            raise ValueError(f"{path}: unterminated string")
        strings.append(raw[offset:end])
    data_index_start = strings_start + string_size
    data_words_start = data_index_start + data_index_size
    data_end = data_words_start + data_word_count * 2
    if data_index_size % 4 or data_end > len(data):
        raise ValueError(f"{path}: malformed legacy data blocks")
    data_offsets = struct.unpack_from(f"<{data_index_size // 4}I", data, data_index_start)
    data_words = struct.unpack_from(f"<{data_word_count}H", data, data_words_start)
    blocks = []
    for offset in data_offsets:
        if offset >= len(data_words):
            raise ValueError(f"{path}: data block starts outside its table")
        count = data_words[offset]
        if offset + 1 + count > len(data_words):
            raise ValueError(f"{path}: truncated data block")
        blocks.append(tuple(value - 0x10000 if value & 0x8000 else value
                            for value in data_words[offset + 1:offset + 1 + count]))
    return ForestGsc(path, data[code_start:declaration_start], tuple(strings), tuple(blocks))
