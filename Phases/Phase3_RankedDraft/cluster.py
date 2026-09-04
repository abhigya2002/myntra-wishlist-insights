"""Map Phase 2 claims onto opportunity areas (behaviors, not features)."""

from __future__ import annotations

import re
from typing import Any

from load import normalize_ws

FIT_NOISE_RE = re.compile(r"\b(rate the fit|fit check|party fit)\b", re.I)
OCCASION_FALSE_RE = re.compile(r"\b(ekart|nearby hub|laptop|gift card)\b", re.I)
AFTER_PURCHASE_RE = re.compile(
    r"\b(returned it|refund|cancelled|myncash|pickup|stole my|"
    r"i ordered|received it|got wet|not refunding|quality check|"
    r"filed a complaint|nch portal|not delivering|not delivered)\b",
    re.I,
)
DELIVERY_COMPLAINT_RE = re.compile(
    r"\b(filed a complaint|nch portal|not delivering|not delivered)\b",
    re.I,
)
TITLE_ECHO_MIN = 24

AREAS: dict[str, dict[str, Any]] = {
    "review_thinness": {
        "id": "review_thinness",
        "title": "Thin or conflicting reviews after a product is identified",
        "behavior": (
            "The shopper has already found a candidate on Myntra (or is scrolling Myntra "
            "for a named item) and then stalls because reviews are missing, mixed, or not trusted."
        ),
        "journey_stage": "uncertainty_after_like",
        "monetary": False,
        "metric_prior": 1.0,
        "non_monetary_need": "reviews",
        "themes": ["review_trust"],
    },
    "quality_uncertainty": {
        "id": "quality_uncertainty",
        "title": "Quality and authenticity doubt after shortlisting",
        "behavior": (
            "Users want an item that will last or match the listing, then hesitate or reverse "
            "because fabric, construction, or authenticity looks unreliable."
        ),
        "journey_stage": "uncertainty_after_like",
        "monetary": False,
        "metric_prior": 0.85,
        "non_monetary_need": "other",
        "themes": ["quality_doubt"],
    },
    "fit_size_uncertainty": {
        "id": "fit_size_uncertainty",
        "title": "Fit and size uncertainty after the item is chosen",
        "behavior": (
            "After identifying a product or category, remaining uncertainty is whether it will "
            "fit — length, cup/band, plus-size belts, or brand-to-brand inconsistency."
        ),
        "journey_stage": "uncertainty_after_like",
        "monetary": False,
        "metric_prior": 0.95,
        "non_monetary_need": "fit",
        "themes": ["fit_uncertainty", "size_inconsistency"],
    },
    "returns_and_order_trust": {
        "id": "returns_and_order_trust",
        "title": "Return and order-integrity distrust that trains delay",
        "behavior": (
            "Failed pickups, cancelled orders, missing refunds, and 'passed quality check' "
            "refusals make the reverse path look unsafe, so committing to a liked item is riskier."
        ),
        "journey_stage": "postpone",
        "monetary": False,
        "metric_prior": 0.65,
        "non_monetary_need": "other",
        "themes": ["returns_safety_net"],
    },
    "assortment_or_access_gap": {
        "id": "assortment_or_access_gap",
        "title": "Catalog miss: scrolled Myntra and still could not find the item",
        "behavior": (
            "Shoppers spend a session on Myntra looking for a specific need (gym tee, tall palazzo, "
            "western wear, NRI access) and leave empty-handed rather than converting a shortlist."
        ),
        "journey_stage": "unmet_need",
        "monetary": False,
        "metric_prior": 0.70,
        "non_monetary_need": "other",
        "themes": ["unmet_need"],
    },
    "off_platform_research": {
        "id": "off_platform_research",
        "title": "Leaving Myntra to ask Reddit, Instagram, or other sites",
        "behavior": (
            "After browsing Myntra, users ask other people or other stores whether a product "
            "works in real life — try-ons, Insta shops, brand sites, peer recs."
        ),
        "journey_stage": "off_platform",
        "monetary": False,
        "metric_prior": 0.90,
        "non_monetary_need": "social_proof",
        "themes": ["off_platform_research", "social_proof"],
    },
    "price_watch_and_checkout": {
        "id": "price_watch_and_checkout",
        "title": "Price surprise and cross-platform price gaps",
        "behavior": (
            "Checkout totals jump, the same SKU is cheaper elsewhere, or the user waits for a "
            "sale event. Price talk is evidence of delay; a monetary incentive is not an opportunity."
        ),
        "journey_stage": "postpone",
        "monetary": True,
        "metric_prior": 0.80,
        "non_monetary_need": None,
        "themes": ["price_uncertainty", "sale_waiting"],
    },
    "occasion_and_styling_uncertainty": {
        "id": "occasion_and_styling_uncertainty",
        "title": "Occasion and styling uncertainty before committing",
        "behavior": (
            "Purchase is tied to a wedding, event, or 'will this look right on me' question. "
            "The item can be identified and still sit unbought until the look is confirmed."
        ),
        "journey_stage": "postpone",
        "monetary": False,
        "metric_prior": 0.75,
        "non_monetary_need": "occasion",
        "themes": ["occasion_delay", "styling_uncertainty"],
    },
    "cross_listing_compare": {
        "id": "cross_listing_compare",
        "title": "Comparing the same shortlist across marketplaces",
        "behavior": (
            "Users hold a candidate and check whether it (or an equivalent) is also on Flipkart, "
            "Nykaa, or a brand site before buying."
        ),
        "journey_stage": "compare",
        "monetary": False,
        "metric_prior": 0.85,
        "non_monetary_need": "comparison",
        "themes": ["comparison"],
    },
}

