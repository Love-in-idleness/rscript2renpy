# 开发参考：RScript 初始化配置

[返回文档目录](README.zh.md)

新适配可先查看 `RsInit.tcf`，获取窗口尺寸、资源目录和启动线索。
不是所有游戏都有此文件或 `RsInit.dll`；缺少时需从 EXE 和脚本确认。

## 检查工具

```bash
python3 tools/inspect_rscript_init.py /path/to/game-resources
python3 tools/inspect_rscript_init.py /path/to/RsInit.tcf --encoding gbk
```

工具只读文件，将 JSON 报告输出到终端，不执行 EXE 或 DLL。
默认文本编码为 CP932，可通过 `--encoding` 指定。
报告包括配置值、资源目录、CFG 是否存在及无法识别的项目。

## 已确认的键

以下来自已分析的 Khime Zero 初始化模块：

| 键 | 用途 |
| --- | --- |
| `title` | 窗口标题 |
| `width`、`height` | 初始化画面尺寸 |
| `exec`、`script` | 初始化脚本开关和编号 |
| `scrdir` | 剧本目录 |
| `sysimgdir`、`layerimgdir`、`faceimgdir`、`bgimgdir` | 图像目录 |
| `moviedir`、`wavedir`、`bgmdir`、`voicedir` | 媒体目录 |
| `savepfx` | 原引擎存档前缀 |
| `scrmod`、`extmod` | 编译器和扩展模块名称 |
| `bgm`、`bgmsource`、`layermod` | 数值字段，具体取值语义尚未确认 |

TCF 不一定是最终配置，CFG 或主程序默认值可能优先。
不要把一款游戏的配置当作所有引擎版本的规则。

## 原生依据

`Khime_zero/RsInit.dll`，SHA-256：
`b35bd24626a65d67ee932f2a62076070805c98b5f7a50f9920c19f2d8696b218`。

- `GetInitialData`（`0x10001dd0`）读取 TCF，填入调用者结构。
- `SaveInitialData`（`0x10002170`）将该版本的 324 字节结构写入 CFG。
- 主程序 `0x415330` 先尝试 CFG，失败后才从 TCF 初始化。
- 中文样本的标题使用 GBK，注释仍有 CP932，不能整份文件统一猜编码。

以上为该构建的静态依据。检查工具不需要分发 DLL。

## 检查

```bash
python3 -B tests/test_rscript_init.py
python3 -B tests/test_rscript_init.py /path/to/Khime_zero
```
