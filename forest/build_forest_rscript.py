#!/usr/bin/env python3
"""Lower LiarsoftTool's current Forest TSC to Jeanne-style rscript RPY."""

from pathlib import Path
import argparse
from functools import lru_cache
import re
import shutil
import subprocess
import sys

from PIL import Image

from forest_tsc import E, read_tsc


COMMANDS = {
    10: "hit", 11: "hitc", 12: "jump", 13: "wait",
    15: "gosub", 16: "return", 17: "backup", 20: "gload", 21: "gcls",
    22: "gmove", 23: "quake", 24: "flash", 26: "queue", 27: "action",
    28: "update", 29: "zupdate", 30: "load", 32: "oload", 33: "move", 34: "movi",
    35: "oaction", 36: "cls", 37: "enabl", 38: "locmode", 39: "draw", 40: "depth",
    41: "group", 42: "tbox", 43: "effect", 44: "effectdep", 45: "tone",
    46: "tonedep", 47: "locgrid", 49: "mode", 50: "backup", 52: "stop",
    55: "makesave", 56: "sysmode", 57: "logflash", 60: "bgm_on",
    61: "bgm_off", 64: "se_off", 65: "movie", 66: "voice",
    67: "voice_off", 68: "se_wait", 69: "voice_wait",
    70: "forest_setclk", 71: "forest_setclksys", 72: "forest_resetclk",
    73: "forest_click", 74: "forest_autoreset", 75: "forest_setlink",
    83: "txcls",
    90: "tboxloc", 91: "texloc",
    92: "tboxback", 93: "cmploc", 94: "tboxcmp", 95: "texcolor",
    96: "texsize", 97: "texfont", 98: "texmode", 99: "texindent", 100: "waitloc",
    103: "waitlod", 104: "waitcol", 120: "osize", 121: "folder", 132: "numenable",
}
OPERATORS = {2: "or", 3: "and", 4: "==", 5: ">=", 6: ">", 7: "<=",
             8: "<", 9: "!=", 10: "+", 11: "-", 12: "*", 13: "//", 14: "%"}
PATCH_INSERT_OPCODES = {13, 32, 36}


def packed(value: int) -> str:
    depth, raw = divmod(value, 0x10000)
    if not depth:
        return str(raw - 0x10000 if raw & 0x8000 else raw)
    result = str(raw)
    for _ in range(depth):
        result = "_r[%s]" % result
    return result


def vm_source(opcode: int, value: int, left: bool, temps: dict[int, str]) -> str:
    mode = (opcode >> (10 if left else 8)) & 3
    if mode == 0:
        return str(value)
    if mode == 1:
        return temps.get(value, "0")
    if mode == 2:
        result = str(value)
        for _ in range(((opcode >> (4 if left else 0)) & 15) + 1):
            result = "_r[%s]" % result
        return result
    return "0"


def emit_vm(opcode: int, operands: tuple[int, ...], temps: dict[int, str]) -> list[str]:
    family = opcode >> 12
    if family == 15:
        destination, source = operands
        temps[destination] = vm_source(opcode, source, False, temps)
        return []
    temporary, left, right = operands
    lhs = vm_source(opcode, left, True, temps)
    rhs = vm_source(opcode, right, False, temps)
    if family == 1:
        if ((opcode >> 10) & 3) == 2:
            temps[temporary] = rhs
            return ["$ %s = %s" % (lhs, rhs)]
        temps[temporary] = rhs
        return []
    temps[temporary] = "(%s %s %s)" % (lhs, OPERATORS.get(family, "+"), rhs)
    return []


def scene_label(scene: str, offset: int) -> str:
    return "_%s_L_%06x" % (scene, offset)


def menu_text(value: str) -> str:
    asset = re.fullmatch(r"<@(\d+)>", value)
    if asset:
        return "forest_asset_%s" % asset.group(1)
    return re.sub(r"<@(\d+)>", lambda match: "[_r[%s]]" % match.group(1), value)


def scenario_sources(folder: Path) -> list[Path]:
    """Return current command-based TSC scripts in a resource directory."""
    if not folder.is_dir():
        return []
    return sorted(source for source in folder.iterdir()
                  if source.is_file() and source.suffix.lower() == ".tsc")


def instruction_strings(tsc, item) -> dict[str, str]:
    """Return the translatable strings carried by one instruction."""
    result = {}
    opcode, operands = item.opcode, item.operands
    if opcode == 14:
        result["prompt"] = menu_text(tsc.string(operands[1]))
        for number, index in enumerate(operands[7:7 + min(operands[0], 5)]):
            if index < len(tsc.strings):
                result["choice%d" % number] = menu_text(tsc.string(index))
    elif opcode == 81:
        name, text = tsc.string(operands[4]), tsc.string(operands[5])
        if re.fullmatch(r"(?:\^c[yk])+", name):
            name = ""
        result["say"] = (name + "：" if name else "") + text
    elif opcode == 82:
        result["append"] = tsc.string(operands[4])
    elif opcode == 32:
        result["oload"] = tsc.string(operands[5])
    return result


def scene_strings(source: Path) -> dict[tuple[int, str], str]:
    """Return strings that a language patch may replace, keyed by command."""
    tsc = read_tsc(source)
    return {(item.offset, kind): value
            for item in tsc.instructions()
            for kind, value in instruction_strings(tsc, item).items()}


def align_insertable_segment(base, patch):
    """Match existing wait/font/cls commands and leave patch additions."""
    @lru_cache(maxsize=None)
    def align(base_index, patch_index):
        if base_index == len(base):
            return ()
        if patch_index == len(patch):
            return None
        if base[base_index].opcode == patch[patch_index].opcode:
            rest = align(base_index + 1, patch_index + 1)
            if rest is not None:
                return ((base_index, patch_index),) + rest
        return align(base_index, patch_index + 1)

    result = align(0, 0)
    if result is None:
        raise ValueError("language patch removes an existing display command")
    return result


def render_patch_command(tsc, item) -> str:
    if item.opcode == 13:
        return "_wait %s" % packed(item.operands[0])
    if item.opcode == 32:
        args = " ".join(packed(value) for value in item.operands[:5])
        return "_oload %s %r" % (args, tsc.string(item.operands[5]))
    if item.opcode == 36:
        args = " ".join(packed(value) for value in item.operands)
        return "_cls %s" % args
    raise ValueError("unsupported language-patch insertion")


