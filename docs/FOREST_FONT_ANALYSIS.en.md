# Developer reference: Forest fonts

[中文](FOREST_FONT_ANALYSIS.zh.md) | [English](FOREST_FONT_ANALYSIS.en.md) | [Русский](FOREST_FONT_ANALYSIS.ru.md) | [日本語](FOREST_FONT_ANALYSIS.ja.md)

[Documentation](README.en.md)

## Native evidence

Sample: PE32 x86 `Forest_CHS_unpacked.exe`, SHA-256:
`94ab25e356d24d9a816ba7bcee6cb30fd6d0f664bbdbc24c000346b2f1b4bda9`.
These are static findings at VAs, not a capture of the font file selected by Windows.

- The CP936 string at `0x46336c` is “黑体”; the CP932 string at `0x46337c` is “ＭＳ 明朝”.
- Constructor `0x43c48f` sets `[esi+0x19c]` to zero. After `0x438d3b` checks it, default branch `0x438da2` requests Hei; alternate branch `0x438d6f` requests Mincho.
- `0x445e70 → 0x445ebc` calls `CreateFontA`: height from size, width and rotation zero, weight 0 or 700, charset 134. No extra Latin compression.
- `0x446042–0x446047` gives double-byte characters a full-size advance; `0x446052–0x446055` gives single-byte characters half.

See [Microsoft's documentation](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createfonta) for `CreateFontA`.

## Port fonts and metrics

Body text defaults to Noto Sans CJK JP Regular; nameplates remain original images.
SimHei is selectable; see its [provenance, hash, and licensing](../port_template/fonts/SimHei-NOTICE.en.md).

SimHei uses 256 units per em, with 128-unit ordinary Latin/space and 256-unit CJK advances.
At 22px, theoretical unhinted advances are 11px / 22px, but FreeType hinting changes actual metrics.
The runtime uses final Ren'Py glyph metrics, not negative spacing or extra Latin compression.

Reference values below use Ren'Py 8.5.3, 22px, 19 fullwidth cells, and 7px line spacing.
They are not guarantees across SDKs, font versions, or devices.

| Font | `Royal Host` advance | CJK width | Sample paragraph lines |
| --- | ---: | ---: | ---: |
| SimHei Regular (auto) | 112px | 22px | 4 |
| Noto Sans CJK JP Regular | 106.703125px | 22px | 3 |
| Noto Sans CJK Light | 105.796875px | 22px | 3 |
| Noto Serif CJK Regular | 114.6875px | 22px | 4 |

The reference paragraph with Noto Regular is:

```text
之后，我俩跑到Royal Host餐厅，就桃色电影
高谈阔论，一直聊到第二天黎明时分，才在
乌鸦的喧闹声中作别。
```

## Limits

Font files, hinting, and fallback affect wrapping. Layout tests do not establish identical glyphs, baselines,
spacing, or rasterization between Windows GDI and FreeType. Recheck after changing fonts, size, or SDK.
See [Text layout](TEXT_WRAPPING.en.md) and [development checks](README.en.md#development-checks).
