#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import build  # noqa: E402


def main() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        resources = root / "resources"
        project = root / "project"
        (resources / "scenario").mkdir(parents=True)
        (resources / "scenario" / "0000.rpy").write_text(
            "label _0000:\n    return\n", encoding="utf-8")
        for folder, filename in (
                ("grps", "ui/panel.png"),
                ("bgm", "Track01.ogg"),
                ("voice", "0001.ogg"),
                ("wav", "0002.ogg"),
                ("mov", "0001.mpg")):
            path = resources / folder / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(folder.encode("ascii"))
        (resources / "grps" / "ignored.wcg").write_bytes(b"raw")
        (project / "game").mkdir(parents=True)

        runtime_count, copied = build(resources, project)
        assert runtime_count == 19
        assert copied == 7
        assert (project / "game" / "scenario" / "0000.rpy").is_file()
        assert (project / "game" / "images" / "grps" / "ui" /
                "panel.png").is_file()
        assert (project / "game" / "bgm" / "Track01.ogg").is_file()
        assert (project / "game" / "voice" / "0001.ogg").is_file()
        assert (project / "game" / "wav" / "0002.ogg").is_file()
        assert (project / "game" / "mov" / "0001.mpg").is_file()
        assert not (project / "game" / "images" / "grps" /
                    "ignored.wcg").exists()

        changed = project / "game" / "scenario" / "0000.rpy"
        changed.write_text("user edit\n", encoding="utf-8")
        try:
            build(resources, project)
        except FileExistsError:
            pass
        else:
            raise AssertionError("different generated files must not be overwritten")

    print("OK: generic port template")


if __name__ == "__main__":
    main()
