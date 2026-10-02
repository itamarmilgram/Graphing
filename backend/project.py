from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TextIO
from .defaults import DEFAULTS, default_project


def save_project(project: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(project, indent=2), encoding="utf-8")


def load_project(stream: TextIO) -> dict[str, Any]:
    value = json.load(stream)
    if not isinstance(value, dict) or "analysis" not in value:
        raise ValueError("Project must contain an analysis section.")
    return value
