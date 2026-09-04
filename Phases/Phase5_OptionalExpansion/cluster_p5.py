"""Phase 3/4 areas plus the two wishlist behaviours the sweep was run to find.

Both new areas are behaviours, not features. "The list outgrows the shopper" is
a finding; "raise the cap" would be a solution and belongs to Part 5.
"""

from __future__ import annotations

import re
import sys
from typing import Any

from config import PHASE3_DIR, PHASE4_DIR

for _path in (PHASE4_DIR, PHASE3_DIR):
    if str(_path) not in sys.path:
        sys.path.append(str(_path))

from cluster import is_after_purchase, is_title_echo, thread_id  # noqa: E402
from cluster import AREAS as P3_AREAS  # noqa: E402
from cluster import assign_area as p3_assign  # noqa: E402

APP_FRICTION_RE = re.compile(
    r"\b(crash|crashes|login|otp|notification|app (is |keeps )?(slow|hang|freeze|frozen)|force close)\b",
    re.I,
)

STORE_SOURCES = frozenset({"play_store", "app_store"})
EXPANSION_SOURCES = frozenset({"youtube"})

AREAS: dict[str, dict[str, Any]] = {
    **P3_AREAS,
    "app_friction": {
        "id": "app_friction",
        "title": "App crash, login, and notification friction",
        "behavior": (
            "The mobile app itself fails (crash, OTP, login, hang) so a liked or wishlisted item "
            "cannot be completed. This is store-volume app friction, not a fashion-uncertainty story."
        ),
        "journey_stage": "unmet_need",
        "monetary": False,
        "metric_prior": 0.40,
        "non_monetary_need": "other",
        "themes": [],
        "store_only_ok": True,
    },
    "wishlist_intent_ambiguity": {
        "id": "wishlist_intent_ambiguity",
        "title": "The wishlist holds shortlists and daydreams in the same place",
        "behavior": (
            "Shoppers add for several unrelated reasons — a real shortlist, a sale watch, "
            "outfit inspiration, or a public list to show friends — and nothing in the product "
            "separates them. An add is therefore a weak and inconsistent signal of intent."
        ),
        "journey_stage": "why_add",
        "monetary": False,
        "metric_prior": 1.0,
        "non_monetary_need": "other",
        "themes": [],
    },
    "wishlist_ceiling": {
        "id": "wishlist_ceiling",
        "title": "The saved list outgrows the shopper who made it",
        "behavior": (
            "Saved items pile up until the list stops being usable: people cannot find what "
            "they saved, purge it, or stop adding. Evidence that the list is an archive. "
            "It does not establish that a larger list would produce more purchases."
        ),
        "journey_stage": "why_add",
        "monetary": False,
        "metric_prior": 0.55,
        "non_monetary_need": "other",
        "themes": [],
    },
}

FACET_TO_AREA = {
    "ceiling": "wishlist_ceiling",
    "archive": "wishlist_intent_ambiguity",
    "intent": "wishlist_intent_ambiguity",
    "why_add": "wishlist_intent_ambiguity",
    "sale_park": "price_watch_and_checkout",
    "fit_block": "fit_size_uncertainty",
    "compare_block": "cross_listing_compare",
}


def assign_area(claim: dict[str, Any], docs_by_id: dict[str, dict[str, Any]]) -> str | None:
    facet = str(claim.get("wishlist_facet") or "")
    if facet:
        return FACET_TO_AREA.get(facet)
    quote = str(claim.get("quote") or "")
    if str(claim.get("source") or "") in STORE_SOURCES and APP_FRICTION_RE.search(quote):
        return "app_friction"
    return p3_assign(claim, docs_by_id)


def cluster_claims(
    claims: list[dict[str, Any]],
    docs_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    clustered: list[dict[str, Any]] = []
    for claim in claims:
        row = dict(claim)
        if not row.get("source"):
            doc = docs_by_id.get(str(row.get("doc_id") or ""), {})
            row["source"] = doc.get("source") or "reddit"
        row["opportunity_id"] = assign_area(row, docs_by_id)
        if row.get("source") in STORE_SOURCES | EXPANSION_SOURCES:
            row["thread_id"] = str(row.get("doc_id") or "")
        else:
            row["thread_id"] = thread_id(row, docs_by_id)
        row["after_purchase"] = is_after_purchase(row)
        row["title_echo"] = is_title_echo(row, docs_by_id)
        clustered.append(row)
    return clustered
