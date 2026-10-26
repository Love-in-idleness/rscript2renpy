# 开发规划

[中文](ROADMAP.zh.md) | [English](ROADMAP.en.md) | [Русский](ROADMAP.ru.md) | [日本語](ROADMAP.ja.md)

[主说明](../README.zh.md)

## 持续改进

完善已支持游戏的兼容性与运行检查，优先修复公共运行时中的问题。
游戏版本、功能和限制以各游戏指南为准。

资源解包与转换继续由独立项目 LiarsoftTool 负责；
本项目专注于 TSC 到 Ren'Py 的生成和运行。

## 长期目标：实验性 `--pure-renpy`

计划增加独立后端，将 TSC 转成原生 Ren'Py 语句，可配合标准 Python、screen 和 ATL，
不携带 TSC 解析器或运行时指令分发器。

此后端尚未实现，当前没有 `--pure-renpy` 开关。
指令覆盖、存档兼容和迁移方案将在开发时确定。

TSC 编辑工具由 [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool/blob/master/docs/ROADMAP.md) 维护。
