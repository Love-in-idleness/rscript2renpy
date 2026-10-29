# Developer reference: text layout

[中文](TEXT_WRAPPING.zh.md) | [English](TEXT_WRAPPING.en.md) | [Русский](TEXT_WRAPPING.ru.md) | [日本語](TEXT_WRAPPING.ja.md)

[Documentation](README.en.md)

Common layout rules and maintenance points. Players change fonts, sizes and line lengths in settings.

## Rules

- Line width is base-font full-width advance × configured count; actual text uses shaped glyph advances.
- All ports use `runtime/kinsoku.json`, with the same format and default character sets as LiarsoftTool's runtime. The old inline tables are removed.
- Keep consecutive forbidden line-start characters on the preceding line; move opening-bracket runs together. An indivisible run may exceed the width instead of dropping characters or creating an illegal break.
- A proportional glyph starting inside the line may hang over the edge; widths still use shaped advances.
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
| 甲乙。！ | 甲乙。！ |
| 甲（「乙 | 甲↵（「乙 |
| 甲（乙 | 甲↵（乙 |
| 甲（ | 甲（ |
| 甲（。 | 甲（。 |

Proportional fonts may break differently. Large sizes or small spacing need clipping/ruby-overlap checks.

## Maintenance

| File | Role |
| --- | --- |
| runtime/kinsoku.json | Single character table, installed as `game/engine/kinsoku.json` |
| runtime/rscript_wrap.py | Prohibited-break and wrapping rules |
| runtime/00_rscript_wrap.rpy | Ren'Py glyph measurement and layout |
| port_template/game/text_features.rpy | Player text settings |
| Game overrides | Defaults, text rectangle and dialect |

The UTF-8 JSON requires integer `version: 1` and strings `no_line_start` and `no_line_end`.
The sets must be disjoint and contain only non-NUL BMP characters. Invalid configuration fails without falling back to old rules.
Ren'Py's resource API reads it in packaged games too. Explicit `^n` breaks are preserved regardless of kinsoku.

Use real Ren'Py glyph metrics; rerun native tests after SDK upgrades. [Forest font evidence](FOREST_FONT_ANALYSIS.en.md).

## Checks

```bash
python3 -B tests/test_text_wrap.py
python3 -B tests/run_native_text_wrap.py /path/to/renpy-sdk
```

Compare mixed Chinese/Japanese/English, ruby, inline images, appended dialogue and direction switches in-game.
