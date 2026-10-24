# 开发记录：2026-10-12 安全与公共层整理

[中文](OPTIMIZATION_REPORT_2026-10-12.zh.md) | [English](OPTIMIZATION_REPORT_2026-10-12.en.md) | [Русский](OPTIMIZATION_REPORT_2026-10-12.ru.md) | [日本語](OPTIMIZATION_REPORT_2026-10-12.ja.md)

[返回文档目录](README.zh.md)

这是历史开发记录，不是安装指南。当前用法以 [主说明](../README.zh.md) 为准。

## 整理范围

| 仓库 | 内容 |
| --- | --- |
| LiarsoftTool | GSC/TXT 输入检查、严格编码、CLI/GTK 公共转换入口 |
| 两仓库 | 文件级安全写入、输入输出目录检查 |
| rscript2renpy | 减少重复复制、统一脚本和配置安装 |

两个仓库保持独立。没有改变游戏指令语义，也没有新增构建数据库或插件框架。

## 当时的检查结果

- Linux CTest 11 项通过，Windows/Wine 10 项通过。
- Python 公共层与 Forest/Khime 最小工程检查通过。
- Forest lint 通过；Khime 有三项既有的持久化默认值重复声明。
- 有效 GSC/TXT 资源与旧实现比较，Forest/Khime 共 444 个输出一致。

以上仅描述该日期的检查，不代表当前版本或完整游戏验收。

## 后续维护

文件级保护不等于整工程更新事务，构建中断后需重新构建。
相关检查位于 `tests/test_file_install.py`、`tests/test_shared_port.py`
以及 LiarsoftTool 的 CTest。按实际改动选择测试，不在用户指南中追加测试流水账。
