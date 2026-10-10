# rscript2renpy &nbsp; [中文](#中文) | [English](#english)

## 中文

`rscript2renpy` 是面向 Liar-soft/raiL-soft CodeX RScript 游戏的实验性
Ren'Py 兼容运行时与移植工具。公共层提供寄存器、自定义指令、图像、音频、
文字、特效、菜单和触屏控制；各游戏目录维护自己的方言与适配策略。

运行时面向 Ren'Py 8（Python 3）。项目只维护 Git 仓库源码，不再发布新的
GitHub Release 或版本包。生成成功、自动测试和 lint 均不代表完整移植成功。

除通用鼠标光标和各游戏应用图标外，仓库不包含游戏剧本、图像、音频、视频或
可执行文件。用户必须使用自己合法持有的游戏文件，自行准备资源并构建工程。

### 游戏移植说明

各游戏的资源要求、生成命令、语言补丁规则、专用行为和验证边界分别维护在
对应目录。以下是同一仓库内的适配项目，不要求切换 Git 分支。
命令示例均在仓库根目录执行。

| 项目 | 说明 |
| --- | --- |
| Forest | [forest/README.md](forest/README.md) |
| Khime Kusaritop（含可选 Khime Zero） | [khime/README.md](khime/README.md) |
| Evermaiden | [evermaiden/README.md](evermaiden/README.md) |
| CannonBall | [cannonball/README.md](cannonball/README.md) |

### 依赖与资源预处理

需要 Python 3、Pillow 和 Ren'Py 8 SDK。资源预处理依赖
[LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool)：
递归解包 XFL/LWG、GSC→TSC、WCG/LIM→PNG，以及封装 WAV→OGG。
普通 PCM WAV 可直接使用；不能把含 Ogg 的封装 WAV 当成普通 WAV 播放。

```bash
liarsofttool -R --unpack-only --gsc-to-tsc /path/to/resources
```

各生成器只读取当前命令式 `scr/*.tsc` 和转换后的资源，不链接或调用
LiarsoftTool，不接受 GSC 输入或旧 `;@gsc-structure-v1` 转储。
本次格式验证使用 LiarsoftTool 2.2.2；具体字节格式、schema 和资源要求见各游戏说明。
TSC 正文为 UTF-8，旧 `;@gsc-text-encoding` 注释不影响读取。
命名入口和 `insub` 目标必须保留新版生成的标签，不回退到旧数值地址。

升级工具后，可用 `tools/refresh_tsc.py` 单独重建已解包目录中的 TSC：

```bash
python3 tools/refresh_tsc.py /path/to/resources \
    --liarsofttool /path/to/LiarsoftTool/build/liarsofttool \
    --encoding cp932 --dialect forest --force
```

按实际游戏选择 `--dialect`：Forest 为 `forest`，Khime 为 `khime`，Evermaiden
为 `modern`，CannonBall 和 Khime Zero 为 `legacy`。编码必须根据输入文件指定，
不能仅凭语言标签判断；相同编码与方言的多个资源目录可一起传入。
该预处理工具显式调用 LiarsoftTool，在临时目录导出并校验整批脚本后逐文件
原子替换；原 GSC 不变。已有 TSC 需加 `--force`，手工修改会被覆盖。
写入不是整批事务，磁盘或权限错误仍可能中断安装；混合编码的未翻译文本
也不会自动修正。

### 通用模板与输出

新移植从 [port_template/README.md](port_template/README.md) 开始。
共用运行时位于 `runtime/`，构建和界面位于 `port_template/`，游戏差异位于
各适配目录的生成器和 `game/*.rpy` 覆盖层。分层约定见
[公共模板说明](docs/SHARED_TEMPLATE_MIGRATION.md)。

生成工程保留原资源目录：剧本在 `game/scr/`，图像在 `game/grp*/`，音频在
`game/bgm/voice/wav/`，视频在 `game/mov/`；运行时、公共界面和配置在
`game/engine/`。语言资源位于 `game/tl/<语言>/` 的对应目录。
旧 `images/scenario/audio` 布局和根目录旧运行时不迁移；请生成到新工程目录。

只安装通用运行时：

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

