"""Reconstruction kit: COURTROOM SKETCH.

Pastel-and-crayon drawings on toned paper, as a courtroom artist would make them: hatched
figures, benches, a witness box, a table of papers, handwritten captions. Scenes draw on
with a ragged sweep instead of cutting. Best for trials, inquiries, commissions, hearings,
interrogations and testimony. Import it from an episode's insert script:

    from recon_sketch import *
    def S_panel(t):
        im, d = sheet()
        bench(im, d, 360, 300, 1560, t, 1)
        for i, x in enumerate((640, 960, 1280)):
            person(im, d, x, 470, t, 10+i, pose="sit", col=CH_DARK, coat=CH_BLUE)
        table(im, d, 520, 640, 1400, t, 30)
        caption(d, "The Oputa Panel · Abuja, 2001", t, 40.2)
        return im

Rules: the people are generic sketched figures, never likenesses of real people; caption
what is shown and label it "SKETCH RECONSTRUCTION · ILLUSTRATIVE" with stamp(); red only
for meaning. Draw in 1920x1080 design coordinates. Finish each frame with sketch_look(img, fi);
use draw_on(prev, cur, u) between scenes.
"""
import numpy as np, cv2, math, os, sys
from PIL import Image, ImageDraw, ImageFilter
from hd import SD, SFont, KS, PXW, PXH, MONO, SERIF, SERIFI

W, H, FPS = 1920, 1080, 30
SKP = (214, 202, 180); CH_DARK = (44, 38, 34); CH_SEPIA = (128, 88, 58); CH_BLUE = (72, 92, 124)
CH_GREEN = (86, 104, 78); CH_FLESH = (196, 152, 122); CH_WHITE = (246, 240, 226); CH_GREY = (140, 132, 120); RED = (190, 40, 32)


def F(p, s): return SFont(p, int(s))
def cl(x, a=0, b=1): return max(a, min(b, x))
def ease(x): x = cl(x); return x*x*(3-2*x)
def J(t, k, a=1.6):          # hand wobble that changes on twos
    q = int(t*12); r = np.random.default_rng(q*131 + k); return r.uniform(-a, a)


def sheet(tone=SKP):
    im = Image.new("RGB", (PXW, PXH), tone); d = SD(ImageDraw.Draw(im)); return im, d


def stroke(d, pts, t, k, col=CH_DARK, w=4, passes=2):
    """A crayon line: two or three slightly offset passes with wobble."""
    for p in range(passes):
        q = [(x + J(t, k + i*3 + p*101), y + J(t, k + i*3 + 50 + p*101)) for i, (x, y) in enumerate(pts)]
        d.line(q, fill=col, width=max(1, w - p), joint="curve")


def hatch(im, poly, t, k, col, gap=11, ang=-38, w=3, density=1.0):
    """Hatched fill clipped to a polygon (design coords): diagonal crayon strokes."""
    m = Image.new("L", (PXW, PXH), 0); SD(ImageDraw.Draw(m)).polygon(poly, fill=255)
    lay = Image.new("RGB", (PXW, PXH), col)
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    strokes = Image.new("L", (PXW, PXH), 0); sd = SD(ImageDraw.Draw(strokes))
    a = math.radians(ang); dx, dy = math.cos(a), math.sin(a); L = (x1 - x0) + (y1 - y0) + 40
    r = np.random.default_rng(k); g = gap/density; c = x0 - (y1 - y0)
    while c < x1 + (y1 - y0):
        j = J(t, k + int(c), 2.5)
        sx, sy = c + j, y1 + 10
        sd.line([(sx, sy), (sx + dx*L, sy + dy*L)], fill=int(170 + 80*r.random()), width=w)
        c += g + r.uniform(-2, 2)
    mask = Image.fromarray((np.asarray(m, np.float32)*np.asarray(strokes, np.float32)/255).astype(np.uint8))
    im.paste(lay, (0, 0), mask)


def blob(im, poly, col, alpha=.55):
    """A soft pastel wash under the hatching."""
    m = Image.new("L", (PXW, PXH), 0); SD(ImageDraw.Draw(m)).polygon(poly, fill=int(255*alpha))
    m = m.filter(ImageFilter.GaussianBlur(2*KS))
    im.paste(Image.new("RGB", (PXW, PXH), col), (0, 0), m)


