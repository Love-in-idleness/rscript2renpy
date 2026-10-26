# rscript2renpy

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

将 CodeX RScript 游戏的 TSC 剧本与资源生成为 Ren'Py 8 工程，供持有原游戏的使用者自行构建。
本项目提供兼容运行时与各游戏生成器，不是适用于所有游戏的一键转换器。

## 开始使用

需要 Python 3、Pillow、Ren'Py 8 SDK，以及用于解包和转换资源的
[LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool)。

1. 按[环境配置与首次构建](docs/SETUP.zh.md)安装工具。
2. 复制合法持有的游戏文件，用 LiarsoftTool 准备资源和 TSC。
3. 按下表中的游戏指南生成、检查并运行工程。

输入资源和输出工程应使用不同目录。生成器只读取 TSC，不处理 GSC。

## 游戏指南

| 游戏 | 支持范围与构建说明 |
| --- | --- |
| Forest | [构建与语言补丁](forest/README.zh.md) |
| Khime Kusaritop | [构建、语言补丁与可选 Khime Zero](khime/README.zh.md) |
| Evermaiden | [构建与语言补丁](evermaiden/README.zh.md) |
| CannonBall | [构建与语言补丁](cannonball/README.zh.md) |
| SevenBridge | [日文版构建](sevenbridge/README.zh.md)，暂不接入语言补丁 |
| KagerouTouryuuki | [特典版构建](kagerou/README.zh.md)，仅支持安装「ハチポチ特典」后 |

各适配的功能与限制见游戏指南；能成功生成工程不等于所有路线均已验证。
语言补丁由使用者另行准备。

## 开发与反馈

- [文档目录](docs/README.zh.md)：使用指南与技术参考。
- [新游戏移植指南](docs/NEW_GAME_PORTING.zh.md)：适配步骤与可填写的 AI 提示词。
- [通用模板](port_template/README.zh.md)：公共能力、界面素材与布局约定。
- [工作约定](AGENTS.zh.md) · [开发规划](docs/ROADMAP.zh.md)。

反馈问题时，请提供游戏版本、生成命令、场景位置及完整报错或截图。
不要公开上传游戏资源、存档或密钥。

## 授权与资源

代码采用 [MIT License](LICENSE)。仓库不包含游戏剧本、图像、音频、视频或 EXE，
但包含通用光标和游戏应用图标；来源见[第三方声明](THIRD_PARTY_NOTICES.zh.md)。

字体分别适用自己的授权：[Noto CJK](port_template/fonts/NotoSans.txt)、
[SimHei](port_template/fonts/SimHei-NOTICE.zh.md)。分发生成工程前请核对资源授权。
