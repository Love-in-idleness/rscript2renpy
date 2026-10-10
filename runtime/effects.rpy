transform dissolve_down_in:
    alpha 0.0
    yoffset -150
    linear 0.5 yoffset 0 alpha 1.0

transform dissolve_down_out:
    alpha 1.0
    yoffset 0
    linear 0.5 yoffset 150 alpha 0.0

transform dissolve_up_in:
    alpha 0.0
    yoffset 150
    linear 0.5 yoffset 0 alpha 1.0

transform dissolve_up_out:
    alpha 1.0
    yoffset 0
    linear 0.5 yoffset -150 alpha 0.0

transform dissolve_left_in:
    alpha 0.0
    xoffset 150
    linear 0.5 xoffset 0 alpha 1.0

transform dissolve_left_out:
    alpha 1.0
    xoffset 0
    linear 0.5 xoffset -150 alpha 0.0

transform dissolve_right_in:
    alpha 0.0
    xoffset -150
    linear 0.5 xoffset 0 alpha 1.0

transform dissolve_right_out:
    alpha 1.0
    xoffset 0
    linear 0.5 xoffset 150 alpha 0.0

transform dissolve_zoom_in(xpos, ypos, anchor):
    subpixel True
    transform_anchor True
    xpos xpos ypos ypos
    anchor anchor
    alpha 0.0
    zoom 1.25
    easein_cubic 0.5 alpha 1.0 zoom 1.0

transform dissolve_zoom_out(xpos, ypos, anchor):
    subpixel True
    transform_anchor True
    xpos xpos ypos ypos
    anchor anchor
    alpha 1.0
    zoom 1.0
    easein_cubic 0.5 alpha 0.0 zoom 1.25

define fast_dissolve = Dissolve(.2)
define rscript_slow_dissolve = Dissolve(2.0)
define rscript_dither = ImageDissolve(
    Tile("engine/gui/rscript_dither.svg"), 0.5, ramplen = 8)

transform oload_fade:
    alpha 0.0
    linear 0.2 alpha 1.0
    on hide:
        linear 0.2 alpha 0.0

transform rscript_white_in:
    shader "rscript.white"
    u_rscript_white 1.0
    linear 1.0 u_rscript_white 0.0

transform rscript_white_out:
    shader "rscript.white"
    u_rscript_white 0.0
    linear 1.0 u_rscript_white 1.0

transform rscript_grid_in:
    # shortcut: shared 1s cadence; calibrate against native playback if needed.
    mesh True
    shader "rscript.grid_wipe"
    u_rscript_grid 255.0
    linear 1.0 u_rscript_grid -1.0

transform rscript_grid_out:
    mesh True
    shader "rscript.grid_wipe"
    u_rscript_grid 0.0
    linear 1.0 u_rscript_grid 255.0



transform move_instant(xpos, ypos, anchor, dur):
    alpha 1.0
    xpos xpos
    ypos ypos
    anchor anchor

transform move_linear(xpos, ypos, anchor, dur):
    alpha 1.0
    linear dur xpos xpos ypos ypos anchor anchor

transform move_accel(xpos, ypos, anchor, dur):
    alpha 1.0
    easeout_cubic dur xpos xpos ypos ypos anchor anchor

transform move_decel(xpos, ypos, anchor, dur):
    alpha 1.0
    easein_cubic dur xpos xpos ypos ypos anchor anchor

transform move_shake_h(xpos, ypos, anchor, dur):
    alpha 1.0
    block:
        linear FRAME * 3 xoffset -(config.screen_width / 32)
        linear FRAME * 3 xoffset (config.screen_width / 32)
        repeat round(dur / (FRAME * 6)) - 1
    easeout FRAME * 3 xoffset 0

transform move_shake_h_sm(xpos, ypos, anchor, dur):
    alpha 1.0
    block:
        linear FRAME * 3 xoffset -(config.screen_width / 192)
        linear FRAME * 3 xoffset (config.screen_width / 192)
        repeat round(dur / (FRAME * 6)) - 1
    easeout FRAME * 3 xoffset 0

