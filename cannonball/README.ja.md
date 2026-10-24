# CannonBall 移植ガイド

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[プロジェクトの説明](../README.ja.md)

## 概要

自身で用意した CannonBall から Ren'Py 8 工程を生成します。開発中です。例はルートで実行します。[環境構築](../docs/SETUP.ja.md)を参照してください。

## リソースの準備

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/CannonBall
liarsofttool -R --unpack-only --gsc-to-tsc -e gbk /path/to/CannonBall.zh
```

原版とパッチを別々に変換し、`scr/*.tsc`、全 `grp*`、`bgm/voice/wav`、既存 `mov` を保持します。タイトルは `grpe/0901` と `bgm/Track01.wav`。通常 PCM WAV・元 MPG は直接使えますが、WAV 内の Ogg は抽出します。中国語例は GBK 用で、実際の符号化を選びます。

## 工程の生成

```bash
python3 cannonball/build_cannonball_rscript.py \
    /path/to/CannonBall /path/to/renpy/CannonBall
```

出力先は自動作成できます。再生成前に手動変更を保存し、`--force` を指定します。通常の生成に原 EXE は不要です。

## 言語パッチ

```bash
python3 cannonball/build_cannonball_rscript.py \
    /path/to/CannonBall /path/to/renpy/CannonBall \
    --language jp --language zh=/path/to/CannonBall.zh
```

`jp` は原言語名、`zh=ディレクトリ` はパッチ。元の相対パスで変更ファイルだけ置きます。シーン全体を置き換え、パッチ固有の分岐・追加シーンを保持します。現中国語パッチのフローは原版と異なり、生成器は日本語フローへ自動修正しません。信頼できるパッチだけ使い、構造の異なる言語を途中で切り替えないでください。

## 操作

設定、セーブ・ロード、文字選択、制御バーは原画像を使用します。レース中は回帰とセーブを禁止し、終了時に復元します。起動動画は `0002.mpg`→`0001.mpg`、タイトル復帰では再生しません。[第三者資産](../THIRD_PARTY_NOTICES.ja.md)を参照してください。

## 確認と制限

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/CannonBall lint
```

- 数字スキン、計数アニメーション、履歴ページは完全再現ではありません。
- 一部転換と音楽 fade は原作と異なる可能性があります。
- 中国語パッチのフロー由来、言語間セーブ、全レース・戦闘・ルートは別途確認が必要です。
- Android は実機確認が必要です。

テストは `tests/test_cannonball_port.py`。根拠と効果一覧は[開発資料](NATIVE_EFFECTS.ja.md)を参照してください。
