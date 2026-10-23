# SevenBridge · [中文](#中文) | [English](#english) | [Русский](README.ru.md)

[返回主说明](../README.md)

## 中文

### 概述

将《SEVEN-BRIDGE》的日文资源生成为 Ren'Py 8 工程。
本适配以日文 `SBridge_jp.exe` 为依据，暂不支持中文补丁。

### 准备资源

安装依赖见[环境配置](../docs/SETUP.md)。复制原游戏资源，在副本上用
LiarsoftTool 递归解包并转换，保留当前格式的 `scr/*.tsc`、图像、
`.meta.xml`、OGG 与普通 PCM WAV。转换参数见 `liarsofttool -h`。

需要 `scr`、`grpe`、`grpo`、`grpo_bu`、`grpo_ex`、`grps`、`bgm`、
`voice` 和 `wav` 目录。语音中的子目录也须解包，不能只提取最外层。
把原游戏的 `mov` 目录一并复制到资源副本，保留 `0002.mpg`、
`0003.mpg` 和 `0004.mpg`。启动时播放 `0002`，`0003/0004` 由剧本调用。

### 生成工程

在仓库根目录执行：

```bash
python3 sevenbridge/build_sevenbridge_rscript.py /path/to/prepared-sevenbridge /path/to/renpy-sevenbridge
```

重新生成时先备份手工修改；`--force` 允许覆盖不同内容的生成文件。

### 语言补丁

当前只生成日文剧本，没有接入其他语言补丁。

### 使用说明

保留原作主菜单，其“环境设置”打开已有的 Text Settings；
游戏内控制栏、右键菜单和存读档界面使用原作素材，
按 `.meta.xml` 布局。各目录用途见[通用界面资源分工](../port_template/README.md#界面资源分工)。
字体、字号和折行可在
共用文字设置中调整。进度与鉴赏解锁保存在独立的 Ren'Py 持久化数据中，
不会读取或覆盖原游戏的存档。

### 检查与已知限制

按[主说明](../README.md)运行 Ren'Py lint，再检查实际画面、音频和路线。
缺少 `mov` 时不能播放对应视频。Android 实机与完整游玩仍需验证。
原程序的版本与实现依据见[开发参考](NATIVE_EVIDENCE.md)。

## English

### Overview

Build a Ren'Py 8 project from the Japanese SEVEN-BRIDGE resources.
This adapter targets `SBridge_jp.exe`; Chinese patches are not supported yet.

### Prepare resources

Follow [environment setup](../docs/SETUP.md). Work on a copy of your game and
use LiarsoftTool to unpack recursively and convert resources. Keep current
`scr/*.tsc`, images, `.meta.xml`, OGG and ordinary PCM WAV files.
See `liarsofttool -h` for conversion options.

Required directories: `scr`, `grpe`, `grpo`, `grpo_bu`, `grpo_ex`, `grps`,
`bgm`, `voice` and `wav`. Unpack nested voice archives too.
Copy the original `mov` directory into the resource working copy, including
`0002.mpg`, `0003.mpg` and `0004.mpg`. Startup plays `0002`;
the scenarios call `0003/0004`.

### Generate the project

Run from the repository root:

```bash
python3 sevenbridge/build_sevenbridge_rscript.py /path/to/prepared-sevenbridge /path/to/renpy-sevenbridge
```

Back up manual edits before rebuilding. `--force` replaces differing generated files.

### Language patches

Only Japanese scenarios are currently supported.

### Using the port

The original main menu is retained; its settings button opens Text Settings.
In-game controls, the right-click menu and save/load
screens use original artwork with `.meta.xml` layouts. See the
[shared UI resource map](../port_template/README.md#ui-resource-map-english) for each directory's role.
Shared text settings let you change fonts, size and wrapping.
Progress and gallery unlocks use separate Ren'Py persistent data and do not
read or overwrite native saves.

### Checks and limitations

Run Ren'Py lint as described in the [main guide](../README.md), then check
graphics, audio and routes in the game. Missing `mov` files cannot be played.
Full playthroughs and Android devices still require verification.
See [native evidence](NATIVE_EVIDENCE.md) for the supported executable.
