# Working agreements

[中文](AGENTS.zh.md) | [English](AGENTS.en.md) | [Русский](AGENTS.ru.md) | [日本語](AGENTS.ja.md)

## Before starting

- Inspect Git status, preserve user changes and search with rg.
- Read the project and affected game READMEs. Path examples: local.paths.example.toml; private paths: ignored local.paths.toml.
- For cross-repository work also read LiarsoftTool's AGENTS.md and its linked instructions.
  Resource conversion belongs to LiarsoftTool; TSC-to-Ren'Py compilation, runtime and UI belong here.

## Implementation boundaries

- Put common functionality in runtime/ and port_template/; dialect and game differences in adapters.
- Do not maintain long-lived copies of shared code or string-patch installed files; fix generators or templates.
- Verify unknown behaviour against this game's EXE, scripts and actual output, not guesses from another game.
- Originals are read-only; convert copies and test temporary projects. Do not commit game assets, generated projects, saves, keys or personal paths.
- Check manual edits before overwriting, following generator permissions. Do not automatically install administrator dependencies or execute unknown EXEs.

## Documentation

- README is for users: purpose, dependencies, resource preparation, build commands, patches and necessary limitations.
- Every project-authored document has separate .zh.md, .en.md, .ru.md and .ja.md versions in the same directory, updated together.
  The unsuffixed .md is navigation only. Do not keep mixed-language bodies or substitute short summaries for translations.
- Preserve original licenses and third-party legal text unchanged; provide translations of project-authored explanations.
- Follow the user's Chinese writing; English, Russian and Japanese must carry the same facts without invented features.
- Write short direct instructions. Error internals, legacy migration, internal fields, regression logs, commit histories and repeated disclaimers do not belong in user guides.
- Game guides use overview, resource preparation, generation, language patches, use, checks and limitations.
- Reverse-engineering hashes, addresses, operands and uncertainties belong in developer references. Static evidence is not gameplay.
- Link each game from the root README; separate user guides and technical references in the documentation index.
- Check options, examples and local links; remove references when removing features. Preserve license, copyright and provenance meaning.

## Validation

- For documentation check links, headings, arguments and git diff --check; do not rerun full games for text-only changes.
- Common code: tests/test_runtime.py and tests/test_port_template.py.
- File installation: tests/test_file_install.py; native images: tests/test_native_images.py.
- Compilation/patches: tests/test_tsc_compiler.py and tests/test_tsc_patches.py.
- Shared project: tests/test_shared_port.py <SDK> --logic-only, plus affected game tests and lint.
- Text/touch changes: tests/run_native_text_wrap.py and tests/run_touch_controls.py.
- Visuals, audio, routes, old saves and Android need actual execution. Report automated checks separately from device results.

## Git

- Commit verified independent tasks locally, with only their files. Honour explicit requests not to commit.
- Without an explicit request do not push, publish releases, raise versions or Android requirements.
- Prefer the current checkout; new branches use codex/.
