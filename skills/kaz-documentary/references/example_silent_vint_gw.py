"""Vintage silent-film reconstruction: the parcel arrives (48.3 - 162.85 s). Schematic, non-graphic; no explosion shown."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recon_silent import *   # toolkit kit (was the episode-local vint_common.py)

T0, T1 = 48.3, 162.85
CREAM = (232, 218, 190); BROWN = (150, 112, 70); GROUND = 820

def lerp(a, b, u): return a + (b-a)*u
def type_on(d, xy, s, t, t0, size=34, col=RED):
    if t > t0: d.text(xy, s[:int((t-t0)*24)], font=F(MONO, size), fill=col)
def label(d, x, y, s, size=26, col=INK):
    f = F(MONO, size); w = f.getbbox(s)[2]
    d.rectangle([x-w/2-10, y-6, x+w/2+10, y+size+8], fill=CREAM, outline=INK, width=2); d.text((x-w/2, y), s, font=f, fill=col)
def envelope(d, x, y, s=1.0, flap=0.0):
    w, h = 64*s, 44*s
    d.rectangle([x-w/2, y-h/2, x+w/2, y+h/2], fill=BROWN, outline=INK, width=max(2, int(3*s)))
    d.line([(x-w/2, y-h/2), (x, y-h/2 + h*.45*(1-flap*1.6)), (x+w/2, y-h/2)], fill=INK, width=max(2, int(3*s)))
def walk_fig(d, x, y, t, k, moving, col=INK, scale=1.0):
    bob = 6*abs(math.sin(t*7)) if moving else 0
    figure(d, x, y - bob, t, k, col=col, scale=scale)

# ---------------- B: at the gate (54.3 - 83.2) ----------------
def street(d, t):
    d.rectangle([0, 0, W, H], fill=PAPER); sky(d)
    wpoly(d, [(1180, 250), (1560, 120), (1940, 250)], t, 5, (120, 94, 66))          # roof beyond wall
    wrect(d, 1230, 250, 1890, 430, t, 8, (196, 176, 140))
    wrect(d, 960, 430, W+10, GROUND, t, 12, (176, 150, 112))                         # compound wall
    wrect(d, 1080, 520, 1320, GROUND, t, 16, (120, 96, 70))                          # gate
    for gx in range(1100, 1320, 30): wline(d, [(gx, 525), (gx, GROUND-4)], t, 20+gx, INK, 4)
    d.rectangle([1420, 560, 1760, 640], fill=CREAM, outline=INK, width=3)
    label(d, 1590, 580, "25 TALABI ST.", 34)
    wline(d, [(0, GROUND), (W, GROUND)], t, 2, INK, 6)
    for i in range(12): wline(d, [(i*170, GROUND+90), (i*170+90, GROUND+90)], t, 30+i, MID, 4)
    d.text((40, H-46), "RECONSTRUCTION · AS DESCRIBED IN LATER ACCOUNTS", font=F(MONO, 22), fill=MID)

def S_gate(t):
    im = Image.new("RGB", (PXW, PXH), PAPER); d = SD(ImageDraw.Draw(im)); street(d, t)
    # car: arrives 54.3-57.6, leaves after 80.8
    if t < 57.6: cx = lerp(-260, 420, ease((t-54.3)/3.3))
    elif t < 80.8: cx = 420
    else: cx = lerp(420, -320, ease((t-80.8)/2.2))
    gx, gy = 1200, GROUND-120                                    # guard at the gate
    figure(d, gx, gy, t, 300, col=(70, 56, 40))
    label(d, gx, gy-300, "SECURITY MAN", 24)
    m1x = m2x = None
    if 59.0 < t < 80.6:
        if t < 61.2: m1x = 760
        elif t < 63.6: m1x = lerp(760, 1010, ease((t-61.2)/2.4))
        elif t < 76.2: m1x = 1010
        elif t < 79.0: m1x = lerp(1010, 760, ease((t-76.2)/2.8))
        else: m1x = 760
        m2x = 640 if t < 79.6 else None
    if m2x: walk_fig(d, m2x, gy, t, 200, False, (30, 24, 18))
    if m1x:
        mv = 61.2 < t < 63.6 or 76.2 < t < 79.0
        walk_fig(d, m1x, gy, t, 100, mv, (30, 24, 18))
    car(d, cx, GROUND-10, t, 400)
    # the envelope: in man 1's hand, then passed through the gate
    if 59.4 < t < 80.6 and m1x:
        if t < 64.2: envelope(d, m1x + 44, gy - 40, 1.0)
        elif t < 65.6: envelope(d, lerp(m1x + 44, gx - 40, ease((t-64.2)/1.4)), gy - 40 - 30*math.sin(math.pi*cl((t-64.2)/1.4)), 1.0)
    if t >= 65.6: envelope(d, gx - 40, gy - 40, 1.0)
    if 59.6 < t < 80.6: label(d, 700, gy-300, "TWO UNIDENTIFIED MEN", 24)
    type_on(d, (120, 120), "A CAR ARRIVES", t, 54.6, 40)
    type_on(d, (120, 175), "A PADDED BROWN ENVELOPE", t, 64.0, 40)
    type_on(d, (120, 230), "GUARD CONFIRMS: GIWA IS AT HOME", t, 69.5, 34, INK)
    type_on(d, (120, 280), "THEY DID NOT WAIT", t, 76.5, 40)
    return im

# ---------------- C: through the compound (83.2 - 101.0) ----------------
def S_compound(t):
    im = Image.new("RGB", (PXW, PXH), PAPER); d = SD(ImageDraw.Draw(im)); sky(d)
    wpoly(d, [(1050, 300), (1500, 140), (1950, 300)], t, 5, (120, 94, 66))
    wrect(d, 1100, 300, 1900, GROUND, t, 8, (196, 176, 140))
    wrect(d, 1400, 520, 1560, GROUND, t, 12, (96, 74, 52))                          # front door
    for wx in (1180, 1680): wrect(d, wx, 420, wx+140, 560, t, 20+wx, (140, 160, 160))
    wline(d, [(0, GROUND), (W, GROUND)], t, 2, INK, 6)
    wpoly(d, [(0, GROUND), (1400, GROUND), (1560, GROUND), (1700, H), (-10, H)], t, 40, (214, 196, 160), MID, 2)
    d.text((40, H-46), "RECONSTRUCTION · AS DESCRIBED BY KAYODE SOYINKA", font=F(MONO, 22), fill=MID)
    gy = GROUND - 120
    # guard walks 83.2-87.3, waits; hand-over at 94.5
    gx = lerp(120, 860, ease((t-83.4)/3.9))
    figure(d, gx, gy, t, 300, col=(70, 56, 40)); label(d, gx, gy-300, "SECURITY MAN", 24)
    bx = None
    if t > 87.3:
        if t < 90.5: bx = lerp(1480, 1060, ease((t-87.3)/3.2))
        elif t < 98.4: bx = 1060
        else: bx = lerp(1060, 1480, ease((t-98.4)/2.2))
        if not (t > 100.4):
            walk_fig(d, bx, gy, t, 500, t < 90.5 or t > 98.4, (44, 34, 26), .95)
            label(d, bx, gy-350, "BILLY · ELDEST SON", 24)
    if t < 94.5: envelope(d, gx + 44, gy - 40)
    elif t < 95.8: envelope(d, lerp(gx + 44, 1060 - 44, ease((t-94.5)/1.3)), gy - 40 - 24*math.sin(math.pi*cl((t-94.5)/1.3)))
    elif bx is not None and t < 100.4: envelope(d, bx - 44, gy - 40)
    type_on(d, (120, 120), "CARRIED TOWARDS THE HOUSE", t, 83.6, 38)
    type_on(d, (120, 175), "HANDED TO GIWA'S SON, BILLY", t, 94.6, 38)
    type_on(d, (120, 230), "BILLY TAKES IT TO HIS FATHER", t, 98.6, 34, INK)
    return im

# ---------------- D / G: the study ----------------
GX, SX, SY = 380, 1540, 760          # Giwa (left), Soyinka (right), seat line
def study(d, t):
    d.rectangle([0, 0, W, H], fill=(206, 186, 150))
    for y in range(0, 860, 70): d.line([(0, y), (W, y)], fill=(198, 178, 142), width=2)
    wrect(d, 760, 120, 1160, 420, t, 4, (150, 170, 168))                            # window
    wline(d, [(960, 120), (960, 420)], t, 6, INK, 4); wline(d, [(760, 270), (1160, 270)], t, 7, INK, 4)
    wrect(d, 60, 120, 420, 600, t, 10, (120, 92, 64))                               # bookshelf
    for r in range(4):
        y = 140 + r*115
        wline(d, [(70, y+105), (410, y+105)], t, 12+r, INK, 4)
        for b in range(9): d.rectangle([80+b*36, y+30+(b*7 % 20), 108+b*36, y+104], fill=((90, 60, 40), (60, 50, 40), (130, 100, 60))[b % 3])
    wline(d, [(0, 860), (W, 860)], t, 15, INK, 5)
    d.rectangle([0, 860, W, H], fill=(170, 140, 104))

def seated(d, x, t, k, face, name):
    wrect(d, x-70, SY-60, x+70, SY+10, t, k, (96, 72, 50))                          # chair seat
    wline(d, [(x-60*face, SY-200), (x-60*face, SY+110)], t, k+4, INK, 10)          # chair back
    figure(d, x, SY, t, k+10, col=(36, 28, 20), sit=True, face=face)
    for lx in (-14, 14): wline(d, [(x+lx, SY-60), (x+lx+80*face, SY-50), (x+lx+80*face, SY+110)], t, k+20+lx, (36, 28, 20), 16)
    label(d, x, SY-320, name, 28)

def desk(d, t):
    wrect(d, 560, 660, 1360, 700, t, 60, (110, 80, 52))
    wrect(d, 600, 700, 1320, 960, t, 64, (130, 98, 64))
    for dx in (680, 1240): wrect(d, dx-50, 760, dx+50, 820, t, 70+dx, (150, 116, 80))

def arms_to(d, x, face, ex, ey, t, k, both=False):
    sh = (x + 30*face, SY-150)
    wline(d, [sh, ((sh[0]+ex)/2, ey+30), (ex, ey)], t, k, (36, 28, 20), 15)
    if both: wline(d, [(x + 10*face, SY-145), ((x+ex)/2, ey+50), (ex, ey+14)], t, k+3, (36, 28, 20), 15)

def S_study1(t):  # 101.0 - 110.0: the envelope passes between them
    im = Image.new("RGB", (PXW, PXH), PAPER); d = SD(ImageDraw.Draw(im)); study(d, t)
    seated(d, GX, t, 100, 1, "DELE GIWA"); seated(d, SX, t, 200, -1, "KAYODE SOYINKA")
    desk(d, t)
    gh, sh = (GX + 150, SY - 120), (SX - 150, SY - 120)
    if t < 102.4: p = gh
    elif t < 103.8: u = ease((t-102.4)/1.4); p = (lerp(gh[0], sh[0], u), gh[1] - 60*math.sin(math.pi*u))
    elif t < 107.4: p = sh
    elif t < 108.8: u = ease((t-107.4)/1.4); p = (lerp(sh[0], gh[0], u), sh[1] - 60*math.sin(math.pi*u))
    else: p = gh
    arms_to(d, GX, 1, gh[0], gh[1], t, 300); arms_to(d, SX, -1, sh[0], sh[1], t, 400)
    envelope(d, p[0], p[1], 1.4)
    type_on(d, (120, 40), "GIWA EXAMINES IT", t, 101.2, 36, RED)
    type_on(d, (1200, 40), "SOYINKA READS THE WRITING", t, 105.2, 36, RED)
    return im

def S_study2(t):  # 146.8 - 162.85: opposite each other, the large desk between them
    im = Image.new("RGB", (PXW, PXH), PAPER); d = SD(ImageDraw.Draw(im)); study(d, t)
    seated(d, GX, t, 100, 1, "DELE GIWA"); seated(d, SX, t, 200, -1, "KAYODE SOYINKA")
    desk(d, t)
    ex, ey = GX + 170, SY - 150
    if t > 156.7: arms_to(d, GX, 1, ex, ey, t, 300, both=True)
    else: arms_to(d, GX, 1, GX + 150, SY - 120, t, 300)
    arms_to(d, SX, -1, SX - 120, SY - 100, t, 400)
    if t > 150.8:                                                                     # the desk between them
        u = ease((t-150.8)/1.2)
        y = 600; d.line([(GX + 110, y), (GX + 110 + (SX - GX - 220)*u, y)], fill=RED, width=5)
        for xx_ in (GX + 110, GX + 110 + (SX - GX - 220)*u): d.line([(xx_, y-16), (xx_, y+16)], fill=RED, width=5)
        type_on(d, (700, 540), "A LARGE DESK BETWEEN THEM", t, 151.2, 30)
    flap = ease((t-160.2)/2.4) if t > 160.2 else 0
    if t > 156.7: envelope(d, ex, ey, 1.6, flap)
    else: envelope(d, GX + 150, SY - 120, 1.4)
    type_on(d, (120, 40), "SITTING OPPOSITE EACH OTHER", t, 147.2, 36, RED)
    type_on(d, (1300, 40), "HELD WITH BOTH HANDS", t, 156.9, 36, RED)
    return im

# ---------------- E: the envelope, close up (110.0 - 137.4) ----------------
EX0, EY0, EX1, EY1 = 540, 250, 1380, 830
def callout(d, t, t0, tip, at, s, size=30, left=None):
    left = tip[0] > at[0]
    if t < t0: return
    u = ease((t-t0)/.5)
    d.line([at, (at[0] + (tip[0]-at[0])*u, at[1] + (tip[1]-at[1])*u)], fill=RED, width=4)
    if u >= 1: d.ellipse([tip[0]-9, tip[1]-9, tip[0]+9, tip[1]+9], fill=RED)
    f = F(MONO, size); n = int((t-t0)*24); w = f.getbbox(s)[2]
    d.text((at[0] - w - 14 if left else at[0] + 14, at[1] - size/2 - 4), s[:n], font=f, fill=RED)

def scribble(d, x, y, w, t, k, col=INK, wd=4):
    pts = [(x + i*w/14, y + 8*math.sin(i*1.9 + k)) for i in range(15)]
    wline(d, pts, t, k, col, wd)

def S_envelope(t):
    im = Image.new("RGB", (PXW, PXH), (196, 176, 140)); d = SD(ImageDraw.Draw(im))
    for y in range(0, H, 40): d.line([(0, y), (W, y)], fill=(188, 168, 132), width=2)
    wrect(d, EX0+16, EY0+16, EX1+16, EY1+16, t, 1, (120, 100, 76), (120, 100, 76), 1)   # shadow
    wrect(d, EX0, EY0, EX1, EY1, t, 2, BROWN, INK, 6)
    for i in range(0, 40):                                                             # padded texture
        x = EX0 + 30 + (i*197) % (EX1-EX0-60); y = EY0 + 30 + (i*131) % (EY1-EY0-60)
        d.ellipse([x-3, y-3, x+3, y+3], fill=(138, 102, 62))
    # coat of arms, simplified: shield with a Y, two supporters, an eagle above
    cx, cy = (EX0+EX1)/2, EY0 + 120
    if t > 133.0:
        d.ellipse([cx-16, cy-82, cx+16, cy-50], fill=INK)
        wpoly(d, [(cx-40, cy-40), (cx+40, cy-40), (cx+36, cy+20), (cx, cy+50), (cx-36, cy+20)], t, 3, (60, 46, 32), INK, 3)
        wline(d, [(cx-26, cy-30), (cx, cy), (cx+26, cy-30)], t, 4, CREAM, 6); wline(d, [(cx, cy), (cx, cy+36)], t, 5, CREAM, 6)
        for sx_ in (-1, 1): d.ellipse([cx + sx_*70 - 18, cy-40, cx + sx_*70 + 18, cy+40], fill=INK)
    # presidency markings: top-left block
    for i in range(3): scribble(d, EX0 + 50, EY0 + 70 + i*42, 260 - i*40, t, 10+i)
    # addressee-only marking: boxed, top right
    d.rectangle([EX1 - 330, EY0 + 50, EX1 - 50, EY0 + 160], outline=INK, width=4)
    scribble(d, EX1 - 310, EY0 + 88, 240, t, 20); scribble(d, EX1 - 310, EY0 + 128, 180, t, 21)
    # name and address
    f = F(SERIFI, 52); d.text((EX0 + 250, EY0 + 330), "Dele Giwa", font=f, fill=INK)
    f2 = F(SERIFI, 38); d.text((EX0 + 250, EY0 + 400), "25 Talabi Street,", font=f2, fill=INK); d.text((EX0 + 250, EY0 + 446), "Ikeja", font=f2, fill=INK)
    callout(d, t, 110.2, (EX0 + 40, EY1 - 60), (380, 930), "PADDED · BROWN", 32, left=False)
    callout(d, t, 113.4, (EX0 + 420, EY0 + 380), (1480, 930), "NAME & ADDRESS", 32)
    callout(d, t, 116.4, (EX0 + 200, EY0 + 90), (640, 140), "MARKINGS LINKED TO THE PRESIDENCY", 28, left=False)
    callout(d, t, 123.6, (EX0 + 180, EY0 + 150), (480, 330), "'COMMANDER-IN-CHIEF'", 28)
    callout(d, t, 127.6, (EX1 - 190, EY0 + 160), (1450, 380), "'ADDRESSEE ONLY'", 30)
    callout(d, t, 133.6, (cx + 40, cy - 20), (1300, 100), "COAT OF ARMS", 32)
    d.text((40, H-46), "SCHEMATIC · AS DESCRIBED IN LATER ACCOUNTS", font=F(MONO, 22), fill=INK)
    return im

def frame_img(t):
    if t < 54.3:
        return intertitle([("Sunday, 19 October 1986", 340, F(SERIF, 88), 0, CREAM),
                           ("25 Talabi Street, Ikeja", 480, F(SERIFI, 70), 0, CREAM),
                           ("Outside the house, a delivery was on its way.", 660, F(SERIF, 46), 49.6, (226, 120, 104))], t, 48.3,
                          extra=lambda d: d.line([(W/2-160, 450), (W/2+160, 450)], fill=RED, width=4)), [54.3]
    if t < 83.2: return S_gate(t), [83.2]
    if t < 101.0: return S_compound(t), [101.0]
    if t < 110.0: return S_study1(t), [110.0]
    if t < 137.4: return S_envelope(t), [137.4]
    if t < 146.8:
        return intertitle([("As recorded before the Oputa Panel:", 330, F(SERIF, 54), 0, CREAM),
                           ("Giwa remarked that it must", 470, F(SERIFI, 84), 138.4, CREAM),
                           ("have come from the President.", 575, F(SERIFI, 84), 138.4, CREAM)], t, 137.4,
                          extra=lambda d: d.line([(W/2-160, 420), (W/2+160, 420)], fill=RED, width=4)), [146.8]
    return S_study2(t), []

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
        cv2.imwrite(sys.argv[3] if len(sys.argv) > 3 else "vgw.jpg", np.vstack([np.hstack(th[i:i+3]) for i in range(0, len(th), 3)]))
    else:
        a, b = round(T0*FPS), round(T1*FPS)
        if os.environ.get('KAZ_VLIMIT'): b = a + int(os.environ['KAZ_VLIMIT'])
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{PXW}x{PXH}", "-r", "30", "-i", "-",
                              "-c:v", "libx264", "-preset", os.environ.get("KAZ_PRESET", "veryfast"), "-crf", os.environ.get("KAZ_CRF", "18"), "-pix_fmt", "yuv420p", os.environ.get("KAZ_VOUT", "vintage_gw.mp4")], stdin=subprocess.PIPE)
        for fi in range(a, b): p.stdin.write(frame(fi).tobytes())
        p.stdin.close(); p.wait()
