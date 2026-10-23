# Developer reference: RScript initialization

[中文](RSCRIPT_INITIALIZATION.zh.md) | [English](RSCRIPT_INITIALIZATION.en.md) | [Русский](RSCRIPT_INITIALIZATION.ru.md)

[Documentation](README.en.md)

For new adapters inspect RsInit.tcf for dimensions, resource paths and startup clues.
Not every game has this file or RsInit.dll; otherwise verify its EXE and scripts.

## Inspector

```bash
python3 tools/inspect_rscript_init.py /path/to/game-resources
python3 tools/inspect_rscript_init.py /path/to/RsInit.tcf --encoding gbk
```

Read-only JSON output, no EXE/DLL execution. CP932 is default; --encoding overrides it.
Reports configuration values, resource directories, CFG presence and unknown items.

## Confirmed keys

From the analyzed Khime Zero initializer:

| Key | Role |
| --- | --- |
| title | Window title |
| width, height | Initial canvas dimensions |
| exec, script | Initial-script switch and number |
| scrdir | Scripts |
| sysimgdir, layerimgdir, faceimgdir, bgimgdir | Images |
| moviedir, wavedir, bgmdir, voicedir | Media |
| savepfx | Native save prefix |
| scrmod, extmod | Compiler/extension module names |
| bgm, bgmsource, layermod | Numeric fields, value semantics unconfirmed |

TCF need not be final: CFG or executable defaults may override it. One game's configuration is not all engine versions' specification.

## Binary evidence

Khime_zero/RsInit.dll, SHA-256 `b35bd24626a65d67ee932f2a62076070805c98b5f7a50f9920c19f2d8696b218`.
GetInitialData (`0x10001dd0`) reads TCF into caller structure; SaveInitialData (`0x10002170`)
writes this version's 324-byte structure to CFG. Main program `0x415330` tries CFG first, then TCF.
The Chinese sample's title uses GBK while comments retain CP932: do not assume one encoding for every byte.
These are build-specific static findings. The inspector does not require distributing the DLL.

## Checks

```bash
python3 -B tests/test_rscript_init.py
python3 -B tests/test_rscript_init.py /path/to/Khime_zero
```
