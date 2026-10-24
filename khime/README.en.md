# Khime Kusaritop port guide

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[Project guide](../README.en.md)

## Overview

Build a Ren'Py 8 project from your own Kusarihime resources, optionally including
`帰省 ～jamais vu～`. Run commands at the repository root. See [setup](../docs/SETUP.en.md).

## Prepare resources

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/Khime
```

Keep scr/*.tsc, grp* directories, .meta.xml, bgm/voice/wav and mov. Extract Ogg wrapped in WAV;
ordinary PCM WAV and original MPG can be used directly. Convert patches separately in their actual encoding.

## Generate the project

```bash
python3 khime/build_khime_rscript.py /path/to/Khime /path/to/renpy/Khime
```

The generator can create the destination. Back up manual edits and add --force when rebuilding.
Use a fresh output directory when upgrading from older generators.

## Language patches

```bash
python3 khime/build_khime_rscript.py /path/to/Khime /path/to/renpy/Khime \
    --language jp --language zh=/path/to/Khime.zh
```

--language jp names the original; --language zh=directory adds a patch. Use original relative paths and provide only changed TSC, images and audio.
Translate dialogue, appended text, choices and text objects; subtitles and associated wait/clear instructions are allowed.
Ordinary patches must not arbitrarily change story logic. Missing scenes use the original.
LiarsoftTool normalizes CodeX BMP alpha before generation; the generator copies images directly.

### Optional side story

```bash
python3 khime/build_khime_rscript.py /path/to/Khime /path/to/renpy/Khime \
    --language jp --language zh=/path/to/Khime.zh \
    --khime-zero /path/to/Khime_zero \
    --khime-zero-language zh=/path/to/Khime_zero.zh
```

This integrates scr/2001.tsc, not the side story's separate title. Its entrance appears on the original main title
once unlocked. Its resources do not overwrite same-number main-game images. Without a side-story patch, original text is used.

## Use

Title settings control font, size, line length, spacing, language and system progress. Defaults: size 29,
21 character widths per dialogue line. Reading speed and sound are in in-game settings.
Startup videos play once per application launch, not on returning to the title.
Licensing for the shared cursor, fonts and icon: [third-party notices](../THIRD_PARTY_NOTICES.en.md).

## Checks and limitations

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/Khime lint
```

Some effects and numeric controls remain incomplete; side-story BGM has no fading yet.
Check full routes, galleries, subtitles, audio and old saves; Android needs separate checks.
Tests: tests/test_khime_builder.py, tests/test_khime_zero.py, tests/test_shared_port.py.
Engine evidence: [developer references](../docs/README.en.md).
