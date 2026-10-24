# 開発計画

[中文](ROADMAP.zh.md) | [English](ROADMAP.en.md) | [Русский](ROADMAP.ru.md) | [日本語](ROADMAP.ja.md)

[プロジェクトの説明](../README.ja.md)

## 現在の方針

- SevenBridge 日本語移植の生成・実行確認を先に完了し、他作品へ広げます。
- 共通機能はテンプレート・ランタイムへ、作品差分は本作 EXE とスクリプトを根拠に実装します。
- 中国語、英語、ロシア語、日本語の文書を機能と同期します。
- LiarsoftTool と独立し、展開、文字コード、画像・音声変換はそちらが担当します。

## 長期計画: 実験的 `--pure-renpy`

将来、TSC のシナリオをネイティブ Ren'Py 文に変換する別バックエンドを追加します。標準 Python、screen、ATL は利用できますが、生成工程に TSC パーサーや実行時命令ディスパッチを持ち込みません。

今回は実装せず、仮のスイッチも追加しません。現在の生成器は RScript 互換ランタイムを使用します。命令範囲、セーブ互換、移行方法はその段階で決めます。

グラフィカル TSC エディターは [LiarsoftTool の長期計画](https://github.com/Love-in-idleness/LiarsoftTool/blob/master/docs/ROADMAP.ja.md)です。
