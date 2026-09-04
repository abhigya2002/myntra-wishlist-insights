"""Relevance gate + quote-backed claims on store reviews."""

from __future__ import annotations

import re
import sys
from typing import Any

from config import IN_SCOPE_LABELS, PHASE2_DIR, STORE_KEYWORDS

if str(PHASE2_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE2_DIR))

from schema import (  # noqa: E402
    MIN_QUOTE_LEN,
    document_text,
    recover_verbatim_quote,
    sanitize_claim,
    sanitize_label,
)

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")

STORE_PATTERNS: list[tuple[re.Pattern[str], list[int], str, str]] = [
    (re.compile(r"\bwishlist\b", re.I), [1, 8], "bookmark_not_intent", "why_add"),
    (re.compile(r"\b(save for later|bookmark|save.*later)\b", re.I), [1, 8], "bookmark_not_intent", "why_add"),
    (re.compile(r"\b(size chart|runs small|sizing|too small|too big|wrong size)\b", re.I), [3, 7], "size_inconsistency", "uncertainty_after_like"),
    (re.compile(r"\b(fit|doesn't fit|does not fit|fitting)\b", re.I), [2, 3, 7], "fit_uncertainty", "uncertainty_after_like"),
    (re.compile(r"\b(quality|cheap|fake|duplicate|not original)\b", re.I), [2, 3], "quality_doubt", "uncertainty_after_like"),
    (re.compile(r"\b(review|reviews|fake review)\b", re.I), [3, 7], "review_trust", "uncertainty_after_like"),
    (re.compile(r"\b(return|refund|pickup|try and buy|try & buy|replacement)\b", re.I), [2, 3, 4], "returns_safety_net", "uncertainty_after_like"),
    (re.compile(r"\b(delivery|delivered|not delivered|late|delay|ekart)\b", re.I), [2, 4], "returns_safety_net", "postpone"),
    (re.compile(r"\b(sale|price drop|eors|discount|expensive)\b", re.I), [4, 8], "price_uncertainty", "postpone"),
    (re.compile(r"\b(crash|login|otp|notification|app.*(slow|hang|freeze))\b", re.I), [2, 10], "unmet_need", "unmet_need"),
]


def store_gate(doc: dict[str, Any]) -> tuple[str, str]:
    source = doc.get("source")
    if source in {"play_store", "app_store"}:
        text = document_text(doc)
        if len(text.strip()) < 8:
            return "noise", "Empty store review."
        return "myntra_primary", "Public review of the Myntra mobile app."
    return "noise", "Not a store review."


def heuristic_extract(doc: dict[str, Any], label: str) -> list[dict[str, Any]]:
    if label not in IN_SCOPE_LABELS:
        return []
    text = document_text(doc)
    sentences = [part.strip() for part in SENTENCE_RE.split(text) if part and part.strip()]
    if not sentences and len(text) >= MIN_QUOTE_LEN:
        sentences = [text]
    claims: list[dict[str, Any]] = []
    seen: set[str] = set()
    for sentence in sentences:
        if len(sentence) < MIN_QUOTE_LEN:
            continue
        for pattern, qids, theme, stage in STORE_PATTERNS:
            if not pattern.search(sentence):
                continue
            recovered = recover_verbatim_quote(sentence, doc)
            if not recovered or recovered.lower() in seen:
                continue
            raw = {
                "quote": recovered,
                "discovery_question_ids": qids,
                "theme": theme,
                "wishlist_signal": "explicit" if re.search(r"\bwishlist\b", recovered, re.I) else "none",
                "stage": stage,
                "segment_signals": [],
                "delay_or_dropoff_signal": "yes"
                if theme in {"sale_waiting", "fit_uncertainty", "quality_doubt", "returns_safety_net", "price_uncertainty"}
                else "unclear",
                "price_mentioned": bool(re.search(r"\b(price|sale|discount|rs\.?|₹)\b", recovered, re.I)),
                "non_monetary_need": {
                    "fit_uncertainty": "fit",
                    "size_inconsistency": "size",
                    "review_trust": "reviews",
                    "returns_safety_net": "other",
                }.get(theme),
                "confidence": "low",
            }
            claim = sanitize_claim(raw, doc, extractor="heuristic")
            if claim:
                seen.add(claim["quote"].lower())
                claims.append(claim)
            break
        if len(claims) >= 2:
            break
    return claims


def extract_document(doc: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    label, rationale = store_gate(doc)
    labeled = {
        "id": doc["id"],
        "url": doc.get("url") or "",
        "source": doc.get("source"),
        "title": doc.get("title") or "",
        "label": sanitize_label(label) or "noise",
        "gate_rationale": rationale,
        "extractor": "heuristic",
        "store": (doc.get("raw_metadata") or {}).get("store"),
        "rating": (doc.get("raw_metadata") or {}).get("rating"),
        "created_at": doc.get("created_at"),
        "keyword_hits": (doc.get("raw_metadata") or {}).get("keyword_hits") or [],
    }
    claims: list[dict[str, Any]] = []
    if labeled["label"] not in IN_SCOPE_LABELS:
        return labeled, claims
    for index, claim in enumerate(heuristic_extract(doc, labeled["label"]), start=1):
        claim["claim_id"] = f"{doc['id']}__s{index}"
        claim["gate_label"] = labeled["label"]
        claim["source"] = doc.get("source")
        claims.append(claim)
    return labeled, claims


def keyword_doc_count(docs: list[dict[str, Any]]) -> dict[str, int]:
    counts = {token: 0 for token in STORE_KEYWORDS}
    for doc in docs:
        hits = (doc.get("raw_metadata") or {}).get("keyword_hits") or []
        for token in hits:
            if token in counts:
                counts[token] += 1
    return counts
