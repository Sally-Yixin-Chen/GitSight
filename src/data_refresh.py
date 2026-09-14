"""定时从 GitHub 更新项目缓存，供网站离线读取。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .data_manager import load_projects as load_json_projects
from .data_manager import save_projects
from .github_api import extract_repo_data, search_repositories
from .runtime_paths import (
    BUNDLED_LEGACY_DATA_FILE,
    DEFAULT_DATA_FILE,
    LEGACY_DATA_FILE,
)


DEFAULT_CACHE_FILE = DEFAULT_DATA_FILE
DEFAULT_QUERY = os.getenv("GITHUB_SEARCH_QUERY", "stars:>1000")
DEFAULT_RESULTS_PER_PAGE = 30

# GitHub Topics 中常见的同义词与宽泛标签。它们不适合作为“差异化筛选”
# 的主选项：例如 awesome/list/resources 会指向相同类型的资源集合。
GENERIC_TOPICS = {
    "awesome", "awesome-list", "books", "coding", "development", "free",
    "list", "lists", "open-source", "programming", "project", "resource",
    "resources", "software",
}


def _topic_family(topic: str) -> str:
    """将语义相近的 GitHub Topic 归入同一筛选类别。"""
    value = topic.casefold()
    if any(word in value for word in ("ai", "agent", "assistant", "llm", "machine-learning", "deep-learning", "neural", "chatgpt", "claude", "openai", "anthropic", "tensorflow")):
        return "ai"
    if any(word in value for word in ("algorithm", "algos", "sorting", "sorts", "data-structure", "math")):
        return "algorithms"
    if any(word in value for word in ("web", "frontend", "react", "angular", "vue", "nodejs")):
        return "web"
    if any(word in value for word in ("backend", "api", "database", "dba")):
        return "backend"
    if any(word in value for word in ("devops", "cloud", "hosting", "dns", "domain", "sysops")):
        return "devops"
    if any(word in value for word in ("security", "hacking", "pentest", "privacy")):
        return "security"
    if any(word in value for word in ("tutorial", "course", "education", "learn", "curriculum", "study", "interview", "career", "certification")):
        return "learning"
    if any(word in value for word in ("design", "ui", "d3")):
        return "design"
    if any(word in value for word in ("automation", "workflow", "low-code", "no-code", "n8n")):
        return "automation"
    if any(word in value for word in ("linux", "bsd", "system", "distributed")):
        return "systems"
    if any(word in value for word in ("blockchain", "web3")):
        return "blockchain"
    if any(word in value for word in ("mcp", "integration", "ipaas")):
        return "integrations"
    if any(word in value for word in ("cli", "developer-tool", "framework", "library")):
        return "developer-tools"
    if any(word in value for word in ("roadmap", "computer-science", "guideline", "documentation")):
        return "learning"
    if any(word in value for word in ("community", "hacktoberfest")):
        return "community"
    if value in {"javascript", "python", "typescript", "golang", "cpp", "java"}:
        return f"language:{value}"
    return "misc"


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
    if LEGACY_DATA_FILE.exists():
        return load_json_projects(LEGACY_DATA_FILE)
    return load_json_projects(BUNDLED_LEGACY_DATA_FILE)


def get_available_topics(projects: list[dict[str, Any]]) -> list[str]:
    """从缓存项目中提取可供网页选择的 Topic 标签。"""
    topics = {
        topic.strip()
        for project in projects
        for topic in (project.get("topics") or [])
        if isinstance(topic, str) and topic.strip()
    }
    return sorted(topics, key=str.casefold)


def get_diverse_topics(projects: list[dict[str, Any]], limit: int = 15) -> list[str]:
    """选择覆盖项目差异最大的 Topic，避免展示大量高度重复的标签。

    算法每一步优先选择能覆盖最多“尚未被已选标签覆盖的项目”的 Topic；
    当新增覆盖相同时，选择出现次数更多的标签。因此既保留常见主题，
    也让后续标签尽量代表不同项目集合。
    """
    if limit <= 0:
        return []

    topic_projects: dict[str, set[int]] = {}
    display_names: dict[str, str] = {}
    for index, project in enumerate(projects):
        for topic in project.get("topics") or []:
            if not isinstance(topic, str) or not topic.strip():
                continue
            display_name = topic.strip()
            normalized = display_name.casefold()
            topic_projects.setdefault(normalized, set()).add(index)
            display_names.setdefault(normalized, display_name)

    selected: list[str] = []
    covered_projects: set[int] = set()
    # 优先排除宽泛标签；当可选标签不足时再用它们补齐。
    candidates = {topic for topic in topic_projects if topic not in GENERIC_TOPICS}
    meaningful_candidates = {
        topic for topic in candidates if _topic_family(topic) != "misc"
    }
    if len(meaningful_candidates) >= limit:
        candidates = meaningful_candidates
    elif len(candidates) < limit:
        candidates.update(topic_projects)

    used_families: set[str] = set()
    while candidates and len(selected) < limit:
        distinct_candidates = [
            topic for topic in candidates
            if _topic_family(topic) not in used_families
        ]
        choices = distinct_candidates or list(candidates)
        selected_topic = min(
            choices,
            key=lambda topic: (
                -len(topic_projects[topic] - covered_projects),
                -len(topic_projects[topic]),
                display_names[topic].casefold(),
            ),
        )
        selected.append(display_names[selected_topic])
        covered_projects.update(topic_projects[selected_topic])
        used_families.add(_topic_family(selected_topic))
        candidates.remove(selected_topic)
    return selected
