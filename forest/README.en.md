# Forest port guide

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md)

[Project overview](../README.en.md)

## Overview

This adapter builds a Ren'Py 8 project from your own Forest resources.
Run examples from the repository root. See [setup](../docs/SETUP.md) for dependencies.

## Prepare resources

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/Forest
```

Keep `scr/*.tsc`, native `grp*` image folders and their `.meta.xml` files,
audio under `bgm/voice/wav`, and videos under `mov`.
The title requires `grpe/9001` and `bgm/Track01.ogg`.
Startup videos are `0002.mpg` and `0001.mpg`.
Prepare each language patch separately, using the encoding of its source files.

## Build

```bash
python3 forest/build_forest_rscript.py /path/to/Forest /path/to/renpy/Forest
```

The builder creates the output directory. Rebuilding overwrites generated files;
back up manual changes first. Use a new output directory when upgrading from an old builder.

## Language patches

```bash
python3 forest/build_forest_rscript.py /path/to/Forest /path/to/renpy/Forest \
    --language jp --language en=/path/to/Forest.en \
    --language zh=/path/to/Forest.zh
```

`--language jp` names the base language, otherwise labelled `Original`.
`--language NAME=DIR` adds a selectable language and may be repeated.
Include only changed files, using their original relative paths.
Language labels do not select file encodings.

Ordinary scenes support translated dialogue, choices and text objects.
Voice-only passages may add `*font` subtitles with related waits and clears;
arbitrary changes to story logic or command order are not supported.

`5000.tsc` uses a complete ending script for each language. Rollback and menus
are disabled during this scene. Use trusted patches and avoid switching between
different story structures during a playthrough.

For Wiki links, put `keywords.json` in the patch root, using entries shaped as
`["complete sentence", "https://example.com/wiki", "marked word"]`.
The sentence must match the current language and the word must be marked with
`^cg…^cw`. Wiki is off by default; toggle it in the Chinese in-game right-click menu,
not title settings.

## Settings and checks

Startup videos play once per launch. Title settings provide fonts, size, line
length, spacing, language and system-progress backup, restore and clear.
Dialogue defaults to size 22 and 19 full-width characters per line; text objects
default to 20. Add TTF, OTF or TTC files to `game/fonts/` for more fonts.
Use the in-game menu for text speed, audio and saving/loading.

Run lint as shown above, then check subtitles, voices, image choices, gallery
returns and saves in actual gameplay. Old saves, language switching and Android
need testing with your resource version.
See [third-party notices](../THIRD_PARTY_NOTICES.md) for asset licenses.
