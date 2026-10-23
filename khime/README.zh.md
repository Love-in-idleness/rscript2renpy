# Khime Kusaritop 移植说明

[中文](README.zh.md)

[返回主说明](../README.zh.md)

## 概述

将用户自备的《腐り姫》资源生成 Ren'Py 8 工程，可选接入外传《帰省 ～jamais vu～》。
以下命令均在仓库根目录执行，环境安装见 [首次构建](../docs/SETUP.md)。

## 准备资源

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/Khime
```

保留 `scr/*.tsc`、`grp*` 图像目录、`.meta.xml`、`bgm/voice/wav` 和 `mov`。
封装在 WAV 中的 Ogg 应先提取；普通 PCM WAV 和原始 MPG 可以直接使用。
补丁单独转换，编码按实际文件选择。

## 生成工程

```bash
python3 khime/build_khime_rscript.py /path/to/Khime /path/to/renpy/Khime
```

输出目录可由脚本创建。重建前备份手工修改，并加上 `--force`。
从旧版生成器升级时，建议使用新的输出目录。

## 语言补丁

```bash
python3 khime/build_khime_rscript.py /path/to/Khime /path/to/renpy/Khime \
    --language jp --language zh=/path/to/Khime.zh
```

`--language jp` 命名原版语言，`--language zh=目录` 添加补丁。
补丁按原资源的相对路径放置，只需提供修改的 TSC、图像和音频。

支持翻译对话、追加文字、选项与文字对象，以及添加字幕和配套等待、清除指令。
普通补丁不能任意修改剧情逻辑；缺少的场景使用原版。
CodeX BMP 的透明度由 LiarsoftTool 预处理，生成器直接复制图片。

### 可选外传

准备好外传及补丁后追加参数：

```bash
python3 khime/build_khime_rscript.py /path/to/Khime /path/to/renpy/Khime \
    --language jp --language zh=/path/to/Khime.zh \
    --khime-zero /path/to/Khime_zero \
    --khime-zero-language zh=/path/to/Khime_zero.zh
```

目前接入外传的 `scr/2001.tsc`，不接入它的独立标题。
入口在本篇原标题满足解锁条件后显示，外传资源不会覆盖本篇同编号图片。
未提供外传补丁时使用原文。

## 使用说明

标题设置可以调整字体、字号、行字数、行距、语言及系统进度。
默认字号 29，对话每行 21 字宽；显示速度和音量在游戏内设置中调整。
启动视频每次打开游戏只播放一次，返回标题不重播。

共用光标、字体与图标授权见 [第三方声明](../THIRD_PARTY_NOTICES.md)。

## 检查与已知限制

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/Khime lint
```

部分图像效果及数字控件尚未完全还原，外传 BGM 暂无淡入淡出。
请检查完整路线、鉴赏、字幕、音频及旧存档；Android 需另行测试。

开发测试：`tests/test_khime_builder.py`、`tests/test_khime_zero.py`、
`tests/test_shared_port.py`。引擎行为分析见 [开发参考](../docs/README.zh.md#开发参考)。
