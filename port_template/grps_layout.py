"""Read CodeX canvas metadata for reusable Ren'Py menu layouts."""

from pathlib import Path
import struct
import xml.etree.ElementTree as ET


def collect_layout(resources: Path) -> dict:
    layouts = {}
    root = resources / "grps"
    choices = []
    for prefix in ("sel_a", "sel_q"):
        choices.extend(path.name for path in sorted(root.glob(prefix + "*"))
                       if (path / "body.png").is_file())
    textboxes = [path.name for path in sorted(root.glob("tbox*"))
                 if (path / "back.png").is_file()]
    for folder in ("confscrn", "compane", "savescrn", *choices, *textboxes):
        source = resources / "grps" / folder
        if not source.is_dir() or not any(source.glob("*.png")):
            continue
        metadata = source / ".meta.xml"
        if not metadata.is_file():
            raise ValueError("%s needs .meta.xml to position its UI assets" % source)
        canvas = ET.parse(metadata).getroot()
        items = {}
        for item in canvas.findall("./Items/Item"):
            if item.get("empty") == "1":
                continue
            name = (item.text or "").strip()
            image = source / (name + ".png")
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
    return layouts
