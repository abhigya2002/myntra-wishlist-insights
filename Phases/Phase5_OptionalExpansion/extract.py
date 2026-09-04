"""Relevance gate + quote-backed claims for the Phase 5 wishlist sweep.

Aimed at the two open questions: Q1 (why add) and Q8 (intent vs bookmark).
Every claim carries a `wishlist_facet` so the report can separate the three
things that get conflated: adding, parking, and actually buying.
"""

from __future__ import annotations

import re
import sys
from typing import Any

from config import IN_SCOPE_LABELS, PHASE2_DIR

if str(PHASE2_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE2_DIR))

from schema import (  # noqa: E402
    MIN_QUOTE_LEN,
    document_text,
    recover_verbatim_quote,
    sanitize_claim,
    sanitize_label,
)

WISHLIST_RE = re.compile(r"\b(wishlist|wish list|saved item|save(d)? for later|shortlist)\b", re.I)
MYNTRA_RE = re.compile(r"\bmyntra\b", re.I)
BOT_RE = re.compile(
    r"(i am a bot|automoderator|this action was performed automatically|"
    r"contact the moderators|join .{0,15}discord)",
    re.I,
)

# facet -> (pattern, question ids, schema theme, stage, delay signal)
# Ordered by priority: the first facet that matches a document wins that quote.
FACET_PATTERNS: list[tuple[str, re.Pattern[str], list[int], str, str, str]] = [
    (
        "ceiling",
        re.compile(
            r"(wishlist is full|list is full|can'?t add (any )?more|cannot add more|"
            r"reached the limit|hit the limit|maximum of \d+|limit of \d+|1000 items?|"
            r"too many (items|things|clothes)|(wishlist|list) is (getting )?(too )?(long|big|huge)|"
            r"unmanageable|delete (something|items) to add|so many (items|things) saved)",
            re.I,
        ),
        [8],
        "bookmark_not_intent",
        "why_add",
        "yes",
    ),
    (
        "archive",
        re.compile(
            r"(never (actually )?(buy|bought|wear|order)|never end up buying|"
            r"forget (about )?(it|them|what|that)|just (browsing|looking|window shopping)|"
            r"window shopping|clean(ing|ed)? (out )?(my|the) (wishlist|list)|"
            r"clear(ed|ing)? (out )?(my|the) (wishlist|list)|empt(y|ying) (my|your|their) wishlist|"
            r"leak your wishlist|share (your|me) .{0,20}(cart|wishlist)|from your wishlist|"
            r"for inspiration|inspo\b|aspirational|"
            r"(half|most|some) (the|of the|of my) (clothes|things|items) I save|"
            r"not for anything I actually|based on future|future version|"
            r"for a life I|sitting (in|there|on) .{0,20}(months|years)|"
            r"been (in|on) my (wishlist|cart) for|"
            r"(save|saving|add|adding) .{0,30}(and|then) (forget|never))",
            re.I,
        ),
        [1, 8],
        "bookmark_not_intent",
        "why_add",
        "yes",
    ),
    (
        "intent",
        re.compile(
            r"(finally (bought|ordered|got)|ended up buying|"
            r"(bought|got|took|taken|ordered|picked) .{0,25}from (my|her|his|their) wishlist|"
            r"waiting for (it|this|them) to go on sale|will buy (it )?(when|once)|"
            r"planning to (buy|order)|about to order|moved? (it )?to (my )?cart)",
            re.I,
        ),
        [1, 8],
        "bookmark_not_intent",
        "why_add",
        "unclear",
    ),
    (
        "sale_park",
        re.compile(
            r"(wait(ing)? for (the )?(sale|eors|big fashion festival)|price drop|"
            r"during the sale|until the sale)",
            re.I,
        ),
        [4, 8],
        "sale_waiting",
        "postpone",
        "yes",
    ),
    (
        "why_add",
        re.compile(
            r"(add(ed|ing)? (it )?to (my )?wishlist|put it (in|on) my wishlist|"
            r"saving (it|this|them) for|making (a )?wishlist|"
            r"(in|on|from) (my|your|her|his|their) wishlist|"
            r"(use|used) to wishlist|wishlist stuff)",
            re.I,
        ),
        [1],
        "bookmark_not_intent",
        "why_add",
        "unclear",
    ),
    (
        "fit_block",
        re.compile(r"(size chart|runs small|sizing|don'?t trust (the )?size|too small|too big)", re.I),
        [2, 3, 7],
        "size_inconsistency",
        "uncertainty_after_like",
        "yes",
    ),
    (
        "compare_block",
        re.compile(r"(which one|help me (choose|pick|decide)|recommendations?|\brecs\b|opinions)", re.I),
        [5],
        "comparison",
        "compare",
        "unclear",
    ),
]

