# Evermaiden 移植ガイド

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[プロジェクトの説明](../README.ja.md)

## 概要

自身で用意した Evermaiden から Ren'Py 8 工程を生成します。対応は開発中です。例はルートで実行します。[環境構築](../docs/SETUP.ja.md)を参照してください。

## リソースの準備

原版とパッチは別の作業コピーで変換します。

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/Evermaiden
liarsofttool -R --unpack-only --gsc-to-tsc -e gbk /path/to/Evermaiden.zh
```

`scr/*.tsc`、全 `grp*` と `.meta.xml`、`bgm/voice/wav`、`mov` を保持します。中国語の例は GBK パッチ用です。実際の符号化に合わせてください。通常 PCM WAV と元 MPG は再変換不要です。

## 工程の生成

```bash
python3 evermaiden/build_evermaiden_rscript.py \
    /path/to/Evermaiden /path/to/renpy/Evermaiden
```

出力先は自動作成できます。再生成前に手動変更を保存し、`--force` を指定します。旧 Evermaiden 工程とは別のセーブディレクトリを使い、旧進捗は移行しません。

## 言語パッチ

```bash
python3 evermaiden/build_evermaiden_rscript.py \
    /path/to/Evermaiden /path/to/renpy/Evermaiden \
    --language jp --language zh=/path/to/Evermaiden.zh
```

原言語名を `jp` とし、`zh=ディレクトリ` でパッチを追加します。元の相対パスで変更ファイルのみ置きます。シーン全体を置き換えるため、パッチの分岐・選択肢・追加 DLC も反映します。欠けたシーンは原版。信頼できるパッチのみ使い、異なる構造の言語を途中で切り替えないでください。

## 操作

既定画面 1280×720、サイズ 32、全角 28 字幅。タイトル設定で文字と言語を変更し、ゲーム内設定は原画像を使います。起動時は `0002.mpg`、`0001.mpg` の順で、タイトル復帰では再生しません。地図選択、CG・音楽鑑賞は原スクリプト制御です。[第三者資産](../THIRD_PARTY_NOTICES.ja.md)を参照してください。

## 確認と制限

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/Evermaiden lint
```

- 一部効果、選択位置、字体選択の見た目は原版と異なります。
- 現サンプルで `2320` の `voice/5/2703`、`4250` の `wav/2527` が不足しています。無音時は先に素材を確認します。
- 全ルート、鑑賞操作、セーブ互換、Android は実検証が必要です。

テストは `tests/test_modern_port.py`。[実装と課題](../docs/EVERMAIDEN_RUNTIME_GAPS.ja.md)を参照してください。
