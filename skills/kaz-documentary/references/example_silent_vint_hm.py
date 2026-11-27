"""Vintage silent-film reconstruction: the night flight to Ndola (59.1 - 150.66 s). Schematic, non-graphic; the crash is not shown."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recon_silent import *   # toolkit kit (was the episode-local vint_common.py)

T0, T1 = 59.1, 150.66
CREAM = (232, 218, 190); GROUND = 820; NIGHT = (34, 30, 28)

def lerp(a, b, u): return a + (b-a)*u
def type_on(d, xy, s, t, t0, size=34, col=RED):
    if t > t0: d.text(xy, s[:int((t-t0)*24)], font=F(MONO, size), fill=col)
def label(d, x, y, s, size=26, col=INK, box=CREAM):
    f = F(MONO, size); w = f.getbbox(s)[2]
    d.rectangle([x-w/2-10, y-6, x+w/2+10, y+size+8], fill=box, outline=INK, width=2); d.text((x-w/2, y), s, font=f, fill=col)

def plane(d, x, y, t, s=1.0, col=(58, 46, 34), light=None, k=0, face=1):
    """Side view of a four-engined propliner, nose towards `face`."""
    P = lambda dx, dy: (x + face*dx*s, y + dy*s)
    wpoly(d, [P(-300, -10), P(-260, -40), P(230, -40), P(290, -22), P(305, 0), P(290, 18), P(230, 26), P(-260, 20)], t, k, col)
    wpoly(d, [P(-300, -10), P(-330, -110), P(-280, -110), P(-230, -36)], t, k+10, col)            # fin
    wpoly(d, [P(-300, 0), P(-360, 12), P(-350, 22), P(-260, 14)], t, k+14, col)                  # tailplane
    wpoly(d, [P(-40, 6), P(110, 6), P(60, 34), P(-90, 34)], t, k+20, col)                       # wing
    for ex in (-30, 50):
        wpoly(d, [P(ex, 0), P(ex+70, 0), P(ex+80, 14), P(ex, 14)], t, k+30+ex, col)
        d.line([P(ex+84, -30), P(ex+84, 44)], fill=INK, width=max(2, int(3*s)))                     # propeller blur
    for i in range(12):
        cx, cy = P(180 - i*34, -22)
        d.ellipse([cx-6*s, cy-6*s, cx+6*s, cy+6*s], fill=light if light else (196, 182, 150))

def stairs(d, x, y, t):
    wpoly(d, [(x, y), (x+30, y), (x+150, GROUND), (x+110, GROUND)], t, 60, (120, 100, 76))
    for i in range(6): d.line([(x+20+i*20, y+i*28), (x+46+i*20, y+i*28)], fill=INK, width=4)

# ---------------- B1: Léopoldville airfield (66.3 - 76.8) ----------------
def S_field(t):
    im = Image.new("RGB", (PXW, PXH), PAPER); d = SD(ImageDraw.Draw(im)); sky(d)
    wrect(d, 1500, 430, 1860, GROUND, t, 2, (186, 164, 126))                                     # terminal
    wrect(d, 1640, 330, 1720, 430, t, 3, (176, 150, 112))                                        # tower
    wrect(d, 1615, 300, 1745, 340, t, 4, (140, 160, 160))
    label(d, 1680, 470, "LÉOPOLDVILLE", 26)
    wline(d, [(0, GROUND), (W, GROUND)], t, 5, INK, 6)
    for i in range(14): wline(d, [(i*150, GROUND+80), (i*150+80, GROUND+80)], t, 30+i, MID, 4)
    plane(d, 760, 640, t, 1.55, k=100)
    stairs(d, 610, 600, t)
    label(d, 760, 380, "THE ALBERTINA · DC-6B", 26)
    # the party walks to the aircraft and boards
    for j in range(5):
        st = 66.6 + j*1.6
        u = cl((t - st)/4.0)
        if u <= 0: continue
        if u < .75: x = lerp(1480, 760, u/.75); y = GROUND - 120
        else: v = (u-.75)/.25; x = lerp(760, 640, v); y = lerp(GROUND-120, 560, v)
        if u < 1: figure(d, x, y, t, 400+j*7, col=(44, 34, 26), scale=.6)
    type_on(d, (120, 120), "SUNDAY, 17 SEPTEMBER 1961", t, 66.6, 40)
    type_on(d, (120, 175), "A ROUTE KEPT SECRET", t, 70.3, 40)
    d.text((40, H-46), "RECONSTRUCTION · ILLUSTRATIVE", font=F(MONO, 22), fill=MID)
    return im

# ---------------- B2: the flight plan (76.8 - 95.3) ----------------
def S_plan(t):
    im = Image.new("RGB", (PXW, PXH), (196, 176, 140)); d = SD(ImageDraw.Draw(im))
    for y in range(0, H, 40): d.line([(0, y), (W, y)], fill=(188, 168, 132), width=2)
    wrect(d, 476, 116, 1476, 986, t, 1, (120, 100, 76), (120, 100, 76), 1)
    wrect(d, 460, 100, 1460, 970, t, 2, CREAM, INK, 5)
    ctext(d, 140, "FLIGHT PLAN", F(SERIF, 64), INK)
    d.line([(520, 230), (1400, 230)], fill=INK, width=3)
    rows = [("AIRCRAFT", "SE-BDY  (DC-6B)", 76.9), ("DEPARTURE", "LÉOPOLDVILLE", 77.6), ("DESTINATION", "LULUABOURG", 79.4),
            ("ALTERNATE", "LÉOPOLDVILLE", 81.6)]
    for i, (k, v, tt) in enumerate(rows):
        y = 290 + i*120
        d.text((540, y), k, font=F(MONO, 30), fill=MID); d.line([(840, y+44), (1400, y+44)], fill=MID, width=2)
        if t > tt: d.text((860, y-4), v[:int((t-tt)*20)], font=F(MONO, 40), fill=INK)
    if t > 86.0:                                                                                  # what the plan left out
        u = ease((t-86.0)/.6)
        d.line([(860, 552), (860 + 300*u, 552)], fill=RED, width=6)
        type_on(d, (560, 800), "ACTUAL DESTINATION: NDOLA", t, 86.4, 42)
        type_on(d, (560, 860), "NOT DISCLOSED TO AVIATION AUTHORITIES", t, 88.6, 28)
    d.text((40, H-46), "SCHEMATIC · NOT THE ORIGINAL DOCUMENT", font=F(MONO, 22), fill=INK)
    return im

# ---------------- C: the route (95.3 - 127.9) ----------------
LEO_, LAKE_, TURN_, NDO_ = (330, 470), (1360, 420), (1420, 640), (1330, 900)
ROUTE = [LEO_, (840, 500), LAKE_, TURN_, (1400, 780), NDO_]
def along(u):
    segs = [math.dist(ROUTE[i], ROUTE[i+1]) for i in range(len(ROUTE)-1)]; L = u*sum(segs)
    for i, s in enumerate(segs):
        if L <= s: f = L/s; a, b = ROUTE[i], ROUTE[i+1]; return (lerp(a[0], b[0], f), lerp(a[1], b[1], f)), math.atan2(b[1]-a[1], b[0]-a[0])
        L -= s
    return ROUTE[-1], math.atan2(ROUTE[-1][1]-ROUTE[-2][1], ROUTE[-1][0]-ROUTE[-2][0])

def S_route(t):
    im = Image.new("RGB", (PXW, PXH), PAPER); d = SD(ImageDraw.Draw(im))
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(214, 196, 160), width=1)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(214, 196, 160), width=1)
    wline(d, [(220, 140), (300, 330), (250, 520), (330, 700), (260, 900)], t, 2, MID, 5)                # coastline
    d.ellipse([1320, 300, 1420, 640], outline=INK, width=4)                                           # Lake Tanganyika
    wline(d, [(1180, 160), (1260, 420), (1300, 700), (1180, 860), (900, 960), (700, 1000)], t, 4, MID, 3)  # border (schematic)
    d.text((1450, 360), "LAKE", font=F(MONO, 24), fill=INK); d.text((1450, 390), "TANGANYIKA", font=F(MONO, 24), fill=INK)
    d.text((760, 740), "KATANGA", font=F(SERIF, 56), fill=MID)
    d.text((1010, 980), "NORTHERN RHODESIA", font=F(MONO, 26), fill=INK)
    for p, n in ((LEO_, "LÉOPOLDVILLE"), (NDO_, "NDOLA")):
        d.ellipse([p[0]-12, p[1]-12, p[0]+12, p[1]+12], fill=INK); d.text((p[0]+20, p[1]-40), n, font=F(MONO, 30), fill=INK)
    u = cl((t-95.6)/31.5)
    if u > 0:
        dashed(d, ROUTE, u, RED, 6)
        (px, py), a = along(u)
        dx, dy = math.cos(a), math.sin(a)
        nose = (px+dx*34, py+dy*34); tail = (px-dx*26, py-dy*26)
        d.line([tail, nose], fill=INK, width=12)
        d.line([(px-dy*34, py+dx*34), (px+dy*34, py-dx*34)], fill=INK, width=8)
    if 114.7 < t:                                                                                  # the threat
        jx, jy = 900, 640
        d.polygon([(jx-40, jy), (jx+40, jy-8), (jx+46, jy), (jx+40, jy+8)], fill=(70, 56, 40))
        d.polygon([(jx-8, jy), (jx-30, jy-32), (jx-18, jy-32), (jx+10, jy)], fill=(70, 56, 40))
        d.text((jx+60, jy-30), "?", font=F(SERIF, 60), fill=RED)
    type_on(d, (120, 70), "A CIRCUITOUS ROUTE", t, 102.3, 40)
    type_on(d, (1100, 1010), "SOUTH ALONG THE BORDER", t, 110.3, 26, INK)
    type_on(d, (130, 860), "KATANGAN AIRCRAFT HAD HARASSED UN FLIGHTS", t, 114.9, 30)
    type_on(d, (130, 905), "RISK OF INTERCEPTION", t, 120.6, 30)
    d.text((40, H-46), "SCHEMATIC MAP · ROUTE APPROXIMATE", font=F(MONO, 22), fill=INK)
    return im

# ---------------- D: night approach (127.9 - 141.3) ----------------
def S_night(t):
    im = Image.new("RGB", (PXW, PXH), NIGHT); d = SD(ImageDraw.Draw(im))
    r = np.random.default_rng(7)
    for _ in range(90):
        x, y = r.integers(0, W), r.integers(0, 600); d.ellipse([x-2, y-2, x+2, y+2], fill=(200, 190, 160))
    wpoly(d, [(0, 820), (400, 800), (900, 830), (1400, 805), (W, 825), (W, H), (0, H)], t, 2, (14, 12, 10), (60, 52, 44), 3)
    for i in range(16):                                                                           # airport lights
        x = 1080 + i*42; tw = .6 + .4*math.sin(t*9 + i)
        d.ellipse([x-5, 836-5, x+5, 836+5], fill=tuple(int(c*tw) for c in (250, 230, 170)))
    d.text((1180, 860), "NDOLA", font=F(MONO, 28), fill=(170, 150, 120))
    u = cl((t-127.9)/13.4)
    plane(d, lerp(250, 1250, u), lerp(360, 560, u), t, .8, col=(8, 8, 8), light=(230, 210, 150), k=200)
    def strip(y, s, tt):
        if t > tt:
            n = int((t-tt)*22); w = F(MONO, 34).getbbox(s)[2]
            d.rectangle([W/2-w/2-24, y-12, W/2+w/2+24, y+52], fill=(226, 208, 172))
            d.text((W/2-w/2, y), s[:n], font=F(MONO, 34), fill=INK)
    strip(110, "CREW: AIRPORT LIGHTS IN SIGHT", 128.2)
    strip(190, "OVERHEAD NDOLA · DESCENDING", 134.6)
    d.text((40, H-46), "AS LATER LOGGED BY NDOLA TOWER", font=F(MONO, 22), fill=(170, 150, 120))
    return im

# ---------------- E: the tower (141.3 - 147.8) ----------------
def S_tower(t):
    im = Image.new("RGB", (PXW, PXH), (150, 126, 96)); d = SD(ImageDraw.Draw(im))
    wrect(d, 260, 140, 1660, 600, t, 2, NIGHT, INK, 8)                                            # window
    for x in (727, 1193): wline(d, [(x, 140), (x, 600)], t, 3, INK, 8)
    for i in range(10): x = 340 + i*130; d.ellipse([x-3, 520-3, x+3, 520+3], fill=(230, 210, 150))
    wrect(d, 120, 640, 1800, 720, t, 5, (110, 84, 58))                                            # desk
    figure(d, 900, 720, t, 300, col=(20, 16, 12), sit=True)
    wrect(d, 1020, 600, 1080, 640, t, 6, (40, 32, 24))                                            # radio set
    k = cl((t-141.3)/5.0)
    for i in range(3):                                                                            # radio waves fading out
        a = int(220*(1-k)); r0 = 40 + i*36 + (t*60 % 36)
        d.arc([1050-r0, 560-r0, 1050+r0, 560+r0], 300, 60, fill=(230, 210, 150) if a > 20 else (60, 50, 40), width=4)
    if t > 141.6:
        s_ = "THE LAST RECORDED CONTACT"[:int((t-141.6)*22)]; w_ = F(MONO, 40).getbbox("THE LAST RECORDED CONTACT")[2]
        d.rectangle([W/2-w_/2-24, 790, W/2+w_/2+24, 862], fill=(226, 208, 172)); d.text((W/2-w_/2, 802), s_, font=F(MONO, 40), fill=RED)
    d.text((40, H-46), "RECONSTRUCTION · ILLUSTRATIVE", font=F(MONO, 22), fill=MID)
    return im

def frame_img(t):
    if t < 66.3:
        return intertitle([("Léopoldville", 330, F(SERIF, 96), 0, CREAM),
                           ("Sunday, 17 September 1961", 480, F(SERIFI, 66), 0, CREAM),
                           ("The real destination was kept secret.", 660, F(SERIF, 46), 61.0, (226, 120, 104))], t, 59.1,
                          extra=lambda d: d.line([(W/2-160, 455), (W/2+160, 455)], fill=RED, width=4)), [66.3]
    if t < 76.8: return S_field(t), [76.8]
    if t < 95.3: return S_plan(t), [95.3]
    if t < 127.9: return S_route(t), [127.9]
    if t < 141.3: return S_night(t), [141.3]
    if t < 147.8: return S_tower(t), [147.8]
    return intertitle([("The Albertina", 380, F(SERIF, 92), 0, CREAM),
                       ("did not land.", 500, F(SERIFI, 86), 148.4, CREAM)], t, 147.8,
                      extra=lambda d: d.line([(W/2-160, 650), (W/2+160, 650)], fill=RED, width=4)), []

def frame(fi):
    t = fi / FPS
    tq = math.floor(t*12)/12
    img, cuts = frame_img(tq)
    out = film(img, fi)
    if t < T0 + .6: out = iris(out, FULL*ease((t-T0)/.6))
    for c in cuts:
        if c - .25 < t < c: out = iris(out, FULL*(1-ease((t-(c-.25))/.25)))
        if c <= t < c + .3: out = iris(out, FULL*ease((t-c)/.3))
    if t > T1 - .6: out = iris(out, FULL*(1-ease((t-(T1-.6))/.6)))
    return cv2.cvtColor(out, cv2.COLOR_RGB2BGR)

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        ts = sys.argv[2].split(",")
        th = [cv2.resize(frame(int(float(s)*FPS)), (640, 360)) for s in ts]
        for f, s in zip(th, ts): cv2.putText(f, s, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, .9, (0, 255, 255), 2)
        while len(th) % 3: th.append(np.zeros_like(th[0]))
        cv2.imwrite(sys.argv[3] if len(sys.argv) > 3 else "vhm.jpg", np.vstack([np.hstack(th[i:i+3]) for i in range(0, len(th), 3)]))
    else:
        a, b = round(T0*FPS), round(T1*FPS)
        if os.environ.get('KAZ_VLIMIT'): b = a + int(os.environ['KAZ_VLIMIT'])
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{PXW}x{PXH}", "-r", "30", "-i", "-",
                              "-c:v", "libx264", "-preset", os.environ.get("KAZ_PRESET", "veryfast"), "-crf", os.environ.get("KAZ_CRF", "18"), "-pix_fmt", "yuv420p", os.environ.get("KAZ_VOUT", "vintage_hm.mp4")], stdin=subprocess.PIPE)
        for fi in range(a, b): p.stdin.write(frame(fi).tobytes())
        p.stdin.close(); p.wait()
