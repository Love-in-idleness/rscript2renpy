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

The `forest` branch contains a Forest-specific generator that consumes assets
extracted from a legally obtained copy of Forest and writes a separate Ren'Py
project.

## License

Project code is available under the [MIT License](LICENSE). See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for incorporated code and the
separately licensed font on the `forest` branch.
