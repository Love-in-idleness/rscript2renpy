#!/usr/bin/env python3
"""Read-only RScript initialization report; independent of builders, EXE and DLL."""

import argparse
import codecs
import json
from pathlib import Path, PureWindowsPath
import re


# Confirmed in Khime Zero's RsInit.dll, not assumed to be a universal schema.
DIRECTORY_KEYS = ("scrdir", "sysimgdir", "layerimgdir", "faceimgdir", "bgimgdir",
                  "moviedir", "wavedir", "bgmdir", "voicedir")
INTEGER_KEYS = {"width", "height", "exec", "script", "bgm", "bgmsource", "layermod"}
KNOWN_KEYS = set(DIRECTORY_KEYS) | INTEGER_KEYS | {"title", "savepfx", "scrmod", "extmod"}


def parse_tcf(path: Path, encoding: str = "cp932") -> dict:
    """ASCII keys first; decode only values, never comments from another codec."""
    codecs.lookup(encoding)
    values, unknown, issues = {}, [], []
    seen = set()
    for number, line in enumerate(path.read_bytes().removeprefix(b"\xef\xbb\xbf").splitlines(), 1):
        line = line.strip(b" \t")
        if not line or line.startswith(b"#"):
            continue
        match = re.fullmatch(rb"([A-Za-z][A-Za-z0-9_]*)[ \t]+(.+)", line)
        if match is None:
            issues.append({"line": number, "message": "unrecognized key/value syntax",
                           "raw_hex": line.hex()})
            continue
        key = match[1].decode("ascii").lower()
        if key in seen:
            values.pop(key, None)
            issues.append({"line": number, "key": key,
                           "message": "duplicate key; native precedence not confirmed"})
            continue
        seen.add(key)
        try:
            value = match[2].decode("ascii" if key in INTEGER_KEYS else encoding)
            if "\x00" in value:
                raise ValueError("NUL in value")
            if key in INTEGER_KEYS:
                if not re.fullmatch(r"[+-]?[0-9]+", value):
                    raise ValueError("expected decimal integer")
                value = int(value)
        except (UnicodeError, ValueError) as error:
            issues.append({"line": number, "key": key, "message": str(error),
                           "raw_hex": match[2].hex()})
            continue
        if key not in KNOWN_KEYS:
            unknown.append({"line": number, "key": key, "value": value})
        else:
            values[key] = value
    return {"encoding": encoding, "values": values, "unknown_keys": unknown, "issues": issues}


def named_file(root: Path, name: str) -> Path | None:
    matches = [p for p in root.iterdir() if p.is_file() and p.name.lower() == name.lower()]
    if len(matches) > 1:
        raise ValueError("ambiguous case-insensitive filename: %s" % matches)
    return matches[0] if matches else None


def inspect_initialization(source: Path, encoding: str = "cp932") -> dict:
    """Return observations and adaptation hints, not an effective engine config."""
    codecs.lookup(encoding)
    source = source.resolve()
    if source.is_dir():
        root, tcf = source, named_file(source, "RsInit.tcf")
    elif source.is_file() and source.suffix.lower() == ".tcf":
        root, tcf = source.parent, source
    else:
        raise ValueError("input must be a resource directory or TCF (not EXE/DLL/CFG)")
    cfg = named_file(root, "RsInit.cfg")
    parsed = parse_tcf(tcf, encoding) if tcf is not None else None
    values = parsed["values"] if parsed else {}
    notes = ["TCF keys and CFG priority are confirmed for the documented Khime Zero engine only.",
             "Missing fields remain unknown; no executable defaults are guessed."]
    if cfg is not None:
        notes.append("Native CFG takes priority in the documented engine. TCF values below are "
                     "reference only; CFG binary layout is not decoded.")
    if tcf is None:
        notes.append("No TCF found. This engine may initialize internally; no DLL/EXE is required or inspected.")
    directories = {}
    for key in DIRECTORY_KEYS:
        if key not in values:
            continue
        raw = values[key]
        windows = PureWindowsPath(raw)
        candidate = root / raw.replace("\\", "/")
        if windows.drive or windows.root or not candidate.resolve().is_relative_to(root):
            directories[key] = {"value": raw, "status": "external path not checked"}
        else:
            directories[key] = {"value": raw, "relative_path": candidate.relative_to(root).as_posix(),
                                "exists": candidate.is_dir()}
    return {
        "report_format": "rscript-init-inspection-v1",
        "tcf": {"path": str(tcf), **parsed} if parsed else None,
        "cfg": {"path": str(cfg), "size_bytes": cfg.stat().st_size,
                "decoded": False} if cfg else None,
        "effective_configuration_confirmed": False,
        "hints": {"title": values.get("title"),
                  "screen_size": {"width": values.get("width"), "height": values.get("height")},
                  "startup": {"exec": values.get("exec"), "script": values.get("script")},
                  "directories": directories,
                  "save_prefix": values.get("savepfx"),
                  "modules": {key: values[key] for key in ("scrmod", "extmod") if key in values}},
        "notes": notes,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="resource directory or RsInit.tcf")
    parser.add_argument("--encoding", default="cp932", metavar="CODEC",
                        help="codec for text values only; default CP932, Chinese Zero uses GBK")
    args = parser.parse_args(argv)
    try:
        report = inspect_initialization(args.source, args.encoding)
    except (OSError, ValueError, LookupError) as error:
        parser.error(str(error))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
