# KagerouTouryuuki 移植说明

[返回主说明](../README.md) · [通用模板](../port_template/README.md)

## 概述

本目录提供《霞外籠逗留記》的实验性 Ren'Py 8 工程生成器，包括原版剧本、
可选中文资源和专用运行时。生成及自动测试不代表完整路线已经验证。
除用户允许沿用的启动视频流程外，专用行为先核对本作 EXE；
未确认的效果明确降级，不猜测像素算法。仓库不包含游戏本体。
以下命令均在仓库根目录执行。

## 准备资源

资源预处理依赖当前 [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool)。
保留原版与补丁各自的 EXE、原始 GSC，并在工作副本转换图像、音频和 TSC；
不要覆盖手工修改过的脚本。当前 TSC 为 `modern-36`，混用 `modern` 与
`rscript19` schema，不能整批强行指定成 Forest 方言。

原版资源包括 `grpe/grpo/grpo_bu/grps/bgm/voice/wav/mov/scr`。
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

当前中文补丁有 140 个 TSC，原版有 147 个。缺失系统场景回退原版。
语言包按完整场景切换，图像与元数据按语言覆盖；不要求逐指令对齐，但补丁
剧情改动也会一起生效。补丁 EXE 的两个字体字符集字节变化不证明剧本只有文本变化。

旧中文 TSC 有 12 处命名入口缺少标签，应从原 GSC 按 GBK 重新导出，
保留对应 `L_xxxxxx` 标签。手工修改过 TSC 时先对比译文，不能直接覆盖：

```bash
python3 tools/refresh_tsc.py /path/to/working-copy \
    --liarsofttool /path/to/liarsofttool --encoding gbk --dialect kagerou --force
```

中文 GSC 曾由编辑后的 TSC 生成。备用方案：若确认其非文本结构严重偏离原版，
可导出中文 TXT，以原版日文 GSC 为模板重新回填译文；先检查文本条目映射和
输入编码，在工作副本验证，不能把“可以生成”当作分支与入口相同的证明。

## 适配说明

依据见 [NATIVE_EVIDENCE.md](NATIVE_EVIDENCE.md)。
`native.py` 的 EXCMD 调用模型已接入图层：加载、清除、寄存器 20、深度和队列。
非焦点角色 `(4,50)` 像素算法未还原，明确扁平化为正常显示。
坐标来自本作 EXE，不复制其他游戏的专用覆盖层。

按用户确认，默认采用竖排、字号档 0、布局档 0：18px，物理区域
`(400,20,360,513)`，首列在右上方，列从右向左排列；横排可通过方向键切换。
横/竖排各有三个原生字号档、九个定位档，数值来自 EXE。折行以文字区域的
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

原生模型测试检查表读取、147/140 场景和输入哈希不变。
隔离 SDK 命令检查实际寄存器间接调用、初始化、资源查找、EXCMD 队列/深度/清除、
整页文字、原生竖排布局、预设切换、段落淡化及两个面板屏幕，
不播放媒体，不进入正式游戏，不使用正式存档。
隔离图形检查可在 `run_kagerou_port.py` 命令末尾追加截图目录，输出
`vertical.png`、`horizontal.png`，仅绘制测试文字和操作面板，不运行剧情。
原版额外鉴赏页、角色语音独立开关未实现，设置/存读档使用公共界面。
原生绘制效果、精确转场、原生记录页外观/分页、原生 CFG/存档导入尚未实现；普通不支持
效果在生成脚本中保留扁平化注释，EXCMD 限制写入构建清单。
lint 提示非 ASCII 素材名及原脚本疑似不可达段，不等于完整游玩证明。
生成器还检查 TXT 的语音资源引用；缺少 Ogg/WAV 时警告并记录，不编造音频。
实际画面、语音、视频解码、完整路线和安卓实机仍需用户验证。
