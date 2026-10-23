# Сторонние ресурсы и лицензии

[中文](THIRD_PARTY_NOTICES.zh.md) | [English](THIRD_PARTY_NOTICES.en.md) | [Русский](THIRD_PARTY_NOTICES.ru.md)

[Главная](README.ru.md)

MIT распространяется на код проекта, но не на все вложенные ресурсы. Ниже — происхождение и отдельные условия;
перед распространением проверьте каждый ресурс.

## renpy-rscript

Runtime RScript включает адаптированный MIT-код renpy-rscript и совместимые части RScript из проекта Sona-Nyl Ren'Py.
На них распространяется [LICENSE](LICENSE). Специальный код игры Sona-Nyl и её слой Kirikiri сюда не входят.

## Курсор Forest

`runtime/gui/rscript_cursor.png` — исходный курсор 32×32 из Windows EXE Forest от Liar-soft,
общий совместимый ресурс переносов RScript. MIT репозитория на изображение не распространяется;
все права принадлежат исходному правообладателю.

## Android-значок Forest

`forest/android/android-icon_foreground.png` содержит значок Forest и копируется только при сборке Forest.
MIT неприменима, все права у исходного правообладателя. Фон — одноцветный слой адаптивного значка.

## Значок Khime

`khime/assets/icon.ico` — оригинальный значок Khime (Kusarihime) из `KhimeKusaritop_s/1.ico`.
`khime/assets/icon.png` — побиксельно идентичная PNG-копия для окна Ren'Py. Генератор копирует их
в `icon.ico` и `game/icon.png`. MIT неприменима, права принадлежат исходному правообладателю.
Указание авторства не даёт разрешения на распространение.
`khime/android/android-icon_foreground.png` — тот же значок, масштабированный ближайшим соседом
на прозрачный адаптивный холст; фон чёрный. Ограничения переднего плана те же.

## Значок Evermaiden

`evermaiden/assets/L42_EM.ico` получен из `Evermaiden_s/L42_EM.ico`. Генератор копирует ICO без изменений
и создаёт из него значки окна, macOS, Android, iOS и Web. MIT неприменима, все права у исходного правообладателя;
указание авторства не является разрешением на распространение.

## Значок CannonBall

`cannonball/assets/2.ico` получен из `CannonBall/2.ico`. Генератор копирует ICO без изменений
и создаёт значки окна, macOS, Android, iOS и Web. MIT неприменима, права у исходного правообладателя;
указание авторства не даёт права распространения.

## Шрифты Forest

`port_template/fonts/simhei.ttf` (SimHei Regular 5.04) соответствует шрифту, запрошенному китайским EXE Forest.
Встроенное уведомление: © Beijing ZhongYi Electronics Co., 1995-2005, All rights reserved.
Это проприетарный шрифт Microsoft, не MIT/OFL. Проект не получил и не подтвердил дополнительных прав
на распространение; указание авторства не является разрешением. См.
[уведомление SimHei](port_template/fonts/SimHei-NOTICE.ru.md) и
[FAQ Microsoft](https://learn.microsoft.com/en-us/typography/fonts/font-faq).

Генератор Forest включает Noto Sans CJK JP Regular, Noto Sans CJK Light и Noto Serif CJK Regular.
Их лицензия SIL Open Font License 1.1 сохранена в `port_template/fonts/NotoSans.txt`.
