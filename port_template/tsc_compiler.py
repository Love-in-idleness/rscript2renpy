"""Shared early/modern CodeX lowering, with explicit adapter policies."""

from pathlib import Path
import sys
import re

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "port_template"))
from rscript_tsc import E, read_tsc  # noqa: E402
from tsc_vm import emit_vm, packed  # noqa: E402
from tsc_patches import (language_patch_data, instruction_strings, menu_text,
                         patch_text_expression, emit_insertions,
                         emit_operand_variants)  # noqa: E402


PASSTHROUGH = {
    10: "hit", 13: "wait", 20: "gload", 23: "quake", 26: "queue",
    27: "action", 28: "update", 30: "load", 36: "cls", 37: "enabl",
    39: "draw", 42: "tbox", 43: "effect", 45: "tone",
    46: "tonedep", 47: "locgrid", 49: "mode", 52: "stop",
    56: "sysmode", 60: "bgm_on", 61: "bgm_off", 65: "movie",
    66: "voice", 67: "voice_off", 68: "se_wait", 69: "voice_wait",
    74: "autoreset", 83: "txcls", 90: "tboxloc",
    92: "tboxback", 93: "cmploc", 94: "tboxcmp", 95: "texcolor",
    96: "texsize", 97: "texfont", 98: "texmode", 99: "texindent",
    103: "waitlod", 104: "waitcol", 132: "numenable",
}
MODERN_PASSTHROUGH = dict(PASSTHROUGH)
MODERN_PASSTHROUGH.update({
    11: "hitc", 17: "backup", 21: "gcls", 22: "gmove", 24: "flash",
    29: "zupdate", 34: "movi", 40: "depth", 41: "group", 44: "effectdep",
    50: "backup", 55: "makesave", 57: "logflash", 91: "texloc",
    100: "waitloc", 106: "namloc", 107: "texpich", 108: "texruby",
})
KHIME_COMMANDS = {
    48: "face", 101: "faceloc", 105: "facedep", 130: "numload",
    131: "numreng", 134: "numloc", 135: "numset", 136: "num",
    70: "setclk", 71: "setclksys", 72: "resetclk", 73: "click",
    75: "setlink", 38: "locmode",
}
EARLY_COMMANDS = dict(MODERN_PASSTHROUGH)
for _modern_only in (106, 107, 108):
    EARLY_COMMANDS.pop(_modern_only)
EARLY_COMMANDS.update({33: "move", 35: "oaction", 38: "locmode", 120: "osize"})

EARLY_PATCH_OPCODES = set(EARLY_COMMANDS) - {30, 36, 64}
EARLY_PATCH_OPCODES.update({70, 71, 72, 73, 75})


def label(scene: str, offset: int) -> str:
    return "_%s_L_%06x" % (scene, offset)


