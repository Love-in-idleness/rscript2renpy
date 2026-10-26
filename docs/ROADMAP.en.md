# Roadmap

[中文](ROADMAP.zh.md) | [English](ROADMAP.en.md) | [Русский](ROADMAP.ru.md) | [日本語](ROADMAP.ja.md)

[Main guide](../README.en.md)

## Ongoing improvements

Improve compatibility and runtime checks for supported games, prioritizing shared runtime fixes.
Each game guide defines its supported versions, features, and limitations.

Resource unpacking and conversion remain in the independent LiarsoftTool project.
This repository focuses on generating and running Ren'Py projects from TSC.

## Long-term goal: experimental `--pure-renpy`

A separate backend is planned to produce native Ren'Py statements, with standard Python, screen, and ATL
where needed, without a TSC parser or runtime instruction dispatcher.

This backend is not implemented; there is no `--pure-renpy` option.
Instruction coverage, save compatibility, and migration will be defined when development begins.

TSC editing tools are maintained by [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool/blob/master/docs/ROADMAP.md).
