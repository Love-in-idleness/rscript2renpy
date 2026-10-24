# Local path configuration

[中文](LOCAL_WORKFLOW.zh.md) | [English](LOCAL_WORKFLOW.en.md) | [Русский](LOCAL_WORKFLOW.ru.md) | [日本語](LOCAL_WORKFLOW.ja.md)

[Documentation](README.en.md)

local.paths.toml records local tools, resources and output locations. It is optional:
it neither supplies arguments automatically nor enables language patches.

## Configure

Copy local.paths.example.toml at the repository root to local.paths.toml and replace examples with absolute paths.

| Section | Contents |
| --- | --- |
| tools | Both repositories, LiarsoftTool CLI/GUI/build directory and Ren'Py SDK |
| Game | Prepared resources, output project and base language |
| Game patches | Language labels and patch directories |

Leave unused items empty. Git ignores this file; do not commit personal paths. Alternatively pass paths directly to generators.

## Working rules

- Original game and patch stay read-only; convert copies.
- Keep output projects outside resource directories.
- Back up manual project edits before rebuilding.
- rebuild_local.sh is a maintainer convenience script, not other users' build entry point.

LiarsoftTool and rscript2renpy can share the file rather than maintain duplicate paths.
Give development tools access only to directories needed for the current task.
