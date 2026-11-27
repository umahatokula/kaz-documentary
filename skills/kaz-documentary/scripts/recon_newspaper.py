"""Reconstruction kit: NEWSPAPER PRINT.

A story told on newsprint: an invented masthead, headlines that set word by word, columns
of text that fill line by line, halftoned photos (the user's own), red pen marks, and page
wipes between spreads. Import it from an episode's insert script (the toolkit is on
PYTHONPATH) and write the scenes for the story:

    from recon_newspaper import *
    def S_front(t):
        im, d = page()
        masthead(d, "THE EVENING DISPATCH", "LAGOS · MONDAY 20 OCTOBER 1986")
        headline(d, 120, 260, 1680, "EDITOR KILLED BY PARCEL BOMB", t, 48.6, 110)
        columns(d, 120, 520, 1060, 440, 3, t, 50.0)
        photo(im, d, "giwa1.jpg", (1240, 520, 1800, 960), t, 49.0, caption="Dele Giwa")
        ring(d, (1230, 510, 1810, 970), t, 53.2)
        return im

Rules: never recreate a real outlet's masthead or logo (use an invented name or none);
label reconstructed pages "RECONSTRUCTION · ILLUSTRATIVE" with stamp(); keep red for
meaning only. Draw in 1920x1080 design coordinates; KAZ_SCALE sets the real size.
Finish every frame with press(img, fi); use wipe(prev, cur, u) on cuts.
"""
import numpy as np, cv2, math, os, sys
from PIL import Image, ImageDraw, ImageOps, ImageFilter
from hd import SD, SFont, KS, PXW, PXH, MONO, SERIF, SERIFI

W, H, FPS = 1920, 1080, 30
NEWS = (236, 230, 214); INK = (30, 28, 26); GREY = (120, 116, 108); RULE = (60, 56, 52); RED = (190, 36, 30)
ASSETS = os.environ.get("KAZ_ASSETS", ".")


def F(p, s): return SFont(p, int(s))
def cl(x, a=0, b=1): return max(a, min(b, x))
def ease(x): x = cl(x); return x*x*(3-2*x)
def back(x, s=1.6): x = cl(x) - 1; return 1 + x*x*((s+1)*x + s)


def page(tone=NEWS):
    """A fresh newsprint page: returns (PIL image, scaled draw)."""
    im = Image.new("RGB", (PXW, PXH), tone); d = SD(ImageDraw.Draw(im))
    return im, d


def masthead(d, name, dateline, y=50):
    """Invented masthead with rules and a dateline. Never a real outlet's name or design."""
    f = F(SERIF, 92); w = f.getbbox(name)[2]
    d.text(((W-w)/2, y), name, font=f, fill=INK)
    d.line([(80, y+120), (W-80, y+120)], fill=RULE, width=5)
    d.line([(80, y+132), (W-80, y+132)], fill=RULE, width=2)
    f2 = F(MONO, 24); w2 = f2.getbbox(dateline)[2]
    d.text(((W-w2)/2, y+142), dateline, font=f2, fill=GREY)
    d.line([(80, y+178), (W-80, y+178)], fill=RULE, width=2)


def headline(d, x, y, w, text, t, t0, size=100, col=INK, per_word=.22, font=None):
    """Sets a headline word by word (each word drops in with a small overshoot). Wraps to width w."""
    f = F(font or SERIF, size); words = text.split(); lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if f.getbbox(trial)[2] > w and cur: lines.append(cur); cur = wd
        else: cur = trial
    lines.append(cur); k = 0
    for i, ln in enumerate(lines):
        cx = x
        for wd in ln.split():
            u = (t - t0 - k*per_word) / .25; k += 1
            if u > 0:
                dy = (1 - back(u)) * -40
                d.text((cx, y + i*size*1.08 + dy), wd, font=f, fill=col)
            cx += f.getbbox(wd + " ")[2]
    return y + len(lines)*size*1.08


