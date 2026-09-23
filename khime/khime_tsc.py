"""Lower Khime's modern CodeX TSC to Ren'Py statements."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "forest"))
from forest_tsc import E, read_tsc  # noqa: E402
from build_forest_rscript import emit_vm, packed  # noqa: E402


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
SUPPORTED_IMAGE_EFFECTS = set(range(9)) | {16} | set(range(20, 29))


def label(scene: str, offset: int) -> str:
    return "_%s_L_%06x" % (scene, offset)


def compile_scene(source: Path) -> str:
    tsc = read_tsc(source, "khime")
    items = tsc.instructions()
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
            lines.append("    return")
        elif op == 12:
            lines.append("    _jump %s" % operands[0])
        elif op == 14:
            count = min(values[0], 5)
            lines.append("    $ khime_choice_prompt = %r" % tsc.string(values[1]))
            lines.append("    menu:")
            for index in range(count):
                text = tsc.string(values[7 + index])
                lines.extend(("        %r:" % text,
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
            if values[3] != 0:
                lines.append("    # Khime conversion: _oload effect %s flattened to 0 "
                             "(not implemented)." % operands[3])
                operands[3] = "0"
            lines.append("    _oload %s %r" %
                         (" ".join(operands[:5]), tsc.string(values[5])))
        elif op in (30, 36):
            effect_index = 4 if op == 30 else 1
            if values[effect_index] not in SUPPORTED_IMAGE_EFFECTS:
                lines.append("    # Khime conversion: _%s effect %s flattened to 0 "
                             "(not implemented)." %
                             (PASSTHROUGH[op], operands[effect_index]))
                operands[effect_index] = "0"
            lines.append("    _%s %s" % (PASSTHROUGH[op], " ".join(operands)))
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
            raw = ((tsc.string(values[4]) + "：") if tsc.string(values[4])
                   else "") + tsc.string(values[5])
            if values[1]:
                lines.append("    _voice %s 0 0 0" % operands[1])
            lines.append("    _khime_say %r" % raw)
        elif op == 82:
            lines.append("    _khime_append %r" % tsc.string(values[4]))
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
            lines.append("    _%s%s" %
                         (PASSTHROUGH[op], " " + " ".join(operands)
                          if operands else ""))
        else:
            raise ValueError("%s: unsupported opcode 0x%04x" % (source, op))
    if tsc.code_size in targets:
        lines.extend(("", "label %s:" % label(scene, tsc.code_size)))
    lines.append("    return")
    return "\n".join(lines) + "\n"
