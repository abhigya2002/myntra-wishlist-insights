"""Phase 3 clustering plus store-only app-friction mapping."""

from __future__ import annotations

import re
import sys
from typing import Any

from config import PHASE3_DIR

if str(PHASE3_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE3_DIR))

from cluster import AREAS as P3_AREAS  # noqa: E402
from cluster import assign_area as p3_assign  # noqa: E402
from cluster import is_after_purchase, is_title_echo, thread_id  # noqa: E402

APP_FRICTION_RE = re.compile(
    r"\b(crash|crashes|login|otp|notification|app (is |keeps )?(slow|hang|freeze|frozen)|force close)\b",
    re.I,
)

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
}


def assign_area(claim: dict[str, Any], docs_by_id: dict[str, dict[str, Any]]) -> str | None:
    quote = str(claim.get("quote") or "")
    source = str(claim.get("source") or "")
    if source in {"play_store", "app_store"} and APP_FRICTION_RE.search(quote):
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
        if row.get("source") == "reddit":
            row["thread_id"] = thread_id(row, docs_by_id)
        else:
            row["thread_id"] = str(row.get("doc_id") or "")
        row["after_purchase"] = is_after_purchase(row)
        row["title_echo"] = is_title_echo(row, docs_by_id)
        clustered.append(row)
    return clustered
