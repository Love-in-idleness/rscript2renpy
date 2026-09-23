#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import build  # noqa: E402
from effect_compat import flatten_unsupported_effects  # noqa: E402


def main() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        resources = root / "resources"
        project = root / "project"
        (resources / "scenario").mkdir(parents=True)
        (resources / "scenario" / "0000.rpy").write_text(
            "label _0000:\n"
            "    _oload 1 2 3 4 0 'text with spaces'\n"
            "    _load 1 2 3 4 19 0\n"
            "    _update 16 10 10\n"
            "    _effect 101 0\n"
            "    _draw 1 3 30\n"
            "    _oaction 1 7\n"
            "    return\n", encoding="utf-8")
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
        runtime_count, copied = build(resources, project)
        assert runtime_count == 19
        assert copied == 7
        assert (project / "game" / "scenario" / "0000.rpy").is_file()
        scene = (project / "game" / "scenario" / "0000.rpy").read_text(
            encoding="utf-8")
        assert "_oload effect 4 flattened to 0" in scene
        assert "_oload 1 2 3 0 0 'text with spaces'" in scene
        assert "_load effect 19 flattened to 0" in scene
        assert "_update effect 16 flattened to 0 (missing grps/ef16.png)" in scene
        assert "_effect effect 101 flattened to 0 (missing grps/es101.png)" in scene
        assert "_draw blend mode 3 flattened to 0" in scene
        assert "_oaction action 7 flattened to no-op" in scene
        assert "    pass\n" in scene
        assert flatten_unsupported_effects(scene, resources) == scene
        assert "scene onlayer master" in (project / "game" / "script.rpy").read_text(
            encoding="utf-8")
        masks = root / "masks" / "grps"
        masks.mkdir(parents=True)
        (masks / "ef16.png").write_bytes(b"mask")
        assert flatten_unsupported_effects("    _update 16 10 10\n",
                                           root / "masks") == "    _update 16 10 10\n"
        dynamic = flatten_unsupported_effects("    _load 1 2 3 4 _r[9] 0\n",
                                               resources)
        assert "effect _r[9] flattened to 0 (not statically supported)" in dynamic
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
