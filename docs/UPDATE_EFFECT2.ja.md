# 開発資料: update 効果 2

[中文](UPDATE_EFFECT2.zh.md) | [English](UPDATE_EFFECT2.en.md) | [Русский](UPDATE_EFFECT2.ru.md) | [日本語](UPDATE_EFFECT2.ja.md)

[文書一覧](README.ja.md)

効果2は **4×4 の順序付き点陣置換**です。モザイクや pixel 拡大縮小ではありません。2026-10-11 に五つの原 PE32 EXE を読み取り専用で確認しました。旧 Pixellate 呼出は依頼どおりコメントとして残し、実行しません。結論は記載ビルドに限定します。

## 呼出と表

update 分岐2から描画mode18の不透明経路まで追跡しました。同じ表の存在だけで命令意味を証明したわけではありません。以下は VA です。

| 作品 | update 分岐→転換 | pixel copy | 16 WORD 表 |
| --- | --- | --- | --- |
| Forest | `41c278[2] → 41c1be → 43ec10` | `431f00`、呼出 `42f393` | `463300` |
| Khime | `422290[2] → 4221d6 → 4482c0` | `439520`、呼出 `436983` | `46e100` |
| CannonBall | `416404[2] → 41635d → 42bdb0` | `4207e0`、呼出 `41deb3` | `450070` |
| Evermaiden | `43b5e4[2] → 43b50b → 4531d0` | `447077` 不透明、copy `4471d0..4471f9` | `4eb550` |
| Kagerou | `41e7e0[2] → 41e726 → 4504e0` | `4437d0`、呼出 `440c33` | `47ef38` |

強度を右4bitシフトして表項目を選び、`(x%4)+4*(y%4)` の bit が1なら新 pixel、0なら旧 pixel。五作の表は同一です。

```text
FFDF EFDF 6FDF 6FD7 6BD7 6BD6 6B56 6A56
2A56 2A52 0A52 0A12 0812 0810 0800 0000
```

各 frame の強度は `floor((Step-frame)*255/Step)`、Step−1 frames 後に新画面を完全確定します。Step0は10、Step1またはWait0に名目待機はありません。時計は timeGetTime/GetTickCount のミリ秒で、百分の一秒ではありません。名目時間は `max(0,Step-1)*Wait/1000`。描画時間、Sleep、Wait より厳密に大きくなるまでの追加スケジュールは模擬せず、他効果の既存時刻規則もこの調査では変更しません。

## ビルド識別

| EXE | SHA-256 |
| --- | --- |
| Forest.exe | `8eb71d07304d362ec26cc47d93c6ef5854b5acadd7c9fe941755ad50820a3e56` |
| KhimeDL.exe | `2dfc7b78d32867716ab0406ccbf176b55a76faea1cb9c40feac25c90775222fe` |
| Cannonball.exe | `df4b5b6dffc7002370d0772869baaba551b08fca970e92609ca64b08174f89ba` |
| startup_jp.exe | `88820f28b8f770b486407e55dda28266c6fec42145192d5bc8ad5be21ab895af` |
| kagerou.exe | `f02998fae350945f4de4dc7eab47997e1e2d9b8aa43d49740a80aad893dcde9b` |

## 実装と確認

`runtime/effects.rpy` が表・frame、`runtime/shaders.rpy` が新旧 pixel 選択、`runtime/03_rscript_gfx.rpy` が呼出を担当します。仮想画布で合成してから全体を滑らかに縮放し、画面倍率で点陣を変えません。

`tests/test_shared_port.py /path/to/renpy-sdk` は隔離 Forest/Khime GL2 工程で1/3/10/16/32 steps、4×4方向、最終画面、700×525 /1000×750 の既知 bitmap 一致を検査します。modern/Kagerou は実命令、Step0、Wait0を確認します。原 EXE 逐frame比較ではなく、Android GPU、完全プレイ、旧セーブは別途確認が必要です。
