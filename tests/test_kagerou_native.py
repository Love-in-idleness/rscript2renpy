#!/usr/bin/env python3
"""Kagerou native-call model; optional read-only tests against user-owned EXEs."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kagerou"))
from native import NativeImage, excmd_calls, text_geometry
from inspect_kagerou import inspect, inspect_scripts


def rejects(function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError("invalid input was accepted")


def snapshot(root):
    files = list((root / "scr").glob("*.tsc")) + list(root.glob("*.exe"))
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}


def main():
    vertical = text_geometry(1, 0, 0)
    assert vertical == dict(size=24, text_rect=(114, 30, 646, 480),
                            pitch=(10, 0), ruby=(0, 9, 9), vertical=True)
    assert text_geometry(0, 0, 0)["text_rect"] == (400, 20, 360, 513)
    assert text_geometry(1, 2, 8)["text_rect"] == (20, 270, 342, 240)
    for direction in range(2):
        for size in range(3):
            for snap in range(9):
                x, y, w, h = text_geometry(direction, size, snap)["text_rect"]
                assert 0 <= x <= 800 - w and 0 <= y <= 600 - h
    rejects(text_geometry, 2, 0, 0)
    rejects(text_geometry, 1, 3, 0)
    rejects(text_geometry, 1, 0, 9)
    settings = dict(x=200, inactive_style=False, queued=True)
    calls = excmd_calls((0, 1, 3011, 0, 0), **settings)
    assert calls[:2] == [(0x41dda0, 1, 3011, 0, 200, 0, 0), ("register", 20, 1)]
    assert len(calls) == 14
    for layer in range(1, 7):
        assert calls[2 * layer] == (0x41f940, layer, 8 if layer == 1 else layer)
        expected = (0, 0) if layer == 1 else (4, 50)
        assert calls[2 * layer + 1] == (0x41f7f0, layer, *expected)
    # The fifth operand is ignored; keep-focus suppresses the entire focus routine.
    assert excmd_calls((0, 6, 5011, 1, 65535), **settings) == [(0x41dda0, 6, 5011, 0, 200, 0, 0)]
    assert excmd_calls((0, 0, 3011, 0, 0), **settings) == []
    assert excmd_calls((0, 8, 3011, 0, 0), **settings) == []
    assert excmd_calls((1, 0, 0, 0, 0), **settings) == [(0x41e020, 0, 0)]
    assert excmd_calls((1, 65535, 0, 0, 0), **settings) == [(0x41e020, 65535, 0)]
    assert excmd_calls((3, 1, 3011, 0, 0), **settings) == []
    focus = excmd_calls((2, 6, 0, 0, 0), x=None, inactive_style=True, queued=False)
    assert focus[0] == ("register", 20, 6) and focus[-1] == (0x41dd30,)
    assert focus[-3:-1] == [(0x41f940, 6, 8), (0x41f7f0, 6, 0, 0)]
    assert all(call[2:] == (0, 0) for call in focus if call[0] == 0x41f7f0)
    unqueued = excmd_calls((0, 1, 3011, 0, 0), x=200, inactive_style=False, queued=False)
    assert unqueued[-2:] == [(0x41dd30,), (0x41dd30,)]
    seventh = excmd_calls((2, 7, 0, 0, 0), **settings)
    assert all(call[1] == call[2] for call in seventh if call[0] == 0x41f940)
    rejects(excmd_calls, (0, 1, 3011, 0), **settings)
    rejects(excmd_calls, (0, -1, 3011, 0, 0), **settings)
    rejects(excmd_calls, (0, 1, 3011, 0, 0), x=None, inactive_style=False, queued=True)

    with TemporaryDirectory(prefix="kagerou-native-") as directory:
        root = Path(directory)
        source = root / "0000.tsc"
        source.write_text(';@gsc-byte-format modern-36\n;@gsc-schema modern\n'
                          '*TXT 0 0 0 0 "" "Text *excmd 0 1 2 3 4" 1\n'
                          '*excmd 0 1 3011 0 0\n*movie 3\n', encoding="utf-8")
        report = inspect_scripts(root)
        assert report["excmd_modes"] == {"0": 1} and report["movie_operands"] == {"3": 1}
        source.write_text(';@gsc-byte-format legacy-28\n;@gsc-schema early\n', encoding="utf-8")
        rejects(inspect_scripts, root)
        source.write_text(';@gsc-byte-format modern-36\n;@gsc-schema modern\n*excmd $r[1] 0 0 0 0\n',
                          encoding="utf-8")
        rejects(inspect_scripts, root)
        unknown = root / "unknown.exe"
        unknown.write_bytes(b"MZ" + bytes(128))
        rejects(NativeImage, unknown)

    if len(sys.argv) > 1:
        root = Path(sys.argv[1])
        patch = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        before = snapshot(root), snapshot(patch) if patch else None
        image = NativeImage(root / "kagerou.exe")
        assert image.base == 0x400000
        assert image.handler(255) == 0x41d29d
        assert image.handler(0x51) == 0x41c9ae
        assert image.handler(0x14) == 0x41c5e9
        # The constants used by the renderer are checked against actual instructions.
        assert image.read(0x4303e2, 2) == b'\x6a\x12'  # native direction 1 (horizontal)
        assert image.read(0x430437, 3) == b'\x0f\x94\xc1'  # SETE, not SETNE
        assert image.read(0x455a1a, 12) == b'\x8b\x86\x70\x01\0\0\x2b\x86\x84\x01\0\0'  # columns right-to-left
        assert image.read(0x4303f1, 10) == b'\x68\x01\x02\0\0\x68\x68\x01\0\0'
        assert image.read(0x42bfce, 7) == b'\x68\x26\x02\0\0\x6a\0'  # (0,550)
        assert image.read(0x42c2be, 10) == b'\x68\x3c\x02\0\0\x68\x49\x02\0\0'
        assert image.draw_handler(4) == 0x408ea6  # Internal image mode 3, not mode 4.
        assert image.draw_handler(0) == 0x408ed0
        assert [image.character_x(n, layout=0, alternate=False) for n in range(1, 7)] == \
            [200, 200, 300, 400, 500, 600]
        assert [image.character_x(n, layout=6, alternate=False) for n in range(1, 7)] == \
            [600, 600, 500, 400, 300, 200]
        assert [image.character_x(n, layout=0, alternate=True) for n in range(1, 7)] == \
            [400, 200, 300, 400, 500, 600]
        rejects(image.read, 0x482a66, 2)  # Uninitialized .data/BSS, not a file offset.
        rejects(image.read, 0x400000, 4)
        rejects(image.handler, 256)
        report = inspect(root, patch)
        assert report["scripts"]["scenes"] == 162
        assert report["scripts"]["schemas"] == {"modern": 98, "rscript19": 64}
        assert report["scripts"]["excmd_modes"] == {"0": 590, "1": 263, "2": 83}
        assert report["startup_movies"] == [dict(path="mov/0002.mpg", exists=True),
                                             dict(path="mov/0001.mpg", exists=False)]
        if patch:
            assert set(report["patch"]["fallback_scenes"]) == \
                ({p.name for p in (root / "scr").glob("*.tsc")} -
                 {p.name for p in (patch / "scr").glob("*.tsc")})
            assert report["patch"]["text_byte_changes"] == \
                [dict(address="0x456d4a", before=128, after=134),
                 dict(address="0x45d0f3", before=128, after=134)]
        arguments = [sys.executable, "-B", str(ROOT / "kagerou/inspect_kagerou.py"), str(root)]
        if patch:
            arguments += ["--patch", str(patch)]
        cli = subprocess.run(arguments, capture_output=True, text=True, check=True)
        assert json.loads(cli.stdout) == report
        assert before == (snapshot(root), snapshot(patch) if patch else None)
        print("OK: native tables, 162 bonus-edition scenes, optional patch, unchanged input hashes")
    print("OK: EXCMD call model, queued refresh, focus depths, guards and TSC audit")


if __name__ == "__main__":
    main()
