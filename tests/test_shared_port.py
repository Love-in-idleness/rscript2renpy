#!/usr/bin/env python3
"""Build disposable Forest/Khime bases and exercise native shared features."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import shutil
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forest"))
sys.path.insert(0, str(ROOT / "khime"))
from build_forest_rscript import main as build_forest
from build_khime_rscript import build_khime
from khime_tsc import compile_scene


def main():
    with TemporaryDirectory(prefix="rscript-shared-") as temporary:
        temporary = Path(temporary)
        for name in ("Forest", "Khime"):
            resources = temporary / (name + "-resources")
            folders = ("scr", "grpe", "grpf", "grpo", "grpo_bg", "grpo_bu",
                       "grpo_ci", "grpo_f", "grpo_ex", "grpo_tp", "grpp",
                       "grps", "bgm", "voice", "wav", "mov")
            for folder in folders:
                (resources / folder).mkdir(parents=True)
            header = (";@gsc-byte-format legacy-28\n;@gsc-schema early\n"
                      if name == "Forest" else
                      ";@gsc-byte-format modern-36\n;@gsc-schema modern\n")
            script = resources / "scr/0000.tsc"
            header += ";@gsc-text-encoding CP932\n"
            script.write_text(header + "*end\n", encoding="utf-8")
            for asset in ("grpe/9001.png", "grps/gf707.png"):
                shutil.copy2(ROOT / "runtime/gui/rscript_cursor.png", resources / asset)
            panel = resources / "grps/compane"
            panel.mkdir()
            for button in ("rev", "bak"):
                shutil.copy2(ROOT / "runtime/gui/rscript_cursor.png", panel / (button + ".png"))
            for button in ("bg", "slide", "slide_f", "rev_f", "bak_f", "fow", "fow_f",
                           "next", "next_f", "voc", "voc_f", "voc_off", "hide", "hide_f"):
                shutil.copy2(ROOT / "runtime/gui/rscript_cursor.png", panel / (button + ".png"))
            (panel / ".meta.xml").write_text(
                '<Canvas><Width>64</Width><Height>32</Height><Items>'
                '<Item x="0" y="0">rev</Item><Item x="32" y="0">bak</Item>'
                '</Items></Canvas>', encoding="utf-8")
            textbox = resources / "grps/tbox01"
            textbox.mkdir()
            shutil.copy2(ROOT / "runtime/gui/rscript_cursor.png", textbox / "back.png")
            (textbox / ".meta.xml").write_text(
                '<Canvas><Width>800</Width><Height>138</Height><Items>'
                '<Item x="0" y="0">back</Item></Items></Canvas>', encoding="utf-8")
            answer = resources / "grps/sel_a00"
            answer.mkdir()
            for image in ("body", "body_f"):
                shutil.copy2(ROOT / "runtime/gui/rscript_cursor.png", answer / (image + ".png"))
            (answer / ".meta.xml").write_text(
                '<Canvas><Width>505</Width><Height>82</Height><Items>'
                '<Item x="0" y="0">body</Item><Item x="0" y="0">body_f</Item>'
                '</Items></Canvas>', encoding="utf-8")
            for asset in ("bgm/Track01.ogg", "wav/0001.ogg", "voice/0001.ogg",
                          "mov/0001.mpg", "mov/0002.mpg"):
                (resources / asset).write_bytes(b"unused fixture")
            project = temporary / name
            if name == "Forest":
                build_forest(["build_forest_rscript.py", str(resources), str(project)])
            else:
                patch = temporary / "translation"
                (patch / "scr").mkdir(parents=True)
                text = ('*font 20 400 200 0 0 "overlay"\n'
                        '*TXT 0 0 0 0 "Alice" "body" 0\n'
                        '*TXA 0 0 0 0 "append" 0\n'
                        '*select 1 "question" END END END END END "answer" "" "" "" "" 0 0 0\n'
                        ':END\n*end\n')
                script.write_text(header + text, encoding="utf-8")
                (patch / "scr/0000.tsc").write_text(
                    header + text.replace('"body"', '"译文"').replace('"overlay"', '"字幕"')
                    .replace('"append"', '"追加"').replace('"answer"', '"选项"'), encoding="utf-8")
                translated = compile_scene(script, patches=[("zh", patch)])
                for word in ("译文", "字幕", "追加", "选项"):
                    assert word in translated
                assert "khime_menu_caption_0" in translated
                (patch / "scr/0000.tsc").write_text(
                    header + text.replace('*TXT', '*wait 7\n*font 21 400 220 0 0 "added subtitle"\n*cls 21 0\n*TXT'),
                    encoding="utf-8")
                subtitles = compile_scene(script, patches=[("zh", patch)])
                assert "added subtitle" in subtitles and "_wait 7" in subtitles
                assert "_cls 21 0" in subtitles
                assert "if _preferences.language == 'zh':" in subtitles
                (patch / "scr/0000.tsc").write_text(
                    header + text.replace('"body"', '"译文"').replace('"overlay"', '"字幕"')
                    .replace('"append"', '"追加"').replace('"answer"', '"选项"'), encoding="utf-8")
                build_khime(resources, project, languages=["jp", "zh=" + str(patch)])
                assert "('zh', 'zh')" in (project / "game/language_config.rpy").read_text()
                assert (project / "game/tl/zh/rscript_strings.rpy").is_file()
                (patch / "scr/0000.tsc").write_text(
                    header + text.replace("*font 20", "*font 21"), encoding="utf-8")
                try:
                    compile_scene(script, patches=[("zh", patch)])
                except ValueError:
                    pass
                else:
                    raise AssertionError("Khime must not silently flatten non-text patch changes")
            for filename in ("text_features.rpy", "touch_controls.rpy", "gui.rpy"):
                assert (project / "game" / filename).read_bytes() == \
                    (ROOT / "port_template/game" / filename).read_bytes()
            for source in (ROOT / "runtime").glob("*.rpy"):
                assert (project / "game" / source.name).read_bytes() == source.read_bytes()
            if len(sys.argv) > 1:
                shutil.copy2(ROOT / "tests/renpy_shared_features.rpy",
                             project / "game/shared_features_test.rpy")
                subprocess.run([str(Path(sys.argv[1]) / "renpy.sh"), str(project),
                                "sharedporttest", "--savedir", str(project / "test-saves")], check=True)
                shutil.copy2(ROOT / "tests/renpy_rev_controls.rpy",
                             project / "game/scenario/0000.rpy")
                command = [str(Path(sys.argv[1]) / "renpy.sh"), str(project),
                           "run", "--savedir", str(project / "test-saves")]
                environment = os.environ | {"RENPY_PERFORMANCE_TEST": "0",
                                            "RENPY_SKIP_SPLASHSCREEN": "1",
                                            "RENPY_SKIP_MAIN_MENU": "1",
                                            "SDL_AUDIODRIVER": "dummy"}
                if shutil.which("xvfb-run"):
                    command = ["xvfb-run", "-a", *command]
                    environment["SDL_VIDEODRIVER"] = "x11"
                with subprocess.Popen(command, env=environment, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True,
                                      start_new_session=True) as process:
                    try:
                        output, _ = process.communicate(timeout=45)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        output, _ = process.communicate()
                        raise AssertionError("rev test timed out: " + output[-4000:])
                assert process.returncode == 0, output[-4000:]
                assert "OK: native menu updates rev target" in output, output[-4000:]
                print("OK: rev returns to latest choice: " + name)
    print("OK: both ports install shared runtime/templates and subtitle patch alignment")


if __name__ == "__main__":
    main()
