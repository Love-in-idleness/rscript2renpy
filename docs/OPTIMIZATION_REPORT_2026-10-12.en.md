# Development record: safety and shared layers, 2026-10-12

[中文](OPTIMIZATION_REPORT_2026-10-12.zh.md) | [English](OPTIMIZATION_REPORT_2026-10-12.en.md) | [Русский](OPTIMIZATION_REPORT_2026-10-12.ru.md)

[Documentation](README.en.md)

Historical record, not installation instructions. Current use: [project guide](../README.en.md).

## Scope

| Repository | Work |
| --- | --- |
| LiarsoftTool | GSC/TXT validation, strict encodings, shared CLI/GTK conversion |
| Both | File-level safe writes, input/output directory checks |
| rscript2renpy | Fewer duplicate copies, shared script/config installation |

Repositories stayed independent. Instruction semantics were unchanged; no build database or plugin framework was added.

## Results at that date

- Linux CTest: 11 passed; Windows/Wine: 10 passed.
- Python shared-layer and minimal Forest/Khime projects passed.
- Forest lint passed; Khime retained three existing duplicate persistent-default declarations.
- 444 valid Forest/Khime GSC/TXT outputs matched the previous implementation.

These results describe that date, not the current version or full-game acceptance.

## Maintenance

File-level protection is not a whole-project transaction; rebuild after interruption.
Checks: tests/test_file_install.py, tests/test_shared_port.py and LiarsoftTool CTest.
Choose tests for actual changes; do not append test logs to user guides.
