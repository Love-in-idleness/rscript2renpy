# Forest Ren'Py 移植工作总结

## 1. 项目目标与结果

本项目把 Liar-soft 2004 年作品《Forest》从 CodeX RScript 运行环境迁移到 Ren'Py 7。最终方案不是把剧本手工改写为普通 Ren'Py 脚本，而是：

1. 用 LiarsoftTool 2.0 将原版 `scr/*.gsc` 转成结构化 `scr/*.tsc`；
2. 由生成器调用 LiarsoftTool 恢复指令结构，并按 offset 应用 TSC 正文修改；
3. 将指令、表达式、跳转和文本降级为接近原 RScript 语义的 `.rpy`；
4. 在 Ren'Py 中实现一层 RScript 兼容运行时；
5. 直接复用解包并转换后的原版图像、音频和视频资源。

当前 103 个 GSC 文件、38,397 条指令均能解析，生成剧本中没有残留的 `unlifted opcode`。PC 版可运行，Android 版可构建；真实设备仍应完成全路线验收。

本次归档版本为 `1.0`。已验证 APK：

- 包名：`io.github.loveinidleness.forest`
- versionName：`1.0`
- versionCode：`1788622602`
- SHA-256：`6b923c921974e26ed174db810e81c770a955acde845bf83a0732dfd3531e9b88`

## 2. 目录和职责

- `forest/forest_gsc.py`：Forest 旧式 28 字节头 GSC 的结构解析器。
- `forest/build_forest_rscript.py`：从原版资源及 TSC 生成完整 Ren'Py 工程。
- `tests/test_forest_resources.py`：检查全部 GSC 的指令边界。
- `tests/test_forest_builder.py`：检查生成规则、关键剧情和资源处理回归。
- `tests/test_liarsofttool2.py`：检查 LiarsoftTool 2.0 TSC 往返及正文编辑。
- `runtime/`：RScript 的 Ren'Py 通用运行时模板。
- 用户提供的资源目录：解包、转换后的 Forest 原版资源及 TSC 输入。
- 用户提供的 Ren'Py 工程：生成出的、可直接运行和打包的工程。

生成目录不应成为手工修改的唯一位置。通用解释器修改写入 runtime 模板；Forest 专用兼容修改写入生成器。对易被忽略的 runtime 修复，生成器还应提供幂等补丁，防止下一次生成丢失。

## 3. GSC 逆向方法

### 3.1 先确定结构，再解释语义

先用 Forest.exe 的 dispatch table 确认 opcode 参数个数和类型，再让解析器遍历全部文件。只有当每条指令末端恰好落在代码区末端时，参数布局才算可信。

不要直接照搬旧 `RsComp.dll` 或其他 AI 生成的表：Forest 使用的方言、文件头和隐藏参数可能不同。每个 opcode 都要同时核对：

- EXE/DLL 中的读取宽度和调用路径；
- 多个真实 GSC 中的参数分布；
- 指令前后的剧情、资源与画面效果；
- 原版实际运行画面。

### 3.2 表达式与控制流

Forest 的参数可包含多层寄存器间接寻址。生成器用 `_r[...]` 保留这种语义，并把 VM 临时表达式直接降为 Ren'Py Python 表达式。条件跳转目标被转换成带原字节偏移的 label，以便追查原始位置。

随机数必须使用 Ren'Py 的可回滚随机源 `renpy.random`，不能使用 Python 全局 `random`，否则存档和回滚会改变剧情一致性。

### 3.3 最后五种 opcode

- `0x20`：`_oload`，在对象图层创建文字 Displayable；字符串索引在生成时解析。
- `0x23`：`_oaction`；Forest 唯一使用 action 4，映射为目标图层的短暂横向摆动。
- `0x53`：`_txcls`，清除当前文本延续状态。
- `0x63`：`_texindent`，更新正文缩进；Forest 姓名牌宽 174 像素，正文从 x=175 开始。
- `0x78`：`_osize`，设置指定对象图层后续文字的字号。

这五种指令在 Forest 中分别出现 58、1、2、4、52 次，测试会核对数量并禁止重新退化为 `unlifted` 注释。

## 4. 资源迁移

### 4.1 图像

LIM/WCG 必须先用 LiarsoftTool 解包或转换为 PNG，并保留资源目录层次及 `.meta.xml`。角色名牌由文本中的 `^gNNN` 选择 `grps/gfNNN.png`。选择界面优先使用 `grps/sel_*` 原图，不用普通 Ren'Py 文字按钮仿制。

