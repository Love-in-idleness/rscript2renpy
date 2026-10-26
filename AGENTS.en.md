# Repository guidelines

[中文](AGENTS.zh.md) | [English](AGENTS.en.md) | [Русский](AGENTS.ru.md) | [日本語](AGENTS.ja.md)

## Change boundaries

- Check Git status, preserve existing edits, and read the affected modules and game guides.
- LiarsoftTool owns resource unpacking and conversion; this repository owns TSC-to-Ren'Py generation, runtime, and UI.
- Keep shared implementations in `runtime/` and `port_template/`, game differences in adapters. Fix source, not only generated projects.
- Establish unknown behavior from the relevant game's EXE, scripts, and observed behavior, not assumptions from another game.
- Keep originals read-only and use copies for conversion and tests. Do not commit game assets, generated projects, saves, personal paths, or keys.
- Check manual edits before overwriting. Preserve input validation and file-level safe writes; do not broaden cleanup targets.

## Documentation

- READMEs serve users: purpose, installation, operation, supported versions, and practical limitations. Put technical evidence in developer references.
- Maintain separate `.zh.md`, `.en.md`, `.ru.md`, and `.ja.md` files for project-authored documents; unsuffixed entries only select a language.
- Keep facts and structure aligned. Use replaceable paths, not maintainer-specific configuration or private material.
- Omit task diaries, chat decisions, commit histories, and obsolete test counts. State useful conclusions as current behavior or limitations.
- Preserve original licenses, attribution, and asset provenance. Identify samples and scope when citing native programs.
- Update instructions, parameters, and links with features; remove all references to deleted documents.

## Checks

Run [shared checks](docs/README.en.md#development-checks) from the repository root, then tests for affected games.
Use your own SDK path for checks requiring Ren'Py.

- Cover compiler, patch, file installation, and native image changes with their corresponding tests.
- Font, wrapping, and touch changes also need native Ren'Py tests and visual checks.
- For documentation, check links, anchors, fences, actual `--help`, and `git diff --check`; no full game run is required.
- Report unit tests, lint, static analysis, and device checks separately. Generation success is not full playthrough verification.

## Git and permissions

- Commit independently verified tasks separately, including only relevant files.
- Pushes, releases, version changes, and raised minimum system requirements need an explicit request.
- Use the `codex/` prefix for new branches; do not switch branches without a reason.
- Do not execute unknown EXEs, perform administrator operations, or install globally without authorization.
