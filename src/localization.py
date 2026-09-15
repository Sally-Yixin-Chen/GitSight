"""为 GitHub 项目加载可维护的中文展示信息。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .runtime_paths import BUNDLED_ROOT, DATA_ROOT


LOCALIZATION_FILENAME = "project_locales.json"


def _localization_candidates() -> list[Path]:
    """返回用户数据和程序内置数据中的中文配置路径。"""
    candidates = [DATA_ROOT / "data" / LOCALIZATION_FILENAME, DATA_ROOT / LOCALIZATION_FILENAME]
    bundled = BUNDLED_ROOT / "data" / LOCALIZATION_FILENAME
    if bundled not in candidates:
        candidates.append(bundled)
    return candidates


def load_project_locales() -> dict[str, dict[str, str]]:
    """读取中文配置；用户目录中的配置优先于程序内置配置。"""
    for source in _localization_candidates():
        if not source.exists():
            continue
        try:
            with source.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValueError(f"中文项目配置不是有效 JSON：{source}") from exc

        if not isinstance(payload, dict):
            raise ValueError(f"中文项目配置应为对象：{source}")

        locales: dict[str, dict[str, str]] = {}
        for key, value in payload.items():
            if not isinstance(key, str) or not isinstance(value, dict):
                continue
            locales[key.strip().casefold()] = {
                field: str(value.get(field) or "").strip()
                for field in ("name", "description")
            }
        return locales
    return {}


def _project_key(project: Mapping[str, Any]) -> str:
    """使用完整仓库名作为中文配置的稳定键。"""
    return str(project.get("full_name") or project.get("name") or "").strip().casefold()


def with_project_locales(
    projects: list[dict[str, Any]],
    locales: Mapping[str, Mapping[str, str]] | None = None,
) -> list[dict[str, Any]]:
    """给项目记录补充中文名和中文介绍，不修改传入的原始列表。"""
    locale_map = locales if locales is not None else load_project_locales()
    localized: list[dict[str, Any]] = []
    for project in projects:
        record = dict(project)
        source = locale_map.get(_project_key(record), {})
        repository = str(record.get("full_name") or record.get("name") or "未命名项目")
        record["chinese_name"] = (
            str(record.get("chinese_name") or source.get("name") or "").strip()
            or repository.rsplit("/", 1)[-1]
        )
        record["chinese_description"] = (
            str(record.get("chinese_description") or source.get("description") or "").strip()
            or "暂无中文项目介绍，点击项目名称查看 GitHub 原始简介。"
        )
        localized.append(record)
    return localized