原版遮罩资源需要验证尺寸、alpha 和方向；只确认“文件存在”不足以证明转场正确。缺失的 `ef*.png` 应从原始遮罩可靠转换，不能生成占位图掩盖问题。

### 4.2 音频

原版扩展名为 WAV 的文件可能是 Liar-soft 封装的 Ogg 流，不能直接交给播放器。应由 LiarsoftTool 提取有效 Ogg 页面并输出 `.ogg`。BGM、voice、SE 使用独立 Ren'Py channel，避免对白推进时错误停止音乐或语音。

语音编号、文件名位数和 channel 必须用真实文件验证。对缺失资源记录日志并继续运行，不能因单个音频缺失终止整个剧情。

### 4.3 视频

原版 MPEG 转为 WebM。启动时依次播放 `0002`、`0001`，只放在 `splashscreen`，不能在返回标题时重复播放。生成器会删除工程中的旧 MPG，避免 APK 同时携带两套视频。

## 5. Ren'Py 兼容层要点

- 分辨率固定为原版 800×600。
- 使用覆盖日文字符的 Noto Sans CJK JP 字体。
- 标题、配置、存档、选择和对话框尽量复用原版素材。
- 系统进度 flag 使用 persistent 数据并及时 `renpy.save_persistent()`，替代原版 `rssave.dat`。
- 回滚边界不能越过游戏入口回到主菜单，否则可能重复执行 default 初始化。
- Android 没有右键，需提供触屏的返回、跳过、自动和菜单控制。
- GLES shader 中必须显式使用浮点常量，例如 `1.0`、`vec3(1.0)`；桌面 OpenGL 可接受的整数/向量混算在 Android GLES 上可能编译失败。
- Character 的 `show_center` 属性会被 Ren'Py 去掉 `show_` 前缀，再以 `center` 参数传给 `screen say`。

## 6. 可重复生成与验证

在 LiarsoftTool 仓库根目录执行：

```bash
python3 -B tsc/test_forest_gsc.py
python3 -B tsc/test_forest_rscript.py
python3 -B tsc/build_forest_rscript.py \
  res_ft/Forest /home/idleness/Source/renpy/Forest
/opt/apps/renpy7/renpy.sh /home/idleness/Source/renpy/Forest lint
```

Android 构建：

```bash
/opt/apps/renpy7/renpy.sh /opt/apps/renpy7/launcher \
  android_build /home/idleness/Source/renpy/Forest
```

每次构建后应检查：

1. APK 的时间、大小和版本名确实来自本次构建；
2. APK 内的 `forest_compat.rpyc` 和 shader 是新生成版本；
3. PC lint 无错误；
4. Android 真机能启动、显示日文、播放 BGM/voice/SE；
5. 触屏控制、存读档、系统 flag 和多周目分支正常；
6. 片尾文字对象及 action 4 的视觉效果与原版一致。

## 7. 已知边界

“所有 opcode 都已生成”不等于“所有通用 RScript 语义都已实现”。runtime 中仍有若干针对其他游戏的占位命令；Forest 当前使用的部分初始化命令由固定 800×600 界面参数等效覆盖。若迁移下一款游戏，应重新统计实际 opcode、参数取值和占位 handler 的调用次数，不能直接假设 Forest 的兼容层足够。

当前 lint 还会报告少量既有警告，包括非 ASCII 资源文件名、无法静态证明可达的跳转 label，以及未完整描述的 colormode。发布前应结合实际路线和 Android 真机测试判断，而不是仅依赖 lint。

## 8. 对后续项目的建议

1. 先制作可重复的资源解包和转码流程，再开始写解释器。
2. 先实现能遍历全部脚本的结构解析器，语义实现随后逐项加入。
3. 每个新 opcode 至少留下“真实出现次数 + 代表性生成结果”的回归断言。
4. 把游戏专用修正集中在单一生成器，避免污染通用 runtime。
5. 所有手工视觉判断记录原版截图、场景号和 GSC 偏移。
6. 将生成工程单独纳入 Git；提交源码，不提交存档、日志、密钥和编译缓存。
7. PC 验证、GLES 模拟和 APK 成功只能降低风险，最终结论必须来自真机完整游玩。