def columns(d, x, y, w, h, n, t, t0, rate=14.0, gap=40, seed=1, lead=30):
    """Greeked body text: n columns of grey bars that fill line by line at `rate` lines/s."""
    r = np.random.default_rng(seed); cw = (w - gap*(n-1)) / n
    rows = int(h // lead); shown = int(max(0, t - t0) * rate)
    for c in range(n):
        cx = x + c*(cw+gap)
        if c: d.line([(cx - gap/2, y), (cx - gap/2, y+h)], fill=GREY, width=1)
        for i in range(rows):
            if c*rows + i >= shown: return
            ln = cw * (r.uniform(.55, .97) if (i+1) % 7 == 0 else r.uniform(.92, 1.0))
            d.rectangle([cx, y + i*lead + 8, cx + ln, y + i*lead + 18], fill=(150, 146, 138))


_HT = {}
def halftone(path, size, cell=7):
    """The user's photo as a newsprint halftone, sized (w, h) in pixels."""
    key = (path, size, cell)
    if key in _HT: return _HT[key]
    src = Image.open(path).convert("L")
    src = ImageOps.fit(src, size, Image.LANCZOS); src = ImageOps.autocontrast(src, 1)
    a = np.asarray(src, np.float32) / 255.0; hgt, wid = a.shape
    out = Image.new("L", (wid, hgt), 236); dr = ImageDraw.Draw(out); c = max(3, int(cell*KS))
    for yy in range(0, hgt, c):
        for xx in range(0, wid, c):
            v = 1 - a[yy:yy+c, xx:xx+c].mean(); r = c * .62 * math.sqrt(v)
            if r > .4:
                cx, cy = xx + c/2, yy + c/2; dr.ellipse([cx-r, cy-r, cx+r, cy+r], fill=28)
    out = out.convert("RGB"); _HT[key] = out
    return out


def photo(im, d, name, box, t, t0, caption=None, cell=7):
    """Pastes a halftoned photo into box (x0, y0, x1, y1) once t > t0 (it prints in from the top)."""
    if t < t0: return
    x0, y0, x1, y1 = box; pw, ph = int((x1-x0)*KS), int((y1-y0)*KS)
    p = os.path.join(ASSETS, name)
    if not os.path.exists(p):
        d.rectangle(box, outline=GREY, width=3); d.line([(x0, y0), (x1, y1)], fill=GREY, width=2); return
    ht = halftone(p, (pw, ph), cell); u = ease((t - t0) / .6)
    vis = ht.crop((0, 0, pw, max(1, int(ph*u))))
    im.paste(vis, (int(x0*KS), int(y0*KS)))
    d.rectangle(box, outline=INK, width=2)
    if caption and u >= 1: d.text((x0, y1 + 10), caption, font=F(SERIFI, 26), fill=INK)


def ring(d, box, t, t0, dur=.5, col=RED, w=6, k=0):
    """Hand-drawn red pen ellipse round box, drawn on over dur seconds."""
    if t < t0: return
    x0, y0, x1, y1 = box; cx, cy, rx, ry = (x0+x1)/2, (y0+y1)/2, (x1-x0)/2 + 18, (y1-y0)/2 + 14
    u = ease((t - t0) / dur); n = int(80*u) + 2; r = np.random.default_rng(k)
    ph = r.uniform(0, 6.3, 2)
    pts = [(cx + rx*(1 + .03*math.sin(2*a + ph[0]))*math.cos(a), cy + ry*(1 + .03*math.sin(3*a + ph[1]))*math.sin(a))
           for a in np.linspace(-2.2, -2.2 + 2*math.pi*1.06*u, n)]
    d.line(pts, fill=col, width=w, joint="curve")


def underline(d, x0, x1, y, t, t0, dur=.35, col=RED, w=7):
    if t < t0: return
    u = ease((t - t0) / dur); d.line([(x0, y), (x0 + (x1-x0)*u, y + 3*math.sin(u*3))], fill=col, width=w)


def note(d, x, y, text, t, t0, size=34, col=RED, rate=22):
    """Red pen margin note that writes on."""
    if t > t0: d.text((x, y), text[:int((t - t0)*rate)], font=F(SERIFI, size), fill=col)


def clipping(im, src, box, rot=-3):
    """Pastes another rendered page (PIL image, full frame) as a rotated cut-out clipping into box."""
    x0, y0, x1, y1 = [int(v*KS) for v in box]
    c = src.resize((x1-x0, y1-y0), Image.LANCZOS).rotate(rot, expand=True, fillcolor=(0, 0, 0))
    mask = Image.new("L", (x1-x0, y1-y0), 255).rotate(rot, expand=True)
    sh = Image.new("RGB", c.size, (60, 54, 46)); im.paste(sh, (x0 + int(14*KS), y0 + int(14*KS)), mask)
    im.paste(c, (x0, y0), mask)


def stamp(d, text="RECONSTRUCTION · ILLUSTRATIVE"):
    d.text((40, H - 46), text, font=F(MONO, 22), fill=GREY)


_rng = np.random.default_rng(11)
_FIB = None
def press(img, fi):
    """Newsprint finish: paper fibre, slight ink spread, faint red misregistration, soft vignette."""
    global _FIB
    if _FIB is None:
        n = _rng.normal(0, 1, (PXH//2, PXW//2)).astype(np.float32)
        n = cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.2), (PXW, PXH))
        yy = (np.arange(PXH)/KS)[:, None]; xx = (np.arange(PXW)/KS)[None, :]
        vig = 1 - .22*np.clip(((xx-W/2)/(W*.6))**2 + ((yy-H/2)/(H*.6))**2, 0, 1)
        _FIB = (1 + .035*n)[..., None] * vig[..., None]
    a = np.asarray(img).astype(np.float32)
    a = cv2.GaussianBlur(a, (0, 0), .55*KS)
    red = (a[..., 0] > a[..., 1]*1.5) & (a[..., 0] > 110)
    if red.any():
        sh = np.roll(red, int(2*KS), axis=1); a[sh & ~red] = a[sh & ~red]*.85 + np.array(RED, np.float32)*.15
    r = np.random.default_rng(fi); a = a*_FIB*(.985 + .015*r.random()) + r.normal(0, 3.5, (PXH, PXW, 1))
    return cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)


