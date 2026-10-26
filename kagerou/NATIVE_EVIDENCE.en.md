# Kagerou: native-program evidence

[中文](NATIVE_EVIDENCE.zh.md) | [English](NATIVE_EVIDENCE.en.md) | [Русский](NATIVE_EVIDENCE.ru.md) | [日本語](NATIVE_EVIDENCE.ja.md)

[Documentation index](../docs/README.en.md)

This development reference records program identity, commands and layouts used by the bonus-edition adapter. Addresses and samples do not establish behavior for other engine versions.

This is static analysis, not a run of the original game. Addresses are VAs at image base `0x400000`, not file offsets. The reader is implemented independently in this directory; it does not import command semantics from other adapters.

## Input versions

| File | SHA-256 |
| --- | --- |
| Original `kagerou.exe` | `f02998fae350945f4de4dc7eab47997e1e2d9b8aa43d49740a80aad893dcde9b` |
| Chinese patch `kagerou_gbk.exe` | `0d024e5cfe6c70f5a9a9149df5fbf040dfb7d97cdeefba03a13625d121dea8de` |

Both are i386 PE32. The only changes in `.text` are `0x80 → 0x86` at `0x456d4a` and `0x45d0f3`: charset arguments in two font-creation paths. Other sections contain localization changes; the entire EXE is not a two-byte patch.

Only resources with 「ハチポチ特典」 installed are supported. A `modern-36` container may use different opcode schemas; read each TSC's metadata. Patches must match this edition; missing translations fall back to the original.

## Dispatch

Main interpreter: `0x41bd00`. At `0x41c12f`, non-VM instructions take the low 16 bits, subtract 3, then dispatch through the byte index at `0x41d4f8` and handler table at `0x41d2e8`. `native.py` reads these tables directly; repository opcode tables are not binary evidence.

| Opcode | Handler | Traced call |
| --- | --- | --- |
| `0x14` | `0x41c5e9` | Two expressions → `0x41f250` (`gload`) |
| `0x1a` | `0x41cad3` | `0x41ff10` (`queue`) |
| `0x1c` | `0x41cae7` | Three expressions → `0x41ff40` (`update`) |
| `0x51` | `0x41c9ae` | `0x41f020` (`TXT`) |
| `0x52` | `0x41ca0b` | `0x41eeb0` (`TXA`) |
| `0xff` | `0x41d29d` | Five expressions → `0x421f00 → 0x431320` |

`TXT` reads an expression, a raw DWORD, two expressions, two raw strings, and a final expression. It discards the first string, retains the second, and takes the final expression's low 16 bits. Subsequent layout, voice and wait semantics have not all been traced: this establishes reading/call paths, not a complete `TXT` implementation.

## EXCMD model

`0x431320` dispatches on the mode's low 16 bits; modes other than 0/1/2 return. The fifth argument is unused here. The model accepts five resolved unsigned WORDs, not expressions.

### Mode 0: load and optionally focus

`0x431370` accepts slots 1–7; others return. It selects X from configuration, calls `0x41dda0(slot,cg,0,x,0,0)`, calls `0x431440(slot)` if argument four is zero, then refreshes through `0x41dd30` if `0x482188` is zero. Focus also checks refresh: a nonqueued load with focus can refresh twice. Do not collapse this into immediate queued refresh or ignore argument four.

X selection at `0x431385–0x4313cc`:

```text
WORD[0x482a6a] != 0:
    signed WORD[0x47eede + 2 * slot]
otherwise:
    signed WORD[0x47eeba + 2 * (6 * (WORD[0x482a66] / 3) + slot)]
```

Nonnegative WORD division truncates. Extracted slot 1–6 positions:

| Explicit configuration | X |
| --- | --- |
| layout=0, alternate=false | 200, 200, 300, 400, 500, 600 |
| layout=6, alternate=false | 600, 600, 500, 400, 300, 200 |
| alternate=true | 400, 200, 300, 400, 500, 600 |

These are branches, not proven defaults. Slot 7 passes native validation but the focus loop covers only 1–6; do not normalize 7 to 6.

### Mode 1: clear

`0x431410` calls `0x41e020(slot,0)` and refreshes according to queue state. Its two conditional jumps exclude no WORD values; the next layer, `0x41dd70`, checks slot <100. Slot 0 passes through unchanged: EXCMD does not implement “clear all portraits.”

