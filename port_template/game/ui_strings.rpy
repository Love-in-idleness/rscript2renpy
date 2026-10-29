# Interface labels are separate from translated scenario text.
init -1 python:
    rscript_ui_strings = {
        "zh": {
            "Text Settings": "文字设置", "Text Display": "文字显示",
            "Text Size": "字号", "Dialogue Characters per Line": "对话每行字数",
            "Overlay Characters per Line": "叠加文字每行字数", "Line Spacing": "行距",
            "Font": "字体", "Previous Font": "上一个字体", "Next Font": "下一个字体",
            "Language": "语言", "Wiki": "维基", "On": "开", "Off": "关",
            "Persistent Progress": "系统进度", "Save Backup": "备份进度",
            "Load Backup": "恢复备份", "Clear Progress": "清除进度",
            "Clear persistent progress? The backup will be kept.": "清除系统进度？已有备份将保留。",
            "Progress backup saved.": "系统进度已备份。",
            "No progress backup is available.": "没有可用的进度备份。",
            "Progress backup restored.": "系统进度已恢复。",
            "Persistent progress cleared (backup kept).": "系统进度已清除，备份已保留。",
            "Back": "返回", "Skip": "跳过", "Auto": "自动", "Hide": "隐藏",
            "Screenshot": "截图", "Menu": "菜单", "Yes": "是", "No": "否",
            "Music": "音乐", "Sound": "音效", "Voice": "语音",
            "Save": "存档", "Load": "读档", "Main Menu": "主菜单", "Quit": "退出游戏",
            "Save %d": "存档 %d", "Load %d": "读档 %d",
            "Return to the main menu? Unsaved progress will be lost.": "返回主菜单？未保存的进度将丢失。",
            "Quit the game? Unsaved progress will be lost.": "退出游戏？未保存的进度将丢失。",
            "Screenshot failed. No image was saved.": "截图失败，图片未保存。",
            "Screenshot saved to Gallery / Pictures / RScript.": "截图已保存至相册 / Pictures / RScript。",
        },
        "ru": {
            "Text Settings": "Настройки текста", "Text Display": "Текст",
            "Text Size": "Размер текста", "Dialogue Characters per Line": "Символов в реплике",
            "Overlay Characters per Line": "Символов в надписях", "Line Spacing": "Межстрочный интервал",
            "Font": "Шрифт", "Previous Font": "Предыдущий шрифт", "Next Font": "Следующий шрифт",
            "Language": "Язык", "Wiki": "Вики", "On": "Вкл.", "Off": "Выкл.",
            "Persistent Progress": "Системный прогресс", "Save Backup": "Создать копию",
            "Load Backup": "Восстановить", "Clear Progress": "Сбросить",
            "Clear persistent progress? The backup will be kept.": "Сбросить системный прогресс? Резервная копия сохранится.",
            "Progress backup saved.": "Резервная копия прогресса сохранена.",
            "No progress backup is available.": "Резервной копии прогресса нет.",
            "Progress backup restored.": "Прогресс восстановлен из копии.",
            "Persistent progress cleared (backup kept).": "Системный прогресс сброшен. Копия сохранена.",
            "Back": "Назад", "Skip": "Пропуск", "Auto": "Авто", "Hide": "Скрыть",
            "Screenshot": "Снимок", "Menu": "Меню", "Yes": "Да", "No": "Нет",
            "Music": "Музыка", "Sound": "Звуки", "Voice": "Голоса",
            "Save": "Сохранить", "Load": "Загрузить", "Main Menu": "Главное меню", "Quit": "Выход",
            "Save %d": "Сохранить %d", "Load %d": "Загрузить %d",
            "Return to the main menu? Unsaved progress will be lost.": "Вернуться в главное меню? Несохранённый прогресс будет потерян.",
            "Quit the game? Unsaved progress will be lost.": "Выйти из игры? Несохранённый прогресс будет потерян.",
            "Screenshot failed. No image was saved.": "Не удалось сохранить снимок экрана.",
            "Screenshot saved to Gallery / Pictures / RScript.": "Снимок сохранён в галерее / Pictures / RScript.",
        },
        "jp": {
            "Text Settings": "文字設定", "Text Display": "文字表示",
            "Text Size": "文字サイズ", "Dialogue Characters per Line": "会話の一行文字数",
            "Overlay Characters per Line": "重ね文字の一行文字数", "Line Spacing": "行間",
            "Font": "フォント", "Previous Font": "前のフォント", "Next Font": "次のフォント",
            "Language": "言語", "Wiki": "Wiki", "On": "オン", "Off": "オフ",
            "Persistent Progress": "システム進行データ", "Save Backup": "バックアップ",
            "Load Backup": "復元", "Clear Progress": "進行データを消去",
            "Clear persistent progress? The backup will be kept.": "システム進行データを消去しますか？バックアップは残ります。",
            "Progress backup saved.": "進行データをバックアップしました。",
            "No progress backup is available.": "進行データのバックアップがありません。",
            "Progress backup restored.": "進行データを復元しました。",
            "Persistent progress cleared (backup kept).": "進行データを消去しました。バックアップは残っています。",
            "Back": "戻る", "Skip": "スキップ", "Auto": "オート", "Hide": "非表示",
            "Screenshot": "撮影", "Menu": "メニュー", "Yes": "はい", "No": "いいえ",
            "Music": "音楽", "Sound": "効果音", "Voice": "音声",
            "Save": "セーブ", "Load": "ロード", "Main Menu": "タイトルへ", "Quit": "ゲーム終了",
            "Save %d": "セーブ %d", "Load %d": "ロード %d",
            "Return to the main menu? Unsaved progress will be lost.": "タイトルに戻りますか？未保存の進行状況は失われます。",
            "Quit the game? Unsaved progress will be lost.": "ゲームを終了しますか？未保存の進行状況は失われます。",
            "Screenshot failed. No image was saved.": "撮影に失敗しました。画像は保存されていません。",
            "Screenshot saved to Gallery / Pictures / RScript.": "画像をギャラリー / Pictures / RScript に保存しました。",
        },
    }

    def rscript_ui_text(text):
        language = _preferences.language
        if language is None:
            language = next((label for value, label in rscript_languages if value is None), None)
        return rscript_ui_strings.get(language, {}).get(text, text)

style rscript_menu_text is text:
    font gui.interface_text_font

style rscript_menu_button_text is button_text:
    font gui.interface_text_font
