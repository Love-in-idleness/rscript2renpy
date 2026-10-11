# KagerouTouryuuki 移植说明

[返回主说明](../README.md) · [通用模板](../port_template/README.md)

## 概述

本目录提供《霞外籠逗留記》的实验性 Ren'Py 8 工程生成器，包括原版剧本、
可选中文资源和专用运行时。生成及自动测试不代表完整路线已经验证。
**只支持安装了「ハチポチ特典」后的游戏；未安装特典的旧版不支持。**
当前基准为 162 个 TSC 场景，包含特典剧情及更新后的鉴赏脚本。
除用户允许沿用的启动视频流程外，专用行为先核对本作 EXE；
未确认的效果明确降级，不猜测像素算法。仓库不包含游戏本体。
以下命令均在仓库根目录执行。

## 准备资源

资源预处理依赖当前 [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool)。
保留原版与补丁各自的 EXE、原始 GSC，并在工作副本转换图像、音频和 TSC；
不要覆盖手工修改过的脚本。当前 TSC 为 `modern-36`，混用 `modern` 与
`rscript19` schema，不能整批强行指定成 Forest 方言。

原版资源包括 `grpe/grpo/grpo_bu/grpo_ex/grps/bgm/voice/wav/mov/scr`。
`0302` 虽设置了 `grpo_cut` 文件夹，但当前语料未从该槽加载图片，
当前资源也无此归档，不将其列为必需目录；将来存在时按资源目录一起复制。
保留 `grps` 的 `.meta.xml`；封装 WAV 中的 Ogg 必须先提取。
生成器只读输入，不将游戏资源或 EXE 提交到本仓库。

## 生成工程

首次生成不用 `--force`；重建前备份手工修改，再明确加上：

```bash
python3 kagerou/build_kagerou_rscript.py \
    /path/to/KagerouTouryuuki /path/to/renpy/KagerouTouryuuki \
    --language jp --language zh=/path/to/KagerouTouryuuki_CHS
/path/to/renpy-sdk/renpy.sh /path/to/renpy/KagerouTouryuuki
```

生成器只读 TSC，不调用 LiarsoftTool。原版目录需要已审计的 `kagerou.exe`；
资源副本不含 EXE 时用 `--exe /path/to/kagerou.exe` 指定只读引用。
未确认 EXE 哈希会报错，不使用另一款游戏的坐标表代替。
输出包含 `game/scr`、`game/tl/zh/scr` 和 `kagerou-build.json`，后者记录
版本依据与限制。不复制原生 EXE、归档、源图编辑文件或原生存档。

只读审计入口：

```bash
python3 kagerou/inspect_kagerou.py /path/to/KagerouTouryuuki \
    --patch /path/to/KagerouTouryuuki_CHS
```

JSON 包含 EXE 哈希、处理函数地址、脚本数量、schema、指令频次、补丁缺失
场景和启动视频存在性。工具不执行 EXE，不解码 GSC，不改变输入文件。

## 语言补丁

当前原版有 162 个 TSC。中文补丁必须基于安装特典后的脚本重建，不能直接
套用旧版的 140 场景补丁；缺少的场景回退当前原版。
语言包按完整场景切换，图像与元数据按语言覆盖；不要求逐指令对齐，但补丁
剧情改动也会一起生效。补丁 EXE 的两个字体字符集字节变化不证明剧本只有文本变化。

旧中文 TSC 有 12 处命名入口缺少标签，应从原 GSC 按 GBK 重新导出，
保留对应 `L_xxxxxx` 标签。手工修改过 TSC 时先对比译文，不能直接覆盖：

```bash
python3 tools/refresh_tsc.py /path/to/working-copy \
    --liarsofttool /path/to/liarsofttool --encoding gbk --dialect kagerou --force
```

### 旧译文迁移到特典版

中文 GSC 曾由编辑后的 TSC 生成。重建工具使用 LiarsoftTool 的 TXT 导出／导入：
以新版日文 GSC 为模板，只回填旧中文的 TXT/TXA 姓名及正文；
指令、跳转、数据块、命名入口和尾部表保留新版字节。
按场景内对话顺序核对数量、语音与非文本参数，不按重复日文句子查找替换。
无法对齐、无法 GBK 编码、TXT 无法无损表示时整批拒绝安装。

```bash
# 默认只验证，不替换文件。
python3 kagerou/rebase_translation.py /path/to/patched-original /path/to/Chinese-patch \
    --liarsofttool /path/to/LiarsoftTool/build/liarsofttool
# 全部验证通过后安装，先备份旧 scr，再替换为重建后的 GSC/TSC。
python3 kagerou/rebase_translation.py /path/to/patched-original /path/to/Chinese-patch \
    --liarsofttool /path/to/LiarsoftTool/build/liarsofttool --apply
```

原版资源始终只读。备份位于补丁目录的 `kagerou-rebase-backup-*/scr`，
同目录的 `rebase-report.json` 记录迁移结果与未翻译场景。
若存在 `NNNN_zh.tsc`，优先采用这份编辑后的译文，原文件保存在备份中，
安装时统一恢复为数字场景名 `NNNN.tsc`。旧 GSC 指令不导入新版模板。
当前 `1501`～`1504` 有译文，`1505`～`1511` 尚未翻译，回退新版日文；
不把未翻译的日文强制写成 GBK，也不生成假译文。

