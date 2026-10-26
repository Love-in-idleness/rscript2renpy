# 開発資料：Forest のフォント

[中文](FOREST_FONT_ANALYSIS.zh.md) | [English](FOREST_FONT_ANALYSIS.en.md) | [Русский](FOREST_FONT_ANALYSIS.ru.md) | [日本語](FOREST_FONT_ANALYSIS.ja.md)

[文書一覧](README.ja.md)

## 原プログラムの根拠

試料は PE32 x86 `Forest_CHS_unpacked.exe`、SHA-256：
`94ab25e356d24d9a816ba7bcee6cb30fd6d0f664bbdbc24c000346b2f1b4bda9`。
以下は VA による静的解析であり、Windows が選択した実ファイルの記録ではありません。

- `0x46336c` の CP936 文字列は「黑体」、`0x46337c` の CP932 文字列は「ＭＳ 明朝」です。
- コンストラクター `0x43c48f` は `[esi+0x19c]` をゼロにします。`0x438d3b` の確認後、既定分岐 `0x438da2` は黑体、別分岐 `0x438d6f` は明朝を要求します。
- `0x445e70 → 0x445ebc` の `CreateFontA` は字号から高さを決め、幅と角度は 0、太さは 0 または 700、charset は 134 です。英字の追加圧縮はありません。
- `0x446042–0x446047` は二バイト文字に字号全幅、`0x446052–0x446055` は一バイト文字に半幅を割り当てます。

`CreateFontA` は [Microsoft の資料](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createfonta)を参照してください。

## 移植のフォントと度量

本文の既定は Noto Sans CJK JP Regular で、名前は原画像のままです。
SimHei は設定から選択できます。[出典・ハッシュ・権利](../port_template/fonts/SimHei-NOTICE.ja.md)を参照してください。

SimHei の em は 256、通常の英字・空白の advance は 128、漢字は 256 です。
22px で hinting なしの理論値は 11px / 22px ですが、FreeType hinting で実測値は変化します。
ランタイムは Ren'Py の最終字形度量を使い、負の字間や追加の英字圧縮では補いません。

以下は Ren'Py 8.5.3、22px、全角 19 字幅、行間 7px の参考値です。
別の SDK、フォント版、端末での保証値ではありません。

| フォント | `Royal Host` advance | 漢字幅 | 参考段落の行数 |
| --- | ---: | ---: | ---: |
| SimHei Regular (auto) | 112px | 22px | 4 |
| Noto Sans CJK JP Regular | 106.703125px | 22px | 3 |
| Noto Sans CJK Light | 105.796875px | 22px | 3 |
| Noto Serif CJK Regular | 114.6875px | 22px | 4 |

Noto Regular での参考段落：

```text
之后，我俩跑到Royal Host餐厅，就桃色电影
高谈阔论，一直聊到第二天黎明时分，才在
乌鸦的喧闹声中作别。
```

## 検証範囲

フォント、hinting、代替フォントは折り返しに影響します。組版テストは Windows GDI と FreeType の
字形、基線、間隔、ラスタライズの完全一致を保証しません。字体・字号・SDK の変更後は再確認してください。
[組版](TEXT_WRAPPING.ja.md)と[開発チェック](README.ja.md#開発時の確認)も参照してください。
