# KagerouTouryuuki port guide

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md)

[Project guide](../README.en.md)

## Overview

Build a Ren'Py 8 project from your own 霞外籠逗留記 resources.
Only versions with ハチポチ特典 installed are supported, not the older base game.
Adaptation remains in progress. Run commands at the repository root; see [setup](../docs/SETUP.en.md).

## Prepare resources

Convert a working copy after installing the bonus:

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/KagerouTouryuuki
```

Keep original kagerou.exe, scr/*.tsc, all grp* directories, .meta.xml, bgm/voice/wav and mov.
Convert Chinese patches in a separate copy. The generator reads layouts from a supported EXE;
it neither executes nor copies it. If absent from the resource copy, specify --exe /path/to/kagerou.exe.

## Generate the project

```bash
python3 kagerou/build_kagerou_rscript.py \
    /path/to/KagerouTouryuuki /path/to/renpy/KagerouTouryuuki
```

The destination can be created. Back up manual edits and add --force when rebuilding.

## Language patches

```bash
python3 kagerou/build_kagerou_rscript.py \
    /path/to/KagerouTouryuuki /path/to/renpy/KagerouTouryuuki \
    --language jp --language zh=/path/to/KagerouTouryuuki_CHS
```

Patches must match the bonus version. Follow original relative paths and provide only changed files.
Language packs replace complete scenes; missing translations use the current original.

## Use

Vertical layout is default. The text panel switches direction, font size, position, shadow and font.
Direction changes keep the selected size. Back and scrolling upward both roll back.
Character-voice switches are on the original image-based settings page. CG, scene and music galleries use bonus scripts/resources.
Startup videos play only on application launch; missing videos are skipped.

## Checks and limitations

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/KagerouTouryuuki lint
```

Intra-paragraph pagination of very long passages, some transitions, original history appearance and native-save import remain unfinished.
Check actual layout, voice, galleries, full routes and Android.
Tests: tests/test_kagerou_native.py, tests/test_kagerou_builder.py, tests/run_kagerou_port.py.
Original-program evidence: [developer reference](NATIVE_EVIDENCE.en.md).
