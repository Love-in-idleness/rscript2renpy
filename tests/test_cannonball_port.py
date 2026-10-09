#!/usr/bin/env python3
"""Legacy schemas, first-string TXT, short menus and full language overlays."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cannonball"))
from build_cannonball_rscript import build_cannonball
from rscript_tsc import read_tsc
from tsc_compiler import compile_scene, compile_overlays
from tsc_vm import emit_vm
from build_port import write_scenario


def main():
    # A temporary captures the value at execution time, not a live expression.
    namespace = {"_r": {7: 12}, "rscript_vm_temps": {}}
    temps = {}
    for line in emit_vm(0xf200, (0, 7), temps, snapshot=True):
        exec(line.removeprefix("$ "), namespace)
    namespace["_r"][7] = 99
    for line in emit_vm(0xa400, (1, 0, 3), temps, snapshot=True):
        exec(line.removeprefix("$ "), namespace)
    assert namespace["rscript_vm_temps"] == {0: 12, 1: 15}
    with TemporaryDirectory(prefix="cannonball-test-") as directory:
        directory = Path(directory)
        base, patch, project = (directory / name for name in ("base", "zh", "project"))
        for folder in ("scr", "grpe", "grpo", "grps", "bgm", "voice", "wav/wav", "backup"):
            (base / folder).mkdir(parents=True)
        (patch / "scr").mkdir(parents=True)
        header = ";@gsc-byte-format legacy-28\n;@gsc-schema pre-codex\n"
        body = ('*se 7\n*gosub 1\n*se_on 0 0 0\n'
                '*TXT 0 91 0 0 "^g001body" "stale string"\n'
                '*select 1 "prompt" END END END END END "answer" "" "" "" ""\n'
                ':END\n*bgm_on 1 2\n*bgm_off 2\n*muldev -3 5 2\n'
                '*numload 1 0 2 0\n*numreng 1 0 100 0 0\n'
                '*numloc 1 20 16\n*numset 1 0 0 10 4\n*numenable 1 1\n*num 1 42 1\n*end\n')
        source = base / "scr/0000.tsc"
        source.write_text(header + body, encoding="utf-8")
        (base / "scr/0001.tsc").write_text(header + "*return 0\n")
        result = compile_scene(source, adapter="pre-codex")
        assert "_say '^g001body'" in result and "stale string" not in result
        assert "_r[0] = 0" in result
        assert result.index("_se 0 7") < result.index("_gosub 1") < result.index("_se_on 0 0 0 0")
        assert "BGM fade 2 flattened to 0" in result and "_bgm_on 1 0 0" in result
        assert "_r[0] = rscript_muldev(-3, 5, 2)" in result
        assert "_rscript_number num 1 42 1" in result
        for schema, suffix in (("early-short-select", ' 1'), ("early", ' 1')):
            text = body.replace('"stale string"', '"stale string"' + suffix)
            if schema == "early":
                text = text.replace('"answer" "" "" "" ""', '"answer" "" "" "" "" 0 0 0')
            source.write_text(header.replace("pre-codex", schema) + text)
            assert "_say '^g001body'" in compile_scene(source, adapter="pre-codex")
        source.write_text(header.replace("pre-codex", "rscript18") + '*voice 71737 0 0 0\n*vm 0xf000 0 -1\n*end\n')
        assert read_tsc(source, "legacy").instructions()[1].operands == (0, -1)
        assert "_voice 71737 0 0 0" in compile_scene(source, adapter="pre-codex")
        source.write_text(header + body)
        try:
            read_tsc(source, "forest")
        except ValueError as error:
            assert "Forest requires" in str(error)
        else:
            raise AssertionError("new dialect leaked into Forest")
        (patch / "scr/0000.tsc").write_text(header + "*wait 4\n" + body.replace("body", "译文"))
        (patch / "scr/5000.tsc").write_text(header + "*end\n")
        files = compile_overlays(base, [("zh", patch)], adapter="pre-codex")
        assert "only available" in files["scr/5000.rpy"]
        assert "_wait 4" in files["tl/zh/scr/0000.rpy"]
        assert "_preferences.language == 'zh'" in files["scr/0000.rpy"]
        for name in ("grpe/0901.png", "grpo/0002.png", "grps/TBOX01B.png", "grps/tbox_w.png", "backup/private.png"):
            shutil.copyfile(ROOT / "runtime/gui/rscript_cursor.png", base / name)
        for name in ("bgm/Track01.wav", "voice/0001.ogg", "wav/wav/0001.ogg"):
            (base / name).write_bytes(b"unplayed fixture")
        build_cannonball(base, project, languages=["jp", "zh=" + str(patch)])
        game = project / "game"
        assert not (game / "backup").exists()
        assert (game / "grps/TBOX01B.png").is_file()
        assert (game / "wav/wav/0001.ogg").is_file()
        assert "wav/wav/%04d.ogg" in (game / "engine/audio_paths.rpy").read_text()
        assert not list(game.glob("*.rpy"))
        for name in ("07_rscript_legacy.rpy", "character.rpy", "images.rpy"):
            assert (game / "engine" / name).read_bytes() == (ROOT / "runtime" / name).read_bytes()
        try:
            build_cannonball(base, base / "output")
        except ValueError as error:
            assert "inside original" in str(error)
        else:
            raise AssertionError("source/output overlap accepted")
        if len(sys.argv) > 1:
            if len(sys.argv) > 3:
                original, translated = map(Path, sys.argv[2:4])
                title_files = compile_overlays(original, [("zh", translated)], adapter="pre-codex")
                for name, text in title_files.items():
                    if Path(name).stem in {"0000", "0001", "0002"}:
                        destination = game / name
                        write_scenario(text, destination, original, force=True)
                for number in (2, 3, 10, *range(11, 30)):
                    for asset in (original / "grpo").glob("%04d.*" % number):
                        if asset.suffix in {".png", ".webp"}:
                            shutil.copyfile(asset, game / "grpo" / asset.name)
                (game / "title_test.rpy").write_text(
                    "define rscript_test_native_title = True\nlabel _3000:\n    return\n")
            shutil.copyfile(ROOT / "tests/renpy_cannonball_port.rpy", game / "legacy_test.rpy")
            subprocess.run([str(Path(sys.argv[1]) / "renpy.sh"), str(project), "cannonballtest",
                            "--savedir", str(directory / "saves")], check=True, timeout=60,
                           env=os.environ | {"RENPY_PATH_TO_SAVES": str(directory / "sdk-saves")})
        if len(sys.argv) > 3:
            base, patch = map(Path, sys.argv[2:4])
            files = compile_overlays(base, [("zh", patch)], adapter="pre-codex")
            assert len(list((base / "scr").glob("*.tsc"))) == 626
            assert len(list((patch / "scr").glob("*.tsc"))) == 437
            assert not any("unlifted opcode" in text for text in files.values())
            print("OK: all 1063 supplied CannonBall TSCs compile with complete patch routes")
    print("OK: legacy schemas, text/menu/SE semantics, resources and language routes")


if __name__ == "__main__":
    main()
