# rscript2renpy

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md)

`rscript2renpy` is a Ren'Py 8 compatibility runtime and porting tool for
CodeX RScript games, mainly from Liar-soft and raiL-soft.

Start with [environment setup and your first build](docs/SETUP.en.md).
For a game that is not yet supported, see the
[new-game porting guide and AI prompt](docs/NEW_GAME_PORTING.en.md).
See the [roadmap](docs/ROADMAP.en.md) for future work.

Apart from the shared cursor and application icons, this repository does not
include game scripts, artwork, audio, video or executables. Prepare resources
from a copy of the game you legally own and build the project yourself.

## Game guides

Each game directory documents its resource requirements, build commands and
language patches. Run command examples from the repository root.

| Game | Guide |
| --- | --- |
| Forest | [forest/README.en.md](forest/README.en.md) |
| Khime Kusaritop, with optional Khime Zero | [khime/README.en.md](khime/README.en.md) |
| Evermaiden | [evermaiden/README.en.md](evermaiden/README.en.md) |
| CannonBall | [cannonball/README.en.md](cannonball/README.en.md) |
| SevenBridge — Japanese version | [sevenbridge/README.en.md](sevenbridge/README.en.md) |
| KagerouTouryuuki — in development; requires the ハチポチ特典 add-on | [kagerou/README.en.md](kagerou/README.en.md) |

## Dependencies and resource preparation

Requires Python 3, Pillow and a Ren'Py 8 SDK. Resource extraction and conversion
require [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool).

Work on a copy of the game. Use LiarsoftTool to unpack archives, export TSC,
and prepare images and audio. Then run the game's build script.
Builders read TSC only; they do not process GSC.

## Shared template and output

Start a new port with the [shared template guide](port_template/README.en.md).
The common runtime is in `runtime/`, build tools and UI are in
`port_template/`, and game-specific code lives in each adapter directory.
See the [architecture guide](docs/SHARED_TEMPLATE_MIGRATION.en.md) for development.
See the [shared UI resource map](port_template/README.en.md#ui-resource-map)
for asset roles, `.meta.xml` layouts and the main menu's Text Settings entry.

Generated projects keep native resource folders: scripts in `game/scr/`,
images in `game/grp*/`, audio in `game/bgm/`, `game/voice/` and `game/wav/`,
and video in `game/mov/`. Runtime, shared UI and configuration go in
`game/engine/`; language resources go in `game/tl/<language>/`.

To install only the common runtime:

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

Existing files with different content are not overwritten automatically.
Game builders also install the shared cursor and Android startup notice.

## Checking a build and reporting issues

Run lint with your Ren'Py SDK:

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy-project lint
```

Then compare graphics, voices, choices and save/load behavior with the original
game. For an issue report, include the game version, build command, error or
screenshot, and the affected scene.
See the [documentation index](docs/README.en.md) for developer tests and references.

## License

Project code uses the [MIT License](LICENSE).
See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.en.md) for third-party code,
cursors, icons and fonts. Noto CJK uses
[SIL Open Font License 1.1](port_template/fonts/NotoSans.txt).
SimHei is separately licensed; see the
[font notice](port_template/fonts/SimHei-NOTICE.en.md).
