#!/usr/bin/env python3
"""Shared emission, early policy boundaries and per-language event ordering."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "port_template"))
from tsc_compiler import compile_scene
from rscript_tsc import read_tsc


def main():
    with TemporaryDirectory() as directory:
        source = Path(directory) / "0000.tsc"
        early = ";@gsc-byte-format legacy-28\n;@gsc-schema early\n"
        source.write_text(early + '*wait 10\n*setclk 1 2 3 4\n'
                          '*fontsize 40 22\n*se 7\n*se_on 999 0 0\n'
                          '*gosub @2\n*return 0\n'
                          '*TXT 0 91 0 0 "^cw" "body" 1\n'
                          '*TXA 0 0 0 0 "append" 0\n'
                          '*face 1 2\n*end\n', encoding="utf-8")
        tsc = read_tsc(source)
        items = {item.opcode: item for item in tsc.instructions()}
        overrides = {"zh": {items[13].offset: (40,),
                             items[70].offset: (1, 2, 30, 40),
                             items[120].offset: (40, 25)}}
        insertions = {"zh": {items[81].offset: ("_wait 2", "_oload 1 0 0 0 0 'subtitle'"),
                              tsc.code_size: ("_cls 1 0",)}}
        result = compile_scene(
            source, adapter="early", statement_prefix="fixture", language="jp",
            language_texts={"zh": {(items[81].offset, "say"): "译文"}},
            language_operands=overrides, language_insertions=insertions)
        assert "        _wait 40\n    else:\n        _wait 10" in result
        assert "        _fixture_setclk 1 2 30 40\n    else:\n        _fixture_setclk 1 2 3 4" in result
        assert "        _osize 40 25\n    else:\n        _osize 40 22" in result
        assert "_se 0 7\n    _se_on 0 999 0 0" in result
        assert "_gosub _r[2]\n    return" in result
        assert "_say jp {'zh': '译文'}.get(_preferences.language, 'body')" in result
        assert "_append jp 'append'" in result and "forest" not in result
        assert result.index("'subtitle'") < result.index("_voice 91") < result.index("_say jp")
        assert result.endswith("        _cls 1 0\n    return\n")
        assert "# unlifted opcode 0x0030" in result and "_fixture_face" not in result

        source.write_text(";@gsc-byte-format modern-36\n;@gsc-schema modern\n"
                          '*return @2\n*end\n', encoding="utf-8")
        result = compile_scene(source, adapter="modern")
        assert "_return _r[2]\n    _end" in result
        try:
            compile_scene(source, language_texts={"bad-name": {}})
        except ValueError as error:
            assert "invalid language name" in str(error)
        else:
            raise AssertionError("unsafe language identifier accepted")
    print("OK: shared compiler preserves early/modern policies and language event order")


if __name__ == "__main__":
    main()
