#!/usr/bin/env python3
"""Shared emission, early policy boundaries and per-language event ordering."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys
import struct

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "port_template"))
import tsc_compiler
from tsc_compiler import compile_scene, compile_overlays
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
        source.write_text(";@gsc-byte-format modern-36\n;@gsc-schema rscript18\n"
                          '*locmode 0 0 0\n*se 3\n*se_on 999 0 0\n'
                          '*se_off 0\n*getflag @100 1\n*getflag 23 0\n'
                          '*jump 1 ""\n', encoding="utf-8")
        result = compile_scene(source, adapter="modern")
        assert "_locmode 0 0 0" in result
        assert "_se 0 3\n    _se_on 0 999 0 0\n    _se_off 0 0" in result
        assert "_jump 1\n" in result
        assert "_getflag _r[100] 1\n    _getflag 23 0" in result
        modern = ";@gsc-byte-format modern-36\n;@gsc-schema modern\n"
        source.write_text(modern + '*move 1 20 30 11 0\n*phase 1 7\n*return 0\n', encoding="utf-8")
        for adapter in ("modern", "khime", "kagerou"):
            result = compile_scene(source, adapter=adapter)
            assert "    _move 1 20 30 11 0\n" in result
            assert "    _oaction 1 7\n" in result
        trailer = (struct.pack('<4I', 0, 1, 0, 46) + b'\0TOP1\0').hex()
        named = modern + ';@gsc-trailer-header 8 6\n;@gsc-trailer ' + trailer + '\n'
        named += '*insub L_00002e 0 0 0 0 0 0 0 0 0 0\n:L_00002e\n*return 0\n'
        source.write_text(named, encoding="utf-8")
        assert read_tsc(source, "modern").named_entries == (("TOP1", 46),)
        source.write_text(named.replace(':L_00002e', '*wait 1\n:L_00002e'), encoding="utf-8")
        relocated = read_tsc(source, "modern")
        assert relocated.named_entries == (("TOP1", 52),)
        assert relocated.instructions()[0].operands[0] == 52
        result = compile_scene(source, adapter="modern")
        assert 'label _g_0000_TOP1:' in result and '_insub _0000_L_000034' in result
        assert compile_scene(relocated, adapter="modern") == result
        base, translated = (Path(directory) / name for name in ("base", "zh"))
        for root in (base, translated):
            (root / "scr").mkdir(parents=True)
            (root / "scr/0000.tsc").write_text(source.read_text(), encoding="utf-8")
        (base / "scr/0001.tsc").write_text(modern + "*end\n", encoding="utf-8")
        with patch.object(tsc_compiler, "read_tsc", wraps=read_tsc) as reader:
            scenes = compile_overlays(base, [("zh", translated)])
        assert reader.call_count == 3, "each original/translated TSC must be parsed once"
        assert len({call.args[0] for call in reader.call_args_list}) == 3
        assert "label _g_0000_TOP1:" in scenes["scr/0000.rpy"]
        assert "jump _g_rscript_variant1_0000_TOP1" in scenes["scr/0000.rpy"]
        translated_source = translated / "scr/0000.tsc"
        translated_source.write_text(translated_source.read_text().replace("*wait 1", "*wait 2"),
                                     encoding="utf-8")
        updated = compile_overlays(base, [("zh", translated)])
        assert updated["scr/0000.rpy"] == scenes["scr/0000.rpy"]
        assert "_wait 2" in updated["tl/zh/scr/0000.rpy"]
        assert updated["tl/zh/scr/0000.rpy"] != scenes["tl/zh/scr/0000.rpy"]
        for invalid, message in (
                (named.replace(':L_00002e\n', ''), 'unknown label'),
                (named.replace('*insub L_00002e 0 0 0 0 0 0 0 0 0 0\n:L_00002e\n', ''),
                 'missing named-entry label'),
                (modern + '*data 0 1\n*end\n', 'data block is outside'),
                (modern + '*datablock 0 32768\n*end\n', 'signed 16-bit'),
                (early + ';@gsc-trailer-header 4 1\n*end\n', 'does not support trailer'),
                (early + ';@gsc-trailer 0000\n*end\n', 'does not support trailer'),
                (modern + ';@gsc-trailer-header 4 1\n;@gsc-trailer-header 4 1\n*end\n', 'duplicate trailer'),
                (modern + '*insub done 0 0 0 0 0 0 0 0 0 0\n:done\n', 'inside GSC code')):
            source.write_text(invalid, encoding="utf-8")
            try:
                read_tsc(source, "forest" if invalid.startswith(early) else "modern")
            except ValueError as error:
                assert message in str(error), error
            else:
                raise AssertionError("unsafe code/data reference accepted")
        source.write_text(modern + '*data 0 0\n*end\n', encoding="utf-8")
        assert read_tsc(source, "modern").instructions()
        assert '_data 0' in compile_scene(source, adapter="modern")
        try:
            compile_scene(source, language_texts={"bad-name": {}})
        except ValueError as error:
            assert "invalid language name" in str(error)
        else:
            raise AssertionError("unsafe language identifier accepted")
    print("OK: shared compiler preserves early/modern policies and language event order")


if __name__ == "__main__":
    main()
