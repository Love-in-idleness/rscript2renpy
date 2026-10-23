# Developer reference: Khime clicks and menus

[中文](KHIME_CLICK_ANALYSIS.zh.md) | [English](KHIME_CLICK_ANALYSIS.en.md) | [Русский](KHIME_CLICK_ANALYSIS.ru.md)

[Documentation](README.en.md)

Read-only analysis of user-supplied KhimeDL_CHS.exe, neither executed nor distributed.
SHA-256 `522bec3e93340ffd3bdb24ba98cfb775f80df9d85460819da840d824ad4822a8`.
PE32, ImageBase `0x400000`; VAs below, specific to this build.

## Native evidence

- Dispatch `0x420825/0x420850/0x420863/0x4208cc` calls setclk/setclksys/resetclk/setlink
  at `0x423910/0x423940/0x4239a0/0x4239c0`.
- setclk: `0x4222b0 → 0x406860`, writes +0x30 enable, +0x34 hover mode, +0x52 result,
  +0x36 ordinary/system class. setclksys: `0x4222e0 → 0x4068d0`, class 1.
- setlink: `0x422370 → 0x4069b0`, last operand chooses slots +0x38/+0x3a,
  positions +0x40/+0x44 and +0x48/+0x4c. Linked objects are this+0x58/this+0x5c, not body this+0x54.
- Hover `0x40a000` selects body effect from +0x34: 0 unchanged, 1 inverse (renderer 13),
  2 white (renderer 4, level 64), 3 hide body (renderer 23). `0x40a065–0x40a097` shows nonzero images in both slots;
  leave `0x40a0c0` restores body colour and hides them.
- Body callback binding: `0x405eb4/0x405ecb/0x405ee2` for click/enter/leave.
  `0x435c60` hits body rectangle +0x3c…+0x48 and pixel alpha, not setlink coordinates.
  load `0x409aa0` updates body position; `0x4098a0` gets body rectangle for slot 0;
  later setlink independently positions previews.
- cls `0x4067ce → 0x406a90` with force 1 resets click enable and both slot IDs (+0x30/+0x38/+0x3a).
  Queue mode clears metadata immediately, drawing can follow. resetclk 0 is skipped at `0x4239a4`, not a global reset.

## Adapter policy

Previously Khime treated slot 0 as the body replacement/hit origin and retained bindings after cls:
0501's hint layer 41 became an old CG-gallery button; 0401 tracks without setlink reused old images/coordinates;
0301 scene replay was affected too.
Khime now declares rscript_click_link_is_preview and rscript_click_native_effects. Shared runtime hits the body position/alpha,
applies native body modes and displays two independent previews; native-dialect cls clears bindings.
Forest/default keeps its existing replacement semantics; these EXE rules are not imposed on unrelated versions.
No player saves were modified or removed. Side-story entry recognizes title body 9006, not old hover replacement 9106.

Tests: tests/test_shared_port.py /path/to/renpy-sdk covers queued clears, reused hint layers, tracks without links,
separate hit/preview positions and both slots. Isolated graphics checks enter/leave, both previews, pixels and return values.
Actual three Khime menus and old saves still need manual checks. tests/test_khime_zero.py also covers the new-hover entry and title return.
