"""Reconstruction kit: SILENT FILM (sepia, boiling lines on twos, iris wipes, intertitles).

Import it from an episode insert script (the toolkit is on PYTHONPATH): from recon_silent import *
Helpers: wline/wpoly/wrect (boiling outlines), dashed (red route), figure, car, sky, intertitle(lines, t, t0),
film(img, fi) for the sepia treatment, iris(out, r) and FULL for wipes, F/cl/ease. Draw in 1920x1080 design
coordinates. Worked examples: the Giwa parcel sequence and the Hammarskjöld night flight (vint_gw.py, vint_hm.py)."""
import numpy as np, cv2, math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hd import SD, SFont, KS, PXW, PXH, fp

W, H, FPS = 1920, 1080, 30
MONO = fp("FreeMonoBold.ttf")
SERIF = fp("Caladea-Bold.ttf")
SERIFI = fp("Caladea-BoldItalic.ttf")
INK = (52, 38, 26); PAPER = (226, 208, 172); MID = (150, 124, 92); DARK = (88, 66, 46); RED = (178, 40, 32)
def F(p, s): return SFont(p, int(s))
def cl(x, a=0, b=1): return max(a, min(b, x))
def ease(x): x = cl(x); return x*x*(3-2*x)
def J(t, k, a=2.0):
    q = int(t*12); r = np.random.default_rng(q*97 + k); return r.uniform(-a, a)
def wline(d, pts, t, k, fill=INK, w=5):
    pts = [(x+J(t, k+i), y+J(t, k+i+50)) for i, (x, y) in enumerate(pts)]
    d.line(pts, fill=fill, width=w, joint="curve")
def wpoly(d, pts, t, k, fill, outline=INK, w=4):
    pts = [(x+J(t, k+i, 1.5), y+J(t, k+i+50, 1.5)) for i, (x, y) in enumerate(pts)]
    d.polygon(pts, fill=fill); d.line(pts+[pts[0]], fill=outline, width=w)
