import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2, math, sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from hd import SD, SFont, KS, PXW, PXH, MONO, SERIF   # resolution layer: see hd.py

A = "/mnt/user-data/attachments/b9ecba84-ee6d-5a3b-a63d-23d7e25b8125/"
IMG = {k: A + v for k, v in dict(post="38dab578-image.jpg", ff="6422fd14-image.jpg", soph="d2faf258-image.jpg",
       map="20963956-image.jpg", princ="c0d492dc-image.jpg", car="c9fed47b-image.jpg", ill1="b55dc356-image.jpg",
       ill2="380122a7-image.jpg", news="a284fceb-image.png", trial="b01c36ef-image.jpg").items()}
W, H, FPS = 1920, 1080, 30
DUR = 92.6
RED = (208, 49, 45)
WW, WH = 5000, 4100
R = 2.0  # card pixels per world unit

def font(p, s): return ImageFont.truetype(p, int(s))
def clamp(x, a=0, b=1): return max(a, min(b, x))
def ss(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease(x): x = clamp(x); return 4*x*x*x if x < .5 else 1 - (-2*x+2)**3/2
def backout(x, s=1.7): x = clamp(x) - 1; return 1 + (s+1)*x**3 + s*x**2

# ---------- background world ----------
rng = np.random.default_rng(1)
def build_bg():
    import themes  # KAZ_THEME env var picks the look; see themes.py
    bg = themes.base_layer(WH, WW)
    m = cv2.cvtColor(cv2.imread(IMG["map"]), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    m = cv2.resize(m, (684*3, 528*3), interpolation=cv2.INTER_CUBIC)
    m = cv2.GaussianBlur(m, (0, 0), 1.2)
    tint = themes.tint_gray_map(m)
    x0, y0 = 1500, 1000
    # feather map edges
    fy = np.minimum(np.arange(m.shape[0]), np.arange(m.shape[0])[::-1]) / 320
    fx = np.minimum(np.arange(m.shape[1]), np.arange(m.shape[1])[::-1]) / 320
    f = np.clip(np.minimum(fy[:, None], fx[None, :]), 0, 1)[..., None] * .8
    reg = bg[y0:y0+m.shape[0], x0:x0+m.shape[1]]
    bg[y0:y0+m.shape[0], x0:x0+m.shape[1]] = reg * (1 - f) + tint * f
    return np.clip(bg, 0, 255).astype(np.uint8)
MAP = lambda x, y: (1500 + x*3, 1000 + y*3)

# ---------- cards ----------
def make_card(path, wworld, border=14, crop=None, gray=False):
    im = Image.open(path).convert("RGB")
    if crop: im = im.crop(crop)
    if gray: im = im.convert("L").convert("RGB")
    pw = int(wworld * R); ph = int(im.height * pw / im.width)
    im = im.resize((pw, ph), Image.LANCZOS)
    b = int(border * R); pad = int(50 * R)
    cw, ch = pw + 2*b, ph + 2*b
    c = Image.new("RGBA", (cw + 2*pad, ch + 2*pad), (0, 0, 0, 0))
    sh = Image.new("L", c.size, 0); ImageDraw.Draw(sh).rectangle([pad, pad + 16*R, pad+cw, pad+ch+16*R], fill=130)
    sh = sh.filter(ImageFilter.GaussianBlur(14*R))
    c.paste((0, 0, 0, 255), (0, 0), sh)
    paper = Image.new("RGBA", (cw, ch), (234, 227, 210, 255))
    paper.paste(im, (b, b))
    c.alpha_composite(paper, (pad, pad))
    a = np.array(c); return cv2.cvtColor(a, cv2.COLOR_RGBA2BGRA)

def make_paper(lines, wworld, hworld):
    pw, ph = int(wworld*R), int(hworld*R); pad = int(50*R)
    c = Image.new("RGBA", (pw+2*pad, ph+2*pad), (0, 0, 0, 0))
    sh = Image.new("L", c.size, 0); ImageDraw.Draw(sh).rectangle([pad, pad+16*R, pad+pw, pad+ph+16*R], fill=130)
    c.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14*R)))
    p = Image.new("RGBA", (pw, ph), (228, 218, 196, 255)); d = ImageDraw.Draw(p)
    for i in range(0, ph, int(26*R)): d.line([(0, i), (pw, i)], fill=(205, 196, 176), width=2)
    y = 40*R
    for txt, sz in lines:
        d.text((36*R, y), txt, font=font(MONO, sz*R), fill=(40, 36, 32)); y += sz*R*1.7
    c.alpha_composite(p, (pad, pad))
    return cv2.cvtColor(np.array(c), cv2.COLOR_RGBA2BGRA)

