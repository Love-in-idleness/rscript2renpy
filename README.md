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
运行时和生成器都不链接或调用 LiarsoftTool。各游戏生成器只读取
LiarsoftTool 2.0 预先生成的结构化 TSC，不接受 GSC 输入。

### 安装通用运行时

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

该命令会把 16 个运行时模块复制到 Ren'Py 工程的 `game/` 目录。除非使用
`--force`，否则不会覆盖内容不同的已有文件。

### Forest 生成器

项目提供《Forest》专用生成器。先使用 LiarsoftTool 2.0 解包、转换
用户自行准备的原版资源，并为剧本生成可编辑 TSC：

```bash
liarsofttool -R --unpack-only --gsc-to-tsc /path/to/forest-resources
```

然后执行：

```bash
python3 forest/build_forest_rscript.py \
    /path/to/forest-resources /path/to/renpy-project
```

默认生成的 `_say` 和 `_append` 不附带语言标记。如需保留语言信息，可添加
`--language japanese`（或其他 Ren'Py 标识符）。

生成器只扫描 `scr/*.tsc`。原始 GSC 是否保留在资源目录中不影响生成结果。

生成器还需要 Python 3、Pillow 和 `ffmpeg`。它只读取用户指定的资源目录，
不会查找、下载或修改已安装的游戏。

项目代码采用 [MIT License](LICENSE)。项目附带的 Noto Sans CJK JP
字体采用 SIL Open Font License 1.1，详见 `forest/fonts/NotoSans.txt`。

### Evermaiden 生成器

`evermaiden` 目录中的生成器面向中文资源，支持 LiarsoftTool 2.0 的 `modern-36` TSC，
并将正文生成为 `_say chinese`。生成方法见
[`evermaiden/README.zh-CN.md`](evermaiden/README.zh-CN.md)。生成器需要
Python 3、fontTools 与 `ffmpeg`，不会附带或下载游戏资源。

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

## Evermaiden generator

The `evermaiden` directory contains a Chinese, `modern-36` TSC adapter. See
`evermaiden/README.zh-CN.md`; it requires Python 3, fontTools, and `ffmpeg`.

## Forest generator

The project contains a Forest-specific generator. It never downloads or
bundles proprietary Forest data. Prepare an extracted resource directory with
at least `scr/`, `grps/`, the other `grp*` directories, and converted OGG audio;
then create an empty Ren'Py project. The generator requires Python 3, Pillow,
`ffmpeg` for MPG conversion, and LiarsoftTool 2.0 for editable TSC input.
Prepare both converted resources and structured TSC files first:

```bash
liarsofttool -R --unpack-only --gsc-to-tsc /path/to/forest-resources
python3 forest/build_forest_rscript.py \
    /path/to/forest-resources /path/to/renpy-project
```

By default, generated `_say` and `_append` statements have no language marker.
Pass `--language japanese` (or another Ren'Py identifier) to emit one.

The generator reads only `scr/*.tsc`; it neither invokes LiarsoftTool nor
accepts GSC input. Keeping original GSC files beside the TSC files does not
affect generation.

The generator only reads the directory supplied by the user. It expects
`scr/*.tsc`, PNG files under the `grp*` directories, OGG files
under `wav/`, `bgm/`, and `voice/`, and `mov/0001` plus `mov/0002` in MPG or
WebM form. It does not locate, extract, download, or modify an installed copy
of the game.

The Noto Sans CJK JP font is distributed under the SIL Open Font
License 1.1 in `forest/fonts/NotoSans.txt`.

## License

Project code is available under the [MIT License](LICENSE). See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for incorporated code and the
separately licensed font included with the Forest generator.
