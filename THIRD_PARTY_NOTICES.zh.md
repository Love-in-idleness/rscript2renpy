# 第三方资源与授权

[中文](THIRD_PARTY_NOTICES.zh.md) | [English](THIRD_PARTY_NOTICES.en.md) | [Русский](THIRD_PARTY_NOTICES.ru.md) | [日本語](THIRD_PARTY_NOTICES.ja.md)

[返回主说明](README.zh.md)

项目代码采用 MIT，但并非所有随附素材都采用 MIT。以下逐项说明来源与独立授权，分发前请确认。

## renpy-rscript

RScript 兼容运行时合并并修改了 MIT 授权的 renpy-rscript，以及 Sona-Nyl Ren'Py 项目中兼容的 RScript 部分，
这些代码适用 [LICENSE](LICENSE)。不包含 Sona-Nyl 游戏专属代码或其 Kirikiri 兼容层。

## Forest 鼠标光标

`runtime/gui/rscript_cursor.png` 是从 Liar-soft《Forest》Windows EXE 提取的原始 32×32 光标，
作为各 RScript 移植共用的兼容素材。不适用本仓库 MIT，权利归原版权方。

## Forest Android 图标

`forest/android/android-icon_foreground.png` 来自《Forest》应用图标，只在生成 Forest 工程时复制。
不适用 MIT，权利归原版权方；配套背景是纯色自适应图标层。

## Khime 应用图标

`khime/assets/icon.ico` 来自 Khime（Kusarihime）的 `KhimeKusaritop_s/1.ico`。
`khime/assets/icon.png` 是像素一致的 Ren'Py 窗口 PNG 副本，生成器分别复制到
`icon.ico` 与 `game/icon.png`。不适用 MIT，权利归原版权方；署名不等于取得再分发许可。
`khime/android/android-icon_foreground.png` 由同一图标最近邻放大并置于透明自适应画布，背景纯黑，前景权利限制相同。

## Evermaiden 应用图标

`evermaiden/assets/L42_EM.ico` 来自 `Evermaiden_s/L42_EM.ico`。生成器原样复制 ICO，
从同图生成窗口、macOS、Android、iOS 和 Web 图标。不适用 MIT，权利归原版权方；署名不构成再分发许可。

## CannonBall 应用图标

`cannonball/assets/2.ico` 来自 `CannonBall/2.ico`。生成器原样复制 ICO，
从同图生成窗口、macOS、Android、iOS 和 Web 图标。不适用 MIT，权利归原版权方；署名不构成再分发许可。

## Forest 字体

`port_template/fonts/simhei.ttf`（SimHei Regular 5.04）用于匹配 Forest 中文 EXE 请求的字体。
内嵌版权原文：© Beijing ZhongYi Electronics Co., 1995-2005, All rights reserved。
它是 Microsoft 提供的专有字体，不适用 MIT 或 OFL；项目未取得或验证额外再分发权，署名不构成许可。
见 [SimHei 说明](port_template/fonts/SimHei-NOTICE.zh.md) 与
[微软字体分发 FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq)。

Forest 生成器附带 Noto Sans CJK JP Regular、Noto Sans CJK Light、Noto Serif CJK Regular，
适用 SIL Open Font License 1.1，原文保存在 `port_template/fonts/NotoSans.txt`。
