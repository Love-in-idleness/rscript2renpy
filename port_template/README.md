# 通用 RScript 移植模板

这个目录用于开始一款新的 CodeX/RScript → Ren'Py 移植。它只复用已经
跨游戏成立的部分，不声称自动兼容所有 RScript 方言。

## 输入约定

先用 LiarsoftTool 解包并转换用户合法持有的游戏资源。模板只接受转换后的
文件，不调用 LiarsoftTool，也不读取 EXE：

- `grp*/**/*.png`
- `bgm/**/*.ogg`、`voice/**/*.ogg`、`wav/**/*.ogg`
- `mov/**/*.mpg`
- 游戏专用 lowerer 生成的 `scenario/**/*.rpy`

原始 GSC、WCG、封装 WAV、XFL 和 LWG 不会复制进 Ren'Py 工程；可直接播放的
普通 PCM WAV 可以复制，有同名提取 Ogg 时只复制 Ogg。
资源目录还可包含 BMP；CodeX 32 位 BMP 还原反向透明度，普通 BMP 保持不透明，
转换为原相对位置下的 PNG，同名 BMP 优先于 PNG。
语言资源安装到 `game/tl/<语言>/<原目录>/`，剧本生成到 `game/scr/`；
所有运行时、公共界面和游戏覆盖层安装到 `game/engine/`。

## 开始新移植

1. 新建游戏专用目录，不复制 `port_template/` 或 `runtime/`。生成器从
   `port_template.build_port` 导入 `validate_resources`、`assemble_port`。
2. 调用 `tsc_compiler.compile_scene` 或 `compile_overlays` 编译全部剧本，
   得到以 `scr/0000.rpy` 等相对路径为键的字典，再调用
   `assemble_port(resources, project, scenes, overlay, marker, patches)`。
   新方言的通用能力优先在公共编译器补全，专用行为留在覆盖层。
3. 游戏差异放在专用 `game/*.rpy` 覆盖文件中；音频命名与提示图位置通过
   `rscript_*_format`、`rscript_ctc_x/y` 配置，不改写安装后的共用文件。
4. 运行构建入口；脚本会创建尚不存在的工程目录：

   ```bash
   python3 <游戏目录>/build_<游戏>_rscript.py /path/to/prepared-resources /path/to/renpy-project
   ```

5. 在游戏目录添加专用的界面、文本规则和标题流程；最后运行
   静态测试及 Ren'Py lint。

模板拒绝覆盖内容不同的现有文件。确认要同步模板或运行时更新时才使用
`--force`。

旧文件布局不受支持，不迁移或归档；使用新的输出工程目录。
已有 RPY 的通用装配 CLI `build_port.py` 仍保留，但新游戏入口无需临时场景目录。

模板还会在工程根目录生成 `android-presplash.png` 和
`android-downloading.png`，替换 Android 构建时默认的 Ren'Py loading 图片。
两者使用同一张项目说明图，标明 GitHub 地址，并提醒玩家自行使用正版游戏文件构建。

所有 `grps/**/.meta.xml` 都读取画布尺寸和坐标，生成 `engine/grps_layout.rpy`。
主要菜单、选项和文本框有 PNG 却没有元数据时明确报错。共用界面用原图实现设置、
存读档、选择项、对话/姓名牌和控制条；默认 `say` screen 已在公共层，
`choice` screen 可 `use rscript_choice(items, prompt)`。
存档时会将 `_r[1]` 记入存档元数据；若存在 `grps/dt1_NNNN.png`，存读档页按此编号显示原游戏章节图，旧存档或缺图时才回退到 Ren'Py 截图。
外传等独立资源可由适配层设置 `rscript_ui.slot_images`（图片路径序列）和
`slot_image_zoom`；公共存档回调记录这组图片，预览横向拼接，返回本篇后仍按存档元数据显示。
缺少坐标元数据会在构建时明确报错，而不是生成位置不明的界面。标题流程和
选择分支仍由各游戏脚本决定。`grps_layout.UI_ACTIONS` 统一声明已知按钮动作，
按元数据存在的按钮自动生成，不再遗漏快存/快读/重播/隐藏或字体选择；未知按钮明确警告，
不凭文件名猜测动作。语言补丁元数据随语言切换；滑条、文本框前后图层、等待提示、
存档预览也使用元数据。素材命名或控制语义不同的作品仍需适配。

