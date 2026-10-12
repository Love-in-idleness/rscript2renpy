"""File-level installation only; a failed build is not a project transaction."""

from contextlib import contextmanager
import os
from pathlib import Path
import secrets
import shutil
import stat


def reject_overlap(source: Path, output: Path) -> None:
    output = output.resolve()
    pending, visited = [source], set()
    while pending:
        directory = pending.pop().resolve()
        if directory == output or directory.is_relative_to(output) or output.is_relative_to(directory):
            raise ValueError("resource input and output project overlap: %s / %s" % (directory, output))
        if directory in visited or not directory.is_dir():
            continue
        visited.add(directory)
        # Check links before any output cleanup; visited also bounds directory-link cycles.
        with os.scandir(directory) as entries:
            pending.extend(Path(entry.path) for entry in entries
                           if entry.is_symlink() or entry.is_dir(follow_symlinks=False))


def files_equal(source: Path, target: Path) -> bool:
    if source.stat().st_size != target.stat().st_size:
        return False
    with source.open("rb") as left, target.open("rb") as right:
        while True:
            block = left.read(64 * 1024)
            if block != right.read(64 * 1024):
                return False
            if not block:
                return True


@contextmanager
def atomic_output(destination: Path):
    destination = Path(destination)
    if destination.is_symlink():
        destination = destination.resolve(strict=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    mode = None
    if destination.exists():
        status = destination.stat()
        if not stat.S_ISREG(status.st_mode) or not status.st_mode & 0o222:
            raise PermissionError("cannot write file: %s" % destination)
        # Replacement must not bypass the existing file's write permissions.
        probe = os.open(destination, os.O_WRONLY | getattr(os, "O_BINARY", 0))
        os.close(probe)
        mode = stat.S_IMODE(status.st_mode)
    while True:
        temporary = destination.parent / (".rscript-" + secrets.token_hex(12) + ".tmp")
        try:
            fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         getattr(os, "O_BINARY", 0), 0o666)
            break
        except FileExistsError:
            continue
    try:
        # Use the exclusively created descriptor, with a path-valued .name for copystat.
        with open(temporary, "wb", opener=lambda _path, _flags: fd) as output:
            fd = -1
            if mode is not None:
                os.chmod(temporary, mode)
            yield output
            output.flush()
        if not destination.exists() or not files_equal(temporary, destination):
            # os.replace does not fall back to a cross-volume copy on Windows.
            os.replace(temporary, destination)
    finally:
        if fd >= 0:
            os.close(fd)
        if temporary.exists():
            if os.name == "nt":
                temporary.chmod(stat.S_IWRITE | stat.S_IREAD)
            temporary.unlink()


def clear_script_cache(path: Path) -> None:
    if path.suffix == ".rpy":
        path.with_suffix(".rpyc").unlink(missing_ok=True)


def copy_file(source: Path, target: Path, force: bool = False, *, metadata=True) -> bool:
    if target.exists() and source.samefile(target):
        return False
    if target.exists():
        if files_equal(source, target):
            if metadata:
                shutil.copystat(source, target)
            clear_script_cache(target)
            return False
        if not force:
            raise FileExistsError("refusing to overwrite different file: %s" % target)
    with source.open("rb") as input_file, atomic_output(target) as output:
        if metadata:
            # A private copy2 source must not be readable in a wider-mode temporary file.
            os.chmod(output.name, stat.S_IMODE(source.stat().st_mode))
        shutil.copyfileobj(input_file, output)
        if metadata:
            output.flush()
            shutil.copystat(source, output.name)
    clear_script_cache(target)
    return True


def write_text(content: str, destination: Path, force: bool = False) -> bool:
    if destination.exists():
        try:
            identical = destination.read_text(encoding="utf-8") == content
        except UnicodeDecodeError:
            if not force:
                raise
            identical = False
        if identical:
            clear_script_cache(destination)
            return False
        if not force:
            raise FileExistsError("refusing to overwrite different file: %s" % destination)
    with atomic_output(destination) as output:
        output.write(content.replace("\n", os.linesep).encode("utf-8"))
    clear_script_cache(destination)
    return True
