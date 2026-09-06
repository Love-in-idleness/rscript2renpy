# rscript2renpy

Reusable Ren'Py runtime for scripts lowered from Liar-soft/raiL-soft CodeX
RScript games.

The current experimental release is **0.1.0**. Runtime behavior depends on the
source game's CodeX dialect, so each new game still requires verification.

This repository contains engine-side support only. It does not contain game
scripts, images, audio, movies, fonts, executables, or other proprietary game
data.

## Install the runtime

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

The command copies the sixteen runtime modules into the project's `game/`
directory. Existing different files are not overwritten unless `--force` is
specified.

These modules provide the register model, custom RScript statements, drawing,
audio, text, effects, and shaders. A game adapter must still provide its own
labels, screens, asset naming rules, and converted scenario files.

## Validation

```bash
python3 -B tests/test_runtime.py
/path/to/renpy.sh /path/to/project lint
```

Runtime behavior depends on the source game's CodeX dialect. Unsupported
opcodes and rendering modes must be implemented and verified per game.

## Forest branch

The `forest` branch contains a Forest-specific generator. It never downloads or
bundles proprietary Forest data. Prepare an extracted resource directory with
at least `scr/`, `grps/`, the other `grp*` directories, and converted OGG audio;
create an empty Ren'Py project; then run:

```bash
python3 forest/build_forest_rscript.py \
    /path/to/forest-resources /path/to/renpy-project
```

The generator requires Python 3, Pillow, `ffmpeg` for MPG conversion, and the
experimental Forest GSC decoder included on this branch. Run LiarsoftTool's
recursive unpack/conversion first when the resource tree still contains packed
archives, WCG/LIM images, or embedded-Ogg WAV files.

The generator only reads the directory supplied by the user. It expects
`scr/*.gsc`, PNG files under the `grp*` directories, OGG files under `wav/`,
`bgm/`, and `voice/`, and `mov/0001` plus `mov/0002` in MPG or WebM form. It
does not locate, extract, download, or modify an installed copy of the game.

The Noto Sans CJK JP font on this branch is distributed under the SIL Open Font
License 1.1 in `forest/fonts/NotoSans.txt`.

## License

Project code is available under the [MIT License](LICENSE). See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for incorporated code and the
separately licensed font on the `forest` branch.
