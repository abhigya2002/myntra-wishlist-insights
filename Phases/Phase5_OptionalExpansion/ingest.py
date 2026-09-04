"""Phase 5 ingest: wishlist-language Reddit sweep plus optional YouTube."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

import reddit_wishlist
import youtube
from config import (
    DEFAULT_MAX_PER_QUERY,
    INGEST_MANIFEST,
    PHASE1_RAW,
    PULL_LOG_PATH,
    RAW_PATH,
    TRIGGER_GAPS,
    WISHLIST_QUERIES,
)
from io_util import read_jsonl, write_json, write_jsonl


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def existing_reddit_ids() -> set[str]:
    """Phase 5 must add documents, not re-count Phase 1's."""
    return {str(row.get("id")) for row in read_jsonl(PHASE1_RAW) if row.get("id")}


def ingest(
    *,
    max_per_query: int = DEFAULT_MAX_PER_QUERY,
    max_subreddits: int | None = None,
    priority_only: bool = False,
    skip_reddit: bool = False,
    skip_youtube: bool = False,
    keep_existing: bool = True,
    log: Callable[[str], None] = print,
) -> dict[str, Any]:
    known = existing_reddit_ids()
    carried = read_jsonl(RAW_PATH) if keep_existing else []
    carried_by_id = {str(row.get("id")): row for row in carried if row.get("id")}
    documents: list[dict[str, Any]] = []
    pull_log: list[dict[str, Any]] = []
    skips: dict[str, str] = {}

    def merged(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = dict(carried_by_id)
        for row in rows:
            if row["id"] not in known:
                out[str(row["id"])] = row
        return list(out.values())

    if skip_reddit:
        skips["reddit_wishlist_sweep"] = "skipped by flag"
    else:
        log(f"Reddit wishlist sweep ({'priority subs' if priority_only else 'all tiers'})...")
        if carried:
            log(f"  carrying {len(carried)} documents already on disk")

        def checkpoint(rows: list[dict[str, Any]], partial_log: list[dict[str, Any]]) -> None:
            write_jsonl(RAW_PATH, merged(rows))
            write_jsonl(PULL_LOG_PATH, partial_log)

        rows, pull_log = reddit_wishlist.sweep(
            max_per_query=max_per_query,
            max_subreddits=max_subreddits,
            priority_only=priority_only,
            log=log,
            checkpoint=checkpoint,
        )
        fresh = [row for row in rows if row["id"] not in known]
        log(f"  swept {len(rows)} docs, {len(fresh)} new beyond Phase 1")
        documents.extend(fresh)

    if skip_youtube:
        skips["youtube"] = "skipped by flag"
    else:
        log("YouTube comments (optional)...")
        yt_docs, reason = youtube.pull(log=log)
        documents.extend(yt_docs)
        if reason:
            skips["youtube"] = reason

    # MouthShut and Quora are named in the Phase 0 spec but both refuse
    # automated collection; recorded as a declared limitation, not a silent hole.
    skips["communities"] = "MouthShut / Quora block automated collection; not ingested"

    documents = merged(documents)
    by_source: dict[str, int] = {}
    for doc in documents:
        key = str(doc.get("source") or "unknown")
        if key == "reddit":
            key = "reddit_wishlist_sweep"
        by_source[key] = by_source.get(key, 0) + 1

    write_jsonl(RAW_PATH, documents)
    write_jsonl(PULL_LOG_PATH, pull_log)
    payload = {
        "phase": 5,
        "trigger_gaps": list(TRIGGER_GAPS),
        "pulled_at": utc_now(),
        "scope": "priority_subreddits" if priority_only else "all_tiers",
        "subreddits": reddit_wishlist.subreddits(priority_only=priority_only),
        "queries": [dict(spec) for spec in WISHLIST_QUERIES],
        "documents": len(documents),
        "by_source": by_source,
        "skipped": skips,
        "raw_path": str(RAW_PATH),
    }
    write_json(INGEST_MANIFEST, payload)
    return payload