def wrect(d, x0, y0, x1, y1, t, k, fill, outline=INK, w=4): wpoly(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], t, k, fill, outline, w)
def ctext(d, y, s, f, fill): w = f.getbbox(s)[2]; d.text(((W-w)/2, y), s, font=f, fill=fill)
def dashed(d, pts, u, fill=RED, w=7, seg=22):
    tot = sum(math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1)); L = u*tot; pos = pts[0]
    for i in range(len(pts)-1):
        a, b = pts[i], pts[i+1]; s = math.dist(a, b)
        f = min(1, L/s) if s else 1; e = (a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f); n = int(math.dist(a, e)//seg)
        for k in range(0, n, 2):
            p, q = k/max(n, 1), (k+1)/max(n, 1)
            d.line([(a[0]+(e[0]-a[0])*p, a[1]+(e[1]-a[1])*p), (a[0]+(e[0]-a[0])*q, a[1]+(e[1]-a[1])*q)], fill=fill, width=w)
        pos = e; L -= s
        if L <= 0: break
    return pos

def figure(d, x, y, t, k, col=INK, arms="down", scale=1.0, beret=False, sit=False, face=1):
    s = scale
    if sit:
        wpoly(d, [(x-34*s, y-60*s), (x+34*s, y-60*s), (x+40*s, y-170*s), (x-40*s, y-170*s)], t, k, col, INK, 3)
    else:
        wpoly(d, [(x-34*s, y), (x+34*s, y), (x+40*s, y-170*s), (x-40*s, y-170*s)], t, k, col, INK, 3)
        for lx in (-18, 18): wline(d, [(x+lx*s, y), (x+lx*s, y+120*s)], t, k+5+lx, col, int(18*s))
    d.ellipse([x-26*s, y-230*s, x+26*s, y-172*s], fill=col)
    if beret: d.ellipse([x-34*s, y-246*s, x+22*s, y-214*s], fill=col)
    else: d.rectangle([x-30*s, y-238*s, x+30*s, y-222*s], fill=col)
    sx, sy = x+30*s*face, y-150*s
    for side in ((1, -1) if arms in ("up", "stop") else (1,)):
        bx = x + 30*s*side
        if arms == "up": wline(d, [(bx, sy), (bx+18*s*side, sy-70*s), (bx+14*s*side, sy-150*s)], t, k+9+side, col, int(16*s))
        elif arms == "stop" and side == 1: wline(d, [(sx, sy), (sx+90*s*face, sy-20*s), (sx+110*s*face, sy-70*s)], t, k+9, col, int(16*s))
        elif arms == "down" or side == -1: wline(d, [(bx, sy), (bx+6*s*side, sy+115*s)], t, k+9+side, col, int(16*s))

def bicycle(d, x, y, t, spin):
    for wx in (x-90, x+90):
        d.ellipse([wx-60, y-60, wx+60, y+60], outline=INK, width=7)
        for s in range(6):
            a = spin + s*math.pi/3; d.line([(wx, y), (wx+56*math.cos(a), y+56*math.sin(a))], fill=INK, width=3)
    wline(d, [(x-90, y), (x-10, y-90), (x+70, y-90), (x+90, y)], t, 800, INK, 7)
    wline(d, [(x-10, y-90), (x, y), (x-90, y)], t, 805, INK, 7)
    wline(d, [(x+70, y-90), (x+80, y-130), (x+60, y-140)], t, 810, INK, 7)

def car(d, x, y, t, k, col=(40, 30, 22)):
    wpoly(d, [(x-170, y-40), (x-110, y-100), (x+90, y-100), (x+150, y-40), (x+180, y-40), (x+180, y+10), (x-180, y+10)], t, k, col)
    wpoly(d, [(x-95, y-90), (x-20, y-90), (x-20, y-45), (x-140, y-45)], t, k+20, (120, 100, 76), INK, 3)
    for wx in (x-110, x+110): d.ellipse([wx-34, y-24, wx+34, y+44], fill=INK); d.ellipse([wx-14, y-4, wx+14, y+24], fill=MID)

def sky(d):
    for i in range(0, 560, 8): d.rectangle([0, i, W, i+8], fill=tuple(int(c*(0.92+0.08*i/560)) for c in PAPER))

def intertitle(lines, t, t0, extra=None):
    im = Image.new("RGB", (PXW, PXH), (18, 14, 10)); d = SD(ImageDraw.Draw(im))
    d.rectangle([180, 140, W-180, H-140], outline=(200, 180, 140), width=4)
    d.rectangle([200, 160, W-200, H-160], outline=(200, 180, 140), width=1)
    for (x, y) in ((200, 160), (W-200, 160), (200, H-160), (W-200, H-160)): d.ellipse([x-12, y-12, x+12, y+12], fill=RED)
    for s, y, ff, tt, col in lines:
        if t >= tt: ctext(d, y, s, ff, col)
    if extra: extra(d)
    return im

# ---------------- film treatment ----------------

yy = (np.arange(PXH)/KS)[:, None]; xx = (np.arange(PXW)/KS)[None, :]
VIG = (1 - .62*np.clip(((xx-W/2)/(W*.58))**2 + ((yy-H/2)/(H*.58))**2, 0, 1))[..., None].astype(np.float32)
def film(img, fi):
    a = np.asarray(img).astype(np.float32)
    g = a.mean(axis=2, keepdims=True); sep = np.concatenate([g*1.07, g*.95, g*.78], 2)
    redmask = ((a[..., 0] > a[..., 1]*1.6) & (a[..., 0] > 120))[..., None]
    a = np.where(redmask, a, sep*.85 + a*.15)
    r = np.random.default_rng(fi)
    a *= 0.93 + 0.07*r.random()
    a = a*VIG + r.normal(0, 13, (PXH, PXW, 1))
    out = np.clip(a, 0, 255).astype(np.uint8)
    for _ in range(r.integers(0, 3)):
        x = int(r.integers(0, W)*KS); cv2.line(out, (x, 0), (x+int(r.integers(-20, 20)*KS), PXH), (235, 225, 200) if r.random() < .6 else (40, 30, 20), 1)
    for _ in range(r.integers(2, 8)):
        cv2.circle(out, (int(r.integers(0, W)*KS), int(r.integers(0, H)*KS)), int(r.integers(1, 4)*KS), (25, 18, 12), -1)
    M = np.float32([[1, 0, r.normal(0, 1.5)*KS], [0, 1, r.normal(0, 2.0)*KS]])
    return cv2.warpAffine(out, M, (PXW, PXH), borderMode=cv2.BORDER_REFLECT)
def iris(o, r):
    m = ((xx-W/2)**2 + (yy-H/2)**2 <= r*r).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 6*KS)[..., None]
    return (o*m).astype(np.uint8)
FULL = math.hypot(W/2, H/2)

