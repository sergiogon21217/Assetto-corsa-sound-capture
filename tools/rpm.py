"""Track engine rpm over time from audio alone.

A 4-cylinder 4-stroke fires twice per revolution, so the main engine tone is the 2nd
order: f2 = rpm / 30 Hz, with harmonics at multiples of f2. For each STFT frame every
candidate rpm gets a harmonic-sum score (energy at f2, 2*f2, ... minus energy halfway
between them, which stops the tracker locking onto half the real rpm). A Viterbi pass
then picks the smoothest high-scoring path, limited to a maximum rpm change per second.

CLI: python tools/rpm.py <file.wav> [--lo 600 --hi 7200]  -> CSV of time,rpm on stdout
"""
import argparse

import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d
from scipy.signal import savgol_filter

from audio import highpass, read_wav

FRAME = 4096          # ~85 ms at 48 kHz: short enough for fast pulls
NFFT = 16384          # zero-padded: ~3 Hz bins
HOP_S = 0.02          # 20 ms between frames
RPM_STEP = 5


def _spectra(x, sr):
    hop = int(sr * HOP_S)
    win = np.hanning(FRAME).astype(np.float32)
    n = 1 + max(0, (len(x) - FRAME) // hop)
    frames = np.lib.stride_tricks.sliding_window_view(x, FRAME)[::hop][:n] * win
    mag = np.abs(np.fft.rfft(frames, NFFT, axis=1)).astype(np.float32)
    t = (np.arange(n) * hop + FRAME / 2) / sr
    return t, mag, sr / NFFT


def _whiten(mag, df, mode):
    """Keep tonal peaks, drop the background. Negatives are clipped.

    mode "sweep": subtract each frequency's median over time. Road/wind noise and cabin
      resonances are roughly stationary per frequency, while the engine lines move.
    mode "steady": subtract a local floor across frequency (~25 Hz wide), because a
      steady engine tone is itself stationary and the time median would remove it.
    """
    lg = np.log(mag + 1e-9)
    if mode == "sweep":
        w = np.clip(lg - np.median(lg, axis=0, keepdims=True), 0, None)
        w = uniform_filter1d(w, size=3, axis=0)       # light smoothing over time
    else:
        w = np.clip(lg - uniform_filter1d(lg, size=max(3, int(25 / df)), axis=1), 0, None)
    return maximum_filter1d(w, size=3, axis=1)       # tolerate slight mistuning


def _sample(w, freqs, df):
    idx = freqs / df
    lo = np.clip(idx.astype(int), 0, w.shape[1] - 2)
    fr = (idx - lo)[None, :]
    return w[:, lo] * (1 - fr) + w[:, lo + 1] * fr


def salience(w, df, cands):
    f2 = cands / 30.0
    s = np.zeros((w.shape[0], len(cands)), np.float32)
    for h in range(1, 5):                      # f2..4*f2: the clearest lines in the cabin
        ok = h * f2 < 1200
        if not ok.any():
            break
        on = _sample(w, h * f2, df)
        off = _sample(w, (h - 0.5) * f2, df)
        s += np.where(ok, on - 0.3 * off, 0) / h ** 0.3
    s = (s - s.mean(axis=1, keepdims=True)) / (s.std(axis=1, keepdims=True) + 1e-9)
    return s


def viterbi(s, max_step, smooth=1.0, start=None, end=None):
    """Best path through score matrix s (frames x states); |state change| <= max_step."""
    n, m = s.shape
    offs = np.arange(-max_step, max_step + 1)
    cost = smooth * (offs / max(max_step, 1)) ** 2
    score = s[0].copy()
    if start is not None:
        score = score + start
    back = np.zeros((n, m), np.int16)
    for i in range(1, n):
        best = np.full(m, -np.inf)
        arg = np.zeros(m, np.int16)
        for o, c in zip(offs, cost):
            shifted = np.full(m, -np.inf)
            if o >= 0:
                shifted[o:] = score[:m - o] - c
            else:
                shifted[:o] = score[-o:] - c
            better = shifted > best
            best[better] = shifted[better]
            arg[better] = o
        score = best + s[i]
        back[i] = arg
    if end is not None:
        score = score + end
    path = np.zeros(n, int)
    path[-1] = int(np.argmax(score))
    for i in range(n - 1, 0, -1):
        path[i - 1] = path[i] - back[i, path[i]]
    return path


def track(x, sr, lo=600, hi=7200, max_rate=3000, start_hint=None, end_hint=None, mode="sweep"):
    """Return (times s, rpm, confidence z-score) for a mono or stereo signal.

    start_hint / end_hint: optional (lo, hi) rpm ranges the path should begin / end in.
    """
    if x.ndim == 2:
        x = x.mean(axis=1)
    x = highpass(x, sr, 20).astype(np.float32)
    t, mag, df = _spectra(x, sr)
    cands = np.arange(lo, hi + RPM_STEP, RPM_STEP, dtype=np.float64)
    s = salience(_whiten(mag, df, mode), df, cands)

    def prior(h):
        if h is None:
            return None
        return np.where((cands >= h[0]) & (cands <= h[1]), 0.0, -1e3)  # effectively hard

    step = max(1, int(round(max_rate * HOP_S / RPM_STEP)))
    path = viterbi(s, step, start=prior(start_hint), end=prior(end_hint))
    rpm = cands[path]
    conf = s[np.arange(len(path)), path]
    if len(rpm) >= 11:
        rpm = savgol_filter(rpm, 11, 2)
    return t, rpm, conf


def refine(x, sr, approx, span=0.06, harmonics=6):
    """Precise rpm of a (near-)steady segment: one long zero-padded FFT, harmonic sum
    over a fine candidate grid within +-span of approx. Resolution ~0.1 % for 1 s."""
    if x.ndim == 2:
        x = x.mean(axis=1)
    x = highpass(x, sr, 20)
    n = 1 << int(np.ceil(np.log2(len(x) * 8)))
    mag = np.abs(np.fft.rfft(x * np.hanning(len(x)), n))
    df = sr / n
    lg = np.log(mag + 1e-12)
    w = np.clip(lg - uniform_filter1d(lg, size=max(3, int(25 / df))), 0, None)
    cands = np.linspace(approx * (1 - span), approx * (1 + span), 2401)
    f2 = cands / 30
    score = np.zeros_like(cands)
    for h in range(1, harmonics + 1):
        score += np.interp(h * f2, np.arange(len(w)) * df, w) / h ** 0.3
    return float(cands[np.argmax(score)])


def local_track(x, sr, approx, win_s=1.0, hop_s=0.2, span=0.08):
    """Slow but precise rpm track for steady holds: refine() on sliding windows.

    The whole-file value (searched within +-span of approx) seeds each window, which may
    then move by up to 4 %.
    """
    centre = refine(x, sr, approx, span=span, harmonics=12)
    w, h = int(win_s * sr), int(hop_s * sr)
    t, r = [], []
    for a in range(0, len(x) - w + 1, h):
        t.append((a + w / 2) / sr)
        r.append(refine(x[a:a + w], sr, centre, span=0.04, harmonics=12))
    return np.array(t), np.array(r), centre


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("wav")
    ap.add_argument("--lo", type=float, default=600)
    ap.add_argument("--hi", type=float, default=7200)
    ap.add_argument("--steady", action="store_true", help="file holds a steady rpm")
    a = ap.parse_args()
    x, sr = read_wav(a.wav)
    t, rpm, conf = track(x, sr, a.lo, a.hi, mode="steady" if a.steady else "sweep")
    print("time_s,rpm,confidence")
    for ti, ri, ci in zip(t, rpm, conf):
        print(f"{ti:.3f},{ri:.0f},{ci:.2f}")


if __name__ == "__main__":
    main()
