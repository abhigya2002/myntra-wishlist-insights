"""Labels, claim schema, and fail-closed quote checks."""

from __future__ import annotations

import re
from typing import Any

GATE_LABELS = ("myntra_primary", "fashion_context", "competitor_only", "noise")
IN_SCOPE_LABELS = {"myntra_primary", "fashion_context"}

STAGES = (
    "why_add",
    "uncertainty_after_like",
    "postpone",
    "compare",
    "off_platform",
    "unmet_need",
)
THEMES = (
    "fit_uncertainty",
    "size_inconsistency",
    "sale_waiting",
    "bookmark_not_intent",
    "quality_doubt",
    "review_trust",
    "comparison",
    "off_platform_research",
    "occasion_delay",
    "styling_uncertainty",
    "social_proof",
    "returns_safety_net",
    "price_uncertainty",
    "unmet_need",
    "other",
)
WISHLIST_SIGNALS = ("explicit", "implied", "none")
DELAY_SIGNALS = ("yes", "no", "unclear")
NON_MONETARY = (
    "fit",
    "size",
    "styling",
    "reviews",
    "occasion",
    "social_proof",
    "comparison",
    "other",
)
SEGMENT_HYPOTHESES = (
    "ethnic_vs_western",
    "first_time_vs_repeat",
    "sale_waiter_vs_occasion_buyer",
    "metro_vs_rest_of_india",
    "size_insecure_vs_size_confident",
)

QUESTION_IDS = set(range(1, 11))
MIN_QUOTE_LEN = 12

_WS = re.compile(r"\s+")


def document_text(doc: dict[str, Any]) -> str:
    parts = [doc.get("title") or "", doc.get("body") or "", doc.get("thread_context") or ""]
    return "\n".join(part for part in parts if part)


def normalize_ws(text: str) -> str:
    return _WS.sub(" ", text or "").strip()


def recover_verbatim_quote(quote: str, doc: dict[str, Any]) -> str | None:
    """Return the quote as it appears in the document, or None (fail closed)."""
    needle = normalize_ws(quote or "")
    if len(needle) < MIN_QUOTE_LEN:
        return None
    haystack_raw = document_text(doc)
    haystack = normalize_ws(haystack_raw)
    if not haystack:
        return None
    idx = haystack.lower().find(needle.lower())
    if idx < 0:
        return None
    recovered = haystack[idx : idx + len(needle)]
    return recovered.strip()


def sanitize_label(value: Any) -> str | None:
    label = str(value or "").strip().lower()
    return label if label in GATE_LABELS else None


def sanitize_claim(raw: dict[str, Any], doc: dict[str, Any], *, extractor: str) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    quote = recover_verbatim_quote(str(raw.get("quote") or ""), doc)
    if not quote:
        return None
    qids = []
    for item in raw.get("discovery_question_ids") or []:
        try:
            qid = int(item)
        except (TypeError, ValueError):
            continue
        if qid in QUESTION_IDS and qid not in qids:
            qids.append(qid)
    if not qids:
        return None
    theme = str(raw.get("theme") or "other").strip().lower().replace(" ", "_")
    if theme not in THEMES:
        theme = "other"
    stage = str(raw.get("stage") or "").strip().lower().replace(" ", "_")
    if stage not in STAGES:
        stage = "unmet_need"
    wishlist = str(raw.get("wishlist_signal") or "none").strip().lower()
    if wishlist not in WISHLIST_SIGNALS:
        wishlist = "none"
    delay = str(raw.get("delay_or_dropoff_signal") or "unclear").strip().lower()
    if delay not in DELAY_SIGNALS:
        delay = "unclear"
    segments = []
    for item in raw.get("segment_signals") or []:
        token = str(item).strip().lower().replace(" ", "_")
        if token in SEGMENT_HYPOTHESES and token not in segments:
            segments.append(token)
    non_mon = str(raw.get("non_monetary_need") or "").strip().lower().replace(" ", "_")
    if non_mon not in NON_MONETARY:
        non_mon = None
    confidence = str(raw.get("confidence") or "medium").strip().lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "medium"
    if extractor == "heuristic":
        confidence = "low"
    price = raw.get("price_mentioned")
    return {
        "quote": quote,
        "discovery_question_ids": qids,
        "theme": theme,
        "wishlist_signal": wishlist,
        "stage": stage,
        "segment_signals": segments,
        "delay_or_dropoff_signal": delay,
        "price_mentioned": bool(price) if isinstance(price, bool) else ("price" in quote.lower() or "sale" in quote.lower()),
        "non_monetary_need": non_mon,
        "confidence": confidence,
        "extractor": extractor,
        "quote_verified": True,
        "doc_id": doc["id"],
        "url": doc.get("url") or "",
    }
