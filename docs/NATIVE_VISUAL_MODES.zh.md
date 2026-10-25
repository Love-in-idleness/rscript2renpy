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
load/cls 的对角移动、18、复杂退出 30～35，move 4/11～13 及 oaction 其它动作
仍需各自的轨迹、对象类型和时序核实；已有近似的动画也不等于逐帧一致。
