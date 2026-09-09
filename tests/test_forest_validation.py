#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forest"))
import build_forest_rscript as forest_builder  # noqa: E402

validate_inputs = forest_builder.validate_inputs


def main() -> None:
    with TemporaryDirectory() as temporary:
        base = Path(temporary)
        resources = base / "resources"
        for name in ("scr", "grpe", "grpo", "grpo_bg", "grpo_bu",
                     "grpo_ci", "grpo_f", "grps", "wav", "bgm",
                     "voice", "mov"):
            (resources / name).mkdir(parents=True)
        tsc = (
            ";@gsc-structure-v1 size=0 fnv1a64=0\n"
            ";@gsc-byte-format legacy-28\n"
            ";@gsc-text-encoding cp932\n"
            ";@gsc-section header "
            "000000001c0000000000000000000000000000000000000000000000\n"
            ";@gsc-section declaration -\n"
            ";@gsc-section strings -\n"
            ";@gsc-section data-index -\n"
            ";@gsc-section data -\n"
            ";@gsc-structure-end\n")
        (resources / "scr" / "0000.tsc").write_text(tsc, encoding="utf-8")
        for path in (resources / "grpe" / "9001.png",
                     resources / "bgm" / "Track01.ogg",
                     resources / "wav" / "0001.ogg",
                     resources / "voice" / "0001.ogg",
                     resources / "mov" / "0001.webm",
                     resources / "mov" / "0002.mpg"):
            path.write_bytes(b"fixture")
        validate_inputs(resources)
        project = base / "project"
        with patch.object(forest_builder, "copy_assets"), \
                patch.object(forest_builder, "convert_masks"), \
                patch.object(forest_builder, "convert_movies"):
            forest_builder.main(["build_forest_rscript.py",
                                 str(resources), str(project)])
        gui = project / "game" / "gui.rpy"
        gui_text = gui.read_text(encoding="utf-8")
        assert "gui.init(800, 600)" in gui_text
        assert '"fonts/NotoSansCJKjp-Regular.otf"' in gui_text
        (resources / "scr" / "0000.tsc").unlink()
        (resources / "scr" / "0000.gsc").write_bytes(b"not accepted")
        try:
            validate_inputs(resources)
        except FileNotFoundError as error:
            assert "scr/*.tsc" in str(error)
        else:
            raise AssertionError("GSC-only input was accepted")
        (resources / "scr" / "0000.gsc").unlink()
        (resources / "scr" / "0000.tsc").write_text(tsc, encoding="utf-8")
        (resources / "voice" / "0001.ogg").unlink()
        try:
            validate_inputs(resources)
        except FileNotFoundError as error:
            assert "voice/*.ogg" in str(error)
        else:
            raise AssertionError("missing converted voice was accepted")
    print("OK: Forest input validation")


if __name__ == "__main__":
    main()
