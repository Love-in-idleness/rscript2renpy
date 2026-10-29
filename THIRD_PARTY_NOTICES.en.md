# Third-party assets and licenses

[中文](THIRD_PARTY_NOTICES.zh.md) | [English](THIRD_PARTY_NOTICES.en.md) | [Русский](THIRD_PARTY_NOTICES.ru.md) | [日本語](THIRD_PARTY_NOTICES.ja.md)

[Project guide](README.en.md)

The MIT license covers project code, not every bundled asset. The notices below identify each asset and its separate terms.

## renpy-rscript

The RScript compatibility runtime incorporates and adapts code from the
MIT-licensed `renpy-rscript` runtime, including compatible RScript portions
used by the Sona-Nyl Ren'Py project. These portions are distributed under the
MIT license in [LICENSE](LICENSE).

Game-specific Sona-Nyl code and its Kirikiri compatibility layer are not part
of this repository.

## Forest mouse cursor

`runtime/gui/rscript_cursor.png` is the original 32x32 mouse cursor extracted
from the Windows executable of Liar-soft's *Forest*. It is included as a
shared compatibility asset for RScript game ports. This image is not covered
by this repository's MIT license; all rights remain with its original
copyright holder.

## Forest Android application icon

`forest/android/android-icon_foreground.png` contains the application icon
from Liar-soft's *Forest*. It is copied only when generating a Forest port.
This image is not covered by this repository's MIT license; all rights remain
with its original copyright holder. The accompanying background image is a
solid-color adaptive-icon layer.

## Khime application icon

`khime/assets/icon.ico` is the original Khime (*Kusarihime*) application icon
supplied as `KhimeKusaritop_s/1.ico`. `khime/assets/icon.png` is a pixel-identical
PNG copy for the Ren'Py window. The Khime generator copies these assets to
`icon.ico` and `game/icon.png` in the generated project. These images are not
covered by this repository's MIT license; all rights remain with the original
copyright holder. Attribution does not establish redistribution permission.

`khime/android/android-icon_foreground.png` is a nearest-neighbor scaled copy
of the same icon on a transparent adaptive-icon canvas; the accompanying
background is solid black. The foreground has the same copyright restrictions.

## Evermaiden application icon

`evermaiden/assets/L42_EM.ico` is the original Evermaiden application icon,
supplied from `Evermaiden_s/L42_EM.ico`. The generator copies the ICO unchanged
and derives the window, macOS, Android, iOS and web icons from that same image.
These assets are not covered by MIT; all rights remain with the original
copyright holder. Attribution does not establish redistribution permission.

## CannonBall application icon

`cannonball/assets/2.ico` is the original CannonBall application icon,
supplied from `CannonBall/2.ico`. The generator copies the ICO unchanged
and derives the window, macOS, Android, iOS and web icons from that same image.
These assets are not covered by MIT; all rights remain with the original
copyright holder. Attribution does not establish redistribution permission.

## Forest fonts

`port_template/fonts/simhei.ttf` (SimHei Regular, version 5.04) is included to match
the font requested by the Chinese Forest executable. Its embedded copyright
is © Beijing ZhongYi Electronics Co., 1995-2005, All rights reserved. This is
a proprietary Microsoft-supplied font, not covered by MIT or OFL. This project
has not obtained or verified additional redistribution rights; attribution
is not permission to distribute it. See [SimHei-NOTICE.md](port_template/fonts/SimHei-NOTICE.en.md)
and Microsoft's [font redistribution FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq).

The Forest generator includes Noto Sans CJK JP Regular, Noto Sans CJK Light,
and Noto Serif CJK Regular. These fonts are licensed under the SIL Open Font
License 1.1; its license text is stored at `port_template/fonts/NotoSans.txt`.

## Additional template fonts

The following files are in `port_template/fonts/`:

| File | Font | Version |
| --- | --- | --- |
| `simfang.ttf` | FangSong (仿宋) | 5.01 |
| `simkai.ttf` | KaiTi (楷体) | 5.01 |
| `simsun.ttc` | SimSun (宋体), NSimSun (新宋体) | 5.21 |

FangSong and KaiTi embed © Beijing ZhongYi Electronics Co., 1995-2005, All rights reserved;
the SimSun collection embeds © Copyright ZHONGYI Electronic Co. 2001, 2020, 2022.
All three files embed Microsoft supplied font license terms, not this project's MIT or Noto's OFL.
Use, embedding and distribution remain subject to the font and source-product licenses;
inclusion and attribution grant no additional rights.
