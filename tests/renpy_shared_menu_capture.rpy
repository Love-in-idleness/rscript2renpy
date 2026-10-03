# Optional desktop render check on a disposable, fully generated project.
label before_main_menu:
    $ persistent.rscript_text_size = rscript_base_text_size
    $ persistent.rscript_text_font = rscript_default_font
    $ rscript_languages = [(None, "jp"), ("en", "en"), ("ru", "ru"), ("zh", "zh")]
    $ _preferences.language = "zh"
    $ rscript_wiki_keywords = {"zh": [("test", "https://example.test", "test")]}
    show screen shared_menu_capture
    $ renpy.pause()

screen shared_menu_capture():
    modal True
    use rscript_text_preferences
    timer 1.0 action [Function(renpy.screenshot, os.path.join(config.basedir, "shared-menu.png")), Quit(confirm=False)]
