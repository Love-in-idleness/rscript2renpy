# rscript2renpy &nbsp; [中文](#中文) | [English](#english)

## 中文

`rscript2renpy` 是面向 Liar-soft/raiL-soft CodeX RScript 游戏的实验性
Ren'Py 兼容运行时与移植工具。它提供寄存器模型、自定义 RScript 指令、
图像、音频、文字、特效和着色器支持；具体游戏仍需单独提供适配层、资源
命名规则和转换后的剧本。

开始新移植时可用独立的只读工具检查 `RsInit.tcf`、CFG 优先级和初始化线索：
`python3 tools/inspect_rscript_init.py /path/to/resources --encoding cp932`。
工具不依赖或运行 EXE／DLL，不改变资源布局或生成器；缺少配置文件的游戏仍可移植。
已知键、混合编码和引擎证据边界见 [RScript 初始化参考](docs/RSCRIPT_INITIALIZATION.md)。

当前运行时面向 Ren'Py 8（Python 3）；Forest 已使用 `/opt/apps/renpy`
中的 Ren'Py 8.5 完成生成与 lint 验证。

Forest、Khime 和试验性 Evermaiden 共用 `runtime/`、`port_template/`，游戏差异放在各自的
`game/*.rpy` 覆盖层。字体、文本/语言设置、Wiki、进度备份和安卓控制均由公共层
维护，详见 [公共模板分层说明](docs/SHARED_TEMPLATE_MIGRATION.md)。
三个生成器统一调用公共 early/modern 编译器与工程装配流程；不迁移旧文件布局
或 `persistent.forest_*` 设置。旧布局需重新生成到新工程目录。

除通用鼠标光标、Forest Android 应用图标、Khime 和 Evermaiden 应用图标外，本项目不包含
游戏剧本、图像、音频、视频或可执行文件。
用户必须从自己合法持有的游戏副本中准备其余资源。

本项目只维护并推送 Git 仓库源码，不再发布新的 GitHub Release 或版本包。

### 依赖 LiarsoftTool

移植工作流依赖
[LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) 完成资源预处理，
包括递归解包 XFL/LWG、GSC→TSC、WCG/LIM→PNG，以及封装 WAV→OGG。
运行时和生成器都不链接或调用 LiarsoftTool。Forest 生成器只读取
LiarsoftTool 2.1 当前生成的命令式 TSC（`*TXT`、`*load`、标签等），不接受
旧版 `;@gsc-structure-v1` 转储或 GSC 输入。

### 安装通用运行时

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

该命令会把通用运行时（含共享折行器）和光标复制到 Ren'Py 工程的 `game/engine/` 目录。除非使用
`--force`，否则不会覆盖内容不同的已有文件。

Forest 与 khime 的对话、追加对话、文本对象使用统一中日俄禁则，按最终字体的
真实字形前进量折行，不按语言切换规则。算法、SDK 衔接、边界示例和验证方式见
[`docs/TEXT_WRAPPING.md`](docs/TEXT_WRAPPING.md)。

### 新游戏移植模板

`port_template/` 是新游戏的半成品模板，负责安装通用运行时、复制已转换资源及
游戏专用 lowerer 生成的剧本。输出保留原资源目录：剧本在 `game/scr/`，图像在
`game/grps/` 等原目录，音频在 `game/bgm/voice/wav/`；运行时、公共界面和游戏覆盖层统一在
`game/engine/`。模板扫描全部 `grps/**/.meta.xml`，自动绑定已知原图控件，未知控件明确警告。
新项目引用该模板，不复制维护另一套；每款游戏只在
自己的目录实现 TSC lowering、方言及专用行为。模板不会调用
LiarsoftTool，也不会把原始 GSC/WCG/封装 WAV/XFL/LWG 复制进 Ren'Py 工程；可直接播放的
普通 PCM WAV 允许复制。完整步骤和
核对清单见 [`port_template/README.md`](port_template/README.md)。
Forest 与 Khime 构建时会安装通用 Android 启动说明图，包含 GitHub 地址及正版资源
自行构建提示。

Evermaiden 的现代脚本移植入口、完整中文/DLC 覆盖与已知限制见
[`evermaiden/README.md`](evermaiden/README.md)。生成器不依赖 EXE 或旧 Evermaiden 工程。

### Forest 生成器

项目提供《Forest》专用生成器。先使用 LiarsoftTool 2.1 解包、转换
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
`Original`。普通参数 `--language NAME` 只为基准脚本添加 RScript/Ren'Py 语言
标记，并把基准语言的菜单标签改为 `NAME`；它不读取补丁，也不会新增一种语言。
未指定时，基准语言在菜单中显示为 `Original`。生成器创建的菜单、确认框、
触屏按钮和通知统一使用英文；用户传入的语言标签仍原样显示。

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
`wav|bgm|voice/*.ogg`、`mov/*.mpg` 和 `keywords.json`。例如，英文补丁的
`scr/2100.tsc` 对应基准资源的 `scr/2100.tsc`，补丁目录不需要包含其余
102 个未修改场景。

