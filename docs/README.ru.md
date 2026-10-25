# Документация

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

## Руководства

- [Среда и первая сборка](SETUP.ru.md)
- [Forest](../forest/README.ru.md)
- [Khime и дополнение](../khime/README.ru.md)
- [Evermaiden](../evermaiden/README.ru.md)
- [CannonBall](../cannonball/README.ru.md)
- [KagerouTouryuuki](../kagerou/README.ru.md)
- [SevenBridge, японская версия](../sevenbridge/README.ru.md)
- [Сторонние ресурсы и лицензии](../THIRD_PARTY_NOTICES.ru.md)

## Разработка

- [План развития](ROADMAP.ru.md)
- [Новая игра и запрос для ИИ](NEW_GAME_PORTING.ru.md)
- [Общий шаблон и назначение UI-ресурсов](../port_template/README.ru.md)
- [Локальные пути](LOCAL_WORKFLOW.ru.md)
- [Правила работы](../AGENTS.ru.md)

Технические справочники:

- [Распределение исходников](SHARED_TEMPLATE_MIGRATION.ru.md)
- [Инициализация](RSCRIPT_INITIALIZATION.ru.md)
- [Вёрстка текста](TEXT_WRAPPING.ru.md), [шрифты Forest](FOREST_FONT_ANALYSIS.ru.md)
- [Khime: клики](KHIME_CLICK_ANALYSIS.ru.md), [эффекты](KHIME_EFFECT_ANALYSIS.ru.md), [управление текстом](KHIME_TEXT_CONTROLS.ru.md)
- [Эффект 2](UPDATE_EFFECT2.ru.md), [runtime Evermaiden](EVERMAIDEN_RUNTIME_GAPS.ru.md)
- [Исходные режимы цвета и рисования](NATIVE_VISUAL_MODES.ru.md)
- [CannonBall](../cannonball/NATIVE_EFFECTS.ru.md), [Kagerou](../kagerou/NATIVE_EVIDENCE.ru.md)
- [Изменения общего слоя от 2026-10-12](OPTIMIZATION_REPORT_2026-10-12.ru.md)

[Анализ SevenBridge](../sevenbridge/NATIVE_EVIDENCE.ru.md).
Адреса и выводы действуют только для файлов с указанными хешами, не являются
спецификацией всех игр.

## Проверки разработчика

Из корня репозитория, со своим SDK:

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

Изменения текста и сенсорного управления проверяются соответственно
`tests/run_native_text_wrap.py` и `tests/run_touch_controls.py`; аргумент — каталог SDK.
Тесты отдельных игр перечислены в их README. Автоматические проверки не заменяют прохождение.
