"""Keep Phase 1 ingest on Myntra. Competitors are comparison-only."""

from __future__ import annotations

import re

MYNTRA_RE = re.compile(r"\bmyntra\b", re.IGNORECASE)
COMPETITOR_RE = re.compile(
    r"\b(ajio|nykaa|nykaa\s*fashion|meesho|ajio\.com|nykaafashion)\b",
    re.IGNORECASE,
)


def mentions_myntra(*parts: str | None) -> bool:
    blob = " ".join(part or "" for part in parts)
    return bool(MYNTRA_RE.search(blob))


def competitor_only(*parts: str | None) -> bool:
    blob = " ".join(part or "" for part in parts)
    return bool(COMPETITOR_RE.search(blob)) and not MYNTRA_RE.search(blob)


def ensure_myntra_query(query: str) -> str:
    """ReviewLens prefixed Spotify queries with the product name. Same here."""
    cleaned = query.strip()
    if MYNTRA_RE.search(cleaned):
        return cleaned
    return f"myntra {cleaned}"


def keep_document(
    *,
    title: str,
    body: str,
    url: str = "",
    thread_context: str = "",
    in_myntra_thread: bool = False,
) -> bool:
    """Submissions and standalone comments must name Myntra.

    Comments on an already-accepted Myntra thread are in-product even if they
    never repeat the brand (e.g. 'runs small'). Competitor-only text is dropped.
    """
    parts = (title, body, url, thread_context)
    if competitor_only(*parts):
        return False
    if in_myntra_thread:
        return True
    return mentions_myntra(*parts)
