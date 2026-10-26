# 开发参考：原生色彩与绘制模式

[中文](NATIVE_VISUAL_MODES.zh.md) | [English](NATIVE_VISUAL_MODES.en.md) | [Русский](NATIVE_VISUAL_MODES.ru.md) | [日本語](NATIVE_VISUAL_MODES.ja.md)

[返回文档目录](README.zh.md)

## 样本与范围

从 Evermaiden 的较新引擎开始，再核对六个移植项目及 Khime Zero。
原 EXE 只读分析，未启动游戏；以下地址均为相应样本的 VA。

| 样本 | SHA-256 |
| --- | --- |
| Forest / Forest.exe | `8eb71d07304d362ec26cc47d93c6ef5854b5acadd7c9fe941755ad50820a3e56` |
| Khime / KhimeDL.exe | `2dfc7b78d32867716ab0406ccbf176b55a76faea1cb9c40feac25c90775222fe` |
| Khime Zero / Khime_zero.exe | `56e3b1316c2fd3bdc7826606fedf938a5b7509385e4ba4300010c7892a7af76c` |
| CannonBall / Cannonball.exe | `df4b5b6dffc7002370d0772869baaba551b08fca970e92609ca64b08174f89ba` |
| SevenBridge / SBridge_jp.exe | `c7d5fc38cf0c354a61d056b607cf1367b2529557e9e0407d0b0fdf12771b35e3` |
| Kagerou / kagerou.exe | `f02998fae350945f4de4dc7eab47997e1e2d9b8aa43d49740a80aad893dcde9b` |
| Evermaiden / startup_jp.exe | `88820f28b8f770b486407e55dda28266c6fec42145192d5bc8ad5be21ab895af` |

SevenBridge 以 `SBridge_jp.exe` 为准，不以同目录其它同名启动程序代替。

## 色彩模式

0 不变、1 黑色、2 反色、3 三通道算术平均灰度；14 不变。
4～13 使用下表算法及 RGB 常量，不是 HSV 滤镜。

| 模式 | 算法 | RGB |
| --- | --- | --- |
| 4 | Tint | `8b4513` |
| 5 | Tint | `483d8b` |
| 6 | Tint | `ff8000` |
| 7 | Night | `181020` |
| 8 | Level | `282040` |
| 9 | Level | `383080` |
| 10 | Level | `802d50` |
| 11 | Night | `904030` |
| 12 | Level | `805030` |
| 13 | Level | `a06040` |

```text
Grade(x,k) = floor(x*(k+1)/128)                  if k < 128
             floor(x+(256-x)*(2*k-255)/256)     otherwise
Tint(C,T) = Grade(T, floor((R+G+B)/3))
m = min(R,G,B)
Night(C,T) = floor(C*(256-m)/256) + floor(Grade(C,T)*(m+1)/256)
```

所有颜色运算保留 alpha。15 是带字节量化、分段色相偏移的 HSL Power，
不是统一增加饱和度。原生像素例：红→(255,1,1)，绿→(7,255,1)，蓝→(255,192,1)。

Forest 支持 1～6；CannonBall、Khime Zero 支持 1～5。
Khime、SevenBridge、Kagerou、Evermaiden 的扩展系列区分对象类型：
Full 支持至 13，Lim 另有 15，14 仍不变。Evermaiden 的对象模式 1 选 Full。
未列出的 WORD 编号保持图像不变，不应标成未实现并强制清零。
公共层保留图层的颜色状态，使移动、旋转和退出过程不丢色。

## 绘制与遮罩

新版 `draw 3` 按遮罩的各通道对下层画面执行 `Grade(destination, mask)`，
不使用 Level，也不是普通 alpha 绘制。按用户决定，旧引擎的 draw 3 普通绘制别名
统一采用这项新版含义；其它旧编号别名继续保留。
`draw 4/5` 分别使用黑/白 LUT，强度为 `WORD(Level)*255//100`。
Kagerou 已有的命名 `dim256` 路径仍接收转换后的字节强度，不做第二次百分比换算。
`effect` 的非 1 模式复用 Grade，不再使用 GIMP Color-to-Alpha 近似；1 仍为目标反色。

Grade 通过两次 GPU 混合实现：先逐通道缩放目标，再添加高光。
两次 framebuffer 舍入允许相差两个色阶；不宣称与 GDI 每个边缘像素完全一致。
透明覆盖率、深度及普通图层的拼接逻辑保持；文字对象不参与位图拼接。

## 对角进出与条纹擦除

`load/cls 11～14` 使用量化余弦路径，11～14 对应左上、右上、左下、右下。
起点或终点取 `(-图宽,-图高)`、`(画布宽,-图高)`、`(-图宽,画布高)`、
`(画布宽,画布高)`；普通位置先扣除 locmode 的图像锚点。

