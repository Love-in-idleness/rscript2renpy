# Roadmap

[中文](ROADMAP.zh.md) | [English](ROADMAP.en.md) | [Русский](ROADMAP.ru.md)

[Project overview](../README.en.md)

Current work prioritizes the Japanese SevenBridge port, shared runtime reuse and
Chinese, English and Russian documentation. LiarsoftTool remains a separate project
responsible for resource extraction and conversion.

An experimental `--pure-renpy` backend is a long-term goal, not an available option.
It would emit native Ren'Py statements, with standard Python, screens and ATL where
needed, but no TSC parser or runtime opcode dispatcher. This phase adds neither an
implementation nor a placeholder flag. Supported instructions, save compatibility
and migration remain future decisions.

The graphical TSC editor belongs to [LiarsoftTool's long-term roadmap](https://github.com/Love-in-idleness/LiarsoftTool/blob/master/docs/ROADMAP.md).
