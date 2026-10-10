#!/usr/bin/env python3
"""Check the generated Kagerou engine in a disposable SDK command project."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: run_kagerou_port.py PROJECT RENPY_SDK')
    source, sdk = (Path(p).resolve() for p in sys.argv[1:])
    with TemporaryDirectory(prefix='kagerou-sdk-') as directory:
        project = Path(directory)
        game = project / 'game'
        game.mkdir()
        shutil.copytree(source / 'game/engine', game / 'engine',
                        ignore=shutil.ignore_patterns('*.rpyc', '__pycache__'))
        for folder in ('fonts', 'gui', 'scr', 'tl', 'grpe', 'grpo', 'grpo_bu',
                       'grps', 'bgm', 'voice', 'wav', 'mov'):
            path = source / 'game' / folder
            if path.exists():
                (game / folder).symlink_to(path, target_is_directory=True)
        shutil.copy2(Path(__file__).with_name('renpy_kagerou_port.rpy'), game / 'kagerou_test.rpy')
        subprocess.run([str(sdk / 'renpy.sh'), str(project), 'kageroutest',
                        '--savedir', str(project / 'test-saves')], check=True,
                       env=os.environ | {'RENPY_PATH_TO_SAVES': str(project / 'sdk-saves')})


if __name__ == '__main__':
    main()
