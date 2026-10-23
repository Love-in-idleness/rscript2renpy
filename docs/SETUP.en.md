# Environment setup and first build

[中文](SETUP.zh.md) | [English](SETUP.en.md) | [Русский](SETUP.ru.md)

[Project guide](../README.en.md)

For already supported games. New games require an adapter: see [new-game porting](NEW_GAME_PORTING.en.md).
Replace every /path/to/... with your own path.

## 1. Dependencies

| Dependency | Use |
| --- | --- |
| Python 3, recommended 3.11+ | Generators |
| Pillow | Image dimensions and application icons |
| Ren'Py 8 SDK | Running, checking and packaging |
| [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) | Resource extraction and script/image/audio conversion |
| Git | Source checkout |

Extract the full SDK. Linux uses renpy.sh; Windows uses renpy.exe.
Normal builds of existing adapters need neither Wine, RsComp.dll nor a Windows VM.

## 2. Get the project

Linux/macOS:

```bash
git clone https://github.com/Love-in-idleness/rscript2renpy.git
cd rscript2renpy
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Pillow
```

Windows PowerShell, at the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install Pillow
```

On Windows replace python3 in generator commands with .\\.venv\\Scripts\\python.exe.
On Linux use python or python3 from the activated environment.

## 3. Prepare copies

Keep originals, converted resources and output separate:

```text
work/
├── originals/Game/
├── prepared/Game/
├── prepared/Game.zh/
└── projects/Game/
```

Do not convert originals or overlap input resources and output projects. Check the game's version requirements;
Kagerou, for example, requires ハチポチ特典. Japanese resources normally use CP932:

```bash
/path/to/liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/prepared/Game
```

Convert a GBK Chinese patch separately:

```bash
/path/to/liarsofttool -R --unpack-only --gsc-to-tsc -e gbk /path/to/prepared/Game.zh
```

Keep resulting scr/*.tsc, usable images/audio and .meta.xml. Ordinary PCM WAV and original MPG can be used directly.
Re-export scripts with LiarsoftTool; first back up edited TSC.

## 4. Generate

Forest example, from the repository root:

```bash
python3 forest/build_forest_rscript.py /path/to/prepared/Forest /path/to/projects/Forest \
    --language jp --language zh=/path/to/prepared/Forest.zh
```

Without a patch, omit --language zh=.... jp names the base language; zh=directory adds a switchable patch.
Labels do not select file encodings. Follow each [game guide](../README.en.md) for its patch policy.
Use a fresh directory for the first build. Back up manual edits before rebuilding and use --force as required by the generator.

## 5. Run and check

```bash
/path/to/renpy-sdk/renpy.sh /path/to/projects/Forest lint
/path/to/renpy-sdk/renpy.sh /path/to/projects/Forest
```

On Windows select the project in the Ren'Py launcher, then lint or run. Android packaging uses the SDK Android tools and needs RAPT setup.
Keep complete output when reporting errors, plus game version, build command and scene.
Lint does not replace actual image, audio, choice and save/load checks.

## Other notes

local.paths.toml is an optional local path note, not required generator configuration: see [local paths](LOCAL_WORKFLOW.en.md).
The project supplies neither original games nor prebuilt game packages. Review [asset licensing](../THIRD_PARTY_NOTICES.en.md)
before distribution and exclude personal saves and signing keys.
