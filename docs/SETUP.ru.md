# Среда и первая сборка

[中文](SETUP.zh.md) | [English](SETUP.en.md) | [Русский](SETUP.ru.md)

Это руководство для уже адаптированных игр. Для новой игры нужен адаптер:
см. [руководство разработчика](NEW_GAME_PORTING.ru.md).
Замените все `/path/to/...` своими путями.

## 1. Зависимости

| Зависимость | Назначение |
| --- | --- |
| Python 3, рекомендуется 3.11+ | Генераторы проекта |
| Pillow | Размеры изображений и значки приложения |
| Ren'Py 8 SDK | Запуск, проверка и упаковка |
| [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool) | Распаковка и преобразование сценариев, изображений и аудио |
| Git | Получение исходников |

Распакуйте полный SDK: в Linux используется `renpy.sh`, в Windows — `renpy.exe`.
Обычная сборка готовой адаптации не требует Wine, RsComp.dll или виртуальной машины Windows.

## 2. Получение проекта

Linux / macOS:

```bash
git clone https://github.com/Love-in-idleness/rscript2renpy.git
cd rscript2renpy
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Pillow
```

В Windows, PowerShell из корня репозитория:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install Pillow
```

В командах Windows замените `python3` на `.\.venv\Scripts\python.exe`.
В Linux используйте `python` или `python3` активированного окружения.

## 3. Рабочие копии ресурсов

Храните оригиналы, преобразованные копии и результат отдельно:

```text
work/
├── originals/Game/
├── prepared/Game/
├── prepared/Game.zh/
└── projects/Game/
```

Не преобразуйте оригинал. Входные ресурсы и выходной проект не должны
перекрываться. Проверьте требования конкретной игры: например, Kagerou нужна
версия с «ハチポチ特典».

Для японских ресурсов обычно подходит CP932:

```bash
/path/to/liarsofttool -R --unpack-only --gsc-to-tsc -e cp932 /path/to/prepared/Game
```

Китайский патч в GBK преобразуйте отдельно:

```bash
/path/to/liarsofttool -R --unpack-only --gsc-to-tsc -e gbk /path/to/prepared/Game.zh
```

В результате нужны `scr/*.tsc`, доступные изображения и аудио. Сохраните `.meta.xml`.
Обычные PCM WAV и исходные MPG можно использовать напрямую. Для повторного
экспорта сценариев используйте LiarsoftTool; сначала сохраните изменённые TSC.

## 4. Сборка проекта

Пример Forest, из корня репозитория:

```bash
python3 forest/build_forest_rscript.py /path/to/prepared/Forest /path/to/projects/Forest \
    --language jp --language zh=/path/to/prepared/Forest.zh
```

Без патча уберите `--language zh=...`. `jp` — метка оригинала, `zh=каталог`
добавляет переключаемый перевод. Метки не меняют кодировку файлов.
Правила патчей различаются: см. [руководства игр](../README.ru.md#руководства-по-играм).

Для первой сборки используйте новый каталог. Перед повторной сохраните ручные
изменения и добавьте `--force`, если генератор этого требует.

## 5. Запуск и проверка

```bash
/path/to/renpy-sdk/renpy.sh /path/to/projects/Forest lint
/path/to/renpy-sdk/renpy.sh /path/to/projects/Forest
```

В Windows выберите проект в запускателе Ren'Py и запустите проверку или игру.
Для Android используйте инструменты SDK; дополнительно настройте RAPT.

При ошибке сохраните полный вывод, версию игры, команду сборки и сцену.
После lint проверьте изображение, звук, выборы и сохранения в игре.

## Дополнительно

`local.paths.toml` — необязательная памятка локальных путей, не требуемая
конфигурация генератора: см. [локальную настройку](LOCAL_WORKFLOW.ru.md).
Проект не распространяет игры и готовые игровые сборки. Перед распространением
проверьте [лицензии ресурсов](../THIRD_PARTY_NOTICES.ru.md); не включайте свои
сохранения или ключи подписи.
