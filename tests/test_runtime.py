#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest.mock import patch
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from install_runtime import install, copy_file, write_script  # noqa: E402
import install_runtime


def main() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        runtime = root / "runtime"
        (runtime / "__pycache__").mkdir(parents=True)
        (runtime / "engine.rpy").write_text("label fixture:\n    return\n")
        (runtime / "engine.rpyc").write_bytes(b"stale cache")
        (runtime / "__pycache__/engine.pyc").write_bytes(b"host cache")
        project = root / "project"
        (project / "game").mkdir(parents=True)
        with patch.object(install_runtime, "RUNTIME", runtime):
            installed = install(project)
        assert [path.name for path in installed] == ["engine.rpy"]
        assert not (project / "game/engine/__pycache__").exists()
    files = sorted((ROOT / "runtime").glob("*.rpy"))
    assert len(files) == 20
    combined = "\n".join(path.read_text(encoding="utf-8") for path in files)
    for marker in ("class RScriptReg", "renpy.register_statement",
                   "def parse_txcls", "renpy.register_shader"):
        assert marker in combined
    assert "xalign gui.dialogue_text_xalign\n            xpos gui.dialogue_xpos" not in combined
    assert 'lang = lex.word()' in combined
    assert '"y": "#FFDE00", "g": rscript_green_color()' in combined
    assert '"w": "#FFFFFF", "k": "#000000"' in combined
    assert r"\^c([bgkopsrvwy])" in combined
    assert 'RScriptText(text_value, kind = "oload"' in combined
    assert 'args["Text"] = lex.rest()' in combined
    assert 'args[name] = lex.match(r"\\S+")' in combined
    assert 'properties["layout"] = "nobreak"' in combined
    assert "def parse_rscript_text(text, color_controls = False):" in combined
    assert 'renpy.re.subn(r"\\^m", "", text)' in combined
    assert "parse_rscript_text(repr(args.Text), True)" in combined
    assert '.rstrip()' not in combined
    assert 'text.replace(u"…", u"...")' not in combined
    assert 'text.replace("%",  "%%")' not in combined
    assert 'define config.old_substitutions = False' in combined
    assert "rscript_wrap.normalize_boundaries" in combined
    assert "{k=-2}" not in combined
    assert 'def rscript_wait_image(glow=False):' in combined
    assert 'rscript_layouts().get("wait%02d"' in combined
    assert 'config.mouse = {' in combined
    assert '"engine/gui/rscript_cursor.png", 0, 0' in combined
    assert "transform rscript_zoom_in:" in combined
    assert "elif effect == 1:" in combined
    assert "define rscript_dither = ImageDissolve(" in combined
    assert 'Tile("engine/gui/rscript_dither.svg")' in combined
    assert "im.Tile" not in combined
    assert "elif effect == 4:" in combined
    effects = (ROOT / "runtime/effects.rpy").read_text(encoding="utf-8")
    wave = effects[effects.index("    def rscript_trunc_div"):effects.index("    def rscript_diagonal_path")]
    motion = {"rscript_move4_timing": "fixed-steps", "rscript_dynamic_tick": .05}
    exec(dedent(wave), motion)
    path = motion["rscript_wave_path"]((0, 100), (300, 100), 1)
    assert path[2:] == (15, (1310700, 0), (0, -45), 8738)
    assert path == motion["rscript_wave_path"]((0, 100), (300, 100), 100)
    position = motion["rscript_wave_position"]
    assert position(path, 0) == (0, 100)
    assert position(path, .4) == (140, 80)
    assert position(path, .8) == (300, 100)
    reverse = motion["rscript_wave_path"]((300, 100), (0, 100), 0)
    assert position(reverse, .4) == (160, 120)
    diagonal = motion["rscript_wave_path"]((10, -20), (-90, 80), 0)
    assert position(diagonal, .3) == (-12, 26)
    motion["rscript_move4_timing"] = "script"
    assert motion["rscript_wave_path"]((0, 0), (300, 0), 10)[2] == 10
    assert motion["rscript_wave_path"]((0, 0), (300, 0), 30)[2] == 30
    assert motion["rscript_wave_path"]((0, 0), (300, 0), 65536)[2] == 15
    motion["rscript_move4_timing"] = "fixed-speed"
    assert motion["rscript_wave_path"]((0, 0), (300, 0), 99)[2] == 10
    short = motion["rscript_wave_path"]((10, 20), (11, 20), 0)
    assert short[2] == 0 and position(short, 10) == (10, 20)
    for timing in ("fixed-steps", "fixed-speed", "script"):
        motion["rscript_move4_timing"] = timing
        stationary = motion["rscript_wave_path"]((-10, -20), (-10, -20), 0)
        assert stationary[2] == 0 and position(stationary, 10) == (-10, -20)
    for folder in ("forest", "sevenbridge"):
        assert 'rscript_move4_timing = "fixed-steps"' in (ROOT / folder / "game/options.rpy").read_text()
    assert 'rscript_move4_timing = "fixed-speed"' in (ROOT / "cannonball/game/options.rpy").read_text()
    assert 'store.rscript_move4_timing = "fixed-steps"' in (ROOT / "khime/game/khime_zero.rpy").read_text()
    for amplitude, steps, first, middle in ((40, 4, 1, -28), (100, 10, 4, -97), (300, 15, 14, -291)):
        offset = motion["rscript_bounce_offset"]
        assert offset(amplitude, steps, 0) == 0
        assert offset(amplitude, steps, 1) == first
        assert offset(amplitude, steps, steps // 2) == middle
        assert offset(amplitude, steps, steps + 1) == 0
    assert "elif effect == 2:" in combined
    assert 'define rscript_update_timing = "legacy"' in combined
    assert 'class RScriptOrderedDissolve(' in combined
    assert '# trans = Pixellate(ef_time, step / 2)' in combined
    assert 'renpy.curry(RScriptOrderedDissolve)(ef_time, step or 10)' in combined
    assert "ef_time = rscript_update_duration(effect, step, wait)" in combined
    assert "def rscript_update_duration(effect, step, wait):" in combined
    assert "rollforward = [ 'K_PAGEDOWN', 'repeat_K_PAGEDOWN', 'mousedown_5' ]" in combined
    assert "dismiss = [ 'mouseup_1', 'mousedown_5'" in combined
    assert "game_menu = [ 'K_ESCAPE', 'K_MENU', 'mousedown_3' ]" in combined
    assert '"mov/%04d.mpg"' in combined
    for python2_only in ('basestring', 'ur"', "ur'", '(int, long, float)',
                         'print "'):
        assert python2_only not in combined

    with TemporaryDirectory() as temporary:
        project = Path(temporary)
        (project / "game").mkdir()
        installed = install(project)
        assert len(installed) == 25
        assert (project / "game" / "engine" / "rscript_wrap.py").is_file()
        assert all(path.is_file() for path in installed)
        assert (project / "game" / "engine" / "gui" / "rscript_cursor.png").is_file()
        assert (project / "game" / "engine" / "gui" / "rscript_dither.svg").is_file()
        assert (project / "game" / "engine" / "gui" / "rscript_empty.svg").is_file()
        script = project / "game/engine/01_defines.rpy"
        cache = script.with_suffix(".rpyc")
        script.write_text("user edit\n", encoding="utf-8")
        cache.write_bytes(b"existing cache")
        try:
            install(project)
        except FileExistsError:
            pass
        else:
            raise AssertionError("runtime installation must preserve conflicting edits")
        assert script.read_text() == "user edit\n"
        assert cache.read_bytes() == b"existing cache"
        install(project, force=True)
        assert script.read_bytes() == (ROOT / "runtime/01_defines.rpy").read_bytes()
        assert not cache.exists()
        copy_file(script, script)
        destination = project / "generated/测试.rpy"
        write_script("label test:\n    # 中文\n    return\n", destination)
        cache = destination.with_suffix(".rpyc")
        cache.write_bytes(b"existing cache")
        try:
            write_script("different\n", destination)
        except FileExistsError:
            pass
        else:
            raise AssertionError("generated script must preserve conflicting edits")
        assert "中文" in destination.read_text(encoding="utf-8")
        assert cache.read_bytes() == b"existing cache"
        write_script("different\n", destination, force=True)
        assert destination.read_text() == "different\n" and not cache.exists()
        cache.write_bytes(b"existing cache")
        write_script("different\n", destination)
        assert not cache.exists()
        old = project / "game/01_defines.rpy"
        old.write_text("old layout\n", encoding="utf-8")
        try:
            install(project, force=True)
        except FileExistsError as error:
            assert "fresh project" in str(error)
        else:
            raise AssertionError("old runtime must not be automatically moved or deleted")
        assert old.read_text() == "old layout\n"

    print("OK: 20 generic RScript runtime modules and shared glyph breaker")


if __name__ == "__main__":
    main()
