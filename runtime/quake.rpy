
init -100 python:


    class Shaker(object):

        anchors = {
          'top' : 0.0,
          'center' : 0.5,
          'bottom' : 1.0,
          'left' : 0.0,
          'right' : 1.0,
          }

        def __init__(self, start, child, x_dist, y_dist, seed = None):
            if start is None:
                start = child.get_placement()

            self.start = [ self.anchors.get(i, i) for i in start ]
            self.x_dist = x_dist
            self.y_dist = y_dist
            self.child = child
            if seed == None:
                self.rng = renpy.random
            else:
                self.rng = renpy.random.Random(seed = seed)

        def __call__(self, t, sizes):


            def fti(x, r):
                if x is None:
                    x = 0
                if isinstance(x, float):
                    return int(x * r)
                else:
                    return x

            xpos, ypos, xanchor, yanchor = [ fti(a, b) for a, b in zip(self.start, sizes) ]

            xpos = xpos - xanchor
            ypos = ypos - yanchor

            nx = xpos + (1.0-t) * self.x_dist * (self.rng.random()*2-1)
            ny = ypos + (1.0-t) * self.y_dist * (self.rng.random()*2-1)

            return (int(nx), int(ny), 0, 0)

    def _Shake(start, time, child = None, x_dist = 100.0, y_dist = 100.0, seed = None, **properties):

        move = Shaker(start, child, x_dist = x_dist, y_dist = y_dist, seed = seed)

        return renpy.display.layout.Motion(move,
                    time,
                    child,
                    add_sizes=True,
                    **properties)

    Shake = renpy.curry(_Shake)
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
