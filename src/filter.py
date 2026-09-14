"""个性化 Topic 筛选与热门项目推荐模块。

本模块先根据用户选择的 GitHub Topics 从已有项目中筛选，再复用
``ranking.get_top_projects`` 的热度算法生成个性化榜单。
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

try:  # 作为 GitPulse 包运行时
    from .ranking import get_top_projects
except ImportError:  # 便于单独运行或测试该模块
    from ranking import get_top_projects


def _normalize_topics(topics: str | Iterable[str] | None) -> set[str]:
    """将用户输入统一为去重、小写的 Topic 集合。"""
    if topics is None:
        return set()
    if isinstance(topics, str):
        # Web 表单可传入 "AI, Python, Web" 这样的文本。
        topics = topics.split(",")

    normalized = set()
    for topic in topics:
        if isinstance(topic, str) and topic.strip():
            normalized.add(topic.strip().casefold())
    return normalized


def filter_projects_by_topics(
    projects: Sequence[Mapping[str, Any]],
    selected_topics: str | Iterable[str] | None,
) -> list[dict[str, Any]]:
    """返回至少命中一个所选 Topic 的项目。

    Topic 比较不区分大小写。未选择任何 Topic 时，返回全部项目的副本，
    使页面可以自然退化为普通热门榜。
    """
    interests = _normalize_topics(selected_topics)
    if not interests:
        return [dict(project) for project in projects]

    matched_projects: list[dict[str, Any]] = []
    for project in projects:
        project_topics = _normalize_topics(project.get("topics"))
        if interests.intersection(project_topics):
            matched_projects.append(dict(project))
    return matched_projects


def get_personalized_top_projects(
    projects: Sequence[Mapping[str, Any]],
    selected_topics: str | Iterable[str] | None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """按兴趣筛选项目，并调用 ranking.py 返回个性化 TOP N。

    Args:
        projects: 已读取的 GitHub 项目数据。
        selected_topics: 用户选择的一个或多个 Topic；多个 Topic 采用“任一
            匹配”规则，例如选择 AI 和 Python 会保留含任一标签的项目。
        limit: 榜单数量，默认 10。
    """
    if limit < 0:
        raise ValueError("limit 不能小于 0")
    filtered_projects = filter_projects_by_topics(projects, selected_topics)
    return get_top_projects(filtered_projects, n=limit)


# 为 Web 路由或课堂示例提供更短的函数名称。
filter_by_topics = filter_projects_by_topics
get_personalized_top10 = get_personalized_top_projects
