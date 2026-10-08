"""Cut one-shot sounds (shifts, pops, crackle bursts, lift-off whoosh) from recordings.

Usage: python tools/oneshots.py processing/2026-10-08.json

Reads the "oneshots" list of the session config. Each entry has a file, an output
group (gear, backfire, turbo...) and a kind:
  segment     explicit cuts: "cuts": [[start_s, length_s], ...]
  bursts      the n busiest non-overlapping windows of length_s between from_s and to_s
  transients  the n strongest single transients (pops) between from_s and to_s
Writes <out_dir>/oneshots/<group>/<name>_<n>.wav and appends to oneshots.csv.
Peaks are capped at -1 dBFS; fades avoid clicks at the cut points.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, find_peaks, sosfiltfilt

from audio import db, highpass, read_wav, rms, write_wav

ROOT = Path(__file__).resolve().parent.parent
PEAK_CAP_DB = -1.0


def fade(x, sr, in_s, out_s):
    y = x.copy()
    a, b = max(1, int(in_s * sr)), max(1, int(out_s * sr))
    y[:a] *= np.linspace(0, 1, a)[:, None]
    y[-b:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, b)))[:, None]
    return y


def hf_envelope(x, sr, hz=1500, win_s=0.005):
    hp = sosfiltfilt(butter(4, hz, "highpass", fs=sr, output="sos"), x.mean(axis=1))
    w = max(1, int(win_s * sr))
    return np.sqrt(np.convolve(hp ** 2, np.ones(w) / w, "same"))


def cuts_segment(x, sr, e):
    return [(s, L) for s, L in e["cuts"]]


def cuts_bursts(x, sr, e):
    env = hf_envelope(x, sr, win_s=0.02)
    L, a, b = e["length_s"], e["from_s"], e["to_s"]
    starts = np.arange(a, b - L, 0.05)
    score = [env[int(s * sr):int((s + L) * sr)].mean() for s in starts]
    chosen = []
    for i in np.argsort(score)[::-1]:
        s = starts[i]
        if all(abs(s - c) >= L for c in chosen):
            chosen.append(s)
        if len(chosen) == e["n"]:
            break
    return [(s, L) for s in sorted(chosen)]


def cuts_transients(x, sr, e):
    env = hf_envelope(x, sr)
    a, b = int(e["from_s"] * sr), int(e["to_s"] * sr)
    pk, pr = find_peaks(env[a:b], distance=int(e.get("spacing_s", 0.25) * sr), prominence=0)
    top = pk[np.argsort(pr["prominences"])[::-1][:e["n"]]]
    pre, post = e.get("pre_s", 0.01), e.get("post_s", 0.15)
    return [((a + p) / sr - pre, pre + post) for p in sorted(top)]


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text())
    rec, out = ROOT / cfg["recordings_dir"], ROOT / cfg["out_dir"] / "oneshots"
    rows = []
    for e in cfg["oneshots"]:
        x, sr = read_wav(rec / e["file"])
        x = highpass(x, sr, 20)
        cuts = {"segment": cuts_segment, "bursts": cuts_bursts, "transients": cuts_transients}[e["kind"]](x, sr, e)
        (out / e["group"]).mkdir(parents=True, exist_ok=True)
        for n, (s, L) in enumerate(cuts, 1):
            seg = x[max(0, int(s * sr)):int((s + L) * sr)]
            seg = fade(seg, sr, e.get("fade_in_s", 0.005), e.get("fade_out_s", min(0.3, L / 3)))
            peak = db(np.abs(seg).max())
            if peak > PEAK_CAP_DB:
                seg = seg * 10 ** ((PEAK_CAP_DB - peak) / 20)
            name = f"{e['name']}_{n}.wav"
            write_wav(out / e["group"] / name, seg, sr)
            rows.append({"group": e["group"], "file": f"oneshots/{e['group']}/{name}",
                         "source": e["file"], "start_s": round(s, 3), "length_s": round(L, 3),
                         "peak_dbfs": round(db(np.abs(seg).max()), 1), "rms_dbfs": round(db(rms(seg)), 1),
                         "note": e.get("note", "")})
        print(f"{e['file']:16s} {e['kind']:10s} -> {len(cuts)} x {e['group']}/{e['name']}")
    with open(out / "oneshots.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
