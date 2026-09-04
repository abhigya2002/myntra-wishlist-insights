"""Transparent ranking rubric from evals.md / architecture.md §3.7."""

from __future__ import annotations

from typing import Any

from config import MIN_RANKED_AREAS

WEIGHTS = {
    "metric_relevance": 0.30,
    "evidence_strength": 0.25,
    "delay_dropoff": 0.20,
    "constraint_fit": 0.15,
    "segment_honesty": 0.10,
}

MIN_CLAIMS = 2


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _round(value: float) -> float:
    return round(value, 4)


def score_area(area: dict[str, Any]) -> dict[str, Any]:
    n = int(area.get("claim_count") or 0)
    docs = int(area.get("doc_count") or 0)
    threads = int(area.get("thread_count") or 0)
    if threads <= 1:
        evidence = 0.35 * min(n / 8.0, 1.0)
    else:
        evidence = (
            0.35 * min(docs / 8.0, 1.0)
            + 0.25 * min(threads / 5.0, 1.0)
            + 0.20 * float(area.get("groq_share") or 0)
            + 0.20 * min(n / 12.0, 1.0)
        )
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
    segment = 1.0
    factors = {
        "metric_relevance": _round(_clamp(metric)),
        "evidence_strength": _round(_clamp(evidence)),
        "delay_dropoff": _round(_clamp(delay)),
        "constraint_fit": _round(_clamp(constraint)),
        "segment_honesty": _round(segment),
    }
    score = 100.0 * sum(factors[name] * weight for name, weight in WEIGHTS.items())
    return {
        **area,
        "factors": factors,
        "weights": dict(WEIGHTS),
        "score": _round(score),
        "eligible": n >= MIN_CLAIMS,
    }


def _factor_label(name: str) -> str:
    return {
        "metric_relevance": "stronger 30-day wishlist-window link",
        "evidence_strength": "broader evidence (more independent threads)",
        "delay_dropoff": "tighter delay/drop-off language",
        "constraint_fit": "better fit with the no-discount constraint",
        "segment_honesty": "more honest segment claims",
    }[name]


def _dominant_diff(higher: dict[str, Any], lower: dict[str, Any]) -> str:
    diffs = []
    for name in WEIGHTS:
        delta = float(higher["factors"][name]) - float(lower["factors"][name])
        diffs.append((delta, name))
    diffs.sort(reverse=True)
    return _factor_label(diffs[0][1])


def comparison_line(ranked: list[dict[str, Any]], index: int) -> str:
    area = ranked[index]
    if index == 0 and len(ranked) > 1:
        neighbor = ranked[1]
        reason = _dominant_diff(area, neighbor)
        return (
            f"Ranks above **{neighbor['title']}** because of {reason} "
            f"({area['score']:.1f} vs {neighbor['score']:.1f} on the rubric)."
        )
    above = ranked[index - 1]
    reason = _dominant_diff(above, area)
    extra = ""
    if index + 1 < len(ranked):
        below = ranked[index + 1]
        extra = f" It still ranks above **{below['title']}** ({area['score']:.1f} vs {below['score']:.1f})."
    return (
        f"Ranks below **{above['title']}** because that area has {reason} "
        f"({above['score']:.1f} vs {area['score']:.1f}).{extra}"
    )


def rank_areas(areas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = [score_area(area) for area in areas]
    eligible = [row for row in scored if row["eligible"]]
    eligible.sort(key=lambda row: (-row["score"], -row["thread_count"], -row["claim_count"], row["id"]))
    if len(eligible) < MIN_RANKED_AREAS:
        leftover = [row for row in scored if not row["eligible"] and row["claim_count"] >= 1]
        leftover.sort(key=lambda row: (-row["score"], -row["claim_count"], row["id"]))
        eligible.extend(leftover[: MIN_RANKED_AREAS - len(eligible)])
    for index, row in enumerate(eligible):
        row["rank"] = index + 1
        row["comparison"] = comparison_line(eligible, index)
    return eligible


def rubric_payload(ranked: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "weights": dict(WEIGHTS),
        "ask": {
            "metric_relevance": "Does this belong in the 30-day wishlist → purchase window?",
            "evidence_strength": "Multiple threads, not one viral post?",
            "delay_dropoff": "Tied to not buying, not just complaining?",
            "constraint_fit": "Can this matter without paying the user?",
            "segment_honesty": "Specific only where quotes support it?",
        },
        "formula": "score = 100 * (0.30*metric + 0.25*evidence + 0.20*delay + 0.15*constraint + 0.10*segment)",
        "ranked": [
            {
                "rank": row["rank"],
                "id": row["id"],
                "score": row["score"],
                "factors": row["factors"],
            }
            for row in ranked
        ],
    }
