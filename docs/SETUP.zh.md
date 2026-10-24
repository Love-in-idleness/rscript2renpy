# 环境配置与首次构建

[中文](SETUP.zh.md) | [English](SETUP.en.md) | [Русский](SETUP.ru.md) | [日本語](SETUP.ja.md)

[返回主说明](../README.zh.md)

本指南用于构建已有适配的游戏。新游戏需要编写适配器，见
[新游戏移植指南](NEW_GAME_PORTING.zh.md)。下列 `/path/to/...` 均需替换为自己的路径。

## 1. 安装依赖

| 依赖 | 用途 |
| --- | --- |
| Python 3（建议 3.11+） | 运行生成脚本 |
| Pillow | 读取图片尺寸、生成应用图标 |
| Ren'Py 8 SDK | 运行、检查和打包工程 |
| [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) | 解包游戏，转换脚本、图像和音频 |
| Git | 获取项目源码 |

解压完整 Ren'Py SDK。Linux 使用 `renpy.sh`，Windows 使用 `renpy.exe`。
已有适配的普通构建不需要 Wine、RsComp.dll 或 Windows 虚拟机。

## 2. 获取项目

Linux / macOS：

```bash
git clone https://github.com/Love-in-idleness/rscript2renpy.git
cd rscript2renpy
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Pillow
```

Windows 在仓库根目录使用 PowerShell：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install Pillow
```

Windows 下的生成命令可将 `python3` 换成
`.\.venv\Scripts\python.exe`，Linux 使用已激活环境中的 `python` 或 `python3`。

## 3. 准备资源副本

原件、转换副本和输出工程分开保存：

```text
work/
├── originals/Game/       原游戏
├── prepared/Game/        用来转换的副本
├── prepared/Game.zh/     单独准备的中文补丁副本
└── projects/Game/        生成的 Ren'Py 工程
```

不要直接转换原件，不要让输出目录包含输入资源。
先查看对应游戏 README 的版本要求，例如 Kagerou 需要「ハチポチ特典」。

日文资源通常使用 CP932：

```bash
/path/to/liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/prepared/Game
```

中文补丁若使用 GBK，则在补丁副本中单独转换：

```bash
/path/to/liarsofttool -R --unpack-only --gsc-to-tsc -e gbk /path/to/prepared/Game.zh
```

转换后应有 `scr/*.tsc`、可用图像和音频。
保留 `.meta.xml`；普通 PCM WAV 和原始 MPG 可以直接使用。
需要重新导出脚本时仍使用 LiarsoftTool，覆盖前先备份修改过的 TSC。

## 4. 生成工程

以 Forest 为例，在仓库根目录执行：

```bash
python3 forest/build_forest_rscript.py /path/to/prepared/Forest /path/to/projects/Forest \
    --language jp --language zh=/path/to/prepared/Forest.zh
```

没有补丁就省略 `--language zh=...`。
`jp` 是基准语言标签，`zh=目录` 添加可切换的语言包；标签不负责转换文件编码。
各游戏的补丁规则不同，请以 [游戏说明](../README.zh.md#游戏移植说明) 为准。

首次构建使用新目录。重建前备份生成工程内的手工修改，按生成器要求使用 `--force`。

## 5. 运行和检查

```bash
/path/to/renpy-sdk/renpy.sh /path/to/projects/Forest lint
/path/to/renpy-sdk/renpy.sh /path/to/projects/Forest
```

Windows 可在 Ren'Py 启动器中选择生成工程，然后运行检查或启动游戏。
Android 打包使用 SDK 的 Android 功能，另需完成 RAPT 环境配置。

报错时保留完整输出，并提供游戏版本、构建命令和出问题的场景。
lint 通过后仍应检查实际画面、音频、选择和存读档。

## 其他说明

`local.paths.toml` 是可选的本机路径备忘，不是生成器必需配置，
见 [本机路径](LOCAL_WORKFLOW.zh.md)。

项目不提供游戏本体或预构建游戏包。分发前请检查
[第三方资源授权](../THIRD_PARTY_NOTICES.zh.md)，不要包含自己的存档或签名密钥。
