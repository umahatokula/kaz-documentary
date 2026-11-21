"""Kaz Documentary promo pass: subscribe prompts + YouTube end screen.

Adds 3-4 s "subscribe" prompts at calm moments and appends a 10 s end screen with
clear space for one YouTube video element and the channel logo (subscribe element).
No outlines are drawn round either space, so YouTube's own elements can sit anywhere in them.

Usage:
  python3 promo.py pick DURATION busy.json [--targets 0.1,0.45,0.75] [--len 4]
      busy.json = [[start_s, end_s], ...]  (year/count/thesis cards, inserts, stamps, flashes, end title)
      prints comma-separated start times of free windows nearest each target fraction.
  python3 promo.py build master.mp4 out.mp4 --channel NAME --times 62,410,705
      [--bg-time 815] [--line "ENJOYING THE CASE FILE?"] [--end 10] [--bitrate 3400k --maxrate 5000k --bufsize 7000k | --crf 24]
      [--audio mix.flac] [--dur SECONDS] [--bg-src part.mp4]
      master.mp4 = finished video with its mixed audio, or a concat list (.txt) of video parts plus --audio and --dur.
      KAZ_SCALE=4/3 renders the prompts and end screen natively at 2560x1440 (hd.py); KAZ_FINAL_PRESET sets the x264 preset.
"""
import argparse, json, math, subprocess, sys, wave, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os as _os, sys as _sys
ROOT = _os.path.dirname(_os.path.abspath(__file__)); _sys.path.insert(0, ROOT)
from hd import SD, SFont, KS, PXW, PXH, MONO, SERIF

W, H, FPS, SR = 1920, 1080, 30, 48000
RED = (208, 49, 45)
SUB_LEN = 4.0
# End-screen layout (YouTube end-screen element zones, kept empty):
VIDEO_BOX = (150, 290, 1050, 796)      # 900x506, 16:9 video element space
LOGO_C, LOGO_R = (1460, 543), 200      # channel logo / subscribe element space

def font(p, s): return SFont(p, int(s))
def cl(x, a=0., b=1.): return max(a, min(b, x))
def ss(x): x = cl(x); return x*x*(3-2*x)
def backout(x, s=1.7): x = cl(x)-1; return 1+(s+1)*x**3+s*x**2

# ---------------- picking calm windows ----------------
def pick(duration, busy, targets, length=SUB_LEN, margin=1.0, start_min=20.0, end_pad=25.0):
    busy = [(a-margin, b+margin) for a, b in busy]
    def free(s): return s >= start_min and s+length <= duration-end_pad and all(s+length <= a or s >= b for a, b in busy)
    out = []
    for f in targets:
        c = f*duration; best = None
        for k in range(0, int(duration*4)):
            for s in (c+k/4, c-k/4):
                if free(s) and all(abs(s-o) > 60 for o in out): best = s; break
            if best is not None: break
        if best is not None: out.append(round(best, 2))
    return sorted(out)

# ---------------- subscribe prompt (RGBA frames) ----------------
def bell(d, cx, cy, s, ang, col):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    def P(x, y): return (cx + (x*ca - y*sa)*s, cy + (x*sa + y*ca)*s)
    body = [P(-.62, .45), P(-.55, -.25), P(-.3, -.62), P(0, -.72), P(.3, -.62), P(.55, -.25), P(.62, .45), P(.8, .62), P(-.8, .62)]
    d.polygon(body, fill=col); d.ellipse([P(0, .82)[0]-.18*s, P(0, .82)[1]-.18*s, P(0, .82)[0]+.18*s, P(0, .82)[1]+.18*s], fill=col)
    d.ellipse([P(0, -.8)[0]-.1*s, P(0, -.8)[1]-.1*s, P(0, -.8)[0]+.1*s, P(0, -.8)[1]+.1*s], fill=col)

