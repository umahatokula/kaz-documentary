"""Rebuild an episode's final soundtrack on the user's computer from its chapter WAVs.

Same chain as the workspace mix: voice (chapters concatenated, 48 kHz mono, padded to voice_len) +
sound_bed.py(cues.json), bed ducked under the voice, loudnorm -14 LUFS, gain_db, limiter, trimmed to the
video length. Rebuilding beats uploading a large audio file over a slow link; the result matches the
workspace mix sample for sample. episode.json: chapters ([wav names in the episode folder]),
voice_len (s), gain_db, audio (output name, e.g. "mix.flac"), frames.
"""
import json, os, subprocess, sys
TK = os.path.dirname(os.path.abspath(__file__))   # series toolkit; usage: make_audio.py EPISODE_DIR
EP = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd(); KAZ = os.path.join(EP, "kaz")
CFG = json.load(open(os.path.join(KAZ, "episode.json")))
out = os.path.join(KAZ, CFG.get("audio", "mix.flac")); W = os.path.join(EP, "_master"); os.makedirs(W, exist_ok=True)
if os.path.exists(out): sys.exit(0)
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
ch = CFG["chapters"]; inp = sum((["-i", os.path.join(EP, c)] for c in ch), [])
ff(*inp, "-filter_complex", f"concat=n={len(ch)}:v=0:a=1,aresample=48000,aformat=channel_layouts=mono,apad=whole_dur={CFG['voice_len']}", "-c:a", "pcm_s16le", f"{W}/voice.wav")
subprocess.run([sys.executable, os.path.join(TK, "sound_bed.py"), os.path.join(KAZ, "cues.json"), f"{W}/bed.wav"], check=True)
ff("-i", f"{W}/voice.wav", "-i", f"{W}/bed.wav", "-filter_complex",
   "[0:a]asplit=2[v][sc];[1:a][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[b];[v][b]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[o]",
   "-map", "[o]", "-ar", "48000", "-c:a", "pcm_s16le", f"{W}/mix.wav")
ff("-i", f"{W}/mix.wav", "-af", f"volume={CFG.get('gain_db', 0)}dB,alimiter=limit=0.89:level=false", "-t", str(CFG["frames"] / 30), "-c:a", "flac", out + ".tmp.flac")
os.replace(out + ".tmp.flac", out)
for f in ("voice.wav", "bed.wav", "mix.wav"): os.remove(f"{W}/{f}")
