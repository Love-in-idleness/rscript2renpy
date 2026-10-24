# Developer reference: text layout

[中文](TEXT_WRAPPING.zh.md) | [English](TEXT_WRAPPING.en.md) | [Русский](TEXT_WRAPPING.ru.md) | [日本語](TEXT_WRAPPING.ja.md)

[Documentation](README.en.md)

Common layout rules and maintenance points. Players change fonts, sizes and line lengths in settings.

## Rules

- Line width is base-font full-width advance × configured count; actual text uses shaped glyph advances.
- Allow one hanging glyph so punctuation need not occupy a line alone; opening brackets cannot end a line.
- ^n forces a break; repeated breaks merge. Colour/link controls consume no width.
- Nameplates have separate layout; inline images occupy final rendered dimensions.
- Appended text relayouts with the existing body; settings changes also refresh text objects.

Forest defaults: dialogue 19 widths, objects 20. Kagerou uses its physical rectangle: horizontal wraps by width,
vertical by height; no arbitrary character count conflicting with presets.

## Ruby and vertical layout

`|正文[注音]` marks a span; `字[注音]` annotates only the adjacent character.
Use full-width ［］ for literal brackets. Ruby reveals with its base characters and consumes no independent reading time.
Verified Evermaiden/Kagerou use native positioning; Kagerou vertical ruby is right of the base.
Changing direction preserves size. Vertical dashes rotate by glyph units, not ordinary horizontal rules.
See [Kagerou evidence](../kagerou/NATIVE_EVIDENCE.en.md).

## Boundary examples

For two equal-width characters, ↵ means line break:

| Input | Result |
| --- | --- |
| 甲乙 | 甲乙 |
| 甲乙丙 | 甲乙↵丙 |
| 甲乙。！ | 甲乙。↵！ |
| 甲（乙 | 甲↵（乙 |
| 甲（ | 甲（ |
| 甲（。 | 甲（。 |

Proportional fonts may break differently. Large sizes or small spacing need clipping/ruby-overlap checks.

## Maintenance

| File | Role |
| --- | --- |
| runtime/rscript_wrap.py | Prohibited-break and wrapping rules |
| runtime/00_rscript_wrap.rpy | Ren'Py glyph measurement and layout |
| port_template/game/text_features.rpy | Player text settings |
| Game overrides | Defaults, text rectangle and dialect |

Use real Ren'Py glyph metrics; rerun native tests after SDK upgrades. [Forest font evidence](FOREST_FONT_ANALYSIS.en.md).

## Checks

```bash
python3 -B tests/test_text_wrap.py
python3 -B tests/run_native_text_wrap.py /path/to/renpy-sdk
```

Compare mixed Chinese/Japanese/English, ruby, inline images, appended dialogue and direction switches in-game.
