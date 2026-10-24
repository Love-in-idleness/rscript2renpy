# SevenBridge: native-program evidence

[中文](NATIVE_EVIDENCE.zh.md) | [English](NATIVE_EVIDENCE.en.md) | [Русский](NATIVE_EVIDENCE.ru.md) | [日本語](NATIVE_EVIDENCE.ja.md)

[User guide](README.en.md)

Checked 2026-10-22. Target: Japanese `SBridge_jp.exe`, PE32/i386, image base `0x400000`, SHA-256:

```text
c7d5fc38cf0c354a61d056b607cf1367b2529557e9e0407d0b0fdf12771b35e3
```

These are file and Ghidra static-analysis results, not a recording of the original game. Originals were neither modified nor executed. All addresses are virtual.

## Resources and entry points

Original scr.xfl contains111 GSCs. The112 older TSCs already in the resource directory are not the build baseline: re-export copies with current LiarsoftTool. Containers are modern-36; each TSC's rscript18/rscript19/modern metadata determines its argument schema.

0000 initializes then jumps to0001. Start follows0100→0110→2001. CG galleries use0201–0208/0210; scene replay uses0301/0302/0310 and5001–5013; music uses0400/0401. Scripts control these screens; unused EXE top_me* fallback titles are not the adapter's menu. Preserve the original title, opening common Text Settings only from its settings action. The maintainer confirmed that another left click after a group's final CG returns to thumbnails. The viewer returns to the source page in r[299], without overwriting hit's register result.

APINI is at `0x469740`; `0x41a260` initializes resource paths and800×600 dimensions. `0x41ab90` tries external RsInit.cfg then RsInit.dll. Neither is supplied in the baseline, so internal EXE settings apply.

## Commands and state

| Implementation | Native evidence |
| --- | --- |
| Dispatch | `0x41cc40`, ordinary opcodes and high-bit VM operations separate |
| Three-argument locmode | case `0x26 → 0x420220`, object0 applies to all ordinary objects |
| folder0 | `0x4204e0`, folders for objects1–49 |
| Single-channel SE | cases `0x3e/0x3f/0x40`,1/3/1 expressions |
| getflag | case `0x72 → 0x421670`, ID and mode expressions |
| CG recording | `0x41fcc0`, always records independent progress bit; only IDs<1000 write r[9000+ID] |
| Ordinary-register snapshot | `0x41a260/0x41b070`,7000 16-bit registers |

getflag mode0 reads the bit into r[0] as Boolean; nonzero sets it, preserving r[0]. IDs are unsigned16-bit. `0x41b450/0x41b470` both use bank0, with `0x424110/0x424190` testing/setting bits. gload uses the same CG table. The port stores it in persistent.seen_cg, included in progress backups.

## Text and media

`0x414990` reads tboxNN layout/images. tbox00 is800×130, text origin(0,11), area682×119, wait(690,102); gfNNN name images are146 wide. Metadata preserves geometry; the adapter draws name/body separately.

`0x413f70` creates the body component; `0x415050(this,0x80)` sets background alpha. Settings use bright selected images and dark *_f images; the common menu follows this direction.

`0x41b0b0` saves r[1]/r[2]/r[3] in headers. `0x4037d0` selects dt1_/dt2_ by saved numbers, not current progress; strings are at `0x469160/0x469158`. Provided chapter strips use dt2_*, so r[2] is also saved. nonbl filenames1–9 are fullwidth,10 ASCII. Canvas/origins come from .meta.xml; do not try ASCII-only names or simply center cropped digits.

`0x41b5b0` groups voice IDs by10000: group0 voice/%04d.wav, others voice/<group>/%04d.wav. Converted OGG is used; PCM WAV remains unchanged. `0x4218d0` preserves repeat,999 loops.

Rechecked2026-10-23: original mov contains0002/0003/0004.mpg, all MPEG-1 video/MP2 audio. Earlier conversion copies omitted the folder. Startup callback `0x4238a0` references mov/0002.mpg and mov/0001.mpg at `0x4238eb/0x42390e`, calling `0x445240`. Common startup order is(2,1), skipping absent0001. Scripts0110/0302 call movies3/4,2004 calls2. Copy mov/*.mpg and preserve these commands.

Startup REA evidence:
`ev_0a8303ae0ac91d42cca1fa64a481fcf91c1ab0bfc78cbd8821b840268a01c474`,
`ev_177a58fd85e2021bd3409f818451f41c36da4a3b309aa5a2872d1d5d49969876`.
GNU objdump instructions:
`ev_32b12957eff616758728f349b1d051ff7ad77752533cd13b791d6b687a91bf83`.

## Evidence and repeatable checks

```bash
python3 -B tests/test_sevenbridge_builder.py
python3 -B tests/run_sevenbridge_port.py /path/to/generated-sevenbridge /path/to/renpy-sdk
```

Add --capture /path/to/captures to capture title, body, settings, save and load screens with isolated saves. Headless runs can use xvfb-run -a. Lint retains warnings for original fullwidth-number filenames and dynamically unreachable branches.

Key REA/Ghidra12.1.4 records:

- Dispatch: `ev_6e60215a5db021d73ca2e5b31caeab471f13ce6021c2770e151610381da40311`
- Progress query: `ev_2094337b09290b909f5863fb0a103aed4f01e10b48c67aad27faf23a5ddda192`
- CG recording: `ev_7f029987eebd0e711fd2b5d454465b8a1f31e3c4fd1c3891731d03d30491942c`
- Audio: `ev_0e12bcca631fa9ef551e87ad96278d2d2c9da8f193376ea1f5f5fb800dade10d`
- Text layout: `ev_8f8d19a742c865ecddd9c34cc6be37ef9fcd394cf9bf4a919cc1039a72f99d83`
- Initialization: `ev_2a124917ccf0f8ee508a62dc67e9d85f8e4934a81db6f81540d7f625beeee713`
- Save header: `ev_782a08b1a9610744432bee9a92493d79bdc1910c99d01bccca39da1cc75f7237`
- Save images: `ev_09e1bf507945becc87a6ff904be3610141ae649d35952d7fd0053fab971de964`

SDK checks are not comparisons with the running original. Font rasterization, every transition, full routes, native Windows and Android devices still need separate acceptance.

