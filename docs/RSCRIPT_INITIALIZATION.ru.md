# Техническая справка: инициализация RScript

[中文](RSCRIPT_INITIALIZATION.zh.md) | [English](RSCRIPT_INITIALIZATION.en.md) | [Русский](RSCRIPT_INITIALIZATION.ru.md) | [日本語](RSCRIPT_INITIALIZATION.ja.md)

[Документация](README.ru.md)

Для нового адаптера изучите RsInit.tcf: размеры, ресурсы и запуск. Не у каждой игры есть
этот файл или RsInit.dll; иначе проверяйте EXE и сценарии.

## Инспектор

```bash
python3 tools/inspect_rscript_init.py /path/to/game-resources
python3 tools/inspect_rscript_init.py /path/to/RsInit.tcf --encoding gbk
```

Только чтение и JSON в терминал, без исполнения EXE/DLL. По умолчанию CP932, меняется --encoding.
Отчёт содержит конфигурацию, каталоги ресурсов, наличие CFG и неизвестные элементы.

## Подтверждённые ключи

По исследованному инициализатору Khime Zero:

| Ключ | Назначение |
| --- | --- |
| title | Заголовок окна |
| width, height | Начальный холст |
| exec, script | Переключатель и номер начального сценария |
| scrdir | Сценарии |
| sysimgdir, layerimgdir, faceimgdir, bgimgdir | Изображения |
| moviedir, wavedir, bgmdir, voicedir | Медиа |
| savepfx | Префикс оригинальных сохранений |
| scrmod, extmod | Имена компилятора/расширения |
| bgm, bgmsource, layermod | Числа, семантика значений не подтверждена |

TCF не обязательно окончательный: CFG или значения EXE могут иметь приоритет.
Конфигурация одной игры — не спецификация всех версий движка.

## Бинарные основания

Khime_zero/RsInit.dll, SHA-256 `b35bd24626a65d67ee932f2a62076070805c98b5f7a50f9920c19f2d8696b218`.
GetInitialData (`0x10001dd0`) читает TCF в структуру вызывающего; SaveInitialData (`0x10002170`)
записывает её 324 байта в CFG. Основная программа `0x415330` сначала пробует CFG, затем TCF.
В китайском образце заголовок GBK, комментарии CP932: всему файлу нельзя приписывать одну кодировку.
Это статические выводы для этой сборки. Инспектор не требует распространения DLL.

## Проверка

```bash
python3 -B tests/test_rscript_init.py
python3 -B tests/test_rscript_init.py /path/to/Khime_zero
```