TSC 补丁会按场景和指令位置对齐，可以翻译已有 `*TXT`、`*TXA`、`*select`
与 `*font` 文本，也可以给原版只有语音的段落新增 `*font` 字幕。新增字幕配套的
`*cls` 清除和 `*wait` 显示时长会随该语言一起启用；切回基准语言时不会执行。
同一句原文可以因所在位置不同而使用不同译文。为防止翻译补丁意外改变剧情，其他
指令的新增、删除或重排都会报错，补丁中的跳转、变量及其他游戏逻辑不会取代基准
脚本。

补丁根目录可放置带 `//` 注释的 `keywords.json`。每项格式为
`["完整句子", "https://链接", "^cg 与 ^cw 之间的词"]`。生成器会校验并
原样复制该文件。Wiki 默认关闭；使用带词条数据的中文补丁时，可在游戏内右键菜单
切换。打开后，只有当前语言中既匹配
完整句子、又由 `^cg…^cw` 标出的文字才显示为绿色并可点击打开链接；关闭时这些
文字保持白色。

标题页设置菜单还可调整字号和每行字符数（默认 22/19），并提供持久化
游戏进度的备份、读取与清除功能；清除进度时保留备份。把 `.ttf`、`.otf`
或 `.ttc` 文件放入生成工程的 `game/fonts/` 后，可在同一菜单中循环切换。
生成器附带 Noto Sans CJK JP Regular、Noto Sans CJK Light 和
Noto Serif CJK Regular，可在菜单中选择；正文默认使用 Noto Sans CJK JP Regular，
其英文实测比 SimHei（黑体）更窄，让本次对照句中的「电影」保持同一行。
旧 SimHei 默认值自动迁移一次，其他已选字体保留；黑体仍可在菜单中选择。
SimHei 不是开源字体，来源与权利说明见
[SimHei-NOTICE.md](port_template/fonts/SimHei-NOTICE.md)，静态分析依据见
[FOREST_FONT_ANALYSIS.md](docs/FOREST_FONT_ANALYSIS.md)。

生成器只扫描 `scr/*.tsc`。原始 GSC 是否保留在资源目录中不影响生成结果。

仓库保存了从《Forest》原版提取的 32×32 光标。安装通用运行时或运行 Forest
生成器时，它会复制为 `game/engine/gui/rscript_cursor.png` 并自动启用；以后其他移植
项目也统一使用这一光标。

生成器还需要 Python 3 和 Pillow。Forest 的原始 MPG 会直接复制到工程，
不会重新编码。生成器只读取用户指定的资源目录，不会查找、下载或修改已安装的游戏。

两款生成器会同时写入 Ren'Py Android 配置和各自的自适应图标，包括
横屏方向、包名与版本。PC／Android 版本统一由通用模板 `port_template/build_port.py`
中的 `PORT_VERSION` 管理，当前为 `1.3`；安卓版本代码最低为 `13`，保留已有更高值。
这不代表已完成安卓打包或实机验证。签名用的 `android.keystore` 和 `bundle.keystore`
不会纳入仓库或复制到工程；Ren'Py 会在构建机器上创建或使用本地签名密钥。

项目代码采用 [MIT License](LICENSE)。项目附带的 Noto CJK 字体采用
SIL Open Font License 1.1，详见 `port_template/fonts/NotoSans.txt`。
SimHei 不适用 MIT/OFL；本项目未取得或验证额外再分发授权。

---

## English

Reusable Ren'Py runtime for scripts lowered from Liar-soft/raiL-soft CodeX
RScript games.

For new ports, `python3 tools/inspect_rscript_init.py /path/to/resources --encoding cp932`
produces a read-only initialization report. It does not use EXE/DLL files or change
builders/assets; games without external configuration are not rejected.
See [the initialization reference](docs/RSCRIPT_INITIALIZATION.md) for known keys,
mixed encodings and version-specific evidence limits.

The runtime now targets Ren'Py 8 and Python 3. Forest generation and lint have
been verified with Ren'Py 8.5.

Forest, Khime and Evermaiden share `runtime/` and `port_template/`; game-specific code
lives in each game's `game/*.rpy` overlay. Fonts, text/language settings, Wiki
links, progress backups and Android controls are maintained in the shared base.
See [the architecture and migration notes](docs/SHARED_TEMPLATE_MIGRATION.md).
All three builders use the shared early/modern compiler and project assembler.
Legacy file layouts and `persistent.forest_*` settings are not migrated; generate
legacy projects into a fresh output directory.

This project is maintained and distributed directly from the Git repository.
No new GitHub Releases or versioned release packages will be published.
Runtime behavior depends on the source game's CodeX dialect, so each new game
still requires verification.

Apart from the shared mouse cursor and Forest, Khime and Evermaiden application
icons, this repository contains engine-side support only. It does not contain game
scripts, other images, audio, movies, executables, or other proprietary game
data.

## Install the runtime

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

