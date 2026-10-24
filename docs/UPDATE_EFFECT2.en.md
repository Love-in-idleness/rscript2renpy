# Developer reference: update effect 2

[中文](UPDATE_EFFECT2.zh.md) | [English](UPDATE_EFFECT2.en.md) | [Русский](UPDATE_EFFECT2.ru.md) | [日本語](UPDATE_EFFECT2.ja.md)

[Documentation](README.en.md)

On 2026-10-11 five user-supplied PE32 EXEs were inspected read-only. Effect 2 is ordered 4×4 pixel replacement,
not mosaic or enlargement followed by shrinking. The old Pixellate call remains commented out as requested, no longer executed.
Evidence is limited to these builds, not every engine version.

## Calls and table

All VAs. Follow update table entry 2 into mode 18's opaque branch; a matching table alone does not prove command semantics.

| Game / EXE | update entry 2 → transition | Pixel-copy routine | 16-WORD table |
| --- | --- | --- | --- |
| Forest / Forest.exe | `41c278[2] → 41c1be → 43ec10` | `431f00`; called by `42f393` | `463300` |
| Khime / KhimeDL.exe | `422290[2] → 4221d6 → 4482c0` | `439520`; called by `436983` | `46e100` |
| CannonBall / Cannonball.exe | `416404[2] → 41635d → 42bdb0` | `4207e0`; called by `41deb3` | `450070` |
| Evermaiden / startup_jp.exe | `43b5e4[2] → 43b50b → 4531d0` | `447077` opaque inline branch, `4471d0..4471f9` copy) | `4eb550` |
| Kagerou / kagerou.exe | `41e7e0[2] → 41e726 → 4504e0` | `4437d0`; called by `440c33` | `47ef38` |

Strength >> 4 selects the WORD; (x%4)+4*(y%4) selects the bit. One copies a new pixel, zero retains the previous pixel.
All five tables match:

```text
FFDF EFDF 6FDF 6FD7 6BD7 6BD6 6B56 6A56
2A56 2A52 0A52 0A12 0812 0810 0800 0000
```

Per-frame strength: floor((Step-frame)*255/Step), Step−1 frames then full new-frame commit.
Step=0 selects 10 at entry. Step=1 or Wait=0 has no nominal animation wait.
timeGetTime/GetTickCount differences are milliseconds, not centiseconds: nominal duration max(0,Step-1)*Wait/1000.
Native draw cost, Sleep and the strict > Wait loop's extra scheduling are not simulated.
Other effects' compatibility timing was not changed by this audit.

## Binary identity

| EXE | SHA-256 |
| --- | --- |
| Forest.exe | `8eb71d07304d362ec26cc47d93c6ef5854b5acadd7c9fe941755ad50820a3e56` |
| KhimeDL.exe | `2dfc7b78d32867716ab0406ccbf176b55a76faea1cb9c40feac25c90775222fe` |
| Cannonball.exe | `df4b5b6dffc7002370d0772869baaba551b08fca970e92609ca64b08174f89ba` |
| startup_jp.exe | `88820f28b8f770b486407e55dda28266c6fec42145192d5bc8ad5be21ab895af` |
| kagerou.exe | `f02998fae350945f4de4dc7eab47997e1e2d9b8aa43d49740a80aad893dcde9b` |

## Implementation and checks

runtime/effects.rpy stores verified masks/frame order; runtime/shaders.rpy chooses old/new pixels.
Compose on the original virtual canvas, then smoothly scale the complete result so window scale does not alter the grid.
runtime/03_rscript_gfx.rpy uses the shared effect.
tests/test_shared_port.py /path/to/renpy-sdk checks all stages for 1/3/10/16/32 steps, 4×4 orientation,
final frame, and 700×525 / 1000×750 windows against generated reference bitmaps in isolated Forest/Khime GL2 projects.
Modern/Kagerou isolation checks actual command dispatch and zero-step/zero-wait edges.
These are not frame-by-frame original-EXE comparisons. Android GPU, full routes and old saves need user validation.
