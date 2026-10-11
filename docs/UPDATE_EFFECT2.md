# update 效果 2：跨游戏原生依据

2026-10-11，只读核对用户提供的五款原版 PE32 EXE。效果 2 是 **4×4 有序点阵
替换**，不是马赛克，也不是把像素放大后再缩小。旧 Pixellate 调用按用户要求
保留为注释，公共运行时不再执行它。此结论仅对应下列已核实的构建。

## 调用链与表

以下均为 VA。先核对 update 分派表第 2 项，再跟踪模式 18 的不透明绘制分支；
不以“文件里存在同一张表”单独证明命令语义。

| 游戏 / EXE | update 第 2 项分支 → 过渡函数 | 点阵像素复制函数 | 16 WORD 表 |
| --- | --- | --- | --- |
| Forest / Forest.exe | `41c278[2] → 41c1be → 43ec10` | `431f00`，由 `42f393` 调用 | `463300` |
| Khime / KhimeDL.exe | `422290[2] → 4221d6 → 4482c0` | `439520`，由 `436983` 调用 | `46e100` |
| CannonBall / Cannonball.exe | `416404[2] → 41635d → 42bdb0` | `4207e0`，由 `41deb3` 调用 | `450070` |
| Evermaiden / startup_jp.exe | `43b5e4[2] → 43b50b → 4531d0` | `447077` 不透明分支（内联，`4471d0..4471f9` 复制） | `4eb550` |
| Kagerou / kagerou.exe | `41e7e0[2] → 41e726 → 4504e0` | `4437d0`，由 `440c33` 调用 | `47ef38` |

强度右移 4 选择表项；坐标按 `(x%4)+4*(y%4)` 选择其中一位。
位为 1 时复制新像素，位为 0 时保留旧像素。五款的表完全一致：

```text
FFDF EFDF 6FDF 6FD7 6BD7 6BD6 6B56 6A56
2A56 2A52 0A52 0A12 0812 0810 0800 0000
```

每帧强度 `floor((Step-frame)*255/Step)`，共 `Step-1` 帧，然后完整提交新画面。
`Step=0` 在 update 入口选为 10；`Step=1`、`Wait=0` 无名义动画等待。
等待由 timeGetTime/GetTickCount 的毫秒差值判断，而非百分之一秒。
因此此效果的名义时长统一为 `max(0,Step-1)*Wait/1000`。
原生绘制耗时、Sleep 和严格“大于 Wait”循环的额外调度时间没有模拟。
其他效果的已有兼容计时本次不改变。

## 构建身份

| EXE | SHA-256 |
| --- | --- |
| Forest.exe | `8eb71d07304d362ec26cc47d93c6ef5854b5acadd7c9fe941755ad50820a3e56` |
| KhimeDL.exe | `2dfc7b78d32867716ab0406ccbf176b55a76faea1cb9c40feac25c90775222fe` |
| Cannonball.exe | `df4b5b6dffc7002370d0772869baaba551b08fca970e92609ca64b08174f89ba` |
| startup_jp.exe | `88820f28b8f770b486407e55dda28266c6fec42145192d5bc8ad5be21ab895af` |
| kagerou.exe | `f02998fae350945f4de4dc7eab47997e1e2d9b8aa43d49740a80aad893dcde9b` |

## 实现与检查

`runtime/effects.rpy` 保存已核实的掩码和帧序列，`runtime/shaders.rpy` 逐像素
选择旧／新画面。先在原虚拟画布合成一次，再平滑缩放到窗口，避免缩放比例改变
点阵本身。`runtime/03_rscript_gfx.rpy` 的效果 2 调用此公共实现。

`tests/test_shared_port.py /path/to/renpy-sdk` 在独立 Forest/Khime GL2 工程
核对 1/3/10/16/32 步的每个阶段、4×4 方向、最终画面，以及 700×525 /
1000×750 窗口与预先生成的点阵位图的一致性。modern 与 Kagerou 隔离测试
检查命令实际使用该实现、零步数和等待为零等边界。
这些检查不是原 EXE 逐帧运行对照；Android GPU、完整游玩和旧存档仍需用户验证。
