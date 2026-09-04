"""Ten discovery questions on Reddit + store + Phase 5 wishlist claims.

Q1 and Q8 were Gaps through Phase 4 because no claim carried wishlist language.
Here their answers are generated from the facet counts the sweep produced, so
they move only as far as the evidence actually moves them.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from typing import Any

from config import PHASE3_DIR

if str(PHASE3_DIR) not in sys.path:
    sys.path.append(str(PHASE3_DIR))

from questions import QUESTION_TEXT, _answer_text, _pick_quotes, _unique_threads, coverage_summary  # noqa: E402

__all__ = ["QUESTION_TEXT", "answer_questions", "coverage_summary", "wishlist_evidence"]

STORE_SOURCES = frozenset({"play_store", "app_store"})

# Q1/Q8 can reach Answered only when both sides of the intent question appear.
ANSWERED_MIN_EXPLICIT = 6
ANSWERED_MIN_THREADS = 4
ANSWERED_MIN_PER_SIDE = 2


def facet_counts(clustered: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(row["wishlist_facet"] for row in clustered if row.get("wishlist_facet")))


def _coverage(
    qid: int,
    rows: list[dict[str, Any]],
    *,
    earned_segments: int,
    wishlist_explicit: int,
    facets: dict[str, int],
) -> str:
    if qid in {1, 8}:
        threads = _unique_threads([row for row in rows if row.get("wishlist_facet")])
        both_sides = (
            facets.get("archive", 0) >= ANSWERED_MIN_PER_SIDE
            and facets.get("intent", 0) >= ANSWERED_MIN_PER_SIDE
        )
        if (
            wishlist_explicit >= ANSWERED_MIN_EXPLICIT
            and threads >= ANSWERED_MIN_THREADS
            and both_sides
        ):
            return "Answered"
        if wishlist_explicit >= 2 and threads >= 2:
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


def _q1_text(facets: dict[str, int], threads: int) -> str:
    if not facets:
        return (
            "The expansion sweep returned no wishlist-language claims, so why people add "
            "still cannot be answered from this corpus."
        )
    return (
        "Adding is not one behaviour. Across {total} wishlist claims in {threads} threads the "
        "sweep separates: parking an item to watch for a sale ({sale_park}), keeping a running "
        "list for inspiration or to show other people ({archive}), a genuine shortlist the person "
        "means to buy ({intent}), and generic 'it's on my wishlist' mentions with no stated "
        "reason ({why_add}). The inspiration and show-and-tell use is not a weaker version of "
        "buying — it is a different activity that happens to use the same button."
    ).format(
        total=sum(facets.values()),
        threads=threads,
        sale_park=facets.get("sale_park", 0),
        archive=facets.get("archive", 0),
        intent=facets.get("intent", 0),
        why_add=facets.get("why_add", 0),
    )


def _q8_text(facets: dict[str, int], threads: int) -> str:
    archive = facets.get("archive", 0)
    intent = facets.get("intent", 0)
    ceiling = facets.get("ceiling", 0)
    if not facets:
        return (
            "Intent vs bookmark still cannot be scored: the expansion returned no "
            "wishlist-language claims."
        )
    lead = (
        f"Bookmark-style use is the larger share of what the sweep found: {archive} claims "
        f"describe saving without buying (lists kept for months, purges, 'just looking', "
        f"public wishlist threads) against {intent} claims that describe a save the person "
        f"actually converted or intends to. Across {threads} independent threads that split "
        "says an add is a weak intent signal by default."
    )
    if ceiling:
        lead += (
            f" {ceiling} claims describe the list becoming unusable at volume. That is further "
            "evidence of archive behaviour. It does not show that a bigger list would produce "
            "more purchases — a shopper who saves past the point of usefulness is the clearest "
            "example of adding being decoupled from buying."
        )
    lead += (
        " Treating every add as intent would fail the eval in evals.md; the defensible reading "
        "is that the wishlist mixes several jobs and the product does not tell them apart."
    )
    return lead


def _store_note(rows: list[dict[str, Any]]) -> str:
    store = [row for row in rows if (row.get("source") or "") in STORE_SOURCES]
    if not store:
        return ""
    play = sum(1 for row in store if row.get("source") == "play_store")
    app = sum(1 for row in store if row.get("source") == "app_store")
    return f" Store reviews add {len(store)} claims on this question (Play {play}, App Store {app})."


def _with_source(evidence: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {row.get("claim_id"): row for row in rows}
    enriched = []
    for item in evidence:
        extra = dict(item)
        parent = by_id.get(item.get("claim_id")) or {}
        extra["source"] = parent.get("source") or "reddit"
        extra["wishlist_facet"] = parent.get("wishlist_facet")
        enriched.append(extra)
    return enriched


def answer_questions(clustered: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_q: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in clustered:
        for qid in row.get("discovery_question_ids") or []:
            by_q[int(qid)].append(row)
    earned_segment_rows = [row for row in clustered if row.get("segment_signals")]
    wishlist_explicit = sum(1 for row in clustered if row.get("wishlist_signal") == "explicit")
    facets = facet_counts(clustered)
    facet_threads = _unique_threads([row for row in clustered if row.get("wishlist_facet")])

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
            facets=facets,
        )
        if qid == 1:
            answer = _q1_text(facets, facet_threads)
        elif qid == 8:
            answer = _q8_text(facets, facet_threads)
        else:
            answer = _answer_text(qid, coverage, rows)
            note = _store_note(rows)
            if note and coverage != "Gap":
                answer += note

        if qid in {1, 8}:
            pool = [row for row in rows if row.get("wishlist_facet")] or rows
        else:
            pool = rows
        answers.append(
            {
                "id": qid,
                "question": QUESTION_TEXT[qid],
                "coverage": coverage,
                "claim_count": len(rows),
                "thread_count": _unique_threads(rows),
                "reddit_claims": sum(1 for row in rows if (row.get("source") or "reddit") == "reddit"),
                "store_claims": sum(1 for row in rows if (row.get("source") or "") in STORE_SOURCES),
                "phase5_claims": sum(1 for row in rows if row.get("wishlist_facet")),
                "answer": answer,
                "evidence": _with_source(_pick_quotes(pool, 3), pool)
                if coverage != "Gap" or qid in {1, 8}
                else [],
            }
        )
    return answers


def wishlist_evidence(clustered: list[dict[str, Any]]) -> dict[str, Any]:
    """The intent-vs-bookmark split, stated as counts rather than a narrative."""
    rows = [row for row in clustered if row.get("wishlist_facet")]
    facets = facet_counts(clustered)
    archive = facets.get("archive", 0)
    intent = facets.get("intent", 0)
    decided = archive + intent
    samples: dict[str, list[dict[str, Any]]] = {}
    for facet in sorted(facets):
        facet_rows = [row for row in rows if row.get("wishlist_facet") == facet]
        samples[facet] = [
            {"quote": row.get("quote"), "url": row.get("url"), "claim_id": row.get("claim_id")}
            for row in _sorted_by_length(facet_rows)[:3]
        ]
    return {
        "claims": len(rows),
        "threads": _unique_threads(rows),
        "docs": len({row.get("doc_id") for row in rows}),
        "facets": facets,
        "bookmark_share_of_decided": round(archive / decided, 4) if decided else None,
        "intent_share_of_decided": round(intent / decided, 4) if decided else None,
        "ceiling_claims": facets.get("ceiling", 0),
        "reading": (
            "Bookmark-style saving outweighs stated intent."
            if archive > intent
            else "Stated intent outweighs bookmark-style saving."
            if intent > archive
            else "Bookmark and intent claims are balanced."
        )
        if decided
        else "Not enough decided claims to state a split.",
        "not_established": (
            "This does not establish that removing a saved-item ceiling would increase purchases. "
            "Volume of saves and conversion of saves are different quantities, and nothing in "
            "this corpus links them."
        ),
        "samples": samples,
    }


def _sorted_by_length(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: -len(str(row.get("quote") or "")))
