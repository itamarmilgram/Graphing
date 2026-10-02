"""Oscilla local scientific plotting application."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file

from backend.analysis import analyze_audio
from backend.audio import audio_metadata, load_audio
from backend.export import export_figure
from backend.plotting import render_plot
from backend.defaults import DEFAULTS, default_project
from backend.project import load_project, save_project

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024 * 1024
STATE: dict[str, Any] = {"audio": None, "metadata": None, "filename": None, "project": default_project()}


def error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/guide")
def guide():
    return render_template("guide.html")


@app.get("/api/defaults")
def defaults():
    return jsonify(DEFAULTS)


@app.post("/api/load")
def load_file():
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return error("Choose a WAV or other supported audio file first.")
    suffix = Path(uploaded.filename).suffix or ".wav"
    temporary = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        uploaded.save(temporary.name)
        audio, metadata = load_audio(temporary.name)
    except Exception as exc:  # library errors should become UI messages
        return error(f"Could not read this audio file: {exc}")
    finally:
        temporary.close()
        os.unlink(temporary.name)
    STATE.update(audio=audio, metadata=metadata, filename=uploaded.filename)
    STATE["project"] = default_project()
    STATE["project"]["file_name"] = uploaded.filename
    return jsonify({"metadata": metadata})


@app.post("/api/render")
def render():
    if STATE["audio"] is None:
        return error("Load an audio file before plotting.")
    try:
        project = request.get_json(force=True) or default_project()
        analysis = analyze_audio(STATE["audio"], STATE["metadata"]["sample_rate"], project)
        image = render_plot(analysis, project, STATE["metadata"])
        if analysis.kind != "spectrogram":
            analysis.summary.setdefault("xlim", [float(analysis.x.min()), float(analysis.x.max())])
            analysis.summary.setdefault("ylim", [float(analysis.y.min()), float(analysis.y.max())])
        STATE["project"] = project
        return jsonify({"image": image, "analysis": analysis.summary, "project": project})
    except ValueError as exc:
        return error(str(exc))
    except Exception as exc:
        app.logger.exception("render failed")
        return error(f"Plot could not be generated: {exc}", 500)


@app.post("/api/export")
def export():
    if STATE["audio"] is None:
        return error("Load an audio file before exporting.")
    payload = request.get_json(force=True) or default_project()
    try:
        analysis = analyze_audio(STATE["audio"], STATE["metadata"]["sample_rate"], payload)
        figure = render_plot(analysis, payload, STATE["metadata"], return_figure=True)
        suffix = str(payload.get("export", {}).get("format", "png")).lower()
        if suffix not in {"png", "svg", "pdf", "jpg", "jpeg", "tif", "tiff"}:
            raise ValueError("Unsupported export format.")
        output = export_figure(figure, suffix, payload.get("export", {}))
        return send_file(output, as_attachment=True, download_name=f"oscilla-plot.{suffix}", mimetype="application/octet-stream")
    except ValueError as exc:
        return error(str(exc))


@app.post("/api/project/save")
def project_save():
    payload = request.get_json(force=True) or STATE["project"]
    target = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    target.close()
    save_project(payload, target.name)
    return send_file(target.name, as_attachment=True, download_name="oscilla-project.json", mimetype="application/json")


@app.post("/api/project/load")
def project_load():
    uploaded = request.files.get("file")
    if not uploaded:
        return error("Choose an Oscilla project JSON file.")
    try:
        return jsonify({"project": load_project(uploaded.stream)})
    except (ValueError, json.JSONDecodeError) as exc:
        return error(f"Invalid project file: {exc}")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8765, debug=False)
