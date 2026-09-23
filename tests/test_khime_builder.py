#!/usr/bin/env python3
"""Smoke-check a converted Khime resource set without copying its assets."""

from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "khime"))
from khime_tsc import compile_scene  # noqa: E402
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
        assert "<01>" not in output
    title = compile_scene(next(path for path in sources if path.stem == "0101"))
    assert "_khime_folder 0 'grpo_tp'" in title
    assert "_khime_setclk 41 1 3 0" in title
    assert "_khime_click 0 0 0" in title
    setup = compile_scene(next(path for path in sources if path.stem == "0111"))
    assert "_khime_locmode 0 1 1" in setup
    effect = compile_scene(next(path for path in sources if path.stem == "1102"))
    assert "_cls 1 19" in effect
    assert "_load 1 5043 400 300 19 0" in effect
    credits = compile_scene(next(path for path in sources if path.stem == "1110"))
    assert "_oload 20 400 188 4 0 '^fm企画・シナリオ'" in credits
    radio = compile_scene(next(path for path in sources if path.stem == "1107"))
    assert "$ khime_choice_prompt = 'さて'" in radio
    assert "'僕も降りるか。':" in radio
    masks = compile_scene(next(path for path in sources if path.stem == "1107"))
    assert "_effect 101 0" in masks
    masks = compile_scene(next(path for path in sources if path.stem == "3677"))
    assert "_update 16 " in masks
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
        build_khime(resources, project)
        script = (project / "game" / "script.rpy").read_text(encoding="utf-8")
        assert "scene onlayer master\n    scene black onlayer black" in script
        credits = (project / "game" / "scenario" / "1110.rpy").read_text(encoding="utf-8")
        assert "_oload effect 4 flattened to 0" in credits
        assert "unsupported text control ^fm flattened to empty" in credits
        for name in ("04_rscript_audio.rpy", "character.rpy", "keymap.rpy",
                     "03_rscript_gfx.rpy"):
            assert (project / "game" / name).read_bytes() == (ROOT / "runtime" / name).read_bytes()
        options = (project / "game" / "options.rpy").read_text(encoding="utf-8")
        assert 'rscript_voice_format = "voice/%04d.ogg"' in options
        assert "rscript_ctc_x = 747" in options
        click = (project / "game" / "khime_compat.rpy").read_text(encoding="utf-8")
        assert 'key "game_menu" action ShowMenu("preferences")' in click
        assert 'key "rollback" action Rollback()' in click
        keymap = (project / "game" / "keymap.rpy").read_text(encoding="utf-8")
        assert "'mousedown_3'" in keymap
        assert "'mousedown_4'" in keymap and "'mousedown_5'" in keymap
        assert '"mov/%04d.mpg"' in (project / "game" / "03_rscript_gfx.rpy").read_text(
            encoding="utf-8")
    print("OK: compiled %d Khime TSC files and title click flow" % len(sources))


if __name__ == "__main__":
    main()
