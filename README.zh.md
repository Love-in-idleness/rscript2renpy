# rscript2renpy

[中文](README.zh.md) | [English](README.en.md)

`rscript2renpy` 是面向 CodeX RScript 游戏（主要来自 Liar-soft / raiL-soft）的
Ren'Py 8 兼容运行时与移植工具。

首次使用见 [环境配置与首次构建](docs/SETUP.md)；开发尚未支持的游戏见
[新游戏移植指南与 AI 提示词](docs/NEW_GAME_PORTING.md)。
后续目标见[开发规划](docs/ROADMAP.zh.md)。

除通用鼠标光标和各游戏应用图标外，仓库不包含游戏剧本、图像、音频、视频或
可执行文件。用户必须使用自己合法持有的游戏文件，自行准备资源并构建工程。

## 游戏移植说明

各游戏的资源要求、生成命令和语言补丁用法分别维护在对应目录。
命令示例均在仓库根目录执行。

| 项目 | 说明 |
| --- | --- |
| Forest | [forest/README.zh.md](forest/README.zh.md) |
| Khime Kusaritop（含可选 Khime Zero） | [khime/README.zh.md](khime/README.zh.md) |
| Evermaiden | [evermaiden/README.zh.md](evermaiden/README.zh.md) |
| CannonBall | [cannonball/README.zh.md](cannonball/README.zh.md) |
| SevenBridge（日文版） | [sevenbridge/README.zh.md](sevenbridge/README.zh.md) |
| KagerouTouryuuki（适配中，仅支持安装「ハチポチ特典」后） | [kagerou/README.zh.md](kagerou/README.zh.md) |

## 依赖与资源预处理

需要 Python 3、Pillow 和 Ren'Py 8 SDK。资源解包与转换依赖
[LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool)。

先复制游戏资源，再用 LiarsoftTool 解包、生成 TSC 并转换图像和音频。
然后运行对应游戏的生成脚本。生成器只读取 TSC，不处理 GSC。

## 通用模板与输出

新移植从 [通用模板](port_template/README.zh.md) 开始。
共用运行时位于 `runtime/`，构建和界面位于 `port_template/`，
游戏差异位于各适配目录。开发分工见 [公共模板说明](docs/SHARED_TEMPLATE_MIGRATION.md)。
界面素材用途、`.meta.xml` 布局和主菜单环境设置入口约定见
[通用界面资源分工](port_template/README.zh.md#界面资源分工)。

生成工程保留原资源目录：剧本在 `game/scr/`，图像在 `game/grp*/`，音频在
`game/bgm/`、`game/voice/`、`game/wav/`，视频在 `game/mov/`。
运行时、公共界面和配置在 `game/engine/`；语言资源在 `game/tl/<语言>/`。

只安装通用运行时：

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

已有不同内容的文件不会直接覆盖。各生成器附带共用光标和 Android 启动说明。

## 检查与反馈

生成后，使用 Ren'Py SDK 的 lint 检查工程：

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy-project lint
```

再对照原游戏检查画面、语音、选项和存读档。遇到问题时，请提供游戏版本、
构建命令、报错或截图，以及对应场景。开发测试与技术参考见 [文档目录](docs/README.zh.md)。

## 授权

代码采用 [MIT License](LICENSE)。第三方代码、光标、图标和字体说明见
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
Noto CJK 字体采用 [SIL Open Font License 1.1](port_template/fonts/NotoSans.txt)；
SimHei 的授权独立，见 [字体说明](port_template/fonts/SimHei-NOTICE.md)。
