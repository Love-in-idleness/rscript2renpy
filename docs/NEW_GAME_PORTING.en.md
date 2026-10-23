# Porting a new game

[中文](NEW_GAME_PORTING.zh.md) | [English](NEW_GAME_PORTING.en.md) | [Русский](NEW_GAME_PORTING.ru.md)

[Project guide](../README.en.md) · [Setup](SETUP.en.md)

For unsupported games. Existing adapters need only their game README, not AI assistance.

## Materials

- Game title, version, updates and bonus content.
- Legally owned originals and patches, plus working copies for conversion.
- Original EXE, LiarsoftTool, Ren'Py 8 SDK and output directory.
- Original-game visuals, audio and actions for comparison.

Prepare TSC/resources with LiarsoftTool. Similar directories alone do not establish adapter compatibility.

## Development order

1. Confirm version, entry point, command dialect and resource layout.
2. Make startup, title and first scene work; check backgrounds, sprites, text, voice and choices together.
3. Complete menus, save/load, rollback, system progress and galleries.
4. Check other routes and add automated tests and user guides.
5. Then address Android packaging and device issues.

Reuse runtime/ and port_template/; keep game differences in a new directory.
Verify uncertain behaviour against this game's EXE, scripts and actual output, not another game's assumptions.

### UI resource checklist

Record each asset's role before implementing UI; see the [shared template](../port_template/README.en.md).
dt* supplies save images, nonbl supplies page digits, compane supplies in-game controls,
confscrn supplies the right-click menu, savescrn supplies save/load UI. Different names still require item-by-item verification.
Read .meta.xml canvas, positions and sizes: do not guess coordinates or centre every cropped image.
Save slots also need saveconf's number/date components. Confirm names, actions, selected and hover states separately.
Keep the original title menu; connect only its environment/settings entry to existing Text Settings, not replace the whole menu.

## Copyable AI prompt

Fill in versions and paths:

```text
Port this CodeX RScript game using rscript2renpy.

Game/version: <title, updates, bonus content>
Adapter directory: rscript2renpy/<slug>
Original resources: <read-only path>
Original EXE: <read-only path>
Conversion copy: <writable path>
Language patches: <label=path, or none>
rscript2renpy repository: <path>
LiarsoftTool repository and CLI: <paths>
Ren'Py 8 SDK: <path>
Output project: <new path>

Provide a reproducible generator so owners of the same game version can build it from the README.
Read both repositories' AGENTS.md and linked instructions, project READMEs and common template; inspect existing changes.
Confirm version, TSC dialect, entry point and resources before listing required adaptations.

Requirements:
1. Originals are read-only, conversion uses copies, generators accept only TSC.
2. Fix conversion problems in LiarsoftTool. Shared features belong in common layers; differences in the adapter.
3. Verify non-reusable behaviour against this EXE, scripts and actual output. Do not guess commands or effects.
4. Make startup, title and first scene work before menus, saves, progress and galleries.
5. Ask me when a visual judgement is uncertain. List unknowns; never silently skip story instructions.
6. Do not commit game assets, generated projects, saves, personal paths or keys.
7. Add tests; verify affected existing adapters for shared changes. Gameplay and Android are separate acceptance checks.
8. Game README covers versions, environment, preparation, commands, language patches and necessary limits.
9. Commit independently tested tasks locally. Do not push or release without a request.

Inspect materials and implementation before starting work.
```

## Delivery checks

The generator needs clear --help, resource/output arguments and no dependency on maintainer paths.
Fix source code, not only a hand-edited output project. Link the game guide from the main README.
Keep binary identity, hashes, key addresses and unknowns in game-specific developer references; do not commit the EXE.
Common checks: [documentation](README.en.md#development-checks). Tests/lint still do not replace checking actual routes, image and audio against the original.
