# Forest / Khime / Evermaiden 公共模板分层

各移植入口安装同一份公共文件，再叠加游戏补丁；不复制另一款游戏的
生成器，也不对复制后的运行时做字符串替换。

当前 LiarsoftTool 会为现代 GSC 的命名入口及 `*insub` 局部目标生成标签。
公共 TSC 读取器按正文标签重定位，不能把尾表旧代码地址直接当新地址使用。
请保留命名入口对应的 `L_xxxxxx` 标签；旧 TSC 缺失标签或仍用数字 `insub`
地址时，从原 GSC 重新导出。现代适配中 `*data` 块编号零不复制任何值，
非零块必须存在；数据块数量不得超过引擎 signed int16 上限 32767。
TSC 正文为 UTF-8，旧编码声明按上游规则忽略；28 字节格式不接受尾表元数据。
工具升级后可使用 `tools/refresh_tsc.py` 显式重建 `scr/*.tsc`：指定工具路径、
输入编码和方言，整批预检后逐文件原子替换；生成器本身仍不调用 LiarsoftTool。

```text
runtime/                    RScript 指令、寄存器、图层/效果、文本度量、语音
port_template/
  rscript_tsc.py, tsc_vm.py  当前 TSC 解析及表达式/VM 公共部分
  tsc_compiler.py           early/modern 共用编译循环，方言和适配策略显式区分
  tsc_patches.py            补丁对齐、文本表达式、字幕插入、参数分支及校验
  build_port.py             资源校验、公共装配、Android/覆盖层/语言包安装
  port_resources.py         图像/元数据/遮罩/原始 MPG/语言资源/keywords.json
  fonts/, android/          共用字体及 Android 启动说明
  game/
    gui.rpy                 共用 GUI；rscript_screen_size 默认 800×600
    text_features.rpy       字体、字号、字数、行距、语言、Wiki、进度备份
    grps_ui.rpy             元数据驱动的设置、选项、存读档、对话控制条
    ui_features.rpy          对话/姓名牌、点击系统动作、旧存档和透明度迁移
    touch_controls.rpy      Back / Skip / Auto / Hide / Screenshot / Menu
forest/game/                Forest 布局策略、指令别名、5000 锁定
khime/game/                 Khime 人脸、方言适配、布局策略及旧指令别名
evermaiden/game/            1280×720、现代文本/音频编号与布局默认值
```

## 公共能力及游戏差异

| 功能 | 公共层 | 游戏补丁 |
| --- | --- | --- |
| 文本 | 实际字形前进量禁则、追加文本、对象、`^n/^b/^i/^s/^d/^w/^c/^f/^v/^g/^a/^m` | 游戏专用 TSC 方言、颜色/字体槽和文本操作数 |
| 文本设置 | 字体、字号、对话/对象字数、行距、速度、语言、进度备份 | Forest 默认 22px／对话 19 字／行距 7；Khime 默认 29px／对话 21 字／行距 −5；对象均 20 字宽 |
| Wiki | `keywords.json`、绿色链接、内联 `gf/gg` 图片标签、原图 WIKI 行 | Forest 的 601/603 图像链接映射 |
| 语音 | `rscript_voice`、重播、停止/等待、Auto 等语音、SE 999 循环 | 文件编号格式及 TSC 语音操作数 |
| GUI | 原图设置、dt1 存读档、图片选项、点击区域、对话/姓名牌和控制条 | 各游戏的坐标、配色、状态图策略及 Khime 人脸 |
| 存档 | Ren'Py 原生用户存档及工程内同步副本 | `options.rpy` 指定各游戏独立、稳定的 `config.save_directory` |
| 版本 | `build_port.py` 的 `PORT_VERSION` 生成 PC／Android 版本，安卓版本代码不倒退 | 各游戏保留包名、图标和其他平台设置，不另设版本号 |
| Android | 触摸控制、原生 Auto、直接写系统相册、启动说明 | 应用名称、图标、RAPT 配置及锁定场景 |
| 剧本 | early/modern 编译循环、解析器、VM、补丁对齐、字幕插入、装配/兼容检查、编译缓存失效、启动视频机制 | Forest 5000 整体替换、2500 图片编号纠错、视频顺序；各游戏方言/参数允许列表 |