## 效果兼容检查

Forest 调用 `install_base` 安装公共层，再用公共 `write_scenario` 写入剧本；
Khime 通过 `build` 调用同一写入机制。写入运行时、界面和剧本时清理对应
`.rpyc`，不删除存档。动态效果默认保留，在运行时读取寄存器并验证效果，
并就地注释；未实现的常量效果仍统一降级。

通用装配入口对每份 `scenario/*.rpy` 执行一次效果兼容检查和未知 `^` 文本指令降级。
`_load`、`_cls`、`_oload`、
`_gload`、`_update`、`_effect`、移动、闪光、`_zupdate`、对象动作和混合模式中的效果及色彩模式，
只有运行时支持、且所需 `grps/efNN.png` 或 `grps/esNNN.png` 存在时才原样保留。
其余常量改为可执行的基础参数，并在 RPY 指令前注释
原值及原因；TSC 输入不改。将来实现新效果时，同步更新 `effect_compat.py`
的支持范围并重建场景。

动画计时在公共运行时处理，不能把已调校的老游戏速度直接套给新引擎。
`rscript_update_timing` 默认 `legacy`，保留 Forest/Khime 已确认的表现；
已核实的现代 CodeX 引擎可在适配层选择 `codex-ms`（Evermaiden 使用此项），
由公共函数按每个效果的循环次数与毫秒等待计算时长，适配层不复制计时代码。
这是引擎语义配置，不根据 TSC 的字节布局自动推断。

## 公共 UI 和字幕补丁

`game/ui_features.rpy` 提供对话/姓名牌、标题文字设置及点击系统动作，
`game/grps_ui.rpy` 提供原图设置、图片选项、dt1 存读档及控制条。
适配层只在后续 init 更新 `rscript_ui` 的实际布局/状态图差异；
字幕速度与透明度统一使用 `persistent.rscript_*`，兼容旧 Forest 存档插图键。
公共 `splashscreen` 默认依次播放 `mov/0002.mpg`、`mov/0001.mpg`，
返回标题不重新播放；只播放实际存在的文件，没有 `mov` 的工程也能启动。
游戏适配层无需重复配置。特殊游戏仍可覆盖 `rscript_boot_movies`，空元组可禁用。
`rscript_folder_zero_all` 和 `rscript_click_grid` 声明方言的全层目录与网格坐标语义。
图片选项通过 `rscript_asset_NNN` 读取寄存器并选择 `sel_aNN/body.png`，
公共层继续识别旧 `forest_asset_NNN`。

`tsc_patches.language_patch_data` 在显式方言下对齐原文与补丁，
允许新增 `font` 及配套 `wait/cls`，重定位分支；拒绝新增剧情逻辑。
调用者明确传入可覆盖的 opcode，不自动放宽非文本参数校验。
`tsc_compiler.py` 统一 early/modern lowering；`compile_overlays` 提供按语言整体
覆盖的场景与命名入口路由，适用于 Evermaiden 的中文/DLC 逻辑变化。它不放宽
Forest/Khime 现有纯文本补丁的对齐规则。
Forest、Khime、Evermaiden 共用 `build_port.validate_resources` 和
`assemble_port`。各游戏只声明自己的资源要求、编译策略及覆盖层；
剧本、补丁词典及补丁元数据预检失败时，不开始覆盖目标工程。
旧 `images/scenario/audio` 布局或根目录旧运行时不自动迁移，即使 `--force`
也会报错；请输出到新工程。当前布局的生成文件仍按原覆盖规则重建。

## 公共文本、语言与进度设置

