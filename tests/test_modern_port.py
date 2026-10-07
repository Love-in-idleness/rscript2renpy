#!/usr/bin/env python3
"""Shared modern lowering and full script/DLC overlay regression checks."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import shutil
import subprocess
import sys
import struct

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evermaiden"))
from build_evermaiden_rscript import build_evermaiden, IMAGE_FOLDERS
from modern_tsc import compile_overlays


def main():
    with TemporaryDirectory(prefix="modern-port-") as directory:
        directory = Path(directory)
        base, patch, project = [directory / name for name in ("base", "zh", "project")]
        for folder in ("scr", "grpe", "grpo", "grpo_ex", "grps", "bgm", "voice", "wav", *IMAGE_FOLDERS):
            (base / folder).mkdir(parents=True)
        (patch / "scr").mkdir(parents=True)
        header = ';@gsc-byte-format modern-36\n;@gsc-schema modern\n'
        source = ('*flagset 1 3 1\n*dynsel "Question" 0\n'
                  '*dynans "Always" 1 0 0\n*dynans "Once" 2 5024 0\n'
                  '*dynans "Unlocked" 3 5025 1\n*dyndo 2 0 1\n'
                  '*se 2 33\n*se_on 2 0 0 0\n*locmode 0 1 1 0\n'
                  '*insub 0 0 0 0 0 0 0 0 0 0 0\n'
                  '*TXT 0 10001 0 0 "Alice" "|漢字[かんじ]^nA^cyB" 0\n'
                  ':END\n*return 0\n')
        (base / 'scr/0000.tsc').write_text(header + source, encoding='utf-8')
        trailer = (struct.pack('<4I', 0, 1, 0, 6) + b'\0REP\0').hex()
        (base / 'scr/0001.tsc').write_text(
            header + ';@gsc-trailer-header 8 5\n;@gsc-trailer ' + trailer + '\n*wait 1\n*end\n')
        (patch / 'scr/0000.tsc').write_text(header + '*wait 2\n' + source.replace('Question', '问题'), encoding='utf-8')
        (patch / 'scr/5000.tsc').write_text(header + '*end\n')
        pcm = base / 'wav/0033.wav'
        pcm.write_bytes(b'PCM test')
        (base / 'wav/0034.wav').write_bytes(b'embedded Ogg wrapper')
        (base / 'wav/0034.ogg').write_bytes(b'Ogg test')
        added = patch / 'grpo_ex/9999.png'
        added.parent.mkdir()
        shutil.copyfile(ROOT / 'runtime/gui/rscript_cursor.png', added)
        files = compile_overlays(base, [('zh', patch)])
        assert len(files) == 7, files.keys()
        assert "if _preferences.language == 'zh':" in files['0000.rpy']
        assert 'jump _rscript_variant0_0000' in files['0000.rpy']
        assert 'only available' in files['5000.rpy']
        assert 'jump _rscript_variant0_0001' in files['0001.rpy']
        assert 'label _g_0001_REP:' in files['0001.rpy']
        assert 'jump _g_rscript_variant0_0001_REP' in files['0001.rpy']
        assert 'label _g_rscript_variant0_0001_REP:' in files['variant0/0001.rpy']
        assert 'label _rscript_variant0_0001_L_000006:' in files['variant0/0001.rpy']
        script = files['variant0/0000.rpy']
        assert '_se 2 33' in script and '_se_on 2 0 0 0' in script
        assert '_insub _rscript_variant0_0000_L_' in script
        assert "_rscript_say ('Alice', '|漢字[かんじ]^nA^cyB', 0)" in script
        assert '_voice 10001 0 0 0' in script
        assert "_dynans ('Once', 2, 5024, 0)" in script
        assert '_flagset 1 3 1' in script
        build_evermaiden(base, project, languages=['jp', 'zh=' + str(patch)])
        game = project / 'game'
        assert (game / 'wav/0033.wav').is_file()
        assert (game / 'wav/0034.ogg').is_file() and not (game / 'wav/0034.wav').exists()
        assert (game / 'tl/zh/images/grpo_ex/9999.png').is_file()
        assert (game / 'ui_features.rpy').read_bytes() == (ROOT / 'port_template/game/ui_features.rpy').read_bytes()
        assert not (game / 'evermaiden_compat.rpy').exists()
        if len(sys.argv) > 1:
            shutil.copyfile(ROOT / 'tests/renpy_modern_port.rpy', game / 'modern_test.rpy')
            subprocess.run([str(Path(sys.argv[1]) / 'renpy.sh'), str(project), 'modernporttest',
                            '--savedir', str(directory / 'test-saves')], check=True,
                           env=os.environ | {'SDL_AUDIODRIVER': 'dummy',
                                             'RENPY_PATH_TO_SAVES': str(directory / 'sdk-saves')})
        print('OK: modern shared lowering, complete language/DLC routes and PCM assets')


if __name__ == '__main__':
    main()