transform move_shake_v(xpos, ypos, anchor, dur):
    alpha 1.0
    block:
        linear FRAME * 3 yoffset -(config.screen_height / 32)
        linear FRAME * 3 yoffset (config.screen_height / 32)
        repeat round(dur / (FRAME * 6)) - 1
    easeout FRAME * 3 yoffset 0

transform move_shake_v_sm(xpos, ypos, anchor, dur):
    alpha 1.0
    block:
        linear FRAME * 3 yoffset -(config.screen_height / 192)
        linear FRAME * 3 yoffset (config.screen_height / 192)
        repeat round(dur / (FRAME * 6)) - 1
    easeout FRAME * 3 yoffset 0

transform rotate_zoom_in:
    transform_anchor True
    rotate 360
    zoom 0.0
    linear 0.5 rotate 0 zoom 1.0

transform rotate_zoom_out:
    transform_anchor True
    rotate 0
    zoom 1.0
    linear 0.5 rotate 360 zoom 0.0

transform rscript_zoom_in:
    transform_anchor True
    zoom 0.0
    linear 0.5 zoom 1.0

transform rscript_zoom_out:
    transform_anchor True
    zoom 1.0
    linear 0.5 zoom 0.0

transform rscript_exit_bottom_right(x, y, origin_anchor):
    xpos absolute(x) ypos absolute(y)
    anchor origin_anchor
    linear 0.5 xpos absolute(config.screen_width) ypos absolute(config.screen_height)

transform rotate_clockwise:
    transform_anchor True
    rotate 0
    linear 0.5 rotate 360



transform _zupdate_in(new_widget, old_widget, new_anchor):
    delay 0.5

    old_widget
    zoom 1.0
    align (0.5, 0.5)
    linear 0.2 zoom 10.0

    new_widget
    zoom 10.0
    align new_anchor
    linear 0.3 zoom 1.0

define zupdate_in = renpy.curry(_zupdate_in)



transform _instant(new_widget, old_widget):
    delay 0.0
    new_widget



transform _effect_start(img, xpos, ypos, anchor):
    img
    xpos xpos
    ypos ypos
    anchor anchor

transform _afterimage(start, trans, delay):
    pause delay
    start
    matrixcolor BrightnessMatrix(0.33)
    alpha 0.4
    parallel:
        trans
    parallel:
        linear 0.5 alpha 0.0 matrixcolor BrightnessMatrix(0.66)

transform afterimage(start, trans, frames=3):
    xpos 0 ypos 0 anchor (0, 0)








    contains:
        _afterimage(start, trans, FRAME * frames * 5)
    contains:
        _afterimage(start, trans, FRAME * frames * 4)
    contains:
        _afterimage(start, trans, FRAME * frames * 3)
    contains:
        _afterimage(start, trans, FRAME * frames * 2)
    contains:
        _afterimage(start, trans, FRAME * frames)
    contains:
        start
        trans


transform flash(color, time=0.05, count=3):
    color
    block:
        alpha 1.0
        pause time
        alpha 0.0
        pause time
        repeat count

transform flash_multi(color=None, time=0.05, count=3):
    "#FFFFFF"
    alpha 1.0
    pause time
    alpha 0.0
    pause time

    "#000FFF"
    alpha 1.0
    pause time
    alpha 0.0
    pause time

    "#FFFFFF"
    alpha 1.0
    pause time
    alpha 0.0
    pause time

    "#FE1800"
    alpha 1.0
    pause time
    alpha 0.0
    pause time

    "#FFFFFF"
    alpha 1.0
    pause time
    alpha 0.0
    pause time

    "#FFF000"
    alpha 1.0
    pause time
    alpha 0.0
    pause time

    repeat count



transform white_in:
    matrixcolor BrightnessMatrix(1.0)
    blur 8
    linear 0.5 blur 0 matrixcolor BrightnessMatrix(0.0)

transform white_out:
    matrixcolor BrightnessMatrix(0.0)
    blur 0
    linear 0.5 blur 8 matrixcolor BrightnessMatrix(1.0)



transform black_in:
    matrixcolor BrightnessMatrix(-1.0)
    blur 8
    linear 0.5 blur 0 matrixcolor BrightnessMatrix(0.0)

