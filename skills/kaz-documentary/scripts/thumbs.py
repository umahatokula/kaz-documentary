"""Thumbnail layouts for kaz-documentary episodes (1280x720 JPG).

Usage: python3 thumbs.py spec.json
spec.json is a list of thumbnails, for example:
[{"layout": "pinned", "out": "thumb_A.jpg", "text": "ACCIDENT|OR ATTACK?", "tag": "NDOLA · 18 SEPT 1961",
  "main": "hammarskjold1.jpg", "second": "albertina.jpg", "theme": "blueprint"},
 {"layout": "fullbleed", "out": "thumb_B.jpg", "text": "65 YEARS.|NO ANSWER.", "tag": "NDOLA · 1961", "main": "wreck.jpg"}]

Layouts (rotate them across episodes; never use the same one twice in a row):
  pinned    two pinned photos on the board colour, a red string between the pins, a stamp with the text.
  split     the main photo fills the left 55% in black and white; huge text on a dark right panel, last line red.
  fullbleed the main photo fills the frame, darkened towards the bottom; huge text bottom left over a red bar.
  casefile  a manila folder: the main photo paper-clipped to it, a typed tab label, the text as a red rubber stamp,
            the second image as a small polaroid.
Images are looked up in $KAZ_ASSETS (the episode folder). "text" uses | for line breaks; keep it to 2-4 words a line.
"theme" picks the board colour for pinned (any themes.py name; default teal_slate). Photos of real people must be
the user's own files.
"""
import json, os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hd import MONO, SERIF

W, H = 1280, 720
RED = (214, 40, 36)
A = os.environ.get("KAZ_ASSETS", ".")
rng = np.random.default_rng(3)
BOARD_RGB = {"teal_slate": (22, 40, 42), "cork": (120, 86, 58), "chalkboard": (30, 42, 36), "blueprint": (16, 40, 72),
             "manila": (196, 168, 118), "olive_canvas": (70, 74, 48), "concrete": (96, 96, 92)}


def font(p, s): return ImageFont.truetype(p, s)


def load(name, gray=True, contrast=1.15):
    im = Image.open(os.path.join(A, name)).convert("RGB")
    if gray: im = im.convert("L").convert("RGB")
    return ImageEnhance.Contrast(im).enhance(contrast)


def board(rgb):
    bg = np.zeros((H, W, 3), np.float32) + np.array(rgb, np.float32)
    n = cv2.resize(rng.random((H//30, W//30)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    bg += (n[..., None] - .5) * 26
    yy, xx = np.mgrid[:H, :W]
    vig = 1 - .55*np.clip(((xx-W/2)/(W*.7))**2 + ((yy-H/2)/(H*.7))**2, 0, 1)
    return Image.fromarray(np.clip(bg*vig[..., None], 0, 255).astype(np.uint8)).convert("RGBA")


def pinned(name, w, rot, gray=True):
    im = load(name, gray); h = int(im.height*w/im.width); im = im.resize((w, h), Image.LANCZOS)
    b = 14; card = Image.new("RGBA", (w + 2*b, h + 2*b), (236, 229, 212, 255)); card.paste(im, (b, b))
    pad = 40; out = Image.new("RGBA", (card.width + 2*pad, card.height + 2*pad), (0, 0, 0, 0))
    sh = Image.new("L", out.size, 0); ImageDraw.Draw(sh).rectangle([pad+8, pad+16, pad+card.width+8, pad+card.height+16], fill=170)
    out.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14))); out.alpha_composite(card, (pad, pad))
    d = ImageDraw.Draw(out); px = out.width//2; d.ellipse([px-10, pad+2, px+10, pad+22], fill=RED + (255,))
    return out.rotate(rot, resample=Image.BICUBIC, expand=True)


def pin_point(img, at):
    """Centre of the red pin in a pasted card (img pasted at `at`)."""
    a = np.asarray(img); m = (a[..., 0] > 180) & (a[..., 1] < 80) & (a[..., 3] > 200)
    ys, xs = np.nonzero(m)
    return (at[0] + xs.mean(), at[1] + ys.mean()) if len(xs) else (at[0] + img.width/2, at[1] + 50)


