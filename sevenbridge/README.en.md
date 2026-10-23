# SevenBridge

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md)

[Project overview](../README.en.md)

## Overview

Build a Ren'Py 8 project from the Japanese SEVEN-BRIDGE resources.
This adapter targets `SBridge_jp.exe`; Chinese patches are not supported yet.

## Prepare resources

Follow [environment setup](../docs/SETUP.en.md). Work on a copy of your game and
use LiarsoftTool to unpack recursively and convert resources. Keep current
`scr/*.tsc`, images, `.meta.xml`, OGG and ordinary PCM WAV files.
See `liarsofttool -h` for conversion options.

Required directories: `scr`, `grpe`, `grpo`, `grpo_bu`, `grpo_ex`, `grps`,
`bgm`, `voice` and `wav`. Unpack nested voice archives too.
Copy the original `mov` directory into the resource working copy, including
`0002.mpg`, `0003.mpg` and `0004.mpg`. Startup plays `0002`;
the scenarios call `0003/0004`.

## Generate the project

Run from the repository root:

```bash
python3 sevenbridge/build_sevenbridge_rscript.py /path/to/prepared-sevenbridge /path/to/renpy-sevenbridge
```

Back up manual edits before rebuilding. `--force` replaces differing generated files.

## Language patches

Only Japanese scenarios are currently supported.

## Using the port

The original main menu is retained; its settings button opens Text Settings.
In-game controls, the right-click menu and save/load
screens use original artwork with `.meta.xml` layouts. See the
[shared UI resource map](../port_template/README.en.md#ui-resource-map) for each directory's role.
Shared text settings let you change fonts, size and wrapping.
Progress and gallery unlocks use separate Ren'Py persistent data and do not
read or overwrite native saves.

## Checks and limitations

Run Ren'Py lint as described in the [main guide](../README.en.md), then check
graphics, audio and routes in the game. Missing `mov` files cannot be played.
Full playthroughs and Android devices still require verification.
See [native evidence](NATIVE_EVIDENCE.en.md) for the supported executable.
