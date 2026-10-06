#!/usr/bin/env python3
"""Independent static tool: mixed encoding, CFG priority, no generator changes."""

from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from inspect_rscript_init import inspect_initialization, parse_tcf, KNOWN_KEYS


def main():
    with TemporaryDirectory(prefix="rscript-init-") as directory:
        root = Path(directory)
        empty = inspect_initialization(root)
        assert empty["tcf"] is None and empty["hints"]["screen_size"]["width"] is None
        assert not empty["effective_configuration_confirmed"]
        source = root / "rsinit.TCF"
        contents = "# 日本語注釈\r\n".encode("cp932") + (
            "title 腐姬 ~jamais vu~\r\nwidth 640\r\nheight 480\r\nexec 1\r\nscript 0\r\n"
            "scrdir scenario\\tsc\r\nsavepfx rssave\r\nscrmod RsComp.dll\r\n"
            "extmod extension.dll\r\nfuture_field preserve me\r\n").encode("gbk")
        source.write_bytes(contents)
        (root / "scenario/tsc").mkdir(parents=True)
        report = inspect_initialization(root, "gbk")
        assert len(KNOWN_KEYS) == 20
        assert report["hints"]["title"] == "腐姬 ~jamais vu~"
        assert report["hints"]["screen_size"] == dict(width=640, height=480)
        assert report["hints"]["startup"] == dict(exec=1, script=0)
        assert report["hints"]["directories"]["scrdir"]["exists"]
        assert report["hints"]["save_prefix"] == "rssave"
        assert report["hints"]["modules"]["extmod"] == "extension.dll"
        assert report["tcf"]["unknown_keys"][0]["value"] == "preserve me"
        assert not report["tcf"]["issues"]
        cfg = root / "RSINIT.CFG"
        cfg.write_bytes(bytes(324))
        report = inspect_initialization(source, "gbk")
        assert report["cfg"]["size_bytes"] == 324 and not report["cfg"]["decoded"]
        assert any("takes priority" in note for note in report["notes"])
        assert not report["effective_configuration_confirmed"]
        result = subprocess.run([sys.executable, "-B", str(ROOT / "tools/inspect_rscript_init.py"),
                                 str(root), "--encoding", "gbk"], capture_output=True, text=True, check=True)
        assert json.loads(result.stdout) == report
        assert source.read_bytes() == contents and cfg.read_bytes() == bytes(324)
        # Unknown/malformed fields remain diagnostic data, never evaluated code.
        source.write_bytes(b"\xef\xbb\xbfwidth 640\nwidth 800\nexec 0\nscript 1x\n"
                           b"bad\nheight \xff\ntitle A\0B\nscrdir ../outside\n"
                           b"bgimgdir C:\\original\nfaceimgdir \\\\server\\share\n")
        parsed = parse_tcf(source, "utf-8")
        assert "width" not in parsed["values"] and parsed["values"]["exec"] == 0
        assert len(parsed["issues"]) == 5
        for key in ("scrdir", "bgimgdir", "faceimgdir"):
            assert inspect_initialization(root)["hints"]["directories"][key]["status"] == "external path not checked"
        try:
            inspect_initialization(cfg)
        except ValueError:
            pass
        else:
            raise AssertionError("must not pretend to decode CFG/EXE/DLL")
    if len(sys.argv) > 1:
        root = Path(sys.argv[1])
        source = root / "RsInit.tcf"
        before = hashlib.sha256(source.read_bytes()).digest()
        report = inspect_initialization(root, "gbk")
        assert report["tcf"]["values"] == dict(title="腐姬 ~jamais vu~", height=480, width=640, exec=1, script=0)
        assert hashlib.sha256(source.read_bytes()).digest() == before
        print("OK: real mixed-encoding Khime Zero TCF, read-only, DLL not used")
    print("OK: static report, 20 known keys, unknown fields, CFG warning and untouched inputs")


if __name__ == "__main__":
    main()