`game/text_features.rpy` 提供 `rscript_text_preferences`，可调整字体、字号、
对话/对象每行字数、行距；并切换语言、Wiki、备份/恢复/清除持久化进度。
文字显示速度通过游戏内右键菜单的原图控件调整，标题文字面板不再提供速度入口。
共有设置名为 `persistent.rscript_*`，游戏通过 `rscript_base_text_size`、
`rscript_inline_base_size`、`rscript_use_speaker_images` 配置差异。
`^gNNN`、`^aNNN` 使用公共内联标签，Wiki 图片链接由适配层提供数字到 URL 的映射。
字体、GUI、语言资源安装不再引用 `forest/`。
语音通道、缺失音频检查及持久化寄存器落盘已进入公共运行时。
详细分层、移植边界和测试命令见 [分层说明](../docs/SHARED_TEMPLATE_MIGRATION.md)。

## Android 触摸控制条

`game/touch_controls.rpy` 是 Forest、Khime 和新移植共用的触摸控制条，
仅在 touch 模式的游戏画面显示：Back、Skip、Auto、Hide、Screenshot、Menu。
Auto 使用 Ren'Py 原生自动推进，选中时高亮；若自动推进时间为 0（无限等待），
点击 Auto 时设为 10 秒/250 字符，否则保留现有设置。此修复也用于原图控制条的 Auto。
自动推进等 `voice` 或公共 `rscript_voice` 语音播放结束；不等待循环 BGM。
点击、滚轮和 Skip 仍可提前推进，不改变脚本 `_wait` 的时间。
Hide 隐藏界面，点击恢复。
Screenshot 在 Android 使用 Ren'Py 内存截屏，直接将 PNG 写入系统 MediaStore 相册
（Android 10+ 为 `Pictures/RScript`），不写应用目录，也不保留临时文件或副本。
文件名包含时间戳，不覆盖已有截图。Android 9 及以下使用系统默认图片目录。
Android 10+ 不需要存储权限；Android 9 及以下需允许应用存储权限。
成功和失败都给出提示；失败时清理本次未完成相册条目，不另存副本，详情记录在日志。
桌面保持原生截屏，保存到游戏存档目录的 `screenshots/screenshot0001.png` 等文件。
进入菜单时隐藏控制条；Back、Menu 遵守 `roll_enabled`、`menu_enabled`。
游戏有额外锁定场景时可覆盖 `rscript_touch_locked()`，Forest 的 5000 场景保留锁定。
手机返回键仍按菜单键处理，而不是回滚。

原生动作及路径可用以下无图形测试检查；实际 Android 触摸和截屏画面仍需设备验证：

```bash
python3 tests/run_touch_controls.py /opt/apps/renpy
python3 tests/run_touch_controls.py /opt/apps/renpy --capture  # 真实桌面像素捕获
```

## 每款游戏必须确认

- GSC/TSC schema、编码、入口场景和 `gosub`/`insub` 调用约定
- 所有 opcode、VM 运算、跳转、选择支和持久化变量均未丢失；效果的有意扁平化有就地注释
- `folder` 与图像目录、图层、坐标、缩放、旋转、消失和过渡参数
- BGM、SE、voice 的文件编号、声道、循环、停止及等待语义
- `TXT`、`TXA`、`font`、控制符、字数、标点、姓名牌和文本框布局
- 标题、右键菜单、存读档、回滚边界、视频和系统存档
- 原版资源覆盖顺序；补丁目录必须最后覆盖基础归档
- 桌面 lint 与用户负责的视觉、音频、流程测试

## 目录分工

```text
port_template/
├── build_port.py          # 通用资源与运行时装配
├── android/notice.png     # Android 启动和下载阶段共用说明图
├── effect_compat.py       # 运行时能力与资源遮罩检查
├── grps_layout.py         # 从复合图元数据提取界面坐标
├── game/
│   ├── grps_ui.rpy        # 共用设置、存档和控制条
│   ├── touch_controls.rpy # Android 触摸控制、Auto 与截屏
│   └── script.rpy         # 统一入口；可由游戏适配层替换
└── README.md              # 本清单

prepared-resources/
├── scenario/*.rpy         # 游戏专用 lowerer 的输出
├── grp*/**/*.png
├── bgm/**/*.ogg
├── voice/**/*.ogg
├── wav/**/*.ogg
└── mov/**/*.mpg
```

`runtime/` 仍是唯一的通用 RScript 运行时来源；新项目不要复制一份运行时源码到
仓库里长期分叉。生成器通过 `tools/install_runtime.py` 安装它。
