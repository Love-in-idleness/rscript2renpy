# 開発資料: Khime のクリックとメニュー

[中文](KHIME_CLICK_ANALYSIS.zh.md) | [English](KHIME_CLICK_ANALYSIS.en.md) | [Русский](KHIME_CLICK_ANALYSIS.ru.md) | [日本語](KHIME_CLICK_ANALYSIS.ja.md)

[文書一覧](README.ja.md)

ボタン判定、関連画像、層消去の原動作です。提供された `KhimeDL_CHS.exe` を読み取り専用で調べ、実行・配布していません。SHA-256 `522bec3e93340ffd3bdb24ba98cfb775f80df9d85460819da840d824ad4822a8`、PE32、ImageBase `0x400000`。以下は VA で、別エンジン版の仕様ではありません。

## 根拠

- dispatch `0x420825/0x420850/0x420863/0x4208cc` は setclk/setclksys/resetclk/setlink の `0x423910/0x423940/0x4239a0/0x4239c0`。
- setclk は `0x4222b0 → 0x406860` で object `+0x30` 有効、`+0x34` hover、`+0x52` return、`+0x36` 普通/システム。`0x4222e0 → 0x4068d0` の setclksys は分類 1。
- setlink は `0x422370 → 0x4069b0`。末尾引数で二つの slot を選び、番号 `+0x38/+0x3a`、座標 `+0x40/+0x44`・`+0x48/+0x4c`。ロード先は `this+0x58/this+0x5c` で、本体 `this+0x54` ではない。
- hover `0x40a000` は mode 0 不変、1 反転(renderer13)、2 白化(renderer4、64)、3 本体非表示(renderer23)。`0x40a065–0x40a097` が非零の二関連図を表示。leave `0x40a0c0` は本体色を戻し、二図を隠す。
- `0x405eb4/0x405ecb/0x405ee2` が click/enter/leave を登録。`0x435c60` は本体矩形 `+0x3c…+0x48` と alpha で判定し、setlink 座標を使わない。`0x409aa0` は本体位置、`0x4098a0` は本体矩形を slot0 へ渡し、後の setlink が独立座標を設定。
- cls `0x4067ce → 0x406a90` は強制値1で有効位・二図番号 `+0x30/+0x38/+0x3a` をリセット。キュー時もメタデータは先に消す。`resetclk 0` は `0x4239a4` で飛ばし、全体リセットではない。

## 適応

以前は Khime が共通 native click を選ばず、slot0 を本体代替・判定座標と扱い、cls 後も束縛が残りました。そのため 0501 のヒント層41が旧画像鑑賞ボタン化し、0401 の関連図なし曲目が旧画像・位置を使い、0301 回想も影響しました。

`rscript_click_link_is_preview` と `rscript_click_native_effects` を指定し、本体位置・alpha 判定、mode 別変換、独立した二図表示、cls の束縛消去を使います。Forest/既定方言の代替図動作は保持し、この EXE の規則を強制しません。セーブは変更しません。帰省入口は旧 hover 図9106でなく本体9006を識別します。

`tests/test_shared_port.py /path/to/renpy-sdk` はキュー消去、再利用、関連図なし曲目、座標分離、二図を検査。独立描画テストは enter/leave・pixel・return を確認し、`tests/test_khime_zero.py` は外伝入口と復帰を検査します。実際の三メニューと旧セーブは手動確認が必要です。
