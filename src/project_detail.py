"""项目详情相关功能。

这个模块负责从项目列表中查找项目，并整理详情页需要展示的数据。
"""

from typing import Any, Dict, Iterable, Optional


def get_project_by_name(projects: Iterable[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    """根据项目名称查找项目。

    支持完整名称（例如 ``facebook/react``）和不区分大小写的查询。
    找不到时返回 ``None``。
    """
    if not name:
        return None

    target = name.strip().casefold()
    for project in projects:
        project_name = str(project.get("name", "")).strip().casefold()
        full_name = str(project.get("full_name", "")).strip().casefold()
        if target in {project_name, full_name}:
            return project
    return None


def get_project_detail(project: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """整理详情页需要展示的字段。

    返回统一的数据结构，页面无需直接处理 API/JSON 中的原始字段。
    """
    if project is None:
        return None

    project_name = str(project.get("full_name") or project.get("name", ""))
    owner, separator, repository = project_name.partition("/")
    return {
        "name": project_name or "未命名项目",
        "owner": project.get("owner") or (owner if separator else ""),
        "repository": repository if separator else str(project.get("name", "")),
        "description": project.get("description") or "暂无项目简介",
        "language": project.get("language") or "未填写",
        "license": project.get("license") or "未填写",
        "url": project.get("url") or project.get("html_url") or f"https://github.com/{project_name}",
        "stars": project.get("stars", 0),
        "forks": project.get("forks", 0),
        "open_issues": project.get("open_issues", 0),
        "last_push_days": project.get("last_push_days", 0),
        "contributors": project.get("contributors", 0),
        "size_kb": project.get("size_kb", 0),
        "hot_score": project.get("hot_score"),
    }