def wipe(prev, cur, u):
    """Page-turn wipe between two finished BGR frames: a ragged paper edge sweeps right to left."""
    u = ease(u); edge = W * (1 - u)
    yy = np.arange(PXH)/KS; jag = 14*np.sin(yy/23) + 9*np.sin(yy/7.0)
    xs = (np.arange(PXW)/KS)[None, :]; m = (xs > (edge + jag)[:, None]).astype(np.float32)
    shade = np.clip(1 - np.abs(xs - (edge + jag)[:, None])/40, 0, 1)*.35
    out = prev*(1 - m[..., None]) + cur*m[..., None]
    return np.clip(out*(1 - shade[..., None]), 0, 255).astype(np.uint8)


if __name__ == "__main__":   # demo stills: python3 recon_newspaper.py demo.jpg
    sheet = []
    for t in (1.0, 2.2, 4.0):
        im, d = page(); masthead(d, "THE EVENING DISPATCH", "DEMO · MONDAY 20 OCTOBER 1986")
        yb = headline(d, 120, 260, 1680, "A PARCEL ARRIVES AT THE EDITOR'S HOUSE", t, .2, 96)
        columns(d, 120, yb + 30, 1060, 1000 - yb - 30, 3, t, .8)
        photo(im, d, "missing.jpg", (1240, yb + 30, 1800, 960), t, .5, caption="(photo)")
        ring(d, (1240, yb + 30, 1800, 960), t, 2.0); note(d, 1240, 990, "addressed by name", t, 2.6, 30)
        stamp(d); sheet.append(cv2.resize(press(im, int(t*30)), (640, 360)))
    cv2.imwrite(sys.argv[1] if len(sys.argv) > 1 else "news_demo.jpg", np.hstack(sheet))
