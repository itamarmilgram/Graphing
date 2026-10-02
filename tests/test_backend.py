import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
from scipy.io import wavfile

from backend.analysis import analyze_audio
from backend.audio import load_audio
from backend.plotting import render_plot
from backend.project import default_project, load_project, save_project


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.rate = 8000
        t = np.arange(self.rate) / self.rate
        self.samples = np.column_stack([np.sin(2 * np.pi * 440 * t), np.sin(2 * np.pi * 880 * t)])
        self.project = default_project()
        self.project["analysis"]["nperseg"] = 512
        self.project["analysis"]["nfft"] = 512
        self.project["analysis"]["noverlap"] = 256

    def test_wav_loading_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tone.wav"
            wavfile.write(path, self.rate, (self.samples * 30000).astype(np.int16))
            audio, metadata = load_audio(path)
        self.assertEqual(audio.shape, self.samples.shape)
        self.assertEqual(metadata["channels"], 2)
        self.assertEqual(metadata["sample_rate"], self.rate)

    def test_fft_peak_and_parameter_validation(self):
        result = analyze_audio(self.samples, self.rate, self.project)
        self.assertAlmostEqual(result.summary["peak_frequency"], 437.5, delta=20)
        self.project["analysis"]["noverlap"] = 512
        with self.assertRaises(ValueError):
            analyze_audio(self.samples, self.rate, self.project)

    def test_other_analysis_modes_render(self):
        for kind in ("waveform", "psd", "welch", "spectrogram", "histogram", "scatter"):
            self.project["analysis_type"] = kind
            result = analyze_audio(self.samples, self.rate, self.project)
            image = render_plot(result, self.project, {"sample_rate": self.rate})
            self.assertTrue(image.startswith("data:image/png"))

    def test_project_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "project.json"
            save_project(self.project, path)
            with path.open("r", encoding="utf-8") as stream:
                loaded = load_project(stream)
        self.assertEqual(loaded["analysis"]["nfft"], 512)


if __name__ == "__main__":
    unittest.main()
