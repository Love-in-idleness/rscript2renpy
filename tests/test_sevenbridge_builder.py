#!/usr/bin/env python3
"""SevenBridge generation, repeat builds and input preservation."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sevenbridge"))
from build_sevenbridge_rscript import build_sevenbridge


def main():
    with TemporaryDirectory(prefix="sevenbridge-builder-") as temporary:
        root = Path(temporary)
        source, project = root / "source", root / "project"
        for name in ("scr", "grpe", "grpo", "grpo_bu", "grpo_ex", "grps", "bgm", "voice", "wav"):
            (source / name).mkdir(parents=True)
        shutil.copyfile(ROOT / "runtime/gui/rscript_cursor.png", source / "grpe/3001.png")
        (source / "bgm/Track01.wav").write_bytes(b"unplayed PCM fixture")
        (source / "mov").mkdir()
        movie = source / "mov/0003.mpg"
        movie.write_bytes(b"unplayed movie fixture")
        script = source / "scr/0000.tsc"
        script.write_text(';@gsc-byte-format modern-36\n;@gsc-schema rscript18\n'
                          '*locmode 0 0 0\n*se 1\n*movie 3\n*getflag 1 1\n*getflag 1 0\n*end\n')
        before = script.read_bytes()
        scenes = build_sevenbridge(source, project)
        assert len(scenes) == 1 and "_getflag 1 1" in scenes["scr/0000.rpy"]
        assert "_se 0 1" in scenes["scr/0000.rpy"]
        assert "_movie 3" in scenes["scr/0000.rpy"]
        assert (project / "game/mov/0003.mpg").read_bytes() == movie.read_bytes()
        assert (project / "game/engine/options.rpy").read_bytes() == (ROOT / "sevenbridge/game/options.rpy").read_bytes()
        assert (project / "game/engine/gallery.rpy").read_bytes() == (ROOT / "sevenbridge/game/gallery.rpy").read_bytes()
        assert (project / "game/grpe/3001.png").is_file()
        assert not (project / "game/scr/0000.tsc").exists()
        assert not (project / "game/engine/__pycache__").exists()
        cache = project / "game/scr/0000.rpyc"
        cache.write_bytes(b"stale script cache")
        build_sevenbridge(source, project)
        assert not cache.exists() and script.read_bytes() == before
        assert movie.read_bytes() == b"unplayed movie fixture"
        assert (project / "game/mov/0003.mpg").read_bytes() == movie.read_bytes()
        try:
            build_sevenbridge(source, source / "output")
        except ValueError as error:
            assert "overlap" in str(error)
        else:
            raise AssertionError("overlapping input/output accepted")
        script.write_text('obsolete source\n')
        try:
            build_sevenbridge(source, root / "invalid-project")
        except ValueError:
            pass
        else:
            raise AssertionError("invalid script accepted")
        assert not (root / "invalid-project").exists()
    print("OK: SevenBridge builder preserves inputs and validates before installation")


if __name__ == "__main__":
    main()
