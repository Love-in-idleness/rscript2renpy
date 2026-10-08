"""Read CodeX canvas metadata for reusable Ren'Py menu layouts."""

from pathlib import Path
import struct
import xml.etree.ElementTree as ET

# Native names shared by CodeX archives. Metadata supplies geometry, not actions.
UI_ACTIONS = {
    "compane": {name: (action,) for name, action in (
        ("rev", "choice_back"), ("bak", "rollback"), ("fow", "rollforward"),
        ("next", "fast_skip"), ("skip", "skip"), ("auto", "auto"),
        ("hide", "hide"), ("voc", "voice"), ("save", "save"),
        ("load", "load"), ("qsave", "quick_save"), ("qload", "quick_load"),
        ("menu", "preferences"))},
    "confscrn": {
        **{name: ("preference", setting, value) for name, setting, value in (
            ("scm_ful", "display", "fullscreen"), ("scm_wnd", "display", "window"),
            ("bgm_on", "music mute", "disable"), ("bgm_off", "music mute", "enable"),
            ("sef_on", "sound mute", "disable"), ("sef_off", "sound mute", "enable"),
            ("voc_on", "voice mute", "disable"), ("voc_off", "voice mute", "enable"),
            ("msp_slw", "text speed", 25), ("msp_nom", "text speed", 75),
            ("msp_now", "text speed", 0), ("msk_on", "skip", "all"),
            ("msk_off", "skip", "seen"),
            # bgr names describe background playback: off.png says Silent ON.
            ("bgr_on", "audio when unfocused", "enable"),
            ("bgr_off", "audio when unfocused", "disable"))},
        "gef_on": ("effects", True), "gef_off": ("effects", False),
        # Native off.png says stop on click; on.png says keep playing.
        "vocst_on": ("voice_stop", False), "vocst_off": ("voice_stop", True),
        "font": ("fonts",), "save": ("save",), "load": ("load",),
        "close": ("close",), "title": ("title",), "exit": ("quit",),
    },
}


def collect_layout(resources: Path, fallback: Path | None = None) -> dict:
    layouts = {}
    root = resources / "grps"
    choices = []
    for prefix in ("sel_a", "sel_q"):
        choices.extend(path.name for path in sorted(root.glob(prefix + "*"))
                       if (path / "body.png").is_file())
    textboxes = [path.name for path in sorted(root.glob("tbox*"))
                 if (path / "back.png").is_file()]
    required = {"confscrn", "compane", "savescrn", *choices, *textboxes}
    folders = required | {str(path.parent.relative_to(root)) for path in root.rglob(".meta.xml")}
    for folder in sorted(folders):
        source = resources / "grps" / folder
        if not source.is_dir():
            continue
        metadata = source / ".meta.xml"
        if not metadata.is_file():
            if any(source.glob("*.png")):
                raise ValueError("%s needs .meta.xml to position its UI assets" % source)
            continue
        canvas = ET.parse(metadata).getroot()
        items = {}
        for item in canvas.findall("./Items/Item"):
            if item.get("empty") == "1":
                continue
            name = (item.text or "").strip()
            image = source / (name + ".png")
            if not image.is_file() and fallback is not None:
                image = fallback / "grps" / folder / (name + ".png")
            if not image.is_file():
                continue
            with image.open("rb") as stream:
                header = stream.read(24)
            if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
                raise ValueError("invalid UI PNG: %s" % image)
            width, height = struct.unpack(">II", header[16:24])
            items[name] = (int(item.get("x")), int(item.get("y")), width, height)
        layouts[folder] = {
            "size": (int(canvas.findtext("Width")), int(canvas.findtext("Height"))),
            "items": items,
        }
        if folder in UI_ACTIONS:
            layouts[folder]["controls"] = {name: spec for name, spec in UI_ACTIONS[folder].items() if name in items}
            unhandled = sorted(name for name in items if name not in UI_ACTIONS[folder]
                               and name not in {"bg", "slide", "font_txt", "fontwnd"}
                               and not name.endswith(("_f", "_c", "_lev", "_vol"))
                               and not (name.endswith("_off") and name[:-4] in UI_ACTIONS[folder]))
            if unhandled:
                layouts[folder]["unhandled"] = unhandled
                print("WARNING: unbound UI controls in %s: %s" % (source, ", ".join(unhandled)))
    return layouts
