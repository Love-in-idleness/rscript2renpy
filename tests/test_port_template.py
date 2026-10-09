#!/usr/bin/env python3

from pathlib import Path
import json
from tempfile import TemporaryDirectory
import sys
from contextlib import redirect_stdout
from io import StringIO
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import build, install_version  # noqa: E402
from effect_compat import flatten_unsupported_effects  # noqa: E402
from text_compat import flatten_unsupported_text_controls  # noqa: E402
from grps_layout import collect_layout  # noqa: E402
from rscript_tsc import read_tsc  # noqa: E402


def main() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        choices = root / "choices.tsc"
        choices.write_text(
            ';@gsc-byte-format modern-36\n;@gsc-schema modern\n'
            '*dynsel "Question" 0\n'
            '*dynans "调查少女像" 1 5024 0\n'
            '*dynans "调查少女像" @1 -2 0\n'
            '*dynnext "Next"\n*dyndo 2 0 1\n*end\n', encoding="utf-8")
        choice_tsc = read_tsc(choices, "khime")
        assert choice_tsc.strings == ("", "Question", "调查少女像", "Next")
        decoded = choice_tsc.instructions()
        assert [item.opcode for item in decoded] == [210, 211, 211, 212, 213, 8]
        assert decoded[1].operands == (2, 1, 5024, 0)
        assert decoded[2].operands == (2, 0x10001, 0xfffe, 0)
        assert choice_tsc.code_size == 68
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
            "    _khime_say '^fmHello ^crred ^g001^nnext ^cyyellow ^fzunknown ^q'\n"
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
        assert runtime_count == 23
        assert (project / "game/engine/port_version.rpy").read_text() == \
            'define config.version = "1.3"\n'
        android = {"version": "0.1", "numeric_version": 200,
                   "package": "test.keep.package", "permissions": ["VIBRATE"]}
        (project / "android.json").write_text(json.dumps(android))
        install_version(project)
        android["version"] = "1.3"
        assert json.loads((project / "android.json").read_text()) == android
        assert copied >= 12
        notice = (ROOT / "port_template" / "android" / "notice.png").read_bytes()
        for name in ("android-presplash.png", "android-downloading.png"):
            assert (project / name).read_bytes() == notice
        assert (project / "game" / "engine" / "touch_controls.rpy").read_bytes() == \
            (ROOT / "port_template" / "game" / "touch_controls.rpy").read_bytes()
        assert (project / "game" / "scr" / "0000.rpy").is_file()
        scene = (project / "game" / "scr" / "0000.rpy").read_text(
            encoding="utf-8")
        assert "_oload 1 2 3 4 0 'text with spaces'" in scene
        assert "_load 1 2 3 4 19 0" in scene
        assert "_oload effect 4 flattened" not in scene
        assert "_load effect 19 flattened" not in scene
        assert "_update effect 16 flattened to 0 (missing grps/ef16.png)" in scene
        assert "_effect effect 101 flattened to 0 (missing grps/es101.png)" in scene
        assert "_draw blend mode 3 flattened to 0" in scene
        assert "_oaction action 7 flattened to no-op" in scene
        assert "unsupported text control ^fz, ^q flattened to empty" in scene
        assert "_khime_say '^fmHello ^crred ^g001^nnext ^cyyellow unknown '" in scene
        controls = "    _oload 1 0 0 0 0 '^FM^CRred^FG^CW ^CB^CS^CP^CV^CO ^V-123^N'\n"
        assert flatten_unsupported_text_controls(controls) == controls
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
        assert flatten_unsupported_effects("    _cls 42 14\n", resources) == "    _cls 42 14\n"
        assert "compound zoom transition not implemented" in flatten_unsupported_effects(
            "    _update 116 16 0\n", resources)
        assert "scene onlayer master" in (project / "game" / "engine" / "script.rpy").read_text(
            encoding="utf-8")
        assert "label main_menu:\n    # Returning lets Ren'Py enter start" in (
            project / "game" / "engine" / "script.rpy").read_text(encoding="utf-8")
        assert "    jump start" not in (project / "game" / "engine" / "script.rpy").read_text(
            encoding="utf-8")
        assert "screen rscript_compane():" in (project / "game" / "engine" / "grps_ui.rpy").read_text(
            encoding="utf-8")
        save_ui = (project / "game" / "engine" / "grps_ui.rpy").read_text(encoding="utf-8")
        save_ui += (project / "game" / "engine" / "ui_features.rpy").read_text(encoding="utf-8")
        assert 'data["rscript_dt1"] = int(store._r[1])' in save_ui
        assert 'FileJson(slot, key="rscript_dt1")' in save_ui
        assert 'grps/dt1_%04d.png' in save_ui
        assert 'key "game_menu" action Function(rscript_open_game_menu)' in (
            project / "game" / "engine" / "grps_ui.rpy").read_text(encoding="utf-8")
        assert 'key "rollback" action Rollback()' in (
            project / "game" / "engine" / "grps_ui.rpy").read_text(encoding="utf-8")
        assert 'text rscript_menu_text(caption):' in (
            project / "game" / "engine" / "grps_ui.rpy").read_text(encoding="utf-8")
        assert collect_layout(resources) == {}
        assert "define rscript_grps_layout = {}" in (
            project / "game" / "engine" / "grps_layout.rpy").read_text(encoding="utf-8")
        masks = root / "masks" / "grps"
        masks.mkdir(parents=True)
        (masks / "ef16.png").write_bytes(b"mask")
        assert flatten_unsupported_effects("    _update 16 10 10\n",
                                           root / "masks") == "    _update 16 10 10\n"
        dynamic = flatten_unsupported_effects("    _load 1 2 3 4 _r[9] 0\n",
                                               resources, preserve_dynamic=False)
        assert "effect _r[9] flattened to 0 (not statically supported)" in dynamic
        preserved = flatten_unsupported_effects("    _load 1 2 3 4 _r[9] 0\n",
                                                 resources)
        assert "_load 1 2 3 4 _r[9] 0" in preserved
        assert "preserved for runtime validation" in preserved
        assert "flattened" not in preserved
        for command in ("_movi 1 2 3 6 8", "_movi 1 2 3 105 8",
                        "_load 1 2 3 4 _r[6503] _r[904]",
                        "_cls 1 _r[6501]", "_effect _r[6511] 0"):
            result = flatten_unsupported_effects("    " + command + "\n", resources)
            assert command in result and "flattened" not in result
        (masks / "ef11.msk").write_bytes(b"converted by install_base")
        assert flatten_unsupported_effects("    _update 11 10 10\n",
                                           root / "masks") == "    _update 11 10 10\n"
        (masks / "ES101.PNG").write_bytes(b"mask")
        assert flatten_unsupported_effects("    _effect 101 1\n",
                                           root / "masks") == "    _effect 101 1\n"
        for effect in (2, 3, 4, 10, 15, 19):
            source = ("    _load 1 2 3 4 %d 0\n"
                      "    _oload 20 30 40 %d 0 'object'\n"
                      "    _cls 20 %d\n") % (effect, effect, effect)
            assert flatten_unsupported_effects(source, resources) == source
        assert "effect 99 flattened" in flatten_unsupported_effects(
            "    _oload 20 30 40 99 0 'unknown'\n", resources)
        assert (project / "game" / "grps" / "ui" /
                "panel.png").is_file()
        assert (project / "game" / "bgm" / "Track01.ogg").is_file()
        assert (project / "game" / "voice" / "0001.ogg").is_file()
        assert (project / "game" / "wav" / "0002.ogg").is_file()
        assert (project / "game" / "mov" / "0001.mpg").is_file()
        assert '"mov/%04d.mpg"' in (project / "game" / "engine" / "03_rscript_gfx.rpy").read_text(
            encoding="utf-8")
        keymap = (project / "game" / "engine" / "keymap.rpy").read_text(encoding="utf-8")
        assert "game_menu = [ 'K_ESCAPE', 'K_MENU', 'mousedown_3' ]" in keymap
        assert "rollforward = [ 'K_PAGEDOWN', 'repeat_K_PAGEDOWN', 'mousedown_5' ]" in keymap
        assert not (project / "game" / "grps" /
                    "ignored.wcg").exists()

        changed = project / "game" / "scr" / "0000.rpy"
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

        legacy = root / "legacy-project"
        (legacy / "game/images/grps").mkdir(parents=True)
        (legacy / "game/images/grps/old.png").write_bytes(b"preserved image")
        (legacy / "game/scenario").mkdir()
        (legacy / "game/scenario/0000.rpy").write_text("user scene edit\n")
        (legacy / "game/saves").mkdir()
        (legacy / "game/saves/1.save").write_bytes(b"player progress")
        try:
            build(resources, legacy, force=True)
        except FileExistsError:
            pass
        else:
            raise AssertionError("legacy layout must fail instead of migrating files")
        assert (legacy / "game/images/grps/old.png").read_bytes() == b"preserved image"
        assert (legacy / "game/scenario/0000.rpy").read_text() == "user scene edit\n"
        assert (legacy / "game/saves/1.save").read_bytes() == b"player progress"
        assert not (legacy / ".rscript-legacy-layout").exists()

        conf = resources / "grps" / "confscrn"
        conf.mkdir()
        Image.new("RGB", (800, 600)).save(conf / "bg.png")
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
        Image.new("RGB", (640, 480)).save(conf / "bg.webp")
        assert collect_layout(resources)["confscrn"]["items"]["bg"] == (4, 2, 640, 480)
        (conf / "bg.png").unlink()
        assert collect_layout(resources)["confscrn"]["items"]["bg"] == (4, 2, 640, 480)
        patch = root / "ui-patch/grps/confscrn"
        patch.mkdir(parents=True)
        (patch / ".meta.xml").write_bytes((conf / ".meta.xml").read_bytes())
        Image.new("RGB", (320, 240)).save(patch / "bg.png")
        assert collect_layout(root / "ui-patch", fallback=resources)["confscrn"]["items"]["bg"] == (4, 2, 320, 240)
        Image.new("RGB", (800, 600)).save(conf / "bg.png")
        (conf / "bg.webp").unlink()
        (conf / ".meta.xml").write_text(
            '<Canvas><Width>800</Width><Height>600</Height><Items>'
            '<Item x="4" y="2" flag="40">bg</Item>'
            '<Item x="0" y="0" flag="8" empty="1">bg</Item>'
            '</Items></Canvas>', encoding="utf-8")
        assert collect_layout(resources)["confscrn"]["items"]["bg"] == (4, 2, 800, 600), \
            "metadata-only LWG entry must not override its same-named image"
        (conf / "unknown_off.png").write_bytes((conf / "bg.png").read_bytes())
        (conf / ".meta.xml").write_text(
            '<Canvas><Width>800</Width><Height>600</Height><Items>'
            '<Item x="0" y="0">unknown_off</Item></Items></Canvas>')
        warning = StringIO()
        with redirect_stdout(warning):
            layout = collect_layout(resources)
        assert layout["confscrn"]["unhandled"] == ["unknown_off"]
        assert "unbound UI controls" in warning.getvalue()

    print("OK: generic port template")


if __name__ == "__main__":
    main()
