from __future__ import annotations

import base64
from io import BytesIO
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .analysis import AnalysisResult


def _color(value: str, fallback: str) -> str:
    return value if isinstance(value, str) and value else fallback


def render_plot(result: AnalysisResult, project: dict[str, Any], metadata: dict[str, Any], return_figure: bool = False):
    figure_settings = project.get("figure", {})
    axes_settings = project.get("axes", {})
    line = project.get("line", {})
    labels = project.get("labels", {})
    legend = project.get("legend", {})
    fig, ax = plt.subplots(figsize=tuple(figure_settings.get("size", [10, 5.8])), dpi=int(figure_settings.get("dpi", 130)))
    fig.patch.set_facecolor(_color(figure_settings.get("background"), "white"))
    ax.set_facecolor(_color(axes_settings.get("background"), "white"))
    if result.kind == "spectrogram":
        mesh = ax.imshow(result.y, extent=result.extent, aspect="auto", origin="lower", cmap=project.get("colorbar", {}).get("cmap", "viridis"))
        fig.colorbar(mesh, ax=ax, label=project.get("colorbar", {}).get("label", "Magnitude"))
    else:
        style = {"color": _color(line.get("color"), "#197c78"), "linewidth": float(line.get("width", 1.8)), "linestyle": line.get("style", "-"), "alpha": float(line.get("alpha", .9))}
        if result.kind == "scatter":
            ax.scatter(result.x[::max(1, len(result.x) // 10000)], result.y[::max(1, len(result.y) // 10000)], s=float(line.get("marker_size", 9)), c=style["color"], alpha=float(line.get("alpha", .8)))
        else:
            ax.plot(result.x, result.y, **style, marker=line.get("marker", ""), label=line.get("label", ""))
    ax.set_title(labels.get("title", ""), fontsize=float(labels.get("title_size", 15)), fontweight=labels.get("title_weight", "normal"), pad=float(labels.get("title_pad", 10)))
    ax.set_xlabel(labels.get("xlabel", result.xlabel), fontsize=float(labels.get("size", 11)))
    ax.set_ylabel(labels.get("ylabel", result.ylabel), fontsize=float(labels.get("size", 11)))
    if axes_settings.get("xscale") in {"linear", "log", "symlog"}: ax.set_xscale(axes_settings["xscale"])
    if axes_settings.get("yscale") in {"linear", "log", "symlog"}: ax.set_yscale(axes_settings["yscale"])
    xlim = project.get("view", {}).get("xlim") or axes_settings.get("xlim")
    ylim = project.get("view", {}).get("ylim") or axes_settings.get("ylim")
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    ax.grid(bool(project.get("grid", {}).get("enabled", True)), which=project.get("grid", {}).get("which", "major"), linestyle=project.get("grid", {}).get("style", "--"), alpha=float(project.get("grid", {}).get("alpha", .28)))
    for annotation in project.get("annotations", []):
        kind = annotation.get("type", "text")
        style = {"color": annotation.get("color", "#d95f59"), "linestyle": annotation.get("linestyle", "--"), "linewidth": float(annotation.get("linewidth", 1.5)), "alpha": float(annotation.get("alpha", .9))}
        if kind == "vline": ax.axvline(float(annotation.get("x", 0)), **style)
        elif kind == "hline": ax.axhline(float(annotation.get("y", 0)), **style)
        elif kind == "region": ax.axvspan(float(annotation.get("x0", 0)), float(annotation.get("x1", 1)), color=annotation.get("color", "#9b8cff"), alpha=float(annotation.get("alpha", .2)))
        elif kind == "point": ax.scatter([float(annotation.get("x", 0))], [float(annotation.get("y", 0))], color=annotation.get("color", "#d95f59"), s=float(annotation.get("size", 45)), alpha=float(annotation.get("alpha", .9)), zorder=5)
        elif kind == "arrow": ax.annotate(annotation.get("text", ""), (float(annotation.get("x1", 0)), float(annotation.get("y1", 0))), xytext=(float(annotation.get("x0", 0)), float(annotation.get("y0", 0))), arrowprops={"arrowstyle": annotation.get("arrowstyle", "->"), "color": annotation.get("color", "#d95f59"), "lw": float(annotation.get("linewidth", 1.5)), "alpha": float(annotation.get("alpha", .9))}, fontsize=float(annotation.get("fontsize", 11)))
        elif kind == "text": ax.annotate(annotation.get("text", "Note"), (float(annotation.get("x", 0)), float(annotation.get("y", 0))), fontsize=float(annotation.get("fontsize", 11)), color=annotation.get("color", "#d95f59"), rotation=float(annotation.get("rotation", 0)), ha=annotation.get("ha", "left"), va=annotation.get("va", "bottom"), bbox={"facecolor": annotation.get("background", "none"), "alpha": float(annotation.get("background_alpha", 0)), "edgecolor": "none", "pad": 3})
    if legend.get("enabled"):
        handles, _ = ax.get_legend_handles_labels()
        if handles:
            ax.legend(loc=legend.get("location", "best"), fontsize=float(legend.get("fontsize", 10)), frameon=bool(legend.get("frame", True)), framealpha=float(legend.get("alpha", .85)), ncol=int(legend.get("ncol", 1)), title=legend.get("title", ""), title_fontsize=float(legend.get("title_size", 10)))
    fig.tight_layout()
    if return_figure: return fig
    output = BytesIO(); fig.savefig(output, format="png", dpi=fig.dpi); plt.close(fig); output.seek(0)
    return "data:image/png;base64," + base64.b64encode(output.read()).decode("ascii")
