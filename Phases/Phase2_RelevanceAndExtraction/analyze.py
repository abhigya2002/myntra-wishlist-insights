"""Mixed relevance gate + claim extraction (heuristic, Groq when keyed)."""

from __future__ import annotations

import json
import re
from typing import Any

from schema import (
    GATE_LABELS,
    IN_SCOPE_LABELS,
    MIN_QUOTE_LEN,
    document_text,
    recover_verbatim_quote,
    sanitize_claim,
    sanitize_label,
)

try:
    from myntra_filter import competitor_only, mentions_myntra
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Phase1_RedditIngest"))
    from myntra_filter import competitor_only, mentions_myntra

FASHION_RE = re.compile(
    r"\b(wishlist|size chart|runs small|fit|kurta|ethnic|western wear|"
    r"online shopping|haul|try.?on|lehenga|saree|palazzo|occasion|"
    r"wait for sale|end of season|eors)\b",
    re.IGNORECASE,
)
SPAM_RE = re.compile(
    r"\b(chromewebstore|use my (coupon|code)|telegram\.me|whatsapp group join)\b",
    re.IGNORECASE,
)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")

KEYWORD_QUESTIONS: list[tuple[re.Pattern[str], list[int], str, str]] = [
    (re.compile(r"\bwishlist\b", re.I), [1, 8], "bookmark_not_intent", "why_add"),
    (re.compile(r"\b(save for later|bookmark)\b", re.I), [1, 8], "bookmark_not_intent", "why_add"),
    (re.compile(r"\b(wait for sale|price drop|eors|end of season)\b", re.I), [4, 8], "sale_waiting", "postpone"),
    (re.compile(r"\b(size chart|runs small|sizing|too small|too big)\b", re.I), [3, 7], "size_inconsistency", "uncertainty_after_like"),
    (re.compile(r"\b(the fit|bad fit|good fit|poor fit|doesn't fit|does not fit|fit issue)\b", re.I), [2, 3, 7], "fit_uncertainty", "uncertainty_after_like"),
    (re.compile(r"\b(quality|cheap fabric|pilling)\b", re.I), [2, 3], "quality_doubt", "uncertainty_after_like"),
    (re.compile(r"\b(review|reviews)\b", re.I), [3, 6, 7], "review_trust", "off_platform"),
    (re.compile(r"\b(vs ajio|ajio vs|which one|compare)\b", re.I), [5], "comparison", "compare"),
    (re.compile(r"\b(has anyone bought|has anyone ordered|should i buy)\b", re.I), [6, 7], "social_proof", "off_platform"),
    (re.compile(r"\b(wedding|diwali|occasion)\b", re.I), [4, 7, 9], "occasion_delay", "postpone"),
    (re.compile(r"\b(return|try and buy|try & buy)\b", re.I), [2, 3, 4], "returns_safety_net", "uncertainty_after_like"),
]


def heuristic_gate(doc: dict[str, Any]) -> tuple[str, str]:
    title = doc.get("title") or ""
    body = doc.get("body") or ""
    thread = doc.get("thread_context") or ""
    url = doc.get("url") or ""
    meta = doc.get("raw_metadata") or {}
    blob_parts = (title, body, url, thread)
    text = document_text(doc)

    if competitor_only(*blob_parts):
        return "competitor_only", "Names a competitor with no Myntra mention."
    if meta.get("pass_name") == "pass4_thread":
        return "myntra_primary", "Comment on a kept Myntra thread."
    if mentions_myntra(*blob_parts):
        if SPAM_RE.search(text) and "myntra" in text.lower() and len(re.findall(r"\bmyntra\b", text, re.I)) <= 1:
            if "supported sites" in text.lower() or "chromewebstore" in text.lower():
                return "noise", "Myntra named only in a promo/tool site list."
        return "myntra_primary", "Document names Myntra or myntra.com."
    if FASHION_RE.search(text):
        return "fashion_context", "India/online fashion shopping talk without naming Myntra."
    if len(text.strip()) < 40:
        return "noise", "Too short to be shopping-journey evidence."
    return "noise", "No Myntra or fashion-shopping journey signal."


def heuristic_extract(doc: dict[str, Any], label: str) -> list[dict[str, Any]]:
    if label not in IN_SCOPE_LABELS:
        return []
    text = document_text(doc)
    sentences = [s.strip() for s in SENTENCE_RE.split(text) if s and s.strip()]
    claims: list[dict[str, Any]] = []
    seen_quotes: set[str] = set()
    for sentence in sentences:
        if len(sentence) < MIN_QUOTE_LEN:
            continue
        for pattern, qids, theme, stage in KEYWORD_QUESTIONS:
            if not pattern.search(sentence):
                continue
            recovered = recover_verbatim_quote(sentence, doc)
            if not recovered or recovered.lower() in seen_quotes:
                continue
            raw = {
                "quote": recovered,
                "discovery_question_ids": qids,
                "theme": theme,
                "wishlist_signal": "explicit" if re.search(r"\bwishlist\b", recovered, re.I) else "none",
                "stage": stage,
                "segment_signals": [],
                "delay_or_dropoff_signal": "yes" if theme in {"sale_waiting", "fit_uncertainty", "quality_doubt"} else "unclear",
                "price_mentioned": bool(re.search(r"\b(price|sale|discount|rs\.?|₹)\b", recovered, re.I)),
                "non_monetary_need": {
                    "fit_uncertainty": "fit",
                    "size_inconsistency": "size",
                    "styling_uncertainty": "styling",
                    "review_trust": "reviews",
                    "occasion_delay": "occasion",
                    "social_proof": "social_proof",
                    "comparison": "comparison",
                }.get(theme),
                "confidence": "low",
            }
            claim = sanitize_claim(raw, doc, extractor="heuristic")
            if claim:
                seen_quotes.add(claim["quote"].lower())
                claims.append(claim)
            break
        if len(claims) >= 3:
            break
    return claims


