"""Background themes for the Kaz board (colours are BGR).

Seven looks so back-to-back videos don't look the same. Pick one per video with the
KAZ_THEME environment variable (default teal_slate), e.g.
    KAZ_THEME=cork python3 board_engine.py stills 2,9,22
Themes: teal_slate, cork, chalkboard, blueprint, manila, olive_canvas, concrete.
Helpers:
    base_layer(h, w, name)            float32 BGR board surface with the theme texture
    tint_gray_map(m, name)            colour a 0..1 grayscale map image in the theme's land colours
    draw_geo_map(bg, proj, x0, y0, w, h, geojson, name, highlight=None)
                                      draw country shapes from a Natural Earth GeoJSON
                                      (raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson)
    label_color(name)                 RGB colour for map labels drawn on the background
    sheet(engine_cmd, times, out)     not provided here: render engine stills once per theme to compare
"""
import numpy as np, cv2, json, os

THEMES = {
  "teal_slate":  dict(label="Teal slate (current)", base=(42, 40, 22), tex="grid", amp=14,
                      land=(84, 88, 62), hi=(138, 150, 118), border=(30, 30, 18), labels=(170, 176, 150)),
  "cork":        dict(label="Cork board", base=(52, 86, 128), tex="cork", amp=22,
                      land=(78, 118, 160), hi=(120, 165, 205), border=(30, 50, 75), labels=(150, 190, 225)),
  "chalkboard":  dict(label="Chalkboard", base=(36, 40, 36), tex="chalk", amp=10,
                      land=(70, 76, 70), hi=(120, 128, 120), border=(205, 210, 205), labels=(200, 205, 200)),
  "blueprint":   dict(label="Blueprint navy", base=(72, 40, 16), tex="blueprint", amp=8,
                      land=(110, 66, 30), hi=(160, 110, 60), border=(220, 190, 150), labels=(230, 205, 170)),
  "manila":      dict(label="Manila case file", base=(140, 178, 200), tex="fibre", amp=12,
                      land=(110, 148, 172), hi=(80, 118, 145), border=(60, 80, 95), labels=(60, 80, 95)),
  "olive_canvas":dict(label="Olive army canvas", base=(36, 62, 58), tex="weave", amp=12,
                      land=(64, 98, 92), hi=(104, 148, 140), border=(24, 40, 38), labels=(150, 190, 180)),
  "concrete":    dict(label="Concrete grey", base=(70, 72, 74), tex="concrete", amp=16,
                      land=(104, 106, 108), hi=(150, 152, 154), border=(40, 40, 42), labels=(190, 192, 194)),
}

def texture(kind, h, w, amp, rng):
    def nz(cell):
        return cv2.resize(rng.random((h//cell+2, w//cell+2)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)[:h, :w] - .5
    t = nz(40) * amp
    if kind == "grid":
        t[:, ::250] += 6; t[::250, :] += 6
    elif kind == "cork":
        t += nz(6) * amp * 1.4
        n = h * w // 900
        ys, xs = rng.integers(0, h, n), rng.integers(0, w, n)
        dots = np.zeros((h, w), np.float32); dots[ys, xs] = rng.choice([-1, 1], n) * 60
        t += cv2.GaussianBlur(dots, (0, 0), 1.6)
    elif kind == "chalk":
        sm = nz(400) * 40 + nz(120) * 18
        t += np.clip(sm, 0, None)
    elif kind == "blueprint":
        g = np.zeros((h, w), np.float32); g[:, ::50] = 10; g[::50, :] = 10; g[:, ::250] = 26; g[::250, :] = 26
        t += g
    elif kind == "fibre":
        f = cv2.resize(rng.random((h//2, w//60+2)).astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)[:h, :w] - .5
        t += f * amp * 1.2 + nz(8) * amp * .6
    elif kind == "weave":
        yy, xx = np.mgrid[:h, :w].astype(np.float32)
        t += (np.sin(xx * 1.1) * np.sin(yy * 1.1)) * 6 + nz(5) * amp * .8
    elif kind == "concrete":
        t += nz(12) * amp + nz(3) * amp * .6
        n = h * w // 4000; dots = np.zeros((h, w), np.float32)
        dots[rng.integers(0, h, n), rng.integers(0, w, n)] = -90
        t += cv2.GaussianBlur(dots, (0, 0), 1.2)
    return t


def get(name=None):
    return THEMES[name or os.environ.get("KAZ_THEME", "teal_slate")]

def base_layer(h, w, name=None, seed=1):
    th = get(name); rng = np.random.default_rng(seed)
    bg = np.zeros((h, w, 3), np.float32) + np.array(th["base"], np.float32)
    bg += texture(th["tex"], h, w, th["amp"], rng)[..., None]
    return bg

def tint_gray_map(m, name=None):
    th = get(name); dark, light = np.array(th["base"], np.float32), np.array(th["hi"], np.float32)
    return dark + (light - dark) * m[..., None]

def label_color(name=None):
    return tuple(int(c) for c in get(name)["labels"][::-1])

def draw_geo_map(bg, proj, x0, y0, w, h, geojson, name=None, highlight=None, feather=260, strength=.85):
    """proj(lon, lat) -> world (x, y). Region x0,y0,w,h in world pixels."""
    th = get(name); gj = json.load(open(geojson))
    land = np.zeros((h, w), np.float32); hi = np.zeros((h, w), np.float32); border = np.zeros((h, w), np.float32)
    for f in gj["features"]:
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            pts = np.array([[proj(lo, la)[0] - x0, proj(lo, la)[1] - y0] for lo, la in poly[0]], np.int32)
            cv2.fillPoly(land, [pts], 1.0, cv2.LINE_AA)
            if highlight and f["properties"].get("ADM0_A3") == highlight: cv2.fillPoly(hi, [pts], 1.0, cv2.LINE_AA)
            cv2.polylines(border, [pts], True, 1.0, 3, cv2.LINE_AA)
    base, mid, light, bd = [np.array(th[k], np.float32) for k in ("base", "land", "hi", "border")]
    tint = base + (mid - base) * land[..., None]
    tint = tint * (1 - .85 * hi[..., None]) + light * .85 * hi[..., None]
    tint = tint * (1 - .55 * border[..., None]) + bd * .55 * border[..., None]
    fy = np.minimum(np.arange(h), np.arange(h)[::-1]) / feather; fx = np.minimum(np.arange(w), np.arange(w)[::-1]) / feather
    fm = np.clip(np.minimum(fy[:, None], fx[None, :]), 0, 1)[..., None] * strength
    bg[y0:y0+h, x0:x0+w] = bg[y0:y0+h, x0:x0+w] * (1 - fm) + tint * fm
