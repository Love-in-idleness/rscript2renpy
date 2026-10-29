#!/usr/bin/env python3
"""SevenBridge generation, repeat builds and input preservation."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import sys
from PIL import Image

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
                          '*locmode 0 0 0\n*se 1\n*movie 3\n*getflag 1 1\n*getflag 1 0\n'
                          '*load 28 1161 0 0 0 8\n*gload 5603 11\n*end\n')
        before = script.read_bytes()
        scenes = build_sevenbridge(source, project)
        assert len(scenes) == 1 and "_getflag 1 1" in scenes["scr/0000.rpy"]
        assert "_se 0 1" in scenes["scr/0000.rpy"]
        assert "_movie 3" in scenes["scr/0000.rpy"]
        output = (project / "game/scr/0000.rpy").read_text()
        assert "_load 28 1161 0 0 0 8" in output
        assert "_gload 5603 11" in output and "flattened" not in output
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

        patch, localized = root / "汉化 Русский patch", root / "localized"
        (patch / "scr").mkdir(parents=True)
        header = ';@gsc-byte-format modern-36\n;@gsc-schema rscript18\n'
        (source / "scr/0001.tsc").write_text(header + '*return 0\n', encoding="utf-8")
        (source / "scr/0210.tsc").write_text(header + '*wait 1\n*return 0\n', encoding="utf-8")
        translated = patch / "scr/0000.tsc"
        script.write_text(
            header + '*TXT 0 0 0 0 "^g001" "本文" 1\n'
            '*select 1 "質問" END END END END END "選択肢" "" "" "" "" 0 0 0\n'
            ':END\n*end\n', encoding="utf-8")
        translated.write_text(
            header + '*TXT 0 0 0 0 "^g001" "译文正文" 1\n'
            '*font 44 10 20 0 0 "新增字幕"\n'
            '*select 1 "中文问题" END END END END END "中文选项" "" "" "" "" 0 0 0\n'
            ':END\n*end\n', encoding="utf-8")
        (patch / "scr/0210.tsc").write_text(header + '*wait 1\n*return 0\n', encoding="utf-8")
        for directory, x in ((source, 10), (patch, 30)):
            panel = directory / "grps/confscrn"
            panel.mkdir(parents=True)
            Image.new("RGBA", (13, 9), "white" if directory == source else "black").save(panel / "close.png")
            (panel / ".meta.xml").write_text(
                '<Canvas><Width>800</Width><Height>600</Height><Items>'
                '<Item x="%d" y="40" flag="40">close</Item>'
                '</Items></Canvas>' % x, encoding="utf-8")
        inputs = {path: path.read_bytes() for directory in (source, patch)
                  for path in directory.rglob("*") if path.is_file()}
        languages = ["jp", "zh=" + str(patch)]
        variants = build_sevenbridge(source, localized, languages=languages)
        game = localized / "game"
        translated_output = variants["scr/0000.rpy"]
        assert "_rscript_variant" not in translated_output
        assert "{'zh': '译文正文'}.get(_preferences.language, '本文')" in translated_output
        assert "_rscript_say ('^g001'," in translated_output
        assert "_oload 44 10 20 0 0 '新增字幕'" in translated_output
        assert "{'zh': '中文问题'}.get(_preferences.language, '質問')" in translated_output
        assert "{'zh': '中文选项'}.get(_preferences.language, '選択肢')" in translated_output
        assert "_preferences.language" not in variants["scr/0001.rpy"]
        assert "label _0001:" in variants["scr/0001.rpy"]
        assert not (game / "tl/zh/scr/0001.rpy").exists()
        assert not (game / "tl/zh/scr").exists()
        assert "label _0210:\nlabel sevenbridge_cg_body:\n" in variants["scr/0210.rpy"]
        assert "_wait 1" in variants["scr/0210.rpy"]
        gallery = (game / "engine/gallery.rpy").read_text()
        assert "call sevenbridge_cg_body" in gallery and "call _rscript_variant0_0210" not in gallery
        config = (game / "engine/language_config.rpy").read_text()
        assert "[(None, 'jp'), ('zh', 'zh')]" in config
        for name in ("close.png", ".meta.xml"):
            assert (game / "tl/zh/grps/confscrn" / name).read_bytes() == (patch / "grps/confscrn" / name).read_bytes()
        layout = (game / "tl/zh/grps_layout.rpy").read_text()
        assert "'close': (30, 40, 13, 9)" in layout
        caches = [game / "scr/0000.rpyc"]
        for cache in caches:
            cache.write_bytes(b"stale localized cache")
        build_sevenbridge(source, localized, languages=languages)
        assert all(not cache.exists() for cache in caches)
        assert all(path.read_bytes() == contents for path, contents in inputs.items())
        extra = patch / "scr/0002.tsc"
        extra.write_text(header + '*return 0\n', encoding="utf-8")
        try:
            build_sevenbridge(source, root / "extra-scene", languages=languages)
        except FileNotFoundError as error:
            assert "no matching base scenario" in str(error)
        else:
            raise AssertionError("unaligned extra scenario accepted")
        assert not (root / "extra-scene").exists()
        extra.unlink()
        for output in (patch, patch / "output"):
            try:
                build_sevenbridge(source, output, languages=languages)
            except ValueError as error:
                assert "overlap" in str(error)
            else:
                raise AssertionError("patch/output overlap accepted")
        translated.write_text('obsolete translated source\n', encoding="utf-8")
        invalid_patch_project = root / "invalid-patch-project"
        try:
            build_sevenbridge(source, invalid_patch_project, languages=languages)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid patch script accepted")
        assert not invalid_patch_project.exists()
        script.write_text('obsolete source\n')
        try:
            build_sevenbridge(source, root / "invalid-project")
        except ValueError:
            pass
        else:
            raise AssertionError("invalid script accepted")
        assert not (root / "invalid-project").exists()
    print("OK: SevenBridge language scenes/assets, fallback, cache cleanup and input preservation")


if __name__ == "__main__":
    main()
