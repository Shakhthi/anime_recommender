import html
import re

import streamlit as st
from dotenv import load_dotenv

from pipeline.pipeline import AnimeRecommendationPipeline

load_dotenv()

st.set_page_config(
    page_title="Anime Matchmaker",
    page_icon="🎌",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css():
    st.markdown(
        """
        <style>
        :root {
            --bg: #0b1020;
            --panel: #101827;
            --panel-strong: #111c2f;
            --line: rgba(148, 163, 184, 0.18);
            --text: #e5eefb;
            --muted: #a0aec0;
            --primary: #8b5cf6;
            --primary-soft: rgba(139, 92, 246, 0.14);
            --success: #22c55e;
        }

        .stApp {
            background: radial-gradient(circle at top left, rgba(139, 92, 246, 0.18), transparent 30%),
                        linear-gradient(180deg, #0b1020 0%, #0f172a 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1.15rem;
            padding-bottom: 2rem;
        }

        .glass-panel {
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.35);
            backdrop-filter: blur(10px);
        }

        .compact-header {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.9rem;
        }

        .compact-header h1 {
            margin: 0;
            color: #f8fafc;
            font-size: clamp(1.7rem, 3vw, 2.35rem);
            line-height: 1.05;
        }

        .compact-header p {
            margin: 0.35rem 0 0;
            color: var(--muted);
            font-size: 0.9rem;
        }

        .mini-label {
            color: var(--muted);
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }

        .hero-box {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.18), rgba(59,130,246,0.08));
            border: 1px solid rgba(139, 92, 246, 0.35);
            border-radius: 20px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
        }

        .recommendation-card {
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.94), rgba(15, 23, 42, 0.82));
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-left: 4px solid #a78bfa;
            border-radius: 18px;
            padding: 0.85rem 1rem 1rem 1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.28);
        }

        .reco-header {
            display: grid;
            grid-template-columns: auto minmax(0, 1fr);
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .reco-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2.3rem;
            height: 2.3rem;
            border-radius: 12px;
            background: rgba(167, 139, 250, 0.18);
            color: #ddd6fe;
            border: 1px solid rgba(167, 139, 250, 0.35);
            font-weight: 700;
            flex-shrink: 0;
        }

        .reco-title {
            margin: 0;
            font-size: 1.2rem;
            font-weight: 700;
            line-height: 1.35;
            color: #f8fafc;
            word-break: break-word;
            overflow-wrap: anywhere;
            white-space: normal;
        }

        .reco-section {
            margin-top: 0.65rem;
            color: #dfe7f5;
            line-height: 1.55;
        }

        .reco-label {
            display: inline-block;
            color: #c4b5fd;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.28rem;
        }

        .chip {
            display: inline-block;
            background: var(--primary-soft);
            color: #ddd6fe;
            border: 1px solid rgba(139, 92, 246, 0.35);
            border-radius: 999px;
            padding: 0.4rem 0.75rem;
            font-size: 0.78rem;
            margin: 0.15rem 0.25rem 0.15rem 0;
        }

        .context-banner {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 0.85rem;
            margin: 0.2rem 0 1rem 0;
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(148, 163, 184, 0.22);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            color: #dbeafe;
            font-size: 0.82rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            font-weight: 600;
        }

        .context-banner strong {
            color: #f8fafc;
            font-weight: 800;
            text-transform: none;
            letter-spacing: 0;
        }

        div[data-testid="stExpander"] {
            border-color: var(--line);
            background: rgba(15, 23, 42, 0.42);
        }

        div[data-testid="stTextArea"] textarea {
            min-height: 96px;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 0.8rem;
            }

            .compact-header {
                display: block;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def init_pipeline():
    return AnimeRecommendationPipeline()


def clear_query():
    st.session_state.last_query = ""
    st.session_state.query_input = ""


def apply_quick_prompt():
    selected_prompt = st.session_state.get("quick_prompt", "")
    if selected_prompt and selected_prompt != "Pick a prompt...":
        st.session_state.query_input = selected_prompt
        st.session_state.last_query = selected_prompt


def _recommendation_number(text: str):
    normalized = re.sub(r"^\s*(?:[*_`]+\s*)*", "", text)
    return re.match(r"^\d+[.)]\s*", normalized)


def _clean_text(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^[\-•*\s]+", "", value)
    value = re.sub(r"^\d+\.\s*", "", value)
    value = re.sub(r"\*\*+$", "", value)
    value = re.sub(r"^(Summary|Plot|Why it matches|Why this fits|Why it fits|Why it works|Reason|Recommendation)\s*[:\-]?\s*", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^Here are.*?recommendations?[:\-]?\s*", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^Based on (your|the) .*?(?:preferences|request|query|interest|taste|vibe)[:\-]?\s*", "", value, flags=re.IGNORECASE)
    return value.strip()


def _looks_like_query_intro(text: str) -> bool:
    cleaned = text.strip().lower()
    if not cleaned:
        return True
    intro_prefixes = (
        "here are",
        "based on",
        "you are looking",
        "you want",
        "you need",
        "your request",
        "your query",
        "your preferences",
        "if you like",
        "for someone who likes",
        "since you want",
        "this matches",
        "for a mix of",
        "for fans of",
        "for a vibe like",
        "if you enjoy",
        "given your",
        "considering your",
        "i recommend",
        "i'd recommend",
        "i would recommend",
        "here is",
    )
    if cleaned.startswith(intro_prefixes):
        return True
    intro_markers = [
        "your preferences",
        "your request",
        "your query",
        "you are looking",
        "you want",
        "anime like",
        "based on the anime",
        "for someone who likes",
        "this preference",
        "this request",
        "the user wants",
        "for a mix of",
        "for fans of",
        "if you enjoy",
        "you enjoy",
        "given your",
        "considering your",
        "i recommend",
        "i'd recommend",
        "i would recommend",
        "here is",
    ]
    return any(marker in cleaned for marker in intro_markers)


def _is_probably_anime_title(text: str) -> bool:
    title = text.strip()
    if not title:
        return False
    lowered = title.lower()
    if lowered in {"recommendation", "here are some recommendations"}:
        return False
    if len(title.split()) > 12:
        return False
    if any(marker in lowered for marker in [
        "you", "your", "query", "preferences", "request", "want", "like anime",
        "for a mix", "based on", "given your", "considering your", "i recommend",
        "i'd recommend", "i would recommend", "here are", "here is", "if you enjoy"
    ]):
        return False
    if any(ch.isdigit() for ch in title):
        return False
    return True


def _split_recommendation_block(block: str):
    lines = [item.strip() for item in block.splitlines() if item.strip()]
    if not lines:
        return None

    normalized_first_line = re.sub(r"^\s*(?:[*_`]+\s*)*", "", lines[0])
    numbered_match = re.match(r"^\d+[.)]\s*(.+)$", normalized_first_line)
    if not numbered_match:
        return None

    raw_title = numbered_match.group(1).strip()
    raw_title = re.split(r"\s+[—–-]\s+", raw_title, maxsplit=1)[0]
    title = _clean_text(raw_title)
    if not _is_probably_anime_title(title) or _looks_like_query_intro(title):
        return None

    filtered_lines = []
    for line in lines:
        clean = _clean_text(line)
        if not clean:
            continue
        if _looks_like_query_intro(clean):
            continue
        filtered_lines.append(clean)

    if not filtered_lines:
        return None

    summary_lines = []
    reason_lines = []

    start_index = 1

    for line in filtered_lines[start_index:]:
        clean = _clean_text(line)
        if not clean:
            continue
        lower = clean.lower()
        if any(token in lower for token in ["why", "matches", "fits", "perfect for", "good for", "works for", "reason"]):
            reason_lines.append(clean)
        else:
            summary_lines.append(clean)

    if not reason_lines and len(summary_lines) >= 2:
        reason_lines = [summary_lines.pop()]

    summary = " ".join(summary_lines) if summary_lines else "This pick matches your requested vibe and story energy."
    reason = " ".join(reason_lines) if reason_lines else "It aligns with your mood, pacing, and thematic preferences."

    return title, summary, reason


def render_recommendations(response: str):
    if not response or not response.strip():
        st.warning("The recommendation engine returned an empty result. Try a broader prompt.")
        return

    context_label = st.session_state.get("last_query", "")
    if not context_label:
        context_label = "your current vibe"
    context_label = html.escape(context_label)

    st.markdown(
        f"<div class='context-banner'>Similar to <strong>{context_label}</strong></div>",
        unsafe_allow_html=True,
    )
    blocks = []
    current = []

    for line in response.splitlines():
        clean = line.strip()
        if not clean:
            continue

        if _recommendation_number(clean):
            if current:
                blocks.append("\n".join(current))
            current = [clean]
            continue

        if current:
            current.append(clean)

    if current:
        blocks.append("\n".join(current))

    valid_blocks = []
    for block in blocks:
        parsed = _split_recommendation_block(block)
        if parsed is None:
            continue
        title, summary, reason = parsed
        valid_blocks.append((title, summary, reason))

    if not valid_blocks:
        st.warning("The engine produced a query summary instead of actual recommendations. Please try a more specific anime prompt.")
        return

    for index, (title, summary, reason) in enumerate(valid_blocks, start=1):
        st.markdown(
            f"""
            <div class="recommendation-card">
                <div class="reco-header">
                    <div class="reco-badge">{index}</div>
                    <h4 class="reco-title">{title}</h4>
                </div>
                <div class="reco-section">
                    <div class="reco-label">Synopsis</div>
                    <div>{summary}</div>
                </div>
                <div class="reco-section">
                    <div class="reco-label">Why it fits</div>
                    <div>{reason}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption("Recommendations are tailored to your vibe, tone, and story preferences.")


def main():
    load_css()

    st.markdown(
        """
        <div class='compact-header'>
            <div>
                <h1>Anime Matchmaker</h1>
                <p>Find your next watch by mood, genre, and story energy.</p>
            </div>
            <div class='mini-label'>Curated discovery</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sample_prompts = [
        "Action-packed anime with a strong rival dynamic",
        "Cozy school romance with a warm emotional tone",
        "Dark fantasy with mystery and powerful worldbuilding",
        "Funny but emotional anime with a found-family vibe",
    ]

    query_col, options_col, action_col = st.columns([2.2, 1.25, 0.75], vertical_alignment="bottom")
    with query_col:
        query = st.text_area(
            "Describe the anime you want",
            height=96,
            value=st.session_state.get("last_query", ""),
            placeholder="Try: heartwarming school slice-of-life with a satisfying ending",
            key="query_input",
            label_visibility="visible",
        )
    with options_col:
        st.markdown("<div class='mini-label'>Quick start</div>", unsafe_allow_html=True)
        selected_prompt = st.selectbox(
            "Choose a vibe",
            ["Pick a prompt..."] + sample_prompts,
            key="quick_prompt",
            on_change=apply_quick_prompt,
            label_visibility="collapsed",
        )
        if selected_prompt != "Pick a prompt...":
            query = selected_prompt
    with action_col:
        submit = st.button("Get recommendations", type="primary", use_container_width=True)
        clear = st.button("Clear", use_container_width=True, on_click=clear_query)

    with st.expander("Prompt library and recommendation signals", expanded=False):
        prompt_cols = st.columns(4)
        for column, prompt in zip(prompt_cols, sample_prompts):
            with column:
                st.caption(prompt)
        st.markdown(
            "<div class='chip'>Mood-aware</div><div class='chip'>Genre fit</div>"
            "<div class='chip'>Story energy</div><div class='chip'>Minimal UI</div>",
            unsafe_allow_html=True,
        )

    if submit and query.strip():
        st.session_state.last_query = query.strip()
        with st.spinner("Curating a shortlist for you..."):
            try:
                pipeline = init_pipeline()
                response = pipeline.recommend(query.strip())
                render_recommendations(response)
            except Exception as exc:
                st.error("The recommendation engine is unavailable right now.")
                st.info("Check that your GROQ API key is valid and the vector database exists in the project.")
                st.exception(exc)
    elif submit and not query.strip():
        st.warning("Please describe the anime vibe you're looking for before searching.")

if __name__ == "__main__":
    main()


