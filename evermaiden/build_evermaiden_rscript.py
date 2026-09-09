#!/usr/bin/env python3
"""Build a Chinese Evermaiden Ren'Py project from unpacked resources."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "forest"))
from forest_tsc import E, read_tsc  # noqa: E402


COMMANDS = {
    10: "hit", 11: "hitc", 13: "wait", 17: "backup",
    20: "gload", 21: "gcls", 22: "gmove", 23: "quake",
    24: "flash", 26: "queue", 27: "action", 28: "update",
    29: "zupdate", 30: "load", 34: "movi", 36: "cls",
    37: "enabl", 38: "locmode", 39: "draw", 40: "depth",
    41: "group", 42: "tbox", 43: "effect", 44: "effectdep",
    45: "tone", 46: "tonedep", 47: "locgrid", 49: "mode",
    50: "backup", 52: "stop", 55: "makesave", 56: "sysmode",
    57: "logflash", 60: "bgm_on", 61: "bgm_off", 62: "se",
    63: "se_on", 64: "se_off", 65: "movie", 66: "voice",
    67: "voice_off", 68: "se_wait", 69: "voice_wait",
    70: "setclk", 71: "setclksys", 72: "resetclk", 73: "click",
    74: "autoreset", 75: "setlink", 83: "txcls", 90: "tboxloc",
    91: "texloc", 92: "tboxback", 93: "cmploc", 94: "tboxcmp",
    95: "texcolor", 96: "texsize", 97: "texfont", 98: "texmode",
    100: "waitloc", 103: "waitlod", 104: "waitcol", 106: "namloc",
    107: "texpich", 108: "texruby", 121: "folder",
    132: "numenable", 200: "insub", 225: "locmap",
}
OPERATORS = {2: "or", 3: "and", 4: "==", 5: ">=", 6: ">",
             7: "<=", 8: "<", 9: "!=", 10: "+", 11: "-",
             12: "*", 13: "//", 14: "%"}


def packed(value: int) -> str:
    depth, raw = divmod(value, 0x10000)
    if not depth:
        return str(raw - 0x10000 if raw & 0x8000 else raw)
    result = str(raw)
    for _ in range(depth):
        result = "_r[%s]" % result
    return result


def vm_source(opcode: int, value: int, left: bool,
              temps: dict[int, str]) -> str:
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


def emit_vm(opcode: int, operands: tuple[int, ...],
            temps: dict[int, str]) -> list[str]:
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


def tsc_text(line: str) -> tuple[str, str]:
    content = line[1:]
    if content.startswith("append "):
        return "", content[7:]
    delimiter = '"："'
    if delimiter not in content:
        return "", content
    return tuple(content.split(delimiter, 1))


def scenario_sources(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.tsc")) if folder.is_dir() else []


def compile_scene(source: Path) -> str:
    tsc = read_tsc(source, ("modern-36",))
    instructions = tsc.instructions()
    scene = source.stem
    targets = {i.operands[0] for i in instructions if i.opcode in (3, 4, 5)}
    for item in instructions:
        if item.opcode == 14:
            targets.update(item.operands[2:2 + min(item.operands[0], 5)])
    lines = ["# Generated from %s." % source.name, "label _%s:" % scene]
    temps: dict[int, str] = {}
    dynamic: list[tuple[str, int]] = []
    dynamic_prompt = ""
    for item in instructions:
        if item.offset in targets:
            lines.extend(("", "label %s:" % scene_label(scene, item.offset)))
        opcode, operands = item.opcode, item.operands
        if opcode & 0xf000:
            lines.extend("    " + line for line in emit_vm(opcode, operands, temps))
        elif opcode == 9:
            temps[operands[0]] = "renpy.random.randrange(0x8000)"
        elif opcode in (3, 4):
            condition = temps.get(0, "0")
            test = "not (%s)" % condition if opcode == 3 else "(%s)" % condition
            lines.extend(("    if %s:" % test,
                          "        jump %s" % scene_label(scene, operands[0])))
        elif opcode == 5:
            lines.append("    jump %s" % scene_label(scene, operands[0]))
        elif opcode == 8:
            lines.append("    _end")
        elif opcode == 12:
            lines.append("    _jump %s" % packed(operands[0]))
        elif opcode == 14:
            count = min(operands[0], 5)
            destination = packed(operands[12])
            lines.append("    menu:")
            for number in range(count):
                caption = tsc.string(operands[7 + number])
                branch = scene_label(scene, operands[2 + number])
                lines.extend(("        %r:" % caption,
                              "            $ _r[%s] = %d" % (destination, number),
                              "            jump %s" % branch))
        elif opcode == 15:
            lines.append("    _gosub " + " ".join(packed(v) for v in operands))
        elif opcode == 16:
            lines.append("    _return %s" % packed(operands[0]))
        elif opcode == 18:
            destination = packed(operands[0])
            for index, value in enumerate(tsc.data(operands[1])):
                lines.append("    $ _r[(%s) + %d] = %d" % (destination, index, value))
        elif opcode == 81:
            edit = tsc.text_edits.get(item.offset)
            if edit:
                name, text = tsc_text(edit)
            else:
                name, text = tsc.string(operands[5]), tsc.string(operands[6])
            value = (name + "：" if name else "") + text
            lines.append("    _say chinese %r" % value)
        elif opcode == 82:
            edit = tsc.text_edits.get(item.offset)
            text = tsc_text(edit)[1] if edit else tsc.string(operands[4])
            lines.append("    _append chinese %r" % text)
        elif opcode == 202:
            lines.append("    $ evermaiden_flagset(%s, %s, %s)" % tuple(
                packed(v) for v in operands))
        elif opcode == 210:
            dynamic_prompt = tsc.string(operands[0])
            dynamic = []
        elif opcode == 211:
            dynamic.append((tsc.string(operands[0]), operands[1]))
        elif opcode == 213:
            lines.append("    $ evermaiden_choice_prompt = %r" % dynamic_prompt)
            lines.append("    menu:")
            for caption, value in dynamic:
                lines.extend(("        %r:" % caption,
                              "            $ _r[%s] = %s" %
                              (packed(operands[1]), packed(value))))
        elif opcode in (32, 35):
            lines.append("    # display setting opcode 0x%04x" % opcode)
        elif opcode in COMMANDS:
            args = " ".join(packed(value) if kind == E else str(value)
                            for kind, value in zip(item.kinds, operands))
            lines.append("    _%s%s" % (COMMANDS[opcode], " " + args if args else ""))
        else:
            lines.append("    # unsupported opcode 0x%04x %s" % (opcode, operands))
    emitted = {item.offset for item in instructions}
    for target in sorted(targets - emitted):
        lines.extend(("", "label %s:" % scene_label(scene, target), "    return"))
    lines.append("    return")
    return "\n".join(lines) + "\n"


GUI = '''init offset = -2
init python:
    gui.init(1280, 720)
define gui.text_font = "fonts/NotoSansCJKsc-Regular.ttf"
define gui.name_text_font = gui.text_font
define gui.text_size = 30
'''


COMPAT = r'''default evermaiden_choice_prompt = ""
default evermaiden_click_links = {}
default evermaiden_click_values = {}
default evermaiden_click_system = {}

init python:
    def evermaiden_flagset(first, last, value):
        for key in range(first, last + 1):
            _r[key] = value

    def evermaiden_image(layer, cg):
        stem = "%04d" % (cg & 0xffff)
        preferred = {
            49: ("grpe", "grpo_ex"),
            47: ("grpo_ef", "grpo_ex"),
            42: ("grpo_cu", "grpo_bu0", "grpo_bu1"),
        }.get(layer, ())
        if 21 <= layer <= 26:
            preferred += ("grpo_bu0", "grpo_bu1", "grpo_cu")
        if layer == 1:
            preferred += ("grpe", "grpo_bg", "grpo", "grpo_ex")
        preferred += ("grpo", "grpo_map", "grpo_ex", "grpo_bg",
                      "grpo_cu", "grpo_bu0", "grpo_bu1", "grpe")
        for folder_name in preferred:
            path = "images/%s/%s.png" % (folder_name, stem)
            if renpy.loadable(path):
                return "%s %s" % (folder_name, stem)
        renpy.log("Evermaiden: missing image layer=%s cg=%s" % (layer, cg))
        return "nothing"

    def evermaiden_voice_file(number):
        if number < 0:
            number += 0x10000
        folder_no, file_no = divmod(number, 10000)
        prefix = "voice/%d/" % folder_no if folder_no else "voice/"
        for suffix in (".ogg", ".wav"):
            path = prefix + "%04d" % file_no + suffix
            if renpy.loadable(path):
                return path
        return None

    def evermaiden_audio_file(folder_name, stem):
        for suffix in (".ogg", ".wav"):
            path = "%s/%s%s" % (folder_name, stem, suffix)
            if renpy.loadable(path):
                return path
        return None

    def evermaiden_system_action(value):
        if value == 0:
            return Quit(confirm=True)
        if value == 1:
            return ShowMenu("save")
        if value == 2:
            return ShowMenu("load")
        if value == 3:
            return ShowMenu("preferences")
        return Return(value)

screen say(who, what):
    window:
        id "window"
        background Solid("#000000b8")
        xpos 0 ypos 535 xsize 1280 ysize 185
        if who:
            text who id "who" font gui.name_text_font size 25 color "#ffffff" xpos 55 ypos 18
        text what id "what" font gui.text_font size 30 color "#ffffff" xpos 220 ypos 18 xsize 1000 line_spacing 7

screen choice(items):
    modal True
    vbox:
        xalign .5 yalign .5 spacing 12
        if evermaiden_choice_prompt:
            text evermaiden_choice_prompt font gui.text_font size 30 color "#ffffff" xalign .5
        for item in items:
            if item.action:
                textbutton item.caption action item.action text_font gui.text_font text_size 28

screen evermaiden_click_screen(options):
    modal True
    for value, system, idle_image, hover_image, xpos, ypos in options:
        imagebutton:
            idle idle_image hover hover_image focus_mask True
            xpos xpos ypos ypos
            action (evermaiden_system_action(value) if system else Return(value))

screen preferences():
    tag menu
    modal True
    key "game_menu" action Return()
    frame:
        xalign .5 yalign .5 padding (40, 30)
        vbox:
            spacing 16
            text "设置" font gui.text_font size 36 xalign .5
            textbutton "返回" action Return() text_font gui.text_font text_size 28

screen save():
    tag menu
    use file_slots("save")
screen load():
    tag menu
    use file_slots("load")
screen file_slots(mode):
    modal True
    frame:
        xalign .5 yalign .5 padding (40, 30)
        vbox:
            spacing 10
            for slot in range(1, 11):
                textbutton ("%02d  " % slot + FileTime(slot, empty="空存档")):
                    action (FileSave(slot) if mode == "save" else FileLoad(slot))
                    text_font gui.text_font text_size 24
            textbutton "返回" action Return() text_font gui.text_font text_size 24

screen confirm(message, yes_action, no_action):
    modal True
    frame:
        xalign .5 yalign .5 padding (40, 30)
        vbox:
            text message font gui.text_font size 28
            hbox:
                spacing 40
                textbutton "确定" action yes_action text_font gui.text_font
                textbutton "取消" action no_action text_font gui.text_font
'''


def copy_tree_files(source: Path, target: Path, suffixes: tuple[str, ...]) -> None:
    for asset in source.rglob("*"):
        if asset.is_file() and asset.suffix.lower() in suffixes:
            output = target / asset.relative_to(source)
            output.parent.mkdir(parents=True, exist_ok=True)
            if (output.is_file() and output.stat().st_size == asset.stat().st_size
                    and output.stat().st_mtime_ns == asset.stat().st_mtime_ns):
                continue
            shutil.copy2(asset, output)


def copy_audio(source: Path, target: Path) -> None:
    """Prefer OGG, retaining WAV only when it has no same-named OGG."""
    for obsolete in target.rglob("*"):
        if obsolete.is_file() and obsolete.suffix.lower() in (".ogg", ".wav") \
                and not obsolete.stem.isascii():
            obsolete.unlink()
    for asset in source.rglob("*.ogg"):
        if not asset.stem.isascii():
            continue
        output = target / asset.relative_to(source)
        output.parent.mkdir(parents=True, exist_ok=True)
        if (output.is_file() and output.stat().st_size == asset.stat().st_size
                and output.stat().st_mtime_ns == asset.stat().st_mtime_ns):
            continue
        shutil.copy2(asset, output)
    for asset in source.rglob("*.wav"):
        if not asset.stem.isascii():
            continue
        relative = asset.relative_to(source)
        if asset.with_suffix(".ogg").is_file():
            duplicate = (target / relative).with_suffix(".wav")
            if duplicate.is_file():
                duplicate.unlink()
            continue
        output = target / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        if (output.is_file() and output.stat().st_size == asset.stat().st_size
                and output.stat().st_mtime_ns == asset.stat().st_mtime_ns):
            continue
        shutil.copy2(asset, output)


def convert_movies(source: Path, target: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is required to convert MPEG movies")
    target.mkdir(parents=True, exist_ok=True)
    for asset in sorted(source.glob("*.mpg")):
        output = target / (asset.stem + ".webm")
        if output.is_file() and output.stat().st_mtime_ns >= asset.stat().st_mtime_ns:
            continue
        temporary = output.with_name(output.stem + ".tmp.webm")
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                        "-i", str(asset), "-c:v", "libvpx-vp9", "-crf", "24",
                        "-b:v", "0", "-c:a", "libvorbis", "-q:a", "5",
                        str(temporary)], check=True)
        temporary.replace(output)


def install_font(game: Path) -> None:
    from fontTools.ttLib import TTCollection
    source = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    if not source.is_file():
        raise FileNotFoundError("NotoSansCJK-Regular.ttc is required")
    target = game / "fonts" / "NotoSansCJKsc-Regular.ttf"
    target.parent.mkdir(parents=True, exist_ok=True)
    collection = TTCollection(source)
    collection.fonts[2].save(target)
    shutil.copy2(Path(__file__).resolve().parents[1] / "forest" / "fonts" /
                 "NotoSans.txt", target.parent / "NotoSans.txt")


def patch_runtime(game: Path) -> None:
    effects = game / "effects.rpy"
    text = effects.read_text(encoding="utf-8").replace(
        'img = "%s %04d" % (folder[layer], cg)',
        'img = evermaiden_image(layer, cg)')
    effects.write_text(text, encoding="utf-8")

    gfx = game / "03_rscript_gfx.rpy"
    text = gfx.read_text(encoding="utf-8").replace(
        'img = "%s %04d" % (folder[args.Layer], args.CGNum)',
        'img = evermaiden_image(args.Layer, args.CGNum)')
    gfx.write_text(text, encoding="utf-8")

    audio = game / "04_rscript_audio.rpy"
    text = audio.read_text(encoding="utf-8")
    text = text.replace('voice_file = "voice/%05d.opus" % args.VoiceNo',
                        'voice_file = evermaiden_voice_file(args.VoiceNo)')
    text = text.replace('        voice(voice_file)',
                        '        if voice_file:\n            renpy.music.play(voice_file, channel="voice", loop=False)')
    text = text.replace('bgm = "bgm/Track%02d.opus" % args.BgmNo',
                        'bgm = evermaiden_audio_file("bgm", "Track%02d" % args.BgmNo)')
    text = text.replace('        renpy.music.play(bgm, channel = "music", fadein = fadein, loop = True, if_changed = True)',
                        '        if bgm:\n            renpy.music.play(bgm, channel = "music", fadein = fadein, loop = True, if_changed = True)')
    text = text.replace('se_file = "wav/%04d.opus" % store.se_queue[args.Channel]',
                        'se_file = evermaiden_audio_file("wav", "%04d" % store.se_queue[args.Channel])')
    text = text.replace('        se_file = [se_file] * (args.Repeat + 1)',
                        '        if not se_file:\n            return\n        loop = args.Repeat == 999\n        se_file = [se_file] if loop else [se_file] * (args.Repeat + 1)')
    text = text.replace('loop = False, fadein = fade, if_changed = False)',
                        'loop = loop, fadein = fade, if_changed = False)')
    text = text.replace('store.se_queue[args.Channel] = args.SeNo',
                        'store.se_queue.extend([0] * max(0, args.Channel + 1 - len(store.se_queue)))\n        store.se_queue[args.Channel] = args.SeNo')
    audio.write_text(text, encoding="utf-8")

    text_runtime = game / "05_rscript_text.rpy"
    text = text_runtime.read_text(encoding="utf-8").replace(
        'renpy.say(who, what, interact = True, show_center = center)',
        'renpy.say(who, what, interact = True)')
    text_runtime.write_text(text, encoding="utf-8")

    command = game / "02_rscript_cmd.rpy"
    text = command.read_text(encoding="utf-8")
    text = text.replace('    def execute_click(o):\n        pass', '''    def execute_click(o):
        options = []
        for layer in sorted(store.evermaiden_click_values):
            if layer not in store.evermaiden_click_links or layer not in store.layer_info:
                continue
            hover, xpos, ypos = store.evermaiden_click_links[layer]
            options.append((store.evermaiden_click_values[layer],
                store.evermaiden_click_system.get(layer, False),
                store.layer_info[layer], evermaiden_image(layer, hover), xpos, ypos))
        if options:
            store._r[0] = renpy.call_screen("evermaiden_click_screen", options=options)
        store.evermaiden_click_links.clear()
        store.evermaiden_click_values.clear()
        store.evermaiden_click_system.clear()''')
    text = text.replace('    def execute_resetclk(o):\n        pass', '''    def execute_resetclk(o):
        store.evermaiden_click_links.clear()
        store.evermaiden_click_values.clear()
        store.evermaiden_click_system.clear()''')
    text = text.replace('    def execute_setclk(o):\n        pass', '''    def execute_setclk(o):
        values = o[0].split()
        if len(values) >= 2:
            layer, value = eval(values[0]), eval(values[1])
            store.evermaiden_click_values[layer] = value
            store.evermaiden_click_system.pop(layer, None)''')
    text = text.replace('    def execute_setclksys(o):\n        pass', '''    def execute_setclksys(o):
        values = o[0].split()
        if len(values) >= 2:
            layer, value = eval(values[0]), eval(values[1])
            store.evermaiden_click_values[layer] = value
            store.evermaiden_click_system[layer] = True''')
    text = text.replace('    def execute_setlink(o):\n        pass', '''    def execute_setlink(o):
        values = o[0].split()
        if len(values) >= 4:
            layer, hover, xpos, ypos = [eval(value) for value in values[:4]]
            store.evermaiden_click_links[layer] = (hover, xpos, ypos)''')
    command.write_text(text, encoding="utf-8")


def validate(root: Path) -> list[Path]:
    required = ("scr", "grpe", "grpo", "grps", "wav", "bgm", "voice", "mov")
    missing = [str(root / name) for name in required if not (root / name).is_dir()]
    sources = scenario_sources(root / "scr")
    if not sources:
        missing.append(str(root / "scr" / "*.tsc"))
    if missing:
        raise FileNotFoundError("missing resources:\n- " + "\n- ".join(missing))
    return sources


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Build the Chinese Evermaiden port")
    parser.add_argument("resources", type=Path)
    parser.add_argument("project", type=Path)
    args = parser.parse_args(argv[1:])
    root, target = args.resources.resolve(), args.project.resolve()
    sources = validate(root)
    game = target / "game"
    scenario = game / "scenario"
    scenario.mkdir(parents=True, exist_ok=True)
    runtime = Path(__file__).resolve().parents[1] / "runtime"
    for source in runtime.glob("*.rpy"):
        if source.name != "screens.rpy":
            shutil.copy2(source, game / source.name)
    patch_runtime(game)
    (game / "gui.rpy").write_text(GUI, encoding="utf-8")
    (game / "evermaiden_compat.rpy").write_text(COMPAT, encoding="utf-8")
    (game / "options.rpy").write_text(
        'define config.name = "Evermaiden 中文版"\n'
        'define config.version = "0.1"\n'
        'define config.has_sound = True\n'
        'define config.has_music = True\n'
        'define config.has_voice = True\n'
        'define config.layers = ["debug", "black", "cg", "master", "flash", '
        '"transient", "screens", "overlay"]\n'
        'define config.check_conflicting_properties = True\n', encoding="utf-8")
    (game / "script.rpy").write_text(
        'label main_menu:\n    return\n\n'
        'label start:\n    scene black\n    call _0000\n    return\n', encoding="utf-8")
    install_font(game)
    image_root = game / "images"
    for name in ("grpe", "grpo", "grpo_bg", "grpo_bu0", "grpo_bu1",
                 "grpo_cu", "grpo_ef", "grpo_ex", "grpo_map", "grps"):
        copy_tree_files(root / name, image_root / name, (".png", ".xml"))
    copy_audio(root / "bgm", game / "bgm")
    copy_audio(root / "wav", game / "wav")
    copy_audio(root / "voice", game / "voice")
    convert_movies(root / "mov", game / "mov")
    for old in scenario.glob("*.rpy*"):
        old.unlink()
    for source in sources:
        (scenario / (source.stem + ".rpy")).write_text(
            compile_scene(source), encoding="utf-8")
    print("Wrote %s: %d Chinese TSC scenes" % (target, len(sources)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
