image cg black = "#000000"
image black = "#000000"
image cg white = "#FFFFFF"
image white = "#FFFFFF"
image nothing = "#0000"

init python hide:

    img_extensions = [".png", ".jpg", ".bmp", ".webp"]

    for _, fn in renpy.loader.listdirfiles(common = False):

        base, ext = os.path.splitext(fn.lower())
        if not ext in img_extensions:
            continue

        split = renpy.re.split(r"[\/\\]", base)
        base_dir = split[0]

        if not base_dir == "images":
            continue



        image_tag = " ".join(split[1:])
        renpy.image(image_tag, fn)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
