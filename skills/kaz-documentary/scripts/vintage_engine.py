import numpy as np, cv2, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hd import SD, SFont, KS, PXW, PXH, MONO, SERIF   # resolution layer: see hd.py
W, H, FPS = 1920, 1080, 30
T0, T1 = 1896/30, 2149/30          # 63.2 -> 71.63
INK = (52, 38, 26); PAPER = (226, 208, 172); MID = (150, 124, 92); DARK = (88, 66, 46); RED = (178, 40, 32)
rng = np.random.default_rng(7)
def F(p, s): return SFont(p, int(s))
def cl(x, a=0, b=1): return max(a, min(b, x))
def ease(x): x = cl(x); return x*x*(3-2*x)
def J(t, k, a=2.0):  # boiling-line jitter, changes on twos (12 fps)
    q = int(t*12); r = np.random.default_rng(q*97 + k); return r.uniform(-a, a)

def wline(d, pts, t, k, fill=INK, w=5):
    pts = [(x+J(t, k+i), y+J(t, k+i+50)) for i, (x, y) in enumerate(pts)]
    d.line(pts, fill=fill, width=w, joint="curve")

def wpoly(d, pts, t, k, fill, outline=INK, w=4):
    pts = [(x+J(t, k+i, 1.5), y+J(t, k+i+50, 1.5)) for i, (x, y) in enumerate(pts)]
    d.polygon(pts, fill=fill); d.line(pts+[pts[0]], fill=outline, width=w)

