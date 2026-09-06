# rscript2renpy &nbsp; [中文](#中文) | [English](#english)

## 中文

`rscript2renpy` 是面向 Liar-soft/raiL-soft CodeX RScript 游戏的实验性
Ren'Py 兼容运行时与移植工具。它提供寄存器模型、自定义 RScript 指令、
图像、音频、文字、特效和着色器支持；具体游戏仍需单独提供适配层、资源
命名规则和转换后的剧本。

本项目不包含任何游戏剧本、图像、音频、视频或可执行文件。用户必须从
自己合法持有的游戏副本中准备资源。

### 依赖 LiarsoftTool

移植工作流依赖
[LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) 完成资源预处理，
包括递归解包 XFL/LWG、GSC→TSC、WCG/LIM→PNG，以及封装 WAV→OGG。
运行时本身不链接 LiarsoftTool；依赖发生在生成 Ren'Py 工程之前。

### 安装通用运行时

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

该命令会把 16 个运行时模块复制到 Ren'Py 工程的 `game/` 目录。除非使用
`--force`，否则不会覆盖内容不同的已有文件。

### Forest 分支

`forest` 分支提供《Forest》专用生成器。先使用 LiarsoftTool 解包并转换用户
自行准备的原版资源，再执行：

```bash
python3 forest/build_forest_rscript.py \
    /path/to/forest-resources /path/to/renpy-project
```

生成器还需要 Python 3、Pillow 和 `ffmpeg`。它只读取用户指定的资源目录，
不会查找、下载或修改已安装的游戏。

项目代码采用 [MIT License](LICENSE)。`forest` 分支附带的 Noto Sans CJK JP
字体采用 SIL Open Font License 1.1，详见 `forest/fonts/NotoSans.txt`。

---

## English

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

## Forest branch

The `forest` branch contains a Forest-specific generator. It never downloads or
bundles proprietary Forest data. Prepare an extracted resource directory with
at least `scr/`, `grps/`, the other `grp*` directories, and converted OGG audio;
create an empty Ren'Py project; then run:

```bash
python3 forest/build_forest_rscript.py \
    /path/to/forest-resources /path/to/renpy-project
```

The generator requires Python 3, Pillow, `ffmpeg` for MPG conversion, and the
experimental Forest GSC decoder included on this branch. Run LiarsoftTool's
recursive unpack/conversion first when the resource tree still contains packed
archives, WCG/LIM images, or embedded-Ogg WAV files.

The generator only reads the directory supplied by the user. It expects
`scr/*.gsc`, PNG files under the `grp*` directories, OGG files under `wav/`,
`bgm/`, and `voice/`, and `mov/0001` plus `mov/0002` in MPG or WebM form. It
does not locate, extract, download, or modify an installed copy of the game.

The Noto Sans CJK JP font on this branch is distributed under the SIL Open Font
License 1.1 in `forest/fonts/NotoSans.txt`.

## License

Project code is available under the [MIT License](LICENSE). See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for incorporated code and the
separately licensed font on the `forest` branch.
