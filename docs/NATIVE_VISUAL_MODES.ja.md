# 開発資料：原生色彩・描画モード

[中文](NATIVE_VISUAL_MODES.zh.md) | [English](NATIVE_VISUAL_MODES.en.md) | [Русский](NATIVE_VISUAL_MODES.ru.md) | [日本語](NATIVE_VISUAL_MODES.ja.md)

[文書一覧](README.ja.md)

## 対象と範囲

新しい Evermaiden エンジンから調べ、六つの移植作品と Khime Zero を比較します。
原 EXE は読み取り専用で解析し、ゲーム自体は起動していません。アドレスは各標本の VA です。

| 標本 | SHA-256 |
| --- | --- |
| Forest / Forest.exe | `8eb71d07304d362ec26cc47d93c6ef5854b5acadd7c9fe941755ad50820a3e56` |
| Khime / KhimeDL.exe | `2dfc7b78d32867716ab0406ccbf176b55a76faea1cb9c40feac25c90775222fe` |
| Khime Zero / Khime_zero.exe | `56e3b1316c2fd3bdc7826606fedf938a5b7509385e4ba4300010c7892a7af76c` |
| CannonBall / Cannonball.exe | `df4b5b6dffc7002370d0772869baaba551b08fca970e92609ca64b08174f89ba` |
| SevenBridge / SBridge_jp.exe | `c7d5fc38cf0c354a61d056b607cf1367b2529557e9e0407d0b0fdf12771b35e3` |
| Kagerou / kagerou.exe | `f02998fae350945f4de4dc7eab47997e1e2d9b8aa43d49740a80aad893dcde9b` |
| Evermaiden / startup_jp.exe | `88820f28b8f770b486407e55dda28266c6fec42145192d5bc8ad5be21ab895af` |

SevenBridge の基準は `SBridge_jp.exe` であり、同じディレクトリの別の起動ファイルではありません。

## 色彩モード

0 は変更なし、1 は黒、2 は反転、3 は RGB の算術平均によるグレー、14 は変更なしです。
4～13 は次のアルゴリズムと RGB 定数を使い、HSV フィルタではありません。

| モード | アルゴリズム | RGB |
| --- | --- | --- |
| 4 | Tint | `8b4513` |
| 5 | Tint | `483d8b` |
| 6 | Tint | `ff8000` |
| 7 | Night | `181020` |
| 8 | Level | `282040` |
| 9 | Level | `383080` |
| 10 | Level | `802d50` |
| 11 | Night | `904030` |
| 12 | Level | `805030` |
| 13 | Level | `a06040` |

```text
Grade(x,k) = floor(x*(k+1)/128)                  if k < 128
             floor(x+(256-x)*(2*k-255)/256)     otherwise
Tint(C,T) = Grade(T, floor((R+G+B)/3))
m = min(R,G,B)
Night(C,T) = floor(C*(256-m)/256) + floor(Grade(C,T)*(m+1)/256)
```

色変換は alpha を保持します。15 はバイト量子化と区分的な色相変形を伴う HSL Power で、
単なる彩度上昇ではありません。原生 RGB 例：赤→(255,1,1)、緑→(7,255,1)、青→(255,192,1)。

Forest は 1～6、CannonBall と Khime Zero は 1～5 を実装します。
Khime、SevenBridge、Kagerou、Evermaiden の拡張系列ではオブジェクト型を区別します。
Full は 13 まで、Lim はさらに 15 を実装し、14 は変更しません。
Evermaiden のオブジェクトモード 1 は Full です。列挙外の WORD 値は画像を変更せず、
未実装として降格する対象ではありません。共通層は移動、回転、アニメーション消去中も色を保持します。

## 描画とマスク

新版の `draw 3` は各チャンネルに `Grade(destination, mask)` を適用します。
Level を使わず、普通の alpha 描画でもありません。ユーザーの指定により、旧エンジンで
通常描画の別名だった 3 もこの新版の意味に統一し、他の旧別名は保持します。
`draw 4/5` は黒／白 LUT、強度は `WORD(Level)*255//100` です。
Kagerou の既存の名前付き `dim256` は換算済みのバイト強度を受け取り、再換算しません。
`effect` の 1 以外は GIMP Color-to-Alpha 近似から Grade へ変更し、1 は背景反転のままです。

Grade は GPU の二段描画で、背景のチャンネルを縮尺してからハイライトを加えます。
各段の丸めで最大二階調の差を許容し、GDI の境界画素と完全一致するとは主張しません。
被覆率、深度、通常のラスタ結合を保ち、文字はラスタ結合へ含めません。

## 根拠

- Evermaiden: `4154d0 / 415810` (Full / Lim), `44d880` (CMath),
  `461a70 / 461c90 / 461e50` (Level / Night / Power).
- Forest: `407fe0 / 408200`; Khime: `40b1a0 / 40b710`;
  Zero: `407910 / 407b00`; CannonBall: `4056d0`;
  SevenBridge: `409820`.
- REA: `ev_75cb85845a085eaa225b93c2ab638203ea2858f7a100edc6ed6a153582bb224a`,
  `ev_8fd952896a36ca15b3b46ccc02fbd32d104f0c3c516dfe76985a7b10aea65ac9`,
  `ev_f8cf3c06d5dfc8f6cb7d77e805c6e00d8fc35f59be596699c1fea2aca8f7a730`,
  `ev_905392cadc15179ebc74e6479ea8cad674b695c001ad6199612d5bb5dfea6b06`.
- Draw: `4129b0` → renderer `2 / 14 / 104 / 3 / 4`,
  `4464e0` case `104`;
  `ev_d72f2de30d9317ab80890eccc8c6d517851b60fbe84c35787f324ef2d2975b49`,
  `ev_2cb8389d102a8c15d2314404097b4b9c666238e5159e510d42ef00c7551d4863`.

## 検証と残作業

独立した float32 Power 参照は、限定した原生画素ルーチンと 5102 個の合成 RGBA 標本で一致しました。
原生コードと非公開テスト用バイナリはコミットしません。共通 GL2 検査は色、移動中と終了後、
回転、消去、draw 3/4/5、通常描画への復帰、CG 層との混合を対象とし、完全なプレイ検証ではありません。

引数を受け付けるだけでは効果全体の再現を証明できません。対角 load/cls、18、複雑な消去 30～35、
move 4/11～13、その他の oaction は軌跡、型、時序の確認が必要です。
既存の近似アニメーションも原版の逐フレーム再現ではありません。
