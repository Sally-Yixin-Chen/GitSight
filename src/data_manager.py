"""JSON persistence helpers for GitSight project records."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

from .runtime_paths import DEFAULT_DATA_FILE


def save_projects(projects: Iterable[dict[str, Any]], file_path: str | Path = DEFAULT_DATA_FILE) -> Path:
    """Save project records as UTF-8 JSON and return the saved path.

    A temporary file and atomic replacement prevent a partially-written JSON
    file if the process is interrupted while saving.
    """
    destination = Path(file_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    records = list(projects)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(records, handle, ensure_ascii=False, indent=2)
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return destination


def load_projects(file_path: str | Path = DEFAULT_DATA_FILE) -> list[dict[str, Any]]:
    """Load saved projects; return an empty list when no data has been saved."""
    source = Path(file_path)
    if not source.exists():
        return []
    try:
        with source.open("r", encoding="utf-8") as handle:
            projects = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"项目数据文件不是有效 JSON：{source}") from exc
    if not isinstance(projects, list):
        raise ValueError(f"项目数据应为列表：{source}")
    return projects