def language_patch_data(base_scr: Path, patch_scr: Path):
    """Return translated strings and language-only subtitle commands."""
    replacements = {}
    insertions = {}
    for patch_source in scenario_sources(patch_scr):
        base_source = base_scr / patch_source.name
        if not base_source.is_file():
            raise FileNotFoundError(
                "%s has no matching base scenario" % patch_source)
        base_tsc, patch_tsc = read_tsc(base_source), read_tsc(patch_source)
        base_items = base_tsc.instructions()
        patch_items = patch_tsc.instructions()
        base_fixed = [(index, item) for index, item in enumerate(base_items)
                      if item.opcode not in PATCH_INSERT_OPCODES]
        patch_fixed = [(index, item) for index, item in enumerate(patch_items)
                       if item.opcode not in PATCH_INSERT_OPCODES]
        if [item.opcode for _, item in base_fixed] != \
                [item.opcode for _, item in patch_fixed]:
            raise ValueError(
                "%s changes scenario structure; language patches may only "
                "replace text and add subtitle display commands" % patch_source)

        pairs = []
        added = []
        base_previous = patch_previous = -1
        for fixed_index in range(len(base_fixed) + 1):
            base_next = (base_fixed[fixed_index][0]
                         if fixed_index < len(base_fixed) else len(base_items))
            patch_next = (patch_fixed[fixed_index][0]
                          if fixed_index < len(patch_fixed) else len(patch_items))
            base_segment = base_items[base_previous + 1:base_next]
            patch_segment = patch_items[patch_previous + 1:patch_next]
            try:
                matched = align_insertable_segment(base_segment, patch_segment)
            except ValueError as error:
                raise ValueError("%s: %s" % (patch_source, error)) from error
            matched_patch = {patch_index for _, patch_index in matched}
            for base_index, patch_index in matched:
                pairs.append((base_previous + 1 + base_index,
                              patch_previous + 1 + patch_index))
            for patch_index, item in enumerate(patch_segment):
                if patch_index in matched_patch:
                    continue
                next_match = next((base_index for base_index, matched_index in matched
                                   if matched_index > patch_index),
                                  len(base_segment))
                base_index = base_previous + 1 + next_match
                offset = (base_items[base_index].offset
                          if base_index < len(base_items) else base_tsc.code_size)
                added.append((patch_previous + 1 + patch_index, offset, item))
            if fixed_index < len(base_fixed):
                pairs.append((base_next, patch_next))
                base_previous, patch_previous = base_next, patch_next

        added.sort()
        added_fonts = {item.operands[0] for _, _, item in added
                       if item.opcode == 32}
        for _, _, item in added:
            if item.opcode == 36 and (item.operands[0] not in added_fonts or
                                      item.operands[1] != 0):
                raise ValueError(
                    "%s adds a clear command unrelated to an added subtitle" %
                    patch_source)
            if item.opcode == 13 and not added_fonts:
                raise ValueError(
                    "%s adds a wait command without an added subtitle" %
                    patch_source)

        scene_replacements = {}
        for base_index, patch_index in sorted(pairs):
            base = instruction_strings(base_tsc, base_items[base_index])
            patch = instruction_strings(patch_tsc, patch_items[patch_index])
            if base.keys() != patch.keys():
                raise ValueError("%s changes translatable command structure" %
                                 patch_source)
            for kind, old in base.items():
                new = patch[kind]
                if old == new:
                    continue
                scene_replacements[(base_items[base_index].offset, kind)] = new

        if scene_replacements:
            replacements[patch_source.name] = scene_replacements
        if added:
            scene_insertions = insertions.setdefault(patch_source.name, {})
            for _, offset, item in added:
                scene_insertions.setdefault(offset, []).append(
                    render_patch_command(patch_tsc, item))
    return replacements, insertions


def language_patch_strings(base_scr: Path, patch_scr: Path) -> dict[str, str]:
    replacements, _ = language_patch_data(base_scr, patch_scr)
    translations = {}
    for source_name, scene_replacements in replacements.items():
        base = scene_strings(base_scr / source_name)
        for key, new in scene_replacements.items():
            old = base[key]
            previous = translations.get(old)
            if previous is not None and previous != new:
                raise ValueError(
                    "%s translates the same source text inconsistently" %
                    (patch_scr / source_name))
            translations[old] = new
    return translations


def write_language_patch(base: Path, patch: Path, language: str,
                         game: Path) -> None:
    target = game / "tl" / language
    if target.is_dir():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    content = "translate %s python:\n    pass\n" % language
    (target / "forest_strings.rpy").write_text(content, encoding="utf-8")

    for folder in ("grpe", "grpo", "grpo_bg", "grpo_bu", "grpo_ci",
                   "grpo_f", "grps"):
        copy_assets(patch / folder, "*.png", target / "images" / folder)
        copy_assets(patch / folder, ".meta.xml", target / "images" / folder)
    for source_folder, target_folder in (("wav", "wav"), ("wav", "audio"),
                                         ("bgm", "bgm"), ("voice", "voice")):
        copy_assets(patch / source_folder, "*.ogg", target / target_folder)
    copy_assets(patch / "mov", "*.webm", target / "mov")
    if list((patch / "mov").glob("*.mpg")):
        convert_movies(patch / "mov", target / "mov")


def parse_language_options(specs: list[str]) -> tuple[str | None,
                                                       list[tuple[str, Path]]]:
    marker = None
    patches = []
    names = set()
    for spec in specs:
        if "=" not in spec:
            if marker is not None:
                raise ValueError("only one plain --language marker is allowed")
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", spec):
                raise ValueError("invalid language name: %s" % spec)
            marker = spec
            continue
        language, folder = spec.split("=", 1)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", language):
            raise ValueError("invalid language name: %s" % language)
        if language in names:
            raise ValueError("duplicate language patch: %s" % language)
        patch = Path(folder).resolve()
        if not patch.is_dir():
            raise FileNotFoundError("language patch directory not found: %s" % patch)
        names.add(language)
        patches.append((language, patch))
    return marker, patches


def patch_text_expression(language_texts, item, kind, default):
    replacements = {
        language: texts[(item.offset, kind)]
        for language, texts in (language_texts or {}).items()
        if (item.offset, kind) in texts
    }
    if not replacements:
        return repr(default), False
    return "%r.get(_preferences.language, %r)" % (replacements, default), True


