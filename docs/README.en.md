# Documentation

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[Project guide](../README.en.md)

## User guides

- [Setup and first build](SETUP.en.md)
- [Forest](../forest/README.en.md)
- [Khime and optional side story](../khime/README.en.md)
- [Evermaiden](../evermaiden/README.en.md)
- [CannonBall](../cannonball/README.en.md)
- [KagerouTouryuuki](../kagerou/README.en.md)
- [SevenBridge build and language patches](../sevenbridge/README.en.md)
- [Asset provenance and licensing](../THIRD_PARTY_NOTICES.en.md)

## Developer references

- [Roadmap](ROADMAP.en.md)
- [New games and AI prompt](NEW_GAME_PORTING.en.md)
- [Shared template and UI assets](../port_template/README.en.md)
- [Source ownership](SHARED_TEMPLATE_MIGRATION.en.md)
- [Initialization](RSCRIPT_INITIALIZATION.en.md)
- [Text layout](TEXT_WRAPPING.en.md) · [Forest fonts](FOREST_FONT_ANALYSIS.en.md)
- [Khime clicks](KHIME_CLICK_ANALYSIS.en.md) · [Effects](KHIME_EFFECT_ANALYSIS.en.md) · [Text controls](KHIME_TEXT_CONTROLS.en.md)
- [Effect 2](UPDATE_EFFECT2.en.md)
- [Native color and drawing modes](NATIVE_VISUAL_MODES.en.md)
- [Evermaiden runtime](EVERMAIDEN_RUNTIME_GAPS.en.md)
- [CannonBall](../cannonball/NATIVE_EFFECTS.en.md)
- [Kagerou](../kagerou/NATIVE_EVIDENCE.en.md)
- [SevenBridge](../sevenbridge/NATIVE_EVIDENCE.en.md)
- [Working agreements](../AGENTS.en.md)

Addresses and conclusions apply only to the specified file hashes, not every game engine.

## Development checks

From the repository root, using your SDK:

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

Text/touch changes additionally use tests/run_native_text_wrap.py / tests/run_touch_controls.py, passing the SDK directory.
Game-specific tests are in each guide. Automated checks do not replace gameplay.
