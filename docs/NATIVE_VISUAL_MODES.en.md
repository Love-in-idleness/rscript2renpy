# Developer reference: native color and drawing modes

[中文](NATIVE_VISUAL_MODES.zh.md) | [English](NATIVE_VISUAL_MODES.en.md) | [Русский](NATIVE_VISUAL_MODES.ru.md) | [日本語](NATIVE_VISUAL_MODES.ja.md)

[Documentation](README.en.md)

## Samples and scope

Start from the newer Evermaiden engine, then compare all six ports and Khime Zero.
The original EXEs were inspected read-only, not launched. Addresses are sample-specific VAs.

| Sample | SHA-256 |
| --- | --- |
| Forest / Forest.exe | `8eb71d07304d362ec26cc47d93c6ef5854b5acadd7c9fe941755ad50820a3e56` |
| Khime / KhimeDL.exe | `2dfc7b78d32867716ab0406ccbf176b55a76faea1cb9c40feac25c90775222fe` |
| Khime Zero / Khime_zero.exe | `56e3b1316c2fd3bdc7826606fedf938a5b7509385e4ba4300010c7892a7af76c` |
| CannonBall / Cannonball.exe | `df4b5b6dffc7002370d0772869baaba551b08fca970e92609ca64b08174f89ba` |
| SevenBridge / SBridge_jp.exe | `c7d5fc38cf0c354a61d056b607cf1367b2529557e9e0407d0b0fdf12771b35e3` |
| Kagerou / kagerou.exe | `f02998fae350945f4de4dc7eab47997e1e2d9b8aa43d49740a80aad893dcde9b` |
| Evermaiden / startup_jp.exe | `88820f28b8f770b486407e55dda28266c6fec42145192d5bc8ad5be21ab895af` |

SevenBridge uses `SBridge_jp.exe`, not another similarly named launcher in that directory.

## Color modes

0 is unchanged, 1 black, 2 inverse, 3 arithmetic-mean grayscale; 14 is unchanged.
Modes 4–13 use these algorithms and RGB constants, not HSV filters.

| Mode | Algorithm | RGB |
| --- | --- | --- |
| 4 | Tint | `8b4513` |
| 5 | Tint | `483d8b` |
| 6 | Tint | `ff8000` |
| 7 | Night | `181020` |
| 8 | Level | `282040` |
| 9 | Level | `383080` |
| 10 | Level | `802d50` |
| 11 | Night | `904030` |
| 12 | Level | `805030` |
| 13 | Level | `a06040` |

```text
Grade(x,k) = floor(x*(k+1)/128)                  if k < 128
             floor(x+(256-x)*(2*k-255)/256)     otherwise
Tint(C,T) = Grade(T, floor((R+G+B)/3))
m = min(R,G,B)
Night(C,T) = floor(C*(256-m)/256) + floor(Grade(C,T)*(m+1)/256)
```

Color conversion preserves alpha. Mode 15 is HSL Power with byte quantization and a piecewise
hue warp, not a uniform saturation increase. Native RGB examples: red→(255,1,1),
green→(7,255,1), blue→(255,192,1).

Forest supports 1–6; CannonBall and Khime Zero support 1–5.
The extended Khime, SevenBridge, Kagerou and Evermaiden family distinguishes object classes:
Full supports through 13, Lim additionally supports 15, and 14 remains unchanged.
Evermaiden object mode 1 selects Full. Unlisted WORD values leave the image unchanged;
they are not unsupported effects to flatten. The shared layer retains color through
movement, rotation and animated clearing.

## Drawing and masks

Modern `draw 3` applies `Grade(destination, mask)` independently to each channel.
It ignores Level and is not ordinary alpha drawing. By user decision, early engines'
normal-drawing alias 3 now uses this modern meaning; other early aliases remain intact.
`draw 4/5` use black/white LUTs with strength `WORD(Level)*255//100`.
Kagerou's existing named `dim256` path still accepts an already-converted byte strength.
Non-1 `effect` modes reuse Grade instead of the GIMP Color-to-Alpha approximation;
mode 1 remains destination inversion.

Grade uses two GPU passes: scale the destination per channel, then add highlights.
Separate framebuffer rounding permits a two-level difference; this is not a claim of
byte-identical GDI edges. Coverage, depth and ordinary raster stitching are preserved;
text objects remain outside raster batches.

## Diagonal paths and striped wipes

`load/cls 11–14` use quantized cosine movement toward/from top-left, top-right,
bottom-left and bottom-right. Corners are `(-width,-height)`, `(canvasWidth,-height)`,
`(-width,canvasHeight)`, `(canvasWidth,canvasHeight)`; normal coordinates first subtract
the locmode image anchor.

The third argument of native `44d4c0` is speed, not a frame count:
`speed=(distance & 65535)//15`, then `steps=distance//speed`.
Movement reuses the dynamic choice menu's Q16 cosine lookup, holds the initial position
on the first tick and explicitly finishes at the endpoint. Grouped objects start together
and share the longest wait, rather than summing per-object delays.