def compile_scene(source: Path, language: str | None = None,
                  language_texts=None, language_insertions=None) -> str:
    if language and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", language):
        raise ValueError("invalid language name: %s" % language)
    for patch_language in set(language_texts or {}) | set(language_insertions or {}):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", patch_language):
            raise ValueError("invalid language name: %s" % patch_language)
    language_arg = " " + language if language else ""
    tsc = read_tsc(source)
    scene = source.stem
    instructions = tsc.instructions()
    targets = {item.operands[0] for item in instructions if item.opcode in (3, 4, 5)}
    for item in instructions:
        if item.opcode == 14:
            for number in range(min(item.operands[0], 5)):
                targets.add(item.operands[2 + number])
    lines = ["# Generated from %s; command offsets are preserved in labels." % source.name,
             "label _%s:" % scene]
    temps: dict[int, str] = {}
    pending_se: str | None = None
    for item in instructions:
        for patch_language, commands in (language_insertions or {}).items():
            added = commands.get(item.offset, ())
            if added:
                lines.append("    if _preferences.language == %r:" %
                             patch_language)
                lines.extend("        " + command for command in added)
        if item.offset in targets:
            lines.extend(("", "label %s:" % scene_label(scene, item.offset)))
        opcode, operands = item.opcode, item.operands
        if opcode & 0xf000:
            lines.extend("    " + line for line in emit_vm(opcode, operands, temps))
            continue
        if opcode == 9:
            temps[operands[0]] = "renpy.random.randrange(0x8000)"
        elif opcode in (3, 4):
            condition = temps.get(0, "0")
            test = "not (%s)" % condition if opcode == 3 else "(%s)" % condition
            lines.extend(("    if %s:" % test, "        jump %s" % scene_label(scene, operands[0])))
        elif opcode == 5:
            lines.append("    jump %s" % scene_label(scene, operands[0]))
        elif opcode == 8:
            lines.append("    return")
        elif opcode == 14:
            count = min(operands[0], 5)
            prompt = menu_text(tsc.string(operands[1]))
            prompt, _ = patch_text_expression(
                language_texts, item, "prompt", prompt)
            result = packed(operands[12])
            lines.append("    $ jump_back_point = renpy.game.log.current.identifier")
            lines.append(
                "    $ forest_choice_prompt = renpy.translation.translate_string(%s)" %
                prompt)
            choices = []
            for number, index in enumerate(operands[7:7 + count]):
                if index >= len(tsc.strings):
                    continue
                choice = menu_text(tsc.string(index))
                choice, changed = patch_text_expression(
                    language_texts, item, "choice%d" % number, choice)
                if changed:
                    variable = "forest_choice_%d" % number
                    lines.append("    $ %s = %s" % (variable, choice))
                    caption = "[%s]" % variable
                else:
                    caption = menu_text(tsc.string(index))
                choices.append((number, caption, item.operands[2 + number]))
            lines.append("    menu:")
            for number, caption, branch in choices:
                lines.extend(("        %r:" % caption,
                              "            $ _r[%s] = %d" % (result, number),
                              "            jump %s" % scene_label(scene, branch)))
        elif opcode == 18:
            destination = packed(operands[0])
            for index, value in enumerate(tsc.data(operands[1])):
                lines.append("    $ _r[(%s) + %d] = %d" % (destination, index, value))
        elif opcode == 81:
            name, text = tsc.string(operands[4]), tsc.string(operands[5])
            if re.fullmatch(r"(?:\^c[yk])+", name):
                name = ""
            value = (name + "：" if name else "") + text
            value, _ = patch_text_expression(language_texts, item, "say", value)
            if operands[1]:
                lines.append("    _voice %s 0 0 0" % packed(operands[1]))
            lines.append("    _say%s %s" % (language_arg, value))
        elif opcode == 82:
            text = tsc.string(operands[4])
            text, _ = patch_text_expression(language_texts, item, "append", text)
            lines.append("    _append%s %s" % (language_arg, text))
        elif opcode == 32:
            args = " ".join(packed(value) for value in operands[:5])
            text, _ = patch_text_expression(
                language_texts, item, "oload", tsc.string(operands[5]))
            lines.append("    _oload %s %s" % (args, text))
        elif opcode == 121 and operands[1] < len(tsc.strings):
            lines.append("    _forest_folder %s %r" % (packed(operands[0]), tsc.string(operands[1])))
        elif opcode == 15:
            lines.append("    _gosub %s" % packed(operands[0]))
        elif opcode == 16:
            lines.append("    return")
        elif opcode == 12:
            lines.append("    _jump %s" % packed(operands[0]))
        elif opcode == 62:
            pending_se = packed(operands[0])
        elif opcode == 63:
            if pending_se is not None:
                lines.append("    _se 0 %s" % pending_se)
                pending_se = None
            args = " ".join(packed(value) for value in operands)
            lines.append("    _se_on 0 %s" % args)
        elif opcode == 64:
            lines.append("    _se_off 0 %s" % packed(operands[0]))
        elif opcode in (30, 36):
            values = list(operands)
            # Forest's 2500.tsc contains one mistyped background number. The
            # surrounding loads use 4416 and grpo_bg/4416.png is the asset that
            # exists; 44120 has no corresponding resource.
            if scene == "2500" and item.offset == 0x22366 and values[1] == 44120:
                values[1] = 4416
            effect_index = 4 if opcode == 30 else 1
            if values[effect_index] in (1, 4, 28):
                values[effect_index] = 0
            args = " ".join(packed(value) if kind == E else str(value)
                            for kind, value in zip(item.kinds, values))
            lines.append("    _%s %s" % (COMMANDS[opcode], args))
        elif opcode in COMMANDS:
            args = " ".join(packed(value) if kind == E else str(value)
                            for kind, value in zip(item.kinds, operands))
            lines.append("    _%s%s" % (COMMANDS[opcode], " " + args if args else ""))
        else:
            lines.append("    # unlifted opcode 0x%04x %s" % (opcode, operands))
    for patch_language, commands in (language_insertions or {}).items():
        added = commands.get(tsc.code_size, ())
        if added:
            lines.append("    if _preferences.language == %r:" % patch_language)
            lines.extend("        " + command for command in added)
    emitted = {item.offset for item in instructions}
    for target in sorted(targets - emitted):
        lines.extend(("", "label %s:" % scene_label(scene, target), "    return"))
    lines.append("    return")
    return "\n".join(lines) + "\n"


RSCRIPT_OBJECTS = r'''


    def parse_oload(lex):
        args = RScriptArguments()
        for name in ("Layer", "xLoc", "yLoc", "Effect", "Colormode", "Text"):
            args[name] = lex.simple_expression()
        lex.expect_eol()
        return args

    def execute_oload(args):
        if args.Effect != 0:
            raise Exception("Unhandled object load effect %d" % args.Effect)

        layer = args.Layer
        xpos = args.xLoc * store.layer_x_grid
        ypos = args.yLoc * store.layer_y_grid
        anchor = store.layer_anchor.get(layer, (0.0, 0.0))
        tag = "layer%d" % layer
        text_value, _ = parse_rscript_text(repr(args.Text), True)
        font_size = store.object_size.get(layer, gui.text_size)
        font_size = max(1, font_size * persistent.forest_text_size // 22)
        text = Text(text_value, font = forest_current_font(),
                    size = font_size, color = "#C8AF00",
                    xmaximum = font_size * persistent.forest_line_chars)
        trans = Transform(
            xpos = xpos,
            ypos = ypos,
            anchor = anchor,
            shader = "rscript.colormode",
            u_colormode = args.Colormode,
        )

        store.layer_info[layer] = text
        store.layer_pos[layer] = (xpos, ypos)
        queue_draw(renpy.show, tag, what = text, at_list = [trans],
                   zorder = store.layer_zorder.get(layer, layer * 2),
                   layer = IMAGE_LAYER)
        process_draw_queue()

    renpy.register_statement("_oload", parse = parse_oload, execute = execute_oload, lint = lint_undef)



    def parse_osize(lex):
        args = rscript_arguments(lex, ["Layer", "Size"])
        lex.expect_eol()
        return args

    def execute_osize(args):
        store.object_size[args.Layer] = args.Size

    renpy.register_statement("_osize", parse = parse_osize, execute = execute_osize, lint = lint_undef)



    def parse_oaction(lex):
        args = rscript_arguments(lex, ["Layer", "Action"])
        lex.expect_eol()
        return args

    def execute_oaction(args):
        if args.Action == 4:
            move_layer(args.Layer, 0, 0, 9, 4, relative = True)
        else:
            raise Exception("Unhandled object action %d" % args.Action)

    renpy.register_statement("_oaction", parse = parse_oaction, execute = execute_oaction, lint = lint_undef)
'''


