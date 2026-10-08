"""Stage the processed audio for the FMOD project and list where every instrument goes.

Usage: python tools/stage_fmod.py processing/2026-10-08.json

Copies int/ and ext/ audio into fmod/Assets/<car>/<event>/... with flat, descriptive
names, and writes fmod/instruments.csv: for each FMOD instrument, the event, track, file,
and its placement on the `rpms` parameter sheet (start, full volume, end, autopitch root).

Engine events get three tracks crossfaded by `throttle`: off (coast-down loops, with
idle at the bottom so idle at 0 throttle works), part (steady holds) and on (WOT slices).
"""
import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RPMS_MAX = 14000            # AC's rpms parameter range: about twice the redline


def placements(rpms):
    """(start, full, end) per loop: fade in from the previous loop's rpm, out to the next."""
    out = []
    for i, r in enumerate(rpms):
        start = rpms[i - 1] if i > 0 else 0
        end = rpms[i + 1] if i + 1 < len(rpms) else RPMS_MAX
        out.append((start, r, end))
    return out


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text())
    car = cfg.get("car_folder", "kona_n")
    src = ROOT / cfg["out_dir"]
    dst = ROOT / "fmod" / "Assets" / car
    if dst.exists():
        shutil.rmtree(dst)
    rows = []
    manifest = list(csv.DictReader(open(src / "manifest.csv")))
    idle = next(r for r in manifest if r["source"] in cfg.get("idle_sources", ["idle n.wav"]))

    for side in ("int", "ext"):
        event = f"engine_{side}"
        for track in ("off", "part", "on"):
            items = [r for r in manifest if r["layer"] == track]
            if track == "off" and idle not in items:
                items = [idle] + items
            items.sort(key=lambda r: float(r["rpm"]))
            for (start, full, end), r in zip(placements([float(r["rpm"]) for r in items]), items):
                name = f"{track}_{round(float(r['rpm'])):04d}.wav"
                (dst / event / track).mkdir(parents=True, exist_ok=True)
                shutil.copy(src / side / r["file"], dst / event / track / name)
                rows.append({"event": event, "track": track, "file": f"{event}/{track}/{name}",
                             "kind": "loop", "rpms_start": round(start), "rpms_full": round(float(r["rpm"])),
                             "rpms_end": round(end), "autopitch_root": round(float(r["rpm"]), 1)})
        lim = next(r for r in manifest if r["layer"] == "limiter")
        (dst / "limiter").mkdir(parents=True, exist_ok=True)
        if side == "ext":                     # AC has one limiter event; use the exterior version
            shutil.copy(src / side / lim["file"], dst / "limiter" / "limiter_loop.wav")
            rows.append({"event": "limiter", "track": "main", "file": "limiter/limiter_loop.wav",
                         "kind": "loop", "rpms_start": "", "rpms_full": "", "rpms_end": "",
                         "autopitch_root": ""})
        for group, event in (("gear", f"gear_{side}"), ("backfire", f"backfire_{side}")):
            for f in sorted((src / side / "oneshots" / group).glob("*.wav")):
                (dst / event).mkdir(parents=True, exist_ok=True)
                shutil.copy(f, dst / event / f.name)
                rows.append({"event": event, "track": "multi", "file": f"{event}/{f.name}",
                             "kind": "one-shot (multi instrument, random)", "rpms_start": "",
                             "rpms_full": "", "rpms_end": "", "autopitch_root": ""})
    for f in sorted((src / "ext" / "oneshots" / "turbo").glob("*.wav")):
        (dst / "turbo").mkdir(parents=True, exist_ok=True)
        shutil.copy(f, dst / "turbo" / f"bov_{f.name}")
        rows.append({"event": "turbo", "track": "bov", "file": f"turbo/bov_{f.name}",
                     "kind": "one-shot on bov", "rpms_start": "", "rpms_full": "", "rpms_end": "",
                     "autopitch_root": ""})
    with open(ROOT / "fmod" / "instruments.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} instruments staged -> fmod/Assets/{car}, fmod/instruments.csv")


if __name__ == "__main__":
    main()
