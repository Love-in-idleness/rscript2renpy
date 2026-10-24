# SevenBridge

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[プロジェクトの説明](../README.ja.md)

## 概要

『SEVEN-BRIDGE』日本語資源から Ren'Py 8 工程を生成します。日本語 `SBridge_jp.exe` を根拠とし、中国語パッチは未接続です。

## リソースの準備

[環境構築](../docs/SETUP.ja.md)後、原本をコピーし、LiarsoftTool で再帰展開・変換します。現形式の `scr/*.tsc`、画像、`.meta.xml`、OGG、通常 PCM WAV を保持します。引数は `liarsofttool -h` を参照してください。

必要ディレクトリは `scr`、`grpe`、`grpo`、`grpo_bu`、`grpo_ex`、`grps`、`bgm`、`voice`、`wav`。音声の内部ディレクトリも展開してください。原 `mov` をコピーして `0002.mpg`、`0003.mpg`、`0004.mpg` を保持します。起動で `0002`、`0003/0004` はシナリオから再生します。

## 工程の生成

ルートで実行します。

```bash
python3 sevenbridge/build_sevenbridge_rscript.py /path/to/prepared-sevenbridge /path/to/renpy-sevenbridge
```

再生成前に手動変更を保存します。`--force` で異なる生成内容の上書きを許可できます。

## 言語パッチ

現在は日本語スクリプトのみです。他言語パッチは接続していません。

## 操作

原タイトルメニューを保持し、「環境設定」から既存 Text Settings を開きます。ゲーム内制御バー、右クリック、セーブ・ロードは原画像と `.meta.xml` を使います。[共通 UI の役割](../port_template/README.ja.md#ui-リソースの役割)も参照してください。

共通文字設定で字体、サイズ、折返しを変更できます。進捗と鑑賞解放は独立した Ren'Py persistent に保存し、原ゲームのセーブを読んだり上書きしたりしません。

## 確認と制限

[主説明](../README.ja.md)に従って lint を実行し、画面、音、ルートを確認してください。`mov` 不足時は該当動画を再生できません。Android 実機と完全プレイは未検証です。[原プログラムの根拠](NATIVE_EVIDENCE.ja.md)を参照してください。
