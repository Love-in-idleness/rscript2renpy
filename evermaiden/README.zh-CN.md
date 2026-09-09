# Evermaiden 中文迁移

本分支只读取 LiarsoftTool 2.0 生成的 `modern-36` 结构化 TSC，不处理 GSC。

```bash
python3 evermaiden/build_evermaiden_rscript.py \
  /path/to/unpacked/Evermaiden /path/to/renpy/Evermaiden
```

输入目录应包含 `scr`、所有 `grp*` 图像目录、`wav`、`bgm`、`voice` 与 `mov`。
生成的对话统一使用 `_say chinese`，并内置简体中文 Noto CJK 字体。