`load/cls 18` is a vertical striped wipe: `x % 16 > level//16`.
The existing alpha path for 17 combines rows and diagonals; these are distinct effects.
For 17/18, level changes by 16 per port-specific `rscript_dynamic_tick`.
All `update 5–99` values select efNN masks; the previous range omitted 5–10.

Evidence: `412e40 / 411b10` (corners and renderer 21), `44d4c0 / 44d070` (movement),
`443900` (stripe loop), `45a710` (initial level), `43b390` (update range).
REA: `ev_d9a7d2b4a36144041f457d8269e9a0043f32474366870c125e98132d9e1f7210`,
`ev_5397d397711d9b7194b22de4675c82e3c8e7bb18695dc368a985c8acb4083876`,
`ev_500edda26e2d17c7ecb107b1553abf292437b9b826a64f6e039ac4fb1f1aa231`,
`ev_21e4dc7d33cac2c8ef9a1b30a02e32ae135bf467534de6539d7991b7eaac044b`.

## move 4: preserve each game's behavior

The actual movement call chains all use a sine-displaced wavy path, not an image-copy transition.
Forest's `401280` image-switch table was previously misidentified as movement; the movement
entry is `405f00`. The user's decision still applies: preserve each game's speed rules.

| Game | Movement entry → initializer | Native speed rule |
| --- | --- | --- |
| CannonBall | `404d80 → 4253c0` | Fixed 30 resource pixels per tick |
| Khime Zero | `405890 → 42e950` | `max(1, WORD(distance//15))` |
| Forest | `405f00 → 436e20` | Same; ignores script Speed |
| SevenBridge | `407090 → 43c310` | Same; ignores script Speed |
| Khime | `408f30 → 43da10` | `max(1, WORD(distance//(WORD(Speed) or 15)))` |
| Kagerou | `408530 → 4463b0` | Same |
| Evermaiden | `413e40 → 44d730` | Same |

The path uses `steps=WORD(distance//speed)` and perpendicular amplitude `(dy,-dx)*3/20`.
Its linear component is Q16 integer arithmetic; the sine phase increment is
`WORD(2*65535//steps)`, with division truncating toward zero. The initial frame holds
the start; after the native steps, position is set to the endpoint. Zero steps do not
activate movement and must not force a teleport. Compute in resource pixels before port
scaling; retain anchors, color, concurrent groups and the longest wait.
`_move/_movi/_gmove` share this implementation. 104/204 retain the existing afterimage
path; afterimages are not claimed to be frame-exact.

REA: `ev_e8d83ef9e7e6a073bc784176918a94c06b5e7715f298ce93921418e9d26f5764`,
`ev_14e88ba825c8a4919b11bd063c48134ac3331867e94a68b6831db5c864491c73`,
`ev_cc4f3dfd1759d85c74ad594f7fe11fcf30b2196cec83aaaaa5b5e59a161bb42f`,
`ev_387005b14b0fcd75ea8e3547485156aa791cdc29b0ea59735d34b482758e432b`,
`ev_ff72b51a8553cb687a0287fd749e36556fe9da490823b482309d1e885a8b0e61`.

## Evidence

- Evermaiden: `4154d0 / 415810` (Full / Lim), `44d880` (CMath),
  `461a70 / 461c90 / 461e50` (Level / Night / Power).
- Forest: `407fe0 / 408200`; Khime: `40b1a0 / 40b710`;
  Zero: `407910 / 407b00`; CannonBall: `4056d0`;
  SevenBridge: `409820`.
- REA: `ev_75cb85845a085eaa225b93c2ab638203ea2858f7a100edc6ed6a153582bb224a`,
  `ev_8fd952896a36ca15b3b46ccc02fbd32d104f0c3c516dfe76985a7b10aea65ac9`,
  `ev_f8cf3c06d5dfc8f6cb7d77e805c6e00d8fc35f59be596699c1fea2aca8f7a730`,
  `ev_905392cadc15179ebc74e6479ea8cad674b695c001ad6199612d5bb5dfea6b06`.
- Draw: `4129b0` → renderer `2 / 14 / 104 / 3 / 4`,
  `4464e0` case `104`;
  `ev_d72f2de30d9317ab80890eccc8c6d517851b60fbe84c35787f324ef2d2975b49`,
  `ev_2cb8389d102a8c15d2314404097b4b9c666238e5159e510d42ef00c7551d4863`.

## Checks and remaining work

An independent float32 Power reference matched the bounded native pixel routine on 5102
synthetic RGBA samples. Native code and private harnesses are not committed.
Shared GL2 checks cover colors, active/final movement, rotation, clearing, draw 3/4/5,
normal-mode restoration and blending across the CG layer, not complete gameplay.

Accepting a parameter does not establish a faithful implementation of every effect.
Complex exits 30/32/33/35, move 11–13 and other oaction
commands still need trajectory, object-class and timing verification.
Existing approximate animations are not frame-exact implementations either.