transform black_out:
    matrixcolor BrightnessMatrix(0.0)
    blur 0
    linear 0.5 blur 8 matrixcolor BrightnessMatrix(-1.0)



transform horiz_blur_in(img, xpos, ypos, anchor, color, center=0):
    shader "rscript.colormode"
    u_colormode color

    contains:
        img
        xpos xpos - 150
        ypos ypos
        anchor anchor
        alpha 0.0
        blur 8
        linear 0.5 xpos xpos alpha 1.0 blur 0
    contains:

        img
        xpos xpos + 150
        ypos ypos
        anchor anchor
        alpha 0.0
        blur 8
        linear 0.5 xpos xpos alpha 1.0 blur 0
    contains:

        img
        xpos xpos
        ypos ypos
        anchor anchor
        alpha 0.0
        blur 8
        linear 0.5 blur 0 alpha 1.0 * center

transform horiz_blur_out(img, xpos, ypos, anchor, color, center=0):
    shader "rscript.colormode"
    u_colormode color

    contains:
        img
        xpos xpos
        ypos ypos
        anchor anchor
        alpha 1.0
        blur 0
        linear 0.5 xpos xpos - 150 alpha 0.0 blur 8
    contains:

        img
        xpos xpos
        ypos ypos
        anchor anchor
        alpha 1.0
        blur 0
        linear 0.5 xpos xpos + 150 alpha 0.0 blur 8
    contains:

        img
        xpos xpos
        ypos ypos
        anchor anchor
        alpha 1.0 * center
        blur 0
        linear 0.5 blur 8 alpha 0.0



transform vert_blur_in(img, xpos, ypos, anchor, color, center=0):
    shader "rscript.colormode"
    u_colormode color

    contains:
        img
        xpos xpos
        ypos ypos - 100
        anchor anchor
        alpha 0.0
        blur 8
        linear 0.5 ypos ypos alpha 1.0 blur 0
    contains:

        img
        xpos xpos
        ypos ypos + 100
        anchor anchor
        alpha 0.0
        blur 8
        linear 0.5 ypos ypos alpha 1.0 blur 0
    contains:

        img
        xpos xpos
        ypos ypos
        anchor anchor
        alpha 0.0
        blur 8
        linear 0.5 blur 0 alpha 1.0 * center


transform vert_blur_out(img, xpos, ypos, anchor, color, center=0):
    shader "rscript.colormode"
    u_colormode color

    contains:
        img
        xpos xpos
        ypos ypos
        anchor anchor
        alpha 1.0
        blur 0
        linear 0.5 ypos ypos - 100 alpha 0.0 blur 8
    contains:

        img
        xpos xpos
        ypos ypos
        anchor anchor
        alpha 1.0
        blur 0
        linear 0.5 ypos ypos + 100 alpha 0.0 blur 8
    contains:

        img
        xpos xpos
        ypos ypos
        anchor anchor
        alpha 1.0 * center
        blur 0
        linear 0.5 blur 8 alpha 0.0




transform grayscale(img):
    img
    matrixcolor SaturationMatrix(0, desat = (85 / 256., 86 / 256., 85 / 256.))



