# 文書一覧

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[プロジェクトの説明](../README.ja.md)

## 利用ガイド

- [環境構築と初回ビルド](SETUP.ja.md)
- [Forest](../forest/README.ja.md)
- [腐り姫と外伝](../khime/README.ja.md)
- [Evermaiden](../evermaiden/README.ja.md)
- [CannonBall](../cannonball/README.ja.md)
- [霞外籠逗留記](../kagerou/README.ja.md)
- [SevenBridge の生成と言語パッチ](../sevenbridge/README.ja.md)
- [第三者資産とライセンス](../THIRD_PARTY_NOTICES.ja.md)

## 開発資料

- [開発計画](ROADMAP.ja.md)
- [作業規約](../AGENTS.ja.md)
- [新ゲーム移植と AI プロンプト](NEW_GAME_PORTING.ja.md)
- [共通テンプレート](../port_template/README.ja.md)
- [UI 資源の役割](../port_template/README.ja.md#ui-リソースの役割)
- [ソースの役割](SHARED_TEMPLATE_MIGRATION.ja.md)
- [初期設定](RSCRIPT_INITIALIZATION.ja.md)
- [組版](TEXT_WRAPPING.ja.md) · [Forest 字体](FOREST_FONT_ANALYSIS.ja.md)
- [Khime クリック](KHIME_CLICK_ANALYSIS.ja.md) · [画像効果](KHIME_EFFECT_ANALYSIS.ja.md) · [制御符](KHIME_TEXT_CONTROLS.ja.md)
- [効果 2](UPDATE_EFFECT2.ja.md)
- [原生色彩・描画モード](NATIVE_VISUAL_MODES.ja.md)
- [Evermaiden ランタイム](EVERMAIDEN_RUNTIME_GAPS.ja.md)
- [CannonBall 原動作](../cannonball/NATIVE_EFFECTS.ja.md)
- [Kagerou 原プログラム](../kagerou/NATIVE_EVIDENCE.ja.md)
- [SevenBridge 原プログラム](../sevenbridge/NATIVE_EVIDENCE.ja.md)

アドレスと結論は明記されたハッシュのビルドだけに適用し、全作品共通の仕様ではありません。

## 開発時の確認

ルートで実行し、SDK パスを置き換えます。

```bash
python3 -B tests/test_runtime.py
python3 -B tests/test_port_template.py
python3 -B tests/test_file_install.py
python3 -B tests/test_native_images.py
python3 -B tests/test_tsc_compiler.py
python3 -B tests/test_tsc_patches.py
python3 -B tests/test_shared_port.py /path/to/renpy-sdk --logic-only
git diff --check
```

文字は `tests/run_native_text_wrap.py`、タッチは `tests/run_touch_controls.py` に SDK を渡して検査します。作品別テストは各 README を参照してください。自動検査は実プレイを代替しません。
