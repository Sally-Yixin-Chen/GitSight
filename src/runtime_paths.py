"""运行时路径：兼容源码运行和 PyInstaller onedir 打包。"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def application_root() -> Path:
    """返回应用根目录；打包后使用 exe 所在目录。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


APPLICATION_ROOT = application_root()
# PyInstaller 6 places bundled data under its internal runtime directory.
BUNDLED_ROOT = Path(getattr(sys, "_MEIPASS", APPLICATION_ROOT))


def user_data_root() -> Path:
    """Return a writable per-user directory for a packaged desktop client."""
    local_app_data = os.getenv("LOCALAPPDATA")
    if getattr(sys, "frozen", False) and local_app_data:
        return Path(local_app_data) / "GitSight"
    return APPLICATION_ROOT


DATA_ROOT = user_data_root()
DEFAULT_DATA_FILE = DATA_ROOT / "data" / "projects.json"
LEGACY_DATA_FILE = DATA_ROOT / "data" / "repos.json"
BUNDLED_LEGACY_DATA_FILE = BUNDLED_ROOT / "data" / "repos.json"