The command copies the runtime, shared glyph line breaker, and cursor into the
project's `game/engine/` directory. Existing different files are not overwritten
unless `--force` is specified.

Forest and khime use one language-independent kinsoku rule set for dialogue,
appended dialogue, and text objects, using the final shaped glyph advances.
Implementation notes, boundary examples, and verification commands are in
[`docs/TEXT_WRAPPING.md`](docs/TEXT_WRAPPING.md).

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

## New-game port template

`port_template/` is a deliberately incomplete starter that installs the shared
runtime and copies converted assets plus game-specific scripts. Generated projects
retain native resource directories (`game/scr`, `game/grps`, `game/bgm`, etc.);
runtime, shared UI and adapters live in `game/engine`. All `grps/**/.meta.xml`
files are scanned; known controls are bound and unknown controls produce warnings.
Forest and Khime builds also install a shared Android loading notice with the
project URL and an instruction to build from legitimately owned game files.
See [`port_template/README.md`](port_template/README.md) for the workflow and
per-game verification checklist.

## Forest generator

The project contains a Forest-specific generator. It never downloads or
bundles proprietary Forest data. Prepare an extracted resource directory with
at least `scr/`, `grps/`, the other `grp*` directories, and converted OGG audio;
then create an empty Ren'Py project. The generator requires Python 3, Pillow,
and LiarsoftTool 2.1 for editable TSC input.
Prepare both converted resources and current command-based TSC files first:

```bash
liarsofttool -R --unpack-only --gsc-to-tsc /path/to/forest-resources
python3 forest/build_forest_rscript.py \
    /path/to/forest-resources /path/to/renpy-project
```

### Language labels and patches

By default, generated `_say` and `_append` statements have no language marker,
and the base language is labelled `Original` in the title settings screen. A plain
`--language NAME` adds that marker to the base script and uses `NAME` as the
base-language label. It does not read a patch or add another language.

`--language NAME=PATCH_DIR` adds a switchable language. `NAME` must be a valid
Ren'Py identifier and is also used verbatim as its menu label. The option may
be repeated for multiple patches and may be combined with one plain base
language marker, as in the example above.

All menus, confirmation prompts, touch controls, and notifications created by
the generator use English. User-supplied language labels are displayed
verbatim.

A patch directory contains only converted files that differ from the base
resources, at the same relative paths; unchanged files should be omitted. It
may contain `scr/*.tsc`, `grp*/*.png`, `wav|bgm|voice/*.ogg`, and
`mov/*.mpg`, plus an optional `keywords.json`. A patched `scr/2100.tsc`, for
example, is compared with the base `scr/2100.tsc`; the other unchanged
scenarios are not required in the patch.

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
project's `game/fonts/` directory can be cycled from the same screen. The default
body font is Noto Sans CJK JP Regular: measured Latin advances are narrower than
SimHei, keeping the Chinese mixed-language reference sentence on three lines.
The previous SimHei default is migrated once; other selected fonts are retained.
SimHei remains selectable but is proprietary, not MIT/OFL;
see [SimHei-NOTICE.md](port_template/fonts/SimHei-NOTICE.md) and the
[static font analysis](docs/FOREST_FONT_ANALYSIS.md).

The generator reads only `scr/*.tsc`; it neither invokes LiarsoftTool nor
accepts GSC input. Keeping original GSC files beside the TSC files does not
affect generation.

`keywords.json` may contain `//` comments. Each entry is
`["complete sentence", "https://URL", "text between ^cg and ^cw"]`.
The generator validates and copies it unchanged. Wiki mode is off by default
and can be toggled from the in-game right-click menu when the active language
has keyword data. When enabled, marked text is green and clickable only when its complete sentence
also matches the current language's keyword data. When disabled, marked text
remains white.

The repository carries the original 32x32 Forest cursor as the shared RScript
cursor. Runtime installation and the Forest generator copy it to
`game/engine/gui/rscript_cursor.png`; future game adapters use the same asset.

The generator only reads the directory supplied by the user. It expects
`scr/*.tsc`, PNG files under the `grp*` directories, OGG files
under `wav/`, `bgm/`, and `voice/`, and `mov/0001.mpg` plus
`mov/0002.mpg`. Original MPG files are copied without re-encoding. The
generator does not locate, extract, download, or modify an installed copy of
the game.

The generator also writes the verified Forest Ren'Py Android configuration and
adaptive icons, including landscape orientation, package name, and version.
Signing files (`android.keystore` and `bundle.keystore`) remain local to the
build machine and are never bundled by this repository.

The bundled Noto Sans CJK JP Regular, Noto Sans CJK Light, and Noto Serif CJK
Regular fonts are distributed under the SIL Open Font License 1.1 in
`port_template/fonts/NotoSans.txt`.
SimHei is separately licensed; additional redistribution rights have not been
obtained or verified by this project.

## License

Project code is available under the [MIT License](LICENSE). See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for incorporated code and the
separately licensed font included with the Forest generator.
