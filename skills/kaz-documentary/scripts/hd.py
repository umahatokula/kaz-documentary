"""Resolution layer for kaz-documentary screen drawing.

All screen-space code is written in 1920x1080 design coordinates. KAZ_SCALE (env) sets the
real pixel size: 1 -> 1920x1080 (identical output), 4/3 -> 2560x1440. Wrap a screen
ImageDraw with SD(...) and use SFont(...) for its fonts; every coordinate, width and font
size is scaled, and getbbox() answers in design units so layout maths stays unchanged.
Never wrap drawing on world-space card images: those have their own resolution (R).
"""
import os
import numpy as np
from PIL import ImageFont

KS = float(os.environ.get("KAZ_SCALE", "1"))

_HERE = os.path.dirname(os.path.abspath(__file__))
TK = _HERE   # the series toolkit folder (shared data such as countries.geojson lives here)
FONT_DIRS = [os.path.join(_HERE, "fonts"), "/usr/share/fonts/truetype/freefont", "/usr/share/fonts/truetype/crosextra"]


def fp(name):
    """Path of a bundled font (scripts/fonts), falling back to the Linux system copy."""
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


MONO, SERIF, SERIFI = fp("FreeMonoBold.ttf"), fp("Caladea-Bold.ttf"), fp("Caladea-BoldItalic.ttf")
PXW, PXH = int(round(1920 * KS)), int(round(1080 * KS))


def sc(v):
    if isinstance(v, (int, float, np.integer, np.floating)):
        return v * KS
    if isinstance(v, np.ndarray):
        return v * KS
    return type(v)(sc(x) for x in v) if isinstance(v, tuple) else [sc(x) for x in v]


def sw(w):
    return max(1, int(round(w * KS)))


class SFont:
    _cache = {}

    def __init__(self, path, size):
        key = (path, int(round(size * KS)))
        if key not in SFont._cache:
            SFont._cache[key] = ImageFont.truetype(path, max(1, key[1]))
        self.f = SFont._cache[key]
        self.size = size

    def getbbox(self, s, *a, **k):
        return tuple(v / KS for v in self.f.getbbox(s, *a, **k))

    def getlength(self, s, *a, **k):
        return self.f.getlength(s, *a, **k) / KS


def _f(font):
    return font.f if isinstance(font, SFont) else font


class SD:
    def __init__(self, d):
        self.d = d

    def text(self, xy, s, fill=None, font=None, **k):
        self.d.text(sc(xy), s, fill=fill, font=_f(font), **k)

    def line(self, xy, fill=None, width=1, joint=None):
        self.d.line(sc(list(xy)) if not isinstance(xy, np.ndarray) else (xy * KS).tolist(), fill=fill, width=sw(width), joint=joint)

    def ellipse(self, xy, fill=None, outline=None, width=1):
        self.d.ellipse(sc(list(xy)), fill=fill, outline=outline, width=sw(width))

    def rectangle(self, xy, fill=None, outline=None, width=1):
        self.d.rectangle(sc(list(xy)), fill=fill, outline=outline, width=sw(width))

    def rounded_rectangle(self, xy, radius=0, fill=None, outline=None, width=1, **k):
        self.d.rounded_rectangle(sc(list(xy)), radius * KS, fill=fill, outline=outline, width=sw(width), **k)

    def polygon(self, xy, fill=None, outline=None, width=1):
        self.d.polygon(sc(list(xy)), fill=fill, outline=outline, width=sw(width))

    def arc(self, xy, start, end, fill=None, width=1):
        self.d.arc(sc(list(xy)), start, end, fill=fill, width=sw(width))

    def point(self, xy, fill=None):
        pts = [xy] if isinstance(xy[0], (int, float, np.integer, np.floating)) else xy
        for x, y in pts:
            if KS <= 1:
                self.d.point((x, y), fill=fill)
            else:
                self.d.rectangle([x * KS, y * KS, x * KS + KS - 1, y * KS + KS - 1], fill=fill)
