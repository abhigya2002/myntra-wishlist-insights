"""Streamlit Ask + Pulse UI — Myntra Stitch design system."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

import config
from chat import answer
from pulse import build_pulse_markdown, write_pulse
from retrieve import clear_cache

APP_DIR = Path(__file__).resolve().parent
ASSETS = APP_DIR / "assets"
LOGO_PATH = ASSETS / "myntra-m.png"

# Honest research prompts (no invented observation counts)
RESEARCH_SIGNALS = [
    {
        "icon": "◇",
        "title": "Intent vs bookmark",
        "prompt": "Why do people add to the Myntra wishlist — intent to buy or bookmark/archive?",
        "meta": "Q1 / Q8 · wishlist facets",
    },
    {
        "icon": "∥",
        "title": "Fit uncertainty",
        "prompt": "How does fit and size uncertainty block purchase after an item is wishlisted or shortlisted?",
        "meta": "ranked: fit_size_uncertainty",
    },
    {
        "icon": "↺",
        "title": "Returns distrust",
        "prompt": "How does return and order-integrity distrust train delay between wishlist add and buy?",
        "meta": "ranked: returns_and_order_trust",
    },
    {
        "icon": "↓",
        "title": "Sale wait",
        "prompt": "What evidence is there that shoppers park items on wishlist waiting for a sale or price drop?",
        "meta": "facet: sale_park",
    },
]


def _logo_data_uri() -> str:
    if not LOGO_PATH.is_file():
        return ""
    raw = LOGO_PATH.read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def _inject_css() -> None:
    """Inject theme via st.html so CSS is not stripped into visible page text."""
    css_path = ASSETS / "theme.css"
    css = css_path.read_text(encoding="utf-8") if css_path.is_file() else ""
    # Fonts + styles in one HTML payload (applies to parent document).
    st.html(
        "<link rel='preconnect' href='https://fonts.googleapis.com'/>"
        "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin/>"
        "<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700"
        "&family=Montserrat:wght@600;700&display=swap' rel='stylesheet'/>"
        f"<style>{css}</style>"
    )


def _render_header(active: str, corpus_ok: bool, groq_ok: bool) -> None:
    logo = _logo_data_uri()
    logo_html = (
        f'<img src="{logo}" alt="Myntra"/>'
        if logo
        else '<div style="width:36px;height:36px;border-radius:8px;background:linear-gradient(135deg,#FF3E6C,#F26A2E);"></div>'
    )
    ask_cls = "wi-tab wi-tab-active" if active == "ask" else "wi-tab"
    pulse_cls = "wi-tab wi-tab-active" if active == "pulse" else "wi-tab"
    corpus_chip = (
        '<span class="wi-chip"><span class="wi-dot"></span>Corpus ready</span>'
        if corpus_ok
        else '<span class="wi-chip">Corpus missing</span>'
    )
    groq_chip = (
        '<span class="wi-chip">Groq connected</span>'
        if groq_ok
        else '<span class="wi-chip">Groq missing</span>'
    )
    st.markdown(
        f"""
<div class="wi-header">
  <div class="wi-brand">
    {logo_html}
    <div class="wi-brand-text">
      <span class="wi-brand-title">Wishlist Insights</span>
      <span class="wi-brand-sub">Internal · Public-signal discovery</span>
    </div>
  </div>
  <div class="wi-tabs">
    <span class="{ask_cls}">Ask</span>
    <span class="{pulse_cls}">Pulse</span>
  </div>
  <div class="wi-status">
    {corpus_chip}
    {groq_chip}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _ensure_index() -> bool:
    if config.INDEX_PATH.is_file():
        return True
    st.warning("Index missing. Rebuild from the sidebar or run `python build_index.py`.")
    return False


def _render_sources(sources: list) -> None:
    if not sources:
        return
    with st.expander("Verified citations / sources", expanded=False):
        for s in sources:
            cid = s.get("claim_id") or s.get("id")
            url = s.get("url") or ""
            layer = s.get("layer")
            score = s.get("score")
            preview = (s.get("text") or "")[:240]
            link = f"[open]({url})" if url else "_no url_"
            st.markdown(
                f"**`{cid}`** · layer=`{layer}` · score=`{score}`  \n"
                f"{preview}  \n"
                f"{link}"
            )


