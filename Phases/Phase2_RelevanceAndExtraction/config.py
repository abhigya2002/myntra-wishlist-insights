"""Phase 2 paths and Groq key loading. Never print the key."""

from __future__ import annotations

import os
from pathlib import Path

PHASE2_DIR = Path(__file__).resolve().parent
PHASES_DIR = PHASE2_DIR.parent
PROJECT_DIR = PHASES_DIR.parent
PHASE0_DIR = PHASES_DIR / "Phase0_CorpusDesign"
PHASE1_RAW = PHASES_DIR / "Phase1_RedditIngest" / "data" / "raw" / "reddit_documents.jsonl"

DATA_DIR = PHASE2_DIR / "data"
LABELED_PATH = DATA_DIR / "labeled" / "reddit_labeled.jsonl"
CLAIMS_PATH = DATA_DIR / "claims" / "reddit_claims.jsonl"
CACHE_PATH = DATA_DIR / "cache" / "groq_raw.jsonl"
LEGACY_CACHE_PATH = DATA_DIR / "cache" / "gemini_raw.jsonl"
SAMPLE_PATH = DATA_DIR / "eval" / "gate_sample.jsonl"
EVAL_NOTES_PATH = DATA_DIR / "eval" / "GATE_CHECK.md"
MANIFEST_PATH = DATA_DIR / "manifest.json"

ENV_SEARCH_PATHS = (
    PHASE2_DIR / ".env",
    PHASE2_DIR / "groq.local",
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
    load_dotenv()
    if _file_token:
        return _file_token
    for name in _KEY_NAMES:
        key = (os.environ.get(name) or "").strip()
        if key:
            return key
    return None


def groq_model() -> str:
    load_dotenv()
    return (os.environ.get("GROQ_MODEL") or DEFAULT_MODEL).strip()


def key_status() -> str:
    return "set" if groq_api_key() else "missing"
