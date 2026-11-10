from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
RUNS_DIR = ROOT / "runs"
PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
PROVIDER_LABELS = {
    "openrouter": "OpenRouter",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "gemini": "Google Gemini",
    "ollama": "Ollama (local)",
}
PROVIDER_KEY_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}
SUGGESTED_PROMPTS = [
    ("Tin AI mới", "Tin AI nổi bật hôm nay là gì? Tóm tắt 5 tin và dẫn nguồn."),
    ("Theo dõi X", "Lấy 5 bài đăng mới nhất từ tài khoản karpathy và tóm tắt giúp mình."),
    ("Tìm paper", "Tìm 3 paper gần đây về đánh giá AI agent, ưu tiên bài liên quan tool use."),
    ("Tra policy", "Chính sách nội bộ nói gì về việc trích dẫn nguồn trong báo cáo nghiên cứu?"),
]
USER_AVATAR = "🧑‍💻"
ASSISTANT_AVATAR = "🔎"

load_lab_env(ROOT)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #13231c;
            --muted: #66736d;
            --paper: #f7f5ef;
            --card: rgba(255, 255, 255, .82);
            --line: rgba(19, 35, 28, .11);
            --green: #0d6b4f;
            --mint: #dff4e8;
            --orange: #e36d3a;
        }
        .stApp {
            background:
                radial-gradient(circle at 8% 8%, rgba(237, 209, 151, .28), transparent 26rem),
                radial-gradient(circle at 92% 22%, rgba(86, 170, 137, .16), transparent 30rem),
                var(--paper);
            color: var(--ink);
        }
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            opacity: .18;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 160 160' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.08'/%3E%3C/svg%3E");
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] {
            background: rgba(246, 243, 234, .92);
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.35rem; }
        .block-container { max-width: 980px; padding-top: 2.2rem; padding-bottom: 7rem; }
        h1, h2, h3 { letter-spacing: -.035em; color: var(--ink); }
        .brand {
            display: flex;
            align-items: center;
            gap: .75rem;
            margin-bottom: 1.8rem;
        }
        .brand-mark {
            display: grid;
            place-items: center;
            width: 2.4rem;
            height: 2.4rem;
            border-radius: 12px;
            color: white;
            font-weight: 800;
            background: var(--green);
            box-shadow: 0 8px 24px rgba(13, 107, 79, .18);
        }
        .brand-name { font-weight: 760; line-height: 1.05; letter-spacing: -.02em; }
        .brand-kicker { color: var(--muted); font-size: .72rem; margin-top: .2rem; }
        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            color: var(--green);
            font-size: .72rem;
            font-weight: 750;
            letter-spacing: .12em;
            text-transform: uppercase;
        }
        .eyebrow-dot {
            width: .45rem;
            height: .45rem;
            border-radius: 50%;
            background: #25a875;
            box-shadow: 0 0 0 .28rem rgba(37, 168, 117, .12);
        }
        .hero { padding: 2.3rem 0 1.4rem; }
        .hero h1 {
            max-width: 780px;
            font-size: clamp(2.45rem, 6vw, 4.35rem);
            line-height: .98;
            margin: .85rem 0 1.05rem;
        }
        .hero h1 em { color: var(--green); font-style: normal; }
        .hero p { max-width: 620px; color: var(--muted); font-size: 1.02rem; line-height: 1.65; }
        .meta-row {
            display: flex;
            flex-wrap: wrap;
            gap: .55rem;
            margin: 1.4rem 0 2.2rem;
        }
        .meta-pill {
            padding: .48rem .72rem;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: rgba(255, 255, 255, .58);
            color: #4b5a53;
            font-size: .76rem;
        }
        .suggestion-label { color: var(--muted); font-size: .76rem; margin: 0 0 .6rem .1rem; }
        .session-bar {
            display: grid;
            grid-template-columns: minmax(200px, 1fr) repeat(3, auto);
            align-items: center;
            gap: .65rem;
            margin: .75rem 0 1.4rem;
            padding: .75rem .85rem;
            border: 1px solid var(--line);
            border-radius: 16px;
            background: rgba(255, 255, 255, .62);
            box-shadow: 0 8px 28px rgba(27, 45, 36, .035);
        }
        .session-title { min-width: 0; }
        .session-title strong { display: block; font-size: .86rem; }
        .session-title span {
            display: block;
            overflow: hidden;
            color: var(--muted);
            font-size: .7rem;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .session-metric {
            min-width: 4.6rem;
            padding: .35rem .6rem;
            border-left: 1px solid var(--line);
            text-align: center;
        }
        .session-metric strong { display: block; color: var(--ink); font-size: .94rem; }
        .session-metric span { color: var(--muted); font-size: .65rem; }
        .stButton > button {
            border: 1px solid var(--line);
            border-radius: 14px;
            background: var(--card);
            color: var(--ink);
            min-height: 2.8rem;
            box-shadow: 0 4px 18px rgba(28, 42, 35, .035);
        }
        .stButton > button:hover { border-color: rgba(13, 107, 79, .45); color: var(--green); }
        [data-testid="stChatMessage"] {
            border: 1px solid var(--line);
            border-radius: 18px;
            background: rgba(255, 255, 255, .68);
            padding: .45rem .55rem;
            margin-bottom: .8rem;
            box-shadow: 0 8px 34px rgba(27, 45, 36, .035);
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: rgba(223, 244, 232, .54);
        }
        [data-testid="stChatInput"] {
            border: 1px solid rgba(13, 107, 79, .24);
            background: rgba(255, 255, 255, .93);
            box-shadow: 0 15px 45px rgba(35, 57, 47, .12);
        }
        [data-testid="stExpander"] {
            border: 1px solid var(--line);
            border-radius: 12px;
            background: rgba(255,255,255,.45);
        }
        .tool-chip {
            display: inline-block;
            margin: 0 .35rem .35rem 0;
            padding: .28rem .56rem;
            border-radius: 8px;
            color: #0a5d44;
            background: var(--mint);
            font-size: .72rem;
            font-weight: 700;
        }
        .trace-summary {
            display: flex;
            flex-wrap: wrap;
            gap: .45rem;
            margin-bottom: .8rem;
        }
        .trace-stat {
            padding: .3rem .55rem;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255,255,255,.62);
            color: var(--muted);
            font-size: .7rem;
        }
        .compare-hero {
            margin: .8rem 0 1.5rem;
            padding: 1.2rem 1.3rem;
            border: 1px solid var(--line);
            border-radius: 18px;
            background: linear-gradient(120deg, rgba(223,244,232,.72), rgba(255,255,255,.58));
        }
        .compare-hero h2 { margin: 0 0 .35rem; font-size: 1.55rem; }
        .compare-hero p { margin: 0; color: var(--muted); font-size: .86rem; }
        .version-card {
            min-height: 9.4rem;
            padding: 1rem;
            border: 1px solid var(--line);
            border-radius: 16px;
            background: rgba(255,255,255,.7);
            box-shadow: 0 8px 28px rgba(27,45,36,.04);
        }
        .version-card .version-label {
            display: inline-block;
            padding: .25rem .5rem;
            border-radius: 7px;
            color: #0a5d44;
            background: var(--mint);
            font-size: .7rem;
            font-weight: 800;
        }
        .version-card .score { margin: .65rem 0 .2rem; font-size: 2rem; font-weight: 780; letter-spacing: -.05em; }
        .version-card .score-label { color: var(--muted); font-size: .7rem; }
        .version-card .version-meta { margin-top: .7rem; color: var(--muted); font-size: .68rem; line-height: 1.45; }
        .response-kicker {
            margin-bottom: .55rem;
            color: var(--muted);
            font-size: .68rem;
            font-weight: 750;
            letter-spacing: .08em;
            text-transform: uppercase;
        }
        .prompt-card {
            margin: .6rem 0 1rem;
            padding: .9rem 1rem;
            border-left: 3px solid var(--green);
            border-radius: 0 12px 12px 0;
            background: rgba(255,255,255,.58);
            color: var(--ink);
        }
        .side-section {
            margin: 1.2rem 0 .55rem;
            color: var(--muted);
            font-size: .68rem;
            font-weight: 750;
            letter-spacing: .1em;
            text-transform: uppercase;
        }
        .status-card {
            padding: .8rem .9rem;
            border: 1px solid var(--line);
            border-radius: 13px;
            background: rgba(255,255,255,.58);
            font-size: .77rem;
            color: var(--muted);
        }
        .status-card strong { color: var(--ink); }
        code { font-size: .8em !important; }
        @media (max-width: 720px) {
            .block-container { padding-top: 1rem; }
            .hero { padding-top: 1rem; }
            .hero h1 { font-size: 2.55rem; }
            .session-bar { grid-template-columns: 1fr 1fr 1fr; }
            .session-title { grid-column: 1 / -1; }
            .session-metric { border-left: 0; border-top: 1px solid var(--line); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def config_paths() -> tuple[Path, Path]:
    return ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml"


@st.cache_data(show_spinner=False)
def load_agent_assets(prompt_mtime: float, tools_mtime: float) -> tuple[str, list[dict[str, Any]]]:
    del prompt_mtime, tools_mtime
    prompt_path, tools_path = config_paths()
    system_prompt = prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    return system_prompt, declarations


def get_agent_assets() -> tuple[str, list[dict[str, Any]]]:
    prompt_path, tools_path = config_paths()
    return load_agent_assets(prompt_path.stat().st_mtime, tools_path.stat().st_mtime)


@st.cache_data(show_spinner=False)
def load_eval_runs(file_signature: tuple[tuple[str, float], ...]) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for path_text, _mtime in file_signature:
        path = Path(path_text)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        payload["_file_name"] = path.name
        runs.append(payload)
    return runs


def get_eval_runs() -> list[dict[str, Any]]:
    paths = sorted(RUNS_DIR.glob("*.json")) if RUNS_DIR.exists() else []
    signature = tuple((str(path), path.stat().st_mtime) for path in paths)
    return load_eval_runs(signature)


def version_sort_key(version: str) -> tuple[int, str]:
    match = re.search(r"(\d+)", version)
    return (int(match.group(1)) if match else -1, version)


def latest_base_runs(runs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for run in runs:
        if run.get("suite") != "base" or not run.get("version"):
            continue
        version = str(run["version"])
        current = selected.get(version)
        run_stamp = str(run.get("generated_at") or run.get("run_id") or run.get("_file_name", ""))
        current_stamp = str(
            current.get("generated_at") or current.get("run_id") or current.get("_file_name", "")
        ) if current else ""
        if current is None or run_stamp > current_stamp:
            selected[version] = run
    return selected


def new_chat_state(provider_name: str, model: str, version: str) -> None:
    prompt_path, tools_path = config_paths()
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])
    artifact_version = build_artifact_version(version, prompt_path, tools_path)

    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model or None,
        "system_prompt": str(prompt_path.relative_to(ROOT)),
        "tools": str(tools_path.relative_to(ROOT)),
        "history_window": st.session_state.history_window,
        "max_tool_rounds": st.session_state.max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)


