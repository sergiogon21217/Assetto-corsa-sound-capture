"""Build the engine loop set for one recording session.

Usage: python tools/build_loops.py processing/2026-10-08.json

The config lists each source file with its kind:
  steady   a constant-rpm hold        -> one loop at its measured rpm
  sweep    a WOT pull or a coast-down -> one loop per grid rpm it passes through
  free     the limiter                -> one loop of the bounce, no rpm alignment
Loops go to <out_dir>/<layer>/<layer>_<rpm>.wav, with manifest.csv describing them.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter1d

from audio import db, highpass, read_wav, rms, write_wav
from loops import flatten, input_span, make_loop
from rpm import HOP_S, local_track, track

ROOT = Path(__file__).resolve().parent.parent


def steady_loop(x, sr, src):
    t, r, centre = local_track(x, sr, src["approx"])
    win = 1.6                                       # loop 1 s + crossfade + margin
    m = x.mean(axis=1)
    best = None
    for c in np.arange(win / 2 + 0.3, len(x) / sr - win / 2 - 0.3, 0.1):
        k = (t > c - win / 2) & (t < c + win / 2)
        if k.sum() < 3:
            continue
        a, b = int((c - win / 2) * sr), int((c + win / 2) * sr)
        env = [db(rms(m[i:i + sr // 10])) for i in range(a, b - sr // 10, sr // 10)]
        score = np.std(r[k]) / np.mean(r[k]) * 100 + np.std(env) / 3
        if best is None or score < best[0]:
            best = (score, c)
    c = best[1]
    target = float(np.interp(c, t, r))
    seg = flatten(x, sr, t, r, c, target, int(1.3 * sr))
    loop, info = make_loop(seg, sr, target, min_len_s=1.0)
    info["source_time_s"] = round(c, 2)
    return [(loop, info)]


def sweep_loops(x, sr, src, grid, conf_min=0.8, loop_s=0.4):
    t, r, c = track(x, sr, *src["range"], start_hint=src.get("start_hint"),
                    end_hint=src.get("end_hint"))
    cs = uniform_filter1d(c, int(0.3 / HOP_S))
    slope = np.gradient(r, t)
    direction = 1 if src["layer"] == "on" else -1
    out = []
    for g in grid:
        cross = np.where(np.diff(np.sign(r - g)) != 0)[0]
        cross = [i for i in cross if direction * slope[i] > 150 and cs[i] > conf_min]
        if not cross:
            continue
        i = max(cross, key=lambda j: cs[j])
        tc = float(np.interp(g, [r[i], r[i + 1]], [t[i], t[i + 1]]) if r[i] != r[i + 1] else t[i])
        need = int((loop_s * 1.15 + 0.1) * sr)
        try:
            a, b = input_span(sr, t, r, tc, g, need)
            k = (t >= a) & (t <= b)
            if a < t[0] or b > t[-1] or not k.any() or cs[k].min() < conf_min * 0.6:
                continue
            seg = flatten(x, sr, t, r, tc, g, need)
            loop, info = make_loop(seg, sr, g, min_len_s=loop_s, xfade_s=0.04)
        except ValueError:
            continue
        info["source_time_s"] = round(tc, 2)
        out.append((loop, info))
    return out


def free_loop(x, sr, src, length_s=1.5, xfade_s=0.15):
    a = int(src.get("start_s", 0.3) * sr)
    seg = x[a:]
    m = seg.mean(axis=1)
    w, xf = int(0.3 * sr), int(xfade_s * sr)
    lags = np.arange(int(length_s * 0.8 * sr), int(length_s * 1.2 * sr), 16)
    lags = lags[lags + max(w, xf) < len(m)]
    corr = [np.dot(m[:w], m[l:l + w]) / (np.linalg.norm(m[:w]) * np.linalg.norm(m[l:l + w]) + 1e-12)
            for l in lags]
    L = int(lags[int(np.argmax(corr))])
    fade = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, xf))[:, None]
    loop = seg[:L].copy()
    loop[:xf] = seg[L:L + xf] * (1 - fade) + seg[:xf] * fade
    return [(loop, {"cycles": "", "length_s": L / sr, "rpm": src.get("rpm", ""),
                    "loop_corr": float(max(corr)), "source_time_s": src.get("start_s", 0.3)})]


def smooth_levels(entries, max_db=6.0):
    """Nudge loops of one layer onto a smooth loudness-vs-rpm curve, so crossfades between
    loops cut from different takes don't pump. Idle is left as recorded. Returns gains (dB)."""
    rpm = np.array([e[1]["rpm"] for e in entries], float)
    lvl = np.array([db(rms(e[0])) for e in entries])
    fit_on = np.array([e[2]["file"] != "idle n.wav" and "idle" not in e[2]["file"] for e in entries])
    gains = np.zeros(len(entries))
    if fit_on.sum() >= 4:
        coef = np.polyfit(np.log(rpm[fit_on]), lvl[fit_on], 2)
        gains[fit_on] = np.clip(np.polyval(coef, np.log(rpm[fit_on])) - lvl[fit_on], -max_db, max_db)
    return gains


def main():
    cfg_path = Path(sys.argv[1])
    cfg = json.loads(cfg_path.read_text())
    rec = ROOT / cfg["recordings_dir"]
    out = ROOT / cfg["out_dir"]
    rows = []
    best = {}                                       # (layer, grid rpm) -> best loop so far
    for src in cfg["sources"]:
        x, sr = read_wav(rec / src["file"])
        x = highpass(x, sr, 20)
        kind = src["kind"]
        made = {"steady": lambda: steady_loop(x, sr, src),
                "sweep": lambda: sweep_loops(x, sr, src, cfg["grid"]),
                "free": lambda: free_loop(x, sr, src)}[kind]()
        print(f"{src['file']:18s} {kind:6s} -> {len(made)} loop(s)")
        for loop, info in made:
            key = (src["layer"], round(info["rpm"]) if kind != "sweep" else
                   min(cfg["grid"], key=lambda g: abs(g - info["rpm"])))
            if key in best and best[key][1]["loop_corr"] >= info["loop_corr"]:
                continue
            best[key] = (loop, info, src, sr)
    ordered = sorted(best.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    gain = {}
    for layer in {k[0] for k, _ in ordered}:
        if layer == "limiter":
            continue
        keys = [k for k, _ in ordered if k[0] == layer]
        for k, g in zip(keys, smooth_levels([best[k] for k in keys])):
            gain[k] = g
    for key, (loop, info, src, sr) in ordered:
        layer = key[0]
        rpm = info["rpm"]
        g = gain.get(key, 0.0)
        loop = loop * 10 ** (g / 20)
        name = f"{layer}_{'limiter' if src['kind'] == 'free' else round(rpm)}.wav"
        (out / layer).mkdir(parents=True, exist_ok=True)
        write_wav(out / layer / name, loop, sr)
        rows.append({"layer": layer, "file": f"{layer}/{name}",
                     "rpm": round(rpm, 1) if rpm != "" else "", "length_s": round(info["length_s"], 3),
                     "cycles": info["cycles"], "loop_corr": round(info["loop_corr"], 3),
                     "gain_db": round(g, 1), "rms_dbfs": round(db(rms(loop)), 1), "source": src["file"],
                     "source_time_s": info["source_time_s"]})
    with open(out / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} loops -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
