from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from scipy.io import wavfile


def load_audio(path: str | Path) -> tuple[np.ndarray, dict[str, Any]]:
    """Load common WAV PCM/float formats and return float32 channels-first data."""
    rate, raw = wavfile.read(path)
    raw = np.asarray(raw)
    if raw.ndim == 1:
        raw = raw[:, None]
    info = np.iinfo(raw.dtype) if np.issubdtype(raw.dtype, np.integer) else None
    if info:
        peak = max(abs(info.min), info.max)
        audio = raw.astype(np.float64) / peak
        bits = raw.dtype.itemsize * 8
    else:
        audio = raw.astype(np.float64)
        bits = raw.dtype.itemsize * 8
    metadata = audio_metadata(audio, int(rate), bits)
    return audio, metadata


def audio_metadata(audio: np.ndarray, sample_rate: int, bit_depth: int | None = None) -> dict[str, Any]:
    return {
        "sample_rate": sample_rate,
        "channels": int(audio.shape[1]),
        "duration": float(audio.shape[0] / sample_rate),
        "samples": int(audio.shape[0]),
        "bit_depth": bit_depth,
    }
