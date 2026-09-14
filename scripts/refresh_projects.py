"""GitSight 每周数据刷新入口。

由 Windows 任务计划程序每周执行一次；普通网站访问不运行此文件。
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.github_api import GitHubAPIError
from src.data_refresh import DEFAULT_CACHE_FILE, refresh_project_cache


def main() -> int:
    try:
        projects = refresh_project_cache()
    except GitHubAPIError as exc:
        print(f"刷新失败，保留原有缓存：{exc}")
        return 1

    print(f"已更新 {len(projects)} 个项目：{DEFAULT_CACHE_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