### Mode 2: focus and color

`0x431440` writes register 20 and visits layers 1–6:

| Layer | `0x41f940(layer,depth)` | `0x41f7f0(layer,mode,strength)` |
| --- | --- | --- |
| Selected slot | depth=8 | mode=0, strength=0 |
| Other, `WORD[0x482a6c]==0` | depth=layer | mode=4, strength=50 |
| Other, `WORD[0x482a6c]!=0` | depth=layer | mode=0, strength=0 |

The two `push esi` at `0x431478` establish layer-dependent depths, not depth 1. `0x41f940 → 0x41e360` sets depth. `0x41f7f0 → 0x41e2d0 → 0x4058b0 → 0x408e40` sets drawing parameters. Two tables at `0x408f40/0x408f24` route mode 4 to `0x408ea6`, internal mode **3**, with strength `50*255/100=127`. Image vtable `0x473f7c` entries `+0xb0/+0xb4` are `0x43fa30/0x43fb00`, writing mode `+0x28` and strength `+0x2c`.

Drawing `0x4406e0 → 0x4412c4/0x44125c → 0x440e65` uses `0x444380` for the transparent-outline branch and `0x444220` otherwise. Both transform RGB through table `0x4a732c` before writing/blending; this is neither image opacity reduction nor grayscale. Initialization `0x446079..0x4460ed` uses `0x475c38=256.0`, `0x475c50=1/256` and truncating conversion `0x4616b0`:

```text
L(level,channel) = trunc(channel*(256-level)/256)
output = L(a,L(level,source)) + L(255-a,destination)
```

Here `a` is the fourth byte's inverse alpha. Strength 127 gives **129/256**, not 50% or 128/255. Shared `dim256` implements only this RGB LUT; the adapter lowers `(4,50)` to `("dim256",127)`. Other games' numeric draw modes are unchanged. Ren'Py retains PNG coverage and GPU blending, so edge rounding is not byte-exact. Isolated GL2 checks cover zero/partial/full opacity and strengths 0/127/255 with a two-level color tolerance.

## Movies

Window path `0x4233c0`: message `0x40e` references `0x47ecf8`, `.\\mov\\0002.mpg`; `0x41e` references `0x47ece8`, `.\\mov\\0001.mpg`, then sets startup state. Available resources contain only 0002 and 0003. `movie 3` occurs in endings 1131/1239/1326/1417/1418.

The user permits the existing startup sequence: on application launch, play existing 0002 then 0001, warn about missing 0001, and retain script movie calls. Generated `game/script.rpy` uses `renpy.session` to prevent replay on title return or same-process `full_restart`.

## 0999 → 1000 calls

The baseline is now 162 bonus scenes, without a changed EXE hash. Added scenes include 0059/0201/0301/0302/1501..1511. Title 0001 uses `jump 201` for CG and `jump 301` for scene replay; 0302 calls a named `"scmode"` entry with `gosub`. Old Chinese command streams must not replace these scripts wholesale. TXT rebuilding preserves new commands and the trailing entry table. This is TSC call evidence, not manual verification of every gallery/unlock.

### Image choices need no setlink

`setclk` at `0x41cb59 → 0x41ffa0 → 0x41e800 → 0x405cb0` writes click enable/result/hover mode to object `+298`, without requiring `setlink` (an optional hover-description image). `0099%select` legally uses only `setclk` on 21–24. Enable loaded image regions; do not filter unlinked objects or skip the choice.

After `_gosub 999`, 0050 passes 1000 as the first `_insub` argument to a local entry, which executes `_gosub _r[10] 0 ...`; 0999 does not jump directly. The old shared runtime wrote r10–19 before resolving the target, replacing 1000 with zero and calling `_0000`. Resolve target and all arguments before register writes; do not edit scripts.

- Opcode 15 at `0x41d820` reads target plus ten parameters into temporary WORDs, calls `0x41da10`; `0x41da7a → 0x41d930` loads the target, then `0x41dabe..0x41dad3` writes parameters.
- Opcode 200 reads a local DWORD address at `0x41c427`, arguments at `0x41c43d..0x41c449`, then calls `0x41daf0`.
- Opcode 16, `0x41c481..0x41c487 → 0x41db80`, restores caller script/cursor; `0x41dbf9` writes r0. The final `return 0` in 0999 is valid.

## Text and origins

