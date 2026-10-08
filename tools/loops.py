"""Turn recordings into seamless constant-rpm loops.

1. flatten(): resample a stretch of audio so the engine runs at exactly one rpm. Engine
   revolutions are integrated from the rpm track, and output samples are placed at equal
   revolution steps, so a sweep (or a slightly drifting hold) becomes a steady tone.
2. make_loop(): pick a loop length of whole engine cycles (1 cycle = 2 revolutions) by
   autocorrelation, then crossfade the end back into the start so the wrap is seamless.
"""
import numpy as np
from scipy.signal import butter, sosfiltfilt

from audio import oversample

OVERSAMPLE = 4


def flatten(x, sr, t_track, rpm_track, center_s, target_rpm, out_len):
    """Return out_len samples of x (n, ch) re-timed to a constant target_rpm.

    center_s: input time that maps to the middle of the output.
    """
    n = len(x)
    rpm_s = np.interp(np.arange(n) / sr, t_track, rpm_track)
    revs = np.concatenate([[0.0], np.cumsum(rpm_s / 60 / sr)])[:n]
    rev_c = np.interp(center_s * sr, np.arange(n), revs)
    rev_out = rev_c + (np.arange(out_len) - out_len / 2) * target_rpm / 60 / sr
    if rev_out[0] < revs[0] or rev_out[-1] > revs[-1]:
        raise ValueError("slice runs past the ends of the recording")
    idx = np.interp(rev_out, revs, np.arange(n)) * OVERSAMPLE
    xo = oversample(x, OVERSAMPLE)
    pos = np.arange(len(xo))
    return np.stack([np.interp(idx, pos, xo[:, c]) for c in range(x.shape[1])], axis=1)


def input_span(sr, t_track, rpm_track, center_s, target_rpm, out_len):
    """Input time range (s) that flatten() would read, for checking track confidence."""
    t = np.arange(0, t_track[-1], 1 / 200)
    revs = np.concatenate([[0.0], np.cumsum(np.interp(t, t_track, rpm_track) / 60 / 200)])[:len(t)]
    rc = np.interp(center_s, t, revs)
    half = out_len / 2 * target_rpm / 60 / sr
    return float(np.interp(rc - half, revs, t)), float(np.interp(rc + half, revs, t))


def _xcorr_at(m, lag, w):
    a, b = m[:w], m[lag:lag + w]
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def make_loop(seg, sr, rpm, min_len_s=1.0, xfade_s=0.06):
    """Cut a seamless loop from seg (n, ch) whose engine runs at ~rpm.

    Returns (loop, info) where info has the cycle count, exact rpm implied by the loop
    length, and the correlation at the loop point (1.0 = perfect repeat).
    """
    cycle = 120 / rpm * sr                                # samples per firing cycle
    cycles = int(np.ceil(min_len_s * sr / cycle))
    x = int(xfade_s * sr)
    # judge the loop point on the engine band only, so road/wind hiss doesn't decide it
    m = sosfiltfilt(butter(4, [30, 1500], "bandpass", fs=sr, output="sos"), seg.mean(axis=1))
    l0 = cycles * cycle
    w = min(len(m) - int(l0 * 1.004) - 1, int(0.25 * sr))
    if w < x:
        raise ValueError("segment too short for this loop length")
    lags = np.arange(int(l0 * 0.996), int(l0 * 1.004) + 1)
    corr = np.array([_xcorr_at(m, lag, w) for lag in lags])
    L = int(lags[np.argmax(corr)])
    if len(seg) < L + x:
        raise ValueError("segment too short for loop plus crossfade")
    fade = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, x))[:, None]   # 0 -> 1
    loop = seg[:L].copy()
    loop[:x] = seg[L:L + x] * (1 - fade) + seg[:x] * fade
    info = {"cycles": cycles, "length_s": L / sr, "rpm": cycles * 120 * sr / L,
            "loop_corr": float(corr.max())}
    return loop, info
