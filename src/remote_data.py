"""Download the centrally published project cache for desktop clients."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl
from urllib.request import Request, urlopen

from .data_manager import save_projects


# The repository remains private; only this GitHub Pages file is public.
# No GitHub credential is embedded in the application.
PUBLIC_DATA_URL = os.getenv(
    "GITSIGHT_PUBLIC_DATA_URL",
    "https://sally-yixin-chen.github.io/GitSight/projects.json",
)
DEFAULT_TIMEOUT = 10


def _cache_busted_url(url: str) -> str:
    """Avoid serving an older copy from a client or CDN cache."""
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["v"] = str(int(time.time()))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def download_projects(file_path: str | Path, url: str = PUBLIC_DATA_URL) -> list[dict[str, Any]]:
    """Download, validate, and atomically save the public project cache."""
    request = Request(
        _cache_busted_url(url),
        headers={"Accept": "application/json", "User-Agent": "GitSight"},
    )
    try:
        with urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"无法下载公共项目数据：{exc}") from exc

    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise RuntimeError("公共项目数据格式无效")

    save_projects(payload, file_path)
    return payload
