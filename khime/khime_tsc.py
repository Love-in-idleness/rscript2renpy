"""Khime uses the shared modern CodeX lowerer (including its Zero dialect)."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "port_template"))
from modern_tsc import compile_scene, read_tsc, PASSTHROUGH, label  # noqa: E402,F401
