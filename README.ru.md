# rscript2renpy

[中文](README.zh.md) | [English](README.en.md) | Русский

`rscript2renpy` — совместимый с Ren'Py 8 runtime и инструменты переноса игр
на CodeX RScript, прежде всего произведений Liar-soft и raiL-soft.

Начните с [настройки среды и первой сборки](docs/SETUP.ru.md).
Для новой игры см. [руководство по переносу и запрос для ИИ](docs/NEW_GAME_PORTING.ru.md).
Дальнейшие цели — в [плане развития](docs/ROADMAP.ru.md).

Кроме общего курсора и значков приложений, репозиторий не содержит игровых
сценариев, изображений, аудио, видео или EXE. Подготовьте законно приобретённые
файлы игры и соберите проект самостоятельно.

## Руководства по играм

Требования к ресурсам, команды сборки и правила языковых патчей описаны отдельно.
Все примеры запускаются из корня репозитория.

| Игра | Руководство |
| --- | --- |
| Forest | [Forest](forest/README.ru.md) |
| Khime Kusaritop, включая необязательную Khime Zero | [Khime](khime/README.ru.md) |
| Evermaiden | [Evermaiden](evermaiden/README.ru.md) |
| CannonBall | [CannonBall](cannonball/README.ru.md) |
| SevenBridge, японская версия | [SevenBridge](sevenbridge/README.ru.md) |
| KagerouTouryuuki, адаптация в работе, только с «ハチポチ特典» | [KagerouTouryuuki](kagerou/README.ru.md) |

## Зависимости и подготовка ресурсов

Нужны Python 3, Pillow и Ren'Py 8 SDK. Распаковка и преобразование ресурсов
выполняются [LiarsoftTool](https://github.com/Love-in-idleness/LiarsoftTool).

Скопируйте ресурсы игры, затем распакуйте их, получите TSC и преобразуйте
изображения и аудио через LiarsoftTool. После этого запускайте генератор игры.
Генераторы читают только TSC, не GSC.

## Общий шаблон и результат

Новую адаптацию начинайте с [общего шаблона](port_template/README.ru.md).
Runtime находится в `runtime/`, сборка и интерфейс — в `port_template/`, различия
игр — в каталогах адаптаций. Распределение UI-ресурсов и правила `.meta.xml`
описаны в руководстве шаблона.

Проект сохраняет структуру ресурсов: сценарии в `game/scr/`, изображения
в `game/grp*/`, аудио в `game/bgm/`, `game/voice/`, `game/wav/`, видео в `game/mov/`.
Общий интерфейс, runtime и настройки находятся в `game/engine/`, переводы —
в `game/tl/<язык>/`.

Чтобы установить только общий runtime:

```bash
python3 tools/install_runtime.py /path/to/renpy-project
```

Существующие файлы с другим содержимым не заменяются без разрешения.
Генераторы добавляют общий курсор и пояснение проекта при запуске Android.

## Проверка и обратная связь

```bash
/path/to/renpy-sdk/renpy.sh /path/to/renpy-project lint
```

После lint сравните изображение, речь, выборы и сохранения с оригиналом.
В отчёте об ошибке укажите версию игры, команду сборки, полный текст ошибки или
снимок экрана и сцену. Тесты и технические заметки — в [документации](docs/README.ru.md).

## Лицензии

Код распространяется по [MIT License](LICENSE). Сторонний код, курсор, значки
и шрифты перечислены в [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Noto CJK использует [SIL Open Font License 1.1](port_template/fonts/NotoSans.txt).
У SimHei отдельные условия: [уведомление о шрифте](port_template/fonts/SimHei-NOTICE.md).
