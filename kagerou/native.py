"""Read-only evidence and EXCMD call model for the two audited Kagerou EXEs.

This is not a renderer or a GSC decoder. Addresses are native virtual addresses;
calls describe the audited program, and never invoke it.
"""

import hashlib
from pathlib import Path
import struct


AUDITED_EXES = {
    "f02998fae350945f4de4dc7eab47997e1e2d9b8aa43d49740a80aad893dcde9b": "original",
    "0d024e5cfe6c70f5a9a9149df5fbf040dfb7d97cdeefba03a13625d121dea8de": "Chinese patch",
}


class NativeImage:
    def __init__(self, path):
        self.data = Path(path).read_bytes()
        self.sha256 = hashlib.sha256(self.data).hexdigest()
        if self.sha256 not in AUDITED_EXES:
            raise ValueError("EXE is not one of the audited Kagerou builds")
        pe = struct.unpack_from("<I", self.data, 0x3c)[0]
        if self.data[:2] != b"MZ" or self.data[pe:pe + 4] != b"PE\0\0":
            raise ValueError("expected PE executable")
        machine, count = struct.unpack_from("<HH", self.data, pe + 4)
        optional_size = struct.unpack_from("<H", self.data, pe + 20)[0]
        optional = pe + 24
        if machine != 0x14c or struct.unpack_from("<H", self.data, optional)[0] != 0x10b:
            raise ValueError("expected i386 PE32 executable")
        self.base = struct.unpack_from("<I", self.data, optional + 28)[0]
        self.sections = []
        for index in range(count):
            offset = optional + optional_size + index * 40
            name = self.data[offset:offset + 8].rstrip(b"\0").decode("ascii")
            virtual_size, rva, size, raw = struct.unpack_from("<IIII", self.data, offset + 8)
            self.sections.append((name, rva, virtual_size, size, raw))

    def read(self, address, size):
        rva = address - self.base
        if size < 0:
            raise ValueError("negative read size")
        for _, start, _, raw_size, raw in self.sections:
            relative = rva - start
            if 0 <= relative < raw_size and relative + size <= raw_size:
                offset = raw + relative
                if offset + size <= len(self.data):
                    return self.data[offset:offset + size]
        # The EXE's .data has a large BSS tail: VA - image base is not a file offset.
        raise ValueError("address 0x%x is not backed by file data" % address)

    def handler(self, opcode):
        if not 3 <= opcode <= 255:
            raise ValueError("opcode is outside the audited non-VM dispatch table")
        index = self.read(0x41d4f8 + opcode - 3, 1)[0]
        return struct.unpack("<I", self.read(0x41d2e8 + index * 4, 4))[0]

    def character_x(self, slot, *, layout, alternate):
        if not 1 <= slot <= 7 or not 0 <= layout <= 65535:
            raise ValueError("invalid native slot or layout word")
        address = (0x47eede + slot * 2 if alternate else
                   0x47eeba + (6 * (layout // 3) + slot) * 2)
        return struct.unpack("<h", self.read(address, 2))[0]

    def draw_handler(self, mode):
        mode &= 65535
        if not 1 <= mode <= 99:
            return 0x408ed0
        index = self.read(0x408f40 + mode - 1, 1)[0]
        return struct.unpack("<I", self.read(0x408f24 + index * 4, 4))[0]


def excmd_calls(operands, *, x, inactive_style, queued):
    """Expand five resolved WORD operands into native calls and register writes.

    x is explicitly supplied from NativeImage.character_x and native configuration.
    No layout/style defaults or pixel effects are inferred here.
    """
    if len(operands) != 5 or any(type(n) is not int or not 0 <= n <= 65535 for n in operands):
        raise ValueError("EXCMD requires five resolved unsigned WORD operands")
    mode, slot, cg, keep_focus, _ = operands
    calls = []

    def refresh():
        if not queued:
            calls.append((0x41dd30,))

    def focus():
        calls.append(("register", 20, slot))
        for layer in range(1, 7):
            calls.append((0x41f940, layer, 8 if layer == slot else layer))
            draw, strength = (0, 0) if layer == slot or inactive_style else (4, 50)
            calls.append((0x41f7f0, layer, draw, strength))
        refresh()

    if mode == 0 and 1 <= slot <= 7:
        if x is None or type(x) is not int or not -32768 <= x <= 32767:
            raise ValueError("load requires a verified signed WORD x coordinate")
        calls.append((0x41dda0, slot, cg, 0, x, 0, 0))
        if keep_focus == 0:
            focus()
        refresh()
    elif mode == 1:
        # 431410's guard accepts every WORD; 41e020 validates the layer downstream.
        calls.append((0x41e020, slot, 0))
        refresh()
    elif mode == 2:
        focus()
    return calls
