# Evermaiden port guide

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[Project guide](../README.en.md)

## Overview

Build a Ren'Py 8 project from your own Evermaiden resources. Adaptation remains in progress.
Run commands at the repository root; see [setup](../docs/SETUP.en.md).

## Prepare resources

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/Evermaiden
liarsofttool -R --unpack-only --gsc-to-tsc -e gbk /path/to/Evermaiden.zh
```

Convert original and patch in separate working copies. Keep scr/*.tsc, all grp* directories, .meta.xml,
bgm/voice/wav and mov. The Chinese example assumes GBK; choose the actual encoding for other versions.
Ordinary PCM WAV and original MPG need no further conversion.

## Generate the project

```bash
python3 evermaiden/build_evermaiden_rscript.py \
    /path/to/Evermaiden /path/to/renpy/Evermaiden
```

The destination can be created automatically. Back up manual edits and add --force when rebuilding.
This adapter uses a separate save directory from the old Evermaiden project and does not migrate its progress.

## Language patches

```bash
python3 evermaiden/build_evermaiden_rscript.py \
    /path/to/Evermaiden /path/to/renpy/Evermaiden \
    --language jp --language zh=/path/to/Evermaiden.zh
```

--language jp names the original; --language zh=directory adds a patch. Match original relative paths and provide only changed files.
This adapter replaces complete scenes, including the patch's branches, choices and added DLC scenes.
Missing translations use the original. Use trusted patches; avoid mid-game switching between structurally different languages.

## Use

Default canvas: 1280×720; text size 32; 28 full-width characters per line. Title settings control text and language;
in-game settings use original images. Startup plays 0002.mpg then 0001.mpg, not again when returning to the title.
Original scripts still control map choices, CG and music galleries.
Licensing for shared cursor, fonts and game icon: [notices](../THIRD_PARTY_NOTICES.en.md).

## Checks and limitations

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/Evermaiden lint
```

- Some effects, choice positions and font-selection appearance still differ from the original.
- Current samples lack voice/5/2703 referenced by scene 2320 and wav/2527 referenced by 4250: check assets first if silent.
- Full routes, gallery operation, save compatibility and Android still need actual checks.

Tests: tests/test_modern_port.py. Implementation and open issues: [runtime reference](../docs/EVERMAIDEN_RUNTIME_GAPS.en.md).
