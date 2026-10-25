# Developer reference: Evermaiden runtime

[中文](EVERMAIDEN_RUNTIME_GAPS.zh.md) | [English](EVERMAIDEN_RUNTIME_GAPS.en.md) | [Русский](EVERMAIDEN_RUNTIME_GAPS.ru.md) | [日本語](EVERMAIDEN_RUNTIME_GAPS.ja.md)

[Documentation](README.en.md)

Modern instruction implementation, native evidence and remaining work. This record uses modern-36 input;
the EXE is read-only static evidence, not required by generated projects. Addresses are VAs in the user's
startup_jp.exe, not every version.

## Implementation and evidence

- Shared generation preserves dynamic effects/colours instead of zeroing register expressions.
  Unsupported constants retain local degradation comments; dynamic values are checked at execution.
- Queued effect/tone/tonedep snapshot register values at instruction execution, not later.
- _update uses shared rscript_update_duration; Evermaiden selects codex-ms, not Forest centiseconds.
  Step=0→10. Dissolve waits Step+1 times, ordered replacement Step−1, masks 2*Step−1,
  white/black Step+1 per phase, in milliseconds. Evidence: 43b390 → 453010 / 4531d0 / 453940 / 452e60.
  update 1 16 16 becomes nominal 0.272s, formerly 2.56s. No native drawing/Sleep/GetTickCount scheduling overhead;
  fixed load/cls duration and move-speed semantics remain approximate.
- locgrid writes the shared coordinate scale, not a local variable.
- group stores membership; clear/move support 0 (loaded objects 1–99) and >100 group selection (remainder modulo 100).
  group 0 remains a no-op. All/group clears preserve per-layer animations; white/black transform before hide,
  left/right exits use exit transitions.
- Move effects 5/6 follow opposite semicircles: 413e40 dispatch, 4141b3 / 41421b → 44d3c0 half-turn/vertical-radius math.
  Existing duration and trails remain, not exact frame scheduling.
- tboxloc/texloc/namloc define box/body/name rectangles. cmploc positions controls independently of the box's bottom-right.
- texsize/texcolor feed shared layout and the numeric palette from 43b6d0; player size remains relative scaling.
  texloc width and player line length jointly limit regular width, retaining hanging rules.
- waitloc/waitlod/waitcol set relative position, asset number and colour. Position is box origin plus offset,
  using waitNN metadata. Load body/grow before the persistent placement callback; otherwise ATL stalls on an empty image.
  Isolated GL2 dialogue covers language/number switching and glow over black.
- texruby font size/slot feed shared metrics within existing line spacing. 46ad7e → 46a1e8 confirms the operand is a slot,
  not alignment. Horizontal 46afa0 distributes short readings evenly/centred, centres long readings,
  recursively ceil-distributes across base lines. 46b125 subtracts offset from base-cell top;
  shared code converts SDK baseline/ascent and applies player size/display scale.
  Preserve shaped advance before SDK overwrites line-end advance; do not infer span from ink bounds.
  Do not increase spacing or move base text. Only modern metric ports use this; old ports retain unbreakable ruby/ink positioning.
  Unused native vertical ruby and exact substitute-font/GDI pixels are not reproduced.
- texmode: 42ced0 → 4576c0 sets alignment; 456c5a mode 1 centres, 456ce9 mode 2 right-aligns, otherwise left.
  Align within script body rectangle, without overriding ^m. Native vertical direction is separate field 1b0.
- texpich: 42d230 stores arguments at 17c/180; 457086 / 457062 use size+line spacing and glyph advance+character spacing.
  Measurement and display share the rule, scaling with player size; player spacing adjusts relative to native default.
  Ordinary Ren'Py text and older ports keep existing behaviour.
- texfont retains slot and adapter mapping. 433e22 adds player font at slot 2; every actual Evermaiden call uses 2.
  Slots 0/1 natively use Inconsolata gt (45f6e7 / 45f733, string 4cd480), not bundled;
  missing mapping uses player font and generated comment. Nonzero box style updates three auxiliary boxes,
  evidenced by 42a410 / 42a460 / 42aad0.
- cls 14 moves bottom-right then disappears, no longer instant clear: 43a9a0 → 410660 → 411b10
  jump-table entry 14 at 411f6a; endpoint uses canvas dimensions copied on object initialization.
  It now shares the quantized cosine path of load/cls 11–14: distance/15 is speed,
  then distance/speed determines steps. See [native visual modes](NATIVE_VISUAL_MODES.en.md).