def cursor(d, x, y, s=1.0):
    pts = [(0, 0), (0, 44), (11, 34), (19, 52), (27, 48), (19, 31), (33, 31)]
    pts = [(x+px*s, y+py*s) for px, py in pts]
    d.polygon(pts, fill=(245, 245, 240)); d.line(pts+[pts[0]], fill=(10, 10, 10), width=3)

def sub_frame(u, line, channel):
    """u = seconds into the 4 s prompt. Returns RGBA PIL image W x H."""
    im = Image.new("RGBA", (PXW, PXH), (0, 0, 0, 0))
    inn = backout(u/.4); out = ss((u-(SUB_LEN-.4))/.4)
    dy = (1-inn)*260 + out*260; alpha = ss(u/.25)*(1-out)
    cw, ch = 470, 170
    card = Image.new("RGBA", (int((cw+80)*KS), int((ch+80)*KS)), (0, 0, 0, 0)); cd = SD(ImageDraw.Draw(card))
    sh = Image.new("L", card.size, 0); SD(ImageDraw.Draw(sh)).rectangle([40, 52, 40+cw, 52+ch], fill=150)
    card.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(12*KS)))
    cd.rectangle([40, 40, 40+cw, 40+ch], fill=(232, 224, 205, 255))
    for yy in range(66, 40+ch, 26): cd.line([(40, yy), (40+cw, yy)], fill=(210, 200, 180, 255), width=1)
    cd.polygon([(40+cw/2-55, 30), (40+cw/2+55, 26), (40+cw/2+57, 52), (40+cw/2-53, 56)], fill=(214, 204, 170, 220))
    n = min(len(line), int(max(0, u-.3)*26))
    cd.text((62, 58), line[:n], font=font(MONO, 26), fill=(40, 36, 32, 255))
    clicked = u > 1.75
    bx0, by0, bx1, by1 = 62, 110, 40+cw-22, 188
    press = 1 - .06*math.exp(-((u-1.75)/.06)**2)
    mx, my = (bx0+bx1)/2, (by0+by1)/2
    bx0, bx1 = mx-(mx-bx0)*press, mx+(bx1-mx)*press; by0, by1 = my-(my-by0)*press, my+(by1-my)*press
    cd.rounded_rectangle([bx0, by0, bx1, by1], 14, fill=(70, 66, 62, 255) if clicked else RED+(255,))
    label = "SUBSCRIBED" if clicked else "SUBSCRIBE"
    f = font(SERIF, 44); tw = f.getbbox(label)[2]
    cd.text((mx-tw/2-22, by0+12), label, font=f, fill=(245, 242, 235, 255))
    ang = 0 if u < 2.0 else 22*math.sin((u-2.0)*28)*math.exp(-(u-2.0)*3)
    bell(cd, mx+tw/2+18, my, 17, ang, (245, 242, 235, 255))
    card = card.rotate(-2, resample=Image.BICUBIC, expand=False)
    x0, y0 = W-cw-120, H-ch-150+dy
    a = np.array(card); a[..., 3] = (a[..., 3]*alpha).astype(np.uint8)
    im.alpha_composite(Image.fromarray(a), (int(x0*KS), int(y0*KS)))
    d = SD(ImageDraw.Draw(im))
    # cursor glides in, clicks, glides away
    if .8 < u < SUB_LEN-.5:
        k = ss((u-.8)/.85); k2 = ss((u-2.6)/.7)
        tx, ty = x0+40+mx+30, y0+40+my+10
        cx = tx + (1-k)*260 + k2*200; cy = ty + (1-k)*180 + k2*160
        cursor(d, cx, cy, .9 if abs(u-1.75) < .08 else 1.0)
    return im

