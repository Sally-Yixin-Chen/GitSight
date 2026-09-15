"""GitHub REST API access helpers for the trending-project analysis app.

The functions in this module deliberately return plain dictionaries/lists.  That
keeps the API boundary separate from later ranking and Flask presentation code.
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GITHUB_API_URL = "https://api.github.com"
DEFAULT_TIMEOUT = 15
MAX_REQUEST_ATTEMPTS = 3


class GitHubAPIError(RuntimeError):
    """Raised when GitHub cannot return usable API data."""


def _request_json_with_headers(
    path: str,
    params: Mapping[str, Any] | None = None,
    token: str | None = None,
) -> tuple[Any, Mapping[str, str]]:
    """Request and decode one GitHub API endpoint, retaining response headers."""
    url = f"{GITHUB_API_URL}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"

    access_token = token or os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GitSight",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    request = Request(url, headers=headers)
    last_error: Exception | None = None
    for attempt in range(1, MAX_REQUEST_ATTEMPTS + 1):
        try:
            with urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8")), response.headers
        except HTTPError as exc:
            # Retry transient GitHub/server errors, but surface client errors
            # such as 403 immediately so the caller can apply its fallback.
            if exc.code not in {500, 502, 503, 504}:
                try:
                    detail = json.loads(exc.read().decode("utf-8")).get("message", exc.reason)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    detail = exc.reason
                raise GitHubAPIError(f"GitHub API 请求失败（{exc.code}）：{detail}") from exc
            last_error = exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc

        if attempt < MAX_REQUEST_ATTEMPTS:
            time.sleep(attempt)

    raise GitHubAPIError(f"无法获取 GitHub API 数据：{last_error}") from last_error


def _request_json(path: str, params: Mapping[str, Any] | None = None, token: str | None = None) -> Any:
    """Request and decode one GitHub API endpoint."""
    payload, _ = _request_json_with_headers(path, params=params, token=token)
    return payload


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


def get_contributor_count(
    owner: str,
    repo: str | None = None,
    token: str | None = None,
) -> int | None:
    """Return the total number of contributors, including pagination."""
    if repo is None:
        try:
            owner, repo = owner.split("/", 1)
        except ValueError as exc:
            raise ValueError("请提供 owner 和 repo，或传入 'owner/repo'") from exc
    if not owner.strip() or not repo.strip():
        raise ValueError("owner 和 repo 不能为空")

    endpoint = f"/repos/{owner}/{repo}/contributors"
    try:
        payload, headers = _request_json_with_headers(
            endpoint,
            params={"per_page": 1, "anon": "true"},
            token=token,
        )
    except GitHubAPIError as exc:
        # GitHub may reject anonymous-contributor expansion for very large
        # repositories. Retry with the named-contributor list so one such
        # repository does not abort the whole cache refresh.
        if "too large to list contributors" not in str(exc):
            raise
        try:
            payload, headers = _request_json_with_headers(
                endpoint,
                params={"per_page": 1, "anon": "false"},
                token=token,
            )
        except GitHubAPIError as retry_exc:
            if "too large to list contributors" in str(retry_exc):
                return None
            raise
    if not isinstance(payload, list):
        return 0

    # With one result per page, the final page number is the exact count.
    match = re.search(
        r"[?&]page=(\d+)[^>]*>;\s*rel=\"last\"",
        headers.get("Link", ""),
    )
    return int(match.group(1)) if match else len(payload)


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
        "size_kb": repository.get("size", 0),
        "topics": repository.get("topics") or [],
        "license": (repository.get("license") or {}).get("spdx_id"),
    }
