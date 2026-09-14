"""定时从 GitHub 更新项目缓存，供网站离线读取。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from data_manager import load_projects as load_json_projects
from data_manager import save_projects
from github_api import extract_repo_data, search_repositories


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE_FILE = PROJECT_ROOT / "data" / "projects.json"
LEGACY_DATA_FILE = PROJECT_ROOT / "data" / "repos.json"
DEFAULT_QUERY = os.getenv("GITHUB_SEARCH_QUERY", "stars:>1000")
DEFAULT_RESULTS_PER_PAGE = 30


def refresh_project_cache(
    file_path: str | Path = DEFAULT_CACHE_FILE,
    query: str = DEFAULT_QUERY,
    per_page: int = DEFAULT_RESULTS_PER_PAGE,
) -> list[dict[str, Any]]:
    """请求一次 GitHub API，并将候选项目覆盖保存到本地 JSON 缓存。"""
    repositories = search_repositories(
        query=query,
        sort="stars",
        order="desc",
        per_page=per_page,
    )
    projects = [extract_repo_data(repository) for repository in repositories]
    save_projects(projects, file_path)
    return projects


def load_cached_projects(file_path: str | Path = DEFAULT_CACHE_FILE) -> list[dict[str, Any]]:
    """读取最近一次成功更新的缓存；不会调用 GitHub API。

    首次定时刷新尚未完成时，兼容读取项目自带的示例数据，保证网站可访问。
    """
    projects = load_json_projects(file_path)
    if projects or Path(file_path) != DEFAULT_CACHE_FILE:
        return projects
    return load_json_projects(LEGACY_DATA_FILE)


def get_available_topics(projects: list[dict[str, Any]]) -> list[str]:
    """从缓存项目中提取可供网页选择的 Topic 标签。"""
    topics = {
        topic.strip()
        for project in projects
        for topic in (project.get("topics") or [])
        if isinstance(topic, str) and topic.strip()
    }
    return sorted(topics, key=str.casefold)
