"""Ten discovery questions on the combined Reddit + store claim set."""

from __future__ import annotations

import sys
from collections import defaultdict
from typing import Any

from config import PHASE3_DIR

if str(PHASE3_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE3_DIR))

from questions import QUESTION_TEXT, _answer_text, _pick_quotes, _unique_threads, coverage_summary  # noqa: E402

__all__ = ["QUESTION_TEXT", "answer_questions", "coverage_summary"]


def _coverage(qid: int, rows: list[dict[str, Any]], *, earned_segments: int, wishlist_explicit: int) -> str:
    if qid in {1, 8}:
        if wishlist_explicit >= 2 and _unique_threads(rows) >= 2:
            return "Partial"
        return "Gap"
    if qid == 9:
        return "Partial" if earned_segments >= 2 else "Gap"
    if qid == 5:
        return "Partial" if rows else "Gap"
    threads = _unique_threads(rows)
    groq = sum(1 for row in rows if row.get("extractor") == "groq")
    reddit = sum(1 for row in rows if (row.get("source") or "reddit") == "reddit")
    if len(rows) >= 2 and threads >= 2 and (groq >= 2 or reddit >= 4 or len(rows) >= 6):
        return "Answered"
    if rows:
        return "Partial"
    return "Gap"


def _with_source(evidence: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {row.get("claim_id"): row for row in rows}
    enriched = []
    for item in evidence:
        extra = dict(item)
        parent = by_id.get(item.get("claim_id")) or {}
        extra["source"] = parent.get("source") or extra.get("source") or "reddit"
        enriched.append(extra)
    return evidence and enriched


def _store_note(rows: list[dict[str, Any]]) -> str:
    store = [row for row in rows if (row.get("source") or "") in {"play_store", "app_store"}]
    if not store:
        return ""
    play = sum(1 for row in store if row.get("source") == "play_store")
    app = sum(1 for row in store if row.get("source") == "app_store")
    return f" Store reviews add {len(store)} claims on this question (Play {play}, App Store {app})."


def answer_questions(clustered: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_q: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in clustered:
        for qid in row.get("discovery_question_ids") or []:
            by_q[int(qid)].append(row)
    earned_segment_rows = [row for row in clustered if row.get("segment_signals")]
    wishlist_explicit = sum(1 for row in clustered if row.get("wishlist_signal") == "explicit")
    answers = []
    for qid in range(1, 11):
        rows = by_q.get(qid, [])
        if qid == 9:
            rows = earned_segment_rows or rows
        coverage = _coverage(
            qid,
            rows,
            earned_segments=len(earned_segment_rows),
            wishlist_explicit=wishlist_explicit,
        )
        answer = _answer_text(qid, coverage, rows)
        extra = _store_note(rows)
        if extra and coverage != "Gap":
            answer = answer + extra
        elif qid in {1, 8} and wishlist_explicit:
            answer = (
                answer
                + f" Combined corpus now has {wishlist_explicit} explicit wishlist-signal claims "
                "(mostly store reviews if Reddit had none)."
            )
        answers.append(
            {
                "id": qid,
                "question": QUESTION_TEXT[qid],
                "coverage": coverage,
                "claim_count": len(rows),
                "thread_count": _unique_threads(rows),
                "reddit_claims": sum(1 for row in rows if (row.get("source") or "reddit") == "reddit"),
                "store_claims": sum(
                    1 for row in rows if (row.get("source") or "") in {"play_store", "app_store"}
                ),
                "answer": answer,
                "evidence": _with_source(_pick_quotes(rows, 3), rows)
                if coverage != "Gap" or qid in {1, 8}
                else [],
            }
        )
    return answers
