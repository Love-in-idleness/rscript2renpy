# 环境配置与首次构建

本指南供第一次使用 rscript2renpy 的用户配置环境并构建已经支持的游戏。
已有适配不需要 AI；新游戏需要开发自己的适配层，见
[新游戏移植指南](NEW_GAME_PORTING.md)。各游戏的版本要求和参数以
[主 README 的游戏列表](../README.md#游戏移植说明)为准。

## 依赖

| 工具 | 用途与要求 |
| --- | --- |
| Git | 获取和更新项目源码 |
| Python | 建议 3.11+，可直接读取本机 TOML 配置；生成器运行于 Python 3 |
| Pillow | 图像处理，安装到生成器使用的 Python 环境 |
| Ren'Py SDK | 使用 Ren'Py 8；本机验证基准为 8.5.3，不代表所有 8.x 均已验证 |
| LiarsoftTool | 解包、GSC→TSC、图像和音频预处理；使用支持当前 TSC 格式的版本 |

生成器使用系统 Python，游戏运行使用 SDK 自带的 Python，两者不是同一个环境。
先按 [Ren'Py 官方说明](https://www.renpy.org/doc/html/quickstart.html)解压 SDK，
保留完整目录；Linux 运行 `renpy.sh`，Windows 运行 `renpy.exe`。
升级 SDK 后需要重新执行相关原生测试。

LiarsoftTool 可使用其仓库提供的预编译 CLI，也可按
[编译说明](https://github.com/Love-in-idleness/LiarsoftTool#中文)从源码构建。
源码编译需要 C++17 工具链、CMake、WebP、Vorbis/Ogg 及平台需要的 Iconv。
GUI 不是移植必需依赖，Windows 的运行时库要求以工具说明为准。
Wine、Windows 虚拟机、RsComp.dll 和 Android SDK 都不是已有端口构建的必需项。

## 获取代码与 Python 环境

以下命令以 Linux 为例，在自己选择的工作目录执行：

```bash
git clone https://github.com/Love-in-idleness/rscript2renpy.git
cd rscript2renpy
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Pillow
python --version
python -c "from PIL import Image; print(Image.__version__)"
```

Windows 可在仓库根目录执行，不必修改 PowerShell 的脚本执行策略：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install Pillow
```

下文的 `python` 在 Windows 可替换为 `.\.venv\Scripts\python.exe`；
工具路径使用相应的 `.exe`。Python 环境说明见
[venv 官方文档](https://docs.python.org/3/library/venv.html)。不要提交虚拟环境。

## 目录、路径与权限

建议分开保存原件、转换副本和输出，所有 `/path/to/...` 都需替换为自己的路径：

```text
work/
├── rscript2renpy/       # 本仓库
├── LiarsoftTool/        # 可选的工具源码仓库
├── renpy-sdk/          # 完整 SDK
├── originals/Game/     # 合法持有的原游戏，保留不动
├── prepared/Game/      # 原游戏的完整副本，供解包转换
├── patches/Game.zh/    # 补丁原件，保留不动
├── prepared/Game.zh/   # 补丁转换副本
└── projects/Game/      # 新的 Ren'Py 输出目录
```

先复制游戏和补丁，再转换副本。保留原始 EXE、GSC 和 `.meta.xml`，不要将输入
目录当成输出目录。游戏更新、特典和补丁必须匹配适配器支持的版本；例如 Kagerou
仅支持安装「ハチポチ特典」后的版本，不能仅凭游戏名称判断兼容性。

可将 `local.paths.example.toml` 复制为 `local.paths.toml`，填写工具、资源副本和
输出的绝对路径。它只记录位置，不会自动注入生成器参数，也不会自动启用补丁；
不需要路径配置时可直接使用 CLI。当前示例含 Forest/Khime，并不是任意游戏的
自动注册入口。具体读取方式见 [本机工作流](LOCAL_WORKFLOW.md)。
`rebuild_local.sh` 是被 Git 忽略的本机便捷脚本，不是对外构建入口。

使用 AI 编辑器时，以代码仓库为工作区：原件和补丁原件只读，源码仓库、转换
副本及指定输出目录可写。跨仓库修复时才开放 LiarsoftTool 源码的写权限。
不要为移植开放整个主目录的写权限，遇到权限限制也不要绕过。

## 转换资源

对已确认采用 CP932 的日文资源副本执行：

```bash
/path/to/liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 \
    /path/to/prepared/Game
```

这一步递归解包并转换，生成器本身不会调用 LiarsoftTool。应得到当前命令式
UTF-8 `scr/*.tsc`、可用图像（PNG/WebP）及音频，保留复合图 `.meta.xml`。
含 Ogg 的封装 WAV 应提取为 OGG；普通 PCM WAV 可直接使用，不需要强制转换。
具体资源目录和视频要求见游戏 README。

补丁在自己的副本中单独转换。输入编码必须根据文件确认，不能按 `zh/en/ru`
标签推断；例如中文补丁可能需要 `-e gbk`。TSC 正文始终为 UTF-8。
不要把补丁先混入日文副本，再用一种编码转换所有 GSC。

工具升级后，如果需要从保留的 GSC 重建已有 TSC，可执行：

```bash
python tools/refresh_tsc.py /path/to/prepared/Forest \
    --liarsofttool /path/to/liarsofttool \
    --encoding cp932 --dialect forest --force
```

这只是已知 Forest 方言的示例。其他已支持方言见 `--help`；未知游戏不能硬套
`forest`。`--force` 会覆盖手工编辑的 TSC，先备份；整批写入不是事务。

## 构建与检查

先查看所选生成器的参数。例如 Forest：

```bash
python forest/build_forest_rscript.py --help
python forest/build_forest_rscript.py \
    /path/to/prepared/Forest /path/to/projects/Forest \
    --language jp --language zh=/path/to/prepared/Forest.zh
```

无补丁时省略 `--language zh=...`。单独的 `jp` 是原版标签；`zh=目录` 是补丁
标签和目录，不负责转码。标签、字幕插入和整场景覆盖规则以各游戏 README 为准。
生成器会创建工程，不需要先在 SDK 中创建模板或提供 `gui.rpy`。

新工程的脚本在 `game/scr/`，公共引擎在 `game/engine/`，语言资源在
`game/tl/<语言>/`。第一次使用新输出目录；重建前备份人工修改。Forest 会覆盖
生成文件，其他入口的 `--force` 规则须查看各自说明。

Linux 可执行静态检查：

```bash
/path/to/renpy-sdk/renpy.sh /path/to/projects/Forest lint
```

Windows 可在 SDK Launcher 中将项目目录指向 `projects/`，选择工程执行 lint
和启动。随后人工检查标题、首段对话、背景、立绘、语音、选择和存读档。
Lint 通过不证明完整路线或 Android 可用。SDK、编码、工具版本及构建命令应与
错误日志一起提供，避免只报告“生成了但不能运行”。

## 授权与发布边界

本仓库只发布代码，不发布新的 Release 或版本包。原游戏资源、生成工程、
存档、签名密钥不提交；本机路径也不提交。现有例外资产和字体授权见
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)。合法持有游戏不等于获得
素材、字体或完整移植包的再分发授权。
