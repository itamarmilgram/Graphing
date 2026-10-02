# Oscilla

Oscilla is a local scientific plotting workbench for WAV files and measurement data. Python performs the audio analysis and Matplotlib produces the exported figure; the browser provides the control surface.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:8765>. Documentation is available at `/guide`.

## Project structure

```text
app.py                  Flask routes and in-memory local session
backend/audio.py        WAV loading and metadata
backend/analysis.py     NumPy/SciPy signal analysis
backend/plotting.py     Matplotlib figure construction
backend/export.py       PNG/SVG/PDF/JPEG/TIFF export
backend/project.py      JSON project state
templates/              HTML pages
static/css/style.css    UI styling
static/js/app.js        Controls, API calls, project interactions
tests/                  Backend tests
```

## Supported analyses and export

Waveform, FFT, PSD, Welch PSD, spectrogram, histogram, and scatter are available. Exports use the actual Matplotlib figure and support PNG, SVG, PDF, JPEG, and TIFF with configurable DPI, transparency, and tight bounding boxes.

## Adding an analysis

Add a branch to `backend/analysis.py` that returns an `AnalysisResult`, add its button in `templates/index.html`, and extend `backend/plotting.py` only when the rendering needs a new primitive such as an image or filled region. Keep file loading, computation, rendering, and export in their existing modules.

## Testing

```bash
python -m unittest discover -s tests -v
```