文字显示速度只在游戏内右键原图菜单调整，标题文字设置面板不提供速度入口。
原图右键菜单及无资源回退菜单的“返回主界面／退出游戏”统一使用英文确认框，
点击 `No` 只关闭确认框，保留当前菜单与进度。提示和 `Yes`／`No` 不随剧情语言翻译。

当前统一版本为 `1.3`，安卓版本代码最低为 `13`。公共构建流程生成
`game/engine/port_version.rpy`，并更新 `android.json` 的版本；保留已有更高的版本代码，
以及本机包名、权限和其他构建配置。RAPT 打包时仍可能按其原生规则使用更高的时间戳版本代码。
Forest／Khime 的游戏配置和安卓配置源文件不再保留重复版本值。

生成工程保留原始资源目录和场景文件名：`game/scr/*.rpy`、`game/grps/`、
`game/grpe/`、`game/bgm/`、`game/voice/`、`game/wav/`、`game/mov/`。
语言覆盖同样位于 `game/tl/<语言>/scr/` 及对应原资源目录；不生成 `variantN/` 文件夹。
所有运行时、公共界面、游戏覆盖层、版本及语言配置放在 `game/engine/`；字体仍在 `game/fonts/`。
公共渲染入口只对相邻的 RScript 位图图层在原始虚拟画布上按像素拼合，再平滑缩放到窗口。
缺失图片的占位文字统一透明；缺失图片文件使用透明占位资源，已有文件的解码错误
仍交给 Ren'Py 处理。此显示策略不关闭 lint 的缺失图像引用检查。
这避免独立头／身体透明边缘在非整数窗口比例下分别插值，形成透底的阶梯接缝；
不改素材或脚本坐标；正文、文本对象、菜单及跨层混合效果不进入位图合成，保持原生渲染。
隔离 GL2 像素回归：`python3 -B tests/test_sprite_seams.py /path/to/renpy-sdk`。
每组相邻位图增加一次纹理合成；实际动画观感和 Android GPU 性能仍需实机确认。
不支持旧工程文件布局迁移。检测到 `images/scenario/audio` 旧目录或已知的
根目录旧运行时模块时，即使指定 `--force` 也会报错，要求使用新的输出工程。
生成器不会移动、归档或删除这些旧文件；当前布局重建仍会清理对应编译缓存。

公共模板扫描全部 `grps/**/.meta.xml`，按画布、坐标、实际图像尺寸生成布局；
同名图片统一优先使用 WebP，再使用 PNG；语言补丁优先于原版，即补丁只有 PNG
时不会被原版 WebP 遮盖。图像注册、菜单、内联图和元数据尺寸读取使用同一优先级。
`grps_layout.UI_ACTIONS` 统一维护已确认的控件名到 Ren'Py 动作的映射。
控制条按元数据实际存在的按钮生成，包括快存、快读、重播、隐藏等，不用游戏白名单裁剪。
语音重播键仅在当前对话有可加载语音时显示；播放结束后仍可重播，新的无语音
对话会清除重播目标，追加对话保留当前语音或使用新指定的语音。
设置页字体选择、滑条、存档预览与等待提示同样复用元数据；语言补丁元数据随语言切换。
未知按钮在构建时列入 `unhandled` 并发出警告；元数据只给位置，不能自动推导未知按钮语义。

旧式平面 `grps` 可由游戏覆盖层提供 `rscript_ui["layouts"]`，其中 `images`
把逻辑控件映射为 `(原资源相对路径, 裁切矩形或 None)`。公共按钮/滑条复用同一
布局与动作，不复制屏幕或改变原资源目录；路径仍按当前语言和 WebP 优先规则查找。
CannonBall 的硬编码菜单与控制条按 EXE 静态证据接入，可选只读工具
`tools/inspect_rscript_ui.py` 报告资源引用及未实现项。二进制几何/动作提取受已验证
版本配置约束；未知程序仅提供引用清单，不保证自动还原所有界面。
原图存读档页也读取同一布局的 `images` 路径/裁切映射，可配置时间文字尺寸与
页码图集，首尾页是否循环由布局决定。CannonBall 的 `dat_*` 平面图集不需要改名
或移动；章节预览仍复用存档里的 `rscript_dt1` 与共享 `DT1` 查找路径。
原图设置页支持布局 `background_dim`，先暗化背景再绘制菜单，关闭后自动
移除；未配置时不改变其他游戏。CannonBall 的强度来自已验证 EXE 的颜色查表。

