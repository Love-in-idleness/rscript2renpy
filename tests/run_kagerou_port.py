#!/usr/bin/env python3
"""Check the generated Kagerou engine in a disposable SDK command project."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import wave
from PIL import Image


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit('usage: run_kagerou_port.py PROJECT RENPY_SDK [CAPTURE_DIRECTORY]')
    source, sdk = (Path(p).resolve() for p in sys.argv[1:3])
    with TemporaryDirectory(prefix='kagerou-sdk-') as directory:
        project = Path(directory)
        game = project / 'game'
        game.mkdir()
        shutil.copytree(source / 'game/engine', game / 'engine',
                        ignore=shutil.ignore_patterns('*.rpyc', '__pycache__'))
        for folder in ('fonts', 'gui', 'scr', 'tl', 'grpe', 'grpo', 'grpo_bu', 'grpo_ex', 'grpo_cut',
                       'grps', 'bgm', 'voice', 'wav', 'mov'):
            path = source / 'game' / folder
            if path.exists():
                # SDK compilation must not share the real project's .rpyc files.
                if folder in ('scr', 'tl'):
                    shutil.copytree(path, game / folder,
                                    ignore=shutil.ignore_patterns('*.rpyc', '__pycache__'))
                else:
                    (game / folder).symlink_to(path, target_is_directory=True)
        shutil.copy2(Path(__file__).with_name('renpy_kagerou_port.rpy'), game / 'kagerou_test.rpy')
        subprocess.run([str(sdk / 'renpy.sh'), str(project), 'kageroutest',
                        '--savedir', str(project / 'test-saves')], check=True,
                       env=os.environ | {'RENPY_PATH_TO_SAVES': str(project / 'sdk-saves')})
        command = [str(sdk / 'renpy.sh'), str(project), 'run',
                   '--savedir', str(project / 'test-saves')]
        environment = os.environ | {'RENPY_PATH_TO_SAVES': str(project / 'sdk-saves'),
            'SDL_AUDIODRIVER': 'dummy', 'RENPY_PERFORMANCE_TEST': '0',
            'RENPY_SKIP_SPLASHSCREEN': '1'}
        if shutil.which('xvfb-run'):
            command = ['xvfb-run', '-a', *command]
            environment['SDL_VIDEODRIVER'] = 'x11'
        fixture = game / 'transition.rpy'
        shutil.copy2(Path(__file__).with_name('renpy_kagerou_transition.rpy'), fixture)
        for language in ('', 'zh'):
            subprocess.run(command, check=True, timeout=45,
                           env=environment | {'KAGEROU_TEST_LANGUAGE': language})
            assert (project / ('transition-%s.png' % (language or 'jp'))).is_file()
        fixture.unlink()
        fixture.with_suffix('.rpyc').unlink(missing_ok=True)
        fixture = game / 'portrait_test.rpy'
        shutil.copy2(Path(__file__).with_name('renpy_kagerou_portrait.rpy'), fixture)
        for language in ('', 'zh'):
            subprocess.run(command, check=True, timeout=45,
                           env=environment | {'KAGEROU_TEST_LANGUAGE': language})
            assert (project / ('portrait-%s.png' % (language or 'jp'))).is_file()
        fixture.unlink()
        fixture.with_suffix('.rpyc').unlink(missing_ok=True)
        for name, seconds in (('short', .5), ('long', 5)):
            with wave.open(str(game / (name + '.wav')), 'wb') as audio:
                audio.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
                audio.writeframes(b'\x00\x00' * int(22050 * seconds))
        fixture = game / 'music_test.rpy'
        shutil.copy2(Path(__file__).with_name('renpy_kagerou_music.rpy'), fixture)
        subprocess.run(command, check=True, timeout=25, env=environment)
        assert all((project / name).is_file() for name in ('music-jp.png', 'music-zh.png'))
        for name in ('music-jp.png', 'music-zh.png'):
            with Image.open(project / name) as screenshot:
                colors = screenshot.convert('RGB').crop((384, 552, 584, 572)).getcolors(4000)
                assert not any(r > 240 and g < 20 and b < 20 for _, (r, g, b) in colors), name
        fixture.unlink()
        fixture.with_suffix('.rpyc').unlink(missing_ok=True)
        fixture = game / 'rollback_test.rpy'
        shutil.copy2(Path(__file__).with_name('renpy_kagerou_rollback.rpy'), fixture)
        for mode in ('back', 'wheel'):
            subprocess.run(command, check=True, timeout=25,
                           env=environment | {'KAGEROU_ROLLBACK_INPUT': mode})
            assert (project / ('rollback-%s.png' % mode)).is_file()
        fixture.unlink()
        fixture.with_suffix('.rpyc').unlink(missing_ok=True)
        if len(sys.argv) == 4:
            shutil.copy2(Path(__file__).with_name('renpy_kagerou_capture.rpy'), game / 'capture.rpy')
            subprocess.run(command, check=True, timeout=45, env=environment)
            destination = Path(sys.argv[3]).resolve()
            destination.mkdir(parents=True, exist_ok=True)
            for name in ('vertical.png', 'horizontal.png', 'preferences-jp.png', 'preferences-zh.png',
                         'transition-jp.png', 'transition-zh.png'):
                shutil.copy2(project / name, destination / name)
            for name in ('music-jp.png', 'music-zh.png', 'rollback-back.png', 'rollback-wheel.png'):
                shutil.copy2(project / name, destination / name)
            for name in ('portrait-jp.png', 'portrait-zh.png'):
                shutil.copy2(project / name, destination / name)


if __name__ == '__main__':
    main()