FOREST_COMPAT = r'''style default:
    font "fonts/NotoSansCJKjp-Regular.otf"

style forest_volume_bar is bar:
    left_bar Solid("#00000000")
    right_bar Solid("#00000000")
    hover_left_bar Solid("#00000000")
    hover_right_bar Solid("#00000000")

default forest_click_links = {}
default forest_click_values = {}
default forest_click_system = {}
default forest_choice_prompt = ""
default forest_speaker = None
default forest_speaker_visible = False
default forest_last_voice = None
default persistent.textbox_opacity = 1.0
default persistent.forest_text_size = 22
default persistent.forest_line_chars = 19
default persistent.forest_text_font = "fonts/NotoSansCJKjp-Regular.otf"
default persistent.forest_progress_backup = None
define forest_languages = [(None, "原文")]

init python:
    def forest_open_game_menu():
        if store.menu_enabled:
            renpy.run(ShowMenu("preferences"))

    def forest_save_json(data):
        data["forest_dt1"] = int(_r[1])

    def forest_replay_voice():
        if forest_last_voice and renpy.loadable(forest_last_voice):
            renpy.music.play(forest_last_voice, channel="rscript_voice",
                             loop=False, if_changed=False)

    def forest_adjust_text(name, delta, low, high):
        value = max(low, min(high, getattr(persistent, name) + delta))
        setattr(persistent, name, value)
        renpy.save_persistent()

    def forest_fonts():
        return sorted(name for name in renpy.list_files()
                      if name.startswith("fonts/") and
                      name.lower().endswith((".ttf", ".otf", ".ttc")))

    def forest_current_font():
        fonts = forest_fonts()
        if persistent.forest_text_font in fonts:
            return persistent.forest_text_font
        return fonts[0] if fonts else gui.text_font

    def forest_font_name():
        return forest_current_font().rsplit("/", 1)[-1]

    def forest_cycle_font(step):
        fonts = forest_fonts()
        if not fonts:
            return
        try:
            index = fonts.index(persistent.forest_text_font)
        except ValueError:
            index = -1 if step > 0 else 0
        persistent.forest_text_font = fonts[(index + step) % len(fonts)]
        renpy.save_persistent()

    def forest_save_progress():
        persistent.forest_progress_backup = {
            "reg": dict(persistent._reg),
            "seen_cg": dict(persistent.seen_cg),
        }
        renpy.save_persistent()
        renpy.notify("持久化数据已保存")

    def forest_load_progress():
        data = persistent.forest_progress_backup
        if data is None:
            renpy.notify("没有可读取的持久化数据备份")
            return
        persistent._reg = dict(data["reg"])
        persistent.seen_cg = dict(data["seen_cg"])
        renpy.save_persistent()
        renpy.notify("持久化数据已读取")

    def forest_clear_progress():
        persistent._reg = {}
        persistent.seen_cg = {}
        renpy.save_persistent()
        renpy.notify("持久化游戏进度已清除（备份已保留）")

    config.game_menu_action = Function(forest_open_game_menu)
    config.save_json_callbacks.append(forest_save_json)
    config.say_menu_text_filter = renpy.translation.translate_string

    if "K_AC_BACK" in config.keymap["rollback"]:
        config.keymap["rollback"].remove("K_AC_BACK")
    if "K_AC_BACK" not in config.keymap["game_menu"]:
        config.keymap["game_menu"].append("K_AC_BACK")
    config.overlay_screens.append("forest_touch_controls")

screen forest_touch_controls():
    zorder 200
    if renpy.variant("touch") and not (
            renpy.get_screen("preferences") or
            renpy.get_screen("save") or
            renpy.get_screen("load")):
        hbox:
            style_prefix "forest_touch"
            spacing 2
            xalign 0.995
            yalign 0.01

            textbutton "戻る" action Rollback()
            textbutton "スキップ" action Skip()
            textbutton "オート" action Preference("auto-forward", "toggle")
            textbutton "メニュー" action ShowMenu("preferences")

style forest_touch_button:
    xminimum 90
    yminimum 44
    padding (8, 4)
    background Solid("#000000a0")
    hover_background Solid("#586b44d0")
    insensitive_background Solid("#00000060")

style forest_touch_button_text:
    font "fonts/NotoSansCJKjp-Regular.otf"
    size 17
    color "#ffffff"
    insensitive_color "#888888"
    text_align 0.5
    xalign 0.5
    yalign 0.5

screen preferences(title_mode=False):
    tag menu
    modal True
    key "game_menu" action Return()

    fixed:
        xysize (518, 420)
        xalign 0.5
        yalign 0.5
        add "images/grps/confscrn/bg.png" xpos 4 ypos 2

        imagebutton:
            idle "images/grps/confscrn/scm_ful_f.png"
            hover "images/grps/confscrn/scm_ful_f.png"
            selected_idle "images/grps/confscrn/scm_ful.png"
            selected_hover "images/grps/confscrn/scm_ful.png"
            action Preference("display", "fullscreen")
            xpos 202 ypos 23
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/scm_wnd_f.png"
            hover "images/grps/confscrn/scm_wnd_f.png"
            selected_idle "images/grps/confscrn/scm_wnd.png"
            selected_hover "images/grps/confscrn/scm_wnd.png"
            action Preference("display", "window")
            xpos 356 ypos 23
            activate_sound "wav/0001.ogg"

        imagebutton:
            idle "images/grps/confscrn/bgm_on_f.png"
            hover "images/grps/confscrn/bgm_on_f.png"
            selected_idle "images/grps/confscrn/bgm_on.png"
            selected_hover "images/grps/confscrn/bgm_on.png"
            action Preference("music mute", "disable")
            xpos 202 ypos 55
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/bgm_off_f.png"
            hover "images/grps/confscrn/bgm_off_f.png"
            selected_idle "images/grps/confscrn/bgm_off.png"
            selected_hover "images/grps/confscrn/bgm_off.png"
            action [Preference("music mute", "enable"), Stop("music")]
            xpos 356 ypos 55
            activate_sound "wav/0001.ogg"
        bar:
            style "forest_volume_bar"
            thumb "images/grps/confscrn/bgm_vol.png"
            hover_thumb "images/grps/confscrn/bgm_vol_f.png"
            value Preference("music volume")
            xpos 234 ypos 87
            xsize 230 ysize 21

        imagebutton:
            idle "images/grps/confscrn/voc_on_f.png"
            hover "images/grps/confscrn/voc_on_f.png"
            selected_idle "images/grps/confscrn/voc_on.png"
            selected_hover "images/grps/confscrn/voc_on.png"
            action Preference("voice mute", "disable")
            xpos 202 ypos 119
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/voc_off_f.png"
            hover "images/grps/confscrn/voc_off_f.png"
            selected_idle "images/grps/confscrn/voc_off.png"
            selected_hover "images/grps/confscrn/voc_off.png"
            action [Preference("voice mute", "enable"), Stop("rscript_voice")]
            xpos 356 ypos 119
            activate_sound "wav/0001.ogg"
        bar:
            style "forest_volume_bar"
            thumb "images/grps/confscrn/voc_vol.png"
            hover_thumb "images/grps/confscrn/voc_vol_f.png"
            value Preference("voice volume")
            xpos 234 ypos 151
            xsize 230 ysize 21

        imagebutton:
            idle "images/grps/confscrn/sef_on_f.png"
            hover "images/grps/confscrn/sef_on_f.png"
            selected_idle "images/grps/confscrn/sef_on.png"
            selected_hover "images/grps/confscrn/sef_on.png"
            action Preference("sound mute", "disable")
            xpos 202 ypos 183
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/sef_off_f.png"
            hover "images/grps/confscrn/sef_off_f.png"
            selected_idle "images/grps/confscrn/sef_off.png"
            selected_hover "images/grps/confscrn/sef_off.png"
            action [Preference("sound mute", "enable"), Stop("se0")]
            xpos 356 ypos 183
            activate_sound "wav/0001.ogg"
        bar:
            style "forest_volume_bar"
            thumb "images/grps/confscrn/sef_vol.png"
            hover_thumb "images/grps/confscrn/sef_vol_f.png"
            value Preference("sound volume")
            xpos 234 ypos 215
            xsize 230 ysize 21

        imagebutton:
            idle "images/grps/confscrn/gef_on_f.png"
            hover "images/grps/confscrn/gef_on_f.png"
            selected_idle "images/grps/confscrn/gef_on.png"
            selected_hover "images/grps/confscrn/gef_on.png"
            action Preference("transitions", "all")
            xpos 202 ypos 247
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/gef_off_f.png"
            hover "images/grps/confscrn/gef_off_f.png"
            selected_idle "images/grps/confscrn/gef_off.png"
            selected_hover "images/grps/confscrn/gef_off.png"
            action Preference("transitions", "none")
            xpos 356 ypos 247
            activate_sound "wav/0001.ogg"

        imagebutton:
            idle "images/grps/confscrn/msp_slw_f.png"
            hover "images/grps/confscrn/msp_slw_f.png"
            selected_idle "images/grps/confscrn/msp_slw.png"
            selected_hover "images/grps/confscrn/msp_slw.png"
            action Preference("text speed", 25)
            xpos 202 ypos 279
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/msp_nom_f.png"
            hover "images/grps/confscrn/msp_nom_f.png"
            selected_idle "images/grps/confscrn/msp_nom.png"
            selected_hover "images/grps/confscrn/msp_nom.png"
            action Preference("text speed", 75)
            xpos 295 ypos 279
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/msp_now_f.png"
            hover "images/grps/confscrn/msp_now_f.png"
            selected_idle "images/grps/confscrn/msp_now.png"
            selected_hover "images/grps/confscrn/msp_now.png"
            action Preference("text speed", 0)
            xpos 388 ypos 279
            activate_sound "wav/0001.ogg"

        imagebutton:
            idle "images/grps/confscrn/msk_on_f.png"
            hover "images/grps/confscrn/msk_on_f.png"
            selected_idle "images/grps/confscrn/msk_on.png"
            selected_hover "images/grps/confscrn/msk_on.png"
            action Preference("skip", "all")
            xpos 202 ypos 311
            activate_sound "wav/0001.ogg"
        imagebutton:
            idle "images/grps/confscrn/msk_off_f.png"
            hover "images/grps/confscrn/msk_off_f.png"
            selected_idle "images/grps/confscrn/msk_off.png"
            selected_hover "images/grps/confscrn/msk_off.png"
            action Preference("skip", "seen")
            xpos 356 ypos 311
            activate_sound "wav/0001.ogg"

        if not title_mode:
            if store.save_enabled:
                imagebutton:
                    idle "images/grps/confscrn/save.png"
                    hover "images/grps/confscrn/save_f.png"
                    action ShowMenu("save")
                    xpos 148 ypos 346
                    activate_sound "wav/0001.ogg"
                imagebutton:
                    idle "images/grps/confscrn/load.png"
                    hover "images/grps/confscrn/load_f.png"
                    action ShowMenu("load")
                    xpos 263 ypos 346
                    activate_sound "wav/0001.ogg"
            imagebutton:
                idle "images/grps/confscrn/close.png"
                hover "images/grps/confscrn/close_f.png"
                action Return()
                xpos 115 ypos 372
                activate_sound "wav/0001.ogg"

        imagebutton:
            idle "images/grps/confscrn/title.png"
            hover "images/grps/confscrn/title_f.png"
            action MainMenu()
            xpos 213 ypos 372
            activate_sound "wav/0001.ogg"
        if not title_mode:
            imagebutton:
                idle "images/grps/confscrn/exit.png"
                hover "images/grps/confscrn/exit_f.png"
                action Quit(confirm=True)
                xpos 311 ypos 372
                activate_sound "wav/0001.ogg"

screen forest_title_preferences():
    tag menu
    modal True
    key "game_menu" action Return()

    add Solid("#000000b0")
    frame:
        xalign 0.5
        yalign 0.5
        xpadding 36
        ypadding 28
        vbox:
            spacing 14
            text "文本显示":
                size 26
                xalign 0.5
            hbox:
                spacing 12
                text "字号 [persistent.forest_text_size]"
                textbutton "－" action Function(
                    forest_adjust_text, "forest_text_size", -1, 14, 40)
                textbutton "＋" action Function(
                    forest_adjust_text, "forest_text_size", 1, 14, 40)
            hbox:
                spacing 12
                text "每行字符 [persistent.forest_line_chars]"
                textbutton "－" action Function(
                    forest_adjust_text, "forest_line_chars", -1, 10, 40)
                textbutton "＋" action Function(
                    forest_adjust_text, "forest_line_chars", 1, 10, 40)
            hbox:
                spacing 12
                text "字体 [forest_font_name()]"
                textbutton "上一字体" action Function(forest_cycle_font, -1)
                textbutton "下一字体" action Function(forest_cycle_font, 1)

            if len(forest_languages) > 1:
                text "语言"
                hbox:
                    spacing 10
                    for language, label in forest_languages:
                        textbutton label:
                            action Language(language)
                            selected _preferences.language == language

            text "持久化游戏进度"
            hbox:
                spacing 10
                textbutton "保存备份" action Function(forest_save_progress)
                textbutton "读取备份" action Function(forest_load_progress)
            textbutton "清除进度":
                xalign 0.5
                action Confirm(
                    "确定清除持久化游戏进度？备份会保留。",
                    Function(forest_clear_progress))
            textbutton "返回":
                xalign 0.5
                action Return()

screen save():
    tag menu
    use forest_file_slots("save")

screen load():
    tag menu
    use forest_file_slots("load")

screen forest_file_slots(mode):
    modal True
    key "game_menu" action Return()
    add ("images/grps/savescrn/bg_%s.png" % mode) xpos -501 ypos -89

    $ slot_positions = [(106, 137), (106, 204), (106, 271), (106, 338), (106, 405), (421, 137), (421, 204), (421, 271), (421, 338), (421, 405)]
    for index, position in enumerate(slot_positions):
        $ slot = index + 1
        $ slot_action = FileSave(slot) if mode == "save" else FileLoad(slot)
        $ dt1 = FileJson(slot, key="forest_dt1")
        button:
            xpos position[0]
            ypos position[1]
            xsize 257
            ysize 62
            background None
            hover_background Solid("#ffffff18")
            action slot_action
            fixed:
                if dt1:
                    add ("images/grps/dt1_%04d.png" % int(dt1))
                    text FileTime(slot, "%Y/%m/%d %H:%M"):
                        xpos 114 ypos 38
                        size 12
                        color "#3b2410"

    imagebutton:
        idle "images/grps/savescrn/prev.png"
        hover "images/grps/savescrn/prev_f.png"
        insensitive "images/grps/savescrn/prev_c.png"
        action FilePagePrevious(max=10, wrap=True, auto=False, quick=False)
        xpos 563 ypos 544
        activate_sound "wav/0001.ogg"
    $ page_name = FileCurrentPage()
    $ page_number = min(10, max(1, int(page_name))) if page_name.isdigit() else 1
    $ page_x = (14, 8, 8, 8, 8, 8, 8, 8, 9, 5)[page_number - 1]
    fixed:
        xpos 599 ypos 537
        xsize 38 ysize 34
        add ("images/grps/nonbl/%d.png" % page_number) xpos page_x ypos 2
    imagebutton:
        idle "images/grps/savescrn/next.png"
        hover "images/grps/savescrn/next_f.png"
        insensitive "images/grps/savescrn/next_c.png"
        action FilePageNext(max=10, wrap=True, auto=False, quick=False)
        xpos 636 ypos 544
        activate_sound "wav/0001.ogg"
    imagebutton:
        idle "images/grps/savescrn/exit.png"
        hover "images/grps/savescrn/exit_f.png"
        action Return()
        xpos 707 ypos 538
        activate_sound "wav/0001.ogg"

screen confirm(message, yes_action, no_action):
    modal True
    add Solid("#000000a0")
    frame:
        xalign 0.5
        yalign 0.5
        xpadding 36
        ypadding 26
        vbox:
            spacing 20
            text message:
                xalign 0.5
                text_align 0.5
                color "#ffffff"
            hbox:
                xalign 0.5
                spacing 50
                textbutton "はい" action yes_action
                textbutton "いいえ" action no_action

screen say(who, what, center=False):
    window:
        id "window"
        background Transform("images/grps/tbox01/back.png", alpha=persistent.textbox_opacity)
        xpos 0
        ypos 462
        xsize 800
        ysize 138
        if forest_speaker_visible and forest_speaker is not None:
            $ speaker_image = "images/grps/gf%03d.png" % forest_speaker
            if renpy.loadable(speaker_image):
                add speaker_image xpos 0 ypos 7
        elif forest_speaker_visible and who:
            text who:
                id "who"
                font forest_current_font()
                size 22
                color "#ffffff"
                xpos 0
                ypos 7
        text what:
            id "what"
            font forest_current_font()
            size persistent.forest_text_size
            color "#ffffff"
            xpos text_indent + 1
            ypos 8
            xsize persistent.forest_line_chars * persistent.forest_text_size
            text_align (0.5 if center else 0.0)
            line_spacing 7

        use forest_compane

screen forest_compane():
    zorder 100
    if not _preferences.afm_enable:
        fixed:
            xpos 606
            ypos 120
            xsize 194
            ysize 18

            bar:
                thumb "images/grps/compane/slide.png"
                hover_thumb "images/grps/compane/slide_f.png"
                base_bar "images/grps/compane/bg.png"
                thumb_offset 2
                value FieldValue(persistent, "textbox_opacity", range=1.0)
                xpos 4
                ypos 2
                xsize 75
                ysize 14
                bar_invert True

            imagebutton:
                idle "images/grps/compane/rev.png"
                hover "images/grps/compane/rev_f.png"
                selected_idle "images/grps/compane/rev.png"
                action If(jump_back_point, RollbackToIdentifier(jump_back_point), NullAction())
                sensitive jump_back_point is not None
                xpos 88
                ypos 2
                focus_mask True
            imagebutton:
                idle "images/grps/compane/bak.png"
                hover "images/grps/compane/bak_f.png"
                selected_idle "images/grps/compane/bak.png"
                action Rollback()
                xpos 105
                ypos 2
                focus_mask True
            imagebutton:
                idle "images/grps/compane/fow.png"
                hover "images/grps/compane/fow_f.png"
                selected_idle "images/grps/compane/fow.png"
                action RollForward()
                xpos 122
                ypos 2
                focus_mask True
            imagebutton:
                idle "images/grps/compane/next.png"
                hover "images/grps/compane/next_f.png"
                selected_idle "images/grps/compane/next.png"
                action Skip(fast=True)
                xpos 139
                ypos 2
                focus_mask True
            imagebutton:
                idle "images/grps/compane/voc.png"
                hover "images/grps/compane/voc_f.png"
                selected_idle "images/grps/compane/voc.png"
                insensitive "images/grps/compane/voc_off.png"
                action Function(forest_replay_voice)
                sensitive forest_last_voice is not None
                xpos 155
                ypos 1
                focus_mask True
            imagebutton:
                idle "images/grps/compane/hide.png"
                hover "images/grps/compane/hide_f.png"
                selected_idle "images/grps/compane/hide.png"
                action HideInterface()
                xpos 173
                ypos 2
                focus_mask True

screen choice(items):
    modal True
    $ options = [item for item in items if item.action is not None]
    vbox:
        xalign 0.5
        yalign 0.4
        spacing -4
        if forest_choice_prompt:
            fixed:
                xsize 505
                ysize 48
                add "images/grps/sel_q00/body.png"
                text forest_choice_prompt:
                    font forest_current_font()
                    size 20
                    color "#2a2015"
                    xpos 35
                    yalign 0.45
        for item in options:
            $ asset = forest_choice_asset(item.caption)
            $ stem = "sel_a%02d" % asset if asset is not None else "sel_a00"
            fixed:
                xsize 505
                ysize 82
                imagebutton:
                    idle "images/grps/%s/body.png" % stem
                    hover "images/grps/%s/body_f.png" % stem
                    focus_mask True
                    xalign 0.5
                    yalign 0.5
                    action item.action
                if asset is None:
                    text item.caption:
                        font forest_current_font()
                        size 21
                        color "#ffffff"
                        outlines [(2, "#18220d", 0, 0)]
                        xpos 48
                        yalign 0.46

screen forest_click_screen(options):
    modal True
    for value, system, idle_image, hover_image, xpos, ypos in options:
        $ click_action = forest_system_action(value) if system else Return(value)
        imagebutton:
            idle idle_image
            hover hover_image
            focus_mask True
            xpos xpos
            ypos ypos
            action click_action

python early:
    def forest_choice_asset(caption):
        try:
            if caption.startswith("forest_asset_"):
                number = store._r[int(caption[13:])]
            else:
                number = int(caption)
        except (TypeError, ValueError):
            return None
        stem = "images/grps/sel_a%02d/body.png" % number
        return number if renpy.loadable(stem) else None

    def parse_forest_folder(lex):
        args = rscript_arguments(lex, ["Layer", "Folder"])
        lex.expect_eol()
        return args

    def execute_forest_folder(args):
        if args.Layer == 0:
            for layer in range(100):
                store.folder[layer] = args.Folder
        else:
            store.folder[args.Layer] = args.Folder

    renpy.register_statement("_forest_folder", parse=parse_forest_folder,
        execute=execute_forest_folder, lint=lint_undef)

    def parse_forest_setclk(lex):
        args = rscript_arguments(lex, ["Layer", "Value", "Mode", "Unknown"])
        lex.expect_eol()
        return args

    def execute_forest_setclk(args):
        store.forest_click_values[args.Layer] = args.Value
        store.forest_click_system.pop(args.Layer, None)

    def execute_forest_setclksys(args):
        store.forest_click_values[args.Layer] = args.Value
        store.forest_click_system[args.Layer] = True

    renpy.register_statement("_forest_setclk", parse=parse_forest_setclk,
        execute=execute_forest_setclk, lint=lint_undef)
    renpy.register_statement("_forest_setclksys", parse=parse_forest_setclk,
        execute=execute_forest_setclksys, lint=lint_undef)

    def forest_system_action(value):
        if value == 0:
            return Quit(confirm=True)
        if value == 1:
            return ShowMenu("save")
        if value == 2:
            return ShowMenu("load")
        if value == 3:
            if store.menu_enabled:
                return ShowMenu("preferences")
            return ShowMenu("forest_title_preferences")
        return Return(value)

    def parse_forest_setlink(lex):
        args = rscript_arguments(lex, ["Layer", "HoverCG", "xLoc", "yLoc"])
        lex.expect_eol()
        return args

    def execute_forest_setlink(args):
        store.forest_click_links[args.Layer] = (args.HoverCG, args.xLoc, args.yLoc)

    renpy.register_statement("_forest_setlink", parse=parse_forest_setlink,
        execute=execute_forest_setlink, lint=lint_undef)

    def parse_forest_click(lex):
        args = rscript_arguments(lex, ["Unknown1", "Unknown2"])
        lex.expect_eol()
        return args

    def execute_forest_click(args):
        options = []
        for layer in sorted(store.forest_click_values):
            if layer not in store.forest_click_links or layer not in store.layer_info:
                continue
            hover_cg, xpos, ypos = store.forest_click_links[layer]
            folder_name = store.folder.get(layer, store.folder.get(0))
            if not folder_name:
                continue
            options.append((
                store.forest_click_values[layer],
                store.forest_click_system.get(layer, False),
                store.layer_info[layer],
                "%s %04d" % (folder_name, hover_cg),
                xpos * store.layer_x_grid,
                ypos * store.layer_y_grid,
            ))
        if options:
            store._r[0] = renpy.call_screen("forest_click_screen", options=options)
        else:
            renpy.notify("Forest: click instruction has no active regions")
            store._r[0] = 0
        store.forest_click_links.clear()
        store.forest_click_values.clear()
        store.forest_click_system.clear()

    renpy.register_statement("_forest_click", parse=parse_forest_click,
        execute=execute_forest_click, lint=lint_undef)

    def parse_forest_noargs(lex):
        lex.rest()
        lex.expect_eol()

    def execute_forest_resetclk(args):
        store.forest_click_links.clear()
        store.forest_click_values.clear()
        store.forest_click_system.clear()

    renpy.register_statement("_forest_resetclk", parse=parse_forest_noargs,
        execute=execute_forest_resetclk, lint=lint_undef)
    renpy.register_statement("_forest_autoreset", parse=parse_forest_noargs,
        execute=lambda args: None, lint=lint_undef)
'''