def person(im, d, x, y, t, k, pose="stand", col=CH_DARK, coat=CH_BLUE, scale=1.0, face=1, arm="down"):
    """A generic sketched figure (no likeness). (x, y) is the hip point; pose 'stand' or 'sit'."""
    s = scale; hy = y - 250*s                                  # head centre
    blob(im, [(x-70*s, y-190*s), (x+70*s, y-190*s), (x+80*s, y), (x-80*s, y)], coat, .6)
    hatch(im, [(x-70*s, y-190*s), (x+70*s, y-190*s), (x+80*s, y), (x-80*s, y)], t, k, col, 12, -40, 3, .9)
    stroke(d, [(x-70*s, y-188*s), (x-82*s, y), (x+80*s, y), (x+70*s, y-188*s), (x+30*s, y-212*s), (x-30*s, y-212*s), (x-70*s, y-188*s)], t, k+1, col, 4)
    blob(im, [(x-38*s, hy-46*s), (x+38*s, hy-46*s), (x+44*s, hy+40*s), (x-44*s, hy+40*s)], CH_FLESH, .45)
    d.ellipse([x-38*s, hy-48*s, x+38*s, hy+46*s], outline=col, width=max(2, int(4*s)))
    stroke(d, [(x-36*s, hy-14*s), (x-20*s, hy-46*s), (x+18*s, hy-50*s), (x+38*s, hy-18*s)], t, k+2, col, 7)   # hair
    trou = tuple(max(0, c - 40) for c in coat)
    if pose == "sit":                                          # side view: thigh forward, shin down
        th = [(x-70*s, y-10*s), (x+(150*face-0)*s, y-14*s), (x+150*face*s, y+44*s), (x-60*s, y+50*s)]
        sh = [(x+(120*face)*s, y+30*s), (x+(160*face)*s, y+30*s), (x+(158*face)*s, y+190*s), (x+(118*face)*s, y+190*s)]
        for poly, kk in ((th, 3), (sh, 4)):
            blob(im, poly, trou, .65); hatch(im, poly, t, k+kk, col, 10, 40, 3, .9); stroke(d, poly + [poly[0]], t, k+kk+10, col, 4)
    else:
        legs = [(x-76*s, y), (x+76*s, y), (x+64*s, y+232*s), (x+12*s, y+232*s), (x, y+70*s), (x-12*s, y+232*s), (x-64*s, y+232*s)]
        blob(im, legs, trou, .65); hatch(im, legs, t, k+3, col, 10, 40, 3, .9); stroke(d, legs + [legs[0]], t, k+4, col, 4)
    if arm == "raised":
        stroke(d, [(x+66*s*face, y-180*s), (x+110*s*face, y-260*s), (x+120*s*face, y-330*s)], t, k+5, col, 6)
    elif arm == "forward":
        stroke(d, [(x+66*s*face, y-176*s), (x+150*s*face, y-120*s), (x+210*s*face, y-118*s)], t, k+5, col, 6)
    else:
        stroke(d, [(x+70*s*face, y-176*s), (x+86*s*face, y-60*s)], t, k+5, col, 6)


def bench(im, d, x0, y, x1, t, k, col=CH_SEPIA):
    """The raised bench: a long panelled desk at height y."""
    blob(im, [(x0, y), (x1, y), (x1, y + 260), (x0, y + 260)], col, 1.0)
    hatch(im, [(x0, y), (x1, y), (x1, y + 260), (x0, y + 260)], t, k, CH_DARK, 16, -30, 2, .7)
    stroke(d, [(x0, y), (x1, y), (x1, y + 260), (x0, y + 260), (x0, y)], t, k+1, CH_DARK, 5)
    for px in np.linspace(x0 + 40, x1 - 40, 6): stroke(d, [(px, y + 40), (px, y + 230)], t, k + int(px), CH_DARK, 3, 1)


def witness_box(im, d, x, y, t, k):
    blob(im, [(x-130, y), (x+130, y), (x+150, y + 220), (x-150, y + 220)], CH_SEPIA, 1.0)
    hatch(im, [(x-130, y), (x+130, y), (x+150, y + 220), (x-150, y + 220)], t, k, CH_DARK, 14, -50, 2, .8)
    stroke(d, [(x-130, y), (x+130, y), (x+150, y + 220), (x-150, y + 220), (x-130, y)], t, k+1, CH_DARK, 5)
    stroke(d, [(x-150, y + 2), (x+150, y + 2)], t, k+2, CH_DARK, 9)


def table(im, d, x0, y, x1, t, k, papers=5):
    blob(im, [(x0, y), (x1, y), (x1 + 40, y + 70), (x0 - 40, y + 70)], CH_SEPIA, 1.0)
    stroke(d, [(x0, y), (x1, y), (x1 + 40, y + 70), (x0 - 40, y + 70), (x0, y)], t, k, CH_DARK, 5)
    r = np.random.default_rng(k)
    for i in range(papers):
        px = x0 + 60 + i*(x1 - x0 - 120)/max(1, papers - 1); py = y + 14 + r.uniform(0, 20); a = r.uniform(-.3, .3)
        c = [(px + math.cos(a)*dx - math.sin(a)*dy, py + math.sin(a)*dx*.3 + math.cos(a)*dy*.3) for dx, dy in ((-40, -30), (40, -30), (40, 30), (-40, 30))]
        d.polygon(c, fill=CH_WHITE); d.line(c + [c[0]], fill=CH_GREY, width=2)