def make_stamp(text):
    f = font(SERIF, 120*R); tw = f.getbbox(text)[2] + 60*R; th = 170*R
    c = Image.new("RGBA", (int(tw), int(th)), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rectangle([6*R, 6*R, tw-6*R, th-6*R], outline=RED+(235,), width=int(9*R))
    d.text((30*R, 12*R), text, font=f, fill=RED+(235,))
    a = np.array(c); noise = rng.random(a.shape[:2]) > .22; a[..., 3] = a[..., 3] * noise
    return cv2.cvtColor(a, cv2.COLOR_RGBA2BGRA)

# card: key -> (img, center world, rot deg, appear time)
CARDS = []
def add(img, cx, cy, rot, t0): CARDS.append(dict(img=img, c=(cx, cy), rot=rot, t0=t0))

# ---------- timeline ----------
# camera keys: t, cx, cy, zoom, rot
K = [(0, 900, 720, 1.05, -1.5), (4.9, 900, 720, 1.28, -1),
     (5.6, 900, 1650, 1.0, 0), (7.3, 960, 1650, 1.05, 0),
     (8.0, 2000, 520, 1.55, 1.5), (11.6, 2010, 520, 1.72, 1.5),
     (12.4, 2250, 560, 1.25, 0), (13.8, 2250, 560, 1.3, 0),
     (14.6, 900, 820, 1.55, -2), (19.6, 920, 840, 1.8, -2),
     (20.3, 2700, 2200, .55, 0), (28.2, 2750, 2200, .6, 0),
     (29.0, 2550, 1950, .72, 0), (35.9, 2560, 1980, .82, 0),
     (36.8, 2520, 2230, 1.15, 1), (42.0, 2520, 2230, 1.32, 1),
     (42.9, 3500, 2900, 1.45, -1), (48.1, 3500, 2900, 1.62, -1),
     (49.0, 3300, 3540, 1.25, 1), (56.0, 3300, 3540, 1.4, 1),
     (56.9, 2500, 3480, 1.35, -1), (62.7, 2500, 3480, 1.5, -1),
     (63.6, 3250, 3250, .9, 0), (67.4, 3260, 3250, 1.0, 0),
     (68.3, 4350, 3000, 1.15, 1.5), (71.2, 4350, 3020, 1.35, 1.5),
     (72.1, 4400, 1300, 1.25, -1), (74.6, 4400, 1300, 1.4, -1),
     (75.6, 3000, 2300, .43, 0), (77.0, 3000, 2300, .45, 0),
     (77.9, 2530, 1820, .95, 0), (84.8, 2560, 1850, 1.05, 0),
     (85.7, 3200, 2450, .8, 0), (89.4, 3200, 2450, .88, 0),
     (91.2, 2900, 2300, .4, 0), (DUR, 2900, 2300, .38, 0)]
def cam(t):
    for i in range(len(K)-1):
        a, b = K[i], K[i+1]
        if a[0] <= t <= b[0]:
            u = ease((t-a[0])/(b[0]-a[0]))
            # zoom interpolate in log space
            z = math.exp(math.log(a[3]) + (math.log(b[3])-math.log(a[3]))*u)
            return (a[1]+(b[1]-a[1])*u, a[2]+(b[2]-a[2])*u, z, a[4]+(b[4]-a[4])*u)
    return K[-1][1:]

SAR, VIE, BEL = MAP(349, 414), MAP(278, 203), MAP(419, 372)
# tags: world anchor, text, t0, offset(screen px)
TAGS = [((2000, 260), "ARCHDUKE FRANZ FERDINAND", 7.9, (-200, 30)),
        ((2000, 300), "HEIR TO AUSTRIA-HUNGARY", 9.6, (-200, 70)),
        ((2500, 300), "SOPHIE, DUCHESS OF HOHENBERG", 13.0, (20, -40)),
        (SAR, "SARAJEVO", 11.6, (40, 40)),
        (MAP(350, 250), "AUSTRIA-HUNGARY", 29.4, (-120, -120)),
        (MAP(350, 250), "MANY NATIONALITIES", 31.4, (-120, -60)),
        (MAP(325, 395), "SOUTH SLAV NATIONALISTS", 38.0, (60, -150)),
        ((3500, 2640), "GAVRILO PRINCIP", 43.4, (60, -60)),
        ((3500, 2680), "BOSNIAN SERB / AGE 19", 45.5, (60, 0)),
        ((3300, 3330), "FIRST ATTEMPT: BOMB", 50.0, (-60, -60)),
        ((3400, 3200), "ROUTE CONFUSION", 64.8, (40, -40)),
        (BEL, "SERBIA", 80.0, (40, -60)),
        (MAP(430, 400), "SERBIAN MILITARY INTELLIGENCE", 86.3, (60, 70))]
# lines: A, B, t0, dur, kind
LINES = [(VIE, BEL, 80.3, .9, "string"), ((3300, 3360), (3500, 3150), 64.4, .7, "string"),
         ((3500, 2900), MAP(419, 372), 86.0, .7, "string")]
ROUTE = [(2330, 3560), (2420, 3630), (2600, 3610), (2690, 3560)]
ELLS = [((900 + 15, 720 + 235), 150, 46, 15.3, .45),   # dagger date on postcard
        (MAP(330, 405), 190, 120, 37.2, .6),            # Bosnia
        (BEL, 80, 60, 80.2, .4)]

def to_screen(p, C):
    cx, cy, z, r = C; a = math.radians(-r)
    x, y = (p[0]-cx)*z, (p[1]-cy)*z
    return (x*math.cos(a) - y*math.sin(a) + W/2, x*math.sin(a) + y*math.cos(a) + H/2)

def world_M(C):
    cx, cy, z, r = C; a = math.radians(-r); c, s = math.cos(a)*z, math.sin(a)*z
    return (KS*np.array([[c, -s, W/2 - c*cx + s*cy], [s, c, H/2 - s*cx - c*cy]], np.float64)).astype(np.float32)

def blend(frame, bgra, M):
    w = cv2.warpAffine(bgra, M, (PXW, PXH), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    a = w[..., 3:4].astype(np.float32) / 255
    frame[:] = frame * (1 - a) + w[..., :3] * a

def card_M(cd, C, extra_scale=1, dy=0):
    h, w = cd["img"].shape[:2]
    rr = math.radians(cd["rot"]); k = extra_scale / R
    c, s = math.cos(rr)*k, math.sin(rr)*k
    L = np.array([[c, -s, cd["c"][0] - (c*w/2 - s*h/2)], [s, c, cd["c"][1] + dy - (s*w/2 + c*h/2)], [0, 0, 1]])
    Wm = np.vstack([world_M(C), [0, 0, 1]])
    return (Wm @ L)[:2].astype(np.float32)

def wobble_ellipse(c, rx, ry, frac, C, seed=0):
    n = int(90*frac)+2; pts = []
    for i in range(n):
        th = -2.3 + 2*math.pi*1.08*(i/89)*1
        jit = 1 + .04*math.sin(i*.7+seed)
        pts.append(to_screen((c[0]+rx*jit*math.cos(th), c[1]+ry*jit*math.sin(th)), C))
    return np.array(pts, np.int32)

def draw_overlays(img, t, C):
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)); d = SD(ImageDraw.Draw(pil, "RGBA"))
    z = C[2]
    for c, rx, ry, t0, du in ELLS:
        if t < t0: continue
        pts = wobble_ellipse(c, rx, ry, clamp((t-t0)/du), C, seed=t0)
        d.line([tuple(p) for p in pts], fill=RED+(240,), width=max(3, int(5*z)), joint="curve")
    for A_, B_, t0, du, kind in LINES:
        if t < t0: continue
        u = ease((t-t0)/du); a = to_screen(A_, C); b0 = to_screen(B_, C)
        b = (a[0]+(b0[0]-a[0])*u, a[1]+(b0[1]-a[1])*u + math.sin(u*math.pi)*25*z)
        d.line([a, b], fill=RED+(230,), width=max(2, int(4*z)))
        for p in (a, b): d.ellipse([p[0]-7, p[1]-7, p[0]+7, p[1]+7], fill=RED+(255,))
    if t > 60.4:  # route to hospital
        u = clamp((t-60.4)/1.2); pts = [to_screen(p, C) for p in ROUTE]
        segs = len(pts)-1; L = u*segs
        for i in range(segs):
            if L <= i: break
            f = min(1, L-i); a, b = pts[i], pts[i+1]; b = (a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f)
            n = int(math.dist(a, b)//14)
            for k in range(0, n, 2):
                p, q = k/max(n, 1), min(1, (k+1)/max(n, 1))
                d.line([(a[0]+(b[0]-a[0])*p, a[1]+(b[1]-a[1])*p), (a[0]+(b[0]-a[0])*q, a[1]+(b[1]-a[1])*q)], fill=RED+(240,), width=5)
    if t > 72.4:  # underline headline
        u = ease((t-72.4)/.5); a = to_screen((4400-500+640*1000/1055, 1300-305+62*1000/1055 + 18), C)
        b = to_screen((4400-500+1045*1000/1055, 1300-305+62*1000/1055 + 18), C)
        d.line([a, (a[0]+(b[0]-a[0])*u, a[1]+(b[1]-a[1])*u)], fill=RED+(240,), width=max(4, int(6*z)))
    fm = SFont(MONO, 30)
    for anchor, txt, t0, off in TAGS:
        if t < t0: continue
        life = 1 - ss((t-t0-7)/.5)
        if t > 85.3: life = max(life, ss((t-85.3)/.6))
        if life <= 0: continue
        LA = int(235*life)
        n = min(len(txt), int((t-t0)*22)); s = txt[:n]
        if n < len(txt) or int(t*2.5) % 2 == 0 and t-t0 < 3: s += "_"
        p = to_screen(anchor, C); q = (p[0]+off[0], p[1]+off[1])
        if not (-400 < q[0] < W+100 and -100 < q[1] < H+100): continue
        tw = fm.getbbox(txt + "_")[2]
        d.line([p, (q[0], q[1]+22)], fill=RED+(LA,), width=2)
        d.ellipse([p[0]-6, p[1]-6, p[0]+6, p[1]+6], fill=RED+(LA,))
        d.rectangle([q[0]-10, q[1]-4, q[0]+tw+10, q[1]+44], fill=(14, 14, 14, LA))
        d.text((q[0], q[1]+2), s, font=fm, fill=(235, 235, 228, LA))
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

def text_center(d, y, s, f, fill):
    w = f.getbbox(s)[2]; d.text(((W-w)/2, y), s, font=f, fill=fill)

def screen_overlays(img, t):
    out = img.astype(np.float32)
    # year card 5.2 - 7.6
    if 5.2 < t < 7.8:
        a = ss((t-5.25)/.3) * (1-ss((t-7.4)/.4))
        out *= 1 - .45*a
        fl = math.exp(-(t-5.25)*5) * a
        yy = (np.arange(PXH)/KS)[:, None]; xx = (np.arange(PXW)/KS)[None, :]; g = np.exp(-(((xx-W/2)/700)**2 + ((yy-H/2)/400)**2))
        out += (g*fl*120)[..., None] * np.array([40, 120, 230]) / 230
        pil = Image.fromarray(cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)); d = SD(ImageDraw.Draw(pil, "RGBA"))
        roll = int(clamp((t-5.4)/.7)*14); yr = "191" + str(min(4, roll % 10 if roll < 10 else 4)) if roll < 14 else "1914"
        al = int(255*a)
        text_center(d, 340, "28 JUNE", SFont(MONO, 44), (220, 220, 210, al))
        text_center(d, 420, yr, SFont(SERIF, 190), (240, 236, 225, al))
        d.line([(560, 540), (860, 540)], fill=(200, 200, 190, al), width=2); d.line([(1060, 540), (1360, 540)], fill=(200, 200, 190, al), width=2)
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    # thesis 20.1 - 28.6
    if 20.1 < t < 28.7:
        a = ss((t-20.1)/.5) * (1-ss((t-28.1)/.5))
        out *= 1 - .55*a
        pil = Image.fromarray(cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)); d = SD(ImageDraw.Draw(pil, "RGBA"))
        al = int(255*a); f1 = SFont(MONO, 50); s1 = "NOT JUST A MURDER."
        n = min(len(s1), int(max(0, t-20.5)*16)); w1 = f1.getbbox(s1)[2]; x1 = (W-w1)/2
        d.text((x1, 400), s1[:n], font=f1, fill=(220, 220, 212, al))
        if t > 22.6:
            u = ease((t-22.6)/.5); d.line([(x1-10, 432), (x1-10+(w1+20)*u, 432)], fill=RED+(al,), width=6)
        if t > 24.3:
            f2 = SFont(SERIF, 150); s2 = "A SPARK"; n2 = min(len(s2), int((t-24.3)*12)); w2 = f2.getbbox(s2 + ".")[2]
            d.text(((W-w2)/2, 500), s2[:n2], font=f2, fill=(242, 238, 228, al))
            if n2 == len(s2): d.text(((W-w2)/2 + f2.getbbox(s2)[2], 500), ".", font=f2, fill=RED+(al,))
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    if t > 89.6:
        a = ss((t-89.7)/.6); fade = 1 - ss((t-91.9)/.6)
        out *= (1 - .85*a)
        pil = Image.fromarray(cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)); d = SD(ImageDraw.Draw(pil, "RGBA"))
        f = SFont(SERIF, 140); text_center(d, 420, "SARAJEVO, 1914", f, RED+(int(255*a),))
        text_center(d, 600, "THE SPARK", SFont(MONO, 40), (220, 220, 212, int(255*a)))
        o = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
        if 89.7 < t < 90.2:  # glitch slices
            for k in range(6):
                y = int(rng.integers(380, 640)); hh = int(rng.integers(8, 30)); sh = int(rng.integers(-60, 60))
                y, hh, sh = int(y*KS), int(hh*KS), int(sh*KS); o[y:y+hh] = np.roll(o[y:y+hh], sh, axis=1)
        return (o * fade).astype(np.uint8)
    return np.clip(out, 0, 255).astype(np.uint8)

