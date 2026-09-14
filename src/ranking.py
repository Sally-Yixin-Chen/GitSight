"""GitHub 候选项目的静态热门排行榜。

本模块只负责评分和排序，不负责调用 GitHub API 或读写 JSON 文件。
综合分数严格使用：H = 0.50 * P + 0.30 * R + 0.20 * S。
"""

from __future__ import annotations

from datetime import datetime, timezone
from math import exp, log1p
from typing import Any, Dict, List, Mapping, Sequence


LANGUAGE_SCORES = {
    "python": 1.00,
    "javascript": 0.95,
    "java": 0.95,
    "c++": 0.90,
    "c": 0.85,
    "html": 0.90,
    "css": 0.90,
    "typescript": 0.85,
    "go": 0.75,
    "rust": 0.65,
}

INTEREST_TOPICS = {
    "python",
    "ai",
    "artificial-intelligence",
    "machine-learning",
    "deep-learning",
    "computer-vision",
    "game",
    "game-development",
    "web",
    "web-development",
    "flask",
    "django",
    "crawler",
    "scraping",
    "data-visualization",
    "algorithm",
    "chatbot",
    "automation",
    "gui",
}


def _number(value: Any, default: float = 0.0) -> float:
    """把可能为空或格式异常的数值转换为非负浮点数。"""
    try:
        number = float(value)
        return max(0.0, number)
    except (TypeError, ValueError):
        return default


def _get_metric(repo: Mapping[str, Any], name: str, api_name: str) -> float:
    """优先读取项目中的统一字段，否则读取 GitHub API 原始字段。"""
    value = repo.get(name)
    if value is None:
        value = repo.get(api_name)
    return _number(value)


def calculate_recency_score(updated_at: Any) -> float:
    """根据最后更新时间计算近期活跃度 R，结果范围为 0~1。

    无法解析更新时间时返回约定的默认分数 0.3。
    """
    if not isinstance(updated_at, str) or not updated_at.strip():
        return 0.3

    value = updated_at.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    try:
        updated = datetime.fromisoformat(value)
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days = max(0.0, (now - updated.astimezone(timezone.utc)).total_seconds() / 86400)
    except (TypeError, ValueError, OverflowError):
        return 0.3

    return exp(-days / 365)


def calculate_language_score(language: Any) -> float:
    """计算主要编程语言的学生适配度。"""
    if not isinstance(language, str) or not language.strip():
        return 0.50
    return LANGUAGE_SCORES.get(language.strip().casefold(), 0.60)


def calculate_topic_score(topics: Any) -> float:
    """根据命中的兴趣主题数量计算 TopicScore。"""
    if not isinstance(topics, (list, tuple, set)):
        return 0.5

    matched = sum(
        1 for topic in topics
        if isinstance(topic, str) and topic.strip().casefold() in INTEREST_TOPICS
    )
    if matched == 0:
        return 0.5
    if matched == 1:
        return 0.7
    if matched == 2:
        return 0.85
    return 1.0


def calculate_student_fit(repo: Mapping[str, Any]) -> float:
    """计算学生兴趣匹配度 S。"""
    language_score = calculate_language_score(repo.get("language"))
    topic_score = calculate_topic_score(repo.get("topics"))
    return 0.5 * language_score + 0.5 * topic_score


def _minmax_normalize(values: Sequence[float]) -> List[float]:
    """对一组数做 Min-Max 归一化；所有值相同时返回 0.5。"""
    if not values:
        return []
    minimum, maximum = min(values), max(values)
    if maximum == minimum:
        return [0.5] * len(values)
    return [(value - minimum) / (maximum - minimum) for value in values]


def calculate_normalized_metrics(projects: Sequence[Mapping[str, Any]]) -> List[Dict[str, float]]:
    """计算所有候选项目的对数值和归一化值。

    返回列表与 ``projects`` 顺序一一对应，每项包含 stars_log、forks_log、
    stars_norm 和 forks_norm，便于传给 ``calculate_hot_score``。
    """
    stars_log = [
        log1p(_get_metric(repo, "stars", "stargazers_count")) for repo in projects
    ]
    forks_log = [
        log1p(_get_metric(repo, "forks", "forks_count")) for repo in projects
    ]
    stars_norm = _minmax_normalize(stars_log)
    forks_norm = _minmax_normalize(forks_log)

    return [
        {
            "stars_log": stars_log[index],
            "forks_log": forks_log[index],
            "stars_norm": stars_norm[index],
            "forks_norm": forks_norm[index],
        }
        for index in range(len(projects))
    ]


def calculate_hot_score(repo: Mapping[str, Any], normalized_stats: Mapping[str, Any]) -> float:
    """计算单个项目的综合热度分数，返回 0~100 且保留两位小数。"""
    popularity = (
        0.7 * _number(normalized_stats.get("stars_norm"), 0.5)
        + 0.3 * _number(normalized_stats.get("forks_norm"), 0.5)
    )
    recency = calculate_recency_score(repo.get("updated_at"))
    student_fit = calculate_student_fit(repo)
    score = 100 * (0.50 * popularity + 0.30 * recency + 0.20 * student_fit)
    return round(max(0.0, min(100.0, score)), 2)


def rank_projects(projects: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """计算并按综合热度从高到低返回项目副本。"""
    normalized_metrics = calculate_normalized_metrics(projects)
    ranked = [
        {**repo, "hot_score": calculate_hot_score(repo, normalized_metrics[index])}
        for index, repo in enumerate(projects)
    ]
    ranked.sort(key=lambda project: project["hot_score"], reverse=True)
    return ranked


def get_top_projects(projects: Sequence[Mapping[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
    """返回排行榜前 n 个项目；n 小于 0 时按 0 处理。"""
    return rank_projects(projects)[: max(0, n)]
