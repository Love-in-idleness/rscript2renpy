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
            for asset in ("grpe/9001.png", "grps/gf707.png", "grpo/0707.png", "grpo/1070.png"):
                shutil.copy2(ROOT / "runtime/gui/rscript_cursor.png", resources / asset)
            conf = resources / "grps/confscrn"
            conf.mkdir()
            for image in ("bg", "auto_lev", "auto_vol", "title", "exit"):
                shutil.copy2(ROOT / "runtime/gui/rscript_cursor.png", conf / (image + ".png"))
            (conf / ".meta.xml").write_text(
                '<Canvas><Width>800</Width><Height>600</Height><Items>'
                '<Item x="0" y="0">bg</Item><Item x="100" y="100">auto_lev</Item>'
                '<Item x="100" y="100">auto_vol</Item>'
                '<Item x="200" y="400">title</Item>'
                '<Item x="400" y="400">exit</Item></Items></Canvas>', encoding="utf-8")
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
            for folder in ("sel_a01", "sel_a02", "sel_a", "sel_q00", "sel_q01"):
                skin = resources / "grps" / folder
                skin.mkdir()
                for image in ("body", "body_f", "text"):
                    shutil.copy2(ROOT / "runtime/gui/rscript_cursor.png", skin / (image + ".png"))
                (skin / ".meta.xml").write_text(
                    '<Canvas><Width>505</Width><Height>82</Height><Items>'
                    '<Item x="0" y="0">body</Item><Item x="0" y="0">body_f</Item>'
                    '<Item x="10" y="4">text</Item></Items></Canvas>', encoding="utf-8")
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
                        '*select 1 "<01>question" END END END END END "<01>answer" "" "" "" "" 0 0 0\n'
                        ':END\n*end\n')
                script.write_text(header + text, encoding="utf-8")
                (patch / "scr/0000.tsc").write_text(
                    header + text.replace('"body"', '"译文"').replace('"overlay"', '"字幕"')
                    .replace('"append"', '"追加"').replace('"<01>answer"', '"<02>选项"'), encoding="utf-8")
                translated = compile_scene(script, patches=[("zh", patch)])
                for word in ("译文", "字幕", "追加", "选项"):
                    assert word in translated
                assert "khime_menu_caption_0" in translated
                assert "<01>answer" in translated and "<02>选项" in translated
                (patch / "scr/0000.tsc").write_text(
                    header + text.replace('*TXT', '*wait 7\n*font 21 400 220 0 0 "added subtitle"\n*cls 21 0\n*TXT'),
                    encoding="utf-8")
                subtitles = compile_scene(script, patches=[("zh", patch)])
                assert "added subtitle" in subtitles and "_wait 7" in subtitles
                assert "_cls 21 0" in subtitles
                assert "if _preferences.language == 'zh':" in subtitles
                (patch / "scr/0000.tsc").write_text(
                    header + text.replace('"body"', '"译文"').replace('"overlay"', '"字幕"')
                    .replace('"append"', '"追加"').replace('"<01>answer"', '"<02>选项"'), encoding="utf-8")
                build_khime(resources, project, languages=["jp", "zh=" + str(patch)])
                assert "('zh', 'zh')" in (project / "game/engine/language_config.rpy").read_text()
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
                assert (project / "game" / "engine" / filename).read_bytes() == \
                    (ROOT / "port_template/game" / filename).read_bytes()
            save_directory = ("Forest-rscript2renpy" if name == "Forest" else
                              "KhimeKusaritop-rscript2renpy")
            assert ('define config.save_directory = "%s"' % save_directory) in \
                (project / "game/engine/options.rpy").read_text(encoding="utf-8")
            assert "config.version" not in (project / "game/engine/options.rpy").read_text()
            assert (project / "game/engine/port_version.rpy").read_text() == \
                'define config.version = "1.2"\n'
            for source in (ROOT / "runtime").glob("*.rpy"):
                assert (project / "game" / "engine" / source.name).read_bytes() == source.read_bytes()
            if len(sys.argv) > 1:
                shutil.copy2(ROOT / "tests/renpy_shared_features.rpy",
                             project / "game/shared_features_test.rpy")
                subprocess.run([str(Path(sys.argv[1]) / "renpy.sh"), str(project),
                                "sharedporttest", "--savedir", str(project / "test-saves")], check=True,
                               env=os.environ | {"RENPY_PATH_TO_SAVES": str(temporary / "sdk-saves")})
                if "--logic-only" in sys.argv[2:]:
                    continue  # SDK parser/screen checks do not require X11.
                command = [str(Path(sys.argv[1]) / "renpy.sh"), str(project),
                           "run", "--savedir", str(project / "test-saves")]
                environment = os.environ | {"RENPY_PERFORMANCE_TEST": "0",
                                            "RENPY_SKIP_SPLASHSCREEN": "1",
                                            "RENPY_SKIP_MAIN_MENU": "1",
                                            "RENPY_PATH_TO_SAVES": str(temporary / "sdk-saves"),
                                            "SDL_AUDIODRIVER": "dummy"}
                if shutil.which("xvfb-run"):
                    command = ["xvfb-run", "-a", *command]
                    environment["SDL_VIDEODRIVER"] = "x11"
                for driver, marker in (("renpy_rev_controls", "OK: native menu updates rev target"),
                                       ("renpy_effects", "OK: native object effects"),
                                       ("renpy_registers", "OK: native bounded register reset"),
                                       ("renpy_end", "OK: native end discards nested story calls"),
                                       ("renpy_boot_movies", "OK: native startup movies play in order only on launch")):
                    shutil.copy2(ROOT / "tests" / (driver + ".rpy"),
                                 project / "game/scr/0000.rpy")
                    (project / "game/scr/0000.rpyc").unlink(missing_ok=True)
                    driver_environment = (environment | {"RENPY_SKIP_SPLASHSCREEN": ""}
                                          if driver in ("renpy_end", "renpy_boot_movies") else environment)
                    with subprocess.Popen(command, env=driver_environment, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, text=True,
                                          start_new_session=True) as process:
                        try:
                            output, _ = process.communicate(timeout=45)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL)
                            output, _ = process.communicate()
                            raise AssertionError(driver + " timed out: " + output[-4000:])
                    assert process.returncode == 0, output[-4000:]
                    assert marker in output, output[-4000:]
                    print(marker + ": " + name)
    print("OK: both ports install shared runtime/templates and subtitle patch alignment")


if __name__ == "__main__":
    main()
