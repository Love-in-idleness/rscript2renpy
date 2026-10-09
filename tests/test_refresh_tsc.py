"""Validated batches never install a raw fallback or overwrite GSC sources."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from refresh_tsc import refresh_tsc
from rscript_tsc import read_tsc


with TemporaryDirectory(prefix="refresh-tsc-test-") as directory:
    root = Path(directory)
    resources = [root / name for name in ("jp", "zh")]
    header = ";@gsc-byte-format legacy-28\n;@gsc-schema early\n"
    for resource in resources:
        (resource / "scr").mkdir(parents=True)
        for number in range(2):
            (resource / "scr" / ("%04d.gsc" % number)).write_bytes(b"unchanged GSC")
            (resource / "scr" / ("%04d.tsc" % number)).write_text("old TSC")
    def converter(args, **kwargs):
        output = Path(args[args.index("-o") + 1])
        for source in args[args.index("-o") + 2:]:
            text = header + '*end\n'
            if broken and Path(source).parent.parent.name == "zh":
                text = ";@gsc-raw-v1 invalid\n"
            (output / Path(source).with_suffix(".tsc").name).write_text(text)
        return subprocess.CompletedProcess(args, 0, "", "")
    broken = True
    with patch("refresh_tsc.subprocess.run", side_effect=converter):
        for force, message in ((False, "already exists"), (True, "regenerate")):
            try:
                refresh_tsc(resources, Path("tool"), "cp932", "forest", force)
            except ValueError as error:
                assert message in str(error), error
            else:
                raise AssertionError("unsafe refresh accepted")
        assert all(p.read_text() == "old TSC" for resource in resources for p in (resource / "scr").glob("*.tsc"))
        broken = False
        assert refresh_tsc(resources, Path("tool"), "cp932", "forest", True) == (4, 4)
        assert refresh_tsc(resources, Path("tool"), "cp932", "forest", True) == (4, 0)
    assert all(p.read_bytes() == b"unchanged GSC" for resource in resources for p in (resource / "scr").glob("*.gsc"))
    assert not list(root.rglob(".tsc-*"))
    if len(sys.argv) > 1:
        tool = str(Path(sys.argv[1]).resolve())
        real = root / "real"
        (real / "scr").mkdir(parents=True)
        source = root / "fixture.tsc"
        source.write_text(header + '*TXT 0 0 0 0 "" "中文日本語" 1\n*end\n', encoding="utf-8")
        gsc = real / "scr/0000.gsc"
        subprocess.run([tool, "-e", "gbk", str(source), "-o", str(gsc)], check=True, capture_output=True)
        before = gsc.read_bytes()
        (real / "scr/0000.tsc").write_text("old TSC")
        assert refresh_tsc([real], Path(tool), "gbk", "forest", True) == (1, 1)
        rebuilt = real / "scr/0000.tsc"
        assert "中文日本語" in read_tsc(rebuilt).strings
        assert ";@gsc-text-encoding" not in rebuilt.read_text(encoding="utf-8")
        assert gsc.read_bytes() == before
        assert rebuilt.stat().st_mtime_ns == gsc.stat().st_mtime_ns
print("OK: staged GSC refresh, failure isolation, explicit overwrite, UTF-8 output and source preservation")
