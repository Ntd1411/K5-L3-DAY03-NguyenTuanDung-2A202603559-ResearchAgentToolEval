from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err

VALID_SORTS = {"stars", "forks", "updated"}


def search_github_repos(
    query: str = "",
    language: str = "",
    sort: str = "stars",
    limit: int = 5,
) -> dict[str, Any]:
    try:
        cleaned_query = (query or "").strip() if isinstance(query, str) else ""
        if not cleaned_query:
            return {
                "tool": "search_github_repos",
                "error": "ValueError",
                "message": "Query must be a non-empty string",
                "items": [],
            }

        cleaned_sort = (sort or "stars").strip().lower() if isinstance(sort, str) else ""
        if cleaned_sort not in VALID_SORTS:
            return {
                "tool": "search_github_repos",
                "error": "ValueError",
                "message": f"Invalid sort '{sort}'. Allowed values: stars, forks, updated",
                "items": [],
            }

        try:
            parsed_limit = int(limit)
        except (TypeError, ValueError):
            return {
                "tool": "search_github_repos",
                "error": "ValueError",
                "message": f"Invalid limit '{limit}'. Must be a positive integer",
                "items": [],
            }
        if parsed_limit <= 0:
            return {
                "tool": "search_github_repos",
                "error": "ValueError",
                "message": "limit must be greater than 0",
                "items": [],
            }
        parsed_limit = min(parsed_limit, 20)

        cleaned_lang = (language or "").strip() if isinstance(language, str) else ""
        q = f"{cleaned_query} language:{cleaned_lang}" if cleaned_lang else cleaned_query

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": os.getenv("ARXIV_USER_AGENT", "AI20k-Day03-Research-Agent/1.0"),
        }
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": q, "sort": cleaned_sort, "order": "desc", "per_page": parsed_limit},
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json() or {}
        raw_items = data.get("items") or []
        items = [
            {
                "title": item.get("full_name") or item.get("name") or "",
                "url": item.get("html_url") or "",
                "source": "github.com",
                "summary": (item.get("description") or "").strip(),
                "stars": item.get("stargazers_count", 0),
                "language": item.get("language") or cleaned_lang,
            }
            for item in raw_items[:parsed_limit]
            if item.get("html_url") or item.get("full_name")
        ]
        return {
            "tool": "search_github_repos",
            "query": cleaned_query,
            "language": cleaned_lang,
            "sort": cleaned_sort,
            "items": items,
        }
    except Exception as exc:
        return err("search_github_repos", exc)