- `0x41f0e1` clears through `0x41ee80` when `WORD[0x482ae0]==1`. `tclsmode` at `0x4206d0` writes it; startup explicitly selects 2.
- `0x42d81a` prepends `^n` from `0x47ee88` when existing text and a nonzero wait are present. At `0x42d86c`, a body starting with CP932 `【` at `0x47ee94` gets an extra `U+3000,^n` from `0x47ee80`. TXT is not raw concatenation.
- Append `0x42d8d1 → 0x430db0`; on failure, `0x42d8da → 0x430f30` clears then appends the current paragraph. Ren'Py checks actual layout height, not native byte capacity; within-paragraph pagination remains unfinished.
- Direction `WORD[0x482a5e]`: native 0=vertical, 1=horizontal (earlier icon interpretation was reversed). SETE `0x430437`, WORD=0: `0x453ef0` sets `+0x1b0=1`; `0x455400 → 0x455800` advances Y and columns right-to-left. WORD=1 uses `0x455420`, advancing X and rows downward. Port settings retain 1=vertical/0=horizontal, remapping native tables/buttons. The port defaults to vertical text. New CFG initialization `0x419bb0` zeros BSS fields, so the EXE file does not prove a default direction byte of 1. Native CFG is not imported.

Presets `0x43027f..0x43042b`; `0x453eb0` writes physical dimensions to `+0x170/+0x16c`, not transposed virtual dimensions:

| Direction | Size index | Font | Physical area | Gap | Ruby |
| --- | --- | --- | --- | --- | --- |
| Vertical | 0 | 24 | 646×480 | 10 | 9 |
| Vertical | 1 | 18 | 494×360 | 8 | 8 |
| Vertical | 2 | 12 | 342×240 | 6 | 6 |
| Horizontal | 0 | 18 | 360×513 | 9 | 9 |
| Horizontal | 1 | 16 | 320×456 | 8 | 8 |
| Horizontal | 2 | 12 | 240×342 | 6 | 6 |

These are native constants, not proof of pixel equivalence. The port uses 24/18/12px in both directions; switching changes geometry/glyph direction only. Native areas, origins and gaps remain; large vertical text uses 646×480, not the horizontal 360×513.

- `0x43045c..0x430788` indexes interleaved X/Y stack constants by `snap+54*direction+18*size`, using native direction. All 54 combinations are in `native.py`: vertical 0/0=(114,30), horizontal 0/0=(400,20), vertical 2/8=(20,270). Ren'Py anchors vertical text at (x+width,y), wrapping by physical height. SDK TextSegment does not inherit direction: HarfBuzz vertical forms are needed to avoid sideways CJK. Isolated captures checked upright glyphs and switching.
- `tbox`, `0x41c8cb → 0x41f220`, calls `0x41e550/0x41e570` according to argument two and refreshes conditionally. Hide `0x42da47` also calls clear-page `0x42d9d0`. Since 0999 ends with `tbox 0 0` without `txcls`, hide must clear the page. `txcls` is `0x41ca48 → 0x41ecd0 → 0x41e590`.
- `locmode`, `0x41c801 → 0x41f890`, reads four expressions; layer 0 visits 1..99. `0x41e310 → 0x405740` writes origins. Nonzero fourth-field behavior is unresolved; samples use zero. `0x408569..0x4085d5` subtracts integer half-width/height for nonzero first/second fields, proving centered origins here. Half-pixel edges need visual comparison.
- `endscene` at `0x41cb25` checks replay WORD `0x4821f8`: normal play continues, nonzero exits the interpreter. The runtime defaults to normal play; replay calls explicitly set the replay flag.

The shared runtime supplies established registers/media/widgets, not copied game-specific overrides. General transitions use compatibility behavior; timing is detailed below, precise pixels remain unverified.

## Ruby syntax and position

These checks use the original EXE identified above, not another port. Replacement fonts need not match GDI rasterization.

