#!/usr/bin/env python3
"""TXT rebase must preserve native code/data and reject misaligned dialogue."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kagerou"))
from rebase_translation import exported_strings, gsc_parts, rebase, run, translation_txt


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: test_kagerou_rebase.py LIARSOFTTOOL')
    tool = Path(sys.argv[1]).resolve()
    with TemporaryDirectory(prefix='kagerou-rebase-test-') as directory:
        base, patch = (Path(directory) / name for name in ('original', 'patch'))
        for folder in (base, patch):
            (folder / 'scr').mkdir(parents=True)
        header = ';@gsc-byte-format modern-36\n;@gsc-schema modern\n*datablock 0 0\n'
        jp = header + '*queue\n*TXT 0 10001 0 0 "" "First^n100%。" 1\n*return 0\n'
        old = header + '*TXT 0 10001 0 0 "" "正文^n百分之百。" 1\n*return 0\n'
        source = base / 'scr/1000.tsc'
        donor = patch / 'scr/1000.tsc'
        source.write_text(jp, encoding='utf-8')
        donor.write_text(old, encoding='utf-8')
        run(tool, '-e', 'cp932', '-o', source.with_suffix('.gsc'), source)
        before = {p: p.read_bytes() for p in (source, source.with_suffix('.gsc'), donor)}
        preview = rebase(base, patch, tool)
        assert preview['scenes'] == [{'scene': '1000', 'translated_strings': 1}]
        assert all(p.read_bytes() == content for p, content in before.items())
        # The explicit edited TSC wins over the ordinary donor, and is backed up.
        edit = patch / 'scr/1000_zh.tsc'
        edit.write_text(old.replace('正文', '修订正文'), encoding='utf-8')
        edited = edit.read_bytes()
        result = rebase(base, patch, tool, apply=True)
        assert gsc_parts(patch / 'scr/1000.gsc') == gsc_parts(source.with_suffix('.gsc'))
        backup = Path(result['backup']) / 'scr'
        assert (backup / donor.name).read_bytes() == before[donor]
        assert (backup / edit.name).read_bytes() == edited
        assert not edit.exists()
        assert '修订正文' in (patch / 'scr/1000.tsc').read_text(encoding='utf-8')
        assert source.read_bytes() == before[source]
        assert source.with_suffix('.gsc').read_bytes() == before[source.with_suffix('.gsc')]
        protected = (patch / 'scr/1000.tsc').read_bytes()
        (patch / 'scr/1000.tsc').write_text(old.replace('10001', '10002'), encoding='utf-8')
        bad = (patch / 'scr/1000.tsc').read_bytes()
        try:
            rebase(base, patch, tool, apply=True)
        except ValueError as error:
            assert 'metadata changed' in str(error)
        else:
            raise AssertionError('changed voice reference accepted')
        assert (patch / 'scr/1000.tsc').read_bytes() == bad
        (patch / 'scr/1000.tsc').write_bytes(protected)
        # No invented translation for newly added Japanese dialogue.
        extra = base / 'scr/1001.tsc'
        extra.write_text(jp, encoding='utf-8')
        run(tool, '-e', 'cp932', '-o', extra.with_suffix('.gsc'), extra)
        assert rebase(base, patch, tool)['untranslated_scenes'] == ['1001']
        sample = ['\u3000本文^n続き', '', '100%。']
        txt = Path(directory) / 'sections.txt'
        txt.write_text('#\\t本文\n続き\n>\n#\n>\n#100%。\n>\n', encoding='utf-8')
        assert exported_strings(txt) == sample
        for text in ('>section', '#section', ' leading space', '\U0001f600'):
            try:
                translation_txt([text])
            except ValueError:
                pass
            else:
                raise AssertionError('unrepresentable TXT accepted')
    print('OK: official TXT export/import, exact non-text bytes, donor precedence, backup and refusal')


if __name__ == '__main__':
    main()
