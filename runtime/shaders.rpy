init python:

    renpy.register_shader("rscript.colormode",
    variables = """
    uniform float u_colormode;
    """,
    fragment_functions = """
    vec3 rgb2hsv(vec3 c)
    {
        vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
        vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
        vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

        float d = q.x - min(q.w, q.y);
        float e = 1.0e-10;
        return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
    }

    vec3 hsv2rgb(vec3 c)
    {
        vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
        vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
        return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
    }

    vec3 rscript_sepia(vec3 c)
    {
      float h = 0.07;
      float s = 0.87;
      float v = rgb2hsv(c).b;
      if (v > 0.5) {
        s = s * pow((1.0 - v) * 2.0, 0.87);
      }
      return hsv2rgb(vec3(h, s, v));
    }

    vec3 rscript_grayscale(vec3 c)
    {
      float gray = dot(c.rgb, vec3(0.299, 0.587, 0.114));
      return vec3(gray);
    }
    """,
    fragment_1000 = """
    if (u_colormode == 1.0) {
      //gl_FragColor.rgb /= gl_FragColor.a;
      //gl_FragColor.rgb = 0;
      //gl_FragColor.rgb *= gl_FragColor.a;
      gl_FragColor.rgb = vec3(0.0);
    }

    if (u_colormode == 2.0) {
      gl_FragColor.rgb /= gl_FragColor.a;
      gl_FragColor.rgb = vec3(1.0) - gl_FragColor.rgb;
      gl_FragColor.rgb *= gl_FragColor.a;
    }

    if (u_colormode == 3.0) {
      gl_FragColor.rgb /= gl_FragColor.a;
      gl_FragColor.rgb = rscript_grayscale(gl_FragColor.rgb);
      gl_FragColor.rgb *= gl_FragColor.a;
    }

    if (u_colormode == 4.0) {
      gl_FragColor.rgb /= gl_FragColor.a;
      gl_FragColor.rgb = rscript_sepia(gl_FragColor.rgb);
      gl_FragColor.rgb *= gl_FragColor.a;
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

    // 3 -> Channel mask
    // I'd have to see it to know what to do.
    """
  )

    renpy.register_shader("rscript.effect",
    variables = """
    uniform float u_effectmode;
    """,
    fragment_functions = """
// Based on the GIMP Color to Alpha plugin
// https://gitlab.gnome.org/GNOME/gimp/blob/bcd98991017f85aff90aee36451970d59edcb95d/plug-ins/common/colortoalpha.c#L206
vec4 color_to_alpha(vec4 src, vec3 col) {
  float alpha1, alpha2, alpha3, alpha4;

  alpha4 = src.a;

  // Ren'Py uses premultiplied alpha, so we need to
  // temporarily un-premultiply it here to do our calculations.
  src.r /= src.a;
  src.g /= src.a;
  src.b /= src.a;

  if (src.r > col.r) {
    alpha1 = (src.r - col.r) / (1.0 - col.r);
  } else if (src.r < col.r) {
    alpha1 = (col.r - src.r) / col.r;
  } else {
    alpha1 = 0.0;
  }

  if (src.g > col.g) {
    alpha2 = (src.g - col.g) / (1.0 - col.g);
  } else if (src.g < col.g) {
    alpha2 = (col.g - src.g) / col.g;
  } else {
    alpha2 = 0.0;
  }

  if (src.b > col.b) {
    alpha3 = (src.b - col.b) / (1.0 - col.b);
  } else if (src.b < col.b) {
    alpha3 = (col.b - src.b) / col.b;
  } else {
    alpha3 = 0.0;
  }

  float a = max(alpha1, max(alpha2, alpha3));

  if (a < 1.0 / 255.0) {
    return vec4(src.r * a, src.g * a, src.b * a, a);
  }

  float r = (src.r - col.r) / a + col.r;
  float g = (src.g - col.g) / a + col.g;
  float b = (src.b - col.b) / a + col.b;
  a *= alpha4;

  return vec4(r * a, g * a, b * a, a);
}
    """,
    fragment_1200 = """
gl_FragColor = color_to_alpha(gl_FragColor, vec3(0.5));
    """
  )
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