def settings_signature(provider_name: str, model: str, version: str) -> tuple[str, str, str]:
    return provider_name, model.strip(), version.strip()


def provider_is_ready(provider_name: str) -> bool:
    if provider_name == "ollama":
        return True
    env_name = PROVIDER_KEY_ENV.get(provider_name)
    return bool(env_name and os.getenv(env_name))


def json_download() -> str:
    transcript = st.session_state.get("transcript", {})
    return json.dumps(transcript, ensure_ascii=False, indent=2, default=str)


def session_metrics() -> tuple[int, int, int]:
    transcript = st.session_state.get("transcript") or {}
    turns = transcript.get("turns", [])
    tool_events = [event for turn in turns for event in turn.get("tool_events", [])]
    source_count = 0
    for event in tool_events:
        result = event.get("result", {})
        if isinstance(result, dict) and isinstance(result.get("items"), list):
            source_count += len(result["items"])
    return len(turns), len(tool_events), source_count


def render_session_header(provider_name: str, model: str, version: str) -> None:
    turns, tool_calls, sources = session_metrics()
    model_label = html.escape(model or getattr(make_provider(provider_name), "default_model", "default"))
    transcript = st.session_state.get("transcript") or {}
    artifact_label = html.escape(str(transcript.get("artifact_version") or version))
    st.markdown(
        f"""
        <div class="session-bar">
            <div class="session-title">
                <strong><span style="color:#25a875">●</span> Phiên nghiên cứu đang hoạt động</strong>
                <span>{PROVIDER_LABELS[provider_name]} · {model_label} · {artifact_label}</span>
            </div>
            <div class="session-metric"><strong>{turns}</strong><span>LƯỢT</span></div>
            <div class="session-metric"><strong>{tool_calls}</strong><span>TOOL CALL</span></div>
            <div class="session-metric"><strong>{sources}</strong><span>NGUỒN</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tool_trace(turn: dict[str, Any]) -> None:
    events = turn.get("tool_events", [])
    if not events:
        return

    raw_tool_names = [str(event.get("tool", "tool")) for event in events]
    tool_names = [html.escape(name) for name in raw_tool_names]
    label = f"Tool trace · {' → '.join(raw_tool_names)}"
    with st.expander(label, expanded=False):
        result_count = sum(
            len(event.get("result", {}).get("items", []))
            for event in events
            if isinstance(event.get("result"), dict) and isinstance(event.get("result", {}).get("items"), list)
        )
        error_count = sum(
            1
            for event in events
            if isinstance(event.get("result"), dict) and event.get("result", {}).get("error")
        )
        rounds = len(turn.get("rounds", []))
        st.markdown(
            f'<div class="trace-summary"><span class="trace-stat">{rounds} vòng xử lý</span>'
            f'<span class="trace-stat">{len(events)} tool call</span>'
            f'<span class="trace-stat">{result_count} kết quả</span>'
            f'<span class="trace-stat">{error_count} lỗi</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "".join(f'<span class="tool-chip">{name}</span>' for name in tool_names),
            unsafe_allow_html=True,
        )
        for index, event in enumerate(events, start=1):
            st.markdown(f"**{index}. `{event.get('tool', 'unknown')}`**")
            args_tab, result_tab = st.tabs(["Arguments", "Result"])
            with args_tab:
                st.json(event.get("args", {}), expanded=True)
            with result_tab:
                st.json(event.get("result", {}), expanded=False)


def render_sidebar(
    tool_declarations: list[dict[str, Any]],
    eval_runs: list[dict[str, Any]],
) -> tuple[str, str, str, str]:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand">
                <div class="brand-mark">R</div>
                <div><div class="brand-name">Research Agent</div><div class="brand-kicker">Tool evaluation lab</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="side-section">Không gian làm việc</div>', unsafe_allow_html=True)
        mode = st.radio(
            "Chế độ",
            ["chat", "compare"],
            format_func=lambda item: "Trò chuyện" if item == "chat" else "So sánh 3 version",
            horizontal=True,
            label_visibility="collapsed",
        )

        provider_name = st.session_state.get("last_provider", "openrouter")
        version = st.session_state.get("last_version", "v3")
        default_model = getattr(make_provider(provider_name), "default_model", "")
        model = st.session_state.get(f"model_{provider_name}", default_model)

        if mode == "chat":
            st.markdown('<div class="side-section">Runtime</div>', unsafe_allow_html=True)
            provider_name = st.selectbox(
                "Provider",
                PROVIDERS,
                index=PROVIDERS.index(provider_name) if provider_name in PROVIDERS else 0,
                format_func=lambda item: PROVIDER_LABELS[item],
            )
            st.session_state.last_provider = provider_name
            default_model = getattr(make_provider(provider_name), "default_model", "")
            model = st.text_input(
                "Model",
                value=st.session_state.get(f"model_{provider_name}", default_model),
                key=f"model_input_{provider_name}",
                placeholder=default_model,
                help="Để trống để dùng model mặc định của provider.",
            )
            st.session_state[f"model_{provider_name}"] = model
            version = st.text_input(
                "Artifact version",
                value=version,
                help="Nhãn version được lưu trong transcript.",
            )
            st.session_state.last_version = version

            ready = provider_is_ready(provider_name)
            state_text = "Sẵn sàng" if ready else f"Thiếu {PROVIDER_KEY_ENV.get(provider_name, 'API key')}"
            state_color = "#0d6b4f" if ready else "#b5522c"
            st.markdown(
                f'<div class="status-card"><span style="color:{state_color}">●</span> <strong>{state_text}</strong><br>'
                f'{len(tool_declarations)} tools · tối đa {st.session_state.max_tool_rounds} vòng</div>',
                unsafe_allow_html=True,
            )

            st.markdown('<div class="side-section">Phiên làm việc</div>', unsafe_allow_html=True)
            if st.button("＋  Cuộc trò chuyện mới", width="stretch"):
                new_chat_state(provider_name, model, version)
                st.session_state.active_signature = settings_signature(provider_name, model, version)
                st.rerun()

            if st.session_state.get("transcript") and st.session_state.get("transcript_path"):
                st.download_button(
                    "↓  Tải transcript JSON",
                    data=json_download(),
                    file_name=st.session_state.transcript_path.name,
                    mime="application/json",
                    width="stretch",
                )

            with st.expander("Thiết lập nâng cao"):
                st.session_state.history_window = st.slider("History window", 1, 10, st.session_state.history_window)
                st.session_state.max_tool_rounds = st.slider("Max tool rounds", 1, 8, st.session_state.max_tool_rounds)
        else:
            comparable = latest_base_runs(eval_runs)
            st.markdown(
                f'<div class="status-card"><strong>{len(comparable)} version base eval</strong><br>'
                f'{len(eval_runs)} run JSON đã được lập chỉ mục</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="side-section">Toolbox</div>', unsafe_allow_html=True)
        names = [item.get("name", "unknown") for item in tool_declarations]
        st.markdown("".join(f'<span class="tool-chip">{name}</span>' for name in names), unsafe_allow_html=True)
        st.caption("Prompt và tool declaration được nạp trực tiếp từ `artifacts/`.")

    return mode, provider_name, model, version


def render_welcome(provider_name: str, model: str, declarations: list[dict[str, Any]]) -> str | None:
    st.markdown(
        """
        <section class="hero">
            <div class="eyebrow"><span class="eyebrow-dot"></span> Evidence-driven research</div>
            <h1>Hỏi một lần.<br><em>Kiểm chứng từng bước.</em></h1>
            <p>Agent tự chọn công cụ, truy xuất nguồn và để lại toàn bộ dấu vết thực thi — từ routing, arguments đến kết quả.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    model_label = html.escape(model or getattr(make_provider(provider_name), "default_model", "default"))
    st.markdown(
        f"""
        <div class="meta-row">
            <span class="meta-pill">◉ {PROVIDER_LABELS[provider_name]}</span>
            <span class="meta-pill">◇ {model_label}</span>
            <span class="meta-pill">⌁ {len(declarations)} công cụ</span>
        </div>
        <div class="suggestion-label">BẮT ĐẦU NHANH VỚI MỘT TÁC VỤ</div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(2)
    selected: str | None = None
    for index, (label, prompt) in enumerate(SUGGESTED_PROMPTS):
        with columns[index % 2]:
            if st.button(f"{label}  ↗", key=f"suggestion_{index}", width="stretch", help=prompt):
                selected = prompt
    return selected


def run_result_map(run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("id")): item
        for item in run.get("results", [])
        if item.get("id") is not None
    }


def percent_label(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value * 100:.0f}%"
    return "—"


def case_input_text(case: dict[str, Any]) -> str:
    value = case.get("input", "")
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def render_version_response(version: str, run: dict[str, Any], case: dict[str, Any] | None) -> None:
    st.markdown(f'<div class="response-kicker">Phản hồi {html.escape(version)}</div>', unsafe_allow_html=True)
    if case is None:
        st.warning("Case này không tồn tại trong run đã chọn.")
        return

    result = case.get("result", {})
    if result.get("passed"):
        st.success("PASS · Routing và arguments đúng")
    else:
        failure_type = result.get("failure_type") or result.get("case_failure_type") or "mismatch"
        st.error(f"FAIL · {failure_type}")

    actual_text = result.get("actual_text")
    calls = result.get("actual_tool_calls") or []
    if actual_text:
        st.markdown(str(actual_text))
    elif calls:
        st.caption("Model phản hồi bằng tool call, không có phần text.")
    else:
        st.caption("Model không trả text và không gọi tool.")

    if calls:
        st.markdown("**Tool call thực tế**")
        for call in calls:
            name = str(call.get("name", "unknown"))
            st.markdown(f'<span class="tool-chip">{html.escape(name)}</span>', unsafe_allow_html=True)
            st.code(json.dumps(call.get("args", {}), ensure_ascii=False, indent=2), language="json")

    failures = result.get("failures") or []
    mismatch = result.get("observed_mismatch")
    if mismatch:
        st.caption(f"Khác biệt quan sát được: {mismatch}")
    for failure in failures:
        st.caption(f"• {failure}")

    with st.expander("Expected vs. actual"):
        st.markdown("**Expected**")
        st.json(case.get("expect", {}), expanded=True)
        st.markdown("**Actual**")
        st.json(
            {
                "tool_calls": calls,
                "text": actual_text,
                "routing_correct": result.get("routing_correct"),
                "args_correct": result.get("args_correct"),
            },
            expanded=True,
        )

    tool_results = case.get("tool_results") or []
    if tool_results:
        with st.expander(f"Tool results · {len(tool_results)}"):
            st.json(tool_results, expanded=False)


def render_version_comparison(eval_runs: list[dict[str, Any]]) -> None:
    latest = latest_base_runs(eval_runs)
    available_versions = sorted(latest, key=version_sort_key)
    default_versions = available_versions[-3:]

    st.markdown(
        """
        <div class="eyebrow"><span class="eyebrow-dot"></span> Evaluation evidence</div>
        <div class="compare-hero">
            <h2>So sánh phản hồi qua 3 phiên bản</h2>
            <p>Đọc cùng một eval case trên ba run thật để đối chiếu routing, arguments, phản hồi text và kết quả tool.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if len(available_versions) < 3:
        st.warning("Cần ít nhất 3 version có base eval trong `runs/` để so sánh.")
        return

    chosen_versions = st.multiselect(
        "Chọn đúng 3 phiên bản",
        available_versions,
        default=default_versions,
        help="Mỗi version dùng run base mới nhất theo generated_at.",
    )
    if len(chosen_versions) != 3:
        st.info("Hãy chọn đúng 3 phiên bản để hiển thị phép so sánh.")
        return

    chosen_versions = sorted(chosen_versions, key=version_sort_key)
    selected_runs = [latest[version] for version in chosen_versions]
    summary_columns = st.columns(3)
    for column, version, run in zip(summary_columns, chosen_versions, selected_runs):
        summary = run.get("summary", {})
        artifact = html.escape(str(run.get("artifact_version", "—")))
        passed = summary.get("passed_cases", 0)
        total = summary.get("measured_cases", summary.get("total_cases", 0))
        score = percent_label(summary.get("case_accuracy"))
        with column:
            st.markdown(
                f"""
                <div class="version-card">
                    <span class="version-label">{html.escape(version)}</span>
                    <div class="score">{score}</div>
                    <div class="score-label">CASE ACCURACY · {passed}/{total} PASS</div>
                    <div class="version-meta">{artifact}<br>{html.escape(str(run.get('model', '—')))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    metric_rows = []
    metric_specs = [
        ("Case accuracy", "case_accuracy"),
        ("Routing accuracy", "tool_routing_accuracy"),
        ("Argument accuracy", "argument_accuracy"),
        ("Multiturn accuracy", "multiturn_accuracy"),
    ]
    for label, key in metric_specs:
        row = {"Metric": label}
        for version, run in zip(chosen_versions, selected_runs):
            row[version] = percent_label(run.get("summary", {}).get(key))
        metric_rows.append(row)
    with st.expander("Bảng metric tổng hợp", expanded=True):
        st.dataframe(metric_rows, width="stretch", hide_index=True)

    result_maps = [run_result_map(run) for run in selected_runs]
    case_ids = sorted(set().union(*(mapping.keys() for mapping in result_maps)))
    if not case_ids:
        st.info("Các run được chọn chưa có case result.")
        return

    different_case_ids = [
        case_id
        for case_id in case_ids
        if len({
            mapping.get(case_id, {}).get("result", {}).get("passed")
            for mapping in result_maps
        }) > 1
    ]
    default_case = different_case_ids[0] if different_case_ids else case_ids[0]

    def case_label(case_id: str) -> str:
        sample = next((mapping[case_id] for mapping in result_maps if case_id in mapping), {})
        prompt = case_input_text(sample).replace("\n", " ")
        if len(prompt) > 88:
            prompt = prompt[:85] + "…"
        return f"{case_id} — {prompt}"

    st.markdown("### Đối chiếu từng phản hồi")
    selected_case_id = st.selectbox(
        "Eval case",
        case_ids,
        index=case_ids.index(default_case),
        format_func=case_label,
    )
    sample_case = next(mapping[selected_case_id] for mapping in result_maps if selected_case_id in mapping)
    st.markdown(
        f'<div class="prompt-card"><strong>Yêu cầu người dùng</strong><br>{html.escape(case_input_text(sample_case))}</div>',
        unsafe_allow_html=True,
    )

    response_columns = st.columns(3)
    for column, version, run, mapping in zip(
        response_columns, chosen_versions, selected_runs, result_maps
    ):
        with column:
            render_version_response(version, run, mapping.get(selected_case_id))


def persist_turn(turn_record: dict[str, Any]) -> None:
    transcript = st.session_state.transcript
    transcript["history_window"] = st.session_state.history_window
    transcript["max_tool_rounds"] = st.session_state.max_tool_rounds
    transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, transcript)


def process_prompt(
    prompt: str,
    provider_name: str,
    model: str,
    version: str,
    system_prompt: str,
    declarations: list[dict[str, Any]],
) -> None:
    signature = settings_signature(provider_name, model, version)
    if not st.session_state.get("transcript") or st.session_state.get("active_signature") != signature:
        new_chat_state(provider_name, model, version)
        st.session_state.active_signature = signature

    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": prompt,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, st.session_state.history_window),
        {"role": "user", "content": prompt},
    ]

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        status = st.status("Đang lập kế hoạch nghiên cứu…", expanded=False)
        try:
            result = run_model_tool_loop(
                provider=make_provider(provider_name),
                messages=messages,
                tools=to_openai_tools(declarations),
                model=model.strip() or None,
                max_tool_rounds=st.session_state.max_tool_rounds,
            )
            turn_record.update(result)
            assistant_text = result.get("assistant_text") or "Agent không trả về nội dung."
            used_tools = [event.get("tool", "tool") for event in result.get("tool_events", [])]
            status.update(
                label=(f"Hoàn tất · {' → '.join(used_tools)}" if used_tools else "Hoàn tất · trả lời trực tiếp"),
                state="complete",
                expanded=False,
            )
            st.markdown(assistant_text)
            render_tool_trace(turn_record)
            st.session_state.history.extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": assistant_text},
            ])
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_text, "turn": turn_record}
            )
        except Exception as exc:
            error_text = f"{type(exc).__name__}: {exc}"
            turn_record.update({"status": "provider_error", "error": error_text})
            status.update(label="Không thể hoàn tất yêu cầu", state="error", expanded=True)
            st.error(error_text)
            st.caption("Kiểm tra API key, model và kết nối mạng rồi thử lại.")

    turn_record["ended_at"] = now_iso()
    persist_turn(turn_record)


def main() -> None:
    st.set_page_config(
        page_title="Research Agent · Tool Lab",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_styles()

    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("history_window", 5)
    st.session_state.setdefault("max_tool_rounds", 4)
    st.session_state.setdefault("transcript", None)
    st.session_state.setdefault("transcript_path", None)
    st.session_state.setdefault("active_signature", None)

    try:
        system_prompt, declarations = get_agent_assets()
    except Exception as exc:
        st.error(f"Không thể nạp artifacts: {type(exc).__name__}: {exc}")
        st.stop()

    eval_runs = get_eval_runs()
    mode, provider_name, model, version = render_sidebar(declarations, eval_runs)

    if mode == "compare":
        render_version_comparison(eval_runs)
        return

    suggested_prompt: str | None = None
    if not st.session_state.messages:
        suggested_prompt = render_welcome(provider_name, model, declarations)
    else:
        st.markdown(
            '<div class="eyebrow"><span class="eyebrow-dot"></span> Research session</div>',
            unsafe_allow_html=True,
        )
        st.markdown("## Luồng nghiên cứu")
        render_session_header(provider_name, model, version)
        for message in st.session_state.messages:
            avatar = USER_AVATAR if message["role"] == "user" else ASSISTANT_AVATAR
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
                if message["role"] == "assistant" and message.get("turn"):
                    render_tool_trace(message["turn"])

    typed_prompt = st.chat_input("Giao một nhiệm vụ nghiên cứu…")
    prompt = typed_prompt or suggested_prompt
    if prompt:
        process_prompt(prompt, provider_name, model, version, system_prompt, declarations)


if __name__ == "__main__":
    main()
