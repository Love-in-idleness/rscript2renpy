"""Lower Khime's modern CodeX TSC to Ren'Py statements."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "port_template"))
from rscript_tsc import E, STRING_OPERANDS, read_tsc  # noqa: E402
from tsc_vm import emit_vm, packed  # noqa: E402
from tsc_patches import language_patch_data, instruction_strings, menu_text  # noqa: E402


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
KHIME_COMMANDS = {
    48: "face", 101: "faceloc", 105: "facedep", 130: "numload",
    131: "numreng", 134: "numloc", 135: "numset", 136: "num",
    70: "setclk", 71: "setclksys", 72: "resetclk", 73: "click",
    75: "setlink", 38: "locmode",
}


def label(scene: str, offset: int) -> str:
    return "_%s_L_%06x" % (scene, offset)


def compile_scene(source: Path, patches=()) -> str:
    tsc = read_tsc(source, "khime")
    items = tsc.instructions()
    patch_texts = {}
    patch_insertions = {}
    patch_operands = {}
    for language, directory in patches:
        path = directory / "scr" / source.name
        if not path.is_file():
            continue  # A partial language patch falls back to original text.
        texts, additions, overrides = language_patch_data(
            source.parent, directory / "scr", dialect="khime",
            override_opcodes=set(PASSTHROUGH) - {20, 65},
            menu_transform=menu_text,
            source_names={source.name})
        patch_texts[language] = texts.get(source.name, {})
        patch_insertions[language] = additions.get(source.name, {})
        patch_operands[language] = overrides.get(source.name, {})

    def text(item, index):
        original = tsc.string(item.operands[index])
        if item.opcode == 14:
            original = menu_text(original)
        kind = ({14: {1: "prompt"}, 32: {5: "oload"},
                 82: {4: "append"}}.get(item.opcode, {}).get(index)
                or "choice%d" % (index - 7))
        values = {language: mapping[(item.offset, kind)]
                  for language, mapping in patch_texts.items()
                  if (item.offset, kind) in mapping}
        return ("%r.get(_preferences.language, %r)" % (values, original)
                if values else repr(original))
    scene = source.stem
    targets = {item.operands[0] for item in items if item.opcode in (3, 4, 5, 200)}
    for item in items:
        if item.opcode == 14:
            targets.update(item.operands[2:2 + min(item.operands[0], 5)])
    boundaries = {item.offset for item in items} | {tsc.code_size}
    if targets - boundaries:
        raise ValueError("%s: non-instruction target %s" %
                         (source, sorted(targets - boundaries)))

    lines = ["# Generated from %s; offsets preserved in labels." % source.name,
             "label _%s:" % scene]
    temps = {}
    pending_se = None
    for item in items:
        for language, additions in patch_insertions.items():
            if item.offset in additions:
                lines.append("    if _preferences.language == %r:" % language)
                lines.extend("        " + command for command in additions[item.offset])
        if item.offset in targets:
            lines.extend(("", "label %s:" % label(scene, item.offset)))
        op, values = item.opcode, item.operands
        operands = [packed(value) if kind == E else str(value)
                    for kind, value in zip(item.kinds, values)]
        if op & 0xf000:
            lines.extend("    " + line for line in emit_vm(op, values, temps))
        elif op == 9:
            temps[values[0]] = "renpy.random.randrange(0x8000)"
        elif op in (3, 4):
            condition = temps.get(0, "0")
            test = "not (%s)" % condition if op == 3 else "(%s)" % condition
            lines.extend(("    if %s:" % test,
                          "        jump %s" % label(scene, values[0])))
        elif op == 5:
            lines.append("    jump %s" % label(scene, values[0]))
        elif op == 8:
            # KhimeDL_CHS.exe 0x41fe3c -> 0x420e66 exits the interpreter,
            # not a gosub frame (opcode 16). Do not resume the caller's story.
            lines.append("    _end")
        elif op == 12:
            lines.append("    _jump %s" % operands[0])
        elif op == 14:
            count = min(values[0], 5)
            lines.append("    $ khime_choice_prompt = %s" % text(item, 1))
            captions = [text(item, 7 + index) for index in range(count)]
            for index, caption in enumerate(captions):
                if patch_texts:
                    lines.append("    $ khime_menu_caption_%d = %s" % (index, caption))
            lines.append("    menu:")
            for index in range(count):
                caption = (repr("[khime_menu_caption_%d]" % index)
                           if patch_texts else captions[index])
                lines.extend(("        %s:" % caption,
                              "            $ _r[%s] = %d" % (operands[12], index),
                              "            $ khime_choice_prompt = None",
                              "            jump %s" % label(scene, values[2 + index])))
        elif op == 15:
            name = operands[0] + (("%" + tsc.string(values[1]))
                                  if tsc.string(values[1]) else "")
            lines.append("    _gosub %s %s" % (name, " ".join(operands[2:])))
        elif op == 16:
            lines.append("    _return %s" % operands[0])
        elif op == 18:
            data = tsc.data(values[1])
            lines.append("    _data %s %s" %
                         (operands[0], " ".join(map(str, data))))
        elif op == 32:
            lines.append("    _oload %s %s" %
                         (" ".join(operands[:5]), text(item, 5)))
        elif op == 62:
            pending_se = operands[-1]
        elif op == 63:
            if pending_se is not None:
                lines.append("    _se 0 %s" % pending_se)
                pending_se = None
            lines.append("    _se_on 0 %s" % " ".join(operands[-3:]))
        elif op == 64:
            lines.append("    _se_off 0 %s" % operands[-1])
        elif op == 81:
            original = instruction_strings(tsc, item)["say"]
            translated = {language: mapping[(item.offset, "say")]
                          for language, mapping in patch_texts.items()
                          if (item.offset, "say") in mapping}
            raw = ("%r.get(_preferences.language, %r)" % (translated, original)
                   if translated else repr(original))
            if values[1]:
                lines.append("    _voice %s 0 0 0" % operands[1])
            lines.append("    _khime_say %s" % raw)
        elif op == 82:
            lines.append("    _khime_append %s" % text(item, 4))
        elif op == 120:
            lines.append("    _osize %s" % " ".join(operands))
        elif op == 121:
            lines.append("    _khime_folder %s %r" %
                         (operands[0], tsc.string(values[1])))
        elif op == 200:
            lines.append("    _insub L_%06x %s" %
                         (values[0], " ".join(operands[1:])))
        elif op in KHIME_COMMANDS:
            lines.append("    _khime_%s %s" %
                         (KHIME_COMMANDS[op], " ".join(operands)))
        elif op in PASSTHROUGH:
            def statement(parameters):
                args = [packed(value) if kind == E else str(value)
                        for kind, value in zip(item.kinds, parameters)]
                return "_%s%s" % (PASSTHROUGH[op], " " + " ".join(args) if args else "")
            overrides = {language: mapping[item.offset]
                         for language, mapping in patch_operands.items()
                         if item.offset in mapping}
            for index, (language, parameters) in enumerate(overrides.items()):
                lines.extend(("    %s _preferences.language == %r:" %
                              ("if" if index == 0 else "elif", language),
                              "        " + statement(parameters)))
            if overrides:
                lines.append("    else:")
            lines.append(("        " if overrides else "    ") + statement(values))
        else:
            raise ValueError("%s: unsupported opcode 0x%04x" % (source, op))
    for language, additions in patch_insertions.items():
        if tsc.code_size in additions:
            lines.append("    if _preferences.language == %r:" % language)
            lines.extend("        " + command for command in additions[tsc.code_size])
    if tsc.code_size in targets:
        lines.extend(("", "label %s:" % label(scene, tsc.code_size)))
    lines.append("    return")
    return "\n".join(lines) + "\n"
