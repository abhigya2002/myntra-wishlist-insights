"""Rank with Reddit as primary evidence; store volume is corroboration, not replacement."""

from __future__ import annotations

import sys
from typing import Any

from config import MIN_RANKED_AREAS, PHASE3_DIR

if str(PHASE3_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE3_DIR))

from rank import WEIGHTS, comparison_line  # noqa: E402


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _round(value: float) -> float:
    return round(value, 4)


def score_area(area: dict[str, Any]) -> dict[str, Any]:
    reddit_n = int(area.get("reddit_claim_count") or 0)
    store_n = int(area.get("store_claim_count") or 0)
    reddit_docs = int(area.get("reddit_doc_count") or 0)
    store_docs = int(area.get("store_doc_count") or 0)
    threads = int(area.get("thread_count") or 0)
    n = int(area.get("claim_count") or 0)

    if reddit_n <= 1:
        reddit_evidence = 0.30 * min(reddit_n / 4.0, 1.0)
    else:
        reddit_evidence = (
            0.45 * min(reddit_docs / 8.0, 1.0)
            + 0.30 * min(max(threads - store_docs, reddit_n) / 5.0, 1.0)
            + 0.25 * min(reddit_n / 12.0, 1.0)
        )
    store_corroboration = 0.0
    if reddit_n >= 1 and store_n >= 1:
        store_corroboration = min(1.0, store_n / 12.0)
    evidence = 0.70 * reddit_evidence + 0.15 * store_corroboration + 0.15 * float(area.get("groq_share") or 0)
    if reddit_n == 0:
        evidence = min(evidence, 0.35)

    delay = 0.70 * float(area.get("delay_share") or 0) + 0.30 * float(area.get("journey_stage_share") or 0)
    metric = float(area.get("metric_prior") or 0.7) * (
        0.40 * float(area.get("journey_stage_share") or 0)
        + 0.35 * float(area.get("delay_share") or 0)
        + 0.25 * (1.0 - float(area.get("after_purchase_share") or 0))
    )
    if area.get("monetary"):
        constraint = 0.25 + 0.25 * (1.0 - float(area.get("price_share") or 0))
    else:
        constraint = 0.70 + 0.30 * (1.0 - float(area.get("price_share") or 0))

    factors = {
        "metric_relevance": _round(_clamp(metric)),
        "evidence_strength": _round(_clamp(evidence)),
        "delay_dropoff": _round(_clamp(delay)),
        "constraint_fit": _round(_clamp(constraint)),
        "segment_honesty": 1.0,
    }
    score = 100.0 * sum(factors[name] * weight for name, weight in WEIGHTS.items())
    if reddit_n >= 2 and store_n >= 3:
        score = min(100.0, score + 3.0)
    eligible = reddit_n >= 2 or (bool(area.get("store_only_ok")) and store_n >= 5 and reddit_n >= 1)
    if reddit_n == 0:
        eligible = False
    return {
        **area,
        "factors": factors,
        "weights": dict(WEIGHTS),
        "score": _round(score),
        "eligible": eligible,
        "n": n,
    }


def rank_areas(areas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = [score_area(area) for area in areas]
    eligible = [row for row in scored if row["eligible"]]
    eligible.sort(key=lambda row: (-row["score"], -row["reddit_claim_count"], -row["claim_count"], row["id"]))
    if len(eligible) < MIN_RANKED_AREAS:
        leftover = [
            row
            for row in scored
            if not row["eligible"] and row["reddit_claim_count"] >= 1
        ]
        leftover.sort(key=lambda row: (-row["score"], -row["reddit_claim_count"], row["id"]))
        eligible.extend(leftover[: MIN_RANKED_AREAS - len(eligible)])
    for index, row in enumerate(eligible):
        row["rank"] = index + 1
        row["comparison"] = comparison_line(eligible, index)
    return eligible


def rubric_payload(ranked: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "weights": dict(WEIGHTS),
        "note": "Evidence strength is 70% Reddit + 15% store corroboration + 15% Groq share. Store-only areas are not ranked.",
        "formula": "score = 100 * rubric + 3 if Reddit>=2 and store>=3",
        "ranked": [
            {
                "rank": row["rank"],
                "id": row["id"],
                "score": row["score"],
                "reddit_claims": row.get("reddit_claim_count"),
                "store_claims": row.get("store_claim_count"),
                "factors": row["factors"],
            }
            for row in ranked
        ],
    }