原生 `44d4c0` 的第三参数是速度，不是帧数：
`speed=(distance & 65535)//15`，再计算 `steps=distance//speed`。
逐 tick 复用动态选择菜单的 Q16 余弦查表；第一个 tick 保留起点，最后补终点。
分组对象同时开始，共用最长等待，不按对象数量累加时长。

`load/cls 18` 是每 16 像素一组的竖条擦除，条件为
`x % 16 > level//16`。17 的既有 alpha 路径是行与斜纹组合，不把两者混同。
17/18 的 level 每 tick 改变 16，使用各适配的 `rscript_dynamic_tick`。
`update 5～99` 均进入 efNN 遮罩路径，原先漏掉了 5～10。

依据：`412e40` / `411b10`（对角与 renderer 21 分派）、`44d4c0 / 44d070`（路径）、
`443900`（竖条像素循环）、`45a710`（level 初始化）、`43b390`（update 范围）。
REA：`ev_d9a7d2b4a36144041f457d8269e9a0043f32474366870c125e98132d9e1f7210`、
`ev_5397d397711d9b7194b22de4675c82e3c8e7bb18695dc368a985c8acb4083876`、
`ev_500edda26e2d17c7ecb107b1553abf292437b9b826a64f6e039ac4fb1f1aa231`、
`ev_21e4dc7d33cac2c8ef9a1b30a02e32ae135bf467534de6539d7991b7eaac044b`。

## move 4：保留各作原义

核对真正的移动调用链后，各作的 4 均为带正弦法向偏移的波浪轨迹，不是图像副本切换。
此前把 Forest 的 `401280` 图像切换表误认作移动表；真正的移动入口是 `405f00`。
这项更正不改变用户决定：按各作原义实现，不统一速度规则。

| 游戏 | 移动入口 → 路径初始化 | 原生速度规则 |
| --- | --- | --- |
| CannonBall | `404d80 → 4253c0` | 固定每 tick 30 个资源像素 |
| Khime Zero | `405890 → 42e950` | `max(1, WORD(distance//15))` |
| Forest | `405f00 → 436e20` | 同上，不使用脚本速度参数 |
| SevenBridge | `407090 → 43c310` | 同上，不使用脚本速度参数 |
| Khime | `408f30 → 43da10` | `max(1, WORD(distance//(WORD(Speed) or 15)))` |
| Kagerou | `408530 → 4463b0` | 同上 |
| Evermaiden | `413e40 → 44d730` | 同上 |

路径取 `steps=WORD(distance//speed)`，垂直于位移的振幅向量为 `(dy,-dx)*3/20`。
直线分量使用 Q16 整数，正弦相位增量为 `WORD(2*65535//steps)`；除法向零截断。
初始帧保留起点，原生步数用尽后补终点；零步数不激活移动，不能强制瞬移。
先在资源像素坐标中计算，再应用移植缩放；保留锚点、颜色、分组并行与最长等待。
`_move/_movi/_gmove` 共用此实现，104/204 保留已有残影路径，不宣称残影逐帧一致。

REA：`ev_e8d83ef9e7e6a073bc784176918a94c06b5e7715f298ce93921418e9d26f5764`、
`ev_14e88ba825c8a4919b11bd063c48134ac3331867e94a68b6831db5c864491c73`、
`ev_cc4f3dfd1759d85c74ad594f7fe11fcf30b2196cec83aaaaa5b5e59a161bb42f`、
`ev_387005b14b0fcd75ea8e3547485156aa791cdc29b0ea59735d34b482758e432b`、
`ev_ff72b51a8553cb687a0287fd749e36556fe9da490823b482309d1e885a8b0e61`。

## 原地弹跳与复杂退出

`move 11/12/13` 在七个样本中均忽略 X/Y/Speed，在当前位置竖直弹跳。
振幅/步数分别为 40/4、100/10、300/15；相位步长为 `0x8800//steps+2`。
初始帧不动，下一 tick 开始查表，第 `steps+1` tick 恢复原位。
残影编号先按 WORD 取值再 `%100`；保留各作 tick 和坐标缩放。

`cls 30～35` 使用相同的原生分派：30 为 75% 斜切后左下移，
31 为两片上下移，32 为上片沿上半圆左移，35 为上下两片左右移；
30/32 每 tick 淡出 14/256，31/35 为 16/256。
33 为 250 像素弹跳并从首 tick 的 6% 放大，34 为同样弹跳并旋转缩小。
切割、缩放和旋转只作用于 Full；Lim/Anim 的对应虚函数为空，仍保留移动和淡出。
CannonBall 使用直接仿射对象，没有后来的 Full/Lim 开关，不能按缺省模式 0 禁掉这些效果。
33/34 等待分别为 21/22 tick；非 Full 的 34 仅等待弹跳的 21 tick。
分组并行并在结束后清理图层，不累加等待。

