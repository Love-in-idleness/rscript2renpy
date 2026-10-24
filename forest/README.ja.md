# Forest 移植ガイド

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[プロジェクトの説明](../README.ja.md)

## 概要

自身で用意した Forest から Ren'Py 8 工程を生成します。コマンドはルートで実行します。[初回構築](../docs/SETUP.ja.md)も参照してください。

## リソースの準備

作業コピーを展開・変換します。

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/Forest
```

`scr/*.tsc`、元の `grp*` と `.meta.xml`、`bgm/voice/wav`、`mov` を残します。タイトルに `grpe/9001` と `bgm/Track01.ogg`、起動動画に `0002.mpg` と `0001.mpg` が必要です。言語パッチは別コピーで実際の文字コードに合わせて変換します。

## 工程の生成

```bash
python3 forest/build_forest_rscript.py /path/to/Forest /path/to/renpy/Forest
```

出力先は自動作成できます。再生成は生成ファイルを上書きするので、手動変更を保存してください。旧生成器からの更新には新しい出力先を推奨します。

## 言語パッチ

```bash
python3 forest/build_forest_rscript.py /path/to/Forest /path/to/renpy/Forest \
    --language jp --language en=/path/to/Forest.en \
    --language zh=/path/to/Forest.zh
```

- `--language jp` は原版の言語名。省略時は `Original`。
- `--language zh=ディレクトリ` は切替可能なパッチ。複数指定できます。
- 原版と同じ相対パスで、変更したファイルのみ置きます。
- タグはメニューの表示名であり、文字コードを選択しません。

通常シーンでは既存台詞・選択肢・文字オブジェクトを翻訳し、音声だけの場面へ `*font` 字幕と待機・消去を追加できます。分岐や命令順は任意に変更しないでください。

`5000.tsc` は言語ごとの終了スクリプト全体を置き換え、再生中は戻る操作とメニューを禁止します。信頼できるパッチのみ使用し、構造が異なる言語を途中で切り替えないでください。

### Wiki 項目

パッチのルートに `keywords.json` を置きます。

```json
[["完全な文", "https://example.com/wiki", "文中で ^cg と ^cw に囲まれた語"]]
```

現在の言語の文に一致させます。Wiki は既定でオフ、中国語版のゲーム内右クリックメニューで切り替えます。タイトル設定にはスイッチがありません。

## 操作

- 起動動画はアプリ起動ごとに一度だけ再生し、タイトルへ戻っても再生しません。
- タイトル設定で字体、サイズ、行字数、行間、言語とシステム進捗のバックアップ・復元・消去を行えます。
- 既定サイズ 22、台詞は全角 19 字幅、文字オブジェクトは 20 字幅。
- `game/fonts/` に TTF、OTF、TTC を置くと字体を追加できます。
- ゲーム内の右クリックメニューで文字速度、音量、セーブ・ロードを操作します。

カーソル・アイコン・字体は[第三者資産の条件](../THIRD_PARTY_NOTICES.ja.md)を参照してください。

## 確認と制限

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/Forest lint
```

字幕、音声、画像選択、鑑賞からの復帰、セーブ・ロードを実際に確認してください。旧セーブ、言語切替、Android は各資源版での検証が必要です。

開発テスト: `tests/test_forest_validation.py`、`tests/test_forest_builder.py`、`tests/test_shared_port.py`。[共通文字規則](../docs/TEXT_WRAPPING.ja.md)も参照してください。
