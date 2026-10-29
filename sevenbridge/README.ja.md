# SevenBridge

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[プロジェクトの説明](../README.ja.md)

## 概要

『SEVEN-BRIDGE』の日本語リソースと任意の中国語パッチから Ren'Py 8 プロジェクトを生成します。
原作の動作は日本語 `SBridge_jp.exe` を基準とし、言語パッチは別途用意します。

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

中国語パッチの `scr.xfl` と `grps.xfl` を別の作業ディレクトリへコピーし、LiarsoftTool で個別に展開・変換します。
翻訳スクリプトは **GBK** ですが、`grps.xfl` と内部 LWG のファイル名は引き続き **CP932** です。

```bash
liarsofttool --unpack-only -R -e gbk /path/to/patch-copy/scr.xfl
liarsofttool --unpack-only -R -e cp932 /path/to/patch-copy/grps.xfl
```

パッチ全体を GBK で変換すると、`nonbl/１` などの全角数字ファイル名を誤って復号します。
日本語原版は CP932 です。生成器は変換済みの `scr/*.tsc` を読み、EXE、GSC、アーカイブを直接処理しません。

パッチの `grps` 画像と `.meta.xml` を保持すると、メニュー、鑑賞、名前画像、右クリック画面も選択言語の素材を使用します。
完全な日本語原版をリソースの基礎として使います。変更のない素材はパッチ側に複製する必要はありません。

```bash
python3 sevenbridge/build_sevenbridge_rscript.py /path/to/prepared-sevenbridge /path/to/renpy-sevenbridge \
    --language jp --language zh=/path/to/patch-copy
```

`--language jp` は原文の表示名、`zh=...` は Text Settings で選べる中国語パッチを指定します。
パッチは原版の命令と対応付け、テキストを置き換え、必要に応じて字幕を追加します。物語の進行は日本語原版に従います。
翻訳のないテキストは日本語のままです。言語変更後は、物語を進めずに現在の台詞を更新します。

## 操作

原タイトルメニューを保持し、「環境設定」から文字設定を開きます。右クリックメニューには文字設定の入口を表示しません。ゲーム内制御バー、右クリック、セーブ・ロードは原画像と `.meta.xml` を使います。[共通 UI の役割](../port_template/README.ja.md#ui-リソースの役割)も参照してください。

共通文字設定で字体、サイズ、折返しを変更できます。進捗と鑑賞解放は独立した Ren'Py persistent に保存し、原ゲームのセーブを読んだり上書きしたりしません。

## 確認と制限

[主説明](../README.ja.md)に従って lint を実行し、画面、音、ルートを確認してください。`mov` 不足時は該当動画を再生できません。Android 実機と完全プレイは未検証です。[原プログラムの根拠](NATIVE_EVIDENCE.ja.md)を参照してください。
