# Forest 移植说明

[返回主说明](../README.md) · [通用模板](../port_template/README.md) · [English](#english)

## 概述

本目录使用公共 `runtime/` 与 `port_template/`，将用户自备的 Forest 资源
生成 Ren'Py 8 工程。专用层保留 Forest 的布局、图片编号纠错、Wiki 映射和
结局语言路由；不包含游戏本体，不查找、下载或修改已安装的游戏。
以下命令均在仓库根目录执行。

## 准备资源

需要 Python 3、Pillow、Ren'Py 8 SDK，以及当前
[LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool)
（格式验证使用 2.2.2）。先在合法持有的游戏副本中完成解包和转换：

```bash
liarsofttool -R --unpack-only --gsc-to-tsc /path/to/Forest
```

输入要求：

- 当前 `legacy-28/early` 命令式 `scr/*.tsc`，不接受旧结构转储或 GSC 输入。
- `grpe/grpo/grpo_bg/grpo_bu/grpo_ci/grpo_f/grps` 等原资源目录及转换后的图像，
  包括标题 `grpe/9001.png`；保留 `grps` 下的 `.meta.xml`。
- 可播放的 `bgm/Track01.ogg`、`wav/*.ogg` 和 `voice/*.ogg`。
- 原始 `mov/0002.mpg`、`mov/0001.mpg`；直接复制，不重新编码。

生成器只扫描 TSC；原始 GSC 可以保留在资源目录中，但不会用于生成。
TSC 正文是 UTF-8。上游转换原 GSC 时需按输入选择编码：日文通常为 `cp932`，
中文通常为 `gbk`；本机英文补丁使用 `cp932`，俄文补丁使用 `cp1251`。
这些是当前资源样本的设置，不是语言标签对应的通用编码规则；混合编码的
未翻译文本不会自动修正。仅刷新 TSC 的方法见
[主说明](../README.md#依赖与资源预处理)。

## 生成工程

```bash
python3 forest/build_forest_rscript.py \
    /path/to/Forest /path/to/renpy/Forest
```

输出目录无需预先创建，不依赖已有 `gui.rpy` 或旧 Ren'Py 工程。
Forest 生成器会覆盖现有生成文件，重建前请备份手工修改；原资源只读使用。
不迁移旧 `images/scenario/audio` 布局或根目录旧运行时，需改用新输出目录。
不迁移旧 `persistent.forest_*` 设置。

剧本位于 `game/scr/`，原图像、音频、视频保留各自目录，解释器、配置和公共
界面统一位于 `game/engine/`；语言包位于 `game/tl/<语言>/`。
生成器安装横屏 Android 配置、自适应图标和共用启动说明，版本由通用模板管理。
签名密钥不入库、不复制；这些配置不代表已完成 Android 打包或实机验证。

## 语言补丁

默认 `_say` 和 `_append` 没有语言标记，标题设置中的基准语言显示为 `Original`。
`--language NAME` 只命名基准语言并添加语言标记，不读取补丁、不新增语言。
`--language NAME=PATCH_DIR` 才添加一种可切换语言；`NAME` 必须是合法的
Ren'Py 标识符，也是菜单中显示的标签。参数可以重复，例如：

```bash
python3 forest/build_forest_rscript.py \
    /path/to/Forest /path/to/renpy/Forest \
    --language jp --language en=/path/to/Forest.en \
    --language zh=/path/to/Forest.zh
```

生成器创建的菜单、确认框、触屏按钮和通知使用英文；用户传入的语言标签原样显示。

补丁目录只需放置发生变化的文件，使用原资源的相对路径。支持 `scr/*.tsc`、
`grp*` 下的转换图像、`wav/bgm/voice` 下的音频、`mov/*.mpg` 和 `keywords.json`。
例如 `scr/2100.tsc` 对应原版同名场景，其余未修改场景不需要重复提供。

### 文本对齐与字幕

普通场景按指令位置对齐，可以翻译已有 `*TXT`、`*TXA`、`*select` 和 `*font`。
原版只有语音的段落允许新增 `*font` 字幕，以及配套的 `*cls` 清除和 `*wait`
时长；这些新增指令只在对应补丁语言下执行。同一句原文可按位置使用不同译文。
非文本参数仅接受公共编译器明确允许的显示、音频等覆盖；不允许任意增加、
删除或重排剧情逻辑，跳转与变量不会被补丁随意替换。

`5000.tsc` 例外：结局按当前语言选择整份脚本，不做正文对齐。该场景禁止
回退和打开菜单，结束后恢复权限。只使用可信补丁；跨语言切换和旧存档仍需验证。

### Wiki 词条

补丁根目录可放置带 `//` 注释的 `keywords.json`，每项格式为：

```json
[["完整句子", "https://example.com/wiki", "^cg 与 ^cw 之间的词"]]
```

生成器校验并复制该文件。Wiki 默认关闭，由带词条的中文右键菜单切换，
标题设置不提供 Wiki 开关。只有当前语言中完整句子匹配、且被 `^cg…^cw`
标记的词才显示为绿色并可点击；关闭时保持白色。颜色和内联图规则由公共层处理。

## 适配说明

原标题的开始、读档、设置、鉴赏和退出动作由脚本驱动，不使用 Ren'Py 默认
主菜单。打开游戏时只播放一次 `0002 → 0001` 启动视频；回到标题不重播。
游戏内设置、存读档、图片选项和控制条复用 `grps` 原图及元数据。

正文默认字号 22、每行 19 个全角字宽、行距 7；文本对象默认每行 20 字宽。
折行按最终字体的真实字形前进量和统一禁则处理，显式 `^n` 仍保留。
标题设置可调整字体、字号、行字数、行距和语言，并备份、读取或清除持久化进度；
清除进度时保留备份。显示速度由游戏内右键菜单控制。

附带 Noto Sans CJK JP Regular、Noto Sans CJK Light 和 Noto Serif CJK Regular，
默认使用 JP Regular。旧 SimHei 默认值只迁移一次，其他已选字体保留；SimHei
仍可选择。也可在生成工程的 `game/fonts/` 放入 `.ttf`、`.otf` 或 `.ttc` 文件。
字体授权见 [SimHei 说明](../port_template/fonts/SimHei-NOTICE.md)，
原程序字体与混合文本度量依据见 [Forest 字体分析](../docs/FOREST_FONT_ANALYSIS.md)。

通用 32×32 光标来自 Forest 原版，安装到 `game/engine/gui/rscript_cursor.png`，
其他适配也共用这一资源。代码、字体、图标与光标的授权说明见
[第三方声明](../THIRD_PARTY_NOTICES.md)。

## 验证与限制

```bash
python3 -B tests/test_forest_validation.py
python3 -B tests/test_forest_builder.py /path/to/Forest
python3 -B tests/test_shared_port.py /path/to/renpy-sdk --logic-only
/path/to/renpy-sdk/renpy.sh /path/to/renpy/Forest lint
```

媒体检查先查看 `python3 tests/test_forest_resources.py --help`，文字与共用运行时
测试见 [主说明](../README.md#验证)。
鉴赏返回的回归检查覆盖已清除对象的锚点重置及重复返回后的缩略图坐标。
Ren'Py 的自定义跳转和原脚本死分支可能产生不可达语句提示，不能据此确认路线。
生成、测试或 lint 不证明实际画面、语音时序、完整路线、跨语言存档或 Android
实机表现；这些仍需用户对照原游戏验证。不发布游戏本体或构建后的游戏包。

## English

### Overview and preparation

This adapter builds Forest for Ren'Py 8 using the shared runtime and template.
It does not download, locate or modify an installed game. Prepare legally owned
resources with current LiarsoftTool (format validation used 2.2.2):

```bash
liarsofttool -R --unpack-only --gsc-to-tsc /path/to/Forest
python3 forest/build_forest_rscript.py /path/to/Forest /path/to/renpy/Forest
```

Use current `legacy-28/early` command-based `scr/*.tsc`, converted `grp*` images
with `.meta.xml`, Ogg under `bgm/voice/wav`, and original `mov/0002.mpg` and
`mov/0001.mpg`. TSC text is UTF-8; choose the source GSC encoding separately.
GSC and old structure dumps are not generator inputs. Python 3 and Pillow are
required; output does not need an existing `gui.rpy` or empty Ren'Py project.

### Generation and language patches

Run examples from the repository root. Rebuilding overwrites generated files;
back up manual changes first. Legacy layouts and `persistent.forest_*` settings
are not migrated. Scripts live in `game/scr`, shared engine files in
`game/engine`, language resources in `game/tl/<language>`.

Without a language marker, the base language is labelled `Original`.
`--language NAME` names the base language; `--language NAME=PATCH_DIR` adds a
switchable language. Names must be valid Ren'Py identifiers, and options may
repeat. Generated menu prompts use English; language labels are shown verbatim.
Patches need only changed files at their original relative paths.

Ordinary scenes align text by command position. Existing `TXT/TXA/select/font`
can be translated, and voice-only passages may add `font` subtitles with related
`cls` and `wait` commands, enabled only for that language. Approved non-text
display/audio operands may also be overridden; arbitrary gameplay changes are
rejected. The same sentence can have different translations at different positions.

`5000.tsc` instead selects a complete credits script for each language. Rollback
and menus are disabled during credits. Load only trusted patches; structural
changes and switching languages mid-game may affect save compatibility.

### Settings and verification

Wiki data uses `keywords.json`, allowing `//` comments and entries shaped as
`["complete sentence", "https://URL", "text between ^cg and ^cw"]`.
Wiki is off by default and toggled from the Chinese in-game artwork, not title
settings. Links require both the full sentence and marked word to match the
current language; disabled Wiki words remain white.

Defaults are 22px, 19 full-width dialogue characters, 20 for text objects, and
7px line spacing. Wrapping uses shaped glyph advances and preserves explicit
breaks. Title settings provide fonts, layout, language and persistent-progress
backup/restore/clear; clearing keeps the backup. Speed is controlled in-game.
Noto Sans CJK JP Regular is the default; Light and Serif are also included.
SimHei remains selectable and separately licensed; the old default is migrated
once. Additional font files may be placed in `game/fonts`.

Startup movies play once per launch, not on returning to the title. Android
configuration and adaptive icons are generated, but do not prove APK/device
compatibility; signing keys remain local. The original Forest cursor is shared
with other ports. See the [main guide](../README.md) and
[third-party notices](../THIRD_PARTY_NOTICES.md) for common behavior and licensing.

Use the checks above after generation. Algorithm tests, SDK checks and lint are
separate from visual/audio accuracy, full playthroughs, saves and device testing.