## 适配说明

依据见 [NATIVE_EVIDENCE.md](NATIVE_EVIDENCE.md)。
`native.py` 的 EXCMD 调用模型已接入图层：加载、清除、寄存器 20、深度和队列。
非焦点角色 `(4,50)` 像素算法未还原，明确扁平化为正常显示。
坐标来自本作 EXE，不复制其他游戏的专用覆盖层。

按用户确认，默认采用竖排、字号档 0、布局档 0：24px，物理区域
`(114,30,646,480)`，首列在右上方，列从右向左排列；横排可通过方向键切换。
等待提示使用原资源 `wait12/16/18/24` 的 60 帧动画，每 50ms 推进一帧，
跟随末字位置；隐藏文本框同时清空当前文字页，防止跨场景残留。
端口的三个字号档统一为 24/18/12px，横竖切换不改变所选字号；
原生方向相关字号常量只留在只读证据模型中，不直接作为 Ren'Py 的竖排字号。
横/竖排文字区域和九个定位档来自 EXE。折行以文字区域的
像素宽度（横排）或高度（竖排）为准，不再提供与原生预设冲突的任意字数设置。
这个默认选择不读取旧 CFG，也不声称从 EXE 文件直接读出了竖排默认值。
全屏使用 `tbox01/back.png` 及元数据原点。
TXT 丢弃第一字符串，姓名保留在正文 `【姓名】` 中；
整页追加、段落分隔、溢出清页、TXA 和 txcls 单独处理。
旧段落按原生文字焦点开关淡化到 `128/255`，当前段落保持正常显示。
共享字形度量处理折行、注音；语音按 `voice/<组>/<四位编号>.ogg` 查找。
单个超长段落与自定义超大字号暂未实现段内分页。

阅读面板使用 `grps/compane`，原生屏幕位置为 `(585,572)`；文字控制面板
使用 `grps/excompane`，位置为 `(0,550)`。子控件原点来自各自 `.meta.xml`。
已核实并接入方向、字号、九宫定位、文字阴影、旧段落淡化、立绘定位及字体选择；
阅读面板提供跳过、回退、自动、重播语音、隐藏界面与文本框透明度。
`bak` 在 EXE 中打开文字记录，不回退游戏状态；当前使用简洁兼容记录页。
字体选择使用跨平台字体列表，阴影使用 Ren'Py 的近似绘制，均非原生像素复刻。
非焦点角色效果 `lctr` 的像素算法尚未核实，按钮禁用，不伪装成已实现。

0999 返回后继续调用 1000，无需改动原剧本。公共 `_gosub/_insub` 在写入参数
寄存器前先求值目标和全部参数，避免 `_r[10]` 保存的 1000 被参数 0 覆盖，
错误进入 `_0000` 标题场景。

启动视频仅进程启动时按 `0002.mpg`、`0001.mpg` 播放存在文件，返回标题不
重复播放。当前资源缺少 `0001.mpg`，警告后跳过，不用结局视频代替。
`0003.mpg` 属于五处结局调用，保留，不加入启动流程。

## 验证与限制

```bash
python3 -B tests/test_kagerou_native.py \
    /path/to/KagerouTouryuuki /path/to/KagerouTouryuuki_CHS
python3 -B tests/test_kagerou_builder.py \
    /path/to/KagerouTouryuuki /path/to/KagerouTouryuuki_CHS
python3 -B tests/run_kagerou_port.py /path/to/renpy/KagerouTouryuuki /path/to/renpy-sdk
/path/to/renpy-sdk/renpy.sh /path/to/renpy/KagerouTouryuuki lint
```

原生模型测试检查表读取、162 个特典版场景和输入哈希不变。
TXT 迁移回归：`python3 -B tests/test_kagerou_rebase.py /path/to/liarsofttool`，
检查导出／导入、非文本字节一致、备份、编辑译文优先级及错误拒绝。
隔离 SDK 命令检查实际寄存器间接调用、初始化、资源查找、EXCMD 队列/深度/清除、
整页文字、原生竖排布局、预设切换、段落淡化及两个面板屏幕，
不播放媒体，不进入正式游戏，不使用正式存档。
隔离图形检查可在 `run_kagerou_port.py` 命令末尾追加截图目录，输出
`vertical.png`、`horizontal.png`，仅绘制测试文字和操作面板，不运行剧情。
特典版的 CG／场景鉴赏使用本版 `0201/0301/0302` 剧本生成，不沿用旧版入口；
实际解锁和鉴赏流程仍需游玩验证。原生音乐鉴赏、角色语音独立开关未实现，
设置/存读档使用公共界面。
原生绘制效果、精确转场、原生记录页外观/分页、原生 CFG/存档导入尚未实现；普通不支持
效果在生成脚本中保留扁平化注释，EXCMD 限制写入构建清单。
lint 提示非 ASCII 素材名及原脚本疑似不可达段，不等于完整游玩证明。
生成器还检查 TXT 的语音资源引用；缺少 Ogg/WAV 时警告并记录，不编造音频。
实际画面、语音、视频解码、完整路线和安卓实机仍需用户验证。
