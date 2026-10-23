# Developer reference: CannonBall engine behaviour

[中文](NATIVE_EFFECTS.zh.md) | [English](NATIVE_EFFECTS.en.md) | [Русский](NATIVE_EFFECTS.ru.md)

[Documentation](../docs/README.en.md)

Image effects, timing, VM and click evidence specific to this build. Cannonball.exe was used read-only,
not executed or required by generation. SHA-256:
`df4b5b6dffc7002370d0772869baaba551b08fca970e92609ca64b08174f89ba`.
Addresses are PE VAs, not transferable to other versions.

| Parameter | Static path and meaning | Port |
| --- | --- | --- |
| BGM fade | 4181b0/4181f0 → 42c6f0/42c790 → 43a510/43a570: nonzero switch; 43d122 sets 20ms timer, 43db4f/43dba6 ends at step 100, 2000ms | Lowering preserves switch/value comments; shared dual-channel crossfade enabled here |
| load/cls 9 | 40371a/4041b2 → 425690: start/end Y = negative image height | Shared top slide-in/out |
| load/cls 17 | 403aa1/4044a2 → 425d30: draw mode 20, step 16; 41df89 → 420320 draws only (y & 15) > (level >> 4) and ((x+y) & 15) > (level >> 4) | Shared grid-wipe shader preserving alpha/depth |
| draw 3, other non-1/2 | 405490: 1→mode 2, 2→mode 14, others→mode 0 | Old dialect normal-draw equivalence, not an unknown effect |

405490 → 41cc90/41cd60 changes the shown image immediately, without another load.
Shared display maintains dynamic blending through load, move, hide/restore and hover replacement, without resetting position/animation.
Draw follows queue order. SDK framebuffer checks normal, alpha, additive and pre/post queue states.
The percentage shader uses shared precision, not guaranteed exact integer native blending.
Before fixes, JP/ZH generated scripts contained 1979 explicit degradations: 1938 BGM, 19 image effects,
20 draw 3 and three incomplete text controls. Removing them does not mean all native behaviour is reproduced.

## Exact text corrections

Only complete matched CannonBall lines are corrected during generation; source game/patch resources stay unchanged.
JP scene 6101 voice 19604 uses ^n, confirming the Chinese bare ^g as a newline typo.
For 2402 voice 446/448, Chinese ^g63 is valid; Japanese has ^g63150/^g6340.
The common parser reads consecutive integers, so no zero-padding fix is applied to Chinese.
For the user-confirmed original bug, only the two Japanese lines become ^g063^cw150 / ^g063^cw40,
separating image ID from body digits with white control. Other numeric boundaries are not guessed.
These corrections and 6101's typo receive generated comments.
Chinese 2108 _oload 44 171 95 0 0 '１１３０' is changed to １１３０（正确） by request,
only in that Chinese scene, not original or other choices.

^g evidence: 426d1b/426d4e dispatches G/g to 426f18; 426f6c calls integer reader 42eaa0 and advances text cursor.
42eaa9..42eab8 skips spaces/tabs, 42eab8..42eac3 handles minus, 42eac3..42ead9 reads all ASCII digits
with value*10+digit, not a three-digit limit. 427520/42752a keeps low 16 bits;
42753b..427541 formats %s%03d using string 4500b0. 039, 0039 and 39 are equivalent.
^a uses the same reader but its Wiki semantics were outside this ^g fix. No EXE execution; evidence is limited to the hash above.

## Exit effects and counters

cls 31: 404900 → 4260e0/42fd00 splits left/right; right moves up, left down by 150px.
4255e0/425740 quarter-sine table drives motion, 425d30 fades simultaneously. 50ms ×16 =0.8s;
original/Chinese 5204 uses it.
cls 34: 404b22 → 4247a0/424db0 parameter 12 is step, not draw mode. Level starts 254, decreases 12;
42f740 rotates/scales by level*100//256 percent. 425aa0/425b10 adds 250px vertical sine motion over 20 steps;
22 frames=1.1s. Original 1602 has two calls.
Shared effects preserve position, anchor and depth, allow fragments outside image bounds, and clear on click-skip.
Ren'Py rotation sampling differs from integer copies; odd-width one-pixel split edges still need calibration.

Numeric controls: 4178b0 → 408a40 loads Num/Bar/Fix; 42d0b0 → 428160/4283a0 slices Num vertically
into ten frames, right-aligns eight digits and hides excess zeroes. 42d450 moves one-fifth of the remaining difference,
truncating toward zero, minimum one; visual timer 42b800/42b920 is 50ms.
408ce0/415c40 makes nonzero num Animate wait until done; zero completes instantly.
Missing skins do not invent text; skipping converges to target. Actual CannonBall only uses Bar:
Num was tested with synthetic ten-frame images, not claimed to exist in game assets.
numreng Mode/Digits are stored at 408d60 but not consumed in this display path; do not invent formatting meanings.

Manual entries: title 0002 load 9; Chinese 5703/7505 cls 17; 5204 cls 31; original 1602 cls 34/health bars;
6502 immediate draw. For BGM changes check simultaneous old fade-out/new fade-in and no restart for the same track.

## Tail mini-game voices

415097..4150b5 evaluates all four voice operands through 415c10, high 16 bits indirection depth,
low signed 16-bit register index. Scene 9020's 0x00011839..0x0001184a means @6201..@6218,
configured by 9040's character table. Old decompilation incorrectly chose rscript18, emitting literal 71737..71754.
LiarsoftTool layout scoring no longer penalizes legal references; re-export TSC.
Generators reject old >16-bit literals, not guess audio files. 418140 Repeat=999 loops;
common runtime preserves it and 9003 stops via voice_off after click.
Finite repeats >1 and voice Fade/Pan remain incomplete, outside this missing-voice fix.
Manual check: collecting the second through seventh matching tail cards triggers character voices; looping prompt stops on click.

## Validation limits

Compilation tests cover all real JP/ZH scripts and expressions. Isolated SDK checks audio API scheduling without music playback.
Shared GL2 tests cover grid/split/rotating exits, immediate blends and object/queue cleanup.
Neither tests nor lint prove original animation pacing, volume curves, complete routes or Android behaviour.
