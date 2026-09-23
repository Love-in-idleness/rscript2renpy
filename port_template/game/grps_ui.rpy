# Shared CodeX UI. Positions and available sprites come from grps/*/.meta.xml.
default persistent.rscript_textbox_opacity = 1.0
default rscript_last_voice = None

init python:
    config.game_menu_action = ShowMenu("preferences")

    def rscript_replay_voice():
        if store.rscript_last_voice:
            renpy.music.play(store.rscript_last_voice, channel="voice")

screen rscript_grps_button(folder, name, button_action, enabled=True):
    $ items = rscript_grps_layout.get(folder, {}).get("items", {})
    $ item = items.get(name)
    if item:
        $ idle_image = "images/grps/%s/%s.png" % (folder, name)
        $ focused_image = ("images/grps/%s/%s_f.png" % (folder, name)
                           if name + "_f" in items else idle_image)
        $ focused = items.get(name + "_f", item)
        $ focused_display = Transform(focused_image,
                                      xoffset=focused[0] - item[0],
                                      yoffset=focused[1] - item[1])
        imagebutton:
            idle idle_image
            hover focused_display
            selected_idle focused_display
            selected_hover focused_display
            xpos item[0]
            ypos item[1]
            sensitive enabled
            action button_action

screen preferences():
    tag menu
    modal True
    key "game_menu" action Return()
    $ layout = rscript_grps_layout.get("confscrn")
    if layout and "bg" in layout["items"]:
        fixed:
            xysize layout["size"]
            xalign 0.5
            yalign 0.5
            $ bg = layout["items"]["bg"]
            add "images/grps/confscrn/bg.png" xpos bg[0] ypos bg[1]

            for name, setting, value in (
                    ("scm_ful", "display", "fullscreen"),
                    ("scm_wnd", "display", "window"),
                    ("bgm_on", "music mute", "disable"),
                    ("bgm_off", "music mute", "enable"),
                    ("sef_on", "sound mute", "disable"),
                    ("sef_off", "sound mute", "enable"),
                    ("voc_on", "voice mute", "disable"),
                    ("voc_off", "voice mute", "enable"),
                    ("gef_on", "transitions", "all"),
                    ("gef_off", "transitions", "none"),
                    ("msp_slw", "text speed", 25),
                    ("msp_nom", "text speed", 75),
                    ("msp_now", "text speed", 0),
                    ("msk_on", "skip", "all"),
                    ("msk_off", "skip", "seen")):
                use rscript_grps_button("confscrn", name,
                                         Preference(setting, value))
            use rscript_grps_button("confscrn", "vocst_on",
                                     SetField(persistent, "rscript_stop_voice_on_advance", True))
            use rscript_grps_button("confscrn", "vocst_off",
                                     SetField(persistent, "rscript_stop_voice_on_advance", False))

            for prefix, setting in (("bgm", "music volume"),
                                    ("sef", "sound volume"),
                                    ("voc", "voice volume"),
                                    ("auto", "auto-forward time")):
                $ track = layout["items"].get(prefix + "_lev")
                $ thumb = layout["items"].get(prefix + "_vol")
                if track and thumb:
                    bar:
                        value Preference(setting)
                        base_bar Solid("#00000000")
                        thumb "images/grps/confscrn/%s_vol.png" % prefix
                        hover_thumb ("images/grps/confscrn/%s_vol_f.png" % prefix
                                     if prefix + "_vol_f" in layout["items"] else
                                     "images/grps/confscrn/%s_vol.png" % prefix)
                        xpos track[0]
                        ypos track[1]
                        xsize track[2]
                        ysize track[3]
                        bar_invert prefix == "auto"

            use rscript_grps_button("confscrn", "save", ShowMenu("save"))
            use rscript_grps_button("confscrn", "load", ShowMenu("load"))
            use rscript_grps_button("confscrn", "title", MainMenu(confirm=False))
            use rscript_grps_button("confscrn", "exit", Quit(confirm=True))
            use rscript_grps_button("confscrn", "close", Return())
    else:
        frame:
            xalign 0.5
            yalign 0.5
            vbox:
                textbutton "Music" action Preference("music mute", "toggle")
                textbutton "Sound" action Preference("sound mute", "toggle")
                textbutton "Voice" action Preference("voice mute", "toggle")
                textbutton "Save" action ShowMenu("save")
                textbutton "Load" action ShowMenu("load")
                textbutton "Back" action Return()

