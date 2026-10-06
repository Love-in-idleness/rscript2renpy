"""Optional Khime Zero (2001 only), isolated from the main game's resources."""

from pathlib import Path
import re
import wave

from build_port import copy_file, copy_tree, write_scenario
from port_resources import convert_bmp_assets, convert_masks
from khime_tsc import compile_scene, read_tsc

IMAGE_FOLDERS = ("grpe", "grpo", "grpo_bu", "grps")


def check_pcm(path: Path) -> None:
    try:
        with wave.open(str(path)):
            pass
    except wave.Error as error:
        raise ValueError("%s is not PCM WAV; extract OGG with LiarsoftTool first" % path) from error


def prepare_zero(resources: Path, patches) -> str:
    """Check referenced media and compile before touching the destination."""
    source = resources / "scr" / "2001.tsc"
    content = compile_scene(source, patches=patches, zero=True)
    for root in [resources, *(patch for _, patch in patches)]:
        for wav in (root / "bgm").glob("*.WAV"):
            if not wav.with_suffix(".ogg").is_file():
                check_pcm(wav)  # Validate every WAV we will copy, before building.
        script = root / "scr" / "2001.tsc"
        if not script.is_file():
            continue
        tsc = read_tsc(script, "forest")
        required = {"grpo/0001.png", "grpo/0101.png"}
        for item in tsc.instructions():
            op, values = item.opcode, item.operands
            if op == 20:
                required.add("grpe/%04d.png" % values[0])
            elif op == 30:
                layer, number = values[:2]
                folder = ("grpe" if layer < 10 else "grpo" if layer < 20
                          else "grpo_bu" if layer < 30 else "grps")
                required.add("%s/%04d.png" % (folder, number))
            elif op == 62:
                required.add("wav/%04d.ogg" % values[-1])
            elif op == 81 and values[1]:
                required.add("voice/%04d.ogg" % values[1])
            elif op == 60:
                track = "bgm/Track%02d.ogg" % values[0]
                if not any((p / track).is_file() for p in (root, resources)):
                    # Standard PCM WAV is playable as-is. Do not copy wrapped
                    # Ogg-in-WAV; LiarsoftTool must extract it before building.
                    wav = next(((p / track).with_suffix(".WAV") for p in (root, resources)
                                if (p / track).with_suffix(".WAV").is_file()), None)
                    if wav is None:
                        raise FileNotFoundError("Khime Zero BGM missing: " + track)
                    check_pcm(wav)
                else:
                    required.add(track)
        for text in tsc.strings:
            required.update("grps/gf%s.png" % n for n in re.findall(r"\^g(\d{3})", text))
        missing = sorted(name for name in required if not any(
            (p / name).is_file() or (name.endswith(".png") and
                                    (p / name).with_suffix(".bmp").is_file())
            for p in (root, resources)))
        if missing:
            raise FileNotFoundError("Khime Zero converted media missing: " + ", ".join(missing))
    return content


def install_zero(resources: Path, patches, game: Path, content: str, force: bool) -> None:
    # Do not call copy_language_assets: it replaces the *main* language package.
    for root, target in [(resources, game),
                         *((patch, game / "tl" / language) for language, patch in patches)]:
        for folder in IMAGE_FOLDERS:
            output = target / "images" / "khime_zero" / folder
            copy_tree(root / folder, output, {".png", ".xml"}, force)
            convert_bmp_assets(root / folder, output)
            convert_masks(root / folder, output)
        for folder in ("bgm", "wav", "voice"):
            output = target / "khime_zero" / folder
            copy_tree(root / folder, output, {".ogg"}, force)
            if folder == "bgm":
                for wav in (root / folder).glob("*.WAV"):
                    if wav.with_suffix(".ogg").is_file():
                        continue
                    check_pcm(wav)
                    copy_file(wav, output / wav.with_suffix(".wav").name, force)
    write_scenario(content, game / "scenario" / "khime_zero_2001.rpy", resources, force)
