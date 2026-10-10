#!/usr/bin/env python3
"""Shared modern lowering and full script/DLC overlay regression checks."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import shutil
import subprocess
import sys
import struct

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evermaiden"))
from build_evermaiden_rscript import build_evermaiden, IMAGE_FOLDERS
from tsc_compiler import compile_overlays, compile_scene
from grps_layout import UI_ACTIONS, collect_layout


def main():
    with TemporaryDirectory(prefix="modern-port-") as directory:
        directory = Path(directory)
        base, patch, project = [directory / name for name in ("base", "zh", "project")]
        for folder in ("scr", "grpe", "grpo", "grpo_ex", "grps", "bgm", "voice", "wav", "mov", *IMAGE_FOLDERS):
            (base / folder).mkdir(parents=True)
        for number in (1, 2, 11, 12):
            (base / 'mov' / ('%04d.mpg' % number)).write_bytes(b'unplayed fixture')
        (patch / "scr").mkdir(parents=True)
        for number in (9, 12, 13, 109, 112, 113, 1070, 1080, 1090):
            shutil.copyfile(ROOT / 'runtime/gui/rscript_cursor.png',
                            base / 'grpo_map' / ('%04d.png' % number))
        for number in (1020, 9001, 9101):
            shutil.copyfile(ROOT / 'runtime/gui/rscript_cursor.png',
                            base / 'grpe' / ('%04d.png' % number))
        for number in (49, 149, 249):
            shutil.copyfile(ROOT / 'runtime/gui/rscript_cursor.png',
                            base / 'grpo_ex' / ('%04d.png' % number))
        for folder, bindings in UI_ACTIONS.items():
            pane = base / 'grps' / folder
            pane.mkdir()
            names = ['bg', *bindings]
            entries = []
            for n, name in enumerate(names):
                shutil.copyfile(ROOT / 'runtime/gui/rscript_cursor.png', pane / (name + '.png'))
                entries.append('<Item x="%d" y="3" flag="8">%s</Item>' % (n * 32, name))
            (pane / '.meta.xml').write_text('<Canvas><Width>1280</Width><Height>720</Height><Items>' + ''.join(entries) + '</Items></Canvas>')
        unknown = base / 'grps/new_panel'
        unknown.mkdir()
        shutil.copyfile(ROOT / 'runtime/gui/rscript_cursor.png', unknown / 'body.png')
        (unknown / '.meta.xml').write_text('<Canvas><Width>32</Width><Height>32</Height><Items><Item x="-2" y="1">body</Item></Items></Canvas>')
        assert collect_layout(base)['new_panel']['items']['body'] == (-2, 1, 32, 32)
        for folder, names in (('savescrn', ('bg_save', 'bg_load', '0', 'exit')),
                              ('fontwnd', ('bg', 'list', 'list_txt', 'prev', 'next', 'exit')),
                              ('saveconf', ('icon', 'thmb', 'date', 'new'))):
            pane = base / 'grps' / folder
            pane.mkdir()
            for name in names:
                shutil.copyfile(ROOT / 'runtime/gui/rscript_cursor.png', pane / (name + '.png'))
            (pane / '.meta.xml').write_text('<Canvas><Width>1280</Width><Height>720</Height><Items>' + ''.join('<Item x="0" y="0">%s</Item>' % name for name in names) + '</Items></Canvas>')
        from PIL import Image
        for folder, color in (('sel_q00', '#56789a'), ('sel_a00', '#345678')):
            pane = base / 'grps' / folder
            pane.mkdir()
            Image.new('RGB', (720, 50), color).save(pane / 'body.png')
            (pane / '.meta.xml').write_text('<Canvas><Width>720</Width><Height>50</Height><Items>'
                '<Item x="0" y="0">body</Item><Item x="40" y="5">text</Item></Items></Canvas>')
        Image.new('RGB', (2, 3), '#123456').save(unknown / 'opaque.bmp')
        patch_ui = patch / 'grps/compane'
        patch_ui.mkdir(parents=True)
        (patch_ui / '.meta.xml').write_text('<Canvas><Width>64</Width><Height>24</Height><Items><Item x="9" y="4">qload</Item></Items></Canvas>')
        header = ';@gsc-byte-format modern-36\n;@gsc-schema modern\n'
        source = (':L_000000\n*flagset 1 3 1\n*dynsel "Question" 0\n'
                  '*dynans "Always" 1 0 0\n*dynans "Once" 2 5024 0\n'
                  '*dynans "Unlocked" 3 5025 1\n*dyndo 2 0 1\n'
                  '*se 2 33\n*se_on 2 0 0 0\n*locmode 0 1 1 0\n'
                  '*insub L_000000 0 0 0 0 0 0 0 0 0 0\n'
                  '*TXT 0 10001 0 0 "Alice" "|漢字[かんじ]^nA^cyB" 0\n'
                  ':END\n*return 0\n')
        (base / 'scr/0000.tsc').write_text(header + source, encoding='utf-8')
        trailer = (struct.pack('<4I', 0, 1, 0, 6) + b'\0REP\0').hex()
        (base / 'scr/0001.tsc').write_text(
            header + ';@gsc-trailer-header 8 5\n;@gsc-trailer ' + trailer + '\n*wait 1\n:L_000006\n*end\n')
        numeric = directory / '1125.tsc'
        trailer = (struct.pack('<4I', 0, 1, 0, 6) + b'\0' + b'8011\0').hex()
        numeric.write_text(header + ';@gsc-trailer-header 8 6\n;@gsc-trailer '
                           + trailer + '\n*wait 1\n:L_000006\n*end\n')
        assert 'label _g_1125_8011:' in compile_scene(numeric)
        jump_source = directory / '0201.tsc'
        jump_source.write_text(header + '*locmap 0 0 0 0 1\n*jump 1 "REP"\n')
        lowered = compile_scene(jump_source, adapter='modern')
        assert '_jump 1%REP' in lowered and '_locmap 0 0 0 0 1' in lowered
        layout_source = directory / '0500.tsc'
        layout_source.write_text(header + '*mode 0 1\n*texfont 0 2\n*texmode 0 0\n'
            '*texpich 0 11 0\n*numenable 0 0\n*texruby 0 0 13 9\n*makesave\n')
        layout_lowered = compile_scene(layout_source, adapter='modern')
        for instruction in ('_mode 0 1', '_texfont 0 2', '_texmode 0 0',
                            '_texpich 0 11 0', '_numenable 0 0'):
            assert instruction in layout_lowered
        assert 'adapter defaults' not in layout_lowered
        assert 'in-memory execution snapshot is not implemented' in layout_lowered
        assert '_texruby 0 0 13 9' in layout_lowered
        assert 'native offset uses the shared interline ruby placement' not in layout_lowered
        (patch / 'scr/0000.tsc').write_text(header + '*wait 2\n' + source.replace('Question', '问题'), encoding='utf-8')
        (patch / 'scr/5000.tsc').write_text(header + '*end\n')
        pcm = base / 'wav/0033.wav'
        pcm.write_bytes(b'PCM test')
        (base / 'wav/0034.wav').write_bytes(b'embedded Ogg wrapper')
        (base / 'wav/0034.ogg').write_bytes(b'Ogg test')
        added = patch / 'grpo_ex/9999.png'
        added.parent.mkdir()
        shutil.copyfile(ROOT / 'runtime/gui/rscript_cursor.png', added)
        files = compile_overlays(base, [('zh', patch)])
        assert len(files) == 5, files.keys()
        assert "if _preferences.language == 'zh':" in files['scr/0000.rpy']
        assert 'jump _rscript_variant0_0000' in files['scr/0000.rpy']
        assert 'only available' in files['scr/5000.rpy']
        assert 'jump _rscript_variant0_0001' in files['scr/0001.rpy']
        assert 'label _g_0001_REP:' in files['scr/0001.rpy']
        assert 'jump _g_rscript_variant0_0001_REP' in files['scr/0001.rpy']
        assert 'label _g_rscript_variant0_0001_REP:' in files['scr/0001.rpy']
        assert 'label _rscript_variant0_0001_L_000006:' in files['scr/0001.rpy']
        script = files['scr/0000.rpy']
        assert 'tl/zh/scr/0000.rpy' in files
        assert not (project / 'game/images').exists()
        assert '_se 2 33' in script and '_se_on 2 0 0 0' in script
        assert '_insub _rscript_variant0_0000_L_' in script
        assert "_rscript_say ('Alice', '|漢字[かんじ]^nA^cyB', 0)" in script
        assert '_voice 10001 0 0 0' in script
        assert "_dynans ('Once', 2, 5024, 0)" in script
        assert '_flagset 1 3 1' in script
        build_evermaiden(base, project, languages=['jp', 'zh=' + str(patch)])
        game = project / 'game'
        assert (project / 'icon.ico').read_bytes() == (ROOT / 'evermaiden/assets/L42_EM.ico').read_bytes()
        with Image.open(ROOT / 'evermaiden/assets/L42_EM.ico') as original, Image.open(game / 'icon.png') as window:
            assert window.convert('RGBA').tobytes() == original.convert('RGBA').tobytes()
        for name, size in (('icon.icns', (1024, 1024)), ('ios-icon.png', (1024, 1024)),
                           ('web-icon.png', (512, 512)), ('android-icon_foreground.png', (432, 432)),
                           ('android-icon_background.png', (432, 432))):
            with Image.open(project / name) as image:
                assert image.size == size, (name, image.size)
        assert 'define config.window_icon = "icon.png"' in (game / 'engine/options.rpy').read_text()
        assert 'define config.version = "1.3"' in (game / 'engine/port_version.rpy').read_text()
        assert 'define rscript_boot_movies = (2, 1)' in (game / 'engine/ui_features.rpy').read_text()
        assert 'rscript_boot_movies =' not in (game / 'engine/options.rpy').read_text()
        for number in (1, 2, 11, 12):
            assert (game / 'mov' / ('%04d.mpg' % number)).read_bytes() == b'unplayed fixture'
        # A repeated build produces identical icon inputs, without --force.
        from build_port import install_icon
        install_icon(ROOT / 'evermaiden/assets/L42_EM.ico', project)
        assert (game / 'wav/0033.wav').is_file()
        assert (game / 'wav/0034.ogg').is_file() and not (game / 'wav/0034.wav').exists()
        assert (game / 'tl/zh/grpo_ex/9999.png').is_file()
        assert (game / 'engine/ui_features.rpy').read_bytes() == (ROOT / 'port_template/game/ui_features.rpy').read_bytes()
        assert not (game / 'evermaiden_compat.rpy').exists()
        assert (game / 'grps/new_panel/.meta.xml').is_file()
        with Image.open(game / 'grps/new_panel/opaque.png') as opaque:
            assert opaque.getpixel((0, 0)) == (18, 52, 86, 255)
        assert not (game / 'audio').exists() and not (game / 'scenario').exists()
        assert (game / 'engine/06_rscript_modern.rpy').is_file()
        assert (game / 'scr/0000.rpy').is_file() and (game / 'tl/zh/scr/5000.rpy').is_file()
        if len(sys.argv) > 1:
            shutil.copyfile(ROOT / 'tests/renpy_modern_port.rpy', game / 'modern_test.rpy')
            subprocess.run([str(Path(sys.argv[1]) / 'renpy.sh'), str(project), 'modernporttest',
                            '--savedir', str(directory / 'test-saves')], check=True,
                           env=os.environ | {'SDL_AUDIODRIVER': 'dummy',
                                             'RENPY_PATH_TO_SAVES': str(directory / 'sdk-saves')})
            if len(sys.argv) > 2:
                # Execute actual converted title/CG/scene scripts in isolation.
                # Use tiny stand-in artwork, not formal game saves or resources.
                resources = Path(sys.argv[2])
                for name in ('0001', '0201', '0301'):
                    (game / 'scr' / (name + '.rpy')).write_text(compile_scene(
                        resources / 'scr' / (name + '.tsc'), adapter='modern'))
                for folder in ('grpe', 'grpo', 'grpo_ex', 'grpo_cu'):
                    (game / folder).mkdir(exist_ok=True)
                    for asset in (resources / folder).glob('*.png'):
                        shutil.copyfile(ROOT / 'runtime/gui/rscript_cursor.png',
                                        game / folder / asset.name)
                shutil.copyfile(ROOT / 'tests/renpy_gallery_flow.rpy', game / 'gallery_test.rpy')
                subprocess.run([str(Path(sys.argv[1]) / 'renpy.sh'), str(project), 'galleryflowtest',
                                '--savedir', str(directory / 'gallery-saves')], check=True,
                               env=os.environ | {'SDL_AUDIODRIVER': 'dummy',
                                                 'RENPY_PATH_TO_SAVES': str(directory / 'gallery-sdk-saves')})
            if '--render' in sys.argv:
                shutil.copyfile(ROOT / 'tests/renpy_modern_ruby.rpy', game / 'scr/0000.rpy')
                (game / 'scr/0000.rpyc').unlink(missing_ok=True)
                result = subprocess.run(['xvfb-run', '-a', str(Path(sys.argv[1]) / 'renpy.sh'),
                                         str(project), 'run', '--savedir', str(directory / 'ruby-saves')],
                                        timeout=45, capture_output=True, text=True,
                                        env=os.environ | {
                                            'SDL_VIDEODRIVER': 'x11', 'SDL_AUDIODRIVER': 'dummy',
                                            'RENPY_RENDERER': 'gl2', 'RENPY_SKIP_SPLASHSCREEN': '1',
                                            'RENPY_SKIP_MAIN_MENU': '1', 'RENPY_PERFORMANCE_TEST': '0',
                                            'RENPY_PATH_TO_SAVES': str(directory / 'ruby-sdk-saves')})
                assert result.returncode == 0, result.stdout + result.stderr
                assert 'OK: native modern ruby drawable layout' in result.stdout, result.stdout + result.stderr
                assert 'OK: native dynamic-choice paging through real menu actions' in result.stdout, result.stdout + result.stderr
                with Image.open('/tmp/rscript-modern-choice.png') as capture:
                    def pixel(x, y):
                        return capture.getpixel((round(x * capture.width / 1280),
                                                 round(y * capture.height / 720)))[:3]
                    assert pixel(500, 150) == (86, 120, 154)  # prompt at y=125
                    for y in (180, 235, 290, 345, 400):
                        assert pixel(500, y + 25) == (52, 86, 120), (y, pixel(500, y + 25))
                        assert pixel(500, y + 52) == (18, 52, 86), (y, pixel(500, y + 52))
                    assert pixel(265, 150) == (86, 120, 154)
                    assert pixel(265, 205) == (18, 52, 86)  # answers are 30px right of prompt
                print('OK: native modern ruby drawable layout and clipping headroom')
                print('OK: native dynamic-choice paging through real menu actions')
                print('OK: dynamic-choice framebuffer positions and five-pixel gaps')
                assert 'OK: dynamic-choice entry, paging without re-entry, selected exit and cleanup' in result.stdout, result.stdout + result.stderr
                for phase in ('enter', 'exit'):
                    with Image.open('/tmp/rscript-modern-motion-%s.png' % phase) as capture:
                        def pixel(x, y):
                            return capture.getpixel((round(x * capture.width / 1280),
                                                     round(y * capture.height / 720)))[:3]
                        if phase == 'enter':
                            assert pixel(50, 205) == (52, 86, 120)  # Moving in from left.
                            assert pixel(950, 205) == (18, 52, 86)
                        else:
                            assert pixel(300, 260) == (52, 86, 120)  # Chosen row stays.
                            assert pixel(300, 315) == (18, 52, 86)  # Other row leaves right.
                print('OK: dynamic-choice motion through GL2 framebuffer and native actions')
                shutil.copyfile(ROOT / 'tests/renpy_boot_movies.rpy', game / 'scr/0000.rpy')
                (game / 'scr/0000.rpyc').unlink(missing_ok=True)
                result = subprocess.run(['xvfb-run', '-a', str(Path(sys.argv[1]) / 'renpy.sh'),
                                         str(project), 'run', '--savedir', str(directory / 'boot-saves')],
                                        check=True, timeout=45, capture_output=True, text=True,
                                        env=os.environ | {
                                            'SDL_VIDEODRIVER': 'x11', 'SDL_AUDIODRIVER': 'dummy',
                                            'RENPY_SKIP_SPLASHSCREEN': '', 'RENPY_SKIP_MAIN_MENU': '1',
                                            'RENPY_PERFORMANCE_TEST': '0',
                                            'RENPY_PATH_TO_SAVES': str(directory / 'boot-sdk-saves')})
                assert 'OK: native startup movies play in order only on launch' in result.stdout, result.stdout + result.stderr
                print('OK: Evermaiden startup movies and return to title')
        print('OK: modern shared lowering, complete language/DLC routes and PCM assets')


if __name__ == '__main__':
    main()
