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
It ignores Level and is not ordinary alpha drawing. All ports use this modern meaning for draw 3; other early aliases remain intact.
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
All `update 5–99` values select efNN masks; including 5–10.

Evidence: `412e40 / 411b10` (corners and renderer 21), `44d4c0 / 44d070` (movement),
`443900` (stripe loop), `45a710` (initial level), `43b390` (update range).

## move 4: preserve each game's behavior

The actual movement call chains all use a sine-displaced wavy path, not an image-copy transition.
Forest's movement entry is `405f00`; `401280` switches images. Preserve each game's speed rules.

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

## In-place bounce and complex exits

In all seven samples, `move 11/12/13` ignore X/Y/Speed and bounce vertically in place.
Amplitude/steps are 40/4, 100/10 and 300/15; phase increment is `0x8800//steps+2`.
The initial frame stays still, lookup starts on the next tick, and tick `steps+1`
restores the origin. Afterimage IDs use WORD then `%100`; retain each port's tick and scaling.

`cls 30–35` share the native dispatch: 30 cuts at 75% and moves one piece down-left;
31 moves two pieces up/down; 32 arcs the upper piece left; 35 moves upper/lower pieces
right/left. Fade is 14/256 per tick for 30/32 and 16/256 for 31/35.
33 bounces by 250 pixels and grows from 6% on its first tick; 34 combines the same bounce
with rotation and shrinking. Cuts, scaling and rotation affect Full only; the corresponding
Lim/Anim virtual slots are stubs, retaining movement and fading.
CannonBall calls affine objects directly, without the later Full/Lim switch;
its default mode 0 must not disable these effects.
33/34 wait 21/22 ticks; non-Full 34 waits only the 21-tick bounce.
Groups run concurrently with one longest wait and clean up layers afterward.

Evidence: `413e40 / 44d570 / 44d070` (bounce), `411b10` (exit dispatch),
`46be30` (cuts), `415e80` (affine stepping), `412b00` (object types).

## Object actions: phase / oaction

The shared compiler now lowers TSC `phase` to `_oaction` for every adapter, not only early dialects.
0 restores the image; 1/2 rotate counterclockwise around the center in steps of 10/20,
restoring at 256. 3/4 count down from 255 in steps of 10/20, rotating clockwise and restoring.
7/8/9 rotate counterclockwise around the bottom-left corner to 64; 10/11/12 rotate
clockwise around bottom-right to 192. Both groups use steps 8/12/30 and retain their
final pose until reset/clear; movement must not replay the action.

Actions 5/6 use the older type-18 bottom-center stretch in every port. Phase advances by
10/20 per tick; `u=trunc(sin(phase/256*2π)*50)` gives width/height percentages
`100+u / 100-u`. Sizes retain Q16 integer truncation; phase 128 restores the image.
Evermaiden's original Full vtable slot `+0x54` instead points to its tick function;
its special single-step behavior is deliberately not used, with no compatibility switch.
Unlisted WORD actions do nothing;
disabled effects or skipping restore the image. Rollback state retains position, color
and depth; clearing/rebuilding also removes action state.
Raster batches convert each layer's show time to elapsed animation time, both for lone
images and stitched groups; absolute clocks no longer make animations finish instantly.

Evidence: Evermaiden `4145c0 / 415e80 / 46c3b0 / 46cd80`;
stretch initializers Forest `4077c0`, Khime `40a980`, Zero `4070f0`, Kagerou `40a800`,
CannonBall `4247e0`; SevenBridge dispatch `407740`.

## Evidence

- Evermaiden: `4154d0 / 415810` (Full / Lim), `44d880` (CMath),
  `461a70 / 461c90 / 461e50` (Level / Night / Power).
- Forest: `407fe0 / 408200`; Khime: `40b1a0 / 40b710`;
  Zero: `407910 / 407b00`; CannonBall: `4056d0`;
  SevenBridge: `409820`.
- Draw: `4129b0` → renderer `2 / 14 / 104 / 3 / 4`,
  `4464e0` case `104`.

## Checks and remaining work

Shared GL2 checks cover colors, movement, rotation, clearing, draw 3/4/5, normal-mode restoration and cross-CG blending.

Accepting a parameter does not establish a faithful implementation of every effect.
GL2 tests cover initial, intermediate and final bounce/exit frames, Full/Lim differences,
action pivots, live stretching, lone/grouped raster clocks, final poses, movement-state retention and cleanup.
Cut edges, affine sampling and existing approximate animations are not claimed to be
pixel-identical to GDI.