def stamp(text, size, rot, fill=(12, 12, 12, 200)):
    f = font(SERIF, size); lines = text.split("|")
    tw = max(f.getbbox(l)[2] for l in lines); lh = int(size*1.08); th = lh*len(lines)
    s = Image.new("RGBA", (tw + 60, th + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    d.rectangle([6, 6, s.width-6, s.height-6], fill=fill, outline=RED + (255,), width=9)
    for i, l in enumerate(lines):
        lw = f.getbbox(l)[2]; d.text(((s.width - lw)/2, 12 + i*lh), l, font=f, fill=RED + (255,))
    a = np.array(s); keep = rng.random(a.shape[:2]) > .12; a[..., 3] = a[..., 3]*keep
    return Image.fromarray(a).rotate(rot, resample=Image.BICUBIC, expand=True)


def tagbox(d, x, y, text, size=34, right=False):
    f = font(MONO, size); tw = f.getbbox(text)[2]
    if right: x = x - tw - 30
    d.rectangle([x, y, x + tw + 30, y + size + 14], fill=(14, 14, 14, 235)); d.text((x + 15, y + 6), text, font=f, fill=(236, 236, 228))


def fit_text(lines, maxw, maxh, start=150):
    s = start
    while s > 40:
        f = font(SERIF, s)
        if max(f.getbbox(l)[2] for l in lines) <= maxw and len(lines)*s*1.05 <= maxh: return f, s
        s -= 4
    return font(SERIF, 40), 40


def L_pinned(sp):
    im = board(BOARD_RGB.get(sp.get("theme", "teal_slate"), (22, 40, 42)))
    g = pinned(sp["main"], 560, 3); im.alpha_composite(g, (0, 10)); p1 = pin_point(g, (0, 10))
    if sp.get("second"):
        c = pinned(sp["second"], 520, -5); at = (W - c.width - 30, 0); im.alpha_composite(c, at); p2 = pin_point(c, at)
        ImageDraw.Draw(im).line([p1, p2], fill=RED + (230,), width=5)
    st = stamp(sp["text"], sp.get("size", 100), 5); im.alpha_composite(st, (W - st.width - 25, H - st.height - 25))
    if sp.get("tag"): tagbox(ImageDraw.Draw(im), W - 30, 352, sp["tag"], right=True)
    return im


def L_split(sp):
    im = Image.new("RGBA", (W, H), (14, 14, 16, 255))
    ph = ImageOps.fit(load(sp["main"]), (int(W*.55), H), Image.LANCZOS, centering=(.5, .3))
    im.paste(ph, (0, 0))
    g = Image.new("L", (int(W*.55), H), 0); gd = ImageDraw.Draw(g)
    for x in range(160): gd.line([(int(W*.55) - x, 0), (int(W*.55) - x, H)], fill=int(255*(1 - x/160)))
    im.paste((14, 14, 16, 255), (0, 0), g)
    d = ImageDraw.Draw(im); lines = sp["text"].split("|"); x0 = int(W*.52)
    f, s = fit_text(lines, W - x0 - 50, H - 220, 150); y = (H - len(lines)*s*1.05)/2 + 20
    for i, l in enumerate(lines):
        d.text((x0, y + i*s*1.05), l, font=f, fill=RED if i == len(lines) - 1 else (240, 236, 226))
    d.rectangle([x0, y - 34, x0 + 120, y - 24], fill=RED)
    if sp.get("tag"): tagbox(d, x0, 40, sp["tag"], 30)
    return im


def L_fullbleed(sp):
    ph = ImageOps.fit(load(sp["main"], contrast=1.25), (W, H), Image.LANCZOS, centering=(.5, .35)).convert("RGBA")
    a = np.asarray(ph).astype(np.float32); yy = np.arange(H)[:, None, None]/H
    a[..., :3] *= (1 - .78*np.clip((yy - .25)/.75, 0, 1))*.9
    im = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(im); lines = sp["text"].split("|")
    f, s = fit_text(lines, W - 120, H*.5, 160); y = H - 60 - len(lines)*s*1.05
    d.rectangle([50, y - 30, 50 + 160, y - 16], fill=RED)
    for i, l in enumerate(lines): d.text((50, y + i*s*1.05), l, font=f, fill=(244, 240, 230))
    if sp.get("tag"): tagbox(d, 50, 40, sp["tag"], 30)
    return im


def L_casefile(sp):
    im = board((150, 120, 80))
    fold = Image.new("RGBA", (W - 80, H - 60), (214, 186, 132, 255)); fd = ImageDraw.Draw(fold)
    fd.rectangle([60, -10, 420, 50], fill=(200, 170, 116, 255))
    for i in range(0, fold.height, 6): fd.line([(0, i), (fold.width, i)], fill=(208, 180, 126, 255))
    im.alpha_composite(fold, (40, 40)); d = ImageDraw.Draw(im)
    if sp.get("tag"): d.text((120, 48), sp["tag"], font=font(MONO, 30), fill=(40, 32, 24))
    ph = ImageOps.fit(load(sp["main"]), (430, 540), Image.LANCZOS, centering=(.5, .3)); card = Image.new("RGBA", (454, 564), (240, 236, 226, 255))
    card.paste(ph, (12, 12)); card = card.rotate(-3, resample=Image.BICUBIC, expand=True); im.alpha_composite(card, (90, 120))
    d.rounded_rectangle([290, 96, 320, 170], 12, outline=(150, 150, 156), width=6)                       # paper clip
    if sp.get("second"):
        p2 = ImageOps.fit(load(sp["second"]), (260, 220), Image.LANCZOS); pol = Image.new("RGBA", (284, 290), (244, 242, 236, 255))
        pol.paste(p2, (12, 12)); pol = pol.rotate(6, resample=Image.BICUBIC, expand=True); im.alpha_composite(pol, (W - 360, 70))
    st = stamp(sp["text"], sp.get("size", 96), -6, fill=(0, 0, 0, 0)); im.alpha_composite(st, (W - st.width - 50, H - st.height - 70))
    return im


LAYOUTS = {"pinned": L_pinned, "split": L_split, "fullbleed": L_fullbleed, "casefile": L_casefile}

if __name__ == "__main__":
    for sp in json.load(open(sys.argv[1])):
        LAYOUTS[sp["layout"]](sp).convert("RGB").save(sp["out"], quality=92); print("wrote", sp["out"])
