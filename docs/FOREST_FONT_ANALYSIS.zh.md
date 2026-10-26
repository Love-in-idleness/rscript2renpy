# 开发参考：Forest 字体

[中文](FOREST_FONT_ANALYSIS.zh.md) | [English](FOREST_FONT_ANALYSIS.en.md) | [Русский](FOREST_FONT_ANALYSIS.ru.md) | [日本語](FOREST_FONT_ANALYSIS.ja.md)

[文档目录](README.zh.md)

## 原程序依据

样本为 PE32 x86 `Forest_CHS_unpacked.exe`，SHA-256：
`94ab25e356d24d9a816ba7bcee6cb30fd6d0f664bbdbc24c000346b2f1b4bda9`。
以下为静态分析，地址是 VA，不代表 Windows 实际选用的字体文件。

- `0x46336c` 的 CP936 字符串为「黑体」，`0x46337c` 的 CP932 字符串为「ＭＳ 明朝」。
- 构造器 `0x43c48f` 将 `[esi+0x19c]` 置零；`0x438d3b` 检查后，默认分支 `0x438da2` 请求黑体，另一分支 `0x438d6f` 请求明朝。
- `0x445e70 → 0x445ebc` 调用 `CreateFontA`：字号决定高度，宽度和旋转角为 0，字重为 0 或 700，charset 为 134。不额外压缩英文。
- `0x446042–0x446047` 给双字节字符一个字号宽度，`0x446052–0x446055` 给单字节字符半个字号宽度。

`CreateFontA` 参数含义见 [Microsoft 文档](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createfonta)。

## 移植字体与度量

正文默认使用 Noto Sans CJK JP Regular；姓名牌仍使用原图。
SimHei 是菜单可选字体，其来源、哈希和许可见[字体声明](../port_template/fonts/SimHei-NOTICE.zh.md)。

SimHei 的 em 为 256，常用拉丁字符和空格前进量为 128，汉字为 256。
22px 下未 hinting 的理论前进量为 11px / 22px，但 FreeType hinting 会改变实际度量。
运行时采用 Ren'Py 最终字形度量，不用负字距或额外英文压缩补偿。

以下为 Ren'Py 8.5.3、22px、19 字宽、7px 行距下的混合文本参考值；
它们不是跨 SDK、字体版本和设备的保证值。

| 字体 | `Royal Host` 前进量 | 汉字宽度 | 参考段落行数 |
| --- | ---: | ---: | ---: |
| SimHei Regular（auto） | 112px | 22px | 4 |
| Noto Sans CJK JP Regular | 106.703125px | 22px | 3 |
| Noto Sans CJK Light | 105.796875px | 22px | 3 |
| Noto Serif CJK Regular | 114.6875px | 22px | 4 |

参考段落在 Noto Regular 下为：

```text
之后，我俩跑到Royal Host餐厅，就桃色电影
高谈阔论，一直聊到第二天黎明时分，才在
乌鸦的喧闹声中作别。
```

## 验证边界

字体文件、hinting 和字体替代会影响折行。布局测试不能证明 Windows GDI 与 FreeType
在字形、基线、间距及栅格上完全一致。更换字体、字号或 SDK 后应重新检查。
公共文字规则见[文字布局](TEXT_WRAPPING.zh.md)，测试入口见[开发检查](README.zh.md#开发检查)。
