# 通用 RScript 移植模板

[返回主说明](../README.md) · [新游戏移植指南](../docs/NEW_GAME_PORTING.md)

这个目录为新适配提供共用的剧本编译、工程生成和界面。
它不是可以直接用于所有 RScript 游戏的一键转换器。

## 输入与输出

先用 LiarsoftTool 准备游戏资源：

- 当前格式的 `scr/*.tsc`。
- PNG、WebP、JPG、BMP 和 BMP 格式的 MSK 遮罩。
- 可播放的 OGG 或普通 PCM WAV。
- 原始 MPG 视频与图像的 `.meta.xml`。

CodeX BMP 的反向 Alpha 由 LiarsoftTool 规范化。
本项目直接复制 BMP/MSK，不再转成 PNG。

生成后的剧本在 `game/scr/`，运行时和界面在 `game/engine/`，
媒体保留原目录名。语言资源放在 `game/tl/<语言>/`。

## 开始新适配

1. 建立 `<游戏目录>/`，不要复制一套 `runtime/` 或 `port_template/`。
2. 确认本作的指令方言和资源要求，使用公共 TSC 编译器编译剧本。
3. 用 `assemble_port` 装配工程，游戏差异放在本目录下的 `game/*.rpy`。
4. 提供接受“资源目录、输出目录”的生成命令和 `--help`。
5. 在游戏 README 写支持版本、资源准备、构建、补丁用法和已知限制。

覆盖已有工程前检查手工修改。不要把生成工程当作唯一的修复位置。

## 共用功能

| 功能 | 说明 |
| --- | --- |
| 文字 | 对话、追加、文字对象、控制符、注音和折行 |
| 设置 | 字体、字号、行字数、行距、语言及系统进度备份 |
| 原图界面 | 设置页、选项、控制条、存读档 |
| 音频 | BGM、音效、语音、重播及自动推进 |
| 语言包 | 文本补丁、字幕插入和游戏专用的整场景覆盖 |
| Android | 触摸控制条、截图、图标和项目启动说明 |

界面优先读取 `.meta.xml` 的布局。不同资源命名或按钮行为需要适配，
不能仅靠图片文件名猜动作。存档槽位可使用原游戏章节图与 `saveconf` 组件。

启动视频默认按 `0002.mpg → 0001.mpg` 播放，每次启动一次。
特殊游戏可配置 `rscript_boot_movies`。

## 游戏差异

每款游戏都要确认：入口和跳转、寄存器、图片坐标和层次、音频编号、
文本规则、菜单、存读档、回滚、持久化与鉴赏。

不能复用的行为应从本作 EXE、脚本和实际效果确认。
未实现的效果应明确标注，不要静默丢弃剧情指令。

## 开发入口

| 文件 | 职责 |
| --- | --- |
| `tsc_compiler.py` | 公共剧本编译 |
| `tsc_patches.py` | 语言补丁与字幕对齐 |
| `build_port.py` | 工程与资源装配 |
| `port_resources.py` | 媒体、语言资源和词条 |
| `grps_layout.py` | 图像元数据布局 |
| `effect_compat.py` | 效果兼容检查 |
| `game/` | 共用 Ren'Py 界面 |
| `../runtime/` | RScript 运行时 |

接口分工见 [开发架构](../docs/SHARED_TEMPLATE_MIGRATION.md)，
文字规则见 [文字布局参考](../docs/TEXT_WRAPPING.md)，
测试入口见 [文档目录](../docs/README.md#开发检查)。
