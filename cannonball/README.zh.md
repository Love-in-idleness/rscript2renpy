# CannonBall 移植说明

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[返回主说明](../README.zh.md)

## 概述

将用户自备的 CannonBall 资源生成 Ren'Py 8 工程。
当前适配仍在完善，以下命令均在仓库根目录执行。
环境安装见 [首次构建](../docs/SETUP.zh.md)。

## 准备资源

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/CannonBall
liarsofttool -R --unpack-only --gsc-to-tsc -e gbk /path/to/CannonBall.zh
```

原版和补丁分别转换。保留 `scr/*.tsc`、全部 `grp*` 图像目录、
`bgm/voice/wav` 和已有的 `mov` 视频。
标题需要 `grpe/0901` 和 `bgm/Track01.wav`。
普通 PCM WAV 与原始 MPG 可以直接使用，封装 WAV 中的 Ogg 需先提取。
中文示例适用于 GBK 补丁，其他版本按实际编码选择。

## 生成工程

```bash
python3 cannonball/build_cannonball_rscript.py \
    /path/to/CannonBall /path/to/renpy/CannonBall
```

输出目录可由脚本创建。重建前备份手工修改，并加上 `--force`。
普通生成不需要原游戏 EXE。

## 语言补丁

```bash
python3 cannonball/build_cannonball_rscript.py \
    /path/to/CannonBall /path/to/renpy/CannonBall \
    --language jp --language zh=/path/to/CannonBall.zh
```

`--language jp` 命名原版语言，`--language zh=目录` 添加补丁。
补丁按原资源的相对路径放置，只需提供修改的文件。

本作采用整场景覆盖，保留补丁自己的分支和新增场景。
当前中文补丁与原版有剧情流程差异，生成器不会将它自动改回日文流程。
请只使用可信补丁，避免在剧情结构不同的语言之间中途切换。

## 使用说明

设置、存读档、文字选项和控制条使用原游戏图片。
赛车画面禁止回退与存档，退出后恢复正常权限。
启动视频依次播放 `0002.mpg`、`0001.mpg`，返回标题不重播。

共用光标、字体与本作图标授权见 [第三方声明](../THIRD_PARTY_NOTICES.zh.md)。

## 检查与已知限制

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/CannonBall lint
```

- 历史文本页外观尚未完全还原。
- 部分转场、音乐淡化与原版可能有差异。
- 中文补丁的流程来源、跨语言存档及完整赛车、战斗、剧情路线需另行检查。
- Android 需要实机测试。

开发测试：`tests/test_cannonball_port.py`。
原程序依据及效果清单见 [开发参考](NATIVE_EFFECTS.zh.md)。