# ---------------- end screen ----------------
def end_bg(master, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", master, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(PXH, PXW, 3)
    img = Image.fromarray(f).filter(ImageFilter.GaussianBlur(18*KS))
    return np.asarray(img).astype(np.float32) * .28

def end_frame(bg, u, total, channel, rng):
    zoom = 1.04 + .03*u/total
    M = cv2.getRotationMatrix2D((PXW/2, PXH/2), 0, zoom)
    b = cv2.warpAffine(bg, M, (PXW, PXH), borderMode=cv2.BORDER_REFLECT)
    im = Image.fromarray(np.clip(b, 0, 255).astype(np.uint8)); d = SD(ImageDraw.Draw(im, "RGBA"))
    a = int(255*ss((u-.3)/.6))
    f = font(SERIF, 72); tw = f.getbbox(channel)[2]
    d.text(((W-tw)/2, 70), channel, font=f, fill=RED+(a,))
    fm = font(MONO, 36)
    s = "WATCH NEXT"; d.text((VIDEO_BOX[0], VIDEO_BOX[1]-62), s[:int(max(0, u-.5)*22)], font=fm, fill=(225, 222, 210, a))
    s = "SUBSCRIBE"; w2 = fm.getbbox(s)[2]
    d.text((LOGO_C[0]-w2/2, LOGO_C[1]+LOGO_R+26), s[:int(max(0, u-.7)*22)], font=fm, fill=(225, 222, 210, a))
    o = np.asarray(im).astype(np.float32) + rng.normal(0, 6, (PXH, PXW, 1))
    fade = ss(u/.5) * (1 - ss((u-(total-.6))/.6))
    return np.clip(o*fade, 0, 255).astype(np.uint8)

# ---------------- audio ----------------
def write_wav(path, x):
    w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1)*32767).astype(np.int16).tobytes()); w.close()
def sub_audio(path):
    rng = np.random.default_rng(5); n = int(SUB_LEN*SR); x = np.zeros(n); t = np.arange(int(.25*SR))/SR
    pop = np.sin(2*np.pi*(520+300*np.exp(-t*30))*t)*np.exp(-t*22)*.25
    x[int(.05*SR):int(.05*SR)+len(pop)] += pop
    m = int(.02*SR); clk = rng.normal(0, 1, m)*np.exp(-np.arange(m)/SR*300)*.35
    x[int(1.75*SR):int(1.75*SR)+m] += clk
    tb = np.arange(int(1.2*SR))/SR
    ding = sum(a*np.sin(2*np.pi*f*tb) for f, a in [(1318, .5), (1976, .25), (2637, .12)])*np.exp(-tb*4)*.18
    x[int(2.0*SR):int(2.0*SR)+len(ding)] += ding
    write_wav(path, x)
def end_audio(path, total):
    t = np.arange(int(total*SR))/SR
    x = sum(a*np.sin(2*np.pi*f*t+np.sin(2*np.pi*.07*t)*2) for f, a in [(55, 1), (65.4, .6), (82.4, .5), (110, .35)])
    x = x/np.abs(x).max()*.14*np.clip(t/1.5, 0, 1)*np.clip((total-t)/3, 0, 1)
    write_wav(path, x)

