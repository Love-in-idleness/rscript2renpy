# rscript2renpy

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

Build Ren'Py 8 projects from the TSC scripts and resources of CodeX RScript games you own.
The repository provides a compatibility runtime and game-specific builders, not a universal one-click converter.

## Getting started

You need Python 3, Pillow, the Ren'Py 8 SDK, and
[LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) to unpack and convert resources.

1. Install the tools using [Setup and first build](docs/SETUP.en.md).
2. Copy your legally owned game files and prepare resources and TSC scripts with LiarsoftTool.
3. Follow the game guide below to generate, check, and run the project.

Keep input resources separate from the output project. Builders read TSC, not GSC.

## Game guides

| Game | Supported version and build guide |
| --- | --- |
| Forest | [Build and language patches](forest/README.en.md) |
| Khime Kusaritop | [Build, language patches, and optional Khime Zero](khime/README.en.md) |
| Evermaiden | [Build and language patches](evermaiden/README.en.md) |
| CannonBall | [Build and language patches](cannonball/README.en.md) |
| SevenBridge | [Japanese edition](sevenbridge/README.en.md); no language patches yet |
| KagerouTouryuuki | [Bonus edition](kagerou/README.en.md); requires 「ハチポチ特典」 |

See each guide for features and limitations. Successful generation does not establish that every route works.
Language patches must be supplied separately.

## Development and feedback

- [Documentation](docs/README.en.md): user guides and technical references.
- [Porting a new game](docs/NEW_GAME_PORTING.en.md): adaptation steps and an AI prompt template.
- [Shared template](port_template/README.en.md): shared features, UI assets, and layout conventions.
- [Repository guidelines](AGENTS.en.md) · [Roadmap](docs/ROADMAP.en.md).

When reporting a problem, include the game version, build command, scene location, and full error or screenshot.
Do not upload game assets, saves, or keys publicly.

## License and assets

Code is licensed under the [MIT License](LICENSE). The repository does not include game scripts,
images, audio, video, or EXEs, except for shared cursors and application icons;
see [Third-party notices](THIRD_PARTY_NOTICES.en.md).

Fonts have separate terms: [Noto CJK](port_template/fonts/NotoSans.txt) and
[SimHei](port_template/fonts/SimHei-NOTICE.en.md). Check asset licenses before distributing generated projects.
