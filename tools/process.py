"""Make the interior (int) and exterior (ext) versions of the loops and one-shots.

Usage: python tools/process.py processing/2026-10-08.json

int: gentle noise reduction (loops only). A road/wind floor is taken from the session's
     noise take, smoothed across frequency so the engine harmonics in it don't notch the
     loops, then subtracted softly (at most -6 dB per bin).
ext: int, then EQ that moves a cabin recording towards an outside one:
     high-pass 40 Hz, cuts on the cabin's own resonances (peaks at the same frequency in
     every loop whatever the rpm, found automatically in 50-250 Hz), a presence lift
     around 2.5 kHz and a small high shelf. Reverb is left to FMOD.
Loops are processed as three copies end to end and the middle one is kept, so filters
and noise reduction wrap around and the loop point stays seamless.
Writes <out_dir>/int/... and <out_dir>/ext/... mirroring the layer/one-shot folders, plus
process.json describing the EQ that was applied.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks, istft, sosfilt, stft, welch

from audio import highpass, read_wav, write_wav

ROOT = Path(__file__).resolve().parent.parent
NPERSEG = 2048


# --- biquads (RBJ audio EQ cookbook) ---------------------------------------------------
def _peaking(f0, gain_db, q, sr):
    a = 10 ** (gain_db / 40)
    w = 2 * np.pi * f0 / sr
    al = np.sin(w) / (2 * q)
    b = [1 + al * a, -2 * np.cos(w), 1 - al * a]
    d = [1 + al / a, -2 * np.cos(w), 1 - al / a]
    return np.array(b + d) / d[0]


def _highshelf(f0, gain_db, sr, s=1.0):
    a = 10 ** (gain_db / 40)
    w = 2 * np.pi * f0 / sr
    al = np.sin(w) / 2 * np.sqrt((a + 1 / a) * (1 / s - 1) + 2)
    c = np.cos(w)
    b = [a * ((a + 1) + (a - 1) * c + 2 * np.sqrt(a) * al), -2 * a * ((a - 1) + (a + 1) * c),
         a * ((a + 1) + (a - 1) * c - 2 * np.sqrt(a) * al)]
    d = [(a + 1) - (a - 1) * c + 2 * np.sqrt(a) * al, 2 * ((a - 1) - (a + 1) * c),
         (a + 1) - (a - 1) * c - 2 * np.sqrt(a) * al]
    return np.array(b + d) / d[0]


# --- analysis ----------------------------------------------------------------------------
def noise_floor(x, sr):
    """Road/wind floor per STFT bin: median over time, smoothed ~1/3 octave across frequency."""
    f, _, Z = stft(x.mean(axis=1), sr, nperseg=NPERSEG)
    mag = np.median(np.abs(Z), axis=1)
    lg = np.log(mag + 1e-12)
    out = np.empty_like(lg)
    for i, fi in enumerate(f):                     # constant-Q smoothing removes harmonic peaks
        half = max(1, int(fi * 0.12 / (f[1] - f[0])))
        out[i] = np.median(lg[max(0, i - half):i + half + 1])
    return np.exp(out)


def cabin_resonances(loops, sr, lo=50, hi=250, max_n=3, min_prom_db=3.0):
    """Peaks that sit at the same frequency in most loops: the cabin, not the engine."""
    specs = []
    for x in loops:
        f, p = welch(np.tile(x.mean(axis=1), 3), sr, nperseg=sr // 2)
        specs.append(10 * np.log10(p + 1e-14))
    med = np.median(specs, axis=0)
    k = (f >= lo) & (f <= hi)
    rel = med[k] - uniform_filter1d(med[k], 41)
    pk, pr = find_peaks(rel, prominence=min_prom_db, distance=8)
    top = pk[np.argsort(pr["prominences"])[::-1][:max_n]]
    return [(float(f[k][i]), float(pr["prominences"][list(pk).index(i)])) for i in sorted(top)]


# --- processing ---------------------------------------------------------------------------
def denoise(x, sr, floor, max_cut_db=6.0, over=1.0, scale=0.7):
    """Soft spectral subtraction. The floor is scaled down per signal so it never claims
    more noise than the signal has in 300-3000 Hz, where road/wind noise dominates."""
    out = np.zeros_like(x)
    g_min = 10 ** (-max_cut_db / 20)
    f = np.fft.rfftfreq(NPERSEG, 1 / sr)
    band = (f > 300) & (f < 3000)
    for c in range(x.shape[1]):
        _, _, Z = stft(x[:, c], sr, nperseg=NPERSEG)
        mag = np.abs(Z)
        k = scale * min(1.0, float(np.median(np.median(mag, axis=1)[band] / floor[band])))
        fl = floor * k
        g = np.clip(1 - over * fl[:, None] / (mag + 1e-12), g_min, 1)
        g = uniform_filter1d(g, 3, axis=1)          # smooth over time: fewer artefacts
        _, y = istft(Z * g, sr, nperseg=NPERSEG)
        out[:, c] = y[:len(x)]
    return out


def ext_chain(sr, resonances, presence_db=3.0, shelf_db=2.0, cut_db=4.0):
    secs = [_peaking(f0, -cut_db, 4.0, sr) for f0, _ in resonances]
    secs.append(_peaking(2500, presence_db, 0.8, sr))
    secs.append(_highshelf(6000, shelf_db, sr))
    return np.array(secs)


def apply_looped(fn, x, xfade_s=0.03, sr=48000):
    """Run fn on three copies end to end and keep the middle, then re-crossfade the loop
    point with the third copy (its natural continuation), so the wrap stays seamless even
    when fn is not exactly periodic (e.g. STFT frames that don't line up with the loop)."""
    n = len(x)
    y = fn(np.concatenate([x, x, x]))
    loop = y[n:2 * n].copy()
    k = min(int(xfade_s * sr), n // 4)
    fade = (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, k)))[:, None]
    loop[:k] = y[2 * n:2 * n + k] * (1 - fade) + y[n:n + k] * fade
    return loop


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text())
    d = ROOT / cfg["out_dir"]
    rec = ROOT / cfg["recordings_dir"]
    nx, sr = read_wav(rec / cfg["noise_profile"])
    floor = noise_floor(highpass(nx, sr, 20), sr)

    loop_rows = [r for r in csv.DictReader(open(d / "manifest.csv"))]
    loops = {r["file"]: read_wav(d / r["file"])[0] for r in loop_rows}
    res = cabin_resonances([v for k, v in loops.items() if not k.startswith("limiter")], sr)
    sos = ext_chain(sr, res)

    skip = {r["file"] for r in loop_rows if r["source"] in cfg.get("no_denoise", [])}
    for f, x in loops.items():
        xi = x if f in skip else apply_looped(lambda y: denoise(y, sr, floor), x)
        xe = apply_looped(lambda y: sosfilt(sos, highpass(y, sr, 40), axis=0), xi)
        for kind, y in (("int", xi), ("ext", xe)):
            p = d / kind / f
            p.parent.mkdir(parents=True, exist_ok=True)
            write_wav(p, np.clip(y, -1, 1), sr)

    for kind in ("int", "ext"):                     # so preview.py / pitch_table.py work on them
        with open(d / kind / "manifest.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(loop_rows[0]))
            w.writeheader()
            w.writerows(loop_rows)

    shots = d / "oneshots" / "oneshots.csv"
    for r in (csv.DictReader(open(shots)) if shots.exists() else []):
        x, _ = read_wav(d / r["file"])
        rel = Path(r["file"]).relative_to("oneshots")
        xe = sosfilt(sos, highpass(np.concatenate([x, np.zeros((sr // 10, x.shape[1]))]), sr, 40), axis=0)[:len(x)]
        for kind, y in (("int", x), ("ext", xe)):
            p = d / kind / "oneshots" / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            write_wav(p, np.clip(y, -1, 1), sr)

    info = {"noise_profile": cfg["noise_profile"], "denoise_max_cut_db": 6,
            "not_denoised": sorted(skip),
            "cabin_resonance_cuts": [{"hz": round(f0, 1), "prominence_db": round(p, 1), "cut_db": -4, "q": 4}
                                     for f0, p in res],
            "presence": {"hz": 2500, "db": 3, "q": 0.8}, "high_shelf": {"hz": 6000, "db": 2},
            "highpass_hz": 40}
    (d / "process.json").write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
