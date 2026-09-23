# 通用 RScript 移植半成品模板

这个目录用于开始一款新的 CodeX/RScript → Ren'Py 移植。它只复用已经
跨游戏成立的部分，不声称自动兼容所有 RScript 方言。

## 输入约定

先用 LiarsoftTool 解包并转换用户合法持有的游戏资源。模板只接受转换后的
文件，不调用 LiarsoftTool，也不读取 EXE：

- `grp*/**/*.png`
- `bgm/**/*.ogg`、`voice/**/*.ogg`、`wav/**/*.ogg`
- `mov/**/*.mpg`
- 游戏专用 lowerer 生成的 `scenario/**/*.rpy`

原始 GSC、WCG、WAV、XFL 和 LWG 不会复制进 Ren'Py 工程。

## 开始新移植

1. 复制本目录并改名，例如 `cp -a port_template khime`。
2. 在新目录实现一个只负责当前游戏的 TSC → RPY lowerer，把结果写到准备目录的
   `scenario/`。不要在通用运行时里塞游戏特例。
3. 按需编辑 `build_port.py` 顶部的 `RESOURCE_TARGETS`；大多数 800×600
   CodeX 游戏不需要修改。
4. 运行构建入口；脚本会创建尚不存在的工程目录：

   ```bash
   python3 port_template/build_port.py /path/to/prepared-resources /path/to/renpy-project
   ```

5. 在游戏目录添加专用的界面、文本规则、标题流程和 runtime 覆盖文件；最后运行
   静态测试及 Ren'Py lint。

模板拒绝覆盖内容不同的现有文件。确认要同步模板或运行时更新时才使用
`--force`。

`grps/confscrn`、`grps/compane`、`grps/savescrn`、`sel_a*`、`sel_q*`、`tbox*` 有 PNG 时还会读取各目录的
`.meta.xml` 画布尺寸和坐标，生成 `grps_layout.rpy`。共用界面用原图实现设置、
存读档、选择项和对话控制条；游戏的 `say` screen 需 `use rscript_compane`，
`choice` screen 可 `use rscript_choice(items, prompt)`。
缺少坐标元数据会在构建时明确报错，而不是生成位置不明的界面。标题流程和
选择分支仍由各游戏脚本决定；素材命名或控制语义不同的作品需在专用适配层修改。

## 效果兼容检查

游戏专用 lowerer 可调用 `effect_compat.flatten_unsupported_effects(rpy, resources, "Game")`；
通用装配入口也会对每份 `scenario/*.rpy` 再检查一次。`_load`、`_cls`、`_oload`、
`_gload`、`_update`、`_effect`、移动、闪光、`_zupdate`、对象动作和混合模式中的效果及色彩模式，
只有运行时支持、且所需 `grps/efNN.png` 或 `grps/esNNN.png` 存在时才原样保留。
其余（包括无法静态判定的表达式）改为可执行的基础参数，并在 RPY 指令前注释
原值及原因；TSC 输入不改。将来实现新效果时，同步更新 `effect_compat.py`
的支持范围并重建场景。

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
├── effect_compat.py       # 运行时能力与资源遮罩检查
├── grps_layout.py         # 从复合图元数据提取界面坐标
├── game/
│   ├── grps_ui.rpy        # 共用设置、存档和控制条
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
