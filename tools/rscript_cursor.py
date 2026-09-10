"""Extract the first Windows cursor resource from a game executable."""

from io import BytesIO
from pathlib import Path
import shutil
import struct
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image


def _wrestool(executable: Path, resource_type: int, output: Path,
              name: int | None = None) -> list[Path]:
    tool = shutil.which("wrestool")
    if not tool:
        raise RuntimeError("wrestool is required to extract the game cursor")
    command = [tool, "-x", "-R", "-t", str(resource_type)]
    if name is not None:
        command.extend(("-n", str(name)))
    command.extend(("-o", str(output), str(executable)))
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(error.stderr.strip() or "wrestool failed") from error
    return sorted(path for path in output.iterdir() if path.is_file())


def extract_cursor(executable: Path, target: Path) -> tuple[int, int]:
    """Extract the first RT_GROUP_CURSOR as PNG and return its hotspot."""
    executable = Path(executable)
    target = Path(target)
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        groups = root / "groups"
        images = root / "images"
        groups.mkdir()
        images.mkdir()
        group_files = _wrestool(executable, 12, groups)
        if not group_files:
            raise RuntimeError("executable has no cursor group")
        group = group_files[0].read_bytes()
        if len(group) < 20 or struct.unpack_from("<HHH", group)[:2] != (0, 2):
            raise RuntimeError("malformed cursor group")
        width, height, _, _, size, resource_id = struct.unpack_from(
            "<HHHHIH", group, 6)
        cursor_files = _wrestool(executable, 1, images, resource_id)
        if len(cursor_files) != 1:
            raise RuntimeError("cursor group does not resolve to one image")
        raw = cursor_files[0].read_bytes()
        if len(raw) != size or len(raw) < 5:
            raise RuntimeError("malformed cursor image")
        hotspot = struct.unpack_from("<HH", raw)
        dib = raw[4:]
        cursor = struct.pack(
            "<HHHBBBBHHII", 0, 2, 1, width % 256,
            (height // 2) % 256, 0, 0, *hotspot, len(dib), 22) + dib
        target.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(BytesIO(cursor)) as image:
            image.convert("RGBA").save(target)
    return hotspot
