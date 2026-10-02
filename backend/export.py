from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


def export_figure(figure, extension: str, settings: dict[str, Any]) -> str:
    suffix = "." + extension
    path = tempfile.NamedTemporaryFile(delete=False, suffix=suffix).name
    dpi = int(settings.get("dpi", figure.dpi))
    transparent = bool(settings.get("transparent", False))
    figure.savefig(path, format=extension, dpi=dpi, transparent=transparent, bbox_inches="tight" if settings.get("bbox_inches", True) else None)
    plt.close(figure)
    return path
