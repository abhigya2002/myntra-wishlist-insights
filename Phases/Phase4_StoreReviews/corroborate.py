"""For each Reddit opportunity, say whether store reviews corroborate or challenge it."""

from __future__ import annotations

from typing import Any


def verdict(area: dict[str, Any]) -> str:
    reddit_n = int(area.get("reddit_claim_count") or 0)
    store_n = int(area.get("store_claim_count") or 0)
    if reddit_n >= 1 and store_n >= 3:
        return "corroborates"
    if reddit_n >= 1 and store_n >= 1:
        return "thin_store"
    if reddit_n == 0 and store_n >= 3:
        return "store_only"
    if reddit_n >= 1 and store_n == 0:
        return "reddit_only"
    return "thin"


def corroboration_table(areas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for area in areas:
        if int(area.get("claim_count") or 0) == 0:
            continue
        item = {
            "id": area["id"],
            "title": area["title"],
            "reddit_claims": area.get("reddit_claim_count") or 0,
            "play_claims": area.get("play_claim_count") or 0,
            "app_claims": area.get("app_claim_count") or 0,
            "store_claims": area.get("store_claim_count") or 0,
            "verdict": verdict(area),
        }
        rows.append(item)
    order = {"corroborates": 0, "thin_store": 1, "reddit_only": 2, "store_only": 3, "thin": 4}
    rows.sort(key=lambda row: (order.get(row["verdict"], 9), -row["reddit_claims"], row["id"]))
    return rows
