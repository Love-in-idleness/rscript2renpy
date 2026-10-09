"""The current LiarsoftTool TSC contract does not require GSC encoding metadata."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "port_template"))
from rscript_tsc import read_tsc

with TemporaryDirectory() as temporary:
    source = Path(temporary) / "current.tsc"
    source.write_text(';@gsc-byte-format legacy-28\n;@gsc-schema early\n'
                      '*TXT 0 0 0 0 "" "中文日本語" 1\n*end\n', encoding="utf-8")
    assert "中文日本語" in read_tsc(source).strings
    current = source.read_text(encoding="utf-8")
    strings = read_tsc(source).strings
    source.write_text(';@gsc-text-encoding invalid\n;@gsc-text-encoding GBK\n' + current, encoding="utf-8")
    assert read_tsc(source).strings == strings and read_tsc(source).encoding == "UTF-8"
    if len(sys.argv) > 2:
        generated = Path(temporary) / "generated.tsc"
        subprocess.run([sys.argv[1], '--gsc-to-tsc', sys.argv[2], '-o', str(generated)], check=True)
        assert ';@gsc-text-encoding' not in generated.read_text(encoding='utf-8')
        assert read_tsc(generated).instructions()
print('OK: current UTF-8 TSC without GSC encoding metadata')
