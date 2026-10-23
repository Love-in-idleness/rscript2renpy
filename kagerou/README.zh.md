# KagerouTouryuuki 移植说明

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md)

[返回主说明](../README.zh.md)

## 概述

将用户自备的《霞外籠逗留記》资源生成 Ren'Py 8 工程。

只支持安装「ハチポチ特典」后的游戏，未安装特典的旧版不支持。
适配仍在完善。以下命令均在仓库根目录执行，环境安装见 [首次构建](../docs/SETUP.zh.md)。

## 准备资源

在安装特典后的游戏工作副本中转换：

```bash
liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/KagerouTouryuuki
```

保留原 `kagerou.exe`、`scr/*.tsc`、全部 `grp*` 图像目录及 `.meta.xml`、
`bgm/voice/wav` 和 `mov`。中文补丁在自己的副本中单独转换。

生成器需要已支持版本的 EXE 来读取布局；它不会执行或复制 EXE。
资源副本中没有 EXE 时，用 `--exe /path/to/kagerou.exe` 指定。

## 生成工程

```bash
python3 kagerou/build_kagerou_rscript.py \
    /path/to/KagerouTouryuuki /path/to/renpy/KagerouTouryuuki
```

输出目录可由脚本创建。重建前备份手工修改，并加上 `--force`。

## 语言补丁

```bash
python3 kagerou/build_kagerou_rscript.py \
    /path/to/KagerouTouryuuki /path/to/renpy/KagerouTouryuuki \
    --language jp --language zh=/path/to/KagerouTouryuuki_CHS
```

补丁必须匹配特典版。按原资源相对路径放置，只需提供修改的文件。
语言包使用整场景覆盖，缺少译文的场景使用当前原版。

## 使用说明

默认竖排。文字面板可以切换横竖排、字号、位置、阴影和字体，
切换方向不会改变所选字号。Back 与滚轮向上都执行回滚。

角色语音开关位于原图设置页。CG、场景和音乐鉴赏使用特典版脚本及资源。
启动视频只在打开游戏时播放，缺少的视频会跳过。

## 检查与已知限制

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy/KagerouTouryuuki lint
```

超长段落的段内分页、部分转场、原生记录页外观和原版存档导入尚未完成。
请检查实际排版、语音、鉴赏、完整路线及 Android。

开发检查：`tests/test_kagerou_native.py`、`tests/test_kagerou_builder.py`、
`tests/run_kagerou_port.py`。原程序依据见 [开发参考](NATIVE_EVIDENCE.zh.md)。
