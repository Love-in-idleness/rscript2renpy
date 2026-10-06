#!/usr/bin/env python3
"""Side-story namespace, patch alignment, title row and PCM/OGG checks."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
import os
import signal
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "khime"))
from build_khime_rscript import build_khime
from khime_tsc import compile_scene
from zero import prepare_zero


def main():
    with TemporaryDirectory(prefix="khime-zero-check-") as directory:
        base = Path(directory)
        resources, zero, patch, main_patch = [base / n for n in ("main", "zero", "zh", "main-zh")]
        for folder in ("scr", "grpe", "grpf", "grpo", "grpo_ex", "grpo_tp", "grpp",
                       "grps", "bgm", "voice", "wav", "mov"):
            (resources / folder).mkdir(parents=True)
        modern = ";@gsc-byte-format modern-36\n;@gsc-schema modern\n"
        title = resources / "scr/0101.tsc"
        title.write_text(modern + '*load 46 9006 253 517 0 0\n*setlink 46 9106 253 517 0\n*end\n')
        original = compile_scene(title)
        extended = compile_scene(title, zero_title=True)
        assert "517+35*khime_zero_unlocked()" not in original
        assert extended.count("517+35*khime_zero_unlocked()") == 2
        assert "_load 46 9006 253 517+35*khime_zero_unlocked() 0 0" in extended
        assert "_khime_setlink 46 9106 253 517+35*khime_zero_unlocked() 0" in extended
        for folder in ("scr", "grpe", "grpo", "grpo_bu", "grps", "bgm", "wav", "voice"):
            (zero / folder).mkdir(parents=True)
        (patch / "scr").mkdir(parents=True)
        early = ";@gsc-byte-format legacy-28\n;@gsc-schema early\n"
        story = (early + '*bgm_on 2 0\n*gload 655 0\n*load 21 1902 320 240 0 0\n'
                 '*fontsize 21 20\n*font 21 320 240 0 0 "caption"\n'
                 '*TXT 0 0 0 0 "" "^g008body" 1\n*end\n')
        (zero / "scr/2001.tsc").write_text(story)
        (patch / "scr/2001.tsc").write_text(story.replace('body', '译文'))
        (patch / "grpo_bu").mkdir()
        for asset in ("grpo/0001.png", "grpo/0101.png", "grpe/0655.png",
                      "grpo_bu/1902.png", "grps/gf008.png"):
            shutil.copy2(ROOT / "runtime/gui/rscript_cursor.png", zero / asset)
        shutil.copy2(zero / "grpo_bu/1902.png", patch / "grpo_bu/1902.png")
        with wave.open(str(zero / "bgm/Track02.WAV"), "wb") as stream:
            stream.setparams((1, 2, 8000, 0, "NONE", "not compressed"))
            stream.writeframes(b"\0\0" * 80)
        (main_patch / "grpo_tp").mkdir(parents=True)
        shutil.copy2(zero / "grpo/0001.png", main_patch / "grpo_tp/9105.png")
        for name in ("9006.png", "9106.png"):
            shutil.copy2(zero / "grpo/0001.png", resources / "grpo_tp" / name)
        content = prepare_zero(zero, [("zh", patch)])
        assert "label _khime_zero_2001:" in content
        assert "'zh': '^g008译文'" in content
        assert "_osize 21 int(round((20)*1.25))" in content
        assert "_khime_zero_gload 655 0" in content
        project = base / "project"
        build_khime(resources, project, languages=["jp", "zh=" + str(main_patch)],
                    zero_resources=zero, zero_languages=["zh=" + str(patch)])
        game = project / "game"
        assert (game / "tl/zh/images/grpo_tp/9105.png").is_file()
        assert (game / "images/khime_zero/grpo_bu/1902.png").is_file()
        assert (game / "tl/zh/images/khime_zero/grpo_bu/1902.png").is_file()
        assert not (game / "images/grpo_bu/1902.png").exists()
        assert (game / "khime_zero/bgm/Track02.wav").is_file()
        assert "khime_zero_available = True" in (game / "zero_config.rpy").read_text()
        if len(sys.argv) > 3:
            sdk = Path(sys.argv[3])
            shutil.copy2(ROOT / "tests/renpy_khime_zero.rpy", game / "zero_test.rpy")
            subprocess.run([str(sdk / "renpy.sh"), str(project), "khimezerotest",
                            "--savedir", str(base / "test-saves")], check=True)
            command = [str(sdk / "renpy.sh"), str(project), "run",
                       "--savedir", str(base / "display-saves")]
            if shutil.which("xvfb-run"):
                command = ["xvfb-run", "-a", *command]
            with subprocess.Popen(command, env=os.environ | {
                    "RENPY_SKIP_SPLASHSCREEN": "1", "RENPY_SKIP_MAIN_MENU": "1",
                    "RENPY_PERFORMANCE_TEST": "0", "SDL_AUDIODRIVER": "dummy"},
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    start_new_session=True) as process:
                try:
                    output, _ = process.communicate(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    output, _ = process.communicate()
                    raise AssertionError("Zero display timed out: " + output[-4000:])
            assert process.returncode == 0, output[-4000:]
            assert "OK: native Zero dialogue interaction and clean return to title" in output, output[-4000:]
            from PIL import Image
            with Image.open(project / "zero-dialogue.png") as shot:
                # The dialogue must actually reach the bottom screen, not merely
                # exist as a widget thousands of pixels outside its container.
                crop = shot.crop((120, 437, 400, 500)).convert("RGB")
                assert any(min(crop.getpixel((x, y))) > 220
                           for y in range(crop.height) for x in range(crop.width))
            print("OK: rendered Zero dialogue and restart preserve main unlock")
            (game / "zero_test.rpy").unlink()
            (game / "zero_test.rpyc").unlink(missing_ok=True)
        build_khime(resources, project, force=True)
        assert "khime_zero_available = False" in (game / "zero_config.rpy").read_text()
        assert "khime_zero_unlocked()" not in (game / "scenario/0101.rpy").read_text()
        (zero / "grpo/0101.png").unlink()
        try:
            prepare_zero(zero, [])
        except FileNotFoundError as error:
            assert "grpo/0101.png" in str(error)
        else:
            raise AssertionError("missing hover artwork must fail before generation")
    if len(sys.argv) > 1:
        zero, patch = map(Path, sys.argv[1:3])
        content = prepare_zero(zero, [("zh", patch)])
        assert "label _khime_zero_2001:" in content and "'zh':" in content
    print("OK: isolated Khime Zero, aligned zh patch, conditional title row and PCM fallback")


if __name__ == "__main__":
    main()
