#!/usr/bin/env python3
"""Safe-install failure tests use disposable files, never game resources."""

import os
from pathlib import Path
import stat
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "port_template"))
import file_install
from build_port import assemble_port, install_base
from port_resources import copy_language_assets


def reject(operation, kind=OSError):
    try:
        operation()
    except kind:
        return
    raise AssertionError("expected operation to fail")


def main():
    with TemporaryDirectory(prefix="rscript-install-") as temporary:
        root = Path(temporary)
        source, target = root / "source", root / "目标.rpy"
        source.write_bytes(b"new")
        target.write_bytes(b"old")
        target.chmod(0o604)
        cache = target.with_suffix(".rpyc")
        cache.write_bytes(b"old cache")
        old_time = target.stat().st_mtime_ns

        def intact():
            assert target.read_bytes() == b"old"
            assert target.stat().st_mtime_ns == old_time
            assert cache.read_bytes() == b"old cache"
            assert not list(root.glob(".rscript-*.tmp"))

        def partial_copy(input_file, output):
            output.write(b"partial")
            raise OSError("simulated write failure")

        with patch.object(file_install.shutil, "copyfileobj", side_effect=partial_copy):
            reject(lambda: file_install.copy_file(source, target, force=True))
        intact()
        with patch.object(file_install.os, "replace", side_effect=OSError("simulated replacement failure")):
            reject(lambda: file_install.write_text("replacement", target, force=True))
        intact()

        real_open = open
        for fault in ("flush", "close"):
            class FailingFile:
                def __init__(self, *args, **kwargs):
                    self.file = real_open(*args, **kwargs)
                def __getattr__(self, name):
                    return getattr(self.file, name)
                def __enter__(self):
                    return self
                def flush(self):
                    if fault == "flush":
                        raise OSError("simulated flush failure")
                    self.file.flush()
                def __exit__(self, *args):
                    self.file.close()
                    if fault == "close":
                        raise OSError("simulated close failure")
            with patch.object(file_install, "open", FailingFile, create=True):
                reject(lambda: file_install.write_text("replacement", target, force=True))
            intact()

        target.chmod(0o444)
        reject(lambda: file_install.copy_file(source, target, force=True), PermissionError)
        intact()
        target.chmod(0o604)
        file_install.write_text("中文\n", target, force=True)
        assert target.read_bytes() == ("中文" + os.linesep).encode("utf-8")
        assert stat.S_IMODE(target.stat().st_mode) == 0o604 and not cache.exists()
        source.chmod(0o640)
        os.utime(source, ns=(1234567890000000000, 1234567890000000000))
        file_install.copy_file(source, target, force=True)
        assert target.read_bytes() == b"new"
        assert stat.S_IMODE(target.stat().st_mode) == stat.S_IMODE(source.stat().st_mode)
        assert target.stat().st_mtime_ns == source.stat().st_mtime_ns
        if os.name != "nt":
            link = root / "link"
            link.symlink_to(target)
            file_install.write_text("through symlink", link, force=True)
            assert link.is_symlink() and target.read_text() == "through symlink"

        resources = root / "resources"
        resources.mkdir()
        sentinel = resources / "input"
        sentinel.write_bytes(b"preserved")
        for output in (resources, resources / "project", root):
            reject(lambda: install_base(resources, output, force=True), ValueError)
            reject(lambda: assemble_port(resources, output, {"scr/0000.rpy": "pass"},
                                         ROOT / "forest", force=True), ValueError)
            assert sentinel.read_bytes() == b"preserved"
        project = root / "project"
        patch_root = project / "language-input"
        patch_root.mkdir(parents=True)
        reject(lambda: assemble_port(resources, project, {"scr/0000.rpy": "pass"},
                                     ROOT / "forest", patches=[("zh", patch_root)],
                                     force=True), ValueError)
        assert not (project / "game").exists()
        game = project / "game"
        package = game / "tl/zh"
        package.mkdir(parents=True)
        (package / "keep").write_text("preserved")
        reject(lambda: copy_language_assets(package, "zh", game), ValueError)
        assert (package / "keep").read_text() == "preserved"
        if os.name != "nt":
            alias = root / "resource-alias"
            alias.symlink_to(resources, target_is_directory=True)
            reject(lambda: file_install.reject_overlap(alias, resources / "project"), ValueError)
    print("OK: atomic copy/text failures, metadata, permissions and overlap checks")


if __name__ == "__main__":
    main()
