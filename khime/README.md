# Khime Kusaritop 移植入口

使用已由 LiarsoftTool 解包、转换的 Khime 资源目录（含当前格式的 `scr/*.tsc`），
生成 Ren'Py 8 工程：

```bash
python3 khime/build_khime_rscript.py \
    /path/to/converted-khime /path/to/new-renpy-project
```

输出目录无需预先创建。脚本会编译全部 TSC 场景，直接调用 `port_template.build_port`
安装共用运行时和资源；Khime 的音频命名、提示图坐标和界面指令仅由
`khime/game/*.rpy` 补充，不在复制后改写共用运行时；
若目标文件已有不同内容，默认拒绝覆盖，确认重建时可加 `--force`。
Khime 默认字号 29、对话每行 21 字、叠加文本每行 20 字、行距 −5；已有玩家设置保留。
支持 `--language jp` 设置原版标签，以及 `--language zh=/path/to/patch`
添加语言补丁。补丁目录可只含修改的 `scr/*.tsc` 和转换后的图像、音频、
`keywords.json`。公共补丁对齐允许新增字幕及配套等待/清除，并校验跳转重定位；
非文本参数只接受 lowerer 明确允许的显示/音频等指令，不允许改变剧情逻辑。
通用模板会把补丁中的 CodeX 32 位 BMP（包括 `grpo_tp/*.bmp`）按反向透明度
转换为语言专用 PNG，用于替换标题等图像。
可翻译对话、追加文本、文本对象、选项和问题，缺少的场景使用原版。
5000 按语言整体替换仍只属于 Forest。

标题的设置按钮打开公共 `rscript_title_preferences`：字体、字号、对话/文本对象
每行字数、行距、速度、语言、Wiki 和持久化备份/恢复/清除。
游戏内仍使用原图音量、存读档设置，并提供 Text Settings 入口。

当前适配已支持脚本跳转、选择、标题图像点击、基础画面、文字和音频指令。
通用模板会检查运行时能力和效果遮罩；尚未实现的图像效果在生成时降级，
RPY 对应位置保留原参数注释；
数字显示控件仍缺乏原游戏的视觉匹配。
设置菜单、存读档和对话控制条由通用模板读取 `grps` 的 PNG 与 `.meta.xml`
生成；标题画面仍由 Khime 脚本的点击区域控制。
Ren'Py lint 通过不等于完成视觉、音频和
全路线游戏测试，这些仍需对照原游戏检查。

## 可选外传《帰省 ～jamais vu～》

本篇照常生成，追加下列参数接入用户自备的 Khime Zero 和翻译补丁：

```bash
python3 khime/build_khime_rscript.py --force \
    /path/to/Khime /path/to/RenPy-Khime \
    --language jp --language zh=/path/to/Khime.zh \
    --khime-zero /path/to/Khime_zero \
    --khime-zero-language zh=/path/to/Khime_zero.zh
```

这一版只接入外传 `scr/2001.tsc`，使用当前 LiarsoftTool 的 `legacy-28/early`
命令格式，不接入其标题和其他场景。所有资源依旧由用户自行解包、转换。
外传图片、姓名牌与音频放入 `khime_zero/` 命名空间，语言资源也有独立子目录，
不会覆盖本篇同编号素材。补丁与本篇共用 `zh` 等语言标签，缺少译文时回退原文。
640×480 的图片和对象坐标等比放大 1.25 倍到 800×600；对话沿用本篇文字设置。

主标题在“狐狸娶亲”（9105）与“退出”（9106）之间新增图片入口，
普通/悬停图分别来自外传 `grpo/0001.png` 与 `grpo/0101.png`。
沿用原标题的持久寄存器 `7901 == 1` 解锁条件：未解锁不显示入口且不能进入；
解锁后将退出行下移 35px，保留独立点击区域。外传结束或从菜单返回标题会重置
运行时，不会把外传 CG 编号写入本篇解锁寄存器；本篇进度和玩家文字设置不清除。

优先播放转换后的 OGG；外传 BGM 尚存的标准 PCM WAV 可直接使用，无需 ffmpeg。
封装 OGG 的 WAV 必须先由 LiarsoftTool 提取，不接受假 WAV。
早期 BGM 淡入/淡出时长尚未确认，暂为无渐变播放，并在生成位置注明。
这是一版待人工验证的适配，画面、音频、字幕时序与旧存档仍需实际游玩确认。
