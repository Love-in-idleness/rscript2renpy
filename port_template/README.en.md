# Shared RScript port template

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[Project overview](../README.en.md) · [New-game guide](../docs/NEW_GAME_PORTING.en.md)

This directory provides shared script compilation, project assembly and UI for new adapters. It is not a one-click converter for every RScript game.

## Input and output

Prepare resources with LiarsoftTool:

- Current-format `scr/*.tsc`.
- PNG, WebP, JPG, BMP and BMP-format MSK masks.
- Playable OGG or ordinary PCM WAV.
- Original MPG movies and image `.meta.xml` files.

LiarsoftTool normalizes CodeX BMP inverse alpha. This project copies BMP/MSK directly, without converting them to PNG.

Generated scripts live in `game/scr/`, runtime/UI in `game/engine/`. Media keep their original directory names. Language assets go in `game/tl/<language>/`.

## Start an adapter

1. Create a game directory without forking `runtime/` or `port_template/`.
2. Confirm this game's dialect and resources, then use the shared TSC compiler.
3. Assemble with `assemble_port`; keep game differences in the adapter's `game/*.rpy`.
4. Provide a build command accepting resource/output directories and `--help`.
5. Document supported versions, preparation, generation, patches and limitations in the game README.

Check manual changes before overwriting projects. Fix generators/templates, not just generated output.

## Shared features

| Feature | Purpose |
| --- | --- |
| Text | Dialogue, append, text objects, controls, ruby and wrapping |
| Settings | Font, size, line length, spacing, language and progress backups |
| Native artwork UI | Settings, choices, controls, save/load |
| Audio | BGM, effects, voices, replay and auto-advance |
| Language packages | Text patches, subtitle insertion and game-specific whole-scene replacement |
| Android | Touch controls, screenshots, icons and project startup notice |

Use metadata for layout first. Naming and button behavior need adaptation: filenames identify likely roles, while actions, states and availability must be checked against this game's scripts or EXE. Save slots can use chapter images and saveconf components.

## UI resource map

Check these resources before implementing screens. This is a shared checklist; verify missing directories or different naming against the particular game's assets.

| Path | Role |
| --- | --- |
| `grps/dt*` | Save-game images |
| `grps/nonbl/` | Number images for menu pagination |
| `grps/compane/` | In-game control bar; filenames identify functions |
| `grps/confscrn/` | In-game right-click menu |
| `grps/savescrn/` | Save/load screen artwork |
| Each directory's `.meta.xml` | Image positions and canvas layout; retain original sizes too |

Keep the original main menu. Its environment/settings button opens the existing Text Settings (`rscript_title_preferences`), not a replacement text-only title. In-game controls, right-click menus and save/load retain native artwork.

Read metadata rather than guessing from screenshots or centering everything. dt* are not story backgrounds/portraits, and nonbl is not dialogue. Treat each save slot as a complete saveconf component: preview, numbers, date, icons and selection mask. A screenshot alone does not replace it. Wire each control to its own action; check selected, idle and hover states separately.

Startup movies default to `0002.mpg → 0001.mpg`, once per launch. Adapters can set `rscript_boot_movies`.

## Game differences

For each game verify entries/jumps, registers, coordinates/layers, audio IDs, text rules, menus, save/load, rollback, persistence and galleries.

Confirm nonreusable behavior from that game's EXE, scripts and observed output. Explicitly identify unsupported effects; do not silently drop story commands.

## Source modules

| File | Responsibility |
| --- | --- |
| `tsc_compiler.py` | Shared script compilation |
| `tsc_patches.py` | Language patches and subtitle alignment |
| `build_port.py` | Project/resource assembly |
| `port_resources.py` | Media, language assets and keywords |
| `grps_layout.py` | Image-metadata layouts |
| `effect_compat.py` | Effect compatibility checks |
| `game/` | Shared Ren'Py UI |
| `../runtime/` | RScript runtime |

See [architecture](../docs/SHARED_TEMPLATE_MIGRATION.en.md), [text layout](../docs/TEXT_WRAPPING.en.md) and [developer checks](../docs/README.en.md#development-checks).
