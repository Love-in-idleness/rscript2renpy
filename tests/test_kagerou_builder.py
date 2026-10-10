#!/usr/bin/env python3
"""Scoped dialect checks and optional compilation of the full user-owned corpus."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
sys.path.insert(0, str(ROOT / "kagerou"))
from rscript_tsc import read_tsc
from tsc_compiler import compile_scene, compile_overlays
from build_kagerou_rscript import BONUS_SCENES, missing_voices, validate_edition


def main():
    with TemporaryDirectory(prefix="kagerou-compiler-") as directory:
        directory = Path(directory)
        base, patch = directory / "base", directory / "zh"
        for root in (base, patch):
            (root / "scr").mkdir(parents=True)
        try:
            validate_edition(base)
        except ValueError as error:
            assert 'ハチポチ特典' in str(error)
        else:
            raise AssertionError('unpatched edition accepted')
        for name in BONUS_SCENES:
            (base / ('scr/%s.tsc' % name)).touch()
        validate_edition(base)
        for name in BONUS_SCENES:
            (base / ('scr/%s.tsc' % name)).unlink()
        source = base / "scr/1000.tsc"
        source.write_text(';@gsc-byte-format modern-36\n;@gsc-schema rscript19\n'
            '*folder 1 "grpo_bu"\n*locmode 1 1 0 0\n'
            '*excmd 0 1 3011 0 0\n*se 1\n*se_on 1 0 0\n*se_off 1\n'
            '*TXT 0 10001 0 0 "discarded" "【女】^n本文" 1\n'
            '*TXA 0 0 0 0 "追加" 1\n*tclsmode 2\n*txcls 0\n*endscene\n*end\n',
            encoding="utf-8")
        compiled = compile_scene(source, adapter="kagerou")
        assert '_kagerou_say (\'discarded\', \'【女】^n本文\', 1)' in compiled
        assert '_kagerou_append (\'追加\', 1)' in compiled
        assert '_voice 10001 0 0 0' in compiled
        for statement in ('_kagerou_excmd 0 1 3011 0 0', '_kagerou_tclsmode 2',
                          '_kagerou_txcls 0', '_kagerou_endscene',
                          '_se 0 1', '_se_on 0 1 0 0', '_se_off 0 1'):
            assert statement in compiled, statement
        try:
            read_tsc(source, "modern")
        except ValueError:
            pass
        else:
            raise AssertionError("Kagerou EXCMD leaked into the general modern dialect")
        (patch / 'scr/1000.tsc').write_text(source.read_text().replace('本文', '正文'), encoding='utf-8')
        (base / 'scr/0000.tsc').write_text(';@gsc-byte-format modern-36\n;@gsc-schema modern\n*end\n', encoding='utf-8')
        scenes = compile_overlays(base, [('zh', patch)], adapter='kagerou')
        assert '正文' in scenes['tl/zh/scr/1000.rpy']
        assert '本文' in scenes['scr/1000.rpy']
        assert 'tl/zh/scr/0000.rpy' not in scenes
        assert missing_voices(base, [('zh', patch)]) == ['voice/1/0001']
        (base / 'voice/1').mkdir(parents=True)
        (base / 'voice/1/0001.wav').write_bytes(b'not played')
        assert missing_voices(base, [('zh', patch)]) == []
    if len(sys.argv) > 1:
        patches = [('zh', Path(sys.argv[2]))] if len(sys.argv) > 2 else []
        scenes = compile_overlays(Path(sys.argv[1]), patches, adapter='kagerou')
        assert len([p for p in scenes if p.startswith('scr/')]) == 162
        if patches:
            assert len([p for p in scenes if p.startswith('tl/zh/')]) == len(list((patches[0][1] / 'scr').glob('*.tsc')))
        assert not any('unlifted opcode' in content for content in scenes.values())
        print('OK: 162 bonus-edition scenes and optional Chinese overlay')
    print('OK: isolated EXCMD dialect, text operands, SE schema variants and fallback scenes')


if __name__ == '__main__':
    main()
