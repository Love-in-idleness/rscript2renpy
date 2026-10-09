"""Cannonball.exe native UI profile, independently usable without the EXE."""
from pathlib import Path
from PIL import Image
from grps_layout import UI_ACTIONS
from exe_ui import constant_positions, inspect_exe

EXE_SHA256 = "df4b5b6dffc7002370d0772869baaba551b08fca970e92609ca64b08174f89ba"
# Constructor 405f..407260, objects' SetPos calls 40621e..406fe3.
BUTTONS = {
    "scm_ful": ("con_01a", 0x7c, 202, 7), "scm_wnd": ("con_01b", 0x80, 356, 7),
    "bgm_on": ("con_02a", 0x84, 202, 39), "bgm_off": ("con_02b", 0x88, 356, 39),
    "voc_on": ("con_03a", 0x8c, 202, 103), "voc_off": ("con_03b", 0x90, 356, 103),
    "sef_on": ("con_04a", 0x94, 202, 167), "sef_off": ("con_04b", 0x98, 356, 167),
    "gef_on": ("con_05a", 0x9c, 202, 231), "gef_off": ("con_05b", 0xa0, 356, 231),
    "msp_slw": ("con_07a", 0xac, 202, 263), "msp_nom": ("con_07b", 0xb0, 295, 263),
    "msp_now": ("con_07c", 0xb4, 388, 263),
    "msk_on": ("con_08a", 0xb8, 202, 295), "msk_off": ("con_08b", 0xbc, 356, 295),
    "save": ("con_14", 0x6c, 157, 330), "load": ("con_15", 0x68, 272, 330),
    "close": ("con_10", 0x64, 121, 356), "title": ("con_11", 0x60, 219, 356),
    "exit": ("con_12", 0x5c, 317, 356),
}
# Callback wiring: 40b662..40b70a -> 40c230..40c310 -> 40f91f..40f97d.
PANE = (("rev", "tbox_c02"), ("bak", "tbox_c03"), ("fow", "tbox_c04"),
        ("next", "tbox_c05"), ("voc", "tbox_c06"), (None, "tbox_c09"),
        (None, "tbox_c10"), ("hide", "tbox_c07"))
# Save-page constructor 4092a0..409902; ten slots at 409460..4094ce.
SAVE_BUTTONS = {"exit": ("dat_re", 653, 503),
                "prev": ("dat_p01", 510, 499), "next": ("dat_p02", 577, 499)}


def native_layouts(resources, positions=None):
    resources = Path(resources)
    files = {p.stem.lower(): p for p in (resources / "grps").iterdir() if p.suffix.lower() == ".png"}
    files.update({p.stem.lower(): p for p in (resources / "grps").iterdir() if p.suffix.lower() == ".webp"})
    layouts = {name: {"items": {}, "images": {}, "controls": {}}
               for name in ("confscrn", "compane", "savescrn", "saveconf")}

    def add(folder, name, source, x, y, states=1):
        path = files.get(source)
        if path is None:
            raise FileNotFoundError("converted native UI image missing: grps/" + source)
        with Image.open(path) as image:
            width, height = image.size
        if height % states:
            raise ValueError("native UI atlas height is not divisible by %d: %s" % (states, path))
        height //= states
        layout = layouts[folder]
        for state in range(states):
            key = name + ("_f" if state == 1 else "_%d" % state if state else "")
            layout["items"][key] = (x, y, width, height)
            layout["images"][key] = (str(path.relative_to(resources)), (0, state * height, width, height) if states > 1 else None)
        if name in UI_ACTIONS.get(folder, {}):
            layout["controls"][name] = UI_ACTIONS[folder][name]
        return width, height

    layouts["confscrn"]["size"] = add("confscrn", "bg", "con_base", 0, 0)
    for name, (source, field, x, y) in BUTTONS.items():
        if positions is not None:
            x, y = positions[field]
        add("confscrn", name, source, x, y, 2)
    # 428540 consumes full track length, subtracting the thumb width (428640).
    for prefix, source, y in (("bgm", "con_16", 71), ("voc", "con_17", 135), ("sef", "con_18", 199)):
        _, height = add("confscrn", prefix + "_vol", source, 234, y, 2)
        layouts["confscrn"]["items"][prefix + "_lev"] = (234, y, 231, height)
    layouts["compane"]["size"] = add("compane", "bg", "tbox_c01", 0, 0)
    add("compane", "slide", "tbox_c08", 4, 2, 2)
    layouts["compane"]["items"]["slide_lev"] = (4, 2, 75, 15)
    x = 87  # 40b220: slider present -> 4 + 83; without slider -> 4.
    for name, source in PANE:
        if name is not None:
            width, _ = add("compane", name, source, x, 1, 2)
        elif source in files:
            raise ValueError("native optional control %s needs callback verification before binding" % source)
        else:
            width = 0  # Native loader's missing optional image has width zero.
        x += width + 1
    layouts["savescrn"]["size"] = add("savescrn", "bg_save", "dat_bgs", 0, 0)
    if add("savescrn", "bg_load", "dat_bgl", 0, 0) != layouts["savescrn"]["size"]:
        raise ValueError("native save/load canvases differ")
    for name, (source, x, y) in SAVE_BUTTONS.items():
        add("savescrn", name, source, x, y, 2)
    # Native pages are 0..9; the Ren'Py page names are 1..10.
    add("savescrn", "number", "dat_no", 545, 499, 10)
    images = layouts["savescrn"]["images"]
    number_source, crop = images["number"]
    for index in range(10):
        images["page%d" % (index + 1)] = (number_source, (0, index * crop[3], crop[2], crop[3]))
    layouts["savescrn"]["page_wrap"] = False
    for index in range(10):
        layouts["savescrn"]["items"][str(index)] = (
            125 + (index // 5) * 275, 137 + (index % 5) * 67, 255, 60)
    # Slot constructor 402150: DT1 at (0,0), timestamp at (110,40), 16px white.
    layouts["saveconf"].update(items={"thmb": (0, 0, 255, 60), "date": (110, 40)},
                               date_size=16, date_outlines=[], date_format="%Y/%m/%d %H:%M")
    return layouts


def extract_native_ui(exe, resources):
    report, strings, instructions = inspect_exe(exe, resources)
    # shortcut: unknown builds only report references; verify a new profile before extracting geometry.
    if report["sha256"] != EXE_SHA256:
        report["unresolved"].append("Unsupported EXE build: resource references only; no assumed geometry/actions")
        return report
    positions = constant_positions(instructions, 0x405f00, 0x407000)
    for source, field, x, y in BUTTONS.values():
        if field not in positions or positions[field] != (x, y):
            raise ValueError("EXE SetPos extraction disagrees with verified profile: " + source)
    report["layouts"] = native_layouts(resources, positions)
    report["profile"] = "cannonball-pe32-native-ui"
    report["unresolved"] = ["CON_06 is present in resources but is not loaded by the native menu constructor",
                            "TBOX_C09/C10 are referenced optional controls without converted images",
                            "Original backlog presentation is not yet ported"]
    bound = {Path(path).stem.lower() for layout in report["layouts"].values()
             for path, crop in layout["images"].values()}
    report["unbound_resource_references"] = sorted(set(report["resource_references"]) - bound)
    return report
