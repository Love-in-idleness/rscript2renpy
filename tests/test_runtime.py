#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from install_runtime import install  # noqa: E402


def main() -> None:
    files = sorted((ROOT / "runtime").glob("*.rpy"))
    assert len(files) == 17
    combined = "\n".join(path.read_text(encoding="utf-8") for path in files)
    for marker in ("class RScriptReg", "renpy.register_statement",
                   "def parse_txcls", "renpy.register_shader"):
        assert marker in combined
    assert "xalign gui.dialogue_text_xalign\n            xpos gui.dialogue_xpos" not in combined
    assert 'lang = lex.word()' in combined
    assert '"y": "#FFDE00", "g": "#D7FFB3"' in combined
    assert '"w": "#FFFFFF", "k": "#000000"' in combined
    assert r"\^c([ygwk])" in combined
    assert "xmaximum = font_size * 19" in combined
    assert "def parse_rscript_text(text, color_controls = False):" in combined
    assert 'renpy.re.subn(r"\\^m[ \\t]*", "", text)' in combined
    assert "parse_rscript_text(repr(args.Text), True)" in combined
    line_break_pattern = r"[ \t]*(\^n)([\<\>]?)[ \t]*"
    assert line_break_pattern in combined
    assert re.sub(line_break_pattern, r"\1\2", "left^n\u3000right") == \
        "left^n\u3000right"
    assert "{k=-2}" not in combined
    assert '"grps wait00 body"\n            xpos 4\n            ypos 5' in combined
    assert 'config.mouse = {' in combined
    assert '"gui/rscript_cursor.png", 0, 0' in combined
    assert "transform rscript_zoom_in:" in combined
    assert "elif effect == 1:" in combined
    assert "define rscript_dither = ImageDissolve(" in combined
    assert 'Tile("gui/rscript_dither.svg")' in combined
    assert "im.Tile" not in combined
    assert "elif effect == 4:" in combined
    assert "ef_time = step * wait / 100." in combined
    assert "ef_time = step * wait / 1000." not in combined
    assert "rollforward = [ 'K_PAGEDOWN', 'repeat_K_PAGEDOWN' ]" in combined
    assert "dismiss = [ 'mouseup_1', 'mousedown_5'" in combined
    for python2_only in ('basestring', 'ur"', "ur'", '(int, long, float)',
                         'print "'):
        assert python2_only not in combined

    with TemporaryDirectory() as temporary:
        project = Path(temporary)
        (project / "game").mkdir()
        installed = install(project)
        assert len(installed) == 19
        assert all(path.is_file() for path in installed)
        assert (project / "game" / "gui" / "rscript_cursor.png").is_file()
        assert (project / "game" / "gui" / "rscript_dither.svg").is_file()

    print("OK: 17 generic RScript runtime modules")


if __name__ == "__main__":
    main()
