"""Render loops along an rpm path, to hear the bank without FMOD.

Usage: python tools/preview.py loops/2026-10-08 [recordings dir]

Uses the same crossfade and pitch rules as pitch_table.py. Writes into <loops>/previews/:
  part_sweep.wav        part-load layer, idle -> 6300 -> idle
  pull_and_coast.wav    ON layer pull 1500 -> 6500, then OFF layer coast 6500 -> 1000
  compare_3k_limit.wav  the real "3k limit" pull, then the ON layer following its rpm
  compare_limit_3k.wav  the real "limit 3k" coast-down, then the OFF layer following it
  compare_2_3_4_wot.wav the real 2-3-4 WOT upshifts, then ON loops following its rpm, with
                        the OFF loops blended in while rpm drops on each shift (no shift
                        one-shots yet)
"""
import csv
import sys
from pathlib import Path

import numpy as np

from audio import highpass, read_wav, write_wav
from pitch_table import layer_points
from rpm import track


def load_layer(d, layer):
    rows = sorted((float(r["rpm"]), r["file"]) for r in csv.DictReader(open(d / "manifest.csv"))
                  if r["layer"] == layer)
    loops = [read_wav(d / f)[0] for _, f in rows]
    return [r for r, _ in rows], loops


def render(rpms, loops, path_rpm, sr):
    """path_rpm: rpm per output sample."""
    out = np.zeros((len(path_rpm), loops[0].shape[1]))
    for loop_rpm, loop, pts in zip(rpms, loops, layer_points(rpms)):
        vol = np.interp(path_rpm, [p[0] for p in pts], [p[1] for p in pts])
        if vol.max() <= 0:
            continue
        pos = np.cumsum(path_rpm / loop_rpm) % len(loop)          # read position, wraps
        i0 = pos.astype(int)
        frac = (pos - i0)[:, None]
        out += (loop[i0] * (1 - frac) + loop[(i0 + 1) % len(loop)] * frac) * vol[:, None]
    return out


def ramp(sr, pts):
    """pts: [(seconds, rpm), ...] -> rpm per sample, geometric between points."""
    t = np.arange(int(pts[-1][0] * sr)) / sr
    return np.exp(np.interp(t, [p[0] for p in pts], np.log([p[1] for p in pts])))


def follow(x, sr, layer_rpms, loops, a_s, b_s, **hints):
    t, r, _ = track(x, sr, **hints)
    k = (t >= a_s) & (t <= b_s)
    ts = np.arange(int(a_s * sr), int(b_s * sr)) / sr
    path = np.interp(ts, t[k], r[k])
    real = x[int(a_s * sr):int(a_s * sr) + len(path)]
    synth = render(layer_rpms, loops, path, sr)
    gap = np.zeros((sr // 2, x.shape[1]))
    return np.concatenate([real, gap, synth])


def follow_shifts(x, sr, on, off, a_s, b_s, drop_rate=-3000, hold_s=0.08, **hints):
    """Like follow(), but throttle is 'off' wherever rpm falls faster than drop_rate rpm/s."""
    t, r, _ = track(x, sr, **hints)
    k = (t >= a_s) & (t <= b_s)
    ts = np.arange(int(a_s * sr), int(b_s * sr)) / sr
    path = np.interp(ts, t[k], r[k])
    drop = np.interp(ts, t[k], (np.gradient(r, t) < drop_rate)[k].astype(float)) > 0.5
    hold = int(hold_s * sr)                       # keep throttle off a moment after the drop
    idx = np.flatnonzero(drop)
    for i in idx:
        drop[i:i + hold] = True
    smooth = int(0.03 * sr)
    throttle = np.convolve(1 - drop.astype(float), np.ones(smooth) / smooth, mode="same")
    throttle = np.clip(throttle, 0, 1)[:, None]
    synth = render(*on, path, sr) * np.sqrt(throttle) + render(*off, path, sr) * np.sqrt(1 - throttle)
    real = x[int(a_s * sr):int(a_s * sr) + len(path)]
    return np.concatenate([real, np.zeros((sr // 2, x.shape[1])), synth])


def main():
    d = Path(sys.argv[1])
    rec = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    out = d / "previews"
    out.mkdir(exist_ok=True)
    sr = 48000
    part = load_layer(d, "part")
    on = load_layer(d, "on")
    off = load_layer(d, "off")
    write_wav(out / "part_sweep.wav", render(*part, ramp(sr, [(0, 900), (1, 900), (8, 6300), (9, 6300), (16, 900)]), sr), sr)
    pull = render(*on, ramp(sr, [(0, 1500), (5, 6500)]), sr)
    coast = render(*off, ramp(sr, [(0, 6500), (8, 1000)]), sr)
    write_wav(out / "pull_and_coast.wav", np.concatenate([pull, coast]), sr)
    if rec:
        x, _ = read_wav(rec / "3k limit.wav")
        write_wav(out / "compare_3k_limit.wav",
                  follow(highpass(x, sr), sr, *on, 1.3, 4.7, lo=2500, hi=7000, start_hint=(2700, 3300)), sr)
        x, _ = read_wav(rec / "limit 3k.wav")
        write_wav(out / "compare_limit_3k.wav",
                  follow(highpass(x, sr), sr, *off, 0.5, 14.5, lo=2500, hi=7000,
                         start_hint=(6200, 6900), end_hint=(2700, 3500)), sr)
        x, _ = read_wav(rec / "2 3 4 wot.wav")
        write_wav(out / "compare_2_3_4_wot.wav",
                  follow_shifts(highpass(x, sr), sr, on, off, 0.15, 6.6, lo=4000, hi=7000,
                                max_rate=12000), sr)
    print("previews ->", out)


if __name__ == "__main__":
    main()
