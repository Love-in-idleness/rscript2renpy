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

transform rscript_grid_in(vertical=False):
    mesh True
    shader ("rscript.column_wipe" if vertical else "rscript.grid_wipe")
    function renpy.curry(rscript_grid_frame)(False)

transform rscript_grid_out(vertical=False):
    mesh True
    shader ("rscript.column_wipe" if vertical else "rscript.grid_wipe")
    function renpy.curry(rscript_grid_frame)(True)



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

    def rscript_grid_frame(clear, trans, st, at):
        tick = int(st / rscript_dynamic_tick + 1e-9)
        trans.u_rscript_grid = min(255, 16 * tick) if clear else max(-1, 255 - 16 * tick)
        return rscript_dynamic_tick if tick < 16 else None

    def rscript_dynamic_position(path, elapsed):
        import math
        start, end, steps, sine = path
        tick = int(elapsed / rscript_dynamic_tick + 1e-9)
        if not steps or tick > steps:
            return end
        if tick == 0:
            return start
        # 44d070 / 44d880: quantized Q16 sin/cos table, then truncating division.
        index = ((0x4000 // steps) * (steps - tick + 1) // 255) % 255
        angle = index / 256.0 * 6.283185308
        sample = int((math.sin(angle) if sine else math.cos(angle)) * 65535)
        if sine:
            return tuple(b + int((a - b) * sample / 65535) for a, b in zip(start, end))
        return tuple(a + int((b - a) * sample / 65535) for a, b in zip(start, end))

    def rscript_trunc_div(value, divisor):
        return value // divisor if value >= 0 else -((-value) // divisor)

    def rscript_wave_path(start, end, speed):
        import math
        delta = tuple(b - a for a, b in zip(start, end))
        distance = math.isqrt(sum(d * d for d in delta))
        if rscript_move4_timing == "fixed-speed":
            pixels = 30
        else:
            count = 15 if rscript_move4_timing == "fixed-steps" else (int(speed) & 0xffff) or 15
            pixels = max(1, (distance // count) & 0xffff)
        steps = (distance // pixels) & 0xffff
        velocity = tuple(rscript_trunc_div(d * 65535, steps) for d in delta) if steps else (0, 0)
        perpendicular = tuple(rscript_trunc_div(d * 3, 20) for d in (delta[1], -delta[0]))
        phase = ((2 * 65535) // steps) & 0xffff if steps else 0
        return start, end, steps, velocity, perpendicular, phase

    def rscript_wave_position(path, elapsed):
        import math
        start, end, steps, velocity, perpendicular, phase = path
        tick = int(elapsed / rscript_dynamic_tick + 1e-9)
        if not steps or tick == 0:
            return start
        if tick > steps:
            return end
        remaining = steps - tick + 1
        index = (phase * remaining // 255) % 255
        sample = int(math.sin(index / 256.0 * 6.283185308) * 65535)
        return tuple(b - rscript_trunc_div(v * remaining, 65535) +
                     rscript_trunc_div(p * sample, 65535)
                     for b, v, p in zip(end, velocity, perpendicular))

    def rscript_wave_move(path, anchor, grid, trans, st, at):
        x, y = rscript_wave_position(path, st)
        trans.pos = (absolute(x * grid[0]), absolute(y * grid[1]))
        trans.anchor = anchor
        return rscript_dynamic_tick if st < (path[2] + 1) * rscript_dynamic_tick else None

    def rscript_diagonal_path(effect, size, pos, anchor, clear):
        import math
        w, h = size
        normal = (pos[0] - w * anchor[0], pos[1] - h * anchor[1])
        corner = ((-w, -h), (config.screen_width, -h),
                  (-w, config.screen_height), (config.screen_width, config.screen_height))[effect - 11]
        start, end = (normal, corner) if clear else (corner, normal)
        distance = int(math.hypot(end[0] - start[0], end[1] - start[1]))
        speed = (distance & 0xffff) // 15
        steps = (distance // speed) & 0xffff if speed else 0
        # A zero native speed leaves the object at its initial position.
        return start, end if speed else start, steps, False

    class RScriptDiagonal(renpy.Displayable):
        def __init__(self, child, effect, pos, anchor, clear):
            super(RScriptDiagonal, self).__init__()
            self.child = renpy.displayable(child)
            self.effect, self.pos, self.anchor, self.clear = effect, pos, anchor, clear

        def path(self):
            source = renpy.render(self.child, config.screen_width, config.screen_height, 0, 0)
            return rscript_diagonal_path(self.effect, source.get_size(), self.pos, self.anchor, self.clear)

        def render(self, width, height, st, at):
            path = self.path()
            x, y = rscript_dynamic_position(path, st)
            image = Transform(self.child, xpos=absolute(x), ypos=absolute(y))
            result = renpy.render(Fixed(image, xysize=(config.screen_width, config.screen_height)), width, height, st, at)
            if st < (path[2] + 1) * rscript_dynamic_tick:
                renpy.redraw(self, rscript_dynamic_tick)
            return result

        def visit(self):
            return [self.child]

    def rscript_queue_diagonal_pause(motion):
        _queue_ef_pause((motion.path()[2] + 1) * rscript_dynamic_tick)

    def rscript_finish_diagonal(tag, motion, trans, zorder):
        if motion.path()[2]:
            rscript_show_layer(tag, what=motion.child, at_list=[trans],
                               zorder=zorder, layer=IMAGE_LAYER)

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

    class RScriptOrderedDissolve(renpy.display.transition.Transition):
        # Same 4x4 table in Forest, Khime, Evermaiden, CannonBall and Kagerou.
        masks = (0xffdf, 0xefdf, 0x6fdf, 0x6fd7, 0x6bd7, 0x6bd6, 0x6b56, 0x6a56,
                 0x2a56, 0x2a52, 0x0a52, 0x0a12, 0x0812, 0x0810, 0x0800, 0)

        def __init__(self, duration, steps, old_widget=None, new_widget=None):
            if steps < 1:
                raise ValueError("Invalid native ordered dissolve parameters")
            super(RScriptOrderedDissolve, self).__init__(duration)
            self.steps = steps
            self.old_widget, self.new_widget = old_widget, new_widget
            self.events = False

        def mask_at(self, st):
            if st >= self.delay or self.steps == 1:
                return 65535
            frame = min(self.steps - 2, max(0, int(st * (self.steps - 1) / self.delay + 1e-9)))
            level = (self.steps - frame) * 255 // self.steps
            return self.masks[level >> 4]

        def render(self, width, height, st, at):
            if st >= self.delay or self.steps == 1 or renpy.game.less_updates:
                return renpy.display.transition.null_render(self, width, height, st, at)
            old = renpy.render(self.old_widget, width, height, st, at)
            new = renpy.render(self.new_widget, width, height, st, at)
            result = renpy.Render(max(old.width, new.width), max(old.height, new.height))
            result.blit(old, (0, 0), focus=False, main=False)
            result.blit(new, (0, 0), focus=True, main=True)
            result.mesh = True
            result.add_shader("rscript.ordered_dissolve")
            result.add_uniform("u_rscript_mask", float(self.mask_at(st)))
            result.add_property("mipmap", False)
            result.add_property("nearest", True)
            renpy.redraw(self, self.delay / (self.steps - 1))
            # Rasterize the dots before window scaling, like the native DIB.
            flat = renpy.Render(result.width, result.height)
            flat.blit(result, (0, 0))
            flat.operation = renpy.display.render.FLATTEN
            flat.mesh = True
            flat.add_shader("renpy.texture")
            flat.add_property("drawable_resolution", False)
            flat.add_property("mipmap", False)
            return flat

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
        if effect == 2:
            # All five audited EXEs: Step=0 selects 10, then Step-1 millisecond waits.
            return max(0, (step or 10) - 1) * wait / 1000.0
        if store.rscript_update_timing == "codex-ms":
            if 100 <= effect < 300:
                return .310 if effect < 200 else .410
            # Native 43b390 / Kagerou 41e5b0: zero selects 10; waits are milliseconds.
            # shortcut: nominal waits omit Windows Sleep(5) jitter; calibrate with native playback.
            step = step or 10
            if 5 <= effect < 100:
                frames = 2 * step - 1
            else:
                frames = step + 1
            return frames * wait / 1000.0
        if store.rscript_update_timing == "legacy":
            return step * wait / 100.0 * (2 if 5 <= effect < 100 else 1)
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
        mode, trans.u_blendlevel = store.layer_blend.get(layer, (0, 0))
        # Named renderer modes are lowered by adapters, never raw opcode numbers.
        if mode in (4, 5, "dim256"):
            trans.shader = "rscript.light256" if mode == 5 else "rscript.dim256"
            if mode != "dim256":
                trans.u_blendlevel = ((int(trans.u_blendlevel) & 0xffff) * 255 // 100) & 0xffff
            trans.u_blendmode = 0
        else:
            trans.shader = "rscript.blend"
            trans.u_blendmode = mode
        return .05

    class RScriptGrade(renpy.Displayable):
        def __init__(self, child):
            super(RScriptGrade, self).__init__()
            self.child = child

        def visit(self):
            return [self.child]

        def get_placement(self):
            return self.child.get_placement()

        def render(self, width, height, st, at):
            source = renpy.render(self.child, width, height, st, at)
            w, h = source.get_size()
            result = renpy.Render(w, h)
            for add, blend in ((0., "rscript_grade_scale"), (1., "rscript_grade_add")):
                part = renpy.Render(w, h)
                part.blit(source, (0, 0))
                part.mesh = True
                part.add_shader("renpy.texture")
                part.add_shader("rscript.grade")
                part.add_uniform("u_rscript_grade_add", add)
                part.add_property("gl_blend_func", config.gl_blend_func[blend])
                result.blit(part, (0, 0))
            # shortcut: two GPU passes round separately, within two byte levels;
            # use destination-texture integer composition for byte-exact edges.
            return result

    def rscript_show_layer(name, at_list=None, **kwargs):
        transforms = list(at_list or [])
        if name.startswith("layer") and name[5:].isdigit():
            number = int(name[5:])
            # Moves/effects must retain native depth, not renpy.show's default 0.
            kwargs.setdefault("zorder", store.layer_zorder.get(number, number * 2))
            visibility = (RScriptRasterVisibility if isinstance(kwargs.get("what"), renpy.display.image.ImageReference)
                          else RScriptObjectVisibility)
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
        color = store.layer_color.get(layer, 0) if clear else rscript_colormode(color, layer)

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




        def _queue_load(what=None):
            if not clear:
                img = displayable if displayable is not None else "%s %04d" % (folder[layer], cg)
                store.layer_info[layer] = img
                store.layer_color[layer] = color
                store.layer_pos[layer] = (xpos or 0, ypos or 0)
                queue_draw(rscript_show_layer, tag, what = what if what is not None else renpy.displayable(img),
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

        elif effect in (11, 12, 13, 14):
            img = store.layer_info.get(layer) if clear else (displayable if displayable is not None else "%s %04d" % (folder[layer], cg))
            if img is not None:
                motion = RScriptDiagonal(img, effect, (xpos, ypos), anchor, clear)
                at_list = [Transform(pos=(absolute(0), absolute(0)), anchor=(0, 0),
                                     shader="rscript.colormode", u_colormode=color)]
                if clear:
                    queue_draw(rscript_show_layer, tag, what=motion, at_list=at_list,
                               zorder=zorder, layer=IMAGE_LAYER)
                else:
                    _queue_load(motion)
                queue_draw(rscript_queue_diagonal_pause, motion)
                queue_draw_delayed(_execute_ef_pause)
                if clear:
                    queue_draw_extra_delayed(renpy.hide, tag, layer=IMAGE_LAYER)
                else:
                    queue_draw_extra_delayed(rscript_finish_diagonal, tag, motion, trans, zorder)

        elif effect in (15, 17, 18):
            # White fade / native 16-pixel grid wipe; both use level step 16.
            fade_in = rscript_white_in if effect == 15 else rscript_grid_in(effect == 18)
            fade_out = rscript_white_out if effect == 15 else rscript_grid_out(effect == 18)
            duration = 1.0 if effect == 15 else 16 * rscript_dynamic_tick
            if not clear:
                at_list.append(fade_in)
                _queue_load()
                queue_ef_pause(duration)
            elif layer in store.layer_info:
                img = store.layer_info.pop(layer)
                store.layer_pos.pop(layer, None)
                queue_draw(rscript_show_layer, tag, what = renpy.displayable(img),
                           at_list = [trans, fade_out],
                           zorder = zorder, layer = IMAGE_LAYER)
                queue_ef_pause(duration)
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
                queue_draw(rscript_show_layer, tag, what = renpy.displayable(store.layer_info[layer]), at_list = [Transform(shader="rscript.colormode", u_colormode=color), ef], layer = IMAGE_LAYER)
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
                queue_draw(rscript_show_layer, tag, what = renpy.displayable(store.layer_info[layer]), at_list = [Transform(shader="rscript.colormode", u_colormode=color), ef], layer = IMAGE_LAYER)
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
            store.layer_color.pop(layer, None)
            store.layer_pos.pop(layer, None)
        process_draw_queue()


    def rotate_layer(layer):
        if layer not in store.layer_info:
            return

        img = store.layer_info[layer]
        xpos, ypos = store.layer_pos.get(layer, (0, 0))
        anchor = store.layer_anchor.get(layer, (0.0, 0.0))
        tag = "layer%d" % layer
        stable = Transform(xpos = xpos, ypos = ypos, anchor = anchor,
                           shader="rscript.colormode", u_colormode=store.layer_color.get(layer, 0))

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

        encoded_effect = int(effect) & 0xffff
        if encoded_effect % 100 == 4:
            with_afterimage = encoded_effect >= 100
            effect = 4
        elif effect > 100:
            effect -= 100
            with_afterimage = True
        if with_afterimage:
            start = _effect_start(img, xpos, ypos, anchor)



        if not relative:
            xpos = x * store.layer_x_grid
            ypos = y * store.layer_y_grid

        else:
            xpos += x * store.layer_x_grid
            ypos += y * store.layer_y_grid



        xpos, ypos = absolute(xpos), absolute(ypos)
        if effect == 4:
            # Native CMath works in resource pixels, before the port's grid scaling.
            grid = (store.layer_x_grid, store.layer_y_grid)
            native_start = tuple(int(p / scale) for p, scale in zip(origin, grid))
            native_end = tuple(int(p / scale) for p, scale in zip((xpos, ypos), grid))
            path = rscript_wave_path(native_start, native_end, speed)
            dur = (path[2] + 1) * rscript_dynamic_tick if path[2] else 0
            if not path[2]:
                xpos, ypos = origin
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

        if effect not in effects and effect not in (4, 5, 6):
            raise Exception("Move effect %d not defined." % effect)

        # Replacing _oload's fade must not inherit its initial alpha=0.
        trans = Transform(xpos = xpos, ypos = ypos, anchor = anchor, alpha = 1.0,
                          shader="rscript.colormode", u_colormode=store.layer_color.get(layer, 0))
        if effect == 4:
            ef = Transform(alpha=1.0, function=renpy.curry(rscript_wave_move)(path, anchor, grid))
        elif effect in (5, 6):
            # Native 413e40 -> 44d3c0: opposite half-circle paths, not shakes.
            ef = Transform(alpha=1.0, function=renpy.curry(rscript_arc_move)(
                origin, (xpos, ypos), anchor, dur, 1 if effect == 5 else -1))
        else:
            ef = effects[effect](xpos, ypos, anchor, dur)



        if with_afterimage:
            # shortcut: retain shared ATL trails; native clone timing needs separate calibration.
            ef = afterimage(start, ef)


        ef.shader = "rscript.colormode"
        ef.u_colormode = store.layer_color.get(layer, 0)
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
