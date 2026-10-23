# Developer reference: Khime image effects

[中文](KHIME_EFFECT_ANALYSIS.zh.md) | [English](KHIME_EFFECT_ANALYSIS.en.md) | [Русский](KHIME_EFFECT_ANALYSIS.ru.md)

[Documentation](README.en.md)

Confirmed object/mask/colour parameters from user-owned KhimeDL_CHS.exe, not distributed.
SHA-256 `522bec3e93340ffd3bdb24ba98cfb775f80df9d85460819da840d824ad4822a8`;
PE32, ImageBase `0x400000`, VAs specific to this file.
load `0x422d70 → 0x4218d0 → 0x4064f0` and font `0x422e20 → 0x421a00 → 0x4066f0`
both enter `0x4070b0`; cls `0x423080 → 0x421b30 → 0x406790` enters `0x407ec0`.
Text and image objects share effects: do not zero every nonzero _oload effect.

| Effect | load / cls | Meaning / shared implementation |
| --- | --- | --- |
| 3 | `0x407218 / 0x407f7a` | Renderer 2, alpha step 32; ordinary fade |
| 4 | `0x40724a / 0x407fae` | Renderer 0x12, step 32; ordered transition |
| 10 | `0x4073da / 0x4081ed` | Enter from / exit toward bottom; native-motion approximation |
| 15 | `0x40771d / 0x408485` | Renderer 4, step 16; white RGB fade preserving alpha |
| 19 | `0x4077f9 / 0x40854e` | Renderer 2, step 8; four times ordinary fade |

Renderer 4: `0x436c2e → 0x439d60`, blends RGB toward white.
Vtable +0x40/+0x44 calls target `0x407d60` (ret 4); operand 20 does not establish scaling.
_effect `0x4235a0` selects renderer by Mode: mode 1 `0x67 → 0x43b0f0` inverts target RGB under zero-red mask;
others `0x68 → 0x43b1f0` blend mid-grey brightness. Shared shader adds target inversion; mode 0 keeps brightness approximation.
Actual files include uppercase ES101.png: generated compatibility lookup ignores case but preserves actual paths, without copying/renaming.
Using existing effect-3 baseline 0.5s gives effect 19=2s and 15=1s.
Original frame intervals, acceleration and integer rounding remain approximate; static analysis/lint do not prove visual equivalence.
Unconfirmed effects remain flattened with comments. Effect-0 text keeps existing Forest fade-in.
Checks: python3 -B tests/test_shared_port.py /path/to/renpy-sdk for real shader compilation,
inverse/white pixels, queues and text effects in isolated projects. Manual cases: 1102 (19), 1110 (text 4),
7501 (clear 10), 7503 (load 15).
