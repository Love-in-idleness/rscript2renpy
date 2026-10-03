# Forest 汉化版默认字体分析

## 静态证据

分析对象：`/home/idleness/Games/Forest/Forest_CHS_unpacked.exe`，PE32 x86。
SHA-256：`94ab25e356d24d9a816ba7bcee6cb30fd6d0f664bbdbc24c000346b2f1b4bda9`。
本次只做静态分析，没有启动 EXE 或记录 Windows GDI 实际选中的字体。

- `0x46336c`：`BA DA CC E5 00`，CP936 解码为「黑体」。
- `0x46337c`：`82 6C 82 72 20 96 BE 92 A9 00`，CP932 解码为「ＭＳ 明朝」。
- 构造器 `0x43c48f` 将字体分支状态 `[esi+0x19c]` 初始化为 0。
  `0x438d3b` 检查此状态；默认分支在 `0x438da2` 传入「黑体」，
  另一分支在 `0x438d6f` 传入「ＭＳ 明朝」。因此默认请求的是黑体，
  不是宋体，也不是 Noto。
- 字形函数 `0x445e70` 在 `0x445ebc` 调用 `CreateFontA`：高度来自字号，
  宽度为 0，旋转角为 0，字重为 0 或 700，charset 为 134
  (`GB2312_CHARSET`)。本调用未额外设置英文压缩系数。
- `0x446019` 附近计算原引擎的缓存前进量：双字节字符在
  `0x446042–0x446047` 使用字号宽度；单字节字符在
  `0x446052–0x446055` 使用字号的一半。原引擎并非按任意比例字体
  的拉丁字符宽度排版。

地址来自 PE 的虚拟地址，用 `rabin2 -i` 和
`radare2 -e bin.relocs.apply=true` 定点检查字符串、调用与初始化分支。
`CreateFontA` 宽度 0 的含义见
[Microsoft API 文档](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createfonta)。

## 仓库默认字体

仓库的 `forest/fonts/simhei.ttf` 来自本机
`/usr/share/fonts/truetype/winfonts/simhei.ttf`，不是 EXE 内嵌字体。
其字体族为 SimHei，Regular，版本 5.04，哈希与许可状态见
[SimHei-NOTICE.md](../forest/fonts/SimHei-NOTICE.md)。

此文件每 em 为 256 单位，常用拉丁字母及 ASCII 空格前进量为 128，
汉字为 256；22px 下未 hinting 的理论前进量为 11px / 22px，
与原引擎半字格／全字格更接近。本机 Ren'Py 原生测试中，22px 的
`a`、`t` 经 FreeType hinting 后前进量为 12px，其余样例字母为 11px。
运行时仍通过 Ren'Py 的最终字形布局取得实际前进量，不增加猜测性的
英文压缩、East Asian Width 估算或负间距。

生成器复制字体及说明；SimHei 保留为菜单可选字体。2026-10-03 的
后续混合文本测试后，正文默认改回 Noto Sans CJK JP Regular，理由如下。
独立姓名牌图片保持不变。旧 SimHei 默认值迁移一次；其他已选字体保留，
迁移后用户仍可在菜单里选回 SimHei。

## 验证边界

自动测试检查资源复制、默认值迁移与 Ren'Py 原生字体度量；lint 检查脚本。
这些不能证明 Windows GDI 与 Ren'Py FreeType 的字形、hinting、基线和
间距完全一致。截图中的混合语言断点仍需人工对照；字体文件版本或
Windows 字体替代也可能造成差异。未经动态捕获，不声称原游戏一定
使用了与仓库逐字节相同的字体文件。

本机 Ren'Py 8.5.3、22px、19 字宽、7px 行距的原生布局测试中，
`之后，我俩跑到Royal Host餐厅，就桃色电影` 仍在「电」后折行，
「影」单独成为下一行；加上后续显式断行文本，共 4 行，高度 120px。
因此，此次默认字体匹配并不等于截图中所有断点差异已解决。
测试同时保留 Noto 的比例字体与 Wiki 标签度量回归用例。

## 混合文本修复：选用英文更窄的默认字体

本机 SDK 的 `font.py` 默认使用 FreeType `auto` hinting。
对 SimHei 实测 `auto-light`、`bytecode`、`none` 后，`Royal Host` 从
112px 缩为 110px，但「影」起点恰好位于 19 字宽边界，仍会换行。
未改变统一折行规则的 `<` 边界判断，也没有额外压缩英文、增加负字距、
扩大配置行宽或移除原文显式 `^n`。

按用户指定的备用方案，比较仓库已有字体，22px 的原生度量如下：

| 字体 | `Royal Host` 前进量 | 单个汉字 | 参考句总行数 |
| --- | ---: | ---: | ---: |
| SimHei Regular（auto） | 112px | 22px | 4 |
| Noto Sans CJK JP Regular | 106.703125px | 22px | 3 |
| Noto Sans CJK Light | 105.796875px | 22px | 3 |
| Noto Serif CJK Regular | 114.6875px | 22px | 4 |

选用 Regular 无衬线字体，保留更接近黑体的字重，避免为了宽度改用细体。
新默认下「影」起点约为 414.7px，小于常规行宽 418px，按已有规则允许
自然延伸。截图对应文本在原生布局测试中为：

```text
之后，我俩跑到Royal Host餐厅，就桃色电影
高谈阔论，一直聊到第二天黎明时分，才在
乌鸦的喧闹声中作别。
```

Wiki 开／关断点一致。原生布局测试不是实际窗口截图对比，其他文本、
自选字体、超大字号和 Android 的显示仍需人工检查。
