#!/usr/bin/env python3
"""Assemble the Khime port after its TSC lowerer prepares scenario RPY."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
from build_port import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
