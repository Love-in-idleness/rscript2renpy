# 開発資料: Khime の画像効果

[中文](KHIME_EFFECT_ANALYSIS.zh.md) | [English](KHIME_EFFECT_ANALYSIS.en.md) | [Русский](KHIME_EFFECT_ANALYSIS.ru.md) | [日本語](KHIME_EFFECT_ANALYSIS.ja.md)

[文書一覧](README.ja.md)

対象 `KhimeDL_CHS.exe`、SHA-256 `522bec3e93340ffd3bdb24ba98cfb775f80df9d85460819da840d824ad4822a8`、PE32、ImageBase `0x400000`。EXE は配布せず、以下の VA と確認結果を別版へ一般化しません。

load `0x422d70 → 0x4218d0 → 0x4064f0`、font `0x422e20 → 0x421a00 → 0x4066f0` は共に `0x4070b0`、cls `0x423080 → 0x421b30 → 0x406790` は `0x407ec0`。文字と画像は効果を共有し、非零 _oload を全てゼロにしてはいけません。

| 引数 | load / cls | 確認内容・共通実装 |
| --- | --- | --- |
| 3 | `0x407218 / 0x407f7a` | renderer2、alpha step32、通常 fade |
| 4 | `0x40724a / 0x407fae` | renderer0x12、step32、点陣転換 |
| 10 | `0x4073da / 0x4081ed` | 下から入る／下へ去る。native move の近似軌跡 |
| 15 | `0x40771d / 0x408485` | renderer4、step16、alpha を保持した白 RGB fade |
| 19 | `0x4077f9 / 0x40854e` | renderer2、step8、通常の四倍の fade |

renderer4 `0x436c2e → 0x439d60` は RGB を白へ混合。vtable `+0x40/+0x44` は `0x407d60` (ret4) で、引数20から縮放と推定できません。

_effect `0x4235a0` の Mode1は renderer `0x67 → 0x43b0f0`、mask 赤ゼロ領域で target RGB 反転。それ以外 `0x68 → 0x43b1f0` は中灰輝度混合。共通 shader に target 反転を加え、Mode0 は既存近似を維持。`ES101.png` 等の大小文字は無視して探索し、実パスを保持します。コピー・改名は不要です。

effect3 の 0.5 秒を基準に19は2秒、15は1秒。原 frame 間隔、加速度、pixel 丸めは未再現です。未確認効果は注釈付き平坦化、文字 effect0 は既存 Forest fade を維持します。静的解析・lint は見た目一致の証明ではありません。

`python3 -B tests/test_shared_port.py /path/to/renpy-sdk` で shader、反転/白 pixel、キュー、文字効果を検査します。目視入口: 1102(19)、1110(文字4)、7501(clear10)、7503(load15)。
