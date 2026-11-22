"""Render the 2560x1440 upload master of a kaz-documentary episode on the user's computer.

Lives in the series toolkit (<series>/_toolkit, with hd.py, themes.py, promo.py, sound_bed.py, make_audio.py,
fonts/, countries.geojson and the shared venv). Usage: run_master.py EPISODE_DIR, started by
<series>/<episode>/render_master.command via render_episode.sh. The episode's own files (board script,
insert scripts, data files, captions, episode.json) live in EPISODE_DIR/kaz/.
Builds the soundtrack, renders the board in parallel chunks around the inserts, renders each insert,
then runs the promo pass into <episode>/out/. Re-running resumes: finished pieces are kept until the
final file is written.

episode.json:
  name, channel, frames (total video frames at 30 fps, without the end screen),
  board ("board.py": supports `full START END OUT`), inserts ([{"script": "vint.py", "frames": [a, b]}]:
  each supports `full` and writes to $KAZ_VOUT), prompt_times ("62.0,410.5,705.2"), end_len (10),
  end_bg_time (seconds, a calm late board moment for the blurred end-screen background),
  audio ("mix.flac", built by make_audio.py), final_bitrate ("20M"), srt (optional captions file).
"""
import json, os, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

TK = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
KAZ = os.path.join(EP, "kaz")
CFG = json.load(open(os.path.join(KAZ, "episode.json")))
WORK = os.path.join(EP, "_master"); OUT = os.path.join(EP, "out")
os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)
FPS = 30
env = dict(os.environ, PYTHONPATH=TK, KAZ_SCALE=str(4/3), KAZ_ASSETS=EP, KAZ_CRF="16", KAZ_PRESET="veryfast")
PY = sys.executable


def mem_gb():
    try:
        return int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout) / 2**30
    except Exception:
        try:
            return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30
        except Exception:
            return 8


cores = os.cpu_count() or 4
workers = max(1, min(cores - 1, int(mem_gb() / float(CFG.get("gb_per_worker", 3.2)))))
print(f"{cores} cores, {mem_gb():.0f} GB memory -> {workers} render workers", flush=True)

print("Building the soundtrack...", flush=True)
subprocess.run([PY, os.path.join(TK, "make_audio.py"), EP], env=env, check=True)

inserts = sorted(CFG.get("inserts", []), key=lambda i: i["frames"][0])
jobs, cur = [], int(CFG.get("first_frame", 0))   # first_frame: tests only
for seg_end in [i["frames"][0] for i in inserts] + [CFG["frames"]]:
    a, b = cur, seg_end
    if b > a:
        n = max(1, round((b - a) / 1500))
        for k in range(n):
            s, e = a + (b - a) * k // n, a + (b - a) * (k + 1) // n
            jobs.append(("board", CFG["board"], s, e, os.path.join(WORK, f"b_{s:06d}.mp4")))
    nxt = [i for i in inserts if i["frames"][0] == seg_end]
    if nxt:
        i = nxt[0]; jobs.append(("insert", i["script"], i["frames"][0], i["frames"][1], os.path.join(WORK, f"v_{i['frames'][0]:06d}.mp4")))
        cur = i["frames"][1]
jobs.sort(key=lambda j: j[2])


def run(job):
    kind, script, s, e, out = job
    if os.path.exists(out + ".done"):
        return job
    if kind == "board":
        r = subprocess.run([PY, os.path.join(KAZ, script), "full", str(s), str(e), out], env=env, cwd=WORK, capture_output=True, text=True)
    else:
        r = subprocess.run([PY, os.path.join(KAZ, script), "full"], env=dict(env, KAZ_VOUT=out), cwd=WORK, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{script} {s}-{e} failed:\n{r.stderr[-2000:]}")
    open(out + ".done", "w").write("ok")
    return job


start = time.time(); done = sum(os.path.exists(j[4] + ".done") for j in jobs)
print(f"Rendering {len(jobs)} pieces at 2560x1440 ({done} already done from an earlier run)...", flush=True)
order = sorted(jobs, key=lambda j: -(j[3] - j[2]) * (2 if j[0] == "insert" else 1))
with ThreadPoolExecutor(workers) as ex:
    for f in as_completed([ex.submit(run, j) for j in order]):
        f.result(); done += 1
        print(f"  {done}/{len(jobs)} pieces done  ({(time.time()-start)/60:.0f} min so far)", flush=True)

print("Joining, adding subscribe prompts, end screen and soundtrack (final encode)...", flush=True)
lst = os.path.join(WORK, "list.txt")
open(lst, "w").write("".join(f"file '{j[4]}'\n" for j in jobs))
host = [j for j in jobs if j[2] / FPS <= CFG["end_bg_time"] < j[3] / FPS] or [jobs[-1]]
final = os.path.join(OUT, CFG["name"] + "_1440p.mp4")
subprocess.run([PY, os.path.join(TK, "promo.py"), "build", lst, final, "--channel", CFG["channel"], "--times", CFG["prompt_times"],
                "--end", str(CFG.get("end_len", 10)), "--audio", os.path.join(KAZ, CFG.get("audio", "mix.flac")),
                "--dur", str(CFG["frames"] / FPS), "--bg-src", host[0][4], "--bg-time", f"{CFG['end_bg_time'] - host[0][2] / FPS:.2f}",
                "--bitrate", CFG.get("final_bitrate", "20M"), "--maxrate", "30M", "--bufsize", "40M"],
               env=dict(env, KAZ_FINAL_PRESET="medium"), cwd=WORK, check=True)
if CFG.get("srt") and os.path.exists(os.path.join(KAZ, CFG["srt"])):
    shutil.copy(os.path.join(KAZ, CFG["srt"]), os.path.join(OUT, CFG["name"] + "_1440p.srt"))
shutil.rmtree(final[:-4] + "_promo", ignore_errors=True)
for j in jobs:
    for p in (j[4], j[4] + ".done"):
        if os.path.exists(p): os.remove(p)
print(f"\nDONE in {(time.time()-start)/60:.0f} min: {final}", flush=True)