依据：`413e40 / 44d570 / 44d070`（弹跳）、`411b10`（退出分派）、
`46be30`（切割）、`415e80`（仿射步进）、`412b00`（对象类型）。
REA：`ev_a1576cf9d2880f5839d03d362097d8db9095dbb47cf870b75e172d95f5e0fb4f`、
`ev_d28ed370b7e7430a2ffd97d08b1d96ce6ab4732ba25aae3982a7b4dc241ff9dc`、
`ev_6d2c711654b8de936d6dba4104fb9e76f52cc8cbcccab87d1a3dab6e5d8277ea`。

## 对象动作 phase / oaction

TSC 的 `phase` 经所有适配的公共生成器输出为 `_oaction`，不再只给早期方言放行。
0 复原；1/2 绕中心逆时针旋转，步长 10/20，满 256 后复原；
3/4 从 255 递减，绕中心顺时针旋转，步长 10/20，结束复原。
7/8/9 绕左下角逆时针转至 64；10/11/12 绕右下角顺时针转至 192，
两组步长均为 8/12/30。终态保留到复原或清除，不因移动而重播。

按用户最新决定，所有移植的 5/6 统一采用旧版类型 18 的底边居中拉伸：相位每 tick 加 10/20，
`u=trunc(sin(phase/256*2π)*50)`，宽/高百分比为 `100+u / 100-u`；
尺寸沿用 Q16 整数截断，相位达到 128 后复原。
Evermaiden 原 EXE 的 Full 虚表槽 `+0x54` 已变为 tick 函数；这里有意不用其
“推进当前动作一帧”的特殊行为，也不保留切换分支。原生编号越界不做动作；关闭效果或跳过时复原。
保存可回滚状态，并保留位置、颜色、深度；清除和重建对象同时清掉动作状态。
位图批处理按每个图层的显示时间换算动画时钟，单图和拼接组都不再把绝对时间当成已播放时长。

依据：Evermaiden `4145c0 / 415e80 / 46c3b0 / 46cd80`；
旧版拉伸初始化为 Forest `4077c0`、Khime `40a980`、Zero `4070f0`、
Kagerou `40a800`、CannonBall `4247e0`；SevenBridge 分派为 `407740`。
REA：`ev_ec0d3fd6f8b2523fde9f7a676a88206246ed28ad00ac2965863a4a0540deb23f`、
`ev_8671b6a05e98ec7f5a2a4fbb7969e1b6dca469b930bcebe324cbe72f8e83b070`、
`ev_9d78c679eb00e624a39e10e228850a608347efe6e8f5578232c8c88b2a148147`、
`ev_ab013bbb9b37ab7772b276bb3503d84148bf934523e6cc6cfe3568118afe130e`。

## 依据

- Evermaiden: `4154d0 / 415810` (Full / Lim), `44d880` (CMath),
  `461a70 / 461c90 / 461e50` (Level / Night / Power).
- Forest: `407fe0 / 408200`; Khime: `40b1a0 / 40b710`;
  Zero: `407910 / 407b00`; CannonBall: `4056d0`;
  SevenBridge: `409820`.
- REA: `ev_75cb85845a085eaa225b93c2ab638203ea2858f7a100edc6ed6a153582bb224a`,
  `ev_8fd952896a36ca15b3b46ccc02fbd32d104f0c3c516dfe76985a7b10aea65ac9`,
  `ev_f8cf3c06d5dfc8f6cb7d77e805c6e00d8fc35f59be596699c1fea2aca8f7a730`,
  `ev_905392cadc15179ebc74e6479ea8cad674b695c001ad6199612d5bb5dfea6b06`.
- Draw: `4129b0` → renderer `2 / 14 / 104 / 3 / 4`,
  `4464e0` case `104`;
  `ev_d72f2de30d9317ab80890eccc8c6d517851b60fbe84c35787f324ef2d2975b49`,
  `ev_2cb8389d102a8c15d2314404097b4b9c666238e5159e510d42ef00c7551d4863`.

## 检查与剩余工作

Power 的独立 float32 参考与受限原生像素例程在 5102 个合成 RGBA 样本中一致；
原生代码和私有测试载体不入库。公共 GL2 测试覆盖颜色、移动中/后状态、旋转、
清除、draw 3/4/5、普通模式恢复及跨 CG 层混合；不是完整游戏游玩验证。

尚不能把“可接受参数”当成全部显示效果已复制。
GL2 测试已覆盖上述弹跳和复杂退出的初始、中间、结束帧、Full/Lim 差异，
以及对象动作的支点、实时拉伸、单图/拼接组时钟、终态、移动后状态和清理；
切割边缘、仿射采样和既有近似动画仍不宣称与 GDI 逐像素一致。
