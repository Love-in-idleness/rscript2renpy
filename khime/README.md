# Khime Kusaritop 移植入口

使用已由 LiarsoftTool 解包、转换的 Khime 资源目录（含当前格式的 `scr/*.tsc`），
生成 Ren'Py 8 工程：

```bash
python3 khime/build_khime_rscript.py \
    /path/to/converted-khime /path/to/new-renpy-project
```

输出目录无需预先创建。脚本会编译全部 TSC 场景，并安装共用运行时和资源；
若目标文件已有不同内容，默认拒绝覆盖，确认重建时可加 `--force`。
目前没有 `--language` 参数。

当前适配已支持脚本跳转、选择、标题图像点击、基础画面、文字和音频指令。
通用模板会检查运行时能力和效果遮罩；尚未实现的图像效果在生成时降级，
RPY 对应位置保留原参数注释；
数字显示控件仍缺乏原游戏的视觉匹配。
设置菜单、存读档和对话控制条由通用模板读取 `grps` 的 PNG 与 `.meta.xml`
生成；标题画面仍由 Khime 脚本的点击区域控制。
Ren'Py lint 通过不等于完成视觉、音频和
全路线游戏测试，这些仍需对照原游戏检查。
