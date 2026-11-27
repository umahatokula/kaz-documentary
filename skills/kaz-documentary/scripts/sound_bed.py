"""Kaz Documentary sound bed: dark drone + pulse + SFX, synthesized (no downloads).
Usage: python3 sound_bed.py cues.json out.wav
cues.json = {"duration": 92.6, "whoosh": [..s], "type": [[start_s, n_chars], ...],
             "thud": [..s], "shot": [..s], "scratch": [[start_s, dur_s], ...],
             "tension": [..s peaks], "film": [[start_s, end_s], ...], "engine": [[start_s, end_s], ...],
             "mood": "drone" | "piano" | "pulse" | "ambient"}   (mood is optional; default drone)
Moods: drone = dark low drone with a soft pulse (the original bed); piano = sparse felt-piano notes in a minor key
over a quiet pad; pulse = a ticking clock and slow heartbeat over a thin pad (procedural, countdown stories);
ambient = airy wind and slow high shimmer (landscapes, long aftermaths)."""
import numpy as np, wave, json, sys
c = json.load(open(sys.argv[1])); sr = 48000; D = c["duration"]; n = int(sr*D); t = np.arange(n)/sr
rng = np.random.default_rng(3)
mood = c.get("mood", "drone")
env = np.clip(t/3, 0, 1)*np.clip((D-t)/2.5, 0, 1)
def tension(y):
    for p in c.get("tension", []): y = y*(1+.6*np.exp(-((t-p)/5)**2))
    return y
def lowpad(scale=1.0):
    y = sum(a*np.sin(2*np.pi*f*t+np.sin(2*np.pi*.07*t)*2) for f, a in [(55,1),(65.4,.6),(82.4,.5),(110,.35),(130.8,.2)])
    return y*(.5+.5*np.sin(2*np.pi*t/23)**2)*env*scale
if mood == "piano":
    x = tension(lowpad())/np.abs(lowpad()).max()*.06
    notes = [110, 130.8, 146.8, 164.8, 196, 220, 261.6, 293.7]       # A minor
    for b in np.arange(4, D-4, 1.0):
        if rng.random() < .32:
            f = notes[rng.integers(len(notes))]; L = int(4*sr); u = np.arange(L)/sr
            tone = sum(h*np.sin(2*np.pi*f*k*u) for k, h in ((1, 1), (2, .45), (3, .18), (4, .08)))*np.exp(-u*1.3)*(1-np.exp(-u*80))
            i = int(b*sr); e = min(n, i+L); x[i:e] += .07*tone[:e-i]
elif mood == "pulse":
    x = tension(lowpad(.6))/np.abs(lowpad()).max()*.08
    for b in np.arange(6, D-3, 1.0):                                   # clock tick
        i = int(b*sr); L = int(.02*sr); x[i:i+L] += .05*rng.normal(0, 1, L)*np.exp(-np.arange(L)/sr*300)
    for b in np.arange(8, D-3, 1.0):                                   # heartbeat
        for off, g in ((0, .1), (.22, .06)):
            i = int((b+off)*sr); L = int(.18*sr); u = np.arange(L)/sr
            if i+L < n: x[i:i+L] += g*np.sin(2*np.pi*52*u)*np.exp(-u*22)
elif mood == "ambient":
    wn = rng.normal(0, 1, n); k = .004                                  # one-pole low-pass wind
    try:
        from scipy.signal import lfilter; y = lfilter([k], [1, k-1], wn)
    except ImportError:
        y = np.zeros(n); a = 0.0
        for j in range(n): a += k*(wn[j]-a); y[j] = a
    y = y/np.abs(y).max()*(.6+.4*np.sin(2*np.pi*t/31))
    sh = sum(np.sin(2*np.pi*f*t)*(.5+.5*np.sin(2*np.pi*t/p)) for f, p in ((659.3, 17), (987.8, 23), (1318.5, 29)))
    x = tension(y*.10 + sh*.012 + lowpad(.3)/np.abs(lowpad()).max()*.05)*env
else:
    pad = tension(lowpad())
    x = pad/np.abs(pad).max()*.16
    for b in np.arange(15, D-2, 1.25):
        i = int(b*sr); L = int(.25*sr); x[i:i+L] += .08*np.sin(2*np.pi*48*np.arange(L)/sr)*np.exp(-np.arange(L)/sr*18)
def add(s, at, g):
    i = int(at*sr); e = min(n, i+len(s)); x[i:e] += g*s[:e-i]
def whoosh(d=.6):
    L = int(d*sr); r = rng.normal(0,1,L); env = np.sin(np.linspace(0,np.pi,L))**2; y = np.zeros(L); a = 0
    for k in range(L): a += (.02+.25*env[k])*(r[k]-a); y[k] = a
    return y*env/(np.abs(y).max()+1e-9)
tt = np.arange(int(1.2*sr))/sr
thud = (np.sin(2*np.pi*(70*np.exp(-tt*6)+40)*tt)*np.exp(-tt*7)+.3*rng.normal(0,1,len(tt))*np.exp(-tt*40))
shot = rng.normal(0,1,len(tt))*np.exp(-tt*9)+.8*np.sin(2*np.pi*55*tt)*np.exp(-tt*4)
click = lambda: rng.normal(0,1,int(.03*sr))*np.exp(-np.arange(int(.03*sr))/sr*250)
W = whoosh()
for a in c.get("whoosh", []): add(W, a, .25)
for s, k in c.get("type", []):
    for j in range(k): add(click(), s+j/22, .12)
for a in c.get("thud", []): add(thud, a, .55)
for a in c.get("shot", []): add(shot, a, .55)
for a, d in c.get("scratch", []):
    L = int(d*sr); add(rng.normal(0,1,L)*.5*(1+np.sin(np.arange(L)/sr*90)), a, .05)
for a, b in c.get("film", []):   # projector clatter + hiss, board SFX softened
    i, j = int(a*sr), int(b*sr); x[i:j] *= .5; L = j-i; seg = np.zeros(L)
    for k in range(int(L/sr*24)):
        p = int(k*sr/24); m = int(.012*sr)
        if p+m < L: seg[p:p+m] += rng.normal(0,1,m)*np.exp(-np.arange(m)/sr*400)
    x[i:j] += seg*.06 + rng.normal(0,1,L)*.02
for a, b in c.get("engine", []):
    i, j = int(a*sr), int(b*sr); u = np.arange(j-i)/sr; x[i:j] += np.sin(2*np.pi*38*u)*(np.sin(2*np.pi*9*u) > 0)*.12
w = wave.open(sys.argv[2], "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes()); w.close()
