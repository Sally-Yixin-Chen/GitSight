"""Render the current GitSight ranking as a static GitHub Pages site."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app import app
from src.runtime_paths import BUNDLED_LEGACY_DATA_FILE, DEFAULT_DATA_FILE


SITE_ROOT = PROJECT_ROOT / "_site"


def main() -> int:
    SITE_ROOT.mkdir(parents=True, exist_ok=True)
    response = app.test_client().get("/")
    if response.status_code != 200:
        raise RuntimeError(f"首页渲染失败：HTTP {response.status_code}")
    (SITE_ROOT / "index.html").write_bytes(response.data)

    data_source = DEFAULT_DATA_FILE if DEFAULT_DATA_FILE.exists() else BUNDLED_LEGACY_DATA_FILE
    if data_source.exists():
        shutil.copy2(data_source, SITE_ROOT / "projects.json")

    static_source = PROJECT_ROOT / "static"
    static_target = SITE_ROOT / "static"
    if static_target.exists():
        shutil.rmtree(static_target)
    shutil.copytree(static_source, static_target)
    (SITE_ROOT / "health.json").write_text('{"status":"ok"}\n', encoding="utf-8")
    print(f"Static site written to {SITE_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
