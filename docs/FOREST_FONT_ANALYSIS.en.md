# Developer reference: Forest fonts

[中文](FOREST_FONT_ANALYSIS.zh.md) | [English](FOREST_FONT_ANALYSIS.en.md) | [Русский](FOREST_FONT_ANALYSIS.ru.md)

[Documentation](README.en.md)

Font choice and mixed-text measurement evidence. Players use settings to change fonts.
Findings are specific to these files and addresses.

## Static evidence

Target: Forest/Forest_CHS_unpacked.exe, PE32 x86, SHA-256
`94ab25e356d24d9a816ba7bcee6cb30fd6d0f664bbdbc24c000346b2f1b4bda9`.
The EXE was not run; Windows GDI's actual selected font was not captured.

- `0x46336c`: BA DA CC E5 00, CP936 “黑体”.
- `0x46337c`: 82 6C 82 72 20 96 BE 92 A9 00, CP932 “ＭＳ 明朝”.
- Constructor `0x43c48f` sets [esi+0x19c]=0. `0x438d3b` checks it:
  default `0x438da2` requests 黑体, alternate `0x438d6f` requests ＭＳ 明朝, not Songti or Noto by default.
- Glyph function `0x445e70` calls CreateFontA at `0x445ebc`: height from size, width 0,
  rotation 0, weight 0 or 700, charset 134 (GB2312_CHARSET); no additional English compression.
- Cached advances near `0x446019`: double-byte chars use font size at `0x446042–0x446047`;
  single-byte use half size at `0x446052–0x446055`, not arbitrary proportional Latin widths.

These VAs were inspected with rabin2 -i and radare2 -e bin.relocs.apply=true for strings, calls and initialization.
CreateFontA width 0: [Microsoft reference](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createfonta).

## Repository fonts

port_template/fonts/simhei.ttf came from /usr/share/fonts/truetype/winfonts/simhei.ttf, not embedded EXE data.
SimHei Regular 5.04: [hash and licensing](../port_template/fonts/SimHei-NOTICE.en.md).
Its em is 256 units: ordinary Latin/ASCII space advance 128, CJK 256. At 22px theoretical unhinted advances
are 11/22px, close to native half/full grids. Local Ren'Py FreeType hinting makes a/t advance 12px,
other sample letters 11px. Runtime uses final Ren'Py glyph metrics, not guessed English compression,
East Asian Width or negative spacing.

Generators copy fonts/notices. SimHei remains selectable. After mixed-text tests on 2026-10-03,
body default returned to Noto Sans CJK JP Regular; nameplate images did not change.
Old SimHei defaults migrate once, other selected fonts stay; users can choose SimHei again.

## Evidence limits

Tests cover copying, default migration and native Ren'Py metrics; lint checks scripts, not identical GDI/FreeType glyphs,
hinting, baselines or spacing. Mixed-text breaks still need comparison. Font versions and Windows fallback may differ;
without dynamic capture the original cannot be claimed to use the exact bundled font bytes.

Local Ren'Py 8.5.3, 22px, 19 widths, 7px line spacing: the sample
“之后，我俩跑到Royal Host餐厅，就桃色电影” still breaks after 电, leaving 影 alone.
With later explicit breaks it is four lines, height 120px. Matching a requested font did not solve every screenshot difference.
Tests retain proportional Noto and Wiki-tag metrics cases.

## Mixed text and current default

Local SDK font.py uses FreeType auto hinting. SimHei auto-light/bytecode/none reduces Royal Host
from 112 to 110px, but 影 still begins at the 19-width boundary. No change to the existing < boundary,
no extra compression, negative spacing, wider configured lines or removal of explicit ^n.
At the user's requested fallback, existing fonts measured at 22px:

| Font | Royal Host advance | CJK glyph | Sample lines |
| --- | ---: | ---: | ---: |
| SimHei Regular（auto） | 112px | 22px | 4 |
| Noto Sans CJK JP Regular | 106.703125px | 22px | 3 |
| Noto Sans CJK Light | 105.796875px | 22px | 3 |
| Noto Serif CJK Regular | 114.6875px | 22px | 4 |

Regular sans-serif keeps weight closer to Hei rather than selecting Light just for width.
With Noto Regular, 影 starts around 414.7px < 418px regular line width, allowing natural extension by existing rules:

```text
之后，我俩跑到Royal Host餐厅，就桃色电影
高谈阔论，一直聊到第二天黎明时分，才在
乌鸦的喧闹声中作别。
```

Wiki on/off has identical breaks. This is native layout testing, not actual-window screenshot comparison.
Other text, custom fonts, large sizes and Android still need manual checks.
