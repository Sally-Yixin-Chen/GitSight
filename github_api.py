"""GitHub REST API access helpers for the trending-project analysis app.

The functions in this module deliberately return plain dictionaries/lists.  That
keeps the API boundary separate from later ranking and Flask presentation code.
"""

from __future__ import annotations

import json
import os
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GITHUB_API_URL = "https://api.github.com"
DEFAULT_TIMEOUT = 15


class GitHubAPIError(RuntimeError):
    """Raised when GitHub cannot return usable API data."""


def _request_json(path: str, params: Mapping[str, Any] | None = None, token: str | None = None) -> Any:
    """Request and decode one GitHub API endpoint."""
    url = f"{GITHUB_API_URL}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"

    access_token = token or os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GitPulse",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("message", exc.reason)
        except (UnicodeDecodeError, json.JSONDecodeError):
            detail = exc.reason
        raise GitHubAPIError(f"GitHub API 请求失败（{exc.code}）：{detail}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise GitHubAPIError(f"无法获取 GitHub API 数据：{exc}") from exc


def search_repositories(
    query: str = "stars:>1000",
    sort: str = "stars",
    order: str = "desc",
    per_page: int = 30,
    page: int = 1,
    token: str | None = None,
) -> list[dict[str, Any]]:
    """Search candidate repositories and return GitHub's repository records.

    ``query`` accepts GitHub's normal repository-search syntax, for example
    ``"language:python stars:>500 pushed:>2026-01-01"``.
    """
    if not query.strip():
        raise ValueError("query 不能为空")
    if not 1 <= per_page <= 100:
        raise ValueError("per_page 必须在 1 到 100 之间")
    if page < 1:
        raise ValueError("page 必须大于 0")

    payload = _request_json(
        "/search/repositories",
        {"q": query, "sort": sort, "order": order, "per_page": per_page, "page": page},
        token,
    )
    return payload.get("items", [])


def get_repository_detail(
    owner: str,
    repo: str | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    """Return the complete API record for one repository.

    Either call ``get_repository_detail("owner", "repository")`` or pass a
    full name such as ``get_repository_detail("owner/repository")``.
    """
    if repo is None:
        try:
            owner, repo = owner.split("/", 1)
        except ValueError as exc:
            raise ValueError("请提供 owner 和 repo，或传入 'owner/repo'") from exc
    if not owner.strip() or not repo.strip():
        raise ValueError("owner 和 repo 不能为空")
    return _request_json(f"/repos/{owner}/{repo}", token=token)


def extract_repo_data(repository: Mapping[str, Any]) -> dict[str, Any]:
    """Extract the stable fields consumed by storage and ranking modules."""
    owner = repository.get("owner") or {}
    return {
        "id": repository.get("id"),
        "name": repository.get("name", ""),
        "full_name": repository.get("full_name", ""),
        "owner": owner.get("login", ""),
        "description": repository.get("description") or "",
        "url": repository.get("html_url", ""),
        "language": repository.get("language") or "",
        "stars": repository.get("stargazers_count", 0),
        "forks": repository.get("forks_count", 0),
        "watchers": repository.get("watchers_count", 0),
        "open_issues": repository.get("open_issues_count", 0),
        "created_at": repository.get("created_at"),
        "updated_at": repository.get("updated_at"),
        "pushed_at": repository.get("pushed_at"),
        "topics": repository.get("topics") or [],
        "license": (repository.get("license") or {}).get("spdx_id"),
    }