THEME_TO_AREA = {
    theme: area_id
    for area_id, spec in AREAS.items()
    for theme in spec["themes"]
}

_URL_THREAD_RE = re.compile(r"/comments/([a-z0-9]+)/", re.I)


def thread_id(claim: dict[str, Any], docs_by_id: dict[str, dict[str, Any]]) -> str:
    doc = docs_by_id.get(claim.get("doc_id") or "", {})
    meta = doc.get("raw_metadata") or {}
    link = meta.get("link_id") or meta.get("reddit_id")
    if meta.get("kind") == "comment" and meta.get("link_id"):
        return str(meta["link_id"])
    if meta.get("kind") == "submission" and meta.get("reddit_id"):
        return str(meta["reddit_id"])
    if link:
        return str(link)
    url = str(claim.get("url") or doc.get("url") or "")
    match = _URL_THREAD_RE.search(url)
    if match:
        return match.group(1)
    return str(claim.get("doc_id") or "")


def is_title_echo(claim: dict[str, Any], docs_by_id: dict[str, dict[str, Any]]) -> bool:
    doc = docs_by_id.get(claim.get("doc_id") or "", {})
    title = normalize_ws(str(doc.get("title") or ""))
    quote = normalize_ws(str(claim.get("quote") or ""))
    if len(title) < TITLE_ECHO_MIN or len(quote) < TITLE_ECHO_MIN:
        return False
    return title.lower() in quote.lower() or quote.lower() in title.lower()


def is_after_purchase(claim: dict[str, Any]) -> bool:
    quote = str(claim.get("quote") or "")
    return bool(AFTER_PURCHASE_RE.search(quote))


def assign_area(claim: dict[str, Any], docs_by_id: dict[str, dict[str, Any]]) -> str | None:
    quote = str(claim.get("quote") or "")
    theme = str(claim.get("theme") or "")

    if FIT_NOISE_RE.search(quote):
        return None

    if theme == "unmet_need" and DELIVERY_COMPLAINT_RE.search(quote):
        return "returns_and_order_trust"

    if theme == "occasion_delay" and OCCASION_FALSE_RE.search(quote):
        lower = quote.lower()
        if "gift card" in lower:
            return "price_watch_and_checkout"
        return "returns_and_order_trust"

    if theme == "other":
        lower = quote.lower()
        if "doubt" in lower:
            return "review_thinness"
        if any(token in lower for token in ("discount", "expensive", "2400")):
            return "price_watch_and_checkout"
        return None

    if theme == "bookmark_not_intent":
        return None

    return THEME_TO_AREA.get(theme)


def cluster_claims(
    claims: list[dict[str, Any]],
    docs_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    clustered: list[dict[str, Any]] = []
    for claim in claims:
        area_id = assign_area(claim, docs_by_id)
        row = dict(claim)
        row["opportunity_id"] = area_id
        row["thread_id"] = thread_id(claim, docs_by_id)
        row["after_purchase"] = is_after_purchase(claim)
        row["title_echo"] = is_title_echo(claim, docs_by_id)
        clustered.append(row)
    return clustered
