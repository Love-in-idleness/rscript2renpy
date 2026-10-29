#!/usr/bin/env python3
"""Algorithm checks with supplied advances; SDK shaping is tested separately."""
from pathlib import Path
from types import SimpleNamespace
from itertools import product
import sys
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from rscript_wrap import parse_kinsoku, glyph_breaks, normalize_boundaries, place_native_ruby, ruby_markup, sync_ruby_times

RULES = parse_kinsoku((Path(__file__).resolve().parents[1] / "runtime/kinsoku.json").read_text(encoding="utf-8"))


def wrap(text, limit, advances=None):
    glyphs = [SimpleNamespace(character=ord(c), advance=w)
              for c, w in zip(text, advances or [1] * len(text))]
    starts = [0] + glyph_breaks(glyphs, limit, RULES) + [len(text)]
    return [text[a:b] for a, b in zip(starts, starts[1:])]


def main():
    assert not RULES[0] & RULES[1]
    assert all(char in RULES[0] for char in "ッヵヶㇰ・‥゛")
    assert all(char in RULES[1] for char in "“£¥‹￥")
    assert not any(char in RULES[0] for char in "—-™®〃“")
    empty = {"version": 1, "no_line_start": "", "no_line_end": ""}
    assert parse_kinsoku(json.dumps(empty)) == (frozenset(), frozenset())
    custom = parse_kinsoku(json.dumps({**empty, "no_line_start": "X"}))
    custom_glyphs = [SimpleNamespace(character=ord(c), advance=1) for c in "甲乙X丙"]
    assert glyph_breaks(custom_glyphs, 2, custom) == [3]
    assert glyph_breaks(custom_glyphs, 2, RULES) == [2]
    for invalid in ("", "[]", "{}", json.dumps({**empty, "extra": 1}),
                    json.dumps({**empty, "version": True}),
                    json.dumps({**empty, "version": 1.0}),
                    json.dumps({**empty, "version": 2}),
                    json.dumps({**empty, "no_line_start": []}),
                    json.dumps({**empty, "no_line_start": "x", "no_line_end": "x"}),
                    '{"version":1,"version":1,"no_line_start":"","no_line_end":""}',
                    *(json.dumps({**empty, "no_line_start": char})
                      for char in ("\0", "\ud800", "\udfff", "😀"))):
        try:
            parse_kinsoku(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid kinsoku accepted: %s" % invalid)
    assert ruby_markup('|寂寞[じゃくまく]') == '{rb}寂寞{/rb}{rt}じゃくまく{/rt}'
    assert ruby_markup('この躯[み]を介[お]いて') == 'この{rb}躯{/rb}{rt}み{/rt}を{rb}介{/rb}{rt}お{/rt}いて'
    assert ruby_markup('|漢字[かんじ]字[じ]') == '{rb}漢字{/rb}{rt}かんじ{/rt}{rb}字{/rb}{rt}じ{/rt}'
    assert ruby_markup('{color=#fff}躯[み]{/color}') == '{color=#fff}{rb}躯{/rb}{rt}み{/rt}{/color}'
    assert ruby_markup('[literal] |unfinished[') == '[literal] |unfinished['
    assert wrap("甲乙", 2) == ["甲乙"]
    assert wrap("甲乙丙", 2) == ["甲乙", "丙"]
    assert wrap("甲乙。！", 2) == ["甲乙。！"]
    assert wrap("甲乙。！丙丁", 2) == ["甲乙。！", "丙丁"]
    assert wrap("甲（「乙丙", 3) == ["甲", "（「乙", "丙"]
    assert wrap("（「乙丙", 1) == ["（「乙", "丙"]
    assert wrap("甲（乙", 2) == ["甲", "（乙"]
    assert wrap("甲（", 2) == ["甲（"]
    assert wrap("甲（。", 2) == ["甲（。"]  # hanging takes priority
    assert wrap("甲乙“", 2) == ["甲乙", "“"]
    assert wrap("甲“乙", 2) == ["甲", "“乙"]
    assert wrap("甲乙“丙", 2) == ["甲乙", "“丙"]
    for char in "\u3000っゃァ»%ッヵヶㇰ・‥゛":
        assert wrap("甲乙" + char + "丙", 2) == ["甲乙" + char, "丙"]
    for char in "：；％々〗℃′″":
        assert wrap("甲乙" + char + "丙", 2) == ["甲乙" + char, "丙"]
    for char in "\u00a0—-™®·〃":
        assert wrap("甲乙" + char + "丙", 2) == ["甲乙", char + "丙"]
    assert wrap("甲〖乙", 2) == ["甲", "〖乙"]
    assert wrap("Ж«Ю", 2) == ["Ж", "«Ю"]
    assert wrap("甲Я。A", 2) == ["甲Я。", "A"]
    assert wrap("Wi甲", 10, [8, 2, 10]) == ["Wi", "甲"]
    assert wrap("甲乙丙", 20, [10, 20, 10]) == ["甲乙", "丙"]
    assert wrap("甲\ufffc乙", 20, [10, 15, 10]) == ["甲\ufffc", "乙"]
    assert wrap("甲乙。", 2, [1.5, 1, 1]) == ["甲乙。"]
    assert wrap("甲（乙", 2, [1.5, 1, 1]) == ["甲", "（乙"]
    assert wrap("甲（", 2, [1.5, 1]) == ["甲（"]
    assert wrap("甲（。", 2, [1.5, 1, 1]) == ["甲（。"]
    assert wrap("甲\u200b乙", 1, [10, 0, 1]) == ["甲\u200b", "乙"]
    assert wrap("（乙", 1, [10, 1]) == ["（乙"]
    assert wrap("", 0) == [""]
    ruby = [SimpleNamespace(character=ord(c), advance=w, ruby=r)
            for c, w, r in (("甲", 1, 0), ("漢", 1, 1), ("字", 1, 1),
                            ("か", 0.5, 2), ("ん", 0.5, 2), ("じ", 0.5, 2), ("乙", 1, 0))]
    assert glyph_breaks(ruby, 3, RULES) == [6]  # Reading adds no inline width.
    assert glyph_breaks(ruby, 2, RULES) == [6]  # Starts inside edge: whole base hangs.
    assert glyph_breaks(ruby, 1, RULES) == [1, 6]  # Never split/orphan the annotation.
    assert glyph_breaks(ruby, 1, RULES, ruby_atomic=False) == [1, 2, 6]
    def glyph(ruby, x, y, width, ascent=10):
        return SimpleNamespace(ruby=ruby, x=x, y=y, advance=width, ascent=ascent)
    base = [glyph(1, 0, 10, 10), glyph(1, 10, 10, 10)]
    short = [glyph(2, 0, 0, 2, 4), glyph(2, 0, 0, 2, 4)]
    place_native_ruby(base + short, 9)
    assert [(g.x, g.y) for g in short] == [(4, -5), (14, -5)]
    long = [glyph(2, 0, 0, 8, 4) for _ in range(3)]
    place_native_ruby(base + long, 9)
    assert [g.x for g in long] == [-2, 6, 14]
    # Ceil allocation is recursive: 2/5 to row one, then 2/3 to row two.
    base = [glyph(1, 0, 10, 10), glyph(1, 10, 10, 10),
            glyph(1, 0, 30, 10), glyph(1, 10, 30, 10), glyph(1, 0, 50, 10)]
    reading = [glyph(2, 0, 0, 2, 4) for _ in range(4)]
    place_native_ruby(base + reading, 9)
    assert [g.y for g in reading] == [-5, -5, 15, 15]
    assert [g.y for g in base] == [10, 10, 30, 30, 50]
    for index, g in enumerate(base):
        g.time = (index + 1) / 25
    sync_ruby_times(base + reading)
    assert [g.time for g in reading] == [g.time for g in base[:4]]
    base = [glyph(1, 0, 10, 10)]
    base[0].time = -3600  # Already displayed before {fast}.
    sync_ruby_times(base + reading)
    assert all(g.time == -3600 for g in reading)
    sync_ruby_times([])
    place_native_ruby([], 9)
    place_native_ruby([glyph(0, 0, 0, 0), glyph(2, 0, 0, 0)], 9)
    # Exhaustively check forward progress and preservation, including zero width.
    for length in range(1, 6):
        for chars in product("甲（。“\u200b", repeat=length):
            text = "".join(chars)
            advances = [0 if c == "\u200b" else 1 for c in chars]
            for limit in (0, 1, 2):
                lines = wrap(text, limit, advances)
                assert "".join(lines) == text and all(lines)
                assert all(left[-1] not in RULES[1] and right[0] not in RULES[0]
                           for left, right in zip(lines, lines[1:]))
    T, P, D, TAG = range(4)
    normalize = lambda tokens: normalize_boundaries(tokens, T, P, D)
    assert normalize([(P, ""), (P, ""), (T, "甲"), (P, "")]) == [(T, "甲")]
    tokens = [(T, "甲 "), (P, ""), (TAG, "color=#fff"),
              (P, ""), (TAG, "w=1"), (T, "\u3000乙 "), (P, "")]
    assert normalize(tokens) == [tokens[i] for i in (0, 1, 2, 4, 5)]
    assert normalize([(P, ""), (D, object()), (P, "")])[0][0] == D
    print("OK: shared kinsoku rules, boundaries and exhaustive progress checks")


if __name__ == "__main__":
    main()
