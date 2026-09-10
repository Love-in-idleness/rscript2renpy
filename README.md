# rscript2renpy &nbsp; [中文](#中文) | [English](#english)

## 中文

`rscript2renpy` 是面向 Liar-soft/raiL-soft CodeX RScript 游戏的实验性
Ren'Py 兼容运行时与移植工具。它提供寄存器模型、自定义 RScript 指令、
图像、音频、文字、特效和着色器支持；具体游戏仍需单独提供适配层、资源
命名规则和转换后的剧本。

当前运行时面向 Ren'Py 8（Python 3）；Forest 已使用 `/opt/apps/renpy`
中的 Ren'Py 8.5 完成生成与 lint 验证。

除通用鼠标光标外，本项目不包含游戏剧本、图像、音频、视频或可执行文件。
用户必须从自己合法持有的游戏副本中准备其余资源。

本项目只维护并推送 Git 仓库源码，不再发布新的 GitHub Release 或版本包。

### 依赖 LiarsoftTool

移植工作流依赖
[LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) 完成资源预处理，
包括递归解包 XFL/LWG、GSC→TSC、WCG/LIM→PNG，以及封装 WAV→OGG。
运行时和生成器都不链接或调用 LiarsoftTool。Forest 生成器只读取
LiarsoftTool 2.0 当前生成的命令式 TSC（`*TXT`、`*load`、标签等），不接受
旧版 `;@gsc-structure-v1` 转储或 GSC 输入。

### 安装通用运行时

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

该命令会把 17 个运行时模块和通用光标复制到 Ren'Py 工程的 `game/` 目录。除非使用
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

#### 语言标签与补丁

默认生成的 `_say` 和 `_append` 不附带语言标记，标题页把基准语言显示为
“原文”。普通参数 `--language NAME` 只为基准脚本添加 RScript/Ren'Py 语言
标记，并把基准语言的菜单标签改为 `NAME`；它不读取补丁，也不会新增一种语言。

参数 `--language NAME=PATCH_DIR` 才会加入一种可切换语言。`NAME` 必须是合法的
Ren'Py 标识符，同时会原样显示为标题页语言标签；`PATCH_DIR` 是该语言的补丁
目录。此参数可以重复使用，以同时加入多个语言补丁，也可以与一个普通的
`--language NAME` 组合。例如：

```bash
python3 forest/build_forest_rscript.py 原版资源 RenPy工程 \
    --language japanese \
    --language english=/path/to/english-patch
```

补丁目录不是另一份完整游戏，只需按原资源的相对路径放置发生变化的文件；不变的
文件应当省略。支持的内容包括 `scr/*.tsc`、`grp*/*.png`、
`wav|bgm|voice/*.ogg` 和 `mov/*.webm`。例如，英文补丁的 `scr/2100.tsc`
对应基准资源的 `scr/2100.tsc`，补丁目录不需要包含其余 102 个未修改场景。

TSC 补丁会按场景和指令位置对齐，可以翻译已有 `*TXT`、`*TXA`、`*select`
与 `*font` 文本，也可以给原版只有语音的段落新增 `*font` 字幕。新增字幕配套的
`*cls` 清除和 `*wait` 显示时长会随该语言一起启用；切回基准语言时不会执行。
同一句原文可以因所在位置不同而使用不同译文。为防止翻译补丁意外改变剧情，其他
指令的新增、删除或重排都会报错，补丁中的跳转、变量及其他游戏逻辑不会取代基准
脚本。

标题页设置菜单还可调整字号和每行字符数（默认 22/19），并提供持久化
游戏进度的备份、读取与清除功能；清除进度时保留备份。把 `.ttf`、`.otf`
或 `.ttc` 文件放入生成工程的 `game/fonts/` 后，可在同一菜单中循环切换；
默认仍使用随生成器提供的 Noto Sans CJK JP。

生成器只扫描 `scr/*.tsc`。原始 GSC 是否保留在资源目录中不影响生成结果。

仓库保存了从《Forest》原版提取的 32×32 光标。安装通用运行时或运行 Forest
生成器时，它会复制为 `game/gui/rscript_cursor.png` 并自动启用；以后其他移植
项目也统一使用这一光标。

生成器还需要 Python 3、Pillow 和 `ffmpeg`。它只读取用户指定的
资源目录，不会查找、下载或修改已安装的游戏。

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

The runtime now targets Ren'Py 8 and Python 3. Forest generation and lint have
been verified with Ren'Py 8.5.

This project is maintained and distributed directly from the Git repository.
No new GitHub Releases or versioned release packages will be published.
Runtime behavior depends on the source game's CodeX dialect, so each new game
still requires verification.

Apart from the shared mouse cursor, this repository contains engine-side
support only. It does not contain game scripts, images, audio, movies,
executables, or other proprietary game data.

## Install the runtime

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

The command copies the seventeen runtime modules and shared cursor into the
project's `game/` directory. Existing different files are not overwritten
unless `--force` is specified.

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
Prepare both converted resources and current command-based TSC files first:

```bash
liarsofttool -R --unpack-only --gsc-to-tsc /path/to/forest-resources
python3 forest/build_forest_rscript.py \
    /path/to/forest-resources /path/to/renpy-project
```

### Language labels and patches

By default, generated `_say` and `_append` statements have no language marker,
and the base language is labelled `原文` in the title settings screen. A plain
`--language NAME` adds that marker to the base script and uses `NAME` as the
base-language label. It does not read a patch or add another language.

`--language NAME=PATCH_DIR` adds a switchable language. `NAME` must be a valid
Ren'Py identifier and is also used verbatim as its menu label. The option may
be repeated for multiple patches and may be combined with one plain base
language marker, as in the example above.

A patch directory contains only converted files that differ from the base
resources, at the same relative paths; unchanged files should be omitted. It
may contain `scr/*.tsc`, `grp*/*.png`, `wav|bgm|voice/*.ogg`, and
`mov/*.webm`. A patched `scr/2100.tsc`, for example, is compared with the base
`scr/2100.tsc`; the other unchanged scenarios are not required in the patch.

Command-based TSC patches are aligned by scene and instruction position. They
may translate existing `*TXT`, `*TXA`, `*select`, and `*font` text, and may add
`*font` subtitles for voice-only passages. Subtitle-related `*cls` clearing and
`*wait` timing are enabled only while that patch language is selected. The same
source text may therefore have context-specific translations. Other inserted,
removed, or reordered commands are rejected, and patched jumps, variables, or
other gameplay logic never replace the base script. Old `;@gsc-structure-v1`
dumps are intentionally unsupported.

The same title settings screen also controls text size, characters per line,
and persistent-progress backup, restore, and clearing; clearing progress keeps
the backup. Additional `.ttf`, `.otf`, and `.ttc` files placed in the generated
project's `game/fonts/` directory can be cycled from the same screen; Noto Sans
CJK JP remains the default.

The generator reads only `scr/*.tsc`; it neither invokes LiarsoftTool nor
accepts GSC input. Keeping original GSC files beside the TSC files does not
affect generation.

The repository carries the original 32x32 Forest cursor as the shared RScript
cursor. Runtime installation and the Forest generator copy it to
`game/gui/rscript_cursor.png`; future game adapters use the same asset.

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
