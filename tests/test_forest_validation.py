#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forest"))
import build_forest_rscript as forest_builder  # noqa: E402

validate_inputs = forest_builder.validate_inputs


def main() -> None:
    with TemporaryDirectory() as temporary:
        base = Path(temporary)
        resources = base / "resources"
        for name in ("scr", "grpe", "grpo", "grpo_bg", "grpo_bu",
                     "grpo_ci", "grpo_f", "grps", "wav", "bgm",
                     "voice", "mov"):
            (resources / name).mkdir(parents=True)
        tsc = (
            ";@gsc-byte-format legacy-28\n"
            ";@gsc-text-encoding CP932\n"
            ";@gsc-schema early\n"
            "*end\n")
        (resources / "scr" / "0000.tsc").write_text(tsc, encoding="utf-8")
        (resources / "Forest.exe").write_bytes(b"fixture")
        patch_dir = base / "english-patch"
        patch_dir.mkdir()
        for path in (resources / "grpe" / "9001.png",
                     resources / "bgm" / "Track01.ogg",
                     resources / "wav" / "0001.ogg",
                     resources / "voice" / "0001.ogg",
                     resources / "mov" / "0001.webm",
                     resources / "mov" / "0002.mpg"):
            path.write_bytes(b"fixture")
        validate_inputs(resources)
        project = base / "project"
        with patch.object(forest_builder, "copy_assets"), \
                patch.object(forest_builder, "convert_masks"), \
                patch.object(forest_builder, "convert_movies"), \
                patch.object(forest_builder, "extract_cursor"):
            forest_builder.main(["build_forest_rscript.py",
                                 str(resources), str(project),
                                 "--language", "english=" + str(patch_dir)])
        gui = project / "game" / "gui.rpy"
        gui_text = gui.read_text(encoding="utf-8")
        assert "gui.init(800, 600)" in gui_text
        assert '"fonts/NotoSansCJKjp-Regular.otf"' in gui_text
        assert "gui.scale(" not in gui_text
        compat_text = (project / "game" / "forest_compat.rpy").read_text(
            encoding="utf-8")
        assert "define forest_languages = [(None, '原文'), ('english', 'english')]" in compat_text
        assert "screen forest_title_preferences():" in compat_text
        assert "default persistent.forest_text_size = 22" in compat_text
        assert "default persistent.forest_line_chars = 19" in compat_text
        assert ('default persistent.forest_text_font = '
                '"fonts/NotoSansCJKjp-Regular.otf"' in compat_text)
        assert 'textbutton "上一字体"' in compat_text
        assert 'textbutton "下一字体"' in compat_text
        assert "default persistent.forest_progress_backup = None" in compat_text
        assert (project / "game" / "tl" / "english" /
                "forest_strings.rpy").read_text(encoding="utf-8") == \
            "translate english python:\n    pass\n"
        text_runtime = (project / "game" / "05_rscript_text.rpy").read_text(
            encoding="utf-8")
        util_runtime = (project / "game" / "01_util.rpy").read_text(
            encoding="utf-8")
        assert "renpy.translation.translate_string(eval(text).rstrip())" in util_runtime
        say_start = text_runtime.index("    def execute_say(o):")
        append_start = text_runtime.index("    def execute_append(o):")
        say_runtime = text_runtime[say_start:append_start]
        append_runtime = text_runtime[append_start:]
        assert say_runtime.index("store.forest_speaker_visible = True") < \
            say_runtime.index("renpy.say(") < \
            say_runtime.index("store.forest_speaker_visible = False")
        assert append_runtime.index("store.forest_speaker_visible = True") < \
            append_runtime.index("renpy.say(") < \
            append_runtime.index("store.forest_speaker_visible = False")
        (resources / "scr" / "0000.tsc").unlink()
        (resources / "scr" / "0000.gsc").write_bytes(b"not accepted")
        try:
            validate_inputs(resources)
        except FileNotFoundError as error:
            assert "scr/*.tsc" in str(error)
        else:
            raise AssertionError("GSC-only input was accepted")
        (resources / "scr" / "0000.gsc").unlink()
        (resources / "scr" / "0000.tsc").write_text(tsc, encoding="utf-8")
        (resources / "voice" / "0001.ogg").unlink()
        try:
            validate_inputs(resources)
        except FileNotFoundError as error:
            assert "voice/*.ogg" in str(error)
        else:
            raise AssertionError("missing converted voice was accepted")
        old_tsc = (
            ";@gsc-structure-v1 size=0 fnv1a64=0\n"
            ";@gsc-byte-format legacy-28\n"
            ";@gsc-text-encoding CP932\n"
            ";@gsc-structure-end\n")
        (resources / "scr" / "0000.tsc").write_text(old_tsc, encoding="utf-8")
        try:
            forest_builder.read_tsc(resources / "scr" / "0000.tsc")
        except ValueError as error:
            assert "obsolete TSC format" in str(error)
        else:
            raise AssertionError("obsolete structured TSC was accepted")
        current_tsc = (
            ";@gsc-byte-format legacy-28\n"
            ";@gsc-text-encoding CP932\n"
            ";@gsc-schema early\n"
            "*TXT 0 0 0 0 \"\" \"^g999Edited text\" 1\n"
            "*end\n")
        (resources / "scr" / "0000.tsc").write_text(
            current_tsc, encoding="utf-8")
        assert "    _say '^g999Edited text'" in forest_builder.compile_scene(
            resources / "scr" / "0000.tsc")
    print("OK: Forest input validation")


if __name__ == "__main__":
    main()