- `4544d9..4544e6 → 45f150`: `|` saves the current body-cell index in ruby `+7c` and sets `+78`; it is not displayed.
- `4544ff..45459d` copies bytes between brackets, ends the base span at current body index−1, then calls `45f170`. Without `|`, `45f18b..45f197` also sets the start to that final cell. Thus `躯[み]` and `介[お]` are single-character ruby, not literal brackets. Current 1000.tsc uses both forms; `抉[えぐ]` and `熾[おこ]` in generated 1000.rpy:29 were the user's misrendered examples.
- `45ead0` selects horizontal `45eb20` or vertical `45ed60` and detects a new line/column when the next X/Y returns to the start. Across boundaries it allocates `ceil(remaining readings*current bases/remaining bases)`, recursively handling the rest at `45eb9d..45ebde` / `45eddd..45ee1e`.
- Horizontal `45ec75..45ed3f`: short readings use centered equal cells within the base span; long readings are centered as a whole and advance by actual width. Y=base-cell top−offset `+74`, not guessed ascender.
- Vertical `45eeb3..45efa8` applies the height equivalent, with reading right edge=first base right edge+offset `+74`, advancing downwards. Transposed Ren'Py layout uses the same cell-top-minus-offset; do not add another font height.
- `4303cb..43042b` sets ruby size `+68` and offset `+74` to 9/8/6. Shared metrics use these settings, not game-year heuristics.

Tests cover both syntaxes, cross-line/column allocation, offsets and SDK glyph direction. Captures use the 1000 opening without player saves. This Kagerou evidence does not establish other EXEs' ruby defaults; Forest/Khime geometry is retained.

## Wait animation and bonus galleries

- `0x430cb0..0x430d39` table [24,18,12,18,16,12], indexed by native `3*direction+size`, selects `grps/waitNN`, not body/grow triangles. Four LWGs each hold 60 frames in metadata order with per-frame origins.
- `0x4191a9` sets pointer `0x47e588`; WORD `+0x190` is 50. `0x4192b1 → 0x44fc90 → 0x44fca0` installs a 50ms timer; `0x44b980` advances and `0x44b9ab` wraps frames. This is not the body/grow glow.
- `0x430dfc → 0x430f60 → 0x455b30` obtains the last body glyph's cell. `0x430e01` places wait bottom-left in vertical layout, top-right horizontally—not at a fixed screen corner. Port geometry uses laid-out cells, excluding ruby.
- Vertical opening brackets `『「【` can have HarfBuzz ink beyond advance. The shared native text layer fits allowable bearing into its cell without changing fullwidth advance or gap. Actual SDK bounds at 24/18/12px are tested.
- `folder`, `0x41cee0 → 0x41fb80`, layer 0 loops 1..99 at `0x41fbb1..0x41fbc8`. Gallery `folder 0 "grpo_ex"` and `locmode 0 0 0 0` must both apply: thumbnails must not inherit centered portrait origins. Forest/Khime folder-all machinery is reused on this EXE's evidence; bonus TSC remains in charge, without a replacement gallery menu.

## Reading controls

### Bonus portrait-folder leak

Bonus 0001 sets every object's folder to grpo; galleries use grpo_ex/top-left. The 0050→0999→1000 path does not rerun 0000's grpo_bu/centered settings for slots 1..6. EXCMD consequently asks for nonexistent grpo/3011; shared missing-image fallback is transparent, hiding portraits throughout play. The assets were present, not omitted during copying.

The port restores the folders/origins explicitly declared in 0000/9999 when EXCMD loads slots 1..6, leaving general folder-all, gallery thumbnails and slot 7 alone. EXE `431370 → 41dda0 → 405940` uses current folders; no automatic old-EXE reset after the bonus title has been established. This is a port correction based on current scripts/resources, not a claimed native reset. Isolated Japanese/Chinese tests follow real title selection through 0050/0999 and check the first 1000 portrait, without player saves.

`0x42c2be..0x42c2d6` positions compane at (585,572); `0x42bfce..0x42bfe3` positions excompane at (0,550). Images, sizes and widget origins come from metadata; excompane has no background. Constructor string pointers establish names, not memory order.

| Name/field | Native path | Port |
| --- | --- | --- |
| skip / +60 | 42d5f0 → 42ce10 → 417f10 | Skip |
| rev / +68 | 42d630 → 42ce90 → 417ee0 | Rollback |
| bak / +74 | 42d5d0 → 42c890, native history | Wheel-equivalent Ren'Py rollback |
| hide / +78 | 42d6d0 → 42ced0 → 417e10 | Hide UI |
| voc / +7c | 42d6f0 → 42cc30 → 417e90 | Replay voice |
| auto / +84 | 42d710 → 42cda0 → 417fe0 | Auto |
| slide / +6c | 42d540 → 42d770 → 431070 | Textbox opacity |

