# SevenBridge: native-program evidence

[中文](NATIVE_EVIDENCE.zh.md) | [English](NATIVE_EVIDENCE.en.md) | [Русский](NATIVE_EVIDENCE.ru.md) | [日本語](NATIVE_EVIDENCE.ja.md)

[User guide](README.en.md)

Target: Japanese `SBridge_jp.exe`, PE32/i386, image base `0x400000`, SHA-256:

```text
c7d5fc38cf0c354a61d056b607cf1367b2529557e9e0407d0b0fdf12771b35e3
```

These are file and Ghidra static-analysis results, not a recording of the original game. Originals were neither modified nor executed. All addresses are virtual.

## Resources and entry points

Export current-format TSC from the original `scr.xfl`, rather than relying on old exports. Containers are `modern-36`; each TSC's `rscript18`, `rscript19`, or `modern` metadata determines its argument schema.

0000 initializes then jumps to0001. Start follows0100→0110→2001. CG galleries use0201–0208/0210; scene replay uses0301/0302/0310 and5001–5013; music uses0400/0401. Scripts control these screens; unused EXE top_me* fallback titles are not the adapter's menu. Preserve the original title, opening common Text Settings only from its settings action. Another left click after a group's final CG returns to thumbnails. The viewer returns to the source page in r[299], without overwriting hit's register result.

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

The original `mov` contains `0002.mpg`, `0003.mpg`, and `0004.mpg`, with MPEG-1 video and MP2 audio. Startup callback `0x4238a0` references `mov/0002.mpg` and `mov/0001.mpg` at `0x4238eb/0x42390e`, calling `0x445240`. The port plays available files in order `(2, 1)`, skipping absent `0001`. Scripts `0110/0302` call movies 3/4 and `2004` calls 2; builds must retain `mov/*.mpg` and these commands.

## Repeatable checks

```bash
python3 -B tests/test_sevenbridge_builder.py
python3 -B tests/run_sevenbridge_port.py /path/to/generated-sevenbridge /path/to/renpy-sdk
```

Add --capture /path/to/captures to capture title, body, settings, save and load screens with isolated saves. Headless runs can use xvfb-run -a. Lint retains warnings for original fullwidth-number filenames and dynamically unreachable branches.

SDK checks are not comparisons with the running original. Font rasterization, every transition, full routes, native Windows and Android devices still need separate acceptance.