# ---------------- scene 1: street map ----------------
QUAY_Y = 640
PATH = [(1650, QUAY_Y), (960, QUAY_Y), (930, 600), (930, 470)]
def map_scene(t):
    im = Image.new("RGB", (PXW, PXH), PAPER); d = SD(ImageDraw.Draw(im))
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(214, 195, 158), width=1)
    # river
    river = [(x, 760 + 18*math.sin(x/140)) for x in range(-20, W+40, 40)]
    d.line(river, fill=MID, width=70); wline(d, [(x, y-36) for x, y in river], t, 1, DARK, 3); wline(d, [(x, y+36) for x, y in river], t, 2, DARK, 3)
    # blocks
    for x0 in range(80, W, 300):
        for y0 in (180, 380):
            if 860 < x0+130 < 1010: continue
            wpoly(d, [(x0, y0), (x0+220, y0), (x0+220, y0+150), (x0, y0+150)], t, x0+y0, (205, 184, 146), DARK, 3)
    # roads
    wline(d, [(0, QUAY_Y), (W, QUAY_Y)], t, 10, INK, 34); d.line([(0, QUAY_Y), (W, QUAY_Y)], fill=PAPER, width=24)
    wline(d, [(930, QUAY_Y), (930, 120)], t, 20, INK, 30); d.line([(930, QUAY_Y-14), (930, 120)], fill=PAPER, width=20)
    # bridge
    wpoly(d, [(895, 700), (965, 700), (965, 830), (895, 830)], t, 30, (210, 190, 150), INK, 4)
    f = F(MONO, 26)
    d.text((1300, QUAY_Y+30), "APPEL QUAY", font=f, fill=INK)
    tx = Image.new("RGBA", (int(420*KS), int(40*KS)), (0, 0, 0, 0)); SD(ImageDraw.Draw(tx)).text((0, 0), "FRANZ JOSEPH ST.", font=f, fill=INK)
    im.paste(tx.rotate(90, expand=True), (int(965*KS), int(120*KS)), tx.rotate(90, expand=True))
    d.text((990, 800), "LATIN BRIDGE", font=f, fill=INK)
    d.text((70, 60), "SARAJEVO  ·  28 JUNE 1914", font=F(SERIF, 54), fill=INK)
    # car progress along path
    u = ease((t-T0-0.3)/1.2)
    segs = [math.dist(PATH[i], PATH[i+1]) for i in range(3)]; L = u*sum(segs); pos = PATH[0]; trail = [PATH[0]]
    for i, s in enumerate(segs):
        if L <= s:
            a, b = PATH[i], PATH[i+1]; pos = (a[0]+(b[0]-a[0])*L/s, a[1]+(b[1]-a[1])*L/s); trail.append(pos); break
        L -= s; trail.append(PATH[i+1]); pos = PATH[i+1]
    # dashed red trail
    for i in range(len(trail)-1):
        a, b = trail[i], trail[i+1]; n = int(math.dist(a, b)//22)
        for k in range(0, n, 2):
            p, q = k/max(n, 1), (k+1)/max(n, 1)
            d.line([(a[0]+(b[0]-a[0])*p, a[1]+(b[1]-a[1])*p), (a[0]+(b[0]-a[0])*q, a[1]+(b[1]-a[1])*q)], fill=RED, width=7)
    d.rounded_rectangle([pos[0]-26, pos[1]-17, pos[0]+26, pos[1]+17], 8, fill=INK)
    # Princip mark + stall
    if t > T0+1.1:
        a = 1
        d.ellipse([1010-14, 585-14, 1010+14, 585+14], fill=INK)
        d.text((1040, 545), "PRINCIP"[:int((t-T0-1.1)*20)], font=f, fill=INK)
    if t > T0+1.4:
        u2 = cl((t-T0-1.4)/.3); pts = []
        for i in range(int(60*u2)+2):
            th = -1.6 + 2*math.pi*1.05*i/60; pts.append((960+120*math.cos(th)+J(t, i, 2), 540+95*math.sin(th)+J(t, i+9, 2)))
        d.line(pts, fill=RED, width=7)
        d.text((560, 470), "WRONG TURN — CAR STALLS"[:int((t-T0-1.45)*30)], font=F(MONO, 30), fill=RED)
    return im

# ---------------- scene 2: street side view ----------------
S2 = T0 + 2.0
def car(d, x, y, t, spin, stopped):
    # body
    wpoly(d, [(x-300, y-40), (x+260, y-40), (x+300, y-110), (x+330, y-110), (x+330, y+20), (x-310, y+20)], t, 300, DARK)
    wpoly(d, [(x+220, y-40), (x+330, y-40), (x+330, y+20), (x+220, y+20)], t, 310, (70, 52, 36))   # hood
    wline(d, [(x+330, y-30), (x+350, y-30)], t, 320, INK, 10)                                         # lamp
    wline(d, [(x-60, y-40), (x-140, y-210)], t, 330, INK, 8)                                         # folded top
    wpoly(d, [(x-320, y-60), (x-240, y-200), (x-200, y-200), (x-260, y-40)], t, 335, (110, 88, 64))
    # passengers: Sophie (big hat), Franz (plumed helmet), driver
    for px, k in ((x-150, 0), (x-60, 1), (x+120, 2)):
        wpoly(d, [(px-30, y-40), (px+30, y-40), (px+26, y-130), (px-26, y-130)], t, 340+k*10, (60, 46, 34) if k != 1 else (205, 196, 176))
        d.ellipse([px-22+J(t, k), y-178, px+22+J(t, k), y-132], fill=(196, 170, 136), outline=INK, width=3)
        if k == 0: d.ellipse([px-55, y-200, px+55, y-168], fill=(60, 46, 34), outline=INK, width=3); d.ellipse([px-25, y-225, px+25, y-180], fill=(60, 46, 34))
        if k == 1:
            d.rectangle([px-22, y-200, px+22, y-172], fill=(60, 46, 34))
            for f in range(7): wline(d, [(px, y-200), (px+30-f*10, y-245+abs(f-3)*6)], t, 360+f, (110, 120, 80), 5)
        if k == 2: d.rectangle([px-24, y-192, px+24, y-172], fill=INK)
    # wheels
    for wx in (x-200, x+200):
        d.ellipse([wx-75, y-35, wx+75, y+115], fill=(40, 30, 22)); d.ellipse([wx-55, y-15, wx+55, y+95], fill=(120, 96, 70))
        for s in range(8):
            a = spin + s*math.pi/4; d.line([(wx, y+40), (wx+52*math.cos(a), y+40+52*math.sin(a))], fill=INK, width=5)
        d.ellipse([wx-12, y+28, wx+12, y+52], fill=INK)

def figure(d, x, y, t, k, col=INK, arm=0.0, scale=1.0):
    s = scale
    wpoly(d, [(x-34*s, y), (x+34*s, y), (x+40*s, y-170*s), (x-40*s, y-170*s)], t, k, col, INK, 3)
    d.ellipse([x-26*s, y-230*s, x+26*s, y-172*s], fill=col)
    d.rectangle([x-30*s, y-238*s, x+30*s, y-222*s], fill=col)
    for lx in (-18, 18): wline(d, [(x+lx*s, y), (x+lx*s, y+120*s)], t, k+5+lx, col, int(18*s))
    # arm: angle 0 = down, 1 = straight forward (to the right)
    a = -math.pi/2 + arm*math.pi/2
    sx, sy = x+30*s, y-150*s
    wline(d, [(sx, sy), (sx+120*s*math.cos(a+math.pi), sy-120*s*math.sin(a+math.pi)) if False else (sx+120*s*math.sin(arm*math.pi/2), sy+120*s*math.cos(arm*math.pi/2))], t, k+9, col, int(16*s))

def street(t):
    im = Image.new("RGB", (PXW, PXH), PAPER); d = SD(ImageDraw.Draw(im))
    lt = t - S2
    # sky gradient + buildings
    for i in range(0, 520, 8): d.rectangle([0, i, W, i+8], fill=tuple(int(c*(0.92+0.08*i/520)) for c in PAPER))
    xs = [-40, 380, 760, 1240, 1640]
    for i, x0 in enumerate(xs):
        top = 150 + (i % 2)*70
        wpoly(d, [(x0, top), (x0+400, top), (x0+400, 760), (x0, 760)], t, 400+i*20, (196, 174, 138) if i % 2 else (182, 158, 122), INK, 4)
        for r in range(3):
            for c in range(3):
                wx, wy = x0+50+c*120, top+50+r*150
                if wy+90 < 640: wpoly(d, [(wx, wy), (wx+70, wy), (wx+70, wy+100), (wx, wy+100)], t, 500+i*30+r*3+c, (98, 76, 54), INK, 3)
    # deli shop front with awning
    wpoly(d, [(380, 560), (780, 560), (760, 620), (400, 620)], t, 600, (140, 112, 80))
    for k in range(8): d.line([(400+k*48, 562), (410+k*48, 618)], fill=PAPER, width=10)
    d.text((440, 640), "DELIKATESSEN", font=F(SERIF, 40), fill=INK)
    # sidewalk + road
    d.rectangle([0, 760, W, 820], fill=(170, 146, 110)); d.line([(0, 820), (W, 820)], fill=INK, width=5)
    d.rectangle([0, 820, W, H], fill=(196, 176, 140))
    for k in range(0, W, 140): d.line([(k + (lt*0) % 140, 960), (k+70, 960)], fill=(170, 150, 116), width=6)
    # crowd silhouettes behind car line
    for i, cx in enumerate(range(80, W, 115)):
        if 560 < cx < 760: continue
        bob = math.sin(t*3+i)*3
        figure(d, cx, 790+bob, t, 700+i*11, col=(118, 94, 68) if i % 2 else (100, 80, 58), arm=0, scale=.8)
    # car: enters from right, slows, stalls, small reverse jolt
    if lt < 1.6: cx = 2400 - 1180*ease(lt/1.6)
    elif lt < 2.0: cx = 1220 + 30*ease((lt-1.6)/.4)
    else: cx = 1250
    spin = -cx/75
    jolt = 0
    shot = S2 + 4.05 - S2  # relative ~ 69.25
    if lt > 1.6 and lt < 2.0: jolt = math.sin(lt*60)*3
    car(d, cx, 870+jolt, t, spin, lt > 2.4)
    # Princip: steps forward from crowd near deli
    px = 600 + 170*ease((lt-2.5)/.7); arm = ease((lt-3.5)/.45)
    figure(d, px, 930, t, 900, col=(24, 18, 12), arm=arm, scale=1.25)
    if 2.6 < lt < 4.0:
        d.text((px-90, 560), "G. PRINCIP"[:int((lt-2.6)*18)], font=F(MONO, 32), fill=RED)
        d.line([(px, 600), (px, 660)], fill=RED, width=4)
    # smoke after shot
    st = t - 69.25
    if st > 0:
        for k in range(6):
            r = 20 + st*60 + k*8; ox = px+200 + k*25 + st*40; oy = 700 - k*10 - st*30
            a = int(cl(1-st/1.6)*160)
            if a > 0: d.ellipse([ox-r, oy-r, ox+r, oy+r], fill=(236, 226, 206))
    return im

def intertitle(t):
    im = Image.new("RGB", (PXW, PXH), (18, 14, 10)); d = SD(ImageDraw.Draw(im))
    d.rectangle([180, 140, W-180, H-140], outline=(200, 180, 140), width=4)
    d.rectangle([200, 160, W-200, H-160], outline=(200, 180, 140), width=1)
    for (x, y) in ((200, 160), (W-200, 160), (200, H-160), (W-200, H-160)): d.ellipse([x-12, y-12, x+12, y+12], fill=RED)
    f = F(SERIF, 96); s1 = "Two shots."; s2 = "The Archduke and Sophie"; s3 = "are fatally wounded."
    for s, y, ff in ((s1, 330, f), (s2, 500, F(SERIF, 72)), (s3, 600, F(SERIF, 72))):
        w = ff.getbbox(s)[2]; d.text(((W-w)/2, y), s, font=ff, fill=(232, 218, 190))
    d.line([(W/2-160, 460), (W/2+160, 460)], fill=RED, width=4)
    return im

# --------------- film treatment ---------------
yy = (np.arange(PXH)/KS)[:, None]; xx = (np.arange(PXW)/KS)[None, :]
VIG = (1 - .62*np.clip(((xx-W/2)/(W*.58))**2 + ((yy-H/2)/(H*.58))**2, 0, 1))[..., None].astype(np.float32)
def film(img, t, fi):
    a = np.asarray(img).astype(np.float32)
    g = a.mean(axis=2, keepdims=True); sep = np.concatenate([g*1.07, g*.95, g*.78], 2)
    redmask = ((a[..., 0] > a[..., 1]*1.6) & (a[..., 0] > 120))[..., None]
    a = np.where(redmask, a, sep*.85 + a*.15)
    r = np.random.default_rng(fi)
    a *= 0.93 + 0.07*r.random()                                    # flicker
    a = a*VIG + r.normal(0, 13, (PXH, PXW, 1))                         # grain
    out = np.clip(a, 0, 255).astype(np.uint8)
    for _ in range(r.integers(0, 3)):                              # scratches
        x = int(r.integers(0, W)*KS); cv2.line(out, (x, 0), (x+int(r.integers(-20, 20)*KS), PXH), (235, 225, 200) if r.random() < .6 else (40, 30, 20), 1)
    for _ in range(r.integers(2, 8)):                              # dust
        cv2.circle(out, (int(r.integers(0, W)*KS), int(r.integers(0, H)*KS)), int(r.integers(1, 4)*KS), (25, 18, 12), -1)
    # gate weave
    M = np.float32([[1, 0, r.normal(0, 1.5)*KS], [0, 1, r.normal(0, 2.0)*KS]])
    out = cv2.warpAffine(out, M, (PXW, PXH), borderMode=cv2.BORDER_REFLECT)
    return out

def frame(fi):
    t = fi / FPS
    tq = math.floor(t*12)/12 if t < 69.2 or t > 69.6 else t     # animate on twos, except the shot
    if t < S2: img = map_scene(tq)
    elif t < 70.0: img = street(tq)
    else: img = intertitle(tq)
    out = film(img, t, fi)
    # shot flash
    st = t - 69.25
    if 0 <= st < .25:
        k = 1 - st/.25; out = np.clip(out.astype(np.float32) + 230*k, 0, 255).astype(np.uint8)
        sh = int(16*k*KS); out = np.roll(out, sh, axis=0)
    # iris in/out (classic silent-film circle)
    def iris(o, r):
        m = ((xx-W/2)**2 + (yy-H/2)**2 <= r*r).astype(np.float32)[..., None]
        m = cv2.GaussianBlur(m, (0, 0), 6*KS)[..., None] if m.ndim == 3 else m
        return (o*m).astype(np.uint8)
    full = math.hypot(W/2, H/2)
    if t < T0 + .6: out = iris(out, full*ease((t-T0)/.6))
    if S2-.25 < t < S2: out = iris(out, full*(1-ease((t-(S2-.25))/.25)))
    if S2 <= t < S2+.3: out = iris(out, full*ease((t-S2)/.3))
    if t > T1 - .45: out = iris(out, full*(1-ease((t-(T1-.45))/.45)))
    return cv2.cvtColor(out, cv2.COLOR_RGB2BGR)

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "stills":
        for s in sys.argv[2].split(","):
            cv2.imwrite(f"v_{s}.jpg", frame(int(float(s)*FPS)))
    else:
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{PXW}x{PXH}", "-r", "30", "-i", "-",
                              "-c:v", "libx264", "-preset", os.environ.get("KAZ_PRESET", "veryfast"), "-crf", os.environ.get("KAZ_CRF", "18"), "-pix_fmt", "yuv420p", os.environ.get("KAZ_VOUT", "vintage.mp4")], stdin=subprocess.PIPE)
        for fi in range(round(T0*FPS), round(T1*FPS)): p.stdin.write(frame(fi).tobytes())
        p.stdin.close(); p.wait()