screen rscript_compane():
    $ layout = rscript_grps_layout.get("compane")
    if layout:
        fixed:
            xysize layout["size"]
            xalign 1.0
            yalign 1.0
            $ items = layout["items"]
            if "bg" in items:
                $ bg = items["bg"]
                add "images/grps/compane/bg.png" xpos bg[0] ypos bg[1]
            $ track = items.get("slide_lev")
            if track and "slide" in items:
                if track[3] > track[2]:
                    vbar:
                        value FieldValue(persistent, "rscript_textbox_opacity", range=1.0)
                        base_bar Solid("#00000000")
                        thumb "images/grps/compane/slide.png"
                        xpos track[0]
                        ypos track[1]
                        xsize track[2]
                        ysize track[3]
                else:
                    bar:
                        value FieldValue(persistent, "rscript_textbox_opacity", range=1.0)
                        base_bar Solid("#00000000")
                        thumb "images/grps/compane/slide.png"
                        xpos track[0]
                        ypos track[1]
                        xsize track[2]
                        ysize track[3]
            use rscript_grps_button("compane", "rev", Rollback())
            use rscript_grps_button("compane", "bak", Rollback())
            use rscript_grps_button("compane", "fow", RollForward())
            use rscript_grps_button("compane", "next", Skip(fast=True))
            use rscript_grps_button("compane", "auto", Preference("auto-forward", "toggle"))
            use rscript_grps_button("compane", "hide", HideInterface())
            use rscript_grps_button("compane", "voc", Function(rscript_replay_voice),
                                     rscript_last_voice is not None)

screen rscript_choice(items, prompt=None):
    modal True
    key "game_menu" action ShowMenu("preferences")
    key "rollback" action Rollback()
    $ answer_folder = next((name for name in sorted(rscript_grps_layout)
                            if name.startswith("sel_a")), None)
    $ prompt_folder = next((name for name in sorted(rscript_grps_layout)
                            if name.startswith("sel_q")), None)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 4
        if prompt:
            if prompt_folder:
                $ question = rscript_grps_layout[prompt_folder]
                fixed:
                    xysize question["size"]
                    $ body = question["items"]["body"]
                    $ textpos = question["items"].get("text", (20, 10))
                    add "images/grps/%s/body.png" % prompt_folder xpos body[0] ypos body[1]
                    text prompt xpos textpos[0] ypos textpos[1] color "#ffffff"
            else:
                text prompt xalign 0.5 color "#ffffff"
        for item in items:
            if item.action is not None:
                if answer_folder:
                    $ answer = rscript_grps_layout[answer_folder]
                    fixed:
                        xysize answer["size"]
                        $ body = answer["items"]["body"]
                        $ textpos = answer["items"].get("text", (20, 10))
                        imagebutton:
                            idle "images/grps/%s/body.png" % answer_folder
                            hover ("images/grps/%s/body_f.png" % answer_folder
                                   if "body_f" in answer["items"] else
                                   "images/grps/%s/body.png" % answer_folder)
                            focus_mask True
                            xpos body[0]
                            ypos body[1]
                            action item.action
                        text item.caption xpos textpos[0] ypos textpos[1] color "#ffffff"
                else:
                    textbutton item.caption action item.action

screen save():
    tag menu
    use rscript_file_slots("save")

screen load():
    tag menu
    use rscript_file_slots("load")

screen rscript_file_slots(mode):
    modal True
    key "game_menu" action Return()
    $ layout = rscript_grps_layout.get("savescrn")
    if layout and "bg_" + mode in layout["items"]:
        fixed:
            xysize layout["size"]
            xalign 0.5
            yalign 0.5
            $ items = layout["items"]
            $ bg = items["bg_" + mode]
            add "images/grps/savescrn/bg_%s.png" % mode xpos bg[0] ypos bg[1]
            for index in range(10):
                $ item = items.get(str(index))
                if item:
                    $ slot = index + 1
                    $ slot_action = FileSave(slot) if mode == "save" else FileLoad(slot)
                    button:
                        xpos item[0]
                        ypos item[1]
                        xsize item[2]
                        ysize item[3]
                        background None
                        hover_background Solid("#ffffff20")
                        action slot_action
                        add FileScreenshot(slot):
                            xpos 4
                            ypos 4
                            xsize 92
                            ysize item[3] - 8
                        text FileTime(slot, "%Y/%m/%d %H:%M"):
                            xpos 101
                            yalign 0.5
                            color "#ffffff"
                            size 15
            use rscript_grps_button("savescrn", "prev",
                                     FilePagePrevious(max=10, wrap=True))
            use rscript_grps_button("savescrn", "next",
                                     FilePageNext(max=10, wrap=True))
            if "number" in items:
                $ number = items["number"]
                text FileCurrentPage() xpos number[0] ypos number[1] color "#ffffff"
            use rscript_grps_button("savescrn", "exit", Return())
    else:
        frame:
            xalign 0.5
            yalign 0.5
            vbox:
                for slot in range(1, 11):
                    $ slot_action = FileSave(slot) if mode == "save" else FileLoad(slot)
                    textbutton ("Save %d" % slot if mode == "save" else "Load %d" % slot):
                        action slot_action
                textbutton "Back" action Return()
