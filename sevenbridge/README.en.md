# SevenBridge

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[Project overview](../README.en.md)

## Overview

Build a Ren'Py 8 project from Japanese SEVEN-BRIDGE resources and an optional Chinese patch.
Original behavior follows `SBridge_jp.exe`; language patches are supplied separately.

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

Copy the Chinese patch's `scr.xfl` and `grps.xfl` into a separate working directory, then convert them
separately with LiarsoftTool. The translated scripts use **GBK**, but member filenames in
`grps.xfl` and its nested LWG archives still use **CP932**:

```bash
liarsofttool --unpack-only -R -e gbk /path/to/patch-copy/scr.xfl
liarsofttool --unpack-only -R -e cp932 /path/to/patch-copy/grps.xfl
```

Do not convert the entire patch directory as GBK: full-width digit filenames such as `nonbl/１`
would be decoded incorrectly. The Japanese base uses CP932.
The builder reads converted `scr/*.tsc`, not EXE, GSC or archive files.

Keep the patch's `grps` images and `.meta.xml` so menus, galleries, nameplates and the right-click
interface can follow the selected language. The Japanese game remains the complete resource base;
the patch need not duplicate unchanged assets.

```bash
python3 sevenbridge/build_sevenbridge_rscript.py /path/to/prepared-sevenbridge /path/to/renpy-sevenbridge \
    --language jp --language zh=/path/to/patch-copy
```

`--language jp` labels the original language; `zh=...` adds a Chinese patch selectable in Text Settings.
Patches align with the original instructions, replacing text and optionally adding subtitles;
the Japanese script keeps control of the story flow. Missing text uses Japanese.
Changing language refreshes the current dialogue without advancing the story.

## Using the port

The original main menu is retained; its settings button opens Text Settings.
The right-click menu has no Text Settings link.
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