def _handle_prompt(prompt: str) -> None:
    if not _ensure_index():
        return
    st.session_state.messages.append({"role": "user", "content": prompt})
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
        if m["role"] in {"user", "assistant"}
    ]
    with st.spinner("Retrieving + synthesizing…"):
        result = answer(prompt, history=history)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources") or [],
        }
    )


# --- Page bootstrap ---
st.set_page_config(
    page_title="Wishlist Insights",
    page_icon="🩷",
    layout="wide",
    initial_sidebar_state="expanded",
)

_inject_css()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "view" not in st.session_state:
    st.session_state.view = "ask"
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

corpus_ok = config.INDEX_PATH.is_file()
groq_ok = config.key_status() == "set"

# Sidebar — workspaces + signals + controls
with st.sidebar:
    st.markdown("### Workspaces")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("RAG Studio", use_container_width=True, type="primary" if st.session_state.view == "ask" else "secondary"):
            st.session_state.view = "ask"
            st.rerun()
    with c2:
        if st.button("Pulse", use_container_width=True, type="primary" if st.session_state.view == "pulse" else "secondary"):
            st.session_state.view = "pulse"
            st.rerun()

    st.markdown("---")
    st.markdown("### Research signals")
    for i, sig in enumerate(RESEARCH_SIGNALS):
        label = f"{sig['icon']}  {sig['title']}\n{sig['meta']}"
        if st.button(label, key=f"sig_{i}", use_container_width=True):
            st.session_state.view = "ask"
            st.session_state.pending_prompt = sig["prompt"]
            st.rerun()

    st.markdown("---")
    st.markdown("### Index & controls")
    st.caption(f"Groq: **{config.key_status()}** · Index: **{'ready' if corpus_ok else 'missing'}**")
    if st.button("Rebuild BM25 index", use_container_width=True):
        with st.spinner("Building index…"):
            from build_index import build_chunks, write_index

            chunks = build_chunks()
            write_index(chunks)
            clear_cache()
        st.success(f"Wrote {len(chunks)} chunks")
        st.rerun()
    if st.button("Regenerate Pulse", use_container_width=True):
        with st.spinner("Writing pulse-report.md…"):
            path = write_pulse(use_llm_blurb=True)
        st.success(f"Wrote {path.name}")
        st.rerun()

_render_header(st.session_state.view, corpus_ok, groq_ok)

# Pending research-signal click
if st.session_state.pending_prompt and st.session_state.view == "ask":
    pending = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    _handle_prompt(pending)
    st.rerun()

if st.session_state.view == "ask":
    if not st.session_state.messages:
        logo = _logo_data_uri()
        logo_tag = f'<img src="{logo}" alt="Myntra"/>' if logo else ""
        st.markdown(
            f"""
<div class="wi-hero">
  {logo_tag}
  <h1>Ask about wishlist behaviour</h1>
  <p>Blockers, intent vs bookmark, public opinion — grounded in the Part 1 discovery freeze. Answers cite claim_id / URL.</p>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="wi-section-label">Try a research signal from the left rail</div>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role = msg["role"]
        with st.chat_message(role):
            if role == "assistant":
                st.caption("Grounded synthesis · Part 1 corpus")
            st.markdown(msg["content"])
            if msg.get("sources"):
                _render_sources(msg["sources"])

    prompt = st.chat_input("Ask about wishlist behaviour, blockers, or public opinion…")
    if prompt:
        _handle_prompt(prompt)
        st.rerun()

else:
    report_path = config.PULSE_REPORT_PATH
    if report_path.is_file():
        md = report_path.read_text(encoding="utf-8-sig")
    else:
        with st.spinner("Generating pulse…"):
            md = build_pulse_markdown(use_llm_blurb=False)
            config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            report_path.write_text(md, encoding="utf-8")

    # Report first (executive snapshot at top of viewport)
    st.markdown(md)

    st.markdown("---")
    a, b = st.columns([1, 1])
    with a:
        if st.button("Regenerate Pulse", use_container_width=True):
            with st.spinner("Writing pulse-report.md…"):
                write_pulse(use_llm_blurb=True)
            st.rerun()
    with b:
        st.download_button(
            "Download .md",
            data=md,
            file_name="pulse-report.md",
            mime="text/markdown",
            use_container_width=True,
        )
