# 开发规划

[中文](ROADMAP.zh.md) | [English](ROADMAP.en.md) | [Русский](ROADMAP.ru.md) | [日本語](ROADMAP.ja.md)

[主说明](../README.zh.md)

## 当前方向

- 先完成 SevenBridge 日文移植的构建与运行检查，再继续扩展其他游戏。
- 公共能力保留在模板和运行时；游戏差异根据本作 EXE 与脚本确认。
- 中文、英文、俄语和日语说明随功能同步。
- 与 LiarsoftTool 保持独立：资源解包、编码、图像和音频转换由 LiarsoftTool 负责。

## 长期规划：实验性 `--pure-renpy`

未来增加独立生成后端，将 TSC 剧情转换为原生 Ren'Py 语句。
可以使用标准 Python、screen 和 ATL，但生成工程不携带 TSC 解析器或
运行时指令分发器。

本轮不实现，也不提供占位开关。当前生成器仍使用 RScript 兼容运行时。
具体指令范围、存档兼容性和迁移方式留待该阶段确定。

图形化 TSC 编辑器属于 LiarsoftTool 的长期规划，见
[对应规划](https://github.com/Love-in-idleness/LiarsoftTool/blob/master/docs/ROADMAP.md)。
