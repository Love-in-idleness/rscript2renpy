# Evermaiden 移植说明

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md)

[返回主说明](../README.zh.md)

## 概述

将用户自备的 Evermaiden 资源生成 Ren'Py 8 工程。
当前适配仍在完善，以下命令均在仓库根目录执行。
环境安装见 [首次构建](../docs/SETUP.zh.md)。

## 准备资源

原版与补丁分别在工作副本中转换：

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/Evermaiden
liarsofttool -R --unpack-only --gsc-to-tsc -e gbk /path/to/Evermaiden.zh
```

保留 `scr/*.tsc`、全部 `grp*` 图像目录及 `.meta.xml`、
`bgm/voice/wav` 和 `mov`。中文示例适用于 GBK 补丁，其他版本按实际编码选择。
普通 PCM WAV 和原始 MPG 不必另行转换。

## 生成工程

```bash
python3 evermaiden/build_evermaiden_rscript.py \
    /path/to/Evermaiden /path/to/renpy/Evermaiden
```

输出目录可由脚本创建。重建前备份手工修改，并加上 `--force`。
本适配与旧版 Evermaiden 工程使用独立存档目录，不迁移旧工程进度。

## 语言补丁

```bash
python3 evermaiden/build_evermaiden_rscript.py \
    /path/to/Evermaiden /path/to/renpy/Evermaiden \
    --language jp --language zh=/path/to/Evermaiden.zh
```

`--language jp` 命名原版语言，`--language zh=目录` 添加补丁。
补丁按原资源的相对路径放置，只需提供修改的文件。

本作采用整场景覆盖：补丁里的分支、选项和新增 DLC 场景也会一起生效。
没有译文的场景使用原版。请只使用可信补丁，避免在剧情结构不同的语言之间中途切换。

## 使用说明

默认画布为 1280×720，字号 32，每行 28 个全角字宽。
标题设置可调整文字和语言；游戏内设置使用原图界面。
启动视频依次为 `0002.mpg`、`0001.mpg`，返回标题不重播。
地图选项、CG 和音乐鉴赏仍由原脚本控制。

共用光标、字体与本作图标授权见 [第三方声明](../THIRD_PARTY_NOTICES.zh.md)。

## 检查与已知限制

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/Evermaiden lint
```

- 部分效果、选项定位和字体选择外观与原版仍有差异。
- 当前资源样本中，`2320` 引用的 `voice/5/2703` 和
  `4250` 引用的 `wav/2527` 缺失；遇到无声时先核对素材。
- 完整路线、鉴赏操作、存档兼容及 Android 尚需实际测试。

开发测试：`tests/test_modern_port.py`。
具体实现和待办见 [运行时参考](../docs/EVERMAIDEN_RUNTIME_GAPS.zh.md)。
