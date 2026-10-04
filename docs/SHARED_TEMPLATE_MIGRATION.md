# Forest / Khime 公共模板分层

两个移植入口现在安装同一份公共文件，再叠加游戏补丁；不复制另一款游戏的
生成器，也不对复制后的运行时做字符串替换。

```text
runtime/                    RScript 指令、寄存器、图层/效果、文本度量、语音
port_template/
  rscript_tsc.py, tsc_vm.py  当前 TSC 解析及表达式/VM 公共部分
  build_port.py             install_base + 场景装配/兼容检查
  port_resources.py         图像/元数据/遮罩/原始 MPG/语言资源/keywords.json
  fonts/, android/          共用字体及 Android 启动说明
  game/
    gui.rpy                 共用 800×600 GUI
    text_features.rpy       字体、字号、字数、行距、速度、语言、Wiki、进度备份
    grps_ui.rpy             元数据驱动的设置、选项、存读档、对话控制条
    touch_controls.rpy      Back / Skip / Auto / Hide / Screenshot / Menu
forest/game/                Forest 专用界面/标题/存档插图/点击指令/偏好迁移
khime/game/                 Khime 专用人脸、坐标、点击指令及界面布局
```

## 公共能力及游戏差异

| 功能 | 公共层 | 游戏补丁 |
| --- | --- | --- |
| 文本 | 实际字形前进量禁则、追加文本、对象、`^n/^b/^i/^s/^d/^w/^c/^g/^a/^m` | 游戏专用 TSC 方言和文本操作数 |
| 文本设置 | 字体、字号、对话/对象字数、行距、速度、语言、进度备份 | Forest 默认 22px，Khime 默认 30px；对话 19、对象 20 字宽 |
| Wiki | `keywords.json`、绿色链接、内联 `gf/gg` 图片标签 | Forest 的 601/603 图像链接映射及原图 WIKI 行 |
| 语音 | `rscript_voice`、重播、停止/等待、Auto 等语音、SE 999 循环 | 文件编号格式及 TSC 语音操作数 |
| GUI | 字体、确认框、通用文本设置及原图菜单组件 | Forest 原图菜单、dt1 存档图和姓名牌布局；Khime 人脸和原图坐标 |
| Android | 触摸控制、原生 Auto、直接写系统相册、启动说明 | 应用名称、图标、RAPT 配置及锁定场景 |
| 剧本 | 解析器、VM 和装配 | Forest 新增字幕/等待补丁、5000 整体替换、启动视频；Khime 方言 |

Forest 的 `forest/game/*.rpy` 是覆盖层，`build_forest_rscript.py` 保留专属
剧本降级器和补丁对齐；通用功能只在 `runtime/`、`port_template/` 修改。
两款游戏的原生选项统一由 `config.menu_arguments_callback` 记录选择点，
`rev` 统一使用公共 `rscript_rev_action()` 返回最近的选择点；缺失或过期的
目标由原生动作禁用。Forest 仅保留控制条布局和输入锁定，不再在剧本中重复记录。
原生运行时安装器 `tools/install_runtime.py` 仍可以单独使用；模板钩子未安装时
保留普通文本颜色和文本设置的默认实现。

Forest 的旧 `persistent.forest_*` 字体/文本/Wiki/备份设置会一次性迁移到
`persistent.rscript_*`。寄存器进度和存档插图键仍使用原来的字段，未更换存档目录，
未清除玩家存档。旧游戏存档的跨版本回滚兼容性仍需实际游玩确认。

## 构建和语言补丁

Forest 的命令行与补丁功能不变；Khime 新增同样的标签参数：

```bash
python3 forest/build_forest_rscript.py /path/to/forest /path/to/Forest \
    --language jp --language zh=/path/to/forest-zh
python3 khime/build_khime_rscript.py /path/to/khime /path/to/Khime \
    --language jp --language zh=/path/to/khime-zh
```

Khime 默认拒绝覆盖不同内容的文件，重建需明确加 `--force`。Forest 保留原入口的
覆盖行为，重建现有项目之前请备份生成文件和手工补丁。

Khime 补丁可以仅提供部分场景。对话、追加、对象和选项可翻译，指令序列与
非文本参数必须不变；不支持 Forest 那种新增字幕/等待的结构补丁，会明确报错。
图像、音频、视频、元数据和 Wiki 词典的语言资源由公共层复制。

当前只有 Forest 完成了专用效果的逐项适配。Khime 及新移植使用公共效果检查，
保留其降级注释。这里没有把两款游戏的专用 opcode 强行视为同一语义。

## 验证

```bash
python3 -B tests/test_shared_port.py /opt/apps/renpy
python3 -B tests/test_runtime.py
python3 -B tests/test_port_template.py
python3 -B tests/test_text_wrap.py
python3 -B tests/run_native_text_wrap.py /opt/apps/renpy
python3 -B tests/run_touch_controls.py /opt/apps/renpy
/opt/apps/renpy/renpy.sh /path/to/Forest lint
/opt/apps/renpy/renpy.sh /path/to/Khime lint
```

`test_shared_port` 在临时目录生成两款最小工程，验证运行时和模板文件逐字节一致，
检查 Khime 语言文本替换及拒绝非文本修改，再调用真实 Ren'Py 检查菜单、Wiki、
字体/字号配置、进度备份和姓名牌生命周期。测试媒体是未播放的占位文件，
此测试不是音视频播放测试；全资源生成及 lint 要另行运行。

现有禁则测试和原生布局测试覆盖真实字形度量。Android 相册测试使用模拟 JNI，
不等于实机验证。需人工确认完整路线、字幕时序、旧存档、原图布局，以及安卓
Auto/触摸/相册的表现。

可在独立测试工程复制 `tests/renpy_shared_menu_capture.rpy` 到 `game/`，使用
`RENPY_SKIP_SPLASHSCREEN=1 RENPY_SKIP_MAIN_MENU= RENPY_PERFORMANCE_TEST=0`
启动桌面 Ren'Py。此测试覆盖 `before_main_menu`，会自动截图并退出，勿放进正式工程。
截图用于检查完整语言/Wiki/进度行组合的布局；已实测并调整为适合 800×600 的紧凑行距。
