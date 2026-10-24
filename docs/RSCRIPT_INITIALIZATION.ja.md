# 開発資料: RScript 初期設定

[中文](RSCRIPT_INITIALIZATION.zh.md) | [English](RSCRIPT_INITIALIZATION.en.md) | [Русский](RSCRIPT_INITIALIZATION.ru.md) | [日本語](RSCRIPT_INITIALIZATION.ja.md)

[文書一覧](README.ja.md)

新規適応は `RsInit.tcf` から画面寸法、資源ディレクトリ、起動情報を調べられます。すべての作品に TCF や `RsInit.dll` があるわけではなく、ない場合は EXE と脚本を調べます。

## 調査ツール

```bash
python3 tools/inspect_rscript_init.py /path/to/game-resources
python3 tools/inspect_rscript_init.py /path/to/RsInit.tcf --encoding gbk
```

読み取りのみで JSON を端末へ出力し、EXE/DLL は実行しません。既定 CP932、`--encoding` で変更できます。設定値、資源場所、CFG 存在、未知項目を報告します。

## 確認済みキー

以下は Khime Zero の初期化モジュールに基づきます。

| キー | 用途 |
| --- | --- |
| `title` | ウィンドウ名 |
| `width`、`height` | 初期画面寸法 |
| `exec`、`script` | 起動スクリプトの有効化と番号 |
| `scrdir` | シナリオ場所 |
| `sysimgdir`、`layerimgdir`、`faceimgdir`、`bgimgdir` | 画像場所 |
| `moviedir`、`wavedir`、`bgmdir`、`voicedir` | メディア場所 |
| `savepfx` | 原セーブ接頭部 |
| `scrmod`、`extmod` | コンパイラー・拡張 module |
| `bgm`、`bgmsource`、`layermod` | 数値。個別の意味は未確認 |

TCF が最終設定とは限らず、CFG や本体の既定値が優先する場合があります。一作品の規則を全エンジンへ一般化しません。

## 根拠

`Khime_zero/RsInit.dll`、SHA-256 `b35bd24626a65d67ee932f2a62076070805c98b5f7a50f9920c19f2d8696b218`。

- `GetInitialData` (`0x10001dd0`) が TCF から呼出側の構造へ記入。
- `SaveInitialData` (`0x10002170`) が 324-byte 構造を CFG に保存。
- 本体 `0x415330` は CFG を先に試し、失敗時に TCF。
- 中国語サンプルは title が GBK、コメントに CP932 が混在。全体を一つの推定で読まない。

このビルドの静的根拠です。ツールに DLL 配布は不要です。

## 確認

```bash
python3 -B tests/test_rscript_init.py
python3 -B tests/test_rscript_init.py /path/to/Khime_zero
```