公共 `permissions.rpy` 将 `sysmode` 的 save/roll 标志同步到 Ren'Py 原生
存档、自动存档和回退许可，菜单/点击键也使用同一权限入口。
覆盖层可指定 `restricted_image_folders`，这些目录的对象实际显示期间额外禁止
存档与回退；只配置 CannonBall 的赛车资源，其他游戏不添加该限制。
进入/离开回退锁定段时设回退边界，不允许结束后滚回赛车段；读档仍受原生存档规则管理。

脚本的 `setlink/click` 按钮只在 `screens` 层提供透明点击区域，保留原图的
透明像素命中遮罩；按钮本体、悬停图和信息卡仍参与 `master` 层的原生深度排序。
悬停替换原图层的图像，不另画一套置顶按钮，退出点击等待后恢复原图并清除信息卡。
因此歌词、遮罩和其他高层图像不会被点击界面重复绘制的低层图片遮住。
公共点击路径另保留 `setclk/setclksys` 的悬停模式；已验证的旧引擎适配可启用
`rscript_click_native_effects`，按 1=反色、2=泛白、3=隐藏本体处理，说明图
仍独立排序。其他方言默认不启用，保持已有悬停替换图语义。
`depth` 同时更新已加载图像，重排与其他绘制操作共用队列；独立 UI 按钮仍可自行绘制。

Forest 的 `forest/game/*.rpy` 是覆盖层，`build_forest_rscript.py` 只保留
入口、资源要求、5000 整体替换、2500 图片纠错和 Wiki 601/603 映射。
三个入口均使用 `tsc_compiler.py`，不再各自维护重复的指令遍历循环。
early 的返回与 SE 语义、现代文本参数及 Khime Zero 策略仍明确区分，不强行等同。
三个入口共用 `assemble_port` 安装基础文件、覆盖层、语言资源及场景；
先完成全部剧本编译与语言词典/元数据校验，再开始覆盖目标。该预检不是事务式写入：
磁盘故障或复制失败仍可能中断安装。补丁对齐、界面与点击行为只在公共层维护。
两款游戏的原生选项统一由 `config.menu_arguments_callback` 记录选择点，
`rev` 统一使用公共 `rscript_rev_action()` 返回最近的选择点；缺失或过期的
目标由原生动作禁用。Forest 仅保留控制条布局和输入锁定，不再在剧本中重复记录。
原生运行时安装器 `tools/install_runtime.py` 仍可以单独使用；模板钩子未安装时
保留普通文本颜色和文本设置的默认实现。

Forest 不再读取或迁移旧 `persistent.forest_*` 设置，仅使用
`persistent.rscript_*`；旧 `textbox_opacity` 单独迁移到公共透明度字段。
新存档使用 `rscript_dt1`，读取时兼容旧 `forest_dt1`，缺图才回退截图。
寄存器进度不变，未清除玩家存档；跨版本回滚仍需实际游玩确认。

两款游戏使用同一套 Ren'Py 原生存档机制。Linux 用户目录分别为
`~/.renpy/Forest-rscript2renpy/` 和 `~/.renpy/KhimeKusaritop-rscript2renpy/`；
桌面版同时保留工程内 `game/saves/` 同步副本。Forest 旧版本漏配
`config.save_directory`，仅使用工程内目录；升级前关闭游戏，备份并将旧
`game/saves/` 内容复制到新的用户目录，保留原文件。若用户目录已有存档，
不要直接覆盖，需先核对冲突。其他平台的实际用户路径由 Ren'Py 决定。

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
python3 -B tests/test_tsc_compiler.py
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