def compile_scene(source: Path, patches=(), *, zero=False, zero_title=False,
                  adapter="khime", scene_prefix="", language=None,
                  language_texts=None, language_insertions=None,
                  language_operands=None, scene_name=None, operand_patch=None,
                  statement_prefix=None) -> str:
    # Zero uses the early/legacy-28 operand table, not Khime's modern dialect.
    legacy = adapter == "pre-codex"
    early = adapter in {"early", "pre-codex"}
    modern = adapter not in {"khime", "early", "pre-codex"}
    dialect = "legacy" if legacy else "forest" if zero or early else "modern"
    tsc = read_tsc(source, dialect)
    items = tsc.instructions()
    patch_texts = language_texts or {}
    patch_insertions = language_insertions or {}
    patch_operands = language_operands or {}
    for patch_language, directory in patches:
        path = directory / "scr" / source.name
        if not path.is_file():
            continue  # A partial language patch falls back to original text.
        texts, additions, overrides = language_patch_data(
            source.parent, directory / "scr", dialect=dialect,
            override_opcodes=set(PASSTHROUGH) - {20, 65},
            menu_transform=menu_text,
            source_names={source.name})
        patch_texts[patch_language] = texts.get(source.name, {})
        patch_insertions[patch_language] = additions.get(source.name, {})
        patch_operands[patch_language] = overrides.get(source.name, {})
    languages = set(patch_texts) | set(patch_insertions) | set(patch_operands)
    if language:
        languages.add(language)
    for name in languages:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ValueError("invalid language name: %s" % name)
    if scene_name and not re.fullmatch(r"[A-Za-z0-9_]+", scene_name):
        raise ValueError("invalid scene name: %s" % scene_name)

    def text(item, index):
        original = tsc.string(item.operands[index])
        if item.opcode == 14:
            original = menu_text(original)
        kind = ({14: {1: "prompt"}, 32: {5: "oload"},
                 82: {4: "append"}}.get(item.opcode, {}).get(index)
                or "choice%d" % (index - 7))
        return patch_text_expression(patch_texts, item, kind, original)[0]
    scene = scene_name or ("khime_zero_" + source.stem if zero else scene_prefix + source.stem)
    commands = EARLY_COMMANDS if early else PASSTHROUGH if adapter == "khime" else MODERN_PASSTHROUGH
    prefix = statement_prefix or ("khime" if adapter == "khime" else "rscript")
    targets = {item.operands[0] for item in items if item.opcode in (3, 4, 5, 200)}
    targets.update(offset for name, offset in tsc.named_entries)
    entries = {}
    for name, offset in tsc.named_entries:
        # Generated labels already start with _g_<scene>_, so numeric names
        # such as Khime 1125's "8011" are valid suffixes too.
        if not re.fullmatch(r"[A-Za-z0-9_]+", name):
            raise ValueError("%s: unsupported named-entry identifier %r" % (source, name))
        entries.setdefault(offset, []).append(name)
    for item in items:
        if item.opcode == 14:
            targets.update(item.operands[2:2 + min(item.operands[0], 5)])
    boundaries = {item.offset for item in items} | {tsc.code_size}
    if not early and targets - boundaries:
        raise ValueError("%s: non-instruction target %s" %
                         (source, sorted(targets - boundaries)))

    header = "command offsets are" if early else "offsets"
    lines = ["# Generated from %s; %s preserved in labels." % (source.name, header),
             "label _%s:" % scene]
    temps = {}
    for item in items:
        emit_insertions(lines, patch_insertions, item.offset)
        if item.offset in targets:
            lines.extend(("", "label %s:" % label(scene, item.offset)))
        for name in entries.get(item.offset, ()):
            lines.append("label _g_%s_%s:" % (scene, name))
        op, values = item.opcode, item.operands
        operands = [packed(value, word16=legacy) if kind == E else str(value)
                    for kind, value in zip(item.kinds, values)]
        if modern and op == 55:
            lines.append("    # CodeX makesave: native in-memory execution snapshot is not implemented; Ren'Py saves its current state.")
        if modern and op == 97 and values[1] != 2:
            lines.append("    # CodeX texfont slot %s needs a port font-slot mapping; unmapped slots use the player font." % operands[1])
        if modern and op == 38 and values[3]:
            lines.append("    # CodeX locmode Mode %s ignored; only the X/Y origin is implemented." % operands[3])
        if modern and op == 213:
            lines.append("    # CodeX dyndo %s: paging/skin retained; native transition/motion uses the shared choice screen." % " ".join(operands))
        if zero_title and source.stem == "0101" and (
                (op == 30 and values[:2] == (46, 9006)) or
                (op == 75 and values[:2] == (46, 9106))):
            lines.append("    # Khime Zero: reserve a row between 9105 and 9106 only when unlocked.")
            # Entry height: ceil(34px * 1.25) + 1px gap = 44px.
            operands[3] = "517+44*khime_zero_unlocked()"
        if op & 0xf000:
            lines.extend("    " + line for line in emit_vm(op, values, temps, snapshot=legacy, word16=legacy))
        elif op == 9:
            if legacy:
                lines.append("    $ rscript_vm_temps[%d] = renpy.random.randrange(0x8000)" % values[0])
            else:
                temps[values[0]] = "renpy.random.randrange(0x8000)"
        elif op in (3, 4):
            condition = "rscript_vm_temps.get(0, 0)" if legacy else temps.get(0, "0")
            test = "not (%s)" % condition if op == 3 else "(%s)" % condition
            lines.extend(("    if %s:" % test,
                          "        jump %s" % label(scene, values[0])))
        elif op == 5:
            lines.append("    jump %s" % label(scene, values[0]))
        elif op == 8:
            # KhimeDL_CHS.exe 0x41fe3c -> 0x420e66 exits the interpreter,
            # not a gosub frame (opcode 16). Do not resume the caller's story.
            lines.append("    return" if early else "    _end")
        elif op == 12:
            entry = tsc.string(values[1]) if len(values) > 1 else ""
            lines.append("    _jump %s" % (operands[0] + ("%" + entry if entry else "")))
        elif op == 14:
            count = min(values[0], 5)
            prompt = text(item, 1)
            if early:
                prompt = "rscript_inline_graphics(renpy.translation.translate_string(%s))" % prompt
            lines.append("    $ %s_choice_prompt = %s" % (prefix, prompt))
            captions = [text(item, 7 + index) for index in range(count)]
            for index, caption in enumerate(captions):
                if early:
                    original = menu_text(tsc.string(values[7 + index]))
                    changed = patch_text_expression(patch_texts, item, "choice%d" % index, original)[1]
                    if changed or "^g" in caption:
                        variable = "%s_choice_%d" % (prefix, index)
                        lines.append("    $ %s = rscript_inline_graphics(renpy.translation.translate_string(%s))" % (variable, caption))
                        captions[index] = repr("[%s]" % variable)
                elif patch_texts:
                    lines.append("    $ khime_menu_caption_%d = %s" % (index, caption))
            lines.append("    menu:")
            for index in range(count):
                caption = (repr("[khime_menu_caption_%d]" % index)
                           if patch_texts and not early else captions[index])
                lines.extend(("        %s:" % caption,
                              "            $ _r[%s] = %d" % (operands[12] if len(operands) > 12 else "0", index)))
                if not early:
                    lines.append("            $ %s_choice_prompt = None" % prefix)
                lines.append("            jump %s" % label(scene, values[2 + index]))
        elif op == 15:
            if early:
                lines.append("    _gosub %s" % operands[0])
            else:
                name = operands[0] + (("%" + tsc.string(values[1]))
                                      if tsc.string(values[1]) else "")
                lines.append("    _gosub %s %s" % (name, " ".join(operands[2:])))
        elif op == 16:
            lines.append("    return" if early else "    _return %s" % operands[0])
        elif op == 18:
            data = () if not early and values[1] == 0 else tsc.data(values[1])
            if early:
                lines.extend("    $ _r[(%s) + %d] = %d" % (operands[0], index, value)
                             for index, value in enumerate(data))
            else:
                lines.append("    _data %s %s" %
                             (operands[0], " ".join(map(str, data))))
        elif op == 32:
            lines.append("    _oload %s %s" %
                         (" ".join(operands[:5]), text(item, 5)))
        elif op == 62:
            if not modern:
                lines.append("    _se 0 %s" % operands[-1])
            else:
                lines.append("    _se %s" % " ".join(operands))
        elif op == 63:
            lines.append("    _se_on %s" % " ".join(
                ["0"] + (operands if early else operands[-3:]) if not modern else operands))
        elif op == 64:
            lines.append("    _se_off %s" % ("0 " + operands[-1]
                                           if not modern else " ".join(operands)))
        elif op == 81:
            original = tsc.string(values[4]) if legacy else instruction_strings(tsc, item)["say"]
            raw = patch_text_expression(patch_texts, item, "say", original)[0]
            if values[1]:
                lines.append("    _voice %s 0 0 0" % operands[1])
            if modern:
                raw = "(%r, %r, %s)" % (tsc.string(values[4]), tsc.string(values[5]), operands[6])
                if any(values[index] for index in (0, 2, 3)):
                    lines.append("    # CodeX TXT box/voice mode operands %s are not implemented." % " ".join(operands[:4]))
            command = "say" + (" " + language if language else "") if early else prefix + "_say"
            lines.append("    _%s %s" % (command, raw))
        elif op == 82:
            body = text(item, 4)
            if modern:
                body = "(%s, %s)" % (body, operands[5])
            command = "append" + (" " + language if language else "") if early else prefix + "_append"
            lines.append("    _%s %s" % (command, body))
        elif op == 120 and not early:
            if zero:
                operands[1] = "int(round((%s)*1.25))" % operands[1]
            lines.append("    _osize %s" % " ".join(operands))
        elif op == 121:
            lines.append("    _%s_folder %s %r" %
                         (prefix, operands[0], tsc.string(values[1])))
        elif op == 200:
            target = label(scene, values[0])
            lines.append("    _insub %s %s" % (target, " ".join(operands[1:])))
        elif op == 202:
            lines.append("    _flagset %s" % " ".join(operands))
        elif legacy and op == 111:
            # Cannonball.exe 0x417f40: signed multiply/divide, result in r0.
            lines.append("    $ _r[0] = rscript_muldev(%s) & 65535" % ", ".join(operands))
        elif legacy and op in {130, 131, 132, 134, 135, 136}:
            lines.append("    _rscript_number %s %s" % (
                {130: "numload", 131: "numreng", 132: "numenable",
                 134: "numloc", 135: "numset", 136: "num"}[op], " ".join(operands)))
        elif op in (210, 211, 212):
            command = {210: "dynsel", 211: "dynans", 212: "dynnext"}[op]
            args = repr(tsc.string(values[0]))
            if op == 211:
                args += ", " + ", ".join(operands[1:])
            elif op == 210:
                args += ", " + operands[1]
            lines.append("    _%s (%s)" % (command, args))
        elif op == 213:
            lines.append("    _dyndo %s" % " ".join(operands))
        elif op == 225:
            lines.append("    _locmap %s" % " ".join(operands))
        elif op in KHIME_COMMANDS and (not early or op in {70, 71, 72, 73, 75}):
            def adapter_statement(parameters):
                args = operands if parameters == values else [
                    packed(value, word16=legacy) if kind == E else str(value)
                    for kind, value in zip(item.kinds, parameters)]
                return "_%s_%s %s" % (prefix, KHIME_COMMANDS[op], " ".join(args))
            emit_operand_variants(lines, patch_operands, item, adapter_statement)
        elif op in commands:
            def statement(parameters):
                args = [packed(value, word16=legacy) if kind == E else str(value)
                        for kind, value in zip(item.kinds, parameters)]
                command = commands[op]
                if zero and op in (20, 60):
                    command = "khime_zero_" + command
                if zero and op in (60, 61):
                    # The early dialect lacks modern FadeLen. Keep the existing
                    # no-fade fallback explicit until its duration is confirmed.
                    if parameters[-1]:
                        lines.append("    # Khime Zero conversion: legacy BGM fade %s flattened to 0 (duration unconfirmed)." % args[-1])
                    args[-1] = "0"
                    args.append("0")
                if legacy and op in (60, 61):
                    # Cannonball.exe 43d122 / 43db4f: 100 ticks of 20 ms.
                    if parameters[-1]:
                        lines.append("    # Legacy BGM fade %s: nonzero enables the native 2000 ms fade." % args[-1])
                    args[-1] = "int(bool(%s))" % args[-1] if parameters[-1] >= 65536 else str(int(bool(parameters[-1])))
                    args.append("2000")
                if legacy and op == 39:
                    # Native 405490 maps only 1/2 specially; all others are normal.
                    mode = parameters[1]
                    if mode >= 65536:
                        args[1] = "{1:1,2:2}.get(%s,0)" % args[1]
                    elif mode not in (0, 1, 2):
                        lines.append("    # Legacy draw mode %s: native normal-drawing alias, not an unsupported effect." % args[1])
                        args[1] = "0"
                if legacy and op == 21:
                    args = ["0"]
                if zero_title and op == 30 and source.stem == "0101" and parameters[:2] == (46, 9006):
                    args[3] = "517+44*khime_zero_unlocked()"
                if early and op == 74:
                    command = prefix + "_" + command
                if operand_patch:
                    args = operand_patch(scene, item, args, lines)
                return "_%s%s" % (command, " " + " ".join(args) if args else "")
            emit_operand_variants(lines, patch_operands, item, statement)
        else:
            if early and not legacy:
                lines.append("    # unlifted opcode 0x%04x %s" % (op, values))
            else:
                raise ValueError("%s: unsupported opcode 0x%04x" % (source, op))
    emit_insertions(lines, patch_insertions, tsc.code_size)
    if early:
        for target in sorted(targets - {item.offset for item in items}):
            lines.extend(("", "label %s:" % label(scene, target), "    return"))
    elif tsc.code_size in targets:
        lines.extend(("", "label %s:" % label(scene, tsc.code_size)))
    for name in entries.get(tsc.code_size, ()):
        lines.append("label _g_%s_%s:" % (scene, name))
    lines.append("    return")
    return "\n".join(lines) + "\n"