Only available asset buttons are shown; no extra menu/save buttons. Back deliberately reuses shared rollback/permissions rather than native history or the old compatibility history page. The slider writes textbox background `+58` object's `+b4` alpha. Constructor `42fd4c → 431070` initializes 128; the shared opaque 255 hid backgrounds/portraits. Port default is 128/255; old default 1.0 is migrated once, preserving other choices and allowing 1.0 again later. Native pixel blending is not visually compared.

Save slot constructor `404135` reads saveconf. `404272/4042ac` keep date/new positions but release placeholder images; `40448b..404528` positions dynamic objects. `4048b5` formats `%04d/%02d/%02d %02d:%02d`. `404a0c` finds newest; `404a1c` loads dat_new there, not the black saveconf/new.png. The shared images map supplies it, saved chapter metadata selects previews, and metadata defines slots/pages. Native date font/color/blending is unverified. Isolated SDK tests trigger both Back and wheel rollback, restoring previous dialogue/local registers; this is a deliberate port difference, not EXE behavior.

excompane callbacks refresh through message 433:

| Control | Callback | WORD | Scope |
| --- | --- | --- | --- |
| size | 42e200 | 482a60 | Three size presets |
| shdw | 42e230 | 482a64 | 0 enables shadow; approximate rendering |
| dir | 42e260 | 482a5e | Direction |
| snap | 42e290 | 482a66 | Nine anchors |
| tfcs | 42e2c0 | 482a68 | 0 dims old paragraphs; 1 does not |
| lfcs | 42e2f0 | 482a6a | Portrait coordinate table |
| lctr | 42e320 | 482a6c | 0 dims nonfocused RGB; 1 normal |
| font | 42ded0 | Font dialog | Cross-platform list replaces Windows dialog |

With tfcs=0, `0x430f40 → 0x455b90` sets old paragraph images to mode 2/alpha128; port uses `{alpha=128/255}`. `0x4314c0` repositions portraits from the extracted tables, slots 1..6 only. `0x431510..0x431532` also reapplies drawing from configuration/current r20 focus without modifying registers/depth. `0x42e320 → 0x433 → 0x416b05 → 0x421bc0 → 0x421c40 → 0x421edd → 0x4314c0` updates colors immediately, including lctr_0/1 icons.

## Voice groups

- `0x40ce96` formats `pv%02d` at `0x47e254`; `0x40cf3f` constructs ten groups pv00..pv09, but assets provide only pv01..pv05 on/off. `0x429a60` constructs off=0 then on=1.
- `0x40e740 → 0x40e710 → 0x40e72b` writes `WORD[0x482238+2*group]`, without stopping current voice. `0x419c1f..0x419c73` initializes ten WORDs on with five `0x00010001` values.
- `0x41a630` checks global `0x48221c`, divides voice ID by10000, then `0x41a661` checks the group WORD and returns if off. The remainder is a four-digit filename: group0 `%s\\%04d.wav`, others `0x47e8ac: %s\\%d\\%04d.wav`.
- Refresh `0x40dcec..0x40dd34` reads ten WORDs. Inspected pv01_on/off selected/hover images are pixel-identical; shared selected frames are reused, not text buttons.
- Shared group support is enabled only where requested, leaving Forest/Khime unchanged. Mock SDK playback covers defaults, one-group mute, other groups continuing, no current-voice interruption and replay restrictions. Japanese/Chinese captures check five groups; actual listening and native CFG import were not tested.

## Remaining behavior

