# 霞外籠逗留記 移植ガイド

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[プロジェクトの説明](../README.ja.md)

## 概要

自身で用意した『霞外籠逗留記』から Ren'Py 8 工程を生成します。**「ハチポチ特典」適用後のみ対応**し、適用前の旧版には対応しません。開発中です。例はルートで実行します。[環境構築](../docs/SETUP.ja.md)を参照してください。

## リソースの準備

特典適用後の作業コピーで変換します。

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/KagerouTouryuuki
```

原 `kagerou.exe`、`scr/*.tsc`、全 `grp*` と `.meta.xml`、`bgm/voice/wav`、`mov` を保持します。中国語パッチは別コピーで変換します。対応版 EXE はレイアウト読取に必要ですが、実行・出力へのコピーはしません。入力にない場合は `--exe /path/to/kagerou.exe` で指定できます。

## 工程の生成

```bash
python3 kagerou/build_kagerou_rscript.py \
    /path/to/KagerouTouryuuki /path/to/renpy/KagerouTouryuuki
```

出力先は自動作成できます。再生成前に手動変更を保存し、`--force` を指定します。

## 言語パッチ

```bash
python3 kagerou/build_kagerou_rscript.py \
    /path/to/KagerouTouryuuki /path/to/renpy/KagerouTouryuuki \
    --language jp --language zh=/path/to/KagerouTouryuuki_CHS
```

特典版に対応したパッチを使い、元の相対パスで変更ファイルのみ置きます。シーン全体を置換し、不足する訳は現在の原版を使います。

## 操作

既定は縦書きです。文字パネルで縦横、サイズ、位置、影、字体を切り替えられます。方向変更で選択サイズは変えません。Back とホイール上はともにロールバックします。

人物別音声スイッチは原画像の設定ページです。CG・シーン・音楽鑑賞は特典版のスクリプトと資源を使います。動画はアプリ起動時のみで、不足動画はスキップします。

## 確認と制限

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/KagerouTouryuuki lint
```

長大段落内の改ページ、一部転換、原記録ページの外観、原セーブ取込は未完成です。組版、音声、鑑賞、全ルート、Android を実際に確認してください。

開発検査: `tests/test_kagerou_native.py`、`tests/test_kagerou_builder.py`、`tests/run_kagerou_port.py`。[開発根拠](NATIVE_EVIDENCE.ja.md)も参照してください。
