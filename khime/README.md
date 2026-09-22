# Khime Kusaritop Ren'Py 移植

本目录从 [`port_template/`](../port_template/README.md) 派生，用于
《霞外籠逗留記（Khime Kusaritop）》的游戏专用适配。通用运行时仍由仓库根目录的
`runtime/` 提供，不在这里复制。

## 当前状态

目前只建立了适配目录和装配入口。Khime 的 TSC → RPY lowerer 尚未实现，因此
构建前仍需有游戏专用 lowerer 生成的 `scenario/*.rpy`；入口会在缺少这些文件时
明确报错，不会生成内容不完整但看似可运行的工程。

## 原始资源结构

Khime 的基础资源位于 XFL/LWG 归档，中文补丁以同名松散目录覆盖基础资源。正确
顺序是：

1. 用当前 LiarsoftTool 解包基础归档并转换 WCG/LWG/WAV；
2. 从 `scr/*.gsc` 重新生成当前格式 TSC，不使用旧 `tsc/` 目录里的过时结果；
3. 转换并覆盖松散的 `grpe/`、`grpo_ex/`、`grps/`、`bgm/` 和 `voice/`；
4. 游戏专用 lowerer 把 TSC 写成 `scenario/*.rpy`；
5. 本目录的构建入口安装通用运行时并装配 Ren'Py 工程。

中文脚本使用 GBK/CP936。资源覆盖时必须保留相对路径，补丁文件最后写入。

## 构建入口

先从 Ren'Py 8 启动器建立空工程，然后执行：

```bash
python3 khime/build_khime_rscript.py \
    /path/to/prepared-khime /path/to/renpy-project
```

可使用 `--force` 同步已经确认的模板/运行时更新；默认拒绝覆盖内容不同的文件。

## 下一步适配

- 解析 LiarsoftTool 当前的 `modern`、`rscript18` 和 `rscript19` TSC
- 保留 VM、局部跳转、`gosub`/`insub` 参数及选择支，不做参数扁平化
- 实现 Khime 使用的 `face`、`facedep`、`faceloc` 和数字显示命令
- 对齐 `folder` 资源映射、文本框、姓名、voice、标题流程及菜单
- 生成全部场景后运行静态测试和 Ren'Py 8 lint

视觉、音频和完整剧情流程仍需由用户在原游戏与 Ren'Py 工程中对照确认。
