# CannonBall port guide

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[Project guide](../README.en.md)

## Overview

Build a Ren'Py 8 project from your own CannonBall resources. Adaptation remains in progress.
Run commands at the repository root; see [setup](../docs/SETUP.en.md).

## Prepare resources

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/CannonBall
liarsofttool -R --unpack-only --gsc-to-tsc -e gbk /path/to/CannonBall.zh
```

Convert original and patch separately. Keep scr/*.tsc, all grp* image directories, bgm/voice/wav and available mov videos.
Title assets: grpe/0901 and bgm/Track01.wav. Ordinary PCM WAV and original MPG work directly;
extract Ogg wrapped in WAV. The Chinese example assumes GBK; use actual encoding for other versions.

## Generate the project

```bash
python3 cannonball/build_cannonball_rscript.py \
    /path/to/CannonBall /path/to/renpy/CannonBall
```

The destination can be created. Back up manual edits and add --force when rebuilding.
Ordinary generation does not require the original EXE.

## Language patches

```bash
python3 cannonball/build_cannonball_rscript.py \
    /path/to/CannonBall /path/to/renpy/CannonBall \
    --language jp --language zh=/path/to/CannonBall.zh
```

--language jp names the original; --language zh=directory adds a patch. Follow original relative paths with changed files only.
Complete scenes are replaced, preserving the patch's branches and new scenes. The current Chinese patch has a different story flow;
the generator does not automatically restore Japanese flow. Use trusted patches and avoid mid-game switching across different structures.

## Use

Settings, save/load, text choices and controls use original images. Racing disables rollback and saving;
normal permissions return afterwards. Startup plays 0002.mpg then 0001.mpg, not again on return to the title.
Licensing for shared cursor, fonts and game icon: [notices](../THIRD_PARTY_NOTICES.en.md).

## Checks and limitations

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/CannonBall lint
```

- History-page appearance is not completely reproduced.
- Some transitions and music fades may differ.
- Chinese patch flow provenance, cross-language saves, full racing, combat and story routes require separate checks.
- Android requires device testing.

Tests: tests/test_cannonball_port.py. Engine evidence and effects: [developer reference](NATIVE_EFFECTS.en.md).
