#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
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
    assert '"y": "#C8AF00", "k": "#000000"' in combined
    assert "xmaximum = font_size * 19" in combined
    assert "def parse_rscript_text(text, color_controls = False):" in combined
    assert "parse_rscript_text(repr(args.Text), True)" in combined
    assert 'config.mouse = {' in combined
    assert '"gui/rscript_cursor.png", 0, 0' in combined
    for python2_only in ('basestring', 'ur"', "ur'", '(int, long, float)',
                         'print "'):
        assert python2_only not in combined

    with TemporaryDirectory() as temporary:
        project = Path(temporary)
        (project / "game").mkdir()
        installed = install(project)
        assert len(installed) == 17
        assert all(path.is_file() for path in installed)

    print("OK: 17 generic RScript runtime modules")


if __name__ == "__main__":
    main()
