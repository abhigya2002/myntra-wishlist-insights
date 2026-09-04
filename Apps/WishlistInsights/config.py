"""Paths and Groq env for WishlistInsights. Never print the API key."""

from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
APPS_DIR = APP_DIR.parent
PROJECT_DIR = APPS_DIR.parent
PHASES_DIR = PROJECT_DIR / "Phases"

# Phase 6 freeze (canonical Part 1 sign-off)
PHASE6_DIR = PHASES_DIR / "Phase6_SignOff"
PHASE6_OUTPUT = PHASE6_DIR / "output"
FREEZE_REPORT = PHASE6_OUTPUT / "discovery-report.md"
FREEZE_LEDGER = PHASE6_OUTPUT / "evidence-ledger.json"
FREEZE_META = PHASE6_OUTPUT / "freeze.json"

# Phase 5 derived + claims + expansion raw
PHASE5_DIR = PHASES_DIR / "Phase5_OptionalExpansion"
PHASE5_DATA = PHASE5_DIR / "data"
PHASE5_CLAIMS = PHASE5_DATA / "claims" / "combined_claims.jsonl"
PHASE5_DERIVED = PHASE5_DATA / "derived"
RANKING_PATH = PHASE5_DERIVED / "ranking.json"
QUESTIONS_PATH = PHASE5_DERIVED / "questions.json"
WISHLIST_EVIDENCE_PATH = PHASE5_DERIVED / "wishlist_evidence.json"
QUANTIFICATION_PATH = PHASE5_DERIVED / "quantification.json"
PHASE5_RAW = PHASE5_DATA / "raw" / "expansion_documents.jsonl"

# Earlier raw corpora
PHASE1_RAW = PHASES_DIR / "Phase1_RedditIngest" / "data" / "raw" / "reddit_documents.jsonl"
PHASE4_RAW = PHASES_DIR / "Phase4_StoreReviews" / "data" / "raw" / "store_reviews.jsonl"

# App artefacts
DATA_DIR = APP_DIR / "data"
INDEX_PATH = DATA_DIR / "index.jsonl"
OUTPUT_DIR = APP_DIR / "output"
PULSE_REPORT_PATH = OUTPUT_DIR / "pulse-report.md"

# Groq — reuse Phase 2 .env pattern
PHASE2_DIR = PHASES_DIR / "Phase2_RelevanceAndExtraction"
ENV_SEARCH_PATHS = (
    PHASE2_DIR / ".env",
    PHASE2_DIR / "groq.local",
    APP_DIR / ".env",
    PROJECT_DIR / ".env",
)

DEFAULT_MODEL = "llama-3.3-70b-versatile"
MODEL_FALLBACKS = (
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
)
_KEY_NAMES = ("GROQ_API_KEY",)
_file_token: str | None = None

# Retrieval
TOP_K = 8
LAYER_BOOST = {
    "claim": 1.35,
    "report": 1.15,
    "derived": 1.20,
    "raw": 1.0,
}

# Chunking
RAW_BODY_MAX = 1200
REPORT_SECTION_MAX = 1800


def _parse_env_text(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if line.lower().startswith("export "):
            line = line[7:].strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            if len(line) >= 20 and "GROQ_API_KEY" not in parsed:
                parsed["GROQ_API_KEY"] = line
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            parsed[key] = value
    return parsed


def _secret_from_streamlit(name: str) -> str | None:
    """Read Streamlit Cloud / local secrets.toml without requiring a running script context."""
    try:
        import streamlit as st

        # st.secrets raises if no secrets file and not on Cloud — catch broadly
        secrets = st.secrets
        if name in secrets:
            value = str(secrets[name]).strip()
            return value or None
    except Exception:
        return None
    return None


def load_dotenv() -> None:
    global _file_token
    for path in ENV_SEARCH_PATHS:
        if not path.is_file():
            continue
        parsed = _parse_env_text(path.read_text(encoding="utf-8-sig"))
        for name in _KEY_NAMES:
            value = (parsed.get(name) or "").strip()
            if value and not _file_token:
                _file_token = value
        for key, value in parsed.items():
            if key in _KEY_NAMES:
                continue
            existing = os.environ.get(key)
            if existing is None or not str(existing).strip():
                os.environ[key] = value


def groq_api_key() -> str | None:
    for name in _KEY_NAMES:
        from_secret = _secret_from_streamlit(name)
        if from_secret:
            return from_secret
    load_dotenv()
    if _file_token:
        return _file_token
    for name in _KEY_NAMES:
        key = (os.environ.get(name) or "").strip()
        if key:
            return key
    return None


def groq_model() -> str:
    from_secret = _secret_from_streamlit("GROQ_MODEL")
    if from_secret:
        return from_secret
    load_dotenv()
    return (os.environ.get("GROQ_MODEL") or DEFAULT_MODEL).strip()


def key_status() -> str:
    return "set" if groq_api_key() else "missing"
