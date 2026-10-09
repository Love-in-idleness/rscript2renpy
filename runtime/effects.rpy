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



transform move_instant(xpos, ypos, anchor, dur):
    xpos xpos
    ypos ypos
    anchor anchor

transform move_linear(xpos, ypos, anchor, dur):
    linear dur xpos xpos ypos ypos anchor anchor

transform move_accel(xpos, ypos, anchor, dur):
    easeout_cubic dur xpos xpos ypos ypos anchor anchor

transform move_decel(xpos, ypos, anchor, dur):
    easein_cubic dur xpos xpos ypos ypos anchor anchor

transform move_shake_h(xpos, ypos, anchor, dur):
    block:
        linear FRAME * 3 xoffset -(config.screen_width / 32)
        linear FRAME * 3 xoffset (config.screen_width / 32)
        repeat round(dur / (FRAME * 6)) - 1
    easeout FRAME * 3 xoffset 0

transform move_shake_h_sm(xpos, ypos, anchor, dur):
    block:
        linear FRAME * 3 xoffset -(config.screen_width / 192)
        linear FRAME * 3 xoffset (config.screen_width / 192)
        repeat round(dur / (FRAME * 6)) - 1
    easeout FRAME * 3 xoffset 0

transform move_shake_v(xpos, ypos, anchor, dur):
    block:
        linear FRAME * 3 yoffset -(config.screen_height / 32)
        linear FRAME * 3 yoffset (config.screen_height / 32)
        repeat round(dur / (FRAME * 6)) - 1
    easeout FRAME * 3 yoffset 0

transform move_shake_v_sm(xpos, ypos, anchor, dur):
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

    def rscript_update_duration(effect, step, wait):
        if store.rscript_update_timing == "codex-ms":
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
        return 0.1

    def rscript_show_layer(name, at_list=None, **kwargs):
        transforms = list(at_list or [])
        if name.startswith("layer") and name[5:].isdigit():
            visibility = (RScriptRasterVisibility if isinstance(kwargs.get("what"), renpy.display.image.ImageReference)
                          else renpy.curry(rscript_layer_visibility))
            transforms.append(Transform(function=visibility(int(name[5:]))))
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

        anchor = layer_anchor.get(layer, (0.0, 0.0))

        if not clear:
            xpos = xpos * store.layer_x_grid
            ypos = ypos * store.layer_y_grid
        else:
            xpos, ypos = store.layer_pos.get(layer, (0.0, 0.0))

        # RScript coordinates are pixels even after a fractional locgrid scale.
        # Bare floats are *relative* positions in Ren'Py, not pixel offsets.
        xpos, ypos = absolute(xpos), absolute(ypos)

        blend_mode, blend_level = store.layer_blend.get(layer, (0, 0))

        trans = Transform(
      xpos = xpos,
      ypos = ypos,
      anchor = anchor,
      shader = ["rscript.blend", "rscript.colormode"],
      u_blendmode = blend_mode,
      u_blendlevel = blend_level,
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

        elif effect == 15:
            # Khime 0x40771d / 0x408485: white RGB fade, alpha step 16.
            if not clear:
                at_list.append(rscript_white_in)
                _queue_load()
                queue_ef_pause(1.0)
            elif layer in store.layer_info:
                img = store.layer_info.pop(layer)
                store.layer_pos.pop(layer, None)
                queue_draw(rscript_show_layer, tag, what = renpy.displayable(img),
                           at_list = [trans, rscript_white_out],
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

        trans = Transform(xpos = xpos, ypos = ypos, anchor = anchor)
        if effect in (5, 6):
            # Native 413e40 -> 44d3c0: opposite half-circle paths, not shakes.
            ef = Transform(function=renpy.curry(rscript_arc_move)(
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
