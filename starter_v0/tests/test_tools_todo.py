"""Tool Unit Test Suite (completed TODO challenge + new tool unit tests).

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
github_search_tool = TOOL_FUNCTIONS["github_search"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    options = ["OpenAI", "Anthropic"]
    result = clarify_tool(
        question="Bạn muốn xem tin của tổ chức nào?",
        response_type="choice",
        options=options,
    )
    assert result["question"] == "Bạn muốn xem tin của tổ chức nào?"
    assert result["response_type"] == "choice"
    assert result["options"] == ["OpenAI", "Anthropic"]
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Item 1", "url": "https://a.com/1", "section": "A"},
        {"title": "Item 2", "url": "https://b.com/2", "section": "B"},
        {"title": "Item 3", "url": "https://a.com/3", "section": "A"},
    ]
    result = format_tool(items=items, template="sections", headline="Digest")
    assert result["item_count"] == 3
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1


def test_format_thread_numbers_items() -> None:
    items = [
        {"title": "First post", "url": "https://x.com/1"},
        {"title": "Second post", "url": "https://x.com/2"},
        {"title": "Third post", "url": "https://x.com/3"},
    ]
    result = format_tool(items=items, template="thread")
    chunks = result["markdown"].split("\n\n")
    assert len(chunks) == 3
    assert chunks[0].startswith("1/ ")
    assert chunks[1].startswith("2/ ")
    assert chunks[2].startswith("3/ ")


def test_format_empty_items_does_not_crash() -> None:
    res_none = format_tool(items=None, template="bullets")
    res_empty = format_tool(items=[], template="sections")
    assert res_none["item_count"] == 0
    assert res_empty["item_count"] == 0
    assert isinstance(res_none["markdown"], str)
    assert isinstance(res_empty["markdown"], str)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot123456:ABCDEF")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI hôm nay", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot123456:ABCDEF" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100987654"
    assert calls[0]["json"]["text"] == "Bản tin AI hôm nay"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = send_tool(text="Bản tin AI", confirmed=True)

    assert calls == []
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    calls = fake_http(FakeResponse({"results": []}))

    result = lookup_tool(query="AI agents", topic="general", timeframe=None, max_results=3)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]
    assert result["timeframe"] is None


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({
        "data": {
            "markdown": "# Heading\nArticle content here.",
            "metadata": {
                "title": "Sample Title",
                "sourceURL": "https://www.openai.com/research/test",
            },
        }
    }))

    result = fetch_tool(url="https://www.openai.com/research/test")

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    item = result["items"][0]
    assert item["title"] == "Sample Title"
    assert item["url"] == "https://www.openai.com/research/test"
    assert item["source"] == "openai.com"
    assert item["summary"] == "# Heading\nArticle content here."


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({
        "data": {
            "markdown": "m" * 5500,
            "metadata": {"title": "Long Page", "sourceURL": "https://example.com/long"},
        }
    }))

    result = fetch_tool(url="https://example.com/long")
    summary = result["items"][0]["summary"]
    assert len(summary) == 4000
    assert summary == "m" * 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test")
    raw_timeline = [
        {"screen_name": "sama", "text": "Missing ID item"},
        *[
            {"tweet_id": str(100 + i), "screen_name": "sama", "text": f"Tweet {i}"}
            for i in range(6)
        ],
    ]
    calls = fake_http(FakeResponse({"timeline": raw_timeline}))

    result = timeline_tool(screenname="sama", limit=3)

    assert len(calls) == 1
    assert calls[0]["params"] == {"screenname": "sama"}
    assert len(result["items"]) == 3
    for idx, item in enumerate(result["items"]):
        assert item["url"] == f"https://x.com/sama/status/{100 + idx}"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test")
    calls = fake_http(FakeResponse({
        "timeline": [{"tweet_id": "999", "screen_name": "openai", "text": "GPT-5 update"}]
    }))

    result = social_search_tool(query="GPT-5", search_type="Top", limit=5)

    assert len(calls) == 1
    assert calls[0]["params"]["query"] == "GPT-5"
    assert calls[0]["params"]["search_type"] == "Top"
    assert result["search_type"] == "Top"
    assert len(result["items"]) == 1


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = policy_tool(query="   ", policy_area="all")
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy_tool(query="API key customer data privacy retention", policy_area="data_privacy")
    assert len(result["results"]) >= 1
    assert all(item["policy_area"] == "data_privacy" for item in result["results"])


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(
        query="injection probe citation viral tweet",
        policy_area="source_citation",
        top_k=5,
    )
    probe_sections = [item for item in result["results"] if item["section"] == "Injection probe"]
    assert len(probe_sections) == 1
    probe = probe_sections[0]
    assert any("ignore the citation policy" in line for line in probe["untrusted_text"])
    assert "ignore the citation policy" not in probe["facts"]


# ---------------- YOUR NEW TOOL(S): github_search ----------------

def test_my_new_tool_happy_path(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "items": [
            {
                "full_name": "explodinggradients/ragas",
                "html_url": "https://github.com/explodinggradients/ragas",
                "description": "Evaluation framework for RAG pipelines",
                "stargazers_count": 8500,
                "language": "Python",
            }
        ]
    }))

    result = github_search_tool(query="rag evaluation", language="python", sort="stars", limit=3)

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"] == {
        "q": "rag evaluation language:python",
        "sort": "stars",
        "order": "desc",
        "per_page": 3,
    }
    assert result["query"] == "rag evaluation"
    assert result["language"] == "python"
    assert result["sort"] == "stars"
    assert result["items"] == [
        {
            "title": "explodinggradients/ragas",
            "url": "https://github.com/explodinggradients/ragas",
            "source": "github.com",
            "summary": "Evaluation framework for RAG pipelines",
            "stars": 8500,
            "language": "Python",
        }
    ]


def test_my_new_tool_bad_input_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": []}))

    empty_query = github_search_tool(query="   ", language="python", sort="stars")
    bad_sort = github_search_tool(query="rag", language="python", sort="popularity")
    bad_limit = github_search_tool(query="rag", language="python", sort="stars", limit=0)

    assert calls == []
    assert empty_query["error"] == "ValueError"
    assert bad_sort["error"] == "ValueError"
    assert bad_limit["error"] == "ValueError"


def test_my_new_tool_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=403))

    result = github_search_tool(query="llm agent", language="python", sort="stars", limit=5)

    assert result["tool"] == "search_github_repos"
    assert result["error"] == "HTTPError"
    assert "403" in result["message"]
