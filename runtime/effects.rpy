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

    def loadcls(layer, effect, cg = None, xpos = 0, ypos = 0, color = 0, clear = False):

        anchor = layer_anchor.get(layer, (0.0, 0.0))

        if not clear:
            xpos = xpos * store.layer_x_grid
            ypos = ypos * store.layer_y_grid
        else:
            xpos, ypos = store.layer_pos.get(layer, (0.0, 0.0))

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
                img = "%s %04d" % (folder[layer], cg)
                store.layer_info[layer] = img
                store.layer_pos[layer] = (xpos or 0, ypos or 0)
                queue_draw(renpy.show, img, at_list = at_list, zorder = zorder, tag = tag, layer = IMAGE_LAYER)


            elif layer == 0:

                numeric_layers = [num for num in store.layer_info
                                  if isinstance(num, (int, float))]
                for num in numeric_layers:
                    queue_draw(renpy.hide, "layer%d" % num, layer = IMAGE_LAYER)
                    store.layer_info.pop(num, None)
                    store.layer_pos.pop(num, None)

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
            _queue_load()





        elif effect == 3:
            _queue_load()
            queue_ef(renpy.with_statement, dissolve)


        elif effect == 5:
            at_list.append(white_in if not clear else white_out)
            _queue_load()
            queue_ef_pause(0.5)


        elif effect == 6:
            at_list.append(black_in if not clear else black_out)
            _queue_load()
            queue_ef_pause(0.5)

        elif effect == 7:
            _queue_load()
            queue_ef(renpy.with_statement, moveinleft)

        elif effect == 8:
            _queue_load()
            queue_ef(renpy.with_statement, moveinright)


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
                queue_draw(renpy.show, store.layer_info[layer], at_list = [ef], tag = tag, layer = IMAGE_LAYER)
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
                queue_draw(renpy.show, store.layer_info[layer], at_list = [ef], tag = tag, layer = IMAGE_LAYER)
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
                ef = ef("%s %04d" % (folder[layer], cg), xpos, ypos, anchor, color, center)

                at_list = [ef]
                _queue_load()
                queue_ef_pause(0.5)
                queue_draw_delayed(renpy.show, store.layer_info[layer], at_list = [trans], tag = tag, layer = IMAGE_LAYER)

            elif layer in store.layer_info:
                ef = ef(store.layer_info[layer], xpos, ypos, anchor, color, center)

                queue_draw(renpy.show, store.layer_info[layer], at_list = [ef], tag = tag, layer = IMAGE_LAYER)
                queue_ef_pause(0.5)
                queue_draw_delayed(renpy.hide, tag, layer = IMAGE_LAYER)

        else:
            raise Exception("Unhandled load/clear effect %d" % effect)

        process_draw_queue()



    def move_layer(layer, x, y, effect, speed, relative = False):
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

        if not effect in effects:
            raise Exception("Move effect %d not defined." % effect)

        trans = Transform(xpos = xpos, ypos = ypos, anchor = anchor)
        ef = effects[effect]
        ef = ef(xpos, ypos, anchor, dur)



        if with_afterimage:
            ef = afterimage(start, ef)


        queue_draw(renpy.show, img, at_list = [ef], tag = tag, layer = layer_name)
        if effect > 0:
            queue_ef_pause(dur)
        queue_draw_extra_delayed(renpy.show, img, at_list = [trans], tag = tag, layer = layer_name)
        process_draw_queue()



    def rscript_ef(effect, step, wait):



        ef_time = step * wait / 1000.

        return ImageDissolve("images/grps/ef%02d.png" % effect, ef_time * 2, ramplen = 64, reverse = True)



    def quake(dur, x = 48, y = 36):
        seed = renpy.time.time()
        for layer in QUAKE_LAYERS:
            renpy.show_layer_at(Shake(None, dur, x_dist = x, y_dist = y, seed = seed), layer)
        renpy.pause(dur)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
