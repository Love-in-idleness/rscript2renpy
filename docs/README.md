# 文档目录

[返回主说明](../README.md)

## 使用指南

- [环境配置与首次构建](SETUP.md)
- [Forest](../forest/README.md)
- [Khime 与可选外传](../khime/README.md)
- [Evermaiden](../evermaiden/README.md)
- [CannonBall](../cannonball/README.md)
- [KagerouTouryuuki](../kagerou/README.md)
- [第三方资源与授权](../THIRD_PARTY_NOTICES.md)

## 开发参考

- [新游戏移植指南与 AI 提示词](NEW_GAME_PORTING.md)
- [通用模板](../port_template/README.md)
- [通用界面资源分工](../port_template/README.md#界面资源分工)
- [源码分工](SHARED_TEMPLATE_MIGRATION.md) · [本机路径](LOCAL_WORKFLOW.md)
- [初始化配置](RSCRIPT_INITIALIZATION.md)
- [文字布局](TEXT_WRAPPING.md) · [Forest 字体](FOREST_FONT_ANALYSIS.md)
- [Khime 点击](KHIME_CLICK_ANALYSIS.md) · [图像效果](KHIME_EFFECT_ANALYSIS.md) · [控制符](KHIME_TEXT_CONTROLS.md)
- [效果 2](UPDATE_EFFECT2.md)
- [Evermaiden 运行时](EVERMAIDEN_RUNTIME_GAPS.md)
- [CannonBall 引擎行为](../cannonball/NATIVE_EFFECTS.md)
- [Kagerou 原程序依据](../kagerou/NATIVE_EVIDENCE.md)
- [2026-10-12 公共层整理记录](OPTIMIZATION_REPORT_2026-10-12.md)

原生参考中的地址和结论只适用于标明哈希的构建，不是所有游戏共用的规范。

## 开发检查

在仓库根目录执行，SDK 路径换成自己的：

```bash
python3 -B tests/test_runtime.py
python3 -B tests/test_port_template.py
python3 -B tests/test_file_install.py
python3 -B tests/test_native_images.py
python3 -B tests/test_tsc_compiler.py
python3 -B tests/test_tsc_patches.py
python3 -B tests/test_shared_port.py /path/to/renpy-sdk --logic-only
git diff --check
```

文字与触屏修改分别运行 `tests/run_native_text_wrap.py` 和
`tests/run_touch_controls.py`，参数为 SDK 目录。
各游戏另有专用测试，见相应 README。自动检查不替代实际游玩。
