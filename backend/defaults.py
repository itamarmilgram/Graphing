"""The single editable source for application defaults.

Change this file for personal defaults. Project state is copied from here when
a new session or new file is opened; later edits only affect that project.
"""
from __future__ import annotations

from copy import deepcopy

DEFAULTS = {
    "analysis_type": "fft",
    "analysis": {
        "channel": 0, "nfft": 8192, "nperseg": 8192, "noverlap": 4096,
        "window": "hann", "window_parameter": 14, "detrend": "constant",
        "scaling": "density", "return_onesided": True, "amplitude": "magnitude",
        "db": True, "start_time": 0, "end_time": 0,
    },
    "figure": {"size": [10, 5.8], "dpi": 130, "background": "white"},
    "axes": {"xscale": "linear", "yscale": "linear", "background": "white", "xlim": None, "ylim": None},
    "line": {"color": "#197c78", "width": 1.8, "style": "-", "marker": "", "marker_size": 6, "alpha": .9, "label": ""},
    "labels": {"title": "", "xlabel": "", "ylabel": "", "size": 11, "title_size": 15, "title_weight": "normal", "title_pad": 10},
    "grid": {"enabled": True, "which": "major", "style": "--", "alpha": .28},
    "legend": {"enabled": False, "location": "best", "fontsize": 10, "frame": True, "alpha": .85, "ncol": 1, "title": "", "title_size": 10},
    "colorbar": {"cmap": "viridis", "label": "Magnitude"},
    "annotations": [],
    "export": {"format": "png", "dpi": 300, "transparent": False, "bbox_inches": True},
    "view": {"xlim": None, "ylim": None, "history": [], "history_index": -1},
}


def default_project() -> dict:
    return deepcopy(DEFAULTS)
