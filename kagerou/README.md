# KagerouTouryuuki 移植说明

[返回主说明](../README.md) · [通用模板](../port_template/README.md)

## 概述

本目录正在建立《霞外籠逗留記》的 Ren'Py 8 适配。目前完成输入审计与
`excmd` 原生调用模型，**尚未提供可游玩的工程生成器**。
除用户明确允许沿用的启动视频流程外，不直接复制其他游戏的语义实现；
指令和显示行为先核对本作 EXE，未确认的效果不猜测。
仓库不包含游戏本体；以下命令均在仓库根目录执行。

## 准备资源

资源预处理依赖当前 [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool)。
保留原版与补丁各自的 EXE、原始 GSC，并在工作副本转换图像、音频和 TSC；
不要覆盖手工修改过的脚本。当前样本的 `scr/*.tsc` 为 `modern-36` 字节格式，
混用 `modern` 与 `rscript19` schema，不能整批强行指定成 Forest 方言。
`modern-36` 不代表所有场景具有同一种指令表。

原版资源包括 `grpe/grpo/grpo_bu/grps/bgm/voice/wav/mov/scr`。
保留 `grps` 的 `.meta.xml`；封装 WAV 中的 Ogg 必须先提取。
输入资源只读使用，不将游戏资源或 EXE 提交到本仓库。

## 生成工程

目前先执行只读审计，不生成 Ren'Py 工程：

```bash
python3 kagerou/inspect_kagerou.py /path/to/KagerouTouryuuki \
    --patch /path/to/KagerouTouryuuki_CHS
```

结果以 JSON 输出到终端，包含 EXE 哈希、原生处理函数地址、脚本数量、schema、
指令频次、补丁缺失场景和启动视频存在性。工具不执行 EXE，不解码 GSC，
不改变输入文件，仅接受已审计的两个 EXE 哈希；其他版本需要重新确认地址。

## 语言补丁

当前中文补丁有 140 个 TSC，原版有 147 个。审计会列出缺失的七个系统场景，
后续生成器应保留原版回退，不能只安装补丁脚本。
补丁 EXE 的 `.text` 只有两个字节变化，均为字体字符集参数，但这不证明
补丁剧本只有文本变化。语言补丁的结构对齐和图像替换尚未实现。

## 适配说明

证据、地址及未确认部分见 [NATIVE_EVIDENCE.md](NATIVE_EVIDENCE.md)。
`native.py` 的 `excmd_calls` 记录原生调用顺序及寄存器 20 的写入；
坐标、未选中角色绘制设置和队列状态由调用方显式传入，不设置猜测的默认值。
该模型尚未接入 Ren'Py 图像层，不代表立绘效果已经可以显示。

启动视频允许沿用“仅进程启动时播放 `0002.mpg`，然后 `0001.mpg`”的流程，
返回标题不重复播放。原版 EXE 也引用这两条路径，但当前原版资源缺少
`0001.mpg`；后续生成器应明确警告并跳过缺失文件，不用 `0003.mpg` 替代。
`0003.mpg` 属于五处结局剧本调用，不能加入启动流程。

## 验证与限制

```bash
python3 -B tests/test_kagerou_native.py
python3 -B tests/test_kagerou_native.py \
    /path/to/KagerouTouryuuki /path/to/KagerouTouryuuki_CHS
```

第一条检查原生调用模型及输入错误；第二条追加真实 EXE 表读取、147/140
场景统计、两个字体补丁字节和输入哈希不变检查。
静态分析与调用模型测试不等于画面验证，也不等于整个引擎已实现。
尚需确认初始化配置、绘制模式的像素算法、文字框与追加/清屏行为、转场、
音频及系统菜单，再实现生成器、SDK 测试和 lint；完整路线和实际画面仍需用户验证。