该命令安装共享折行器和光标，默认拒绝覆盖不同内容的文件；确认覆盖时加
`--force`。通用光标来自 Forest 原版，后续移植也使用同一资源。
各生成器安装共用 Android 启动说明，包含项目地址及正版资源自行构建提示。
PC／Android 版本由 `port_template/build_port.py` 的 `PORT_VERSION` 统一管理，
当前为 `1.3`，安卓版本代码最低为 `13`，保留已有更高值。
签名密钥不入库、不复制；生成配置与图标不代表已完成打包或实机验证。

开始新适配前，可只读检查 `RsInit.tcf` 和初始化线索：

```bash
python3 tools/inspect_rscript_init.py /path/to/resources --encoding cp932
```

该工具不执行 EXE／DLL，不改变资源或生成器。已知键、CFG 优先级、混合编码与
证据边界见 [RScript 初始化参考](docs/RSCRIPT_INITIALIZATION.md)。

### 验证

```bash
python3 -B tests/test_runtime.py
python3 -B tests/test_port_template.py
python3 -B tests/test_shared_port.py /path/to/renpy-sdk --logic-only
/path/to/renpy-sdk/renpy.sh /path/to/renpy-project lint
```

游戏专用测试见各适配 README。静态检查、算法测试、SDK 检查、lint、实际画面、
完整路线与 Android 实机验证分别报告，不互相替代。
统一禁则与真实字形度量见 [文字布局说明](docs/TEXT_WRAPPING.md)。

### 授权

代码采用 [MIT License](LICENSE)。第三方代码、光标、图标和字体说明见
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。Noto CJK 字体采用
[SIL Open Font License 1.1](port_template/fonts/NotoSans.txt)。
SimHei 不适用 MIT/OFL；本项目未取得或验证额外再分发授权，见
[SimHei-NOTICE.md](port_template/fonts/SimHei-NOTICE.md)。

---

## English

`rscript2renpy` is an experimental Ren'Py 8 / Python 3 runtime and porting tool
for Liar-soft/raiL-soft CodeX RScript games. Shared code lives in `runtime/` and
`port_template/`; each game directory provides its own dialect and adapter.

The repository distributes source only, with no new GitHub Releases or versioned
packages. Apart from the shared cursor and application icons, it does not include
proprietary game data. Build from resources you legally own.

### Game guides

Resource requirements, commands, patch policies, game-specific behavior and
verification limits are documented separately. These are directories in one
repository, not Git branches. Run command examples from the repository root.

- [Forest](forest/README.md) — includes an English guide.
- [Khime Kusaritop and optional Khime Zero](khime/README.md).
- [Evermaiden](evermaiden/README.md).
- [CannonBall](cannonball/README.md).

### Dependencies and resource preparation

Use Python 3, Pillow, a Ren'Py 8 SDK and
[LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) to prepare
archives, current command-based TSC, images and playable audio. Builders do not
invoke LiarsoftTool or accept GSC/old structure dumps. Ordinary PCM WAV is
playable; wrapped Ogg must be extracted first.

`tools/refresh_tsc.py` explicitly invokes LiarsoftTool to refresh TSC from GSC.
Choose the correct encoding and dialect; `--force` overwrites edited TSC.
Each replacement is atomic, but the batch is not transactional. Original GSC
is unchanged. TSC text is UTF-8; keep current named-entry and `insub` labels.

### Shared template and output

See the [new-game template](port_template/README.md),
[shared architecture](docs/SHARED_TEMPLATE_MIGRATION.md),
[text layout](docs/TEXT_WRAPPING.md) and
[initialization reference](docs/RSCRIPT_INITIALIZATION.md).

Output retains native resource directories. Scripts live in `game/scr`, runtime
and configuration in `game/engine`, language packages in `game/tl/<language>`.
Legacy layouts are rejected rather than migrated. To install only the runtime:

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

Existing different files require `--force`. Ports share the original Forest
cursor and an Android loading notice with the project URL and legal-resource
build instructions. Shared PC/Android versioning does not imply successful APK
builds or device testing. Signing keys remain local.

### Verification and licensing

Use the shared checks above and the game-specific guide. Tests and lint are not
proof of complete gameplay, audiovisual accuracy or Android compatibility.

Project code uses the [MIT License](LICENSE). See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for other assets and licenses.
Noto CJK uses [OFL 1.1](port_template/fonts/NotoSans.txt); SimHei is separately
licensed, with no additional redistribution rights verified by this project.
