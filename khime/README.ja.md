# 腐り姫 移植ガイド

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[プロジェクトの説明](../README.ja.md)

## 概要

自身で用意した『腐り姫』から Ren'Py 8 工程を生成し、任意で『帰省 ～jamais vu～』を追加できます。コマンドはルートで実行します。[環境構築](../docs/SETUP.ja.md)も参照してください。

## リソースの準備

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/Khime
```

`scr/*.tsc`、`grp*`、`.meta.xml`、`bgm/voice/wav`、`mov` を残します。WAV 内の Ogg は抽出し、通常の PCM WAV と元 MPG は直接使えます。パッチは別コピーで実際の文字コードを指定します。

## 工程の生成

```bash
python3 khime/build_khime_rscript.py /path/to/Khime /path/to/renpy/Khime
```

出力先は自動作成できます。再生成前に手動変更を保存し、`--force` を指定します。旧生成器からの更新には新規出力先を推奨します。

## 言語パッチ

```bash
python3 khime/build_khime_rscript.py /path/to/Khime /path/to/renpy/Khime \
    --language jp --language zh=/path/to/Khime.zh
```

`--language jp` は原版の言語名、`zh=ディレクトリ` はパッチ追加です。原版と同じ相対パスに、変更した TSC、画像、音声のみ置きます。

台詞、追加本文、選択肢、文字オブジェクトの翻訳と、字幕・待機・消去の追加に対応します。通常パッチで任意のフロー変更はできません。欠けたシーンは原版を使います。CodeX BMP の透明度は LiarsoftTool で処理し、生成器は直接コピーします。

### 外伝の追加

```bash
python3 khime/build_khime_rscript.py /path/to/Khime /path/to/renpy/Khime \
    --language jp --language zh=/path/to/Khime.zh \
    --khime-zero /path/to/Khime_zero \
    --khime-zero-language zh=/path/to/Khime_zero.zh
```

現在は外伝の `scr/2001.tsc` を接続し、独立タイトルは使用しません。本篇のタイトルで解放条件を満たすと入口が現れます。同番号資源は本篇を上書きしません。外伝のパッチなしでは原文を使います。

## 操作

タイトル設定で字体、サイズ、行字数、行間、言語、システム進捗を変更できます。既定サイズ 29、台詞は 21 字幅。文字速度と音量はゲーム内設定です。動画は起動時のみ再生し、タイトル復帰では再生しません。[第三者資産](../THIRD_PARTY_NOTICES.ja.md)も確認してください。

## 確認と制限

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/Khime lint
```

一部の効果と数字コントロールは完全再現でなく、外伝 BGM の fade も未対応です。全ルート、鑑賞、字幕、音、旧セーブを確認し、Android は別途テストしてください。

開発テスト: `tests/test_khime_builder.py`、`tests/test_khime_zero.py`、`tests/test_shared_port.py`。[開発資料](../docs/README.ja.md#開発資料)を参照してください。
