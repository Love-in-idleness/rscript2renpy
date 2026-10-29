#!/usr/bin/env python3
"""Native BMP/MSK installation; optionally verify LiarsoftTool's producer."""
from pathlib import Path
from tempfile import TemporaryDirectory
import struct
import subprocess
import sys
from PIL import Image
from bmp_fixture import bmp_v4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import validate_resources
from grps_layout import collect_layout, ui_image
from port_resources import RESOURCE_PATTERNS, copy_assets, copy_language_assets


def fails(action, text):
    try:
        action()
    except ValueError as error:
        assert text in str(error), error
    else:
        raise AssertionError("expected rejection: " + text)


def main():
    with TemporaryDirectory(prefix="native-images-") as temporary:
        root = Path(temporary)
        source, project = root / "resources", root / "project"
        folder = source / "grps/tbox01"
        folder.mkdir(parents=True)
        (folder / "back.BMP").write_bytes(bmp_v4())
        (folder / ".meta.xml").write_text(
            '<Canvas><Width>3</Width><Height>1</Height><Items>'
            '<Item x="4" y="5">back</Item></Items></Canvas>')
        Image.new("L", (3, 1), 128).save(source / "grps/ef11.msk", "BMP")
        (source / "scr").mkdir()
        (source / "scr/0000.tsc").write_text(
            ';@gsc-byte-format legacy-28\n;@gsc-schema early\n*end\n')
        validate_resources(source, files=("grps/tbox01/back.png",),
                           patterns=("grps/tbox01/*.png",))
        assert ui_image(folder, "back").name == "back.BMP"
        (folder / "back.png").write_bytes(b"lower-priority fixture")
        (folder / "back.WeBp").write_bytes(b"higher-priority fixture")
        assert ui_image(folder, "back").name == "back.WeBp"
        (folder / "back.png").unlink()
        (folder / "back.WeBp").unlink()
        (folder / "back.BMP").rename(folder / "back.BmP")
        validate_resources(source, patterns=("grps/tbox01/*.png",))
        (folder / "back.BmP").rename(folder / "back.BMP")
        assert collect_layout(source)["tbox01"]["items"]["back"] == (4, 5, 3, 1)
        output = project / "game/grps"
        for _ in range(2):
            copy_assets(source / "grps", RESOURCE_PATTERNS, output, force=False, metadata=True)
            assert (output / "tbox01/back.BMP").read_bytes() == bmp_v4()
            assert not (output / "tbox01/back.png").exists()
            assert (output / "ef11.msk").read_bytes() == (source / "grps/ef11.msk").read_bytes()
        copy_language_assets(source, "fixture", project / "game")
        assert (project / "game/tl/fixture/grps/tbox01/back.BMP").read_bytes() == bmp_v4()
        assert (project / "game/tl/fixture/grps/ef11.msk").is_file()
        stale = output / "tbox01/back.PNG"
        stale.write_bytes(b"old generated PNG")
        fails(lambda: copy_assets(source / "grps", RESOURCE_PATTERNS, output), "obsolete converted PNG")
        assert stale.read_bytes() == b"old generated PNG"
        Image.new("RGB", (3, 1)).save(folder / "back.PNG")
        copy_assets(source / "grps", RESOURCE_PATTERNS, output)
        assert stale.read_bytes() == (folder / "back.PNG").read_bytes()
        raw = root / "raw"
        raw.mkdir()
        pixels = bytes((30, 20, 10, 255, 30, 20, 10, 127, 30, 20, 10, 0))
        codex = (b"BM" + struct.pack("<IHHI", 66, 0, 0, 54) +
                 struct.pack("<IiiHHIIiiII", 40, 3, 1, 1, 32, 0, 12, 0, 0, 0, 0) + pixels)
        bmp = raw / "raw.bmp"
        bmp.write_bytes(codex)
        fails(lambda: copy_assets(raw, ("*.bmp",), root / "raw-out"), "LiarsoftTool --unpack-only")
        assert bmp.read_bytes() == codex
        assert not (root / "raw-out/raw.bmp").exists()
        if len(sys.argv) > 1:
            subprocess.run([sys.argv[1], "--unpack-only", str(bmp)], check=True)
            assert bmp.read_bytes() == bmp_v4()
            copy_assets(raw, ("*.bmp",), root / "raw-out")
            with Image.open(root / "raw-out/raw.bmp") as image:
                assert [image.getpixel((x, 0)) for x in range(3)] == \
                    [(10, 20, 30, alpha) for alpha in (0, 128, 255)]
    print("OK: native BMP/MSK copies, layout, language patches, stale-output and raw-BMP guards")


if __name__ == "__main__":
    main()