def build():
    add(make_card(IMG["post"], 900), 900, 720, -3, .2)
    add(make_card(IMG["ff"], 420), 2000, 520, 4, 7.6)
    add(make_card(IMG["soph"], 380), 2500, 580, -5, 12.6)
    add(make_card(IMG["princ"], 420), 3500, 2900, 3, 42.5)
    add(make_card(IMG["car"], 700), 3300, 3550, -4, 48.5)
    add(make_paper([("28 JUNE 1914", 30), ("", 20), ("> TOWN HALL", 26), ("  RECEPTION", 26), ("", 20), ("> HOSPITAL", 26), ("  VISIT WOUNDED", 26)], 520, 560), 2500, 3480, -2, 56.4)
    add(make_card(IMG["ill1"], 560), 4600, 2700, -7, 67.8)
    add(make_card(IMG["ill2"], 650), 4320, 3080, 3, 68.0)
    add(make_card(IMG["news"], 1000), 4400, 1300, -2, 71.5)
    add(make_card(IMG["trial"], 700), 3750, 2150, 2, 85.2)
    return make_stamp("FAILED")

def render(frames, out):
    bg = build_bg(); stamp = build()
    yy = (np.arange(PXH)/KS)[:, None]; xx = (np.arange(PXW)/KS)[None, :]; vig = 1 - .45*np.clip(((xx-W/2)/(W*.62))**2 + ((yy-H/2)/(H*.62))**2, 0, 1)
    vig = vig[..., None].astype(np.float32)
    grains = [rng.normal(0, 7, (PXH, PXW, 1)).astype(np.float32) for _ in range(6)]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{PXW}x{PXH}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", os.environ.get("KAZ_PRESET", "veryfast"), "-crf", os.environ.get("KAZ_CRF", "18"), "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fi in frames:
        t = fi / FPS; C = list(cam(t))
        for st in (53.55, 69.25):  # shakes
            if st < t < st+.35:
                k = (1-(t-st)/.35)*14; C[0] += k*math.sin(t*90)/C[2]; C[1] += k*math.cos(t*77)/C[2]
        frame = cv2.warpAffine(bg, world_M(C), (PXW, PXH), flags=cv2.INTER_LINEAR, borderValue=(38, 38, 24)).astype(np.float32)
        for cd in CARDS:
            if t < cd["t0"]: continue
            u = (t - cd["t0"]) / .45
            sc = 1.12 - .12*backout(u); dy = -60*(1-ease(u))
            p = to_screen(cd["c"], C); r = max(cd["img"].shape[:2]) / R * C[2]
            if p[0]+r < 0 or p[0]-r > W or p[1]+r < 0 or p[1]-r > H: continue
            im = cd["img"]
            if u < 1:
                im = im.copy(); im[..., 3] = (im[..., 3] * ss(u*1.6)).astype(np.uint8)
            blend(frame, im, card_M(dict(cd, img=im), C, sc, dy))
        if t > 53.55:
            u = (t-53.55)/.2; sc = 1.6 - .6*backout(u, 2.2)
            sd = dict(img=stamp, c=(3330, 3560), rot=-12)
            blend(frame, stamp, card_M(sd, C, sc))
        frame = np.clip(frame, 0, 255).astype(np.uint8)
        frame = draw_overlays(frame, t, C)
        frame = screen_overlays(frame, t)
        f = frame.astype(np.float32)
        # fired flash + rgb split
        for st in (69.25,):
            if st < t < st+.3:
                k = 1-(t-st)/.3; f = f + 160*k
                f[..., 2] = np.roll(f[..., 2], int(12*k*KS), axis=1); f[..., 0] = np.roll(f[..., 0], -int(12*k*KS), axis=1)
        if 53.55 < t < 53.75:
            f[..., 2] = np.roll(f[..., 2], int(10*KS), axis=1); f[..., 0] = np.roll(f[..., 0], -int(10*KS), axis=1)
        f = f * vig + grains[fi % 6]
        if t < .5: f *= t/.5
        ff.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        render([int(t*FPS) for t in ts], "stills.mp4")
    else:
        render(range(int(sys.argv[2]), int(sys.argv[3])), sys.argv[4])
