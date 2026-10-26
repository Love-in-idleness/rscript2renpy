init python:

    renpy.register_shader("rscript.colormode",
    variables = """
    uniform float u_colormode;
    """,
    fragment_functions = """
    // CMath::Init / CGrapConvLevel: byte LUTs, including the 127/128 boundary.
    vec3 rscript_grade(vec3 c, vec3 level)
    {
        return floor(mix(c * (level + 1.0) / 128.0,
            c + (256.0 - c) * (2.0 * level - 255.0) / 256.0,
            step(vec3(128.0), level)));
    }

    vec3 rscript_grayscale(vec3 c)
    {
        return vec3(floor((c.r + c.g + c.b) / 3.0));
    }

    vec3 rscript_tint(vec3 c, vec3 tint)
    {
        return rscript_grade(tint, rscript_grayscale(c));
    }

    vec3 rscript_night(vec3 c)
    {
        return rscript_tint(c, vec3(72.0, 61.0, 139.0));
    }

    vec3 rscript_sunset(vec3 c)
    {
        return rscript_tint(c, vec3(255.0, 128.0, 0.0));
    }

    vec3 rscript_night_mix(vec3 c, vec3 level)
    {
        float minimum = min(c.r, min(c.g, c.b));
        return floor(c * (256.0 - minimum) / 256.0)
             + floor(rscript_grade(c, level) * (minimum + 1.0) / 256.0);
    }

    float rscript_hsl_channel(float h, float p, float q)
    {
        if (h > 360.0) h -= 360.0;
        else if (h < 0.0) h += 360.0;
        if (h < 60.0) return p + (q - p) * h / 60.0;
        if (h < 180.0) return q;
        if (h < 240.0) return p + (q - p) * (240.0 - h) / 60.0;
        return p;
    }

    // CGrapConvPower: quantized HSL, not a conventional hue rotation.
    vec3 rscript_power(vec3 c)
    {
        float lo = min(c.r, min(c.g, c.b));
        float hi = max(c.r, max(c.g, c.b));
        float delta = hi - lo;
        float total = hi + lo;
        float lbyte = floor((total + 1.0) / 2.0);
        if (delta == 0.0) return vec3(lbyte);
        float sbyte = floor(delta / min(total, 510.0 - total) * 255.0 + 0.5);
        float h;
        if (c.r == hi) h = (c.g - c.b) / delta;
        else if (c.g == hi) h = (c.b - c.r) / delta + 2.0;
        else h = (c.r - c.g) / delta + 4.0;
        // Native cvttsd2si truncates negative red-sector hues toward zero.
        h = mod(float(int(h * 42.0 + 0.5)) + 256.0, 256.0);
        if (h >= 127.0 && h <= 209.0) {
            float d = h - 168.0;
            h = mod(h + floor((1764.0 - d * d) * 120.0 / 1764.0), 256.0);
        }
        h = h * 360.0 / 255.0;
        float s = sbyte / 255.0;
        float l = lbyte / 255.0;
        float q = lbyte < 128.0 ? l * s + l : l + s - l * s;
        float p = l + l - q;
        return floor(vec3(rscript_hsl_channel(h + 120.0, p, q),
                          rscript_hsl_channel(h, p, q),
                          rscript_hsl_channel(h - 120.0, p, q)) * 255.0 + 0.5);
    }
    """,
    fragment_1000 = """
    if (gl_FragColor.a > 0.0 && u_colormode >= 1.0 && u_colormode <= 15.0 && u_colormode != 14.0) {
        vec3 c = floor(gl_FragColor.rgb / gl_FragColor.a * 255.0 + 0.5);
        if (u_colormode == 1.0) c = vec3(0.0);
        if (u_colormode == 2.0) c = vec3(255.0) - c;
        if (u_colormode == 3.0) c = rscript_grayscale(c);
        if (u_colormode == 4.0) c = rscript_tint(c, vec3(139.0, 69.0, 19.0));
        if (u_colormode == 5.0) c = rscript_night(c);
        if (u_colormode == 6.0) c = rscript_sunset(c);
        if (u_colormode == 7.0) c = rscript_night_mix(c, vec3(24.0, 16.0, 32.0));
        if (u_colormode == 8.0) c = rscript_grade(c, vec3(40.0, 32.0, 64.0));
        if (u_colormode == 9.0) c = rscript_grade(c, vec3(56.0, 48.0, 128.0));
        if (u_colormode == 10.0) c = rscript_grade(c, vec3(128.0, 45.0, 80.0));
        if (u_colormode == 11.0) c = rscript_night_mix(c, vec3(144.0, 64.0, 48.0));
        if (u_colormode == 12.0) c = rscript_grade(c, vec3(128.0, 80.0, 48.0));
        if (u_colormode == 13.0) c = rscript_grade(c, vec3(160.0, 96.0, 64.0));
        if (u_colormode == 15.0) c = rscript_power(c);
        gl_FragColor.rgb = c / 255.0 * gl_FragColor.a;
    }
    """
  )


    renpy.register_shader("rscript.blend",
    variables = """
      uniform float u_blendmode;
      uniform float u_blendlevel;
    """,
    fragment_functions = """

    """,
    fragment_1100 = """
    // 0 -> default, so do nothing.

    // 1 -> Subtractive alpha
    // I don't think it's possible to do right now?
    if (u_blendmode == 1.0) {
      //gl_FragColor = color1 - color0;
      //gl_FragColor.a = 0.0;
      gl_FragColor *= (1.0 - (u_blendlevel / 100.0));
    }

    // 2 -> Additive alpha
    if (u_blendmode == 2.0) {
      gl_FragColor.a = 0.0;
      gl_FragColor *= (1.0 - (u_blendlevel / 100.0));
    }

    // Other modes require dialect-specific lowering.
    """
  )

    renpy.register_shader("rscript.dim256",
    variables = """
    uniform float u_blendlevel;
    """,
    fragment_1100 = """
    // Native LUT[channel] = trunc(channel * (256 - level) / 256).
    // Change straight RGB, not coverage; transparent sprite edges remain intact.
    // shortcut: GPU alpha rounding differs by up to 2 byte levels; use integer
    // destination composition if byte-exact native edge matching is required.
    if (gl_FragColor.a > 0.0) {
        vec3 rgb = floor(gl_FragColor.rgb / gl_FragColor.a * 255.0 + 0.5);
        rgb = floor(rgb * (256.0 - u_blendlevel) / 256.0);
        gl_FragColor.rgb = rgb / 255.0 * gl_FragColor.a;
    }
    """
    )

    renpy.register_shader("rscript.light256",
        variables="uniform float u_blendlevel;",
        fragment_1100="""
if (gl_FragColor.a > 0.0) {
    vec3 rgb = floor(gl_FragColor.rgb / gl_FragColor.a * 255.0 + 0.5);
    rgb = floor(rgb + (256.0 - rgb) * u_blendlevel / 256.0);
    gl_FragColor.rgb = rgb / 255.0 * gl_FragColor.a;
}
""")

    from renpy.uguu import GL_FUNC_ADD, GL_ONE, GL_ZERO, GL_ONE_MINUS_SRC_ALPHA
    # Grade is per-channel: multiply the destination, then add its highlight.
    config.gl_blend_func["rscript_grade_scale"] = (
        GL_FUNC_ADD, GL_ZERO, 0x0300,  # GL_SRC_COLOR
        GL_FUNC_ADD, GL_ZERO, GL_ONE)
    config.gl_blend_func["rscript_grade_add"] = (
        GL_FUNC_ADD, GL_ONE, GL_ONE,
        GL_FUNC_ADD, GL_ZERO, GL_ONE)
    renpy.register_shader("rscript.grade",
        variables="uniform float u_rscript_grade_add;",
        fragment_1200="""
float a = gl_FragColor.a;
vec3 level = floor(gl_FragColor.rgb / max(a, 0.00001) * 255.0 + 0.5);
vec3 high = step(vec3(128.0), level);
if (u_rscript_grade_add == 0.0) {
    vec3 scale = mix((level + 1.0) / 128.0, (511.0 - 2.0 * level) / 256.0, high);
    gl_FragColor = vec4(mix(vec3(1.0), scale, a), 1.0);
} else {
    gl_FragColor = vec4(high * (2.0 * level - 255.0) / 255.0 * a, 1.0);
}
""")


    # Khime renderer 0x67 inverts destination RGB where the mask's red is zero.
    config.gl_blend_func["rscript_invert"] = (
        GL_FUNC_ADD, 0x0307, GL_ONE_MINUS_SRC_ALPHA,  # GL_ONE_MINUS_DST_COLOR
        GL_FUNC_ADD, GL_ZERO, GL_ONE)
    renpy.register_shader("rscript.effect_invert",
        fragment_1200 = """
float a = gl_FragColor.a * (1.0 - step(0.5 / 255.0, gl_FragColor.r));
gl_FragColor = vec4(a);
""")

    renpy.register_shader("rscript.ordered_dissolve",
        variables = """
uniform sampler2D tex0;
uniform sampler2D tex1;
uniform float u_rscript_mask;
attribute vec2 a_tex_coord;
attribute vec4 a_position;
varying vec2 v_tex_coord;
varying vec2 v__pixel;
""",
        vertex_200 = "v_tex_coord = a_tex_coord;",
        vertex_300 = "v__pixel = a_position.xy;",
        fragment_200 = """
vec2 pixel = mod(floor(v__pixel), 4.0);
float bit = pixel.x + 4.0 * pixel.y;
float selected = mod(floor(u_rscript_mask / exp2(bit)), 2.0);
gl_FragColor = mix(texture2D(tex0, v_tex_coord), texture2D(tex1, v_tex_coord), selected);
""")

    renpy.register_shader("rscript.white",
        variables = "uniform float u_rscript_white;",
        fragment_1200 = """
gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(gl_FragColor.a), u_rscript_white);
""")

    # Cannonball.exe 4203a6..420421: row and diagonal must exceed level >> 4.
    renpy.register_shader("rscript.grid_wipe",
        variables = """
uniform float u_rscript_grid;
attribute vec4 a_position;
varying vec2 v__pixel;
""",
        vertex_300 = "v__pixel = a_position.xy;",
        fragment_1200 = """
vec2 pixel = floor(v__pixel);
float threshold = floor(u_rscript_grid / 16.0);
float visible = step(threshold + 1.0, mod(pixel.y, 16.0))
              * step(threshold + 1.0, mod(pixel.x + pixel.y, 16.0));
gl_FragColor *= visible;
""")

    renpy.register_shader("rscript.fragment_mask",
        variables="""
            uniform vec4 u_rscript_fragment;
            uniform float u_rscript_fragment_axis;
            varying vec2 v_tex_coord;
        """,
        fragment_300="""
            vec2 p = floor(v_tex_coord * u_rscript_fragment.xy);
            float extent = u_rscript_fragment.x;
            float breadth = u_rscript_fragment.y;
            if (u_rscript_fragment_axis > 0.5) {
                p = p.yx;
                extent = u_rscript_fragment.y;
                breadth = u_rscript_fragment.x;
            }
            float split = floor(extent * u_rscript_fragment.z / 100.0);
            float slope = (extent - 2.0 * split) * 65535.0 / max(1.0, breadth);
            slope = sign(slope) * floor(abs(slope));
            float cut = split + sign(slope) * floor(abs(slope * p.y) / 65535.0);
            float small = min(split, extent - split);
            float large = max(split, extent - split);
            float keep = u_rscript_fragment.w < 0.5
                ? float(p.x < cut && p.x < large)
                : float(p.x >= cut && p.x >= small);
            gl_FragColor *= keep;
        """)

    renpy.register_shader("rscript.column_wipe",
        variables="""
uniform float u_rscript_grid;
attribute vec4 a_position;
varying vec2 v__pixel;
""",
        vertex_300="v__pixel = a_position.xy;",
        fragment_1200="""
float threshold = floor(u_rscript_grid / 16.0);
gl_FragColor *= step(threshold + 1.0, mod(floor(v__pixel.x), 16.0));
""")
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
