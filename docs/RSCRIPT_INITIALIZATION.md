# RScript 初始化知识与只读检查工具

这份参考用于开始新的移植，不改变 Forest／Khime 的生成器、资源布局、
启动场景、画面尺寸或存档目录。大部分游戏没有 `RsInit.dll`，缺少它并不是错误。
初始化配置只是适配证据之一，不是所有 CodeX 版本共用的完整规范。

## 独立工具

```bash
python3 tools/inspect_rscript_init.py /path/to/game-resources
python3 tools/inspect_rscript_init.py /path/to/RsInit.tcf --encoding gbk
```

工具只读资源根目录或指定 TCF，将 JSON 报告写到标准输出。它不接受、加载、
执行或复制 EXE／DLL，也不调用 LiarsoftTool、生成器或 Ren'Py；只有 Python 标准库依赖。
不递归扫描游戏正文，不修改文件，不重命名或搬移资源。

报告提供：

- TCF 中可确认的标题、尺寸、`exec`／`script`、存档前缀和模块名称。
- 声明的资源目录及其在输入根目录下是否存在；Windows 反斜杠按路径分隔符检查。
  绝对路径、网络共享及越出输入根目录的路径只记录，不检查外部目录。
- 同目录 CFG 的存在及字节数，明确提示其可能覆盖 TCF；不解码未知二进制布局。
- 未知键、无法解码的原始值、重复键和不认识的语法。重复键不选“首个”或“最后一个”。

没有 TCF 时仍返回报告，但不猜测标题、800×600 缺省尺寸或启动场景。
`effective_configuration_confirmed` 始终为 `false`：工具报告的是配置文件观察，
没有运行引擎确认其最终初始化结构。使用者据此人工决定适配层和资源准备方式。

数值按十进制读取；文本值默认 CP932，可显式指定 `--encoding`。
先识别 ASCII 键和 `#` 注释，再仅解码有效配置值；不能把混合编码文件整份解码。
错误编码可能产生合法但错误的文字，工具不凭启发式自动猜编码。
中文 Khime Zero 应使用 GBK：它的日文注释是 CP932，但标题字节是 GBK。
UTF-8 值可使用 `--encoding utf-8`，UTF-8 BOM 会被去掉。

## 已确认的初始化键

以下 20 个键来自所分析的 Khime Zero DLL。新版本新增键保留在报告
`unknown_keys` 中，不把它们当作 opcode，也不套用已知键的语义。

| 键 | 已知用途／移植线索 |
| --- | --- |
| `title` | 原游戏窗口标题 |
| `width`、`height` | 初始化画面尺寸，不等同于素材最大尺寸 |
| `exec`、`script` | 是否执行初始化脚本、其编号；不意味着自动进入某条剧情 |
| `scrdir` | 剧本目录 |
| `sysimgdir`、`layerimgdir`、`faceimgdir`、`bgimgdir` | 系统图、对象图、脸图、背景图目录 |
| `moviedir`、`wavedir`、`bgmdir`、`voicedir` | 视频、音效、BGM、语音目录 |
| `savepfx` | 原引擎存档文件名前缀，不是 Ren'Py 存档目录 |
| `scrmod`、`extmod` | 编译器／扩展模块配置，仅记录名称，不加载模块 |
| `bgm`、`bgmsource`、`layermod` | 初始化数值字段；具体取值语义未确认，不据此生成运行时行为 |

缺失字段通常由调用者提供的初始化结构保留缺省值，因此 TCF 不是完整配置快照。
启动脚本、目录名和窗口尺寸应在新的游戏适配中独立核对；不要把 Khime Zero
的配置覆盖到主游戏或推广成所有 RScript 游戏的规则。

## 静态证据及限制

参考文件：`Khime_zero/RsInit.dll`；SHA-256：
`b35bd24626a65d67ee932f2a62076070805c98b5f7a50f9920c19f2d8696b218`。
文件及配置原件不纳入仓库，工具本身不依赖这份 DLL。

- `GetInitialData` 实现 `0x10001dd0` 读取 `RsInit.tcf`，把找到的键写入调用者结构。
  `title` 键地址 `0x1002e0e0`，其余已知键集中在 `0x1002e01c`～`0x1002e0dc`。
- `SaveInitialData` 实现 `0x10002170` 将 324 字节结构写入 `RsInit.cfg`。
  324 是这一 DLL 的结构大小，不是所有版本通用的 CFG 格式标识。
- 所提供的原游戏分析指出，主程序 `0x415330` 先尝试 CFG，打不开才调用 DLL
  读取 TCF。此调用顺序来自该游戏样本，不能凭任意同名 DLL 推断其他 EXE 的行为。
- 本次实际读取的 TCF 为“腐姬 ~jamais vu~”、640×480、`exec 1`、`script 0`。
  DLL 使用 ANSI 字节处理，不能据其存在推断整款游戏固定使用 CP932。
- 这些初始化证据没有新增 GSC opcode、图像解码或音频解码语义。

测试：

```bash
python3 -B tests/test_rscript_init.py
python3 -B tests/test_rscript_init.py /path/to/Khime_zero
```

第一项是合成输入与命令行验证；第二项额外核对已知真实 TCF 并检查输入哈希不变。
均非游戏运行或视觉验证，不需构建、重生成现有工程或运行 Ren'Py lint。