See the [game guide](README.en.md#checks-and-limitations).

## Music gallery

The existing EXE supports the bonus script's music entry; modification dates do not prove a missing new EXE. Title `setclksys 23 7 3 0` uses `0x409d82 → 0x417cb0 / 0x417d88[7] → 0x417d57 → 0x419ac0`. This reads window ID `0x482164` and calls `0x44eab0`. Registration `0x4196ab` pushes constructor `0x41a8a0`, `0x4196b6` calls registration, then `0x4196d2` stores returned AX in `0x482164`: the store belongs to the preceding call, not the next registration. Resource name: `0x47e8f0: muscmenu`.

| Native path | Behavior |
| --- | --- |
| `0x41a8a0` | Stop story BGM; select first track without playback; enumerate available images1..20, no unlock check |
| `0x41b410` | Stopped: different track selects, same track starts. Playing: selection restarts immediately, clears pause |
| `0x41b530 / 0x41b5d0 / 0x41b380` | Play / pause-resume / stop; play while playing does nothing |
| `0x41b660 / 0x41b680` | Previous blocked at first; next after last stops and selects first |
| `0x41b340` | Message `0x7e8`, parameter0 advances track; port checks independent channel completion |
| `0x41b6c0 / 0x4512b0` | Temporary `0x49ddec` volume only: 0..255 → truncated `(value-255)*3000/255` centi-dB, not global preference |
| `0x41b220` | Exit stops and restores global volume, without resuming previous BGM |

`0x41b5a5 → 0x451140` bypasses the story BGM switch; the port uses its own channel. Minimum slider is −30dB, not mute. muscmenu metadata supplies geometry and _f/_p states; current resources have 15 tracks and common language overlays. The shared template only provides game-registered system_actions; system7 is not generalized. `0x41ac16..0x41ac3a` takes level's bounds for a slider; `0x41ac89` releases the red placeholder. Draw only bar/bar_f, not level.

Automated tests cover selection, pause, switching, boundaries, decode start/end, temporary volume and cleanup. Isolated graphical tests use synthetic WAVs to check real Ren'Py completion advances and exit does not resume outer BGM. They do not verify real sound-card volume, full native UI or every replay route.

## update timing in milliseconds

`0x41cae7 → 0x41ff40 → 0x41e5b0` reads effect/steps/wait. `0x41e5cc..0x41e5d1` replaces zero steps with10. `0x41e7e0` dispatches immediate, dissolve, ordered replacement, white and black.

| Effect | Native loop | Nominal seconds |
| --- | --- | --- |
| 1 | `0x450630`; `0x4506c5` takes steps+1 | `(step+1)*wait/1000` |
| 2 | `0x4504e0`; `0x450540` takes steps−1, skips nonpositive; ordered, not mosaic | `max(0,step-1)*wait/1000` |
| 3 / 4 | `0x450f50 / 0x450cb0`, two phases of steps+1 | `2*(step+1)*wait/1000` |
| Mask | `0x450380`, double steps then subtract1 | `(2*step-1)*wait/1000` |
| 1xx / 2xx | `0x4507a0 / 0x450940`, two fixed31/41-frame loops, Sleep(5) each | 0.310 / 0.410 |

The loop uses WINMM!timeGetTime (IAT `0x4732dc`), sleeping at least once through KERNEL32!Sleep(5) (IAT `0x473070`) until actual difference is **greater than** wait. Shared codex-ms calculates nominal counts, not Windows scheduling. Current Japanese constant effects are0..3: `1 32 40`=1.32s, `1 16 20`=.34s, 0999 `1 15 100`=1.60s (old centisecond results12.8/3.2/15). Kagerou opts into ms mode; other ports received only the shared effect2 timing correction in this audit. Zero steps become10 before constructors too, avoiding division by zero. EXE-byte assertions/isolated SDK tests cover durations, register arguments and queues, not exact native pixels/scheduling.

## update 2: ordered replacement

`0x45050a` sets draw mode **18**, not scaling. `0x4412c4[18] → 0x44125c[13] → 0x440c17`; opaque `0x440c33 → 0x4437d0`. `0x443855..0x44385b` shifts strength right4, selecting one of16 WORDs at `0x47ef38`. `0x443899..0x4438ef` tests bit `(x%4)+4*(y%4)`:1 copies the new pixel,0 retains old. `0x45e01a..0x45e01c` negates DIB height, establishing top-down rows.

```text
FFDF EFDF 6FDF 6FD7 6BD7 6BD6 6B56 6A56
2A56 2A52 0A52 0A12 0812 0810 0800 0000
```

`0x44e4b0` draws the current window to the effect source; destination `+0x9c` retains the last frame. Strength descends from255 by `floor((step-frame)*255/step)`; after steps−1 frames, `0x44e450` commits the entire new image. Masks grow monotonically: neither Ren'Py's two-stage Pixellate nor the old8×8 SVG is equivalent.

The read-only native model checks Kagerou's table. Shared RScriptOrderedDissolve works in virtual-canvas pixels before whole-canvas scaling. Four other EXEs use the same table/copy logic; see [cross-game audit](../docs/UPDATE_EFFECT2.en.md). Isolated GL2 tests check1/3/10/16/32 steps,4×4 orientation each frame and full final image, not native runtime or Android GPU equivalence.

