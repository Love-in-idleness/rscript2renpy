# 第三者資産とライセンス

[中文](THIRD_PARTY_NOTICES.zh.md) | [English](THIRD_PARTY_NOTICES.en.md) | [Русский](THIRD_PARTY_NOTICES.ru.md) | [日本語](THIRD_PARTY_NOTICES.ja.md)

[プロジェクトの説明](README.ja.md)

コードは MIT ですが、同梱素材のすべてが MIT ではありません。配布前に出典と個別の権利条件を確認してください。

## renpy-rscript

MIT の renpy-rscript と、Sona-Nyl Ren'Py プロジェクトの互換 RScript 部分を統合・修正しています。[LICENSE](LICENSE) が適用されます。Sona-Nyl 固有実装と Kirikiri 互換層は含みません。

## Forest のカーソル

`runtime/gui/rscript_cursor.png` は Liar-soft『Forest』Windows EXE から抽出した元の 32×32 カーソルで、各移植共通の互換素材です。MIT ではなく、権利は原著作権者に帰属します。

## Forest Android アイコン

`forest/android/android-icon_foreground.png` は Forest のアイコン由来で、Forest 工程のみへコピーします。MIT ではなく原権利者に帰属します。背景は単色の adaptive icon 層です。

## 腐り姫のアイコン

`khime/assets/icon.ico` は `KhimeKusaritop_s/1.ico` 由来。`khime/assets/icon.png` は画素一致のウィンドウ用 PNG で、`icon.ico` と `game/icon.png` へコピーします。MIT ではなく、出典表示は再配布許可を意味しません。`khime/android/android-icon_foreground.png` は同じアイコンを最近傍拡大して透明画布に配置し、背景は黒です。同じ権利制限があります。

## Evermaiden のアイコン

`evermaiden/assets/L42_EM.ico` は `Evermaiden_s/L42_EM.ico` 由来。ICO はそのままコピーし、ウィンドウ・macOS・Android・iOS・Web 用を生成します。MIT ではなく、権利は原著作権者に帰属し、出典表示は再配布許可ではありません。

## CannonBall のアイコン

`cannonball/assets/2.ico` は `CannonBall/2.ico` 由来。ICO はそのままコピーし、ウィンドウ・macOS・Android・iOS・Web 用を生成します。MIT ではなく、出典表示は再配布許可ではありません。

## Forest の字体

`port_template/fonts/simhei.ttf`（SimHei Regular 5.04）は中国語 Forest EXE の要求字体に合わせたものです。内蔵の原著作権表記: © Beijing ZhongYi Electronics Co., 1995-2005, All rights reserved。

Microsoft 提供の専有字体で、MIT/OFL は適用されません。追加の再配布権を取得・検証していません。出典表示は許可ではありません。[SimHei の説明](port_template/fonts/SimHei-NOTICE.ja.md)と [Microsoft FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq)を参照してください。

Forest に含める Noto Sans CJK JP Regular、Noto Sans CJK Light、Noto Serif CJK Regular は SIL Open Font License 1.1 で、原文は `port_template/fonts/NotoSans.txt` にあります。

## その他のテンプレート字体

次のファイルは `port_template/fonts/` にあります。

| ファイル | 字体 | バージョン |
| --- | --- | --- |
| `simfang.ttf` | FangSong（仿宋） | 5.01 |
| `simkai.ttf` | KaiTi（楷体） | 5.01 |
| `simsun.ttc` | SimSun（宋体）、NSimSun（新宋体） | 5.21 |

仿宋・楷体の内蔵著作権表示は © Beijing ZhongYi Electronics Co., 1995-2005, All rights reserved、
宋体コレクションは © Copyright ZHONGYI Electronic Co. 2001, 2020, 2022 です。
三つとも Microsoft supplied font の許諾条件を内蔵し、プロジェクトの MIT や Noto の OFL は適用されません。
使用・埋込・配布は字体および提供元製品の許諾に従います。収録・出典表示は追加の権利を与えません。
