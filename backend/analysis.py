from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import signal


@dataclass
class AnalysisResult:
    kind: str
    x: np.ndarray
    y: np.ndarray
    summary: dict[str, Any]
    xlabel: str
    ylabel: str
    extent: tuple[float, float, float, float] | None = None


def _settings(project: dict[str, Any]) -> dict[str, Any]:
    return project.get("analysis", {})


def _window(settings: dict[str, Any]) -> Any:
    value = settings.get("window", "hann")
    if value == "kaiser":
        return ("kaiser", float(settings.get("window_parameter", 14)))
    return value


def _segment(settings: dict[str, Any], length: int) -> tuple[int, int, int]:
    nfft = int(settings.get("nfft", 2048))
    nperseg = min(int(settings.get("nperseg", 2048)), length)
    noverlap = int(settings.get("noverlap", nperseg // 2))
    if nperseg < 2:
        raise ValueError("nperseg must be at least 2.")
    if noverlap < 0 or noverlap >= nperseg:
        raise ValueError("noverlap must be between 0 and nperseg - 1.")
    if nfft < nperseg:
        raise ValueError("nfft must be greater than or equal to nperseg.")
    return nfft, nperseg, noverlap


def analyze_audio(audio: np.ndarray, sample_rate: int, project: dict[str, Any]) -> AnalysisResult:
    settings = _settings(project)
    channel = int(settings.get("channel", 0))
    if channel < 0 or channel >= audio.shape[1]:
        raise ValueError("Selected channel is not available in this file.")
    values = audio[:, channel]
    start = max(0, int(float(settings.get("start_time", 0)) * sample_rate))
    requested_end = float(settings.get("end_time", 0))
    stop = min(len(values), int((requested_end if requested_end > 0 else len(values) / sample_rate) * sample_rate))
    if stop <= start:
        raise ValueError("The selected time region is empty.")
    values = values[start:stop]
    kind = project.get("analysis_type", "fft")
    nfft, nperseg, noverlap = _segment(settings, len(values))
    window = _window(settings)
    detrend = settings.get("detrend", "constant") or False
    if detrend == "false":
        detrend = False
    scaling = settings.get("scaling", "density")
    one_sided = bool(settings.get("return_onesided", True))
    if kind == "waveform":
        x = np.arange(len(values)) / sample_rate + start / sample_rate
        return AnalysisResult(kind, x, values, {"points": len(values)}, "Time (s)", "Amplitude")
    if kind == "fft":
        spectrum = np.fft.rfft(values[:nperseg] * signal.get_window(window, nperseg), n=nfft) if one_sided else np.fft.fft(values[:nperseg] * signal.get_window(window, nperseg), n=nfft)
        x = np.fft.rfftfreq(nfft, 1 / sample_rate) if one_sided else np.fft.fftfreq(nfft, 1 / sample_rate)
        y = np.abs(spectrum) / max(nperseg, 1)
        if settings.get("amplitude", "magnitude") == "power":
            y = y**2
        if settings.get("db", False):
            y = 10 * np.log10(np.maximum(y, 1e-15)) if settings.get("amplitude") == "power" else 20 * np.log10(np.maximum(y, 1e-15))
        return AnalysisResult(kind, x, y, {"peak_frequency": float(x[np.argmax(y)]), "resolution": float(sample_rate / nfft)}, "Frequency (Hz)", "dB" if settings.get("db") else "Magnitude")
    if kind in {"psd", "welch"}:
        x, y = signal.welch(values, fs=sample_rate, window=window, nperseg=nperseg, noverlap=noverlap, nfft=nfft, detrend=detrend, return_onesided=one_sided, scaling=scaling)
        if settings.get("db", False):
            y = 10 * np.log10(np.maximum(y, 1e-15))
        return AnalysisResult(kind, x, y, {"peak_frequency": float(x[np.argmax(y)])}, "Frequency (Hz)", "dB/Hz" if settings.get("db") else "Power spectral density")
    if kind == "spectrogram":
        x, times, z = signal.spectrogram(values, fs=sample_rate, window=window, nperseg=nperseg, noverlap=noverlap, nfft=nfft, detrend=detrend, return_onesided=one_sided, scaling=scaling, mode="magnitude")
        if settings.get("db", False):
            z = 20 * np.log10(np.maximum(z, 1e-15))
        return AnalysisResult(kind, times, z, {"frequency_bins": len(x), "time_bins": len(times)}, "Time (s)", "Frequency (Hz)", (float(times.min()), float(times.max()), float(x.min()), float(x.max())))
    if kind == "histogram":
        y, edges = np.histogram(values, bins=int(settings.get("bins", 50)))
        return AnalysisResult(kind, (edges[:-1] + edges[1:]) / 2, y, {"bins": len(y)}, "Amplitude", "Count")
    if kind == "scatter":
        x = np.arange(len(values)) / sample_rate + start / sample_rate
        return AnalysisResult(kind, x, values, {"points": len(values)}, "Time (s)", "Amplitude")
    raise ValueError(f"Unsupported analysis type: {kind}")
