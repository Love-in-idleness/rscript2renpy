# Forest 移植说明

[返回主说明](../README.md) · [English](#english)

## 概述

将用户自备的 Forest 资源生成 Ren'Py 8 工程。以下命令均在仓库根目录执行。
环境安装见 [首次构建](../docs/SETUP.md)。

## 准备资源

在游戏工作副本中解包并转换：

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/Forest
```

保留 `scr/*.tsc`、原来的 `grp*` 图像目录及 `.meta.xml`、
`bgm/voice/wav` 音频和 `mov` 视频。
标题需要 `grpe/9001` 与 `bgm/Track01.ogg`；启动视频为 `0002.mpg`、`0001.mpg`。
语言补丁在自己的工作副本中单独转换，编码按实际文件选择。

## 生成工程

```bash
python3 forest/build_forest_rscript.py /path/to/Forest /path/to/renpy/Forest
```

输出目录可由脚本创建。重建会覆盖生成文件，请先备份手工修改。
从旧版生成器升级时，建议使用新的输出目录。

## 语言补丁

```bash
python3 forest/build_forest_rscript.py /path/to/Forest /path/to/renpy/Forest \
    --language jp --language en=/path/to/Forest.en \
    --language zh=/path/to/Forest.zh
```

- `--language jp` 设置原版的语言标签；省略时显示为 `Original`。
- `--language zh=目录` 添加可切换的补丁语言，可以重复传入。
- 补丁按原游戏的相对路径放置，只需提供修改的文件。
- 标签是菜单里显示的名称，不负责选择资源编码。

普通场景可翻译已有对话、选项与文字对象，也允许给只有语音的段落添加
`*font` 字幕及配套的等待、清除指令。不要任意改变剧情分支或指令顺序。

`5000.tsc` 单独处理：按语言使用整份结局脚本，播放期间禁止回退和打开菜单。
只使用可信补丁；不同剧情结构的语言包不宜在游戏中途切换。

### Wiki 词条

在补丁根目录提供 `keywords.json`：

```json
[["完整句子", "https://example.com/wiki", "句子中被 ^cg 和 ^cw 标记的词"]]
```

词条必须与当前语言的句子匹配。Wiki 默认关闭，从中文版游戏内右键菜单切换，
标题设置中没有此开关。

## 使用说明

- 启动视频每次打开游戏只播放一次，返回标题不重播。
- 标题设置可以调整字体、字号、每行字数、行距和语言，以及备份、恢复或清除系统进度。
- 默认字号 22，对话每行 19 个全角字宽；文字对象默认每行 20 字宽。
- 在生成工程的 `game/fonts/` 中放入 TTF、OTF 或 TTC，可添加字体。
- 游戏内右键菜单控制显示速度、音量及存读档。

光标、图标与字体授权见 [第三方声明](../THIRD_PARTY_NOTICES.md)。

## 检查与已知限制

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/Forest lint
```

请实际检查字幕、语音、图片选项、鉴赏返回和存读档。
旧存档、跨语言切换及 Android 仍需按自己的资源版本测试。

开发测试：`tests/test_forest_validation.py`、
`tests/test_forest_builder.py`、`tests/test_shared_port.py`。
共用文字规则见 [文字布局参考](../docs/TEXT_WRAPPING.md)。

## English

### Overview

This adapter builds a Ren'Py 8 project from your own Forest resources.
Run examples from the repository root. See [setup](../docs/SETUP.md) for dependencies.

### Prepare resources

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/Forest
```

Keep `scr/*.tsc`, native `grp*` image folders and their `.meta.xml` files,
audio under `bgm/voice/wav`, and videos under `mov`.
The title requires `grpe/9001` and `bgm/Track01.ogg`.
Startup videos are `0002.mpg` and `0001.mpg`.
Prepare each language patch separately, using the encoding of its source files.

### Build

```bash
python3 forest/build_forest_rscript.py /path/to/Forest /path/to/renpy/Forest
```

The builder creates the output directory. Rebuilding overwrites generated files;
back up manual changes first. Use a new output directory when upgrading from an old builder.

### Language patches

```bash
python3 forest/build_forest_rscript.py /path/to/Forest /path/to/renpy/Forest \
    --language jp --language en=/path/to/Forest.en \
    --language zh=/path/to/Forest.zh
```

`--language jp` names the base language, otherwise labelled `Original`.
`--language NAME=DIR` adds a selectable language and may be repeated.
Include only changed files, using their original relative paths.
Language labels do not select file encodings.

Ordinary scenes support translated dialogue, choices and text objects.
Voice-only passages may add `*font` subtitles with related waits and clears;
arbitrary changes to story logic or command order are not supported.

`5000.tsc` uses a complete ending script for each language. Rollback and menus
are disabled during this scene. Use trusted patches and avoid switching between
different story structures during a playthrough.

For Wiki links, put `keywords.json` in the patch root, using entries shaped as
`["complete sentence", "https://example.com/wiki", "marked word"]`.
The sentence must match the current language and the word must be marked with
`^cg…^cw`. Wiki is off by default; toggle it in the Chinese in-game right-click menu,
not title settings.

### Settings and checks

Startup videos play once per launch. Title settings provide fonts, size, line
length, spacing, language and system-progress backup, restore and clear.
Dialogue defaults to size 22 and 19 full-width characters per line; text objects
default to 20. Add TTF, OTF or TTC files to `game/fonts/` for more fonts.
Use the in-game menu for text speed, audio and saving/loading.

Run lint as shown above, then check subtitles, voices, image choices, gallery
returns and saves in actual gameplay. Old saves, language switching and Android
need testing with your resource version.
See [third-party notices](../THIRD_PARTY_NOTICES.md) for asset licenses.
