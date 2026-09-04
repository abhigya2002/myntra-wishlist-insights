"""Wishlist-language Reddit sweep for the Q1 / Q8 gap.

Phase 1 pulled Myntra-named queries and returned exactly one document
containing the word "wishlist". Two things change here:

  1. Brand-optional. architecture.md 3.3 asks for recall on buy-later
     behaviour even when Myntra is not named. Competitor-only text still drops.
  2. Thread-first. Arctic Shift's comment keyword search times out, so we find
     wishlist *threads* by post search and then pull each thread's comments by
     link_id. Comments inside a wishlist thread are on-topic even when they
     never repeat the word, which is the same in-thread rule Phase 1 used.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Callable

from archive import ArchiveClient, ArchiveError
from config import (
    DEFAULT_MAX_PER_QUERY,
    PHASE0_SPEC,
    PHASE1_DIR,
    PRIORITY_SUBREDDITS,
    SWEEP_TIERS,
    WISHLIST_QUERIES,
)
from io_util import read_json
from vendor import load

_filter = load("phase1_myntra_filter", PHASE1_DIR / "myntra_filter.py")
_normalize = load("phase1_normalize", PHASE1_DIR / "normalize.py")

competitor_only = _filter.competitor_only
mentions_myntra = _filter.mentions_myntra
comment_document = _normalize.comment_document
job_id = _normalize.job_id
submission_document = _normalize.submission_document

WISHLIST_TERMS = (
    "wishlist",
    "wish list",
    "saved item",
    "save for later",
    "saved for later",
    "shortlist",
    "bookmark",
)

MIN_COMMENT_CHARS = 25
MAX_COMMENTS_PER_THREAD = 60

BOT_RE = re.compile(
    r"(i am a bot|automoderator|this action was performed automatically|"
    r"contact the moderators|join .{0,15}discord)",
    re.I,
)


def _epoch(date_str: str) -> int:
    return int(datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())


def window() -> tuple[int, int]:
    spec = read_json(PHASE0_SPEC)
    win = spec.get("time_window", {})
    return _epoch(win.get("start", "2024-08-17")), _epoch(win.get("end", "2026-08-17"))


def subreddits(*, priority_only: bool = False) -> list[str]:
    if priority_only:
        return list(PRIORITY_SUBREDDITS)
    tiers = read_json(PHASE0_SPEC).get("reddit", {}).get("subreddit_tiers", {})
    ordered: list[str] = []
    for tier in SWEEP_TIERS:
        for sub in tiers.get(tier, []):
            if sub not in ordered:
                ordered.append(sub)
    return ordered


def mentions_wishlist(*parts: str | None) -> bool:
    blob = " ".join(part or "" for part in parts).lower()
    return any(term in blob for term in WISHLIST_TERMS)


def keep_submission(doc: dict[str, Any], *, brand_required: bool) -> bool:
    title = doc.get("title") or ""
    body = doc.get("body") or ""
    if competitor_only(title, body) and not mentions_myntra(title, body):
        return False
    if brand_required:
        return mentions_myntra(title, body)
    return mentions_wishlist(title, body) or mentions_myntra(title, body)


def keep_comment(doc: dict[str, Any]) -> bool:
    body = doc.get("body") or ""
    if len(body.strip()) < MIN_COMMENT_CHARS:
        return False
    if BOT_RE.search(body):
        return False
    if competitor_only(body) and not mentions_myntra(body):
        return False
    return True


def sweep(
    *,
    max_per_query: int = DEFAULT_MAX_PER_QUERY,
    max_subreddits: int | None = None,
    priority_only: bool = False,
    sleep_s: float = 2.5,
    log: Callable[[str], None] = print,
    checkpoint: Callable[[list[dict[str, Any]], list[dict[str, Any]]], None] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """`checkpoint` is called after each subreddit so an interrupted pull is not lost."""
    after, before = window()
    subs = subreddits(priority_only=priority_only)
    if max_subreddits:
        subs = subs[:max_subreddits]

    client = ArchiveClient(sleep_s=sleep_s)
    documents: dict[str, dict[str, Any]] = {}
    pull_log: list[dict[str, Any]] = []
    threads_seen: set[str] = set()

    for spec in WISHLIST_QUERIES:
        query = str(spec["query"])
        query_id = str(spec["id"])
        brand_required = bool(spec.get("brand_required"))
        kept_for_query = 0

        for sub in subs:
            if kept_for_query >= max_per_query:
                break

            meta = {
                "query_id": query_id,
                "query": query,
                "search_scope": "phase5_wishlist_sweep",
                "subreddit": sub,
                "pull_job_id": job_id(query_id, "phase5", sub, "submission"),
                "spec_version": "1.0.0",
                "pass_name": "phase5_wishlist",
                "discovery_questions": spec.get("questions"),
                "brand_required": brand_required,
            }

            try:
                rows = client.search(
                    "submission",
                    subreddit=sub,
                    query=query,
                    after=after,
                    before=before,
                    limit=25,
                )
            except ArchiveError as exc:
                pull_log.append(
                    {"job_id": meta["pull_job_id"], "status": "error", "error": str(exc)[:180]}
                )
                continue

            kept_posts = 0
            kept_comments = 0
            for row in rows:
                doc = submission_document(row, meta)
                if not doc or not keep_submission(doc, brand_required=brand_required):
                    continue
                post_id = str(row.get("id") or "")
                if doc["id"] not in documents:
                    doc["raw_metadata"]["matched_query_ids"] = [query_id]
                    documents[doc["id"]] = doc
                    kept_posts += 1
                    kept_for_query += 1
                else:
                    matched = documents[doc["id"]]["raw_metadata"].setdefault("matched_query_ids", [])
                    if query_id not in matched:
                        matched.append(query_id)

                if not post_id or post_id in threads_seen:
                    continue
                threads_seen.add(post_id)
                kept_comments += _pull_thread(
                    client,
                    post_id=post_id,
                    parent_title=doc.get("title") or "",
                    meta=meta,
                    documents=documents,
                    pull_log=pull_log,
                )

            pull_log.append(
                {
                    "job_id": meta["pull_job_id"],
                    "status": "ok",
                    "fetched": len(rows),
                    "kept_posts": kept_posts,
                    "kept_comments": kept_comments,
                }
            )
            if kept_posts or kept_comments:
                log(f"  r/{sub} [{query_id}] posts={kept_posts} comments={kept_comments}")
            if checkpoint and (kept_posts or kept_comments):
                checkpoint(list(documents.values()), pull_log)

        log(f"query {query_id!r}: kept {kept_for_query} posts (running total {len(documents)} docs)")

    return list(documents.values()), pull_log


def _pull_thread(
    client: ArchiveClient,
    *,
    post_id: str,
    parent_title: str,
    meta: dict[str, Any],
    documents: dict[str, dict[str, Any]],
    pull_log: list[dict[str, Any]],
) -> int:
    url = (
        "https://arctic-shift.photon-reddit.com/api/comments/search"
        f"?link_id={post_id}&limit={MAX_COMMENTS_PER_THREAD}"
    )
    try:
        payload = client._get(url)  # noqa: SLF001 - single-purpose internal fetch
    except ArchiveError as exc:
        pull_log.append({"job_id": f"thread__{post_id}", "status": "error", "error": str(exc)[:180]})
        return 0

    rows = payload.get("data") or []
    comment_meta = {
        **meta,
        "pull_job_id": f"thread__{post_id}",
        "in_wishlist_thread": True,
    }
    kept = 0
    for row in rows:
        doc = comment_document(row, comment_meta, parent_title=parent_title)
        if not doc or doc["id"] in documents or not keep_comment(doc):
            continue
        doc["raw_metadata"]["matched_query_ids"] = [meta["query_id"]]
        documents[doc["id"]] = doc
        kept += 1
    return kept
