# 開発資料: Forest の字体

[中文](FOREST_FONT_ANALYSIS.zh.md) | [English](FOREST_FONT_ANALYSIS.en.md) | [Русский](FOREST_FONT_ANALYSIS.ru.md) | [日本語](FOREST_FONT_ANALYSIS.ja.md)

[文書一覧](README.ja.md)

字体選択と混在テキスト計測の根拠です。字体変更はゲーム設定を使います。サンプルとアドレスを他版へ一般化しません。

## 静的根拠

対象 `Forest/Forest_CHS_unpacked.exe`、PE32 x86、SHA-256 `94ab25e356d24d9a816ba7bcee6cb30fd6d0f664bbdbc24c000346b2f1b4bda9`。EXE は起動せず、Windows GDI の実選択字体を捕捉したものではありません。

- `0x46336c`: `BA DA CC E5 00` は CP936 で「黑体」。
- `0x46337c`: `82 6C 82 72 20 96 BE 92 A9 00` は CP932 で「ＭＳ 明朝」。
- constructor `0x43c48f` が `[esi+0x19c]` を 0 にし、`0x438d3b` が検査。既定 `0x438da2` は黑体、別分岐 `0x438d6f` はＭＳ 明朝。宋体でも Noto でもない。
- `0x445e70` 内の `0x445ebc` が CreateFontA。height はサイズ、width/角度 0、weight 0 または 700、charset 134 (`GB2312_CHARSET`)。英字圧縮係数なし。
- `0x446019` 付近の advance は、二バイト文字 `0x446042–0x446047` が字体サイズ、一バイト `0x446052–0x446055` は半分。任意の比例ラテン字体計測ではない。

PE VA を `rabin2 -i` と `radare2 -e bin.relocs.apply=true` で確認しました。width 0 の意味は [CreateFontA](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createfonta) を参照してください。

## リポジトリの字体

`port_template/fonts/simhei.ttf` はローカルの `/usr/share/fonts/truetype/winfonts/simhei.ttf` 由来で、EXE 内蔵ではありません。SimHei Regular 5.04 のハッシュ・権利は[字体説明](../port_template/fonts/SimHei-NOTICE.ja.md)にあります。

em=256、通常のラテン文字・空白の advance=128、漢字=256。22px の hinting 前は 11/22px で、原作の半字／全字格に近い値です。Ren'Py native テストの hinting 後は `a`・`t` が 12px、他サンプルは 11px。実行時は最終字形配置から計測し、推測の英字圧縮、East Asian Width、負の字間は追加しません。

字体と説明をコピーし、SimHei を選択肢として残します。2026-10-03 の混在テスト後、本文既定を Noto Sans CJK JP Regular に戻しました。名前画像は不変。旧 SimHei の既定値だけ一度移行し、他の選択は保持します。後から SimHei を選び直せます。

## 検証範囲

自動テストはコピー、既定値移行、Ren'Py native 計測、lint を検査します。GDI と FreeType の形、hinting、baseline、間隔が同じという証明ではありません。混在の断点は目視比較が必要で、字体版や Windows 代替にも左右されます。同一バイトの字体が原作で選ばれたとは動的捕捉なしに断定しません。

Ren'Py 8.5.3、22px、19 字幅、行間 7px の SimHei テストでは `之后，我俩跑到Royal Host餐厅，就桃色电影` は「电」後に改行し「影」が次行に残りました。後続の明示改行込みで 4 行、120px。字体一致だけで全断点が解決するわけではありません。Noto 比例字体と Wiki タグの回帰も残します。

## 混在テキストと既定値

SDK `font.py` は FreeType `auto` hinting が既定。`auto-light`、`bytecode`、`none` で Royal Host は 112→110px ですが、「影」が境界上で改行します。共通規則の `<`、明示 `^n`、字間や行幅を変更しません。

| 字体（22px） | Royal Host | 一漢字 | 参考文の行数 |
| --- | ---: | ---: | ---: |
| SimHei Regular auto | 112px | 22px | 4 |
| Noto Sans CJK JP Regular | 106.703125px | 22px | 3 |
| Noto Sans CJK Light | 105.796875px | 22px | 3 |
| Noto Serif CJK Regular | 114.6875px | 22px | 4 |

黑体に近い太さを保つ Regular sans を選び、幅のために Light を既定にしません。「影」は約 414.7px < 418px となり、既存のぶら下がりで収まります。

```text
之后，我俩跑到Royal Host餐厅，就桃色电影
高谈阔论，一直聊到第二天黎明时分，才在
乌鸦的喧闹声中作别。
```

Wiki オン／オフで断点は同じです。native 計測は実ウィンドウ画像比較ではなく、別文、自選字体、大サイズ、Android は目視確認が必要です。