init python:

    def rscript_clear_frame(effect, tick):
        import math
        if effect == 31:
            remaining = max(0, 10 - tick)
            angle = (0x4000 // 9) * min(9, remaining) // 255
            offset = 0 if tick == 0 else 150 - int(150 * int(math.sin(angle * math.tau / 256) * 65535) / 65535)
            return (max(0., 1 - min(256, tick * 16) / 256.), offset, 0, 1)
        if effect == 34:
            if tick == 0:
                return (1, 0, 0, 1)
            level = max(0, 254 - tick * 12)
            remaining = max(0, 21 - tick)
            angle = (390 - ((0x8800 // 20 + 2) * remaining // 255)) % 255
            offset = int(-250 * int(math.sin(angle * math.tau / 256) * 65535) / 65535) if remaining else 0
            return (float(level > 0), offset, -level * 360 / 256., max(1, level * 100 // 256) / 100.)
        raise ValueError("Unsupported native clear effect: %s" % effect)

    class RScriptClearExit(renpy.Displayable):
        def __init__(self, child, effect, pos=(0, 0), anchor=(0, 0)):
            super(RScriptClearExit, self).__init__()
            self.child, self.effect = renpy.displayable(child), effect
            self.pos, self.anchor = pos, anchor

        def render(self, width, height, st, at):
            source = renpy.render(self.child, width, height, st, at)
            w, h = map(int, source.get_size())
            left, top = self.pos[0] - w * self.anchor[0], self.pos[1] - h * self.anchor[1]
            alpha, offset, angle, zoom = rscript_clear_frame(self.effect, int(st / .05 + 1e-9))
            if self.effect == 31:
                split = w // 2
                # shortcut: odd-width native split has a one-pixel seam; calibrate if a game uses it.
                children = [Transform(self.child, crop=(0, 0, split, h),
                                      pos=(absolute(left), absolute(top + offset)), alpha=alpha),
                            Transform(self.child, crop=(split, 0, w - split, h),
                                      pos=(absolute(left + split), absolute(top - offset)), alpha=alpha)]
            else:
                children = [Transform(self.child, anchor=(.5, .5), zoom=zoom, rotate=angle,
                                      pos=(absolute(left + w / 2.), absolute(top + h / 2. + offset)), alpha=alpha)]
            # Keep displaced fragments in source-space coordinates on the game canvas.
            result = renpy.render(Fixed(*children, xysize=(config.screen_width, config.screen_height)), width, height, st, at)
            if alpha:
                renpy.redraw(self, .05)
            return result

        def visit(self):
            return [self.child]

    def rscript_zoom_crop(width, height, locate, level):
        # startup_jp.exe 43ba20 / 4542c0: keypad centre, clamped integer crop.
        anchors = ((.5, .5), (0, 1), (.5, 1), (1, 1), (0, .5),
                   (.5, .5), (1, .5), (0, 0), (.5, 0), (1, 0))
        x, y = anchors[locate] if 0 <= locate <= 9 else anchors[0]
        w, h = max(1, width * 100 // (100 + level)), max(1, height * 100 // (100 + level))
        return (min(width - w, max(0, int(width * x) - w // 2)),
                min(height - h, max(0, int(height * y) - h // 2)), w, h)

    class RScriptCompoundZoom(renpy.display.transition.Transition):
        def __init__(self, effect, old_widget=None, new_widget=None):
            kind, anchors = divmod(effect, 100)
            if kind not in (1, 2):
                raise ValueError("Unsupported compound update: %s" % effect)
            self.increment, self.limit = (20, 600) if kind == 1 else (50, 2000)
            self.frames = self.limit // self.increment + 1
            super(RScriptCompoundZoom, self).__init__(self.frames * .010)
            self.old_widget, self.new_widget = old_widget, new_widget
            self.old_locate, self.new_locate = divmod(anchors, 10)
            self.events = False

        def render(self, width, height, st, at):
            if st >= self.delay or renpy.game.less_updates:
                return renpy.display.transition.null_render(self, width, height, st, at)
            frame = min(2 * self.frames - 1, int(st / .005))
            second = frame >= self.frames
            index = frame - self.frames if second else frame
            level = self.limit - index * self.increment if second else index * self.increment
            widget = self.new_widget if second else self.old_widget
            crop = rscript_zoom_crop(width, height,
                                    self.new_locate if second else self.old_locate, level)
            image = Transform(widget, crop=crop, xysize=(width, height))
            result = renpy.render(image, width, height, st, at)
            renpy.redraw(self, .005)
            return result

    def rscript_update_duration(effect, step, wait):
        if store.rscript_update_timing == "codex-ms":
            if 100 <= effect < 300:
                return .310 if effect < 200 else .410
            # Native 43b390: zero selects 10 steps; waits are milliseconds.
            step = step or 10
            if effect == 2:
                frames = max(0, step - 1)
            elif effect >= 11:
                frames = 2 * step - 1
            else:
                frames = step + 1
            return frames * wait / 1000.0
        if store.rscript_update_timing == "legacy":
            return step * wait / 100.0 * (2 if effect >= 11 else 1)
        raise ValueError("Unknown RScript update timing: %s" % store.rscript_update_timing)

    def rscript_arc_position(start, end, fraction, direction):
        import math
        angle = math.pi * min(1.0, max(0.0, fraction))
        dx, dy = (end[0] - start[0]) / 2., (end[1] - start[1]) / 2.
        return (start[0] + dx * (1 - math.cos(angle)) - direction * dy * math.sin(angle),
                start[1] + dy * (1 - math.cos(angle)) + direction * dx * math.sin(angle))

    def rscript_arc_move(start, end, anchor, dur, direction, trans, st, at):
        trans.xpos, trans.ypos = map(absolute, rscript_arc_position(start, end, st / max(dur, .001), direction))
        trans.anchor = anchor
        return 0 if st < dur else None

    def rscript_layer_visibility(layer, trans, st, at):
        # Keep the loaded image and its effects; enabl is visibility, not cls.
        trans.alpha = float(bool(store.layer_enabled.get(layer, 1)))
        trans.u_blendmode, trans.u_blendlevel = store.layer_blend.get(layer, (0, 0))
        return .05

    def rscript_show_layer(name, at_list=None, **kwargs):
        transforms = list(at_list or [])
        if name.startswith("layer") and name[5:].isdigit():
            number = int(name[5:])
            # Moves/effects must retain native depth, not renpy.show's default 0.
            kwargs.setdefault("zorder", store.layer_zorder.get(number, number * 2))
            visibility = (RScriptRasterVisibility if isinstance(kwargs.get("what"), renpy.display.image.ImageReference)
                          else renpy.curry(rscript_layer_visibility))
            transforms.append(Transform(shader="rscript.blend", u_blendmode=0, u_blendlevel=0,
                                        function=visibility(number)))
        renpy.show(name, at_list=transforms, **kwargs)

    def rscript_selected_layers(layer):
        if layer == 0:
            return sorted(num for num in store.layer_info
                          if isinstance(num, int) and 1 <= num < 100)
        if isinstance(layer, int) and layer > 100:
            # Native 43bfc0 / 43c8d0: hundreds select a group by remainder.
            return [num for num in range(1, 100)
                    if store.layer_groups.get(num, 0) == layer % 100]
        return [layer]

    def rscript_apply_layers(layer, function, *args, **kwargs):
        queued = store.in_queue
        delayed_start = len(store.draw_queue_delayed)
        store.in_queue = True
        try:
            for selected in rscript_selected_layers(layer):
                function(selected, *args, **kwargs)
            # A scene transition applies to the whole batch, not once per object.
            transitions = []
            operations = []
            for operation in store.draw_queue_delayed[delayed_start:]:
                if operation[0] == renpy.with_statement:
                    if operation in transitions:
                        continue
                    transitions.append(operation)
                operations.append(operation)
            store.draw_queue_delayed[delayed_start:] = operations
        finally:
            store.in_queue = queued
        process_draw_queue()

    def loadcls(layer, effect, cg = None, xpos = 0, ypos = 0, color = 0, clear = False, displayable = None):

        if clear and (layer == 0 or layer > 100):
            rscript_apply_layers(layer, loadcls, effect, clear=True)
            return

        if clear and store.rscript_click_native_effects:
            # Native Khime 4067ce -> 406a90 resets both links even in a queue.
            execute_resetclk(RScriptArguments(Layer=layer))

        anchor = layer_anchor.get(layer, (0.0, 0.0))

        if not clear:
            xpos = xpos * store.layer_x_grid
            ypos = ypos * store.layer_y_grid
        else:
            xpos, ypos = store.layer_pos.get(layer, (0.0, 0.0))

        # RScript coordinates are pixels even after a fractional locgrid scale.
        # Bare floats are *relative* positions in Ren'Py, not pixel offsets.
        xpos, ypos = absolute(xpos), absolute(ypos)

        trans = Transform(
      xpos = xpos,
      ypos = ypos,
      anchor = anchor,
      shader = "rscript.colormode",
      u_colormode = color,
    )

        at_list = [
      trans,
    ]

        zorder = layer_zorder.get(layer, layer * 2)
        tag = "layer%d" % layer




        def _queue_load():
            if not clear:
                img = displayable if displayable is not None else "%s %04d" % (folder[layer], cg)
                store.layer_info[layer] = img
                store.layer_pos[layer] = (xpos or 0, ypos or 0)
                queue_draw(rscript_show_layer, tag, what = renpy.displayable(img),
                           at_list = at_list, zorder = zorder, layer = IMAGE_LAYER)


            else:
                if layer in store.layer_info:
                    del store.layer_info[layer]

                if layer in store.layer_pos:
                    del store.layer_pos[layer]

                queue_draw(renpy.hide, tag, layer = IMAGE_LAYER)

        if store.in_queue:
            queue_ef = queue_draw_delayed

        else:
            queue_ef = queue_draw





        if effect == 0:
            if displayable is not None:
                at_list.append(oload_fade)
            _queue_load()





        elif effect == 1:
            if not clear:
                at_list.append(rscript_zoom_in)
                _queue_load()
                queue_ef_pause(0.5)

            elif layer in store.layer_info:
                img = store.layer_info.pop(layer)
                store.layer_pos.pop(layer, None)
                queue_draw(rscript_show_layer, tag, what = renpy.displayable(img),
                           at_list = [trans, rscript_zoom_out], layer = IMAGE_LAYER)
                queue_ef_pause(0.5)
                queue_draw_delayed(renpy.hide, tag, layer = IMAGE_LAYER)


        elif effect == 2:
            _queue_load()
            queue_ef(renpy.with_statement, fast_dissolve)

        elif effect == 3:
            _queue_load()
            queue_ef(renpy.with_statement, dissolve)

        elif effect == 4:
            _queue_load()
            queue_ef(renpy.with_statement, rscript_dither)


        elif effect in (5, 6):
            if not clear:
                at_list.append(white_in if effect == 5 else black_in)
                _queue_load()
                queue_ef_pause(0.5)
            elif layer in store.layer_info:
                # Keep the artwork visible until its outgoing transform ends.
                at_list.append(white_out if effect == 5 else black_out)
                queue_draw(rscript_show_layer, tag,
                           what=renpy.displayable(store.layer_info[layer]),
                           at_list=at_list, zorder=zorder, layer=IMAGE_LAYER)
                queue_ef_pause(0.5)
                queue_draw_delayed(renpy.hide, tag, layer=IMAGE_LAYER)

        elif effect == 7:
            _queue_load()
            queue_ef(renpy.with_statement, moveoutleft if clear else moveinleft)

        elif effect == 8:
            _queue_load()
            queue_ef(renpy.with_statement, moveoutright if clear else moveinright)

        elif effect == 9:
            _queue_load()
            queue_ef(renpy.with_statement, moveouttop if clear else moveintop)

        elif effect == 10:
            _queue_load()
            queue_ef(renpy.with_statement, moveoutbottom if clear else moveinbottom)

        elif effect == 14 and clear:
            # Native 43a9a0 -> 410660 -> 411b10 case 14 (411f6a).
            # Target is the canvas bottom-right; retain shared animation timing.
            if layer in store.layer_info:
                queue_draw(rscript_show_layer, tag,
                           what=renpy.displayable(store.layer_info[layer]),
                           at_list=[trans, rscript_exit_bottom_right(xpos, ypos, anchor)],
                           zorder=zorder, layer=IMAGE_LAYER)
                queue_ef_pause(0.5)
                queue_draw_delayed(renpy.hide, tag, layer=IMAGE_LAYER)

        elif effect in (15, 17):
            # White fade / native 16-pixel grid wipe; both use level step 16.
            fade_in = rscript_white_in if effect == 15 else rscript_grid_in
            fade_out = rscript_white_out if effect == 15 else rscript_grid_out
            if not clear:
                at_list.append(fade_in)
                _queue_load()
                queue_ef_pause(1.0)
            elif layer in store.layer_info:
                img = store.layer_info.pop(layer)
                store.layer_pos.pop(layer, None)
                queue_draw(rscript_show_layer, tag, what = renpy.displayable(img),
                           at_list = [trans, fade_out],
                           zorder = zorder, layer = IMAGE_LAYER)
                queue_ef_pause(1.0)
                queue_draw_delayed(renpy.hide, tag, layer = IMAGE_LAYER)

        elif effect == 19:
            # Alpha step 8 versus effect 3's 32: four times the fade duration.
            _queue_load()
            queue_ef(renpy.with_statement, rscript_slow_dissolve)


        elif effect == 16:

            dissolve_zoom = dissolve_zoom_in if not clear else dissolve_zoom_out



            if xpos == 0 and ypos == 0 and anchor == (0.0, 0.0):
                ef = dissolve_zoom(0.5, 0.5, (0.5, 0.5))

            else:
                ef = dissolve_zoom(xpos, ypos, anchor)

            if not clear:
                at_list.append(ef)
                _queue_load()
                queue_ef_pause(0.5)

            elif layer in store.layer_info:
                queue_draw(rscript_show_layer, tag, what = renpy.displayable(store.layer_info[layer]), at_list = [ef], layer = IMAGE_LAYER)
                queue_ef_pause(0.5)
                queue_draw_delayed(renpy.hide, tag, layer = IMAGE_LAYER)


        elif effect in [20, 21, 22, 23]:
            ef = {
        20: dissolve_down_in if not clear else dissolve_down_out,
        21: dissolve_up_in if not clear else dissolve_up_out,
        22: dissolve_right_in if not clear else dissolve_right_out,
        23: dissolve_left_in if not clear else dissolve_left_out,
      }[effect]

            if not clear:
                at_list.append(ef)
                _queue_load()
                queue_ef_pause(0.5)

            elif layer in store.layer_info:
                queue_draw(rscript_show_layer, tag, what = renpy.displayable(store.layer_info[layer]), at_list = [ef], layer = IMAGE_LAYER)
                queue_ef_pause(0.5)
                queue_draw_delayed(renpy.hide, tag, layer = IMAGE_LAYER)

        elif effect in [24, 25, 26, 27]:
            ef = {
        24: vert_blur_in if not clear else vert_blur_out,
        25: horiz_blur_in if not clear else horiz_blur_out,
        26: vert_blur_in if not clear else vert_blur_out,
        27: horiz_blur_in if not clear else horiz_blur_out,
      }[effect]

            center = 0
            if effect in [26, 27]:
                center = 1

            if not clear:
                img = displayable if displayable is not None else "%s %04d" % (folder[layer], cg)
                ef = ef(img, xpos, ypos, anchor, color, center)

                at_list = [ef]
                _queue_load()
                queue_ef_pause(0.5)
                queue_draw_delayed(rscript_show_layer, tag, what = renpy.displayable(store.layer_info[layer]), at_list = [trans], layer = IMAGE_LAYER)

            elif layer in store.layer_info:
                ef = ef(store.layer_info[layer], xpos, ypos, anchor, color, center)

                queue_draw(rscript_show_layer, tag, what = renpy.displayable(store.layer_info[layer]), at_list = [ef], layer = IMAGE_LAYER)
                queue_ef_pause(0.5)
                queue_draw_delayed(renpy.hide, tag, layer = IMAGE_LAYER)

        elif clear and effect in (31, 34):
            if layer in store.layer_info:
                trans.pos, trans.anchor = (absolute(0), absolute(0)), (0, 0)
                queue_draw(rscript_show_layer, tag,
                           what=RScriptClearExit(store.layer_info[layer], effect, (xpos, ypos), anchor),
                           at_list=[trans], zorder=zorder, layer=IMAGE_LAYER)
                queue_ef_pause(.8 if effect == 31 else 1.1)
                queue_draw_delayed(renpy.hide, tag, layer=IMAGE_LAYER)

        elif effect == 28:
            if not clear:
                at_list.append(rotate_zoom_in)
                _queue_load()
                queue_ef_pause(0.5)

            elif layer in store.layer_info:
                img = store.layer_info.pop(layer)
                store.layer_pos.pop(layer, None)
                queue_draw(rscript_show_layer, tag, what = renpy.displayable(img),
                           at_list = [trans, rotate_zoom_out], layer = IMAGE_LAYER)
                queue_ef_pause(0.5)
                queue_draw_delayed(renpy.hide, tag, layer = IMAGE_LAYER)

        else:
            raise Exception("Unhandled load/clear effect %d" % effect)

        if clear:
            store.layer_info.pop(layer, None)
            store.layer_pos.pop(layer, None)
        process_draw_queue()


    def rotate_layer(layer):
        if layer not in store.layer_info:
            return

        img = store.layer_info[layer]
        xpos, ypos = store.layer_pos.get(layer, (0, 0))
        anchor = store.layer_anchor.get(layer, (0.0, 0.0))
        tag = "layer%d" % layer
        stable = Transform(xpos = xpos, ypos = ypos, anchor = anchor)

        queue_draw(rscript_show_layer, tag, what = renpy.displayable(img),
                   at_list = [stable, rotate_clockwise], layer = IMAGE_LAYER)
        queue_ef_pause(0.5)
        queue_draw_extra_delayed(rscript_show_layer, tag, what = renpy.displayable(img),
                                 at_list = [stable], layer = IMAGE_LAYER)
        process_draw_queue()



    def move_layer(layer, x, y, effect, speed, relative = False):
        if isinstance(layer, int) and (layer == 0 or layer > 100):
            rscript_apply_layers(layer, move_layer, x, y, effect, speed, relative=relative)
            return

        if isinstance(layer, (int, float)):
            tag = "layer%d" % layer
            layer_name = IMAGE_LAYER

        else:
            tag = CG_TAG
            layer_name = CG_LAYER

        if layer not in store.layer_info:
            return

        img = store.layer_info[layer]
        dur = 0.5 if speed == 0 else speed / 16.0

        xpos, ypos = store.layer_pos.get(layer, (0, 0))
        origin = (xpos, ypos)
        anchor = layer_anchor.get(layer, (0.0, 0.0))



        with_afterimage = False
        start = None

        if effect > 100:
            effect -= 100
            with_afterimage = True
            start = _effect_start(img, xpos, ypos, anchor)



        if not relative:
            xpos = x * store.layer_x_grid
            ypos = y * store.layer_y_grid

        else:
            xpos += x * store.layer_x_grid
            ypos += y * store.layer_y_grid



        xpos, ypos = absolute(xpos), absolute(ypos)
        store.layer_pos[layer] = (xpos, ypos)

        effects = {
      0: move_instant,
      1: move_linear,
      2: move_accel,
      3: move_decel,
      7: move_shake_v,
      8: move_shake_v_sm,
      9: move_shake_h,
      10: move_shake_h_sm,
    }

        if effect not in effects and effect not in (5, 6):
            raise Exception("Move effect %d not defined." % effect)

        # Replacing _oload's fade must not inherit its initial alpha=0.
        trans = Transform(xpos = xpos, ypos = ypos, anchor = anchor, alpha = 1.0)
        if effect in (5, 6):
            # Native 413e40 -> 44d3c0: opposite half-circle paths, not shakes.
            ef = Transform(alpha=1.0, function=renpy.curry(rscript_arc_move)(
                origin, (xpos, ypos), anchor, dur, 1 if effect == 5 else -1))
        else:
            ef = effects[effect](xpos, ypos, anchor, dur)



        if with_afterimage:
            ef = afterimage(start, ef)


        queue_draw(rscript_show_layer, tag, what = renpy.displayable(img), at_list = [ef], layer = layer_name)
        if effect > 0:
            queue_ef_pause(dur)
        queue_draw_extra_delayed(rscript_show_layer, tag, what = renpy.displayable(img), at_list = [trans], layer = layer_name)
        process_draw_queue()



    def rscript_ef(effect, step, wait):



        return ImageDissolve(rscript_image_path("grps/ef%02d.png" % effect),
                            rscript_update_duration(effect, step, wait),
                            ramplen = 64, reverse = True)



    def quake(dur, x = 48, y = 36):
        seed = renpy.time.time()
        for layer in QUAKE_LAYERS:
            renpy.show_layer_at(Shake(None, dur, x_dist = x, y_dist = y, seed = seed), layer)
        renpy.pause(dur)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
