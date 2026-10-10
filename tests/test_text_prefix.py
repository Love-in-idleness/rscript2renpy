#!/usr/bin/env python3
"""Exercise the real shared parser with lightweight Ren'Py service stubs."""
import ast
from pathlib import Path
import re
from textwrap import dedent
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def load_functions(path, names, namespace):
    source = path.read_text(encoding="utf-8")
    pattern = r"(?m)^    def [^\n]+\n(?:(?: {8}[^\n]*|[ \t]*)\n)*"
    for match in re.finditer(pattern, source):
        if re.match(r"    def (\w+)", match.group()).group(1) not in names:
            continue
        tree = ast.parse(dedent(match.group()))
        functions = [node for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name in names]
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), "exec"), namespace)


def main():
    store = SimpleNamespace(rscript_speaker=None)
    namespace = dict(
        renpy=SimpleNamespace(re=re, translation=SimpleNamespace(translate_string=lambda s: s),
                              loadable=lambda path: True),
        store=store, persistent=SimpleNamespace(rscript_text_size=22),
        gui=SimpleNamespace(text_font="test.ttf"),
        rscript_use_speaker_images=True, rscript_speaker_images_override=False,
        rscript_prepare_wiki_text=lambda s: s,
        rscript_green_color=lambda: "#FFFFFF")
    load_functions(ROOT / "port_template/game/text_features.rpy",
                   {"rscript_prepare_text", "rscript_inline_graphics", "rscript_menu_text",
                    "rscript_wiki_plain", "rscript_g_tag"}, namespace)
    load_functions(ROOT / "runtime/01_util.rpy",
                   {"parse_rscript_text", "rscript_style_controls", "rscript_text_palette"}, namespace)
    prepare = namespace["rscript_prepare_text"]
    parse = namespace["parse_rscript_text"]
    for prefix in ("", "^cy", "^m^cy", "^cy^m", "^b^i^fm^s2^d3^w10^n", "^CY^M"):
        store.rscript_speaker = None
        assert prepare(prefix + "^g999正文^g001") == prefix + "正文{rscript_g=001:22}"
        assert store.rscript_speaker == 999
    parsed, center = parse(repr('^cy^g999“翻转”是紧急回避突发事态时用的技能。'), True)
    assert parsed == '{color=#FFDE00}“翻转”是紧急回避突发事态时用的技能。{/color}'
    assert not center and store.rscript_speaker == 999
    parsed, center = parse(repr("^cy^m^g999正文"), True)
    assert center and "rscript_g=" not in parsed
    for prefix in ("正文", " ", "\u3000", "\u00a0", "^v1", "^a001", "|正文[注音]", "^q"):
        store.rscript_speaker = None
        assert "{rscript_g=999:22}" in prepare(prefix + "^g999正文")
        assert store.rscript_speaker is None
    namespace["rscript_use_speaker_images"] = False
    assert prepare("^cy^g999正文") == "^cy{rscript_g=999:22}正文"
    namespace["rscript_speaker_images_override"] = True
    assert prepare("^cy^g999正文") == "^cy正文"
    namespace["rscript_use_speaker_images"] = True
    namespace["rscript_speaker_images_override"] = False
    observed = []

    def wiki(text):
        observed.append(text)
        return text.replace("^cg", "^cg{a=https://example.invalid}{color=#D7FFB3}") + "{/color}{/a}"

    namespace["rscript_prepare_wiki_text"] = wiki
    result = prepare("^cg^g001正文^g002^cw")
    assert observed == ["^cg正文^g002^cw"]
    assert "rscript_g=001" not in result and "rscript_g=002" in result
    namespace["rscript_prepare_wiki_text"] = lambda s: s
    namespace["renpy"].substitute = lambda s: s
    store.rscript_speaker = None
    result = namespace["rscript_menu_text"]("^cy^g999选项")
    assert "rscript_g=999" in result and store.rscript_speaker is None
    for spelling in ("39", "039", "0039", "00039", " \t0039", "65575", "-65497"):
        store.rscript_speaker = None
        assert prepare("^G" + spelling + "正文") == "正文"
        assert store.rscript_speaker == 39
        parsed, _ = parse(repr("正文^G" + spelling + "尾"), True)
        assert parsed == "正文{rscript_g=039:22}尾"
        store.rscript_speaker = None
        assert namespace["rscript_menu_text"]("^g" + spelling + "选项") == "{rscript_g=039:22}选项"
        assert store.rscript_speaker is None
        assert namespace["rscript_wiki_plain"]("前^G" + spelling + "后") == "前后"
    for spelling, number in (("63", 63), ("0", 0), ("1000", 1000), ("003912", 3912)):
        assert prepare("^g" + spelling + "正文") == "正文"
        assert store.rscript_speaker == number
        assert namespace["rscript_inline_graphics"]("^g" + spelling + "尾") == "{rscript_g=%03d:22}尾" % number
    parsed, _ = parse(repr("^g39^cw150"), True)
    assert store.rscript_speaker == 39 and "150" in parsed
    namespace.update(rscript_inline_base_size=22, rscript_ui={},
                     rscript_text_image_path=lambda name: "grps/" + name + ".png",
                     Transform=lambda path, **kwargs: (path, kwargs))
    namespace["renpy"].TEXT_DISPLAYABLE = "displayable"
    tag = namespace["rscript_g_tag"]
    assert tag("rscript_g", "0039:22") == [("displayable", ("grps/gf039.png", {"zoom": 1.0}))]
    assert tag("rscript_g", "bad:22") == []
    print("shared leading-control/nameplate parser: PASS")


if __name__ == "__main__":
    main()
