---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, language, sort, limit]
outputs: [query, language, sort, items]
side_effect: false
---
# github_search

Searches public open-source repositories on GitHub by keyword, optional programming language, and sort order (`stars`, `forks`, `updated`).
Returns repository metadata (`title`, `url`, `source`, `summary`, `stars`, `language`) ready for research digests.
