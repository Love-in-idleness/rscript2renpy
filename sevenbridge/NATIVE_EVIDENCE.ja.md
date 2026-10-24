# SevenBridge: 原プログラムの根拠

[中文](NATIVE_EVIDENCE.zh.md) | [English](NATIVE_EVIDENCE.en.md) | [Русский](NATIVE_EVIDENCE.ru.md) | [日本語](NATIVE_EVIDENCE.ja.md)

[利用ガイド](README.ja.md)

確認日2026-10-22。日本語 `SBridge_jp.exe`、PE32/i386、ImageBase `0x400000`、SHA-256:

```text
c7d5fc38cf0c354a61d056b607cf1367b2529557e9e0407d0b0fdf12771b35e3
```

原ファイルと Ghidra の静的解析で、原ゲームの実行映像ではありません。原本は変更・実行していません。以下は VA です。

## 資源と入口

scr.xfl は111 GSC。既存112旧TSCは基準にせず、現LiarsoftToolでコピー上に再生成します。modern-36 containerと各TSCのrscript18/rscript19/modern schemaを区別します。

0000→0001、開始は0100→0110→2001。CG鑑賞は0201–0208/0210、回想は0301/0302/0310と5001–5013、音楽は0400/0401。脚本が鑑賞を制御するため、EXE内の未使用top_me*を採用しません。タイトルを保持し、環境設定のみ共通Text Settings。利用者確認によりCG組の末尾で次の左クリックはthumbnailへ戻ります。移植はr[299]の元頁へ帰り、hitのレジスターを強制変更しません。

APINIは `0x469740`、初期化 `0x41a260`、800×600。`0x41ab90` はRsInit.cfg、次にRsInit.dllを試しますが基準環境に両方ないため、EXE内蔵設定です。

## 命令と状態

| 実装 | 根拠 |
| --- | --- |
| dispatch | `0x41cc40`、低opcodeと高VMを分離 |
| 三引数locmode | case `0x26 → 0x420220`、object0は全普通object |
| folder0 | `0x4204e0`、object1–49のfolderを更新 |
| 単channel SE | cases0x3e/0x3f/0x40は1/3/1式 |
| getflag | case `0x72 → 0x421670`、番号とmode |
| CG記録 | `0x41fcc0`、常に独立bit。番号<1000のみr[9000+番号] |
| 普通register snapshot | `0x41a260/0x41b070`、16-bit×7000 |

getflag mode0はbitをr[0]へ、非零は進捗を立てr[0]保持。番号はunsigned16。`0x41b450/0x41b470` はbank0、`0x424110/0x424190` がbit問合せ/設定。gloadと同じ表を移植のpersistent.seen_cgへ保存し、既存バックアップにも含めます。

## 文字とメディア

`0x414990` がtboxNNを読みます。tbox00は800×130、本文(0,11)、682×119、wait(690,102)、gfNNNの幅146。metadataを保持し、名前と本文を分離します。`0x413f70` が本文、`0x415050(this,0x80)` は背景alpha。設定の明図が選択、*_fが暗図で、共通UIも同じ向きです。

`0x41b0b0` はr[1]/r[2]/r[3]をセーブheaderへ。`0x4037d0` は現在進捗でなく保存番号でdt1_/dt2_を選びます。接頭部は `0x469160/0x469158`。本作章条はdt2_*なのでr[2]も保存します。nonblの1–9名は全角、10は半角。metadataの画布・offsetを読み、半角名探索や切り抜き中央化だけにしません。

`0x41b5b0` はvoice番号を10000で組分けし、0はvoice/%04d.wav、他はvoice/<組>/%04d.wav。変換後は同名OGG、PCM WAVは原状保持。`0x4218d0` はRepeatを保持し999=loop。

2026-10-23再確認で、原movは0002/0003/0004.mpg（MPEG-1動画+MP2音声）。旧コピーでmovを落としていました。起動callback `0x4238a0` の `0x4238eb/0x42390e` はmov/0002と0001を参照し `0x445240` を呼びます。共通順序(2,1)を使い、ない0001は既存処理で飛ばします。0110/0302は動画3/4、2004は2。mov/*.mpgをコピーして脚本呼出を保持します。

起動のREA Evidence:
`ev_0a8303ae0ac91d42cca1fa64a481fcf91c1ab0bfc78cbd8821b840268a01c474`、
`ev_177a58fd85e2021bd3409f818451f41c36da4a3b309aa5a2872d1d5d49969876`。
GNU objdump:
`ev_32b12957eff616758728f349b1d051ff7ad77752533cd13b791d6b687a91bf83`。

## 検証記録

```bash
python3 -B tests/test_sevenbridge_builder.py
python3 -B tests/run_sevenbridge_port.py /path/to/generated-sevenbridge /path/to/renpy-sdk
```

`--capture /path/to/captures` で隔離セーブからタイトル、本文、設定、保存・読込を捕捉できます。画面なしではxvfb-run -aで包めます。lintには原全角数字ファイル名と動的分岐の不可達警告が残ります。

REA/Ghidra12.1.4の主要記録:

- dispatch: `ev_6e60215a5db021d73ca2e5b31caeab471f13ce6021c2770e151610381da40311`
- 進捗問合せ: `ev_2094337b09290b909f5863fb0a103aed4f01e10b48c67aad27faf23a5ddda192`
- CG記録: `ev_7f029987eebd0e711fd2b5d454465b8a1f31e3c4fd1c3891731d03d30491942c`
- 音声: `ev_0e12bcca631fa9ef551e87ad96278d2d2c9da8f193376ea1f5f5fb800dade10d`
- 文字配置: `ev_8f8d19a742c865ecddd9c34cc6be37ef9fcd394cf9bf4a919cc1039a72f99d83`
- 初期化: `ev_2a124917ccf0f8ee508a62dc67e9d85f8e4934a81db6f81540d7f625beeee713`
- セーブheader: `ev_782a08b1a9610744432bee9a92493d79bdc1910c99d01bccca39da1cc75f7237`
- 保存画像: `ev_09e1bf507945becc87a6ff904be3610141ae649d35952d7fd0053fab971de964`

SDK検査は原作実行との比較ではありません。字形、全転換、全ルート、Windows/Android実機は別途確認が必要です。
