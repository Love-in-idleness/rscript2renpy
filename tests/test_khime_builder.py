#!/usr/bin/env python3
"""Smoke-check a converted Khime resource set without copying its assets."""

from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import struct
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "khime"))
from khime_tsc import compile_scene, read_tsc  # noqa: E402
from build_khime_rscript import build_khime  # noqa: E402
sys.path.insert(0, str(ROOT / "port_template"))
from grps_layout import collect_layout  # noqa: E402


def main() -> None:
    sources = sorted((Path(sys.argv[1]) / "scr").glob("*.tsc"))
    assert sources, "Khime TSC files missing"
    for source in sources:
        output = compile_scene(source)
        assert output.startswith("# Generated from ")
        assert "label _%s:" % source.stem in output
        tsc = read_tsc(source, "khime")
        assert output.count("    _end\n") == sum(
            item.opcode == 8 for item in tsc.instructions()), source
        for item in tsc.instructions():
            if item.opcode == 14:
                for index in (item.operands[1], *item.operands[7:7 + min(item.operands[0], 5)]):
                    caption = tsc.string(index)
                    if caption.startswith("<01>"):
                        assert repr(caption) in output, (source, caption)
    title = compile_scene(next(path for path in sources if path.stem == "0101"))
    assert "_khime_folder 0 'grpo_tp'" in title
    assert "_khime_setclk 41 1 3 0" in title
    assert "_khime_click 0 0 0" in title
    setup = compile_scene(next(path for path in sources if path.stem == "0111"))
    assert "_khime_locmode 0 1 1" in setup
    effect = compile_scene(next(path for path in sources if path.stem == "1102"))
    assert "_cls 1 19" in effect
    assert "_load 1 5043 400 300 19 0" in effect
    credit_source = next(path for path in sources if path.stem == "1110")
    credits = compile_scene(credit_source)
    credit_tsc = read_tsc(credit_source, "khime")
    first_font = next(item for item in credit_tsc.instructions() if item.opcode == 32)
    assert "_oload 20 400 188 4 0 %r" % credit_tsc.string(first_font.operands[5]) in credits
    radio_source = next(path for path in sources if path.stem == "1107")
    radio = compile_scene(radio_source)
    radio_tsc = read_tsc(radio_source, "khime")
    select = next(item for item in radio_tsc.instructions() if item.opcode == 14)
    # Preserve source text; do not require one particular localization.
    assert "$ khime_choice_prompt = %r" % radio_tsc.string(select.operands[1]) in radio
    assert "%r:" % radio_tsc.string(select.operands[7]) in radio
    masks = compile_scene(next(path for path in sources if path.stem == "1107"))
    assert "_effect 101 0" in masks
    masks = compile_scene(next(path for path in sources if path.stem == "3677"))
    assert "_update 16 " in masks
    assert "_jump 3673" in masks and "_return 0" in masks
    ending = compile_scene(next(path for path in sources if path.stem == "3661"))
    assert "label _3661_L_000112:\n    _end\n" in ending
    layout = collect_layout(Path(sys.argv[1]))
    assert layout["confscrn"]["items"]["bg"][:2] == (0, 0)
    assert layout["compane"]["items"]["hide"][:2] == (3, 67)
    assert layout["savescrn"]["items"]["next"][:2] == (412, 551)
    assert layout["sel_a01"]["items"]["text"][:2] == (55, 17)
    assert layout["tbox01"]["items"]["text"][:2] == (68, 27)
    with TemporaryDirectory() as temporary:
        resources = Path(temporary) / "resources"
        project = Path(temporary) / "project"
        (resources / "scr").mkdir(parents=True)
        shutil.copy2(next(path for path in sources if path.stem == "1110"),
                     resources / "scr" / "1110.tsc")
        for folder in ("grpe", "grpf", "grpo", "grpo_ex", "grpo_tp",
                       "grpp", "grps", "bgm", "voice", "wav", "mov"):
            (resources / folder).mkdir()
        patch = Path(temporary) / "patch"
        (patch / "grpo_tp").mkdir(parents=True)
        (patch / "grpo_tp" / "9001.bmp").write_bytes(
            b"BM" + struct.pack("<IHHI", 62, 0, 0, 54) +
            struct.pack("<IiiHHIIiiII", 40, 2, 1, 1, 32, 0, 8, 0, 0, 0, 0) +
            b"\x00\x00\x00\xff\x00\xff\x00\x00")
        (patch / "grpe").mkdir()
        shutil.copy2(patch / "grpo_tp" / "9001.bmp", patch / "grpe" / "9001.bmp")
        build_khime(resources, project, languages=["jp", "zh=%s" % patch])
        for folder in ("grpe", "grpo_tp"):
            with Image.open(project / "game" / "tl" / "zh" / "images" /
                            folder / "9001.png") as translated:
                assert translated.getpixel((0, 0)) == (0, 0, 0, 0)
                assert translated.getpixel((1, 0)) == (0, 255, 0, 255)
        notice = (ROOT / "port_template" / "android" / "notice.png").read_bytes()
        for name in ("android-presplash.png", "android-downloading.png"):
            assert (project / name).read_bytes() == notice
        assert (project / "game" / "touch_controls.rpy").read_bytes() == \
            (ROOT / "port_template" / "game" / "touch_controls.rpy").read_bytes()
        script = (project / "game" / "script.rpy").read_text(encoding="utf-8")
        assert "scene onlayer master\n    scene black onlayer black" in script
        credits = (project / "game" / "scenario" / "1110.rpy").read_text(encoding="utf-8")
        assert "_oload effect 4 flattened to 0" not in credits
        assert "_oload 20 400 188 4 0" in credits
        assert "unsupported text control ^fm flattened to empty" not in credits
        assert "'^fm企画・シナリオ'" in credits
        for name in ("04_rscript_audio.rpy", "character.rpy", "keymap.rpy",
                     "03_rscript_gfx.rpy", "00_rscript_wrap.rpy", "rscript_wrap.py"):
            assert (project / "game" / name).read_bytes() == (ROOT / "runtime" / name).read_bytes()
        options = (project / "game" / "options.rpy").read_text(encoding="utf-8")
        assert 'rscript_voice_format = "voice/%04d.ogg"' in options
        assert "rscript_ctc_x = 729" in options
        assert 729 + 24 + 8 == 800 - layout["compane"]["size"][0]
        click = (project / "game" / "ui_features.rpy").read_text(encoding="utf-8")
        assert 'key "game_menu" action Function(rscript_open_game_menu)' in click
        assert 'key "rollback" action Rollback()' in click
        assert "rscript_text what:" in click
        assert "xalign 0.5" in click and "text_align 0.5" in click
        assert "execute_append((None, repr(eval(value))))" in (
            project / "game" / "khime_compat.rpy").read_text(encoding="utf-8")
        keymap = (project / "game" / "keymap.rpy").read_text(encoding="utf-8")
        assert "'mousedown_3'" in keymap
        assert "'mousedown_4'" in keymap and "'mousedown_5'" in keymap
        assert '"mov/%04d.mpg"' in (project / "game" / "03_rscript_gfx.rpy").read_text(
            encoding="utf-8")
    print("OK: compiled %d Khime TSC files and title click flow" % len(sources))


if __name__ == "__main__":
    main()