Layout call chains: 43b600 / 43b690 / 43b270 (box/body/name), 43a850 (controls), 43b870 (size),
43b840 → 42d0d0 (ruby), 43b920 / 43b900 / 43b8d0 (wait image).

- update 100..299 implemented 2026-10-10, no longer degraded. 43b390 chooses 453a60 / 4537e0 by hundreds;
  tens/units select old/new nine-grid centres through 43ba20. 4542c0 / 451b60 crop using integer W*100/(100+level),
  clamping out-of-screen centres. Hundreds=1: level 0..600 step 20, two phases of 31×5ms=0.310s;
  hundreds=2: 0..2000 step 50, two 41×5ms=0.410s. Step/Wait are unused. Shared crops/timing pass actual isolated Ren'Py framebuffer tests;
  GDI sampling/blending is not pixel-compared and gameplay visuals still need inspection.
- mode: 43c3b0 → 412b00 rebuilds/clears objects; 0 covers all 1–99, even unloaded; >100 selects group.
  Mode is stored, background CG/folder/group/depth retained. Enabled for Evermaiden, not silently changed in old ports.
  Native mode 1/2 storage/GDI-backend differences are not reproduced.
- numenable: 43bd20 → 41c7c0 switches independent numeric layers, using shared state and queued snapshots.
  Actual Evermaiden uses only mode 0.
- Dynamic choices: 409750 shows all up to five answers; six or more use four per page plus next button.
  4090a1 advances and wraps to first page. Filter registers before pagination. dynnext supplies caption,
  default native 4c902c “次へ”; retain 43d559's 100-answer limit and dynsel clear/append.
  4080f0 operand 2 selects sel_qNN/sel_aNN skins via shared metadata. Exit/error clears temporary skins, not ordinary choices.
- Without selmap, 408974..408afe sums skin canvas heights with 5px before each answer;
  top=max(0,H*80//100-total)//2. Each answer is centred; title shifts left 30px from its own centre.
  Empty title still contributes object height. Missing skins retain plain menus; ordinary/Forest/Khime layouts do not change.
  Current Evermaiden has no selmapNN and follows this native fallback.
  43d739..43d762 / 43d81d..43d845 starts motion only for Effect=0 with effects enabled and no skip.
  Others stay put; 2/3 invokes update 1/2 15 0 with zero nominal wait, no invented duration.
  Actual 2 0 1 therefore stays stationary.
- dyndo Effect=0 without selmap uses shared motion: 0/1 expand from title, 2/3 vertical, 4/5 horizontal,
  retaining default branch 40943b..4096b9. Entry/title exit uses 44d4c0; unselected answers exit via 44d310;
  selected answer stays until others leave. Reproduce quantized cos/sin easing.
  408de0 distance/10 and 408c1f distance/5 are speed parameters; 44d310/44d4c0 derives step count from distance/speed.
  44d880 builds Q16 using i/256*6.283185308; 44d070 looks up each step, truncates coordinates and sets endpoint
  on the next tick after remaining steps reach zero.
  Config 4eb058+1b4 through 433b99 → 452680 sets timer: file default WORD 42ms here, shared constructor default 50ms,
  overridden to 42ms for Evermaiden. Port neither bundles/reads EXE nor native player CFG; Ren'Py schedules execution.
  Page changes do not repeat entry; effects-off/skip suppress motion; interaction is blocked during motion.
  Same metadata controls are reused, without extra checkpoints or overwriting menu rollback-forward data.
  Very short distances below speed divisor go directly to endpoint rather than native zero-speed stalling;
  not found in current normal skins, requiring comparison if such layouts appear.

## Unfinished

- makesave at 43e310 → 433140 copies 0x996c runtime bytes and 7000 local registers to memory, not disk;
  it is not renpy.save(). Saving the earlier snapshot rather than current execution position remains unimplemented.
  Other numeric commands and other instructions' group selection are not individually verified.
- Fixed native font-slot 0/1 glyphs and vertical ruby remain unreproduced.
- External selmap coordinates are not parsed: mode 0 should use their endpoints; only the missing-file fallback is implemented.
  selmap is not LWG image metadata.
- Unknown dynamic effects may still raise explicit runtime errors. Preserving expressions does not mean every effect works.

## Checks

Use tests/test_modern_port.py, passing SDK/resource paths as needed.