def copy_assets(source: Path, pattern: str, target: Path) -> None:
    if source.is_dir():
        for asset in source.rglob(pattern):
            output = target / asset.relative_to(source)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(asset, output)


def convert_masks(source: Path, target: Path) -> None:
    for asset in source.rglob("*.msk"):
        output = (target / asset.relative_to(source)).with_suffix(".png")
        output.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(asset) as image:
            image.save(output, "PNG")


def convert_movies(source: Path, target: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is required to convert Forest's MPEG movies")
    target.mkdir(parents=True, exist_ok=True)
    for obsolete in target.iterdir():
        if obsolete.is_file() and obsolete.suffix.lower() == ".mpg":
            obsolete.unlink()
    for asset in sorted(source.glob("*.mpg")):
        output = target / (asset.stem + ".webm")
        if (output.is_file() and output.stat().st_size
                and output.stat().st_mtime_ns >= asset.stat().st_mtime_ns):
            continue
        temporary = output.with_name(output.stem + ".tmp" + output.suffix)
        try:
            subprocess.run([
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(asset),
                "-c:v", "libvpx-vp9", "-crf", "18", "-b:v", "0",
                "-c:a", "libvorbis", "-q:a", "5",
                str(temporary),
            ], check=True)
            temporary.replace(output)
        finally:
            if temporary.exists():
                temporary.unlink()


def validate_inputs(root: Path) -> None:
    required_dirs = (
        "scr", "grpe", "grpo", "grpo_bg", "grpo_bu", "grpo_ci",
        "grpo_f", "grps", "wav", "bgm", "voice", "mov",
    )
    missing = [str(root / name) for name in required_dirs
               if not (root / name).is_dir()]
    required_assets = (
        root / "grpe" / "9001.png",
        root / "bgm" / "Track01.ogg",
    )
    missing.extend(str(path) for path in required_assets if not path.is_file())
    if not scenario_sources(root / "scr"):
        missing.append(str(root / "scr" / "*.tsc"))
    for folder in ("wav", "voice"):
        if not list((root / folder).glob("*.ogg")):
            missing.append(str(root / folder / "*.ogg"))
    for movie in ("0001", "0002"):
        if not any((root / "mov" / (movie + suffix)).is_file()
                   for suffix in (".mpg", ".MPG", ".webm")):
            missing.append(str(root / "mov" / (movie + ".{mpg,webm}")))
    if missing:
        raise FileNotFoundError(
            "resources must be unpacked and converted first; missing:\n- " +
            "\n- ".join(missing))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Build a Forest Ren'Py project from converted resources")
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument(
        "--language", metavar="NAME[=PATCH_DIR]", action="append", default=[],
        help="plain NAME marks _say/_append; NAME=DIR adds a translated patch")
    args = parser.parse_args(argv[1:])
    language_marker, language_patches = parse_language_options(args.language)
    root = args.resources.resolve()
    target = args.project.resolve()
    here = Path(__file__).resolve().parents[1]
    runtime = here / "runtime"
    font_source = here / "forest" / "fonts"
    gui_template = here / "forest" / "gui.rpy"
    game = target / "game"
    validate_inputs(root)
    scenario = game / "scenario"
    scenario.mkdir(parents=True, exist_ok=True)
    for cache in scenario.glob("*.rpyc"):
        cache.unlink()
    for source in runtime.glob("*.rpy"):
        if source.name not in {"script.rpy", "build.rpy", "options.rpy"} and not source.name.startswith("unren-"):
            shutil.copyfile(source, game / source.name)
    cursor = game / "gui" / "rscript_cursor.png"
    cursor.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(runtime / "gui" / "rscript_cursor.png", cursor)
    for obsolete in game.glob("unren-*.rpy*"):
        obsolete.unlink()
    definitions_path = game / "01_defines.rpy"
    definitions_text = definitions_path.read_text(encoding="utf-8")
    if "    default object_size = {}" not in definitions_text:
        definitions_text = definitions_text.replace(
            "    default layer_anchor = {}",
            "    default layer_anchor = {}\n    default object_size = {}")
    definitions_text = definitions_text.replace(
        "                persistent._reg[key] = value",
        "                persistent._reg[key] = value\n"
        "                renpy.save_persistent()")
    definitions_path.write_text(definitions_text, encoding="utf-8")
    gfx_path = game / "03_rscript_gfx.rpy"
    gfx_text = gfx_path.read_text(encoding="utf-8")
    if "def parse_oload(lex):" not in gfx_text:
        gfx_path.write_text(gfx_text.rstrip() + RSCRIPT_OBJECTS, encoding="utf-8")
    gui_path = game / "gui.rpy"
    if not gui_path.is_file():
        shutil.copyfile(gui_template, gui_path)
    gui_text = gui_path.read_text(encoding="utf-8")
    gui_text = gui_text.replace("gui.init(1280, 720)", "gui.init(800, 600)")
    gui_text = gui_text.replace(
        "NOTO_SANS", '"fonts/NotoSansCJKjp-Regular.otf"')
    gui_text = gui_text.replace(
        '"DejaVuSans.ttf"', '"fonts/NotoSansCJKjp-Regular.otf"')
    gui_text = re.sub(r"gui\.scale\((-?\d+(?:\.\d+)?)\)", r"\1", gui_text)
    gui_path.write_text(gui_text, encoding="utf-8")
    fonts = game / "fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    for name in ("NotoSansCJKjp-Regular.otf", "NotoSans.txt"):
        shutil.copyfile(font_source / name, fonts / name)
    audio_path = game / "04_rscript_audio.rpy"
    audio_text = audio_path.read_text(encoding="utf-8")
    audio_text = audio_text.replace('"bgm/Track%02d.opus"', '"bgm/Track%02d.ogg"')
    audio_text = audio_text.replace('"wav/%04d.opus"', '"wav/%04d.ogg"')
    audio_text = audio_text.replace('"voice/%05d.opus"', '"voice/%04d.ogg"')
    audio_text = audio_text.replace(
        "        voice(voice_file)",
        "        if renpy.loadable(voice_file):\n"
        "            store.forest_last_voice = voice_file\n"
        "            renpy.music.play(voice_file, channel = \"rscript_voice\", loop = False, if_changed = False)\n"
        "        else:\n"
        "            renpy.log(\"Forest: missing voice %s\" % voice_file)")
    audio_text = audio_text.replace('channel = "voice"', 'channel = "rscript_voice"')
    audio_text = audio_text.replace('wait_audio("voice")', 'wait_audio("rscript_voice")')
    audio_text = audio_text.replace(
        "        renpy.music.play(bgm, channel = \"music\", fadein = fadein, loop = True, if_changed = True)",
        "        if renpy.loadable(bgm):\n"
        "            renpy.music.play(bgm, channel = \"music\", fadein = fadein, loop = True, if_changed = True)\n"
        "        else:\n"
        "            renpy.log(\"Forest: missing BGM %s\" % bgm)")
    audio_text = audio_text.replace(
        "        se_file = [se_file] * (args.Repeat + 1)",
        "        if not renpy.loadable(se_file):\n"
        "            renpy.log(\"Forest: missing sound effect %s\" % se_file)\n"
        "            return\n"
        "        loop = args.Repeat == 999\n"
        "        se_file = [se_file] if loop else [se_file] * (args.Repeat + 1)")
    audio_text = audio_text.replace(
        "        renpy.music.play(se_file, channel, loop = False, fadein = fade, if_changed = False)",
        "        renpy.music.play(se_file, channel, loop = loop, fadein = fade, if_changed = False)")
    audio_path.write_text(audio_text, encoding="utf-8")
    text_path = game / "05_rscript_text.rpy"
    text_runtime = text_path.read_text(encoding="utf-8")
    text_runtime = text_runtime.replace(
        '        who = lex.match(r"(.*?)：")',
        "        who = None",
        1)
    text_runtime = text_runtime.replace(
        "        what, center = parse_rscript_text(what)",
        "        store.forest_speaker = None\n"
        "        store.forest_speaker_visible = True\n"
        "        what, center = parse_rscript_text(what)",
        1)
    text_runtime = text_runtime.replace(
        "        if store.jump_back_point is None:",
        "        store.forest_speaker_visible = False\n\n"
        "        if store.jump_back_point is None:",
        1)
    text_runtime = text_runtime.replace(
        "        who  = store.last_spk\n"
        "        what, center = parse_rscript_text(what)",
        "        who  = store.last_spk\n"
        "        store.forest_speaker_visible = True\n"
        "        what, center = parse_rscript_text(what)",
        1)
    text_runtime = text_runtime.replace(
        "        who.do_extend()\n"
        "        renpy.say(who, what, interact = True, show_center = center)\n\n"
        "    renpy.register_statement(\"_append\"",
        "        who.do_extend()\n"
        "        renpy.say(who, what, interact = True, show_center = center)\n"
        "        store.forest_speaker_visible = False\n\n"
        "    renpy.register_statement(\"_append\"",
        1)
    text_path.write_text(text_runtime, encoding="utf-8")
    util_path = game / "01_util.rpy"
    util_text = util_path.read_text(encoding="utf-8")
    util_text = util_text.replace(
        "        text = eval(text).rstrip()",
        "        text = renpy.translation.translate_string(eval(text).rstrip())\n"
        "        speaker = renpy.re.match(r\"^\\^g(\\d{3})\", text)\n"
        "        if speaker:\n"
        "            store.forest_speaker = int(speaker.group(1))\n"
        "            text = text[speaker.end():]",
        1)
    util_path.write_text(util_text, encoding="utf-8")
    channels_path = game / "audio.rpy"
    channels_text = channels_path.read_text(encoding="utf-8")
    channels_text = channels_text.replace(
        '        renpy.music.stop("voice")',
        '        renpy.music.stop("voice")\n'
        '        renpy.music.stop("rscript_voice")')
    channels_text = channels_text.replace(
        '    renpy.music.register_channel(name = "se0"',
        '    renpy.music.register_channel(name = "rscript_voice", mixer = "voice", tight = True, loop = False)\n'
        '    renpy.music.register_channel(name = "se0"')
    channels_path.write_text(channels_text, encoding="utf-8")
    character_path = game / "character.rpy"
    character_text = character_path.read_text(encoding="utf-8")
    character_text = character_text.replace("        xpos 1191", "        xpos 735")
    character_text = character_text.replace("        ypos 639", "        ypos 565")
    character_path.write_text(character_text, encoding="utf-8")
    language_labels = [(None, language_marker or "原文")]
    language_labels.extend((name, name) for name, _ in language_patches)
    compat = FOREST_COMPAT.replace(
        'define forest_languages = [(None, "原文")]',
        "define forest_languages = %r" % language_labels)
    (game / "forest_compat.rpy").write_text(compat, encoding="utf-8")
    for folder in ("grpe", "grpo", "grpo_bg", "grpo_bu", "grpo_ci", "grpo_f", "grps"):
        copy_assets(root / folder, "*.png", game / "images" / folder)
        copy_assets(root / folder, ".meta.xml", game / "images" / folder)
    for obsolete in (game / "images" / "grps" / "confscrn").glob("*lev.png"):
        obsolete.unlink()
    convert_masks(root / "grps", game / "images" / "grps")
    for source_folder, target_folder in (("wav", "wav"), ("wav", "audio"),
                                         ("bgm", "bgm"), ("voice", "voice")):
        audio_target = game / target_folder
        for pattern in ("*.wav", "*.ogg"):
            for obsolete in audio_target.glob(pattern):
                obsolete.unlink()
        copy_assets(root / source_folder, "*.ogg", audio_target)
    convert_movies(root / "mov", game / "mov")
    patch_texts = {}
    patch_insertions = {}
    for language, patch in language_patches:
        replacements, insertions = language_patch_data(root / "scr",
                                                        patch / "scr")
        patch_texts[language] = replacements
        patch_insertions[language] = insertions
        write_language_patch(root, patch, language, game)
    (game / "options.rpy").write_text(
        'define config.name = "Forest"\n'
        'define config.version = "1.0"\n'
        'define config.has_sound = True\n'
        'define config.has_music = True\n'
        'define config.has_voice = True\n'
        'define config.layers = ["debug", "black", "cg", "master", "flash", '
        '"transient", "screens", "overlay"]\n', encoding="utf-8")
    (game / "script.rpy").write_text(
        'label splashscreen:\n'
        '    scene onlayer master\n'
        '    scene black onlayer black\n'
        '    _movie 2\n'
        '    _movie 1\n'
        '    return\n\n'
        'label main_menu:\n'
        '    return\n\n'
        'label start:\n'
        '    scene onlayer master\n'
        '    scene black onlayer black\n'
        '    call _0000\n'
        '    return\n', encoding="utf-8")
    sources = scenario_sources(root / "scr")
    for source in sources:
        scene_texts = {
            language: replacements[source.name]
            for language, replacements in patch_texts.items()
            if source.name in replacements
        }
        scene_insertions = {
            language: insertions[source.name]
            for language, insertions in patch_insertions.items()
            if source.name in insertions
        }
        (scenario / (source.stem + ".rpy")).write_text(
            compile_scene(source, language_marker, scene_texts,
                          scene_insertions),
            encoding="utf-8")
    print("Wrote %s: %d rscript scenes" % (target, len(sources)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
