# Forest / Khime 公共模板分层

两个移植入口现在安装同一份公共文件，再叠加游戏补丁；不复制另一款游戏的
生成器，也不对复制后的运行时做字符串替换。

```text
runtime/                    RScript 指令、寄存器、图层/效果、文本度量、语音
port_template/
  rscript_tsc.py, tsc_vm.py  当前 TSC 解析及表达式/VM 公共部分
  tsc_patches.py             文字补丁对齐、字幕/等待/清除插入、参数覆盖校验
  build_port.py             install_base + 场景装配/兼容检查
  port_resources.py         图像/元数据/遮罩/原始 MPG/语言资源/keywords.json
  fonts/, android/          共用字体及 Android 启动说明
  game/
    gui.rpy                 共用 800×600 GUI
    text_features.rpy       字体、字号、字数、行距、速度、语言、Wiki、进度备份
    grps_ui.rpy             元数据驱动的设置、选项、存读档、对话控制条
    ui_features.rpy          对话/姓名牌、点击系统动作、旧存档和透明度迁移
    touch_controls.rpy      Back / Skip / Auto / Hide / Screenshot / Menu
forest/game/                Forest 布局策略、旧指令别名、偏好迁移、5000 锁定
khime/game/                 Khime 人脸、方言适配、布局策略及旧指令别名
```

## 公共能力及游戏差异

| 功能 | 公共层 | 游戏补丁 |
| --- | --- | --- |
| 文本 | 实际字形前进量禁则、追加文本、对象、`^n/^b/^i/^s/^d/^w/^c/^f/^v/^g/^a/^m` | 游戏专用 TSC 方言、颜色/字体槽和文本操作数 |
| 文本设置 | 字体、字号、对话/对象字数、行距、速度、语言、进度备份 | Forest 默认 22px，Khime 默认 30px；对话 19、对象 20 字宽 |
| Wiki | `keywords.json`、绿色链接、内联 `gf/gg` 图片标签、原图 WIKI 行 | Forest 的 601/603 图像链接映射 |
| 语音 | `rscript_voice`、重播、停止/等待、Auto 等语音、SE 999 循环 | 文件编号格式及 TSC 语音操作数 |
| GUI | 原图设置、dt1 存读档、图片选项、点击区域、对话/姓名牌和控制条 | 各游戏的坐标、配色、状态图策略及 Khime 人脸 |
| Android | 触摸控制、原生 Auto、直接写系统相册、启动说明 | 应用名称、图标、RAPT 配置及锁定场景 |
| 剧本 | 解析器、VM、补丁对齐、字幕插入、装配/兼容检查、编译缓存失效、启动视频机制 | Forest 5000 整体替换、视频顺序；各游戏方言/参数允许列表 |

Forest 的 `forest/game/*.rpy` 是覆盖层，`build_forest_rscript.py` 保留专属
剧本降级器和参数策略；补丁对齐、界面与点击行为只在公共层维护。
两款游戏的原生选项统一由 `config.menu_arguments_callback` 记录选择点，
`rev` 统一使用公共 `rscript_rev_action()` 返回最近的选择点；缺失或过期的
目标由原生动作禁用。Forest 仅保留控制条布局和输入锁定，不再在剧本中重复记录。
原生运行时安装器 `tools/install_runtime.py` 仍可以单独使用；模板钩子未安装时
保留普通文本颜色和文本设置的默认实现。

Forest 的旧 `persistent.forest_*` 字体/文本/Wiki/备份设置会一次性迁移到
`persistent.rscript_*`；旧 `textbox_opacity` 单独迁移到公共透明度字段。
新存档使用 `rscript_dt1`，读取时兼容旧 `forest_dt1`，缺图才回退截图。
寄存器进度和存档目录不变，未清除玩家存档；跨版本回滚仍需实际游玩确认。

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

两款补丁都可以仅提供部分场景。对话、追加、对象和选项可翻译，
允许新增字幕及配套等待/清除；重定位跳转，但不允许插入或修改剧情逻辑。
非文本参数覆盖由各 lowerer 的允许列表约束；Khime 没有整体替换场景机制。
图像、音频、视频、元数据和 Wiki 词典的语言资源由公共层复制。

两款生成器都使用公共场景写入/兼容检查并清理对应 `.rpyc`。
Forest 保留已确认的动态效果表达式，并注释交由运行时验证；
Khime/新移植默认降级无法静态判定的效果。这里没有把方言 opcode 强行视为同一语义。

Khime EXE 的对象效果与文本控制符依据、已实现范围和未确认差异分别见
[特效分析](KHIME_EFFECT_ANALYSIS.md) 和 [文本控制符分析](KHIME_TEXT_CONTROLS.md)。

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
