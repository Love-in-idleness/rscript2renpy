#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import build  # noqa: E402
from effect_compat import flatten_unsupported_effects  # noqa: E402
from text_compat import flatten_unsupported_text_controls  # noqa: E402
from grps_layout import collect_layout  # noqa: E402


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
            "    _khime_say '^fmHello ^crred ^g001^nnext ^cyyellow'\n"
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
        assert runtime_count == 21
        assert copied >= 12
        notice = (ROOT / "port_template" / "android" / "notice.png").read_bytes()
        for name in ("android-presplash.png", "android-downloading.png"):
            assert (project / name).read_bytes() == notice
        assert (project / "game" / "touch_controls.rpy").read_bytes() == \
            (ROOT / "port_template" / "game" / "touch_controls.rpy").read_bytes()
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
        assert "unsupported text control ^fm, ^cr flattened to empty" in scene
        assert "_khime_say 'Hello red ^g001^nnext ^cyyellow'" in scene
        assert flatten_unsupported_text_controls(scene) == scene
        expression = "    _say jp {'en': '^a601A', 'zh': '^cg绿'}.get(lang, '^n日本')\n"
        lowered = flatten_unsupported_text_controls(expression)
        assert "^a601 flattened to empty" not in lowered
        assert "'en': '^a601A'" in lowered
        assert "'^cg绿'" in lowered and "'^n日本'" in lowered
        numeric_body = "    _say '^g999１２３^g001123^a601２^s12'\n"
        assert flatten_unsupported_text_controls(numeric_body) == numeric_body
        assert "    pass\n" in scene
        assert flatten_unsupported_effects(scene, resources) == scene
        assert "scene onlayer master" in (project / "game" / "script.rpy").read_text(
            encoding="utf-8")
        assert "label main_menu:\n    # Returning lets Ren'Py enter start" in (
            project / "game" / "script.rpy").read_text(encoding="utf-8")
        assert "    jump start" not in (project / "game" / "script.rpy").read_text(
            encoding="utf-8")
        assert "screen rscript_compane():" in (project / "game" / "grps_ui.rpy").read_text(
            encoding="utf-8")
        save_ui = (project / "game" / "grps_ui.rpy").read_text(encoding="utf-8")
        save_ui += (project / "game" / "ui_features.rpy").read_text(encoding="utf-8")
        assert 'data["rscript_dt1"] = int(store._r[1])' in save_ui
        assert 'FileJson(slot, key="rscript_dt1")' in save_ui
        assert 'images/grps/dt1_%04d.png' in save_ui
        assert 'key "game_menu" action Function(rscript_open_game_menu)' in (
            project / "game" / "grps_ui.rpy").read_text(encoding="utf-8")
        assert 'key "rollback" action Rollback()' in (
            project / "game" / "grps_ui.rpy").read_text(encoding="utf-8")
        assert 'text rscript_menu_text(item.caption):' in (
            project / "game" / "grps_ui.rpy").read_text(encoding="utf-8")
        assert collect_layout(resources) == {}
        assert "define rscript_grps_layout = {}" in (
            project / "game" / "grps_layout.rpy").read_text(encoding="utf-8")
        masks = root / "masks" / "grps"
        masks.mkdir(parents=True)
        (masks / "ef16.png").write_bytes(b"mask")
        assert flatten_unsupported_effects("    _update 16 10 10\n",
                                           root / "masks") == "    _update 16 10 10\n"
        dynamic = flatten_unsupported_effects("    _load 1 2 3 4 _r[9] 0\n",
                                               resources)
        assert "effect _r[9] flattened to 0 (not statically supported)" in dynamic
        preserved = flatten_unsupported_effects("    _load 1 2 3 4 _r[9] 0\n",
                                                 resources, preserve_dynamic=True)
        assert "_load 1 2 3 4 _r[9] 0" in preserved
        assert "preserved for runtime validation" in preserved
        assert "flattened" not in preserved
        (masks / "ef11.msk").write_bytes(b"converted by install_base")
        assert flatten_unsupported_effects("    _update 11 10 10\n",
                                           root / "masks") == "    _update 11 10 10\n"
        assert (project / "game" / "images" / "grps" / "ui" /
                "panel.png").is_file()
        assert (project / "game" / "bgm" / "Track01.ogg").is_file()
        assert (project / "game" / "voice" / "0001.ogg").is_file()
        assert (project / "game" / "wav" / "0002.ogg").is_file()
        assert (project / "game" / "mov" / "0001.mpg").is_file()
        assert '"mov/%04d.mpg"' in (project / "game" / "03_rscript_gfx.rpy").read_text(
            encoding="utf-8")
        keymap = (project / "game" / "keymap.rpy").read_text(encoding="utf-8")
        assert "game_menu = [ 'K_ESCAPE', 'K_MENU', 'mousedown_3' ]" in keymap
        assert "rollforward = [ 'K_PAGEDOWN', 'repeat_K_PAGEDOWN', 'mousedown_5' ]" in keymap
        assert not (project / "game" / "images" / "grps" /
                    "ignored.wcg").exists()

        changed = project / "game" / "scenario" / "0000.rpy"
        cache = changed.with_suffix(".rpyc")
        cache.write_bytes(b"obsolete cache")
        build(resources, project, force=True)
        assert not cache.exists()
        changed.write_text("user edit\n", encoding="utf-8")
        try:
            build(resources, project)
        except FileExistsError:
            pass
        else:
            raise AssertionError("different generated files must not be overwritten")

        conf = resources / "grps" / "confscrn"
        conf.mkdir()
        (conf / "bg.png").write_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x03\x20\x00\x00\x02\x58")
        try:
            collect_layout(resources)
        except ValueError as error:
            assert ".meta.xml" in str(error)
        else:
            raise AssertionError("UI without canvas metadata must fail visibly")
        (conf / ".meta.xml").write_text(
            '<Canvas><Width>800</Width><Height>600</Height><Items>'
            '<Item x="4" y="2" flag="40">bg</Item></Items></Canvas>',
            encoding="utf-8")
        assert collect_layout(resources)["confscrn"]["items"]["bg"] == (4, 2, 800, 600)
        (conf / ".meta.xml").write_text(
            '<Canvas><Width>800</Width><Height>600</Height><Items>'
            '<Item x="4" y="2" flag="40">bg</Item>'
            '<Item x="0" y="0" flag="8" empty="1">bg</Item>'
            '</Items></Canvas>', encoding="utf-8")
        assert collect_layout(resources)["confscrn"]["items"]["bg"] == (4, 2, 800, 600), \
            "metadata-only LWG entry must not override its same-named image"

    print("OK: generic port template")


if __name__ == "__main__":
    main()