def compile_overlays(resources: Path, patches=(), *, adapter="modern") -> dict[str, str]:
    """Whole-scenario localization, including added scenes and changed offsets."""
    variants = [(None, resources), *patches]
    files = {}
    routes = {}
    entry_routes = {}
    for index, (language, directory) in enumerate(variants):
        sources = sorted((directory / "scr").glob("*.tsc"))
        if not sources:
            raise FileNotFoundError("no current TSC scripts: %s" % (directory / "scr"))
        for source in sources:
            if not source.stem.isdigit():
                raise ValueError("numeric scene filename required: %s" % source)
            prefix = "rscript_variant%d_" % index
            destination = ("scr/%s.rpy" % source.stem if language is None else
                           "tl/%s/scr/%s.rpy" % (language, source.stem))
            files[destination] = compile_scene(
                source, adapter=adapter, scene_prefix=prefix)
            routes.setdefault(source.stem, []).append((language, prefix + source.stem))
            for name, offset in read_tsc(source, "legacy" if adapter == "pre-codex" else "modern").named_entries:
                entry_routes.setdefault((source.stem, name), []).append((language, "_g_%s%s_%s" % (prefix, source.stem, name)))
    for scene, destinations in routes.items():
        lines = ["# Generated language-aware scene entry.", "label _%s:" % scene]
        for language, target in destinations:
            if language is not None:
                lines += ["    if _preferences.language == %r:" % language,
                          "        jump _%s" % target]
        base = next((target for language, target in destinations if language is None), None)
        if base:
            lines.append("    jump _%s" % base)
        else:
            lines.append("    $ raise Exception(%r)" %
                         ("Scene %s is only available in its language/DLC patch" % scene))
        key = "scr/%s.rpy" % scene
        files[key] = "\n".join(lines) + "\n" + files.get(key, "")
    for (scene, name), destinations in entry_routes.items():
        lines = ["label _g_%s_%s:" % (scene, name)]
        for language, target in destinations:
            if language is not None:
                lines += ["    if _preferences.language == %r:" % language,
                          "        jump %s" % target]
        base = next((target for language, target in destinations if language is None), None)
        # Native named lookup falls back to the scene beginning if not found.
        lines.append("    jump %s" % (base or "_%s" % scene))
        files["scr/%s.rpy" % scene] += "\n" + "\n".join(lines) + "\n"
    return files
