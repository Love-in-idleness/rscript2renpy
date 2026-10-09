image cg black = "#000000"
image black = "#000000"
image cg white = "#FFFFFF"
image white = "#FFFFFF"
image nothing = "#0000"

init 100 python:
    _rscript_system_styles = config.init_system_styles

    def rscript_system_styles():
        # Ren'Py resets error styles after init; retain its system font setup.
        _rscript_system_styles()
        style._image_error.color = "#00000000"
        style._image_error.outlines = []

    config.init_system_styles = rscript_system_styles
    config.missing_show = lambda name, what, layer: Null()

    def rscript_missing_image(filename):
        # Missing files are blank; existing images retain normal error handling.
        if not renpy.loader.loadable(filename, directory="images"):
            return im.Image("engine/gui/rscript_empty.svg")
        return None

    config.missing_image_callback = rscript_missing_image

init -130 python:
    def rscript_image_path(path):
        base, ext = os.path.splitext(path)
        if ext.lower() not in (".webp", ".png", ".jpg", ".bmp"):
            return path
        # Language overrides take precedence over the base game's format.
        for prefix in renpy.loader.get_prefixes():
            for suffix in (".webp", ".png", ".jpg", ".bmp"):
                candidate = prefix + base + suffix
                if renpy.loadable(candidate, tl=False):
                    return candidate
        return path

init python:
    class RScriptRasterVisibility:
        def __init__(self, layer):
            self.layer = layer

        def __call__(self, trans, st, at):
            return rscript_layer_visibility(self.layer, trans, st, at)

    def rscript_native_images(child):
        entries = getattr(child, "scene_list", None)
        if not entries:
            return child
        result = renpy.display.layout.MultiBox(layout="fixed")
        batch = []

        def flush():
            if len(batch) > 1:
                group = renpy.display.layout.MultiBox(layout="fixed")
                group.append_scene_list(batch)
                # Stitch only raster pieces, never text, screens or blend effects.
                result.add(Flatten(Transform(group, nearest=True),
                                   drawable_resolution=False))
            elif batch:
                entry = batch[0]
                result.add(entry.displayable, entry.show_time, entry.animation_time)
            batch.clear()

        for entry in entries:
            if isinstance(getattr(entry.displayable, "function", None), RScriptRasterVisibility):
                batch.append(entry)
            else:
                flush()
                result.add(entry.displayable, entry.show_time, entry.animation_time)
        flush()
        return result

    config.layer_transforms.setdefault(IMAGE_LAYER, []).insert(0, rscript_native_images)

init python hide:

    img_extensions = [".webp", ".png", ".jpg", ".bmp"]
    registered_tags = set()

    for _, fn in renpy.loader.listdirfiles(common = False):

        base, ext = os.path.splitext(fn.lower())
        if not ext in img_extensions:
            continue

        split = renpy.re.split(r"[\/\\]", base)
        if split[0] == "tl" and len(split) > 3:
            # Added DLC artwork needs a logical tag even without a base asset.
            # The logical filename keeps Ren'Py's current-language lookup.
            split = split[2:]
            fn = "/".join(fn.replace("\\", "/").split("/")[2:])
        base_dir = split[0]

        if base_dir in ("engine", "gui", "fonts", "tl"):
            continue



        image_tag = " ".join(split)
        if image_tag not in registered_tags:
            # Tags are case-insensitive; actual filesystem paths are not.
            renpy.image(image_tag, DynamicImage("[rscript_image_path(%r)]" % (os.path.splitext(fn)[0] + ".png")))
            registered_tags.add(image_tag)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
