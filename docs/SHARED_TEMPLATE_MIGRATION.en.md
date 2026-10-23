# Developer reference: shared template and adapters

[中文](SHARED_TEMPLATE_MIGRATION.zh.md) | [English](SHARED_TEMPLATE_MIGRATION.en.md) | [Русский](SHARED_TEMPLATE_MIGRATION.ru.md)

[Documentation](README.en.md) · [Template](../port_template/README.en.md)

Source ownership, not a game build guide; use each game's README for ordinary builds.

## Responsibilities

| Location | Responsibility |
| --- | --- |
| LiarsoftTool | Archives, GSC/TSC, encodings, image/audio conversion |
| runtime/ | Instructions, registers, layers, text and audio |
| port_template/ | Script compilation, patch alignment, resource installation and common UI |
| Game adapter | Dialect, version checks, default layouts, specific behaviour |
| Generated project | Build result, not the shared-code maintenance location |

Fix common behaviour in the shared layer; keep differences in adapters. Do not maintain divergent runtime copies
or string-patch installed shared files.

## Generation

Generators read prepared TSC, compile scenes, then install through assemble_port. Users convert resources beforehand with LiarsoftTool.
Common installation copies media/configuration and removes corresponding .rpyc. Inputs, patches and output cannot overlap.
Resolve errors and rebuild after interruption. Scripts live in game/scr/, runtime in game/engine/,
languages in game/tl/<language>/; media keeps original directories.

## Patches

| Game | Policy |
| --- | --- |
| Forest | Text/subtitle alignment; complete replacement for 5000 |
| Khime | Text/subtitle alignment; separate side-story resources |
| Evermaiden, CannonBall, Kagerou | Complete scene replacement |

Do not mix patches into originals. Missing translations fall back; saves cannot be presumed interchangeable across different story structures.

## Runtime and UI

Text, voice, click and draw queues share implementations; explicit dialect configuration chooses behaviour.
TSC byte layouts alone do not establish animation, coordinate or timing semantics.
grps_layout.py reads composite metadata; grps_ui.rpy handles settings, choices, saves and controls.
Adapters supply verified layouts for hard-coded native UI. Text defaults to slow; player settings,
persistent progress and game-specific save directories are maintained separately.
PC/Android display versions are managed by build_port.py; ordinary updates must not raise Android minimums.
Screenshots, touch and packaging still need device validation.

## Checks

Run test_runtime.py, test_port_template.py and test_shared_port.py first, then affected game tests.
Commands: [documentation](README.en.md#development-checks). After SDK upgrades rerun native text/UI checks;
record full-game results separately.