def build(a):
    work = os.path.splitext(a.out)[0] + "_promo"; os.makedirs(work, exist_ok=True)
    times = [float(x) for x in a.times.split(",") if x]
    # subscribe overlay clip with alpha
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{PXW}x{PXH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "qtrle", f"{work}/sub.mov"], stdin=subprocess.PIPE)
    for i in range(int(SUB_LEN*FPS)): p.stdin.write(np.asarray(sub_frame(i/FPS, a.line, a.channel)).tobytes())
    p.stdin.close(); p.wait(); sub_audio(f"{work}/sub.wav")
    # end screen
    dur = a.dur or float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.master], capture_output=True, text=True).stdout)
    bg = end_bg(a.bg_src or a.master, a.bg_time if a.bg_time is not None else max(0, dur-12)); rng = np.random.default_rng(9)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{PXW}x{PXH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", f"{work}/end.mp4"], stdin=subprocess.PIPE)
    for i in range(int(a.end*FPS)): p.stdin.write(end_frame(bg, i/FPS, a.end, a.channel, rng).tobytes())
    p.stdin.close(); p.wait(); end_audio(f"{work}/end.wav", a.end)
    # compose
    cmd = ["ffmpeg", "-y", "-v", "error"] + (["-f", "concat", "-safe", "0"] if a.master.endswith(".txt") else []) + ["-i", a.master]
    for t in times: cmd += ["-itsoffset", str(t), "-i", f"{work}/sub.mov"]
    cmd += ["-i", f"{work}/end.mp4", "-i", f"{work}/end.wav", "-i", f"{work}/sub.wav"] + (["-i", a.audio] if a.audio else [])
    ne = 1+len(times); fc = []; v = "[0:v]"
    for k, t in enumerate(times):
        fc.append(f"{v}[{k+1}:v]overlay=0:0:eof_action=pass:enable='between(t,{t},{t+SUB_LEN})'[v{k}]"); v = f"[v{k}]"
    sa = ne+2
    fc.append(f"[{sa}:a]asplit={len(times)}" + "".join(f"[s{k}]" for k in range(len(times))))
    for k, t in enumerate(times): fc.append(f"[s{k}]adelay={int(t*1000)}|{int(t*1000)}[d{k}]")
    fc.append(f"[{ne+3 if a.audio else 0}:a]aformat=sample_rates={SR}:channel_layouts=stereo[m]")
    fc.append("[m]" + "".join(f"[d{k}]" for k in range(len(times))) + f"amix=inputs={len(times)+1}:normalize=0:duration=first[ma]")
    fc.append(f"[{ne+1}:a]aformat=sample_rates={SR}:channel_layouts=stereo[ea]")
    fc.append(f"{v}[ma][{ne}:v][ea]concat=n=2:v=1:a=1[vo][ao]")
    enc = ["-b:v", a.bitrate, "-maxrate", a.maxrate, "-bufsize", a.bufsize] if a.bitrate else ["-crf", str(a.crf)]
    cmd += ["-filter_complex", ";".join(fc), "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-preset", os.environ.get("KAZ_FINAL_PRESET", "veryfast"), *enc,
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    print("subscribe prompts at", times, "| end screen", a.end, "s | video space", VIDEO_BOX, "| logo centre", LOGO_C, "r", LOGO_R)

if __name__ == "__main__":
    if sys.argv[1] == "pick":
        ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("duration", type=float); ap.add_argument("busy")
        ap.add_argument("--targets", default="0.1,0.45,0.75"); ap.add_argument("--len", type=float, default=SUB_LEN)
        a = ap.parse_args(); print(",".join(str(x) for x in pick(a.duration, json.load(open(a.busy)), [float(x) for x in a.targets.split(",")], a.len)))
    elif sys.argv[1] == "preview":
        line = sys.argv[2] if len(sys.argv) > 2 else "ENJOYING THE CASE FILE?"
        for u in (0.2, 0.6, 1.4, 1.8, 2.3, 3.8):
            bgi = Image.new("RGBA", (PXW, PXH), (40, 44, 38, 255)); bgi.alpha_composite(sub_frame(u, line, "X")); bgi.convert("RGB").save(f"sub_{u}.png")
    else:
        ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("master"); ap.add_argument("out")
        ap.add_argument("--channel", required=True); ap.add_argument("--times", required=True); ap.add_argument("--bg-time", type=float, default=None)
        ap.add_argument("--line", default="ENJOYING THE CASE FILE?"); ap.add_argument("--end", type=float, default=10.0)
        ap.add_argument("--bitrate", default=None); ap.add_argument("--maxrate", default="5000k"); ap.add_argument("--bufsize", default="7000k"); ap.add_argument("--crf", type=int, default=24)
        ap.add_argument("--audio", default=None); ap.add_argument("--dur", type=float, default=None); ap.add_argument("--bg-src", default=None)
        build(ap.parse_args())
