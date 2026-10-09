#!/usr/bin/env python3
"""Legacy schemas, first-string TXT, short menus and full language overlays."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import shutil
import subprocess
import sys
import textwrap
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cannonball"))
from build_cannonball_rscript import build_cannonball
from rscript_tsc import read_tsc
from tsc_compiler import compile_scene, compile_overlays
from tsc_vm import emit_vm, packed
from build_port import write_scenario
from ui_layout import BUTTONS, PANE, SAVE_BUTTONS, extract_native_ui, native_layouts
from exe_ui import constant_positions, inspect_exe


def main():
    assert constant_positions([(1, "lea edi,[esi+0x68]"), (2, "mov eax,DWORD PTR [edi]"),
                               (3, "push 0x14a"), (4, "push 0x110"),
                               (5, "call DWORD PTR [eax+0x78]")], 0, 6) == {0x68: (272, 330)}
    # A temporary captures the value at execution time, not a live expression.
    namespace = {"_r": {7: 12}, "rscript_vm_temps": {}}
    temps = {}
    for line in emit_vm(0xf200, (0, 7), temps, snapshot=True):
        exec(line.removeprefix("$ "), namespace)
    namespace["_r"][7] = 99
    for line in emit_vm(0xa400, (1, 0, 3), temps, snapshot=True):
        exec(line.removeprefix("$ "), namespace)
    assert namespace["rscript_vm_temps"] == {0: 12, 1: 15}
    # Execute the runtime helpers, not a second implementation in the test.
    helpers = (ROOT / "runtime/07_rscript_legacy.rpy").read_text().split("python early:\n")[1].split("    def parse_rscript_number")[0]
    exec(textwrap.dedent(helpers), namespace)
    for family, left, right, expected in (
            (10, 100, 65535, 99), (10, 65535, 1, 0), (11, 0, 1, 65535),
            (12, 256, 256, 0), (5, 65535, 0, 0), (8, 65535, 0, 1),
            (4, -1, 65535, 1), (9, -1, 65535, 0),
            (13, 65529, 3, 65534), (14, 65529, 3, 65535),
            (13, 32768, 65535, 32768), (2, 4, 5, 1), (3, 4, 5, 1)):
        for line in emit_vm(family << 12, (0, left, right), {}, snapshot=True, word16=True):
            exec(line.removeprefix("$ "), namespace)
        assert namespace["rscript_vm_temps"][0] == expected, (family, left, right)
    for opcode, operands in ((0xf000, (0, -1)), (0x1800, (0, 7, -1))):
        for line in emit_vm(opcode, operands, {}, snapshot=True, word16=True):
            exec(line.removeprefix("$ "), namespace)
        assert namespace["rscript_vm_temps"][0] == 65535
    assert namespace["_r"][7] == 65535
    assert eval(packed(0x10007, word16=True), namespace) == -1
    assert packed(0x10007) == "_r[7]"  # Other adapters retain their semantics.
    with TemporaryDirectory(prefix="cannonball-test-") as directory:
        directory = Path(directory)
        base, patch, project = (directory / name for name in ("base", "zh", "project"))
        for folder in ("scr", "grpe", "grpo", "grps", "bgm", "voice", "wav/wav", "mov", "backup"):
            (base / folder).mkdir(parents=True)
        for number in (1, 2):
            (base / 'mov' / ('%04d.mpg' % number)).write_bytes(b'unplayed fixture')
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
        assert "BGM fade 2: nonzero enables the native 2000 ms fade" in result
        assert "_bgm_on 1 1 2000" in result and "_bgm_off 1 2000" in result
        source.write_text(header + '*bgm_on 1 0\n*bgm_off @7\n*draw 1 3 50\n*draw 1 99 50\n*draw 1 @8 50\n*end\n')
        lowered = compile_scene(source, adapter="pre-codex")
        assert "_bgm_on 1 0 2000" in lowered
        assert "_bgm_off int(bool(rscript_signed16(_r[7]))) 2000" in lowered
        assert lowered.count("_draw 1 0 50") == 2
        assert "native normal-drawing alias" in lowered and "flattened" not in lowered
        assert "_draw 1 {1:1,2:2}.get(rscript_signed16(_r[8]),0) 50" in lowered
        # Lowered expressions must survive the common visual compatibility pass.
        from effect_compat import flatten_unsupported_effects
        assert "flattened" not in flatten_unsupported_effects(lowered, base)
        source.write_text(header + body)
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
        for source, _, _, _ in BUTTONS.values():
            width = 108 if source == "con_07c" else 85 if source.startswith("con_07") or source in {"con_14", "con_15"} else 80 if source in {"con_10", "con_11", "con_12"} else 140
            Image.new("RGBA", (width, 42), "#ffffff").save(base / "grps" / (source.upper() + ".png"))
        for source, size in (("CON_BASE", (518, 387)), ("TBOX_C01", (194, 18)),
                             ("TBOX_C08", (5, 30)), *(("con_%d" % n, (21, 42)) for n in (16, 17, 18)),
                             *((source, (17, 34)) for name, source in PANE if name is not None),
                             ("dat_bgs", (800, 600)), ("dat_bgl", (800, 600)), ("dat_no", (38, 340)),
                             ("dat_re", (56, 52)), ("dat_p01", (40, 68)), ("dat_p02", (40, 68)),
                             ("DT1_0001", (255, 60)), ("DT1_0002", (255, 60)),
                             ("BAR01", (468, 11)), ("BAR02", (336, 36)), ("BAR03", (336, 36))):
            Image.new("RGBA", size, "#ffffff").save(base / "grps" / (source + ".png"))
        Image.new("RGBA", (520, 100), "#ffffff").save(base / "grps/SEL_A.png")
        Image.new("RGBA", (520, 56), "#ffffff").save(base / "grps/SEL_Q.png")
        layout = native_layouts(base)
        assert layout["confscrn"]["size"] == (518, 387)
        assert layout["sel_a"]["size"] == (520, 50)
        assert layout["sel_a"]["images"]["body_f"][1] == (0, 50, 520, 50)
        assert layout["sel_q"]["size"] == (520, 56)
        assert layout["confscrn"]["items"]["save"] == (157, 330, 85, 21)
        assert layout["confscrn"]["images"]["save_f"][1] == (0, 21, 85, 21)
        assert layout["confscrn"]["background_dim"] == 204 / 256
        assert layout["compane"]["items"]["hide"] == (179, 1, 17, 17)
        assert set(layout["compane"]["controls"]) == {"rev", "bak", "fow", "next", "voc", "hide"}
        assert layout["savescrn"]["size"] == (800, 600)
        assert layout["savescrn"]["items"]["0"] == (125, 137, 255, 60)
        assert layout["savescrn"]["items"]["5"] == (400, 137, 255, 60)
        assert layout["savescrn"]["items"]["9"] == (400, 405, 255, 60)
        assert layout["savescrn"]["images"]["page10"][1] == (0, 306, 38, 34)
        assert not layout["savescrn"]["page_wrap"]
        for name, (source, x, y) in SAVE_BUTTONS.items():
            assert layout["savescrn"]["items"][name][:2] == (x, y)
        Image.new("RGBA", (518, 387), "#000000").save(base / "grps/CON_BASE.webp")
        assert native_layouts(base)["confscrn"]["images"]["bg"][0].endswith(".webp")
        invalid = directory / "invalid.exe"
        invalid.write_bytes(b"MZ")
        try:
            inspect_exe(invalid, base)
        except ValueError:
            pass
        else:
            raise AssertionError("truncated EXE accepted")
        for name in ("bgm/Track01.wav", "voice/0001.ogg", "wav/wav/0001.ogg"):
            (base / name).write_bytes(b"unplayed fixture")
        build_cannonball(base, project, languages=["jp", "zh=" + str(patch)])
        game = project / "game"
        assert not (game / "backup").exists()
        assert (game / "grps/TBOX01B.png").is_file()
        assert (game / "wav/wav/0001.ogg").is_file()
        assert "wav/wav/%04d.ogg" in (game / "engine/audio_paths.rpy").read_text()
        assert 'define rscript_boot_movies = (2, 1)' in (game / 'engine/ui_features.rpy').read_text()
        assert 'rscript_boot_movies =' not in (game / 'engine/options.rpy').read_text()
        for number in (1, 2):
            assert (game / 'mov' / ('%04d.mpg' % number)).read_bytes() == b'unplayed fixture'
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
                report = extract_native_ui(original / "Cannonball.exe", original)
                assert report["layouts"] == native_layouts(original)
                assert len(report["layouts"]["confscrn"]["controls"]) == 20
                assert "tbox_c08" in report["resource_references"]
                assert "tbox%02db" in report["resource_references"]
                assert "con_06a" not in report["resource_references"]
                unknown = directory / "unknown.exe"
                unknown.write_bytes((original / "Cannonball.exe").read_bytes() + b"\0")
                unsupported = extract_native_ui(unknown, original)
                assert not unsupported["layouts"] and "Unsupported EXE" in unsupported["unresolved"][0]
                title_files = compile_overlays(original, [("zh", translated)], adapter="pre-codex")
                for name, text in title_files.items():
                    if Path(name).stem in {"0000", "0001", "0002", "1011", "1071", "1072"}:
                        destination = game / name
                        write_scenario(text, destination, original, force=True)
                for number in (2, 3, 10, *range(11, 30)):
                    for asset in (original / "grpo").glob("%04d.*" % number):
                        if asset.suffix in {".png", ".webp"}:
                            shutil.copyfile(asset, game / "grpo" / asset.name)
                for folder, numbers in (("grpe", (404,)), ("grpo_r1", (801, 802, 811)),
                                        ("grpo_cl", (1401, 1801, 741, 201, 601, 6, 7, 8, 9, 10))):
                    for resources, output in ((original, game), (translated, game / "tl/zh")):
                        for number in numbers:
                            for asset in (resources / folder).glob("%04d.*" % number):
                                if asset.suffix in {".png", ".webp"}:
                                    destination = output / folder / asset.name
                                    destination.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copyfile(asset, destination)
                for folder, details in report["layouts"].items():
                    for path, crop in details["images"].values():
                        shutil.copyfile(original / path, game / path)
                        # Translation lookup must prefer PNG over the base WebP.
                        patched = translated / Path(path).with_suffix(".png")
                        if patched.is_file():
                            destination = game / "tl/zh" / patched.relative_to(translated)
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copyfile(patched, destination)
                for number in (1, 2):
                    for asset in (original / "grps").glob("DT1_%04d.*" % number):
                        if asset.suffix in {".png", ".webp"}:
                            shutil.copyfile(asset, game / "grps" / asset.name)
                (game / "engine/native_ui.rpy").write_text('init 10 python:\n    rscript_ui["layouts"] = %r\n' % report["layouts"])
                (game / "title_test.rpy").write_text(
                    "define rscript_test_native_title = True\nlabel _3000:\n    return\n")
            shutil.copyfile(ROOT / "tests/renpy_cannonball_port.rpy", game / "legacy_test.rpy")
            subprocess.run([str(Path(sys.argv[1]) / "renpy.sh"), str(project), "cannonballtest",
                            "--savedir", str(directory / "saves")], check=True, timeout=60,
                           env=os.environ | {"RENPY_PATH_TO_SAVES": str(directory / "sdk-saves")})
            if "--render" in sys.argv:
                shutil.copyfile(ROOT / "tests/renpy_cannonball_click.rpy", game / "scr/click_render_test.rpy")
                subprocess.run(["xvfb-run", "-a", str(Path(sys.argv[1]) / "renpy.sh"), str(project),
                                "run", "--savedir", str(directory / "render-saves")],
                               check=True, timeout=45, env=os.environ | {
                                   "SDL_VIDEODRIVER": "x11", "SDL_AUDIODRIVER": "dummy",
                                   "RENPY_SKIP_SPLASHSCREEN": "1", "RENPY_PERFORMANCE_TEST": "0",
                                   "RENPY_PATH_TO_SAVES": str(directory / "render-sdk-saves")})
                for suffix in ('.rpy', '.rpyc'):
                    (game / 'scr' / ('click_render_test' + suffix)).unlink(missing_ok=True)
                shutil.copyfile(ROOT / 'tests/renpy_boot_movies.rpy', game / 'scr/0000.rpy')
                (game / 'scr/0000.rpyc').unlink(missing_ok=True)
                result = subprocess.run(['xvfb-run', '-a', str(Path(sys.argv[1]) / 'renpy.sh'),
                                         str(project), 'run', '--savedir', str(directory / 'boot-saves')],
                                        check=True, timeout=45, capture_output=True, text=True,
                                        env=os.environ | {
                                            'SDL_VIDEODRIVER': 'x11', 'SDL_AUDIODRIVER': 'dummy',
                                            'RENPY_SKIP_SPLASHSCREEN': '', 'RENPY_SKIP_MAIN_MENU': '1',
                                            'RENPY_PERFORMANCE_TEST': '0',
                                            'RENPY_PATH_TO_SAVES': str(directory / 'boot-sdk-saves')})
                assert 'OK: native startup movies play in order only on launch' in result.stdout, result.stdout + result.stderr
                print('OK: CannonBall startup movies and return to title')
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
