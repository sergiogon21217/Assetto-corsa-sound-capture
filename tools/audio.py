"""Small WAV and signal helpers shared by the processing tools (numpy + scipy only)."""
import wave

import numpy as np
from scipy.signal import butter, resample_poly, sosfiltfilt


def read_wav(path):
    """Return (samples float64 in [-1, 1], shape (n, channels)), sample rate."""
    with wave.open(str(path)) as w:
        sr, ch, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if width == 2:
        x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    elif width == 3:
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(np.int32)
        v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        x = np.where(v >= 1 << 23, v - (1 << 24), v).astype(np.float64) / (1 << 23)
    else:
        raise ValueError(f"{path}: unsupported sample width {width}")
    return x.reshape(-1, ch), sr


def write_wav(path, x, sr):
    """Write float samples (n,) or (n, channels) as 16-bit PCM, clipping at full scale."""
    x = np.atleast_2d(np.asarray(x).T).T
    pcm = np.clip(np.round(x * 32767), -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def highpass(x, sr, hz=20.0):
    sos = butter(4, hz, "highpass", fs=sr, output="sos")
    return sosfiltfilt(sos, x, axis=0)


def oversample(x, factor=4):
    """Band-limited upsampling, so later linear interpolation is clean."""
    return resample_poly(x, factor, 1, axis=0)


def db(v):
    return 20 * np.log10(np.maximum(v, 1e-12))


def rms(x):
    return float(np.sqrt(np.mean(np.square(x))))
