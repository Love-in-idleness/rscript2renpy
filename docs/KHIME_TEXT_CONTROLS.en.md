# Developer reference: Khime text controls

[中文](KHIME_TEXT_CONTROLS.zh.md) | [English](KHIME_TEXT_CONTROLS.en.md) | [Русский](KHIME_TEXT_CONTROLS.ru.md)

[Documentation](README.en.md)

Controls, choice-skin markers and remaining limits, specific to the user-owned KhimeDL_CHS.exe from the
[effect audit](KHIME_EFFECT_ANALYSIS.en.md). No EXE distribution. Addresses are VAs at ImageBase `0x400000`.
Parser `0x441180` checks ^ at `0x441263`, dispatches through byte table `0x4415fc` and pointer table `0x4415c8`.
Alternate parser `0x4416d0` uses `0x441a94/0x441a64`; both accept case-insensitive controls.

## Confirmed controls

| Control | Native branch | Behaviour |
| --- | --- | --- |
| `^fm` / `^fg` | `0x441371`; subtable `0x4416a4/0x441698` | Select font slot m/g until next font switch |
| `^cr` | `0x441318` | `#B73333` |
| `^cb` | `0x441342` | `#2020FF` |
| `^cs` | `0x441311` | `#79F1F2` |
| `^cp` | `0x441326` | `#F8B1EF` |
| `^cv` | `0x441334` | `#C187F6` |
| `^co` | `0x44133b` | `#FAA25A` |
| `^v[-0-9]+` | `0x4414e4` / `0x441988` | Convert consecutive ASCII digits/minus to full-width glyphs |

Colour subtables: `0x441660/0x441634`. Existing ^cy/^cw/^ck mean #FFDE00/#FFFFFF/#000000.
Khime ^cg at `0x44132d` means #7FDFA5, declared by game configuration, not Forest's Wiki-off white policy.
When the current language has a Wiki entry, the shared Wiki switch still controls green links.
^fm/^fg select font names `0x46e194/0x46d110` at `0x441b5b`; both GBK strings in this patched EXE are 黑体.
Both slots map to existing fonts/simhei.ttf: do not infer Mincho from m.
The common parser reads rscript_text_fonts; unspecified slots or missing mapped files fall back to GUI font.
No new font asset or extractor is added.

One implementation covers _say, _append, _oload and menu text. Compatibility checks preserve implemented controls;
unknown controls remain flattened with local comments. Font/colour/bold/italic tags close and reopen on changes,
avoiding crossed tags. Forest's nameplates, inline images and Wiki colours are unchanged.

## Choice skin marker <NN>

Not a ^ control or disposable prefix. Choice `0x410b70` checks < at `0x410bb6`; prompt `0x4133a0`
at `0x4133e8`. Both call `0x44b580` to split at first > then `0x44b5d0` to read decimal.
Default number 0, low 16 bits formatted with at least two decimal digits at `0x43e3c0`.
Bases `0x46d45c/0x46d464` are sel_a / sel_q: <01>正文 selects grps/sel_a01 or grps/sel_q01.
Body after > renders through `0x410df0/0x4136db → 0x441140`; the marker is hidden but chooses the skin.
The text child supplies body coordinates; choices use body and hover body_f.
If a numbered skin fails, `0x410ef1/0x41372a` uses unnumbered sel_a/sel_q, not an arbitrary other number.

Shared rscript_menu_panel() parses the decimal marker, selects assets and passes body to the existing text parser.
Originals, patches and generated RPY retain it; Khime lowerer no longer deletes <01>.
Forest's register/numeric image-only choices keep existing logic; text skin markers do not hide body text.
Missing skins fall back to plain text buttons; malformed markers are not guessed away.

## Recognized but not faithfully reproduced

- ^l/^L at `0x441299` resets font, colour, bold/italic, delay and layout. Full reset is not implemented;
  flattening remains documented in generated comments, not treated merely as a newline.
- ^c0…^c9 at `0x441349` reads configurable object colours. Unknown values are not invented; still flattened.
- ^sN at `0x4413f4` scales glyphs; `0x441b00`: 0/1/2/3 → 0.5/1/1.5/2, otherwise N−1.
  Existing incremental size handling is not equivalent; Forest was not silently changed.
- ^dN at `0x4413b9`: N=0 no delay, otherwise base delay + 2*(N−1). CPS scaling is approximate;
  native clock units need confirmation.
- ^m at `0x441468` sets layout 1; `0x44215e` centres by half remaining width. Shared centring exists,
  but original per-line layout is not every Ren'Py layout rule.
- ^g/^a images, ^b/^i styles and ^n breaks use common implementation. No ^w in this EXE's dispatch,
  which does not disprove waiting semantics in other dialects.

## Checks

tests/test_port_template.py checks case, preserved controls and unknown-control comments.
tests/run_native_text_wrap.py /path/to/renpy-sdk uses actual shaping for font switches, mixed tags,
full-width digits, wrapping and centring. tests/test_shared_port.py /path/to/renpy-sdk checks shared parsing,
Khime green/font slots and Forest Wiki without touching player saves.
Actual subtitle screens need manual confirmation, e.g. 1110's ^fm credits and ^cr dialogue.
