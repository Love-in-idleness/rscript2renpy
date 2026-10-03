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

生成器复制字体及说明，将正文默认设为 SimHei；独立姓名牌图片保持不变，
设置界面字体保留 Noto。旧 Noto 默认值迁移一次；其他已选字体保留，
迁移后用户仍可在菜单里选回 Noto。

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