def analysis_prompt(doc: dict[str, Any], heuristic_label: str) -> str:
    text = document_text(doc)[:6000]
    meta = doc.get("raw_metadata") or {}
    return f"""You are labeling Reddit evidence for a Myntra Growth discovery engine.
Product under study: Myntra only. AJIO/Nykaa are comparison context, never the protagonist.
North-star metric: % of users who buy at least one wishlisted item within 30 days of adding it.
Do not propose features or discounts.

Step 1 — relevance gate. Choose exactly one label:
- myntra_primary: about using Myntra (named or clearly that app/site)
- fashion_context: India online fashion shopping, no Myntra
- competitor_only: AJIO/Nykaa/Meesho with no Myntra signal
- noise: ads, spam, promo, unrelated, or Myntra mentioned only in a site list

Prefer recall for wishlist, fit, size, postpone, compare, off-platform research, bookmark vs intent.

Heuristic suggestion (you may override): {heuristic_label}

Step 2 — extract 0–4 claims ONLY if label is myntra_primary or fashion_context.
FAIL CLOSED: every claim.quote MUST be a verbatim substring of the document (copy-paste a span).
If you cannot copy a real span, return claims: [].
Do not invent quotes. Do not paraphrase.

Each claim:
- quote: verbatim span from the document
- discovery_question_ids: integers 1-10 from:
  1 why add to Myntra wishlist
  2 what prevents purchase
  3 uncertainty after they like a product
  4 postpone
  5 how they compare shortlisted items
  6 what they seek outside Myntra
  7 fit/size/styling/price/reviews/occasion/social proof
  8 wishlist as intent vs bookmark
  9 segment differences (only if the text supports a segment)
  10 unmet needs
- theme: one of fit_uncertainty, size_inconsistency, sale_waiting, bookmark_not_intent, quality_doubt, review_trust, comparison, off_platform_research, occasion_delay, styling_uncertainty, social_proof, returns_safety_net, price_uncertainty, unmet_need, other
- wishlist_signal: explicit | implied | none
- stage: why_add | uncertainty_after_like | postpone | compare | off_platform | unmet_need
- segment_signals: [] or subset of ethnic_vs_western, first_time_vs_repeat, sale_waiter_vs_occasion_buyer, metro_vs_rest_of_india, size_insecure_vs_size_confident — only if the quote supports it
- delay_or_dropoff_signal: yes | no | unclear
- price_mentioned: boolean
- non_monetary_need: fit | size | styling | reviews | occasion | social_proof | comparison | other | null
- confidence: high | medium | low

Document:
id: {doc.get("id")}
subreddit: {meta.get("subreddit")}
kind: {meta.get("kind")}
url: {doc.get("url")}
text:
\"\"\"
{text}
\"\"\"

Return JSON only:
{{"label": "...", "gate_rationale": "...", "claims": []}}
"""


def merge_llm_result(
    doc: dict[str, Any],
    heuristic_label: str,
    heuristic_reason: str,
    llm: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    label = heuristic_label
    rationale = heuristic_reason
    extractor = "heuristic"
    if llm:
        llm_label = sanitize_label(llm.get("label"))
        if llm_label:
            label = llm_label
            rationale = str(llm.get("gate_rationale") or rationale)
            extractor = "groq"
    labeled = {
        "id": doc["id"],
        "url": doc.get("url") or "",
        "source": doc.get("source") or "reddit",
        "title": doc.get("title") or "",
        "label": label,
        "gate_rationale": rationale,
        "heuristic_label": heuristic_label,
        "extractor": extractor,
        "subreddit": (doc.get("raw_metadata") or {}).get("subreddit"),
        "kind": (doc.get("raw_metadata") or {}).get("kind"),
        "created_at": doc.get("created_at"),
    }
    claims: list[dict[str, Any]] = []
    if label not in IN_SCOPE_LABELS:
        return labeled, claims
    raw_claims = []
    if llm and extractor == "groq":
        raw_claims = llm.get("claims") if isinstance(llm.get("claims"), list) else []
        for index, raw in enumerate(raw_claims):
            claim = sanitize_claim(raw if isinstance(raw, dict) else {}, doc, extractor="groq")
            if claim:
                claim["claim_id"] = f"{doc['id']}__c{index+1}"
                claim["gate_label"] = label
                claims.append(claim)
    if not claims:
        for index, claim in enumerate(heuristic_extract(doc, label), start=1):
            claim["claim_id"] = f"{doc['id']}__h{index}"
            claim["gate_label"] = label
            claims.append(claim)
    return labeled, claims


def cache_key_record(doc_id: str, payload: dict[str, Any]) -> str:
    return json.dumps({"id": doc_id, "payload": payload}, ensure_ascii=False)
