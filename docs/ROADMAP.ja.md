# 開発計画

[中文](ROADMAP.zh.md) | [English](ROADMAP.en.md) | [Русский](ROADMAP.ru.md) | [日本語](ROADMAP.ja.md)

[メインガイド](../README.ja.md)

## 継続的な改善

対応ゲームの互換性と動作確認を進め、共通ランタイムの修正を優先します。
対応版、機能、制限は各ゲームのガイドを参照してください。

リソースの展開・変換は独立した LiarsoftTool が担当し、
本プロジェクトは TSC からの Ren'Py 生成と実行に集中します。

## 長期目標：実験的な `--pure-renpy`

TSC を通常の Ren'Py 文へ変換する独立バックエンドを計画しています。
必要に応じて標準 Python、screen、ATL を使い、生成物には TSC パーサーや命令ディスパッチャーを含めません。

未実装であり、現在 `--pure-renpy` オプションはありません。
命令範囲、セーブ互換、移行方法は開発時に決定します。

TSC 編集ツールは [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool/blob/master/docs/ROADMAP.md) で管理します。
