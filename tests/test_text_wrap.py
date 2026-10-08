#!/usr/bin/env python3
"""Algorithm checks with supplied advances; SDK shaping is tested separately."""
from pathlib import Path
from types import SimpleNamespace
from itertools import product
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from rscript_wrap import NO_LINE_START, NO_LINE_END, glyph_breaks, normalize_boundaries


def wrap(text, limit, advances=None):
    glyphs = [SimpleNamespace(character=ord(c), advance=w)
              for c, w in zip(text, advances or [1] * len(text))]
    starts = [0] + glyph_breaks(glyphs, limit) + [len(text)]
    return [text[a:b] for a, b in zip(starts, starts[1:])]


def main():
    assert wrap("甲乙", 2) == ["甲乙"]
    assert wrap("甲乙丙", 2) == ["甲乙", "丙"]
    assert wrap("甲乙。！", 2) == ["甲乙。", "！"]
    assert wrap("甲（乙", 2) == ["甲", "（乙"]
    assert wrap("甲（", 2) == ["甲（"]
    assert wrap("甲（。", 2) == ["甲（。"]  # hanging takes priority
    assert "“" in NO_LINE_START and "“" in NO_LINE_END
    assert wrap("甲乙“", 2) == ["甲乙“"]
    assert wrap("甲“乙", 2) == ["甲", "“乙"]
    assert wrap("甲乙“丙", 2) == ["甲乙", "“丙"]
    for char in "\u3000\u00a0っゃァ»—-%™®":
        assert wrap("甲乙" + char + "丙", 2) == ["甲乙" + char, "丙"]
    assert wrap("Ж«Ю", 2) == ["Ж", "«Ю"]
    assert wrap("甲Я。A", 2) == ["甲Я。", "A"]
    assert wrap("Wi甲", 10, [8, 2, 10]) == ["Wi", "甲"]
    assert wrap("甲乙丙", 20, [10, 20, 10]) == ["甲乙", "丙"]
    assert wrap("甲\ufffc乙", 20, [10, 15, 10]) == ["甲\ufffc", "乙"]
    assert wrap("甲乙。", 2, [1.5, 1, 1]) == ["甲乙", "。"]
    assert wrap("甲（乙", 2, [1.5, 1, 1]) == ["甲", "（乙"]
    assert wrap("甲（", 2, [1.5, 1]) == ["甲（"]
    assert wrap("甲（。", 2, [1.5, 1, 1]) == ["甲", "（。"]
    assert wrap("甲\u200b乙", 1, [10, 0, 1]) == ["甲\u200b", "乙"]
    assert wrap("（乙", 1, [10, 1]) == ["（", "乙"]
    assert wrap("", 0) == [""]
    ruby = [SimpleNamespace(character=ord(c), advance=w, ruby=r)
            for c, w, r in (("甲", 1, 0), ("漢", 1, 1), ("字", 1, 1),
                            ("か", 0.5, 2), ("ん", 0.5, 2), ("じ", 0.5, 2), ("乙", 1, 0))]
    assert glyph_breaks(ruby, 3) == [6]  # Reading adds no inline width.
    assert glyph_breaks(ruby, 2) == [6]  # Starts inside edge: whole base hangs.
    assert glyph_breaks(ruby, 1) == [1, 6]  # Never split/orphan the annotation.
    # Exhaustively check forward progress and preservation, including zero width.
    for length in range(1, 6):
        for chars in product("甲（。“\u200b", repeat=length):
            text = "".join(chars)
            advances = [0 if c == "\u200b" else 1 for c in chars]
            for limit in (0, 1, 2):
                lines = wrap(text, limit, advances)
                assert "".join(lines) == text and all(lines)
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
