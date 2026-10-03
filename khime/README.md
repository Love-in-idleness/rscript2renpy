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
支持 `--language jp` 设置原版标签，以及 `--language zh=/path/to/patch`
添加语言补丁。补丁目录可只含修改的 `scr/*.tsc` 和转换后的图像、音频、
`keywords.json`。Khime 当前要求对应场景保持指令和非文本参数不变；
可翻译对话、追加文本、文本对象、选项和问题，缺少的场景使用原版。
Forest 翻译组新增字幕及 5000 整体替换仍由 Forest 专属 lowerer 处理。

标题的设置按钮打开公共 `rscript_text_preferences`：字体、字号、对话/文本对象
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
