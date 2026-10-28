# SevenBridge

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[返回主说明](../README.zh.md)

## 概述

将《SEVEN-BRIDGE》的日文资源与可选中文补丁生成为 Ren'Py 8 工程。
原作行为以日文 `SBridge_jp.exe` 为依据，语言补丁单独提供。

## 准备资源

安装依赖见[环境配置](../docs/SETUP.zh.md)。复制原游戏资源，在副本上用
LiarsoftTool 递归解包并转换，保留当前格式的 `scr/*.tsc`、图像、
`.meta.xml`、OGG 与普通 PCM WAV。转换参数见 `liarsofttool -h`。

需要 `scr`、`grpe`、`grpo`、`grpo_bu`、`grpo_ex`、`grps`、`bgm`、
`voice` 和 `wav` 目录。语音中的子目录也须解包，不能只提取最外层。
把原游戏的 `mov` 目录一并复制到资源副本，保留 `0002.mpg`、
`0003.mpg` 和 `0004.mpg`。启动时播放 `0002`，`0003/0004` 由剧本调用。

## 生成工程

在仓库根目录执行：

```bash
python3 sevenbridge/build_sevenbridge_rscript.py /path/to/prepared-sevenbridge /path/to/renpy-sevenbridge
```

重新生成时先备份手工修改；`--force` 允许覆盖不同内容的生成文件。

## 语言补丁

先把中文补丁中的 `scr.xfl`、`grps.xfl` 复制到独立目录，再用 LiarsoftTool 分别转换。
汉化脚本使用 **GBK**，但 `grps.xfl` 及内部 LWG 的成员文件名仍使用 **CP932**：

```bash
liarsofttool --unpack-only -R -e gbk /path/to/patch-copy/scr.xfl
liarsofttool --unpack-only -R -e cp932 /path/to/patch-copy/grps.xfl
```

不要对整个补丁目录统一使用 GBK，否则 `nonbl/１` 等全角数字文件名会被解错。
日文原版使用 CP932。生成器读取转换后的 `scr/*.tsc`，不直接读取 EXE、GSC 或封包。

保留补丁中的 `grps` 图像与 `.meta.xml`，让菜单、鉴赏、姓名牌和右键界面随语言切换。
日文原版仍作为完整资源基础；补丁不必重复提供未修改的素材。

```bash
python3 sevenbridge/build_sevenbridge_rscript.py /path/to/prepared-sevenbridge /path/to/renpy-sevenbridge \
    --language jp --language zh=/path/to/patch-copy
```

`--language jp` 设置原文标签；`zh=...` 添加可在 Text Settings 中选择的中文补丁。
补丁按完整场景覆盖，允许翻译脚本调整指令结构或增加场景；未提供的场景沿用日文。

## 使用说明

保留原作主菜单，其“环境设置”打开已有的 Text Settings；
游戏内控制栏、右键菜单和存读档界面使用原作素材，
按 `.meta.xml` 布局。各目录用途见[通用界面资源分工](../port_template/README.zh.md#界面资源分工)。
字体、字号和折行可在
共用文字设置中调整。进度与鉴赏解锁保存在独立的 Ren'Py 持久化数据中，
不会读取或覆盖原游戏的存档。

## 检查与已知限制

按[主说明](../README.zh.md)运行 Ren'Py lint，再检查实际画面、音频和路线。
缺少 `mov` 时不能播放对应视频。Android 实机与完整游玩仍需验证。
原程序的版本与实现依据见[开发参考](NATIVE_EVIDENCE.zh.md)。
