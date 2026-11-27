"""Per-episode style menu with rotation rules.

  python3 style_menu.py SERIES_DIR                 print every decision with its options, marking the ones
                                                   blocked by the rotation rules (JSON, for building questions)
  python3 style_menu.py SERIES_DIR add EP CHOICES  record an episode's choices (CHOICES: a JSON file or string)
                                                   in SERIES_DIR/style_log.json, after checking the rules
  python3 style_menu.py SERIES_DIR check CHOICES   check choices against the rules without recording them

SERIES_DIR is the series folder (for example ~/Documents/Kaz Documentary). The log is a list of
{"episode": ..., "date": ..., "choices": {...}} in upload order. Rules come from styles.json: an option of a
decision with "rotate": N may not repeat any of the previous N episodes' choices for that decision. thumb_layout
may be a list [main, test]; both count. Free-text decisions (set_piece) are recorded but never blocked.
"""
import json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = json.load(open(os.path.join(HERE, "styles.json")))["decisions"]


def load_log(series):
    p = os.path.join(series, "style_log.json")
    return json.load(open(p)) if os.path.exists(p) else []


def used(log, key, n):
    out = {}
    for e in log[-n:] if n else []:
        v = e["choices"].get(key)
        for x in (v if isinstance(v, list) else [v]):
            if x: out[x] = e["episode"]
    return out


def menu(series):
    log = load_log(series); res = []
    for d in SPEC:
        u = used(log, d["key"], d.get("rotate", 0)); item = {"key": d["key"], "group": d["group"], "question": d["question"]}
        if d.get("free"):
            item["free"] = True; item["hint"] = d.get("hint", ""); item["previous"] = [e["choices"].get(d["key"]) for e in log[-3:]]
        else:
            item["allowed"] = {k: v for k, v in d["options"].items() if k not in u}
            item["blocked"] = {k: f"used in {u[k]}" for k in d["options"] if k in u}
        res.append(item)
    return {"episodes_logged": [e["episode"] for e in log], "decisions": res}


def check(series, choices, exclude=None):
    log = [e for e in load_log(series) if e["episode"] != exclude]; problems = []
    for d in SPEC:
        v = choices.get(d["key"])
        if v is None: problems.append(f"{d['key']}: not chosen"); continue
        if d.get("free"): continue
        vals = v if isinstance(v, list) else [v]
        for x in vals:
            if x not in d["options"]: problems.append(f"{d['key']}: unknown option {x!r}")
        u = used(log, d["key"], d.get("rotate", 0))
        for x in vals:
            if x in u: problems.append(f"{d['key']}: {x!r} was used in {u[x]} (rotate {d['rotate']})")
    return problems


def read_choices(arg):
    return json.load(open(arg)) if os.path.exists(arg) else json.loads(arg)


if __name__ == "__main__":
    series = os.path.expanduser(sys.argv[1])
    if len(sys.argv) == 2:
        print(json.dumps(menu(series), indent=1, ensure_ascii=False))
    elif sys.argv[2] == "check":
        p = check(series, read_choices(sys.argv[3])); print("\n".join(p) if p else "ok")
    elif sys.argv[2] == "add":
        ep, ch = sys.argv[3], read_choices(sys.argv[4]); p = check(series, ch, exclude=ep)
        if p and "--force" not in sys.argv:
            print("not recorded:\n" + "\n".join(p) + "\n(re-run with --force only if the user chose this knowingly)"); sys.exit(1)
        log = [e for e in load_log(series) if e["episode"] != ep]
        log.append({"episode": ep, "date": datetime.date.today().isoformat(), "choices": ch})
        json.dump(log, open(os.path.join(series, "style_log.json"), "w"), indent=1, ensure_ascii=False); print("recorded", ep)