def window(im, d, x0, y0, x1, y1, t, k, sky=(170, 186, 196)):
    blob(im, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], sky, .7)
    stroke(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], t, k, CH_DARK, 5)
    stroke(d, [((x0+x1)/2, y0), ((x0+x1)/2, y1)], t, k+1, CH_DARK, 4); stroke(d, [(x0, (y0+y1)/2), (x1, (y0+y1)/2)], t, k+2, CH_DARK, 4)


def caption(d, text, t, t0, y=968, size=38, col=CH_DARK, rate=26):
    """Handwritten-style caption on a paper strip at the foot of the sketch."""
    if t < t0: return
    f = F(SERIFI, size); s = text[:int((t - t0)*rate)]; w = f.getbbox(text)[2]
    d.rectangle([(W - w)/2 - 30, y - 12, (W + w)/2 + 30, y + size + 18], fill=CH_WHITE)
    d.text(((W - w)/2, y), s, font=f, fill=col)


def label(d, x, y, text, t, t0, size=28, col=RED, rate=22):
    """Red handwritten label with a short pointer line."""
    if t < t0: return
    d.text((x, y), text[:int((t - t0)*rate)], font=F(SERIFI, size), fill=col)


def stamp(d, text="SKETCH RECONSTRUCTION · ILLUSTRATIVE"):
    d.text((40, H - 46), text, font=F(MONO, 22), fill=CH_GREY)


_TOOTH = None
def sketch_look(img, fi):
    """Paper tooth (pastel catches on the grain), a little smudge and a soft vignette. No flicker."""
    global _TOOTH
    if _TOOTH is None:
        r = np.random.default_rng(5); n = r.normal(0, 1, (PXH, PXW)).astype(np.float32)
        n = cv2.GaussianBlur(n, (0, 0), .8*KS); m = cv2.GaussianBlur(r.normal(0, 1, (PXH, PXW)).astype(np.float32), (0, 0), 30*KS)
        yy = (np.arange(PXH)/KS)[:, None]; xx = (np.arange(PXW)/KS)[None, :]
        vig = 1 - .28*np.clip(((xx-W/2)/(W*.62))**2 + ((yy-H/2)/(H*.62))**2, 0, 1)
        _TOOTH = ((1 + .05*n + .04*m/np.abs(m).max()) * vig)[..., None]
    a = np.asarray(img).astype(np.float32)
    a = cv2.GaussianBlur(a, (0, 0), .7*KS)*.7 + a*.3
    r = np.random.default_rng(fi); a = a*_TOOTH*(.99 + .01*r.random())
    return cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)


def draw_on(prev, cur, u):
    """Scene change as an artist's sweep: the new sketch appears behind a ragged diagonal edge."""
    u = ease(u); yy = (np.arange(PXH)/KS)[:, None]; xx = (np.arange(PXW)/KS)[None, :]
    edge = -400 + (W + 800)*u
    jag = 22*np.sin(yy/31) + 12*np.sin(yy/9 + xx/40)
    m = np.clip(((edge + jag) - (xx + .45*yy)) / 60, 0, 1)[..., None]
    return (prev*(1 - m) + cur*m).astype(np.uint8)


if __name__ == "__main__":   # demo still: python3 recon_sketch.py demo.jpg
    t = 1.0; im, d = sheet()
    window(im, d, 160, 90, 520, 380, t, 1)
    for i, x in enumerate((780, 1110, 1440)): person(im, d, x, 400, t, 20 + i*7, pose="stand", coat=(CH_BLUE, CH_GREEN, CH_SEPIA)[i], scale=.62)
    bench(im, d, 520, 330, 1700, t, 3)                         # people behind furniture: draw them first
    person(im, d, 300, 690, t, 70, coat=CH_GREEN, scale=.7, arm="raised"); witness_box(im, d, 300, 640, t, 60)
    person(im, d, 1650, 760, t, 90, pose="sit", face=-1, coat=CH_BLUE, scale=.75, arm="forward")
    table(im, d, 760, 760, 1500, t, 80)
    caption(d, "Hearing room, 2001 · sketch reconstruction", t, 0); label(d, 1460, 700, "petition", t, 0); stamp(d)
    a = sketch_look(im, 1)
    im2, d2 = sheet(); caption(d2, "next scene", t, 0); b = sketch_look(im2, 2)
    cv2.imwrite(sys.argv[1] if len(sys.argv) > 1 else "sketch_demo.jpg", np.hstack([cv2.resize(a, (960, 540)), cv2.resize(draw_on(a, b, .5), (960, 540))]))