MAX_CLAIMS_PER_DOC = 3
QUOTE_WIDTH = 260


def gate(doc: dict[str, Any]) -> tuple[str, str]:
    """Wishlist behaviour is in scope even when Myntra is not named."""
    text = document_text(doc)
    if len(text.strip()) < MIN_QUOTE_LEN:
        return "noise", "Too short to support a quote."
    if BOT_RE.search(text):
        return "noise", "Automated moderator or promo comment."
    if MYNTRA_RE.search(text):
        return "myntra_primary", "Names Myntra in a wishlist-sweep document."
    meta = doc.get("raw_metadata") or {}
    if WISHLIST_RE.search(text):
        return "fashion_context", "Wishlist or save-for-later behaviour without naming Myntra."
    if meta.get("in_wishlist_thread"):
        return "fashion_context", "Comment inside a wishlist thread."
    return "noise", "No Myntra and no wishlist behaviour."


def _window(text: str, start: int, end: int, width: int = QUOTE_WIDTH) -> str:
    """A readable span around a match. Reddit posts are often one run-on sentence."""
    lo = max(0, start - width // 3)
    hi = min(len(text), end + width)
    if lo > 0:
        space = text.find(" ", lo)
        if 0 <= space < start:
            lo = space + 1
    if hi < len(text):
        space = text.rfind(" ", end, hi)
        if space > end:
            hi = space
    return text[lo:hi].strip()


def _match_scope(doc: dict[str, Any]) -> str:
    """Match inside the document's own words.

    `document_text` appends `thread_context`, which for a comment is the parent
    post title. Matching against that makes quotes trail off into a repeated
    title, so comments match on their body alone. Recovery still runs against
    the full document, so the quote stays verbatim.
    """
    body = str(doc.get("body") or "").strip()
    title = str(doc.get("title") or "").strip()
    kind = (doc.get("raw_metadata") or {}).get("kind")
    if kind == "comment":
        return body or document_text(doc)
    return (f"{title}\n{body}".strip() if title else body) or document_text(doc)


def heuristic_extract(doc: dict[str, Any], label: str) -> list[dict[str, Any]]:
    if label not in IN_SCOPE_LABELS:
        return []
    text = _match_scope(doc)
    if len(text.strip()) < MIN_QUOTE_LEN:
        return []

    claims: list[dict[str, Any]] = []
    seen: set[str] = set()
    for facet, pattern, qids, theme, stage, delay in FACET_PATTERNS:
        if len(claims) >= MAX_CLAIMS_PER_DOC:
            break
        match = pattern.search(text)
        if not match:
            continue
        span = _window(text, match.start(), match.end())
        recovered = recover_verbatim_quote(span, doc)
        if not recovered or recovered.lower() in seen:
            continue
        raw = {
            "quote": recovered,
            "discovery_question_ids": qids,
            "theme": theme,
            "wishlist_signal": "explicit" if WISHLIST_RE.search(recovered) else "implied",
            "stage": stage,
            "segment_signals": [],
            "delay_or_dropoff_signal": delay,
            "price_mentioned": bool(re.search(r"\b(price|sale|discount|rs\.?|₹)\b", recovered, re.I)),
            "non_monetary_need": {
                "size_inconsistency": "size",
                "comparison": "comparison",
            }.get(theme),
            "confidence": "low",
        }
        claim = sanitize_claim(raw, doc, extractor="heuristic")
        if claim:
            claim["wishlist_facet"] = facet
            seen.add(claim["quote"].lower())
            claims.append(claim)
    return claims


def extract_document(doc: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    label, rationale = gate(doc)
    meta = doc.get("raw_metadata") or {}
    labeled = {
        "id": doc["id"],
        "url": doc.get("url") or "",
        "source": doc.get("source"),
        "title": doc.get("title") or "",
        "label": sanitize_label(label) or "noise",
        "gate_rationale": rationale,
        "extractor": "heuristic",
        "subreddit": meta.get("subreddit"),
        "query_id": meta.get("query_id"),
        "created_at": doc.get("created_at"),
    }
    claims: list[dict[str, Any]] = []
    if labeled["label"] not in IN_SCOPE_LABELS:
        return labeled, claims
    for index, claim in enumerate(heuristic_extract(doc, labeled["label"]), start=1):
        claim["claim_id"] = f"{doc['id']}__p5c{index}"
        claim["gate_label"] = labeled["label"]
        claim["source"] = doc.get("source")
        claims.append(claim)
    return labeled, claims


def facet_counts(claims: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for claim in claims:
        facet = str(claim.get("wishlist_facet") or "unfaceted")
        counts[facet] = counts.get(facet, 0) + 1
    return counts
