# 文档目录

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md) | [日本語](README.ja.md)

[返回主说明](../README.zh.md)

## 使用指南

- [环境配置与首次构建](SETUP.zh.md)
- [Forest](../forest/README.zh.md)
- [Khime 与可选外传](../khime/README.zh.md)
- [Evermaiden](../evermaiden/README.zh.md)
- [CannonBall](../cannonball/README.zh.md)
- [KagerouTouryuuki](../kagerou/README.zh.md)
- [SevenBridge（日文版）](../sevenbridge/README.zh.md)
- [第三方资源与授权](../THIRD_PARTY_NOTICES.zh.md)

## 开发参考

- [开发规划](ROADMAP.zh.md)
- [工作约定](../AGENTS.zh.md)
- [新游戏移植指南与 AI 提示词](NEW_GAME_PORTING.zh.md)
- [通用模板](../port_template/README.zh.md)
- [通用界面资源分工](../port_template/README.zh.md#界面资源分工)
- [源码分工](SHARED_TEMPLATE_MIGRATION.zh.md) · [本机路径](LOCAL_WORKFLOW.zh.md)
- [初始化配置](RSCRIPT_INITIALIZATION.zh.md)
- [文字布局](TEXT_WRAPPING.zh.md) · [Forest 字体](FOREST_FONT_ANALYSIS.zh.md)
- [Khime 点击](KHIME_CLICK_ANALYSIS.zh.md) · [图像效果](KHIME_EFFECT_ANALYSIS.zh.md) · [控制符](KHIME_TEXT_CONTROLS.zh.md)
- [效果 2](UPDATE_EFFECT2.zh.md)
- [原生色彩与绘制模式](NATIVE_VISUAL_MODES.zh.md)
- [Evermaiden 运行时](EVERMAIDEN_RUNTIME_GAPS.zh.md)
- [CannonBall 引擎行为](../cannonball/NATIVE_EFFECTS.zh.md)
- [Kagerou 原程序依据](../kagerou/NATIVE_EVIDENCE.zh.md)
- [SevenBridge 原程序依据](../sevenbridge/NATIVE_EVIDENCE.zh.md)
- [2026-10-12 公共层整理记录](OPTIMIZATION_REPORT_2026-10-12.zh.md)

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
