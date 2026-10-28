# rscript2renpy

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

所有する CodeX RScript ゲームの TSC とリソースから Ren'Py 8 プロジェクトを生成します。
互換ランタイムとゲーム別の生成器を提供するもので、すべてのゲームに使える自動変換器ではありません。

## はじめに

Python 3、Pillow、Ren'Py 8 SDK、および展開・変換用の
[LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) が必要です。

1. [環境設定と初回ビルド](docs/SETUP.ja.md)に従ってツールを用意します。
2. 正規に所有するゲームをコピーし、LiarsoftTool でリソースと TSC を準備します。
3. 以下のゲーム別ガイドに従い、プロジェクトを生成・確認・実行します。

入力と出力は別のディレクトリにしてください。生成器が読むのは TSC で、GSC は処理しません。

## ゲーム別ガイド

| ゲーム | 対応版と生成方法 |
| --- | --- |
| Forest | [生成と言語パッチ](forest/README.ja.md) |
| Khime Kusaritop | [生成、言語パッチ、任意の Khime Zero](khime/README.ja.md) |
| Evermaiden | [生成と言語パッチ](evermaiden/README.ja.md) |
| CannonBall | [生成と言語パッチ](cannonball/README.ja.md) |
| SevenBridge | [生成と言語パッチ](sevenbridge/README.ja.md) |
| KagerouTouryuuki | [特典版](kagerou/README.ja.md)。「ハチポチ特典」の適用が必要 |

機能と制限は各ガイドを参照してください。生成成功は全ルートの動作確認を意味しません。
言語パッチは利用者が別途用意します。

## 開発と報告

- [ドキュメント](docs/README.ja.md)：利用ガイドと技術資料。
- [新しいゲームの移植](docs/NEW_GAME_PORTING.ja.md)：作業手順と AI 向けプロンプト。
- [共通テンプレート](port_template/README.ja.md)：共通機能、UI 素材、配置規則。
- [作業規約](AGENTS.ja.md) · [開発計画](docs/ROADMAP.ja.md)。

不具合報告にはゲームの版、生成コマンド、場面、完全なエラーまたは画像を添えてください。
ゲーム素材、セーブ、鍵は公開しないでください。

## ライセンスと素材

コードは [MIT License](LICENSE) です。共通カーソルとアプリアイコンを除き、
ゲームのシナリオ、画像、音声、動画、EXE は含みません。
出典は[第三者に関する通知](THIRD_PARTY_NOTICES.ja.md)を参照してください。

フォントには別の条件があります：[Noto CJK](port_template/fonts/NotoSans.txt)、
[SimHei](port_template/fonts/SimHei-NOTICE.ja.md)。生成物を配布する前に素材の権利を確認してください。
