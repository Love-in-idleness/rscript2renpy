# rscript2renpy

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

`rscript2renpy` は CodeX RScript のゲーム（主に Liar-soft / raiL-soft）向けの Ren'Py 8 互換ランタイムと移植ツールです。

初めての方は[環境構築](docs/SETUP.ja.md)、未対応作品の開発は[新ゲーム移植ガイドと AI プロンプト](docs/NEW_GAME_PORTING.ja.md)、今後の目標は[開発計画](docs/ROADMAP.ja.md)を参照してください。

共通カーソルと各ゲームのアプリアイコン以外に、ゲームのシナリオ、画像、音声、動画、実行ファイルは含みません。正当に入手したゲームファイルから各自でリソースを準備し、ビルドしてください。

## ゲーム別ガイド

各作品の必要リソース、生成コマンド、言語パッチの説明は個別ディレクトリにあります。例はリポジトリのルートで実行します。

| 作品 | ガイド |
| --- | --- |
| Forest | [forest/README.ja.md](forest/README.ja.md) |
| 腐り姫（オプションの帰省を含む） | [khime/README.ja.md](khime/README.ja.md) |
| Evermaiden | [evermaiden/README.ja.md](evermaiden/README.ja.md) |
| CannonBall | [cannonball/README.ja.md](cannonball/README.ja.md) |
| SevenBridge（日本語版） | [sevenbridge/README.ja.md](sevenbridge/README.ja.md) |
| 霞外籠逗留記（対応作業中。「ハチポチ特典」適用後のみ） | [kagerou/README.ja.md](kagerou/README.ja.md) |

## 依存関係とリソースの準備

Python 3、Pillow、Ren'Py 8 SDK が必要です。展開・変換には [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) を使います。

ゲームをコピーしてから、LiarsoftTool で展開、TSC 出力、画像・音声変換を行い、各作品の生成スクリプトを実行します。生成器は TSC のみを読み、GSC は扱いません。

## 共通テンプレートと出力

新しい移植は[共通テンプレート](port_template/README.ja.md)から始めます。ランタイムは `runtime/`、ビルドと GUI は `port_template/`、作品差分は各アダプターにあります。[ソースの役割分担](docs/SHARED_TEMPLATE_MIGRATION.ja.md)と[UI リソースの役割](port_template/README.ja.md#ui-リソースの役割)も参照してください。

生成工程は原ディレクトリ名を保持します。シナリオは `game/scr/`、画像は `game/grp*/`、音声は `game/bgm/`・`game/voice/`・`game/wav/`、動画は `game/mov/`。共通実装と設定は `game/engine/`、言語リソースは `game/tl/<言語>/` です。

ランタイムだけを導入する場合:

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

異なる内容の既存ファイルは無断で上書きしません。各生成器は共通カーソルと Android 起動説明を含めます。

## 確認と報告

生成後に Ren'Py SDK の lint を実行します。

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy-project lint
```

原ゲームと画面、音声、選択肢、セーブ・ロードを比較してください。問題を報告する際はゲーム版、ビルドコマンド、エラーや画像、対象シーンを添えてください。[文書一覧](docs/README.ja.md)に開発テストと技術資料があります。

## ライセンス

コードは [MIT License](LICENSE) です。第三者コード、カーソル、アイコン、字体は[第三者資産とライセンス](THIRD_PARTY_NOTICES.ja.md)を参照してください。Noto CJK は [SIL Open Font License 1.1](port_template/fonts/NotoSans.txt)、SimHei は[別の条件](port_template/fonts/SimHei-NOTICE.ja.md)です。
