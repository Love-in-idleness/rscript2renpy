#!/usr/bin/env python3

from pathlib import Path
import json
from tempfile import TemporaryDirectory
from textwrap import dedent
from types import SimpleNamespace
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forest"))
import build_forest_rscript as forest_builder  # noqa: E402
from rscript_tsc import read_tsc  # noqa: E402

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
        patch_dir = base / "english-patch"
        patch_dir.mkdir()
        keywords_text = (
            '[\n'
            '  // URLs may contain comment-like slashes.\n'
            '  ["A keyword.", "https://example.test/a//b", "keyword"]\n'
            ']\n')
        (patch_dir / "keywords.json").write_text(
            keywords_text, encoding="utf-8")
        for path in (resources / "grpe" / "9001.png",
                     resources / "bgm" / "Track01.ogg",
                     resources / "wav" / "0001.ogg",
                     resources / "voice" / "0001.ogg",
                     resources / "mov" / "0001.mpg",
                     resources / "mov" / "0002.mpg"):
            path.write_bytes(b"fixture")
        validate_inputs(resources)
        project = base / "project"
        forest_builder.main(["build_forest_rscript.py",
                             str(resources), str(project),
                             "--language", "english=" + str(patch_dir)])
        assert (project / "game" / "engine" / "gui" / "rscript_cursor.png").read_bytes() == \
            (ROOT / "runtime" / "gui" / "rscript_cursor.png").read_bytes()
        assert '"mov/%04d.mpg"' in (
            project / "game" / "engine" / "03_rscript_gfx.rpy").read_text(encoding="utf-8")
        gfx_text = (project / "game" / "engine" / "03_rscript_gfx.rpy").read_text(
            encoding="utf-8")
        assert 'RScriptText(text_value, kind = "oload"' in gfx_text
        assert (project / "game" / "engine" / "rscript_wrap.py").is_file()
        assert (project / "game" / "engine" / "00_rscript_wrap.rpy").is_file()
        assert (project / "game" / "engine" / "touch_controls.rpy").read_bytes() == \
            (ROOT / "port_template" / "game" / "touch_controls.rpy").read_bytes()
        assert ("xmaximum = font_size * persistent.rscript_oload_line_chars"
                not in gfx_text)
        for name in ("android-icon_background.png",
                     "android-icon_foreground.png"):
            assert (project / name).read_bytes() == \
                (ROOT / "forest" / "android" / name).read_bytes()
        android = json.loads((project / "android.json").read_text(encoding="utf-8"))
        assert android["version"] == "1.3" and android["numeric_version"] == 13
        assert 'define config.version = "1.3"' in (project / "game/engine/port_version.rpy").read_text()
        notice = (ROOT / "port_template" / "android" / "notice.png").read_bytes()
        for name in ("android-presplash.png", "android-downloading.png"):
            assert (project / name).read_bytes() == notice
        assert not (project / "android.keystore").exists()
        assert not (project / "bundle.keystore").exists()
        gui = project / "game" / "engine" / "gui.rpy"
        gui_text = gui.read_text(encoding="utf-8")
        assert "gui.init(*rscript_screen_size)" in gui_text
        assert 'define gui.text_font = "fonts/NotoSansCJKjp-Regular.otf"' in gui_text
        for name in ("simhei.ttf", "SimHei-NOTICE.md"):
            assert (project / "game" / "fonts" / name).read_bytes() == \
                (ROOT / "port_template" / "fonts" / name).read_bytes()
        assert "gui.scale(" not in gui_text
        compat_text = (project / "game" / "engine" / "forest_compat.rpy").read_text(
            encoding="utf-8")
        compat_text += (project / "game" / "engine" / "text_features.rpy").read_text(encoding="utf-8")
        compat_text += (project / "game" / "engine" / "language_config.rpy").read_text(encoding="utf-8")
        compat_text += (project / "game" / "engine" / "00_rscript_wrap.rpy").read_text(encoding="utf-8")
        compat_text += (project / "game" / "engine" / "ui_features.rpy").read_text(encoding="utf-8")
        compat_text += (project / "game" / "engine" / "grps_ui.rpy").read_text(encoding="utf-8")
        assert "    rscript_languages = [(None, 'Original'), ('english', 'english')]" in compat_text
        assert "screen forest_title_preferences():" in compat_text
        assert "default persistent.rscript_text_size = rscript_base_text_size" in compat_text
        assert "default persistent.rscript_say_line_chars = 19" in compat_text
        assert "default persistent.rscript_oload_line_chars = 20" in compat_text
        assert "default persistent.rscript_line_spacing = 7" in compat_text
        assert "default persistent.rscript_wiki_mode = False" in compat_text
        assert "'https://example.test/a//b'" in compat_text
        assert 'if _preferences.language in rscript_wiki_keywords:' in compat_text
        assert 'Function(rscript_set_wiki, True)' in compat_text
        assert 'Function(rscript_set_wiki, False)' in compat_text
        assert 'text "Wiki Mode" yalign 0.5' not in compat_text
        assert "line_spacing persistent.rscript_line_spacing" in compat_text
        assert 'define rscript_default_font = "fonts/NotoSansCJKjp-Regular.otf"' in compat_text
        assert 'default persistent.rscript_text_font = rscript_default_font' in compat_text
        start = compat_text.index("    def rscript_update_default_font():")
        end = compat_text.index("    config.start_callbacks.append", start)
        previous_font = "fonts/simhei.ttf"
        settings = SimpleNamespace(rscript_text_font=previous_font,
                                   rscript_previous_default_font=previous_font)
        saved = []
        namespace = dict(persistent=settings, rscript_default_font="fonts/NotoSansCJKjp-Regular.otf",
                         renpy=SimpleNamespace(save_persistent=lambda: saved.append(True)))
        exec(dedent(compat_text[start:end]), namespace)
        update_font = namespace["rscript_update_default_font"]
        update_font()
        assert settings.rscript_text_font == "fonts/NotoSansCJKjp-Regular.otf" and len(saved) == 1
        settings.rscript_text_font = previous_font
        update_font()
        assert settings.rscript_text_font == previous_font and len(saved) == 1
        settings.rscript_text_font = "fonts/NotoSerifCJK-Regular.ttc"
        settings.rscript_previous_default_font = previous_font
        update_font()
        assert settings.rscript_text_font == "fonts/NotoSerifCJK-Regular.ttc"
        assert 'textbutton "Previous Font"' in compat_text
        assert 'textbutton "Next Font"' in compat_text
        for old_text in ("原文", "持久化", "戻る", "スキップ", "オート",
                         "メニュー", "文本", "字号", "字体", "语言",
                         "返回", "はい", "いいえ"):
            assert old_text not in compat_text
        assert "default persistent.rscript_progress_backup = None" in compat_text
        assert (project / "game" / "tl" / "english" /
                "rscript_strings.rpy").read_text(encoding="utf-8") == \
            "translate english python:\n    pass\n"
        assert (project / "game" / "tl" / "english" /
                "keywords.json").read_text(encoding="utf-8") == keywords_text
        text_runtime = (project / "game" / "engine" / "05_rscript_text.rpy").read_text(
            encoding="utf-8")
        command_runtime = (project / "game" / "engine" / "02_rscript_cmd.rpy").read_text(
            encoding="utf-8")
        util_runtime = (project / "game" / "engine" / "01_util.rpy").read_text(
            encoding="utf-8")
        assert "renpy.pause(delay / 10.)" in command_runtime
        assert "text = eval(text)" in util_runtime
        assert "text = rscript_prepare_text(text)" in util_runtime
        assert "text = rscript_prepare_wiki_text(text)" in compat_text
        assert '"g": rscript_green_color()' in util_runtime
        say_start = text_runtime.index("    def execute_say(o, interact=True):")
        append_start = text_runtime.index("    def execute_append(o, interact=True):")
        say_runtime = text_runtime[say_start:append_start]
        append_runtime = text_runtime[append_start:]
        assert "parse_rscript_text(what, True)" in say_runtime
        assert "parse_rscript_text(what, True)" in append_runtime
        assert "renpy.say(who, what, interact = interact" in say_runtime
        assert "renpy.say(who, what, interact = interact" in append_runtime
        assert '        if center:\n            rscript_text what:\n' \
            '                id "what"' in compat_text
        assert '        else:\n            rscript_text what:\n' \
            '                id "what"' in compat_text
        assert say_runtime.index("rscript_dialogue_begin") < \
            say_runtime.index("renpy.say(") < \
            say_runtime.index("rscript_dialogue_end")
        assert append_runtime.index("rscript_dialogue_begin") < \
            append_runtime.index("renpy.say(") < \
            append_runtime.index("rscript_dialogue_end")
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
            read_tsc(resources / "scr" / "0000.tsc")
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
        (resources / "voice/0001.ogg").write_bytes(b"fixture")
        generated = project / "game/engine/port_version.rpy"
        generated.write_text("untouched on invalid input\n", encoding="utf-8")
        (patch_dir / "scr").mkdir()
        patch_source = patch_dir / "scr/0000.tsc"
        patch_source.write_text(tsc.replace("*end", "*gosub 99\n*end"), encoding="utf-8")
        try:
            forest_builder.main(["build", str(resources), str(project),
                                 "--language", "english=" + str(patch_dir)])
        except ValueError:
            pass
        else:
            raise AssertionError("invalid patch accepted")
        assert generated.read_text() == "untouched on invalid input\n"
        patch_source.unlink()
        (patch_dir / "keywords.json").write_text("invalid JSON", encoding="utf-8")
        try:
            forest_builder.main(["build", str(resources), str(project),
                                 "--language", "english=" + str(patch_dir)])
        except ValueError:
            pass
        else:
            raise AssertionError("invalid keywords accepted")
        assert generated.read_text() == "untouched on invalid input\n"
        (patch_dir / "keywords.json").write_text(keywords_text, encoding="utf-8")
        panel = patch_dir / "grps/confscrn"
        panel.mkdir(parents=True)
        (panel / "bg.png").write_bytes(b"missing metadata fixture")
        try:
            forest_builder.main(["build", str(resources), str(project),
                                 "--language", "english=" + str(patch_dir)])
        except ValueError as error:
            assert ".meta.xml" in str(error)
        else:
            raise AssertionError("invalid patch metadata accepted")
        assert generated.read_text() == "untouched on invalid input\n"
        assert (project / "game/tl/english/keywords.json").read_text() == keywords_text
    print("OK: Forest input validation")


if __name__ == "__main__":
    main()
