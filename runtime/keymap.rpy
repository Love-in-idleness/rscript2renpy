init -99:

    define config.keymap = dict(



    rollback = [ 'K_PAGEUP', 'repeat_K_PAGEUP', 'K_AC_BACK', 'mousedown_4' ],
    screenshot = [ 's', 'alt_K_s', 'alt_shift_K_s' ],
    toggle_afm = [ ],
    toggle_fullscreen = [ 'f', 'alt_K_RETURN', 'alt_K_KP_ENTER', 'K_F11' ],
    game_menu = [ 'K_ESCAPE', 'K_MENU', 'mouseup_3' ],
    hide_windows = [ 'mouseup_2', 'h' ],
    launch_editor = [ 'E' ],
    dump_styles = [ ],
    reload_game = [ 'R', 'alt_shift_K_r' ],
    inspector = [ 'I' ],
    full_inspector = [ 'alt_shift_K_i' ],
    developer = [ 'D', 'alt_shift_K_d' ],
    quit = [ ],
    iconify = [ ],
    help = [  ],
    choose_renderer = [ 'G', 'alt_shift_K_g' ],
    progress_screen = [ 'alt_shift_K_p', 'meta_shift_K_p', 'K_F2' ],

    scroll_up = ["mousedown_4", "K_UP", "repeat_K_UP", "K_PAGEUP", "repeat_K_PAGEUP"],
    scroll_down = ["mousedown_5", "K_DOWN", "repeat_K_DOWN", "K_PAGEDOWN", "repeat_K_PAGEDOWN"],


    self_voicing = [ 'v', 'V', 'alt_K_v'  ],
    clipboard_voicing = [ 'C', 'alt_shift_K_c' ],
    debug_voicing = [ 'alt_shift_K_v', 'meta_shift_K_v' ],


    rollforward = [ 'mousedown_5', 'K_PAGEDOWN', 'repeat_K_PAGEDOWN' ],
    dismiss = [ 'mouseup_1', 'K_RETURN', 'K_SPACE', 'K_KP_ENTER', 'K_SELECT' ],
    dismiss_unfocused = [ ],


    dismiss_hard_pause = [ ],


    focus_left = [ 'K_LEFT', 'repeat_K_LEFT' ],
    focus_right = [ 'K_RIGHT', 'repeat_K_RIGHT' ],
    focus_up = [ 'K_UP', 'repeat_K_UP' ],
    focus_down = [ 'K_DOWN', 'repeat_K_DOWN' ],


    button_ignore = [ 'mousedown_1' ],
    button_select = [ 'mouseup_1', 'K_RETURN', 'K_KP_ENTER', 'K_SELECT' ],
    button_alternate = [ 'mouseup_3' ],
    button_alternate_ignore = [ 'mousedown_3' ],


    input_backspace = [ 'K_BACKSPACE', 'repeat_K_BACKSPACE' ],
    input_enter = [ 'K_RETURN', 'K_KP_ENTER' ],
    input_left = [ 'K_LEFT', 'repeat_K_LEFT' ],
    input_right = [ 'K_RIGHT', 'repeat_K_RIGHT' ],
    input_up = [ 'K_UP', 'repeat_K_UP' ],
    input_down = [ 'K_DOWN', 'repeat_K_DOWN' ],
    input_delete = [ 'K_DELETE', 'repeat_K_DELETE' ],
    input_home = [ 'K_HOME' ],
    input_end = [ 'K_END' ],


    viewport_leftarrow = [ 'K_LEFT', 'repeat_K_LEFT' ],
    viewport_rightarrow = [ 'K_RIGHT', 'repeat_K_RIGHT' ],
    viewport_uparrow = [ 'K_UP', 'repeat_K_UP' ],
    viewport_downarrow = [ 'K_DOWN', 'repeat_K_DOWN' ],
    viewport_wheelup = [ 'mousedown_4' ],
    viewport_wheeldown = [ 'mousedown_5' ],
    viewport_drag_start = [ 'mousedown_1' ],
    viewport_drag_end = [ 'mouseup_1' ],
    viewport_pageup = [  'K_PAGEUP', 'repeat_K_PAGEUP' ],
    viewport_pagedown = [  'K_PAGEDOWN', 'repeat_K_PAGEDOWN' ],


    skip = [ 'K_LCTRL', 'K_RCTRL' ],
    stop_skipping = [ ],
    toggle_skip = [ 'K_TAB' ],
    fast_skip = [ '>' ],


    bar_activate = [ 'mousedown_1', 'K_RETURN', 'K_KP_ENTER', 'K_SELECT' ],
    bar_deactivate = [ 'mouseup_1', 'K_RETURN', 'K_KP_ENTER', 'K_SELECT' ],
    bar_left = [ 'K_LEFT', 'repeat_K_LEFT' ],
    bar_right = [ 'K_RIGHT', 'repeat_K_RIGHT' ],
    bar_up = [ 'K_UP', 'repeat_K_UP' ],
    bar_down = [ 'K_DOWN', 'repeat_K_DOWN' ],


    save_delete = [ 'K_DELETE' ],


    drag_activate = [ 'mousedown_1' ],
    drag_deactivate = [ 'mouseup_1' ],


    console = [ 'shift_O', 'alt_shift_K_o' ],
    console_older = [ 'K_UP', 'repeat_K_UP' ],
    console_newer = [ 'K_DOWN', 'repeat_K_DOWN'],


    director = [ 'd' ],


    toggle_music = [ 'm' ],
    viewport_up = [ 'mousedown_4' ],
    viewport_down = [ 'mousedown_5' ],


    performance = [ 'K_F3' ],
    image_load_log = [ 'K_F4' ],
    profile_once = [ 'K_F8' ],
    memory_profile = [ 'K_F7' ],





    )

init -98 python hide:

    config.underlay = [
    renpy.Keymap(
      rollback = renpy.rollback,
      screenshot = _screenshot,
      toggle_fullscreen = renpy.toggle_fullscreen,
      toggle_afm = _keymap_toggle_afm,
      toggle_skip = _keymap_toggle_skipping,
      fast_skip = _fast_skip,
      game_menu = _invoke_game_menu,
      hide_windows = renpy.curried_call_in_new_context("_hide_windows"),
      launch_editor = _launch_editor,
      reload_game = _reload_game,
      developer = _developer,
      quit = renpy.quit_event,
      iconify = renpy.iconify,
      help = _help,
      choose_renderer = renpy.curried_call_in_new_context("_choose_renderer"),
      console = _console.enter,
      profile_once = _profile_once,
      memory_profile = _memory_profile,
      self_voicing = Preference("self voicing", "toggle"),
      clipboard_voicing = Preference("clipboard voicing", "toggle"),
      debug_voicing = Preference("debug voicing", "toggle"),
      progress_screen = _progress_screen,
      director = director.Start(),
      performance = ToggleScreen("_performance"),

    )
  ]
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
