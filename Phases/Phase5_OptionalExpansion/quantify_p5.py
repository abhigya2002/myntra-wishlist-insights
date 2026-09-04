"""Counts across Reddit, store, and expansion sources. Reddit stays primary."""

from __future__ import annotations

from collections import Counter
from typing import Any

from cluster_p5 import AREAS, EXPANSION_SOURCES, STORE_SOURCES
from config import IN_SCOPE_LABELS

JOURNEY_STAGES = frozenset({"why_add", "uncertainty_after_like", "postpone", "compare", "off_platform"})


def _share(part: int, whole: int) -> float:
    return round(part / whole, 4) if whole else 0.0


def _source_of(row: dict[str, Any]) -> str:
    return str(row.get("source") or "reddit")


def corpus_stats(
    claims: list[dict[str, Any]],
    labeled: list[dict[str, Any]],
    raw_docs: list[dict[str, Any]],
) -> dict[str, Any]:
    in_scope = [row for row in labeled if row.get("label") in IN_SCOPE_LABELS]
    by_source_claims = Counter(_source_of(row) for row in claims)
    reddit = by_source_claims.get("reddit", 0)
    store = sum(by_source_claims.get(name, 0) for name in STORE_SOURCES)
    expansion = sum(by_source_claims.get(name, 0) for name in EXPANSION_SOURCES)
    phase5 = sum(1 for row in claims if row.get("wishlist_facet"))
    return {
        "raw_docs": len(raw_docs),
        "labeled_docs": len(labeled),
        "in_scope_docs": len(in_scope),
        "by_label": dict(Counter(row.get("label") or "unknown" for row in labeled)),
        "by_source_docs": dict(Counter(_source_of(row) for row in raw_docs)),
        "by_source_claims": dict(by_source_claims),
        "claims_total": len(claims),
        "claims_clustered": sum(1 for row in claims if row.get("opportunity_id")),
        "claims_unclustered": sum(1 for row in claims if not row.get("opportunity_id")),
        "claim_docs": len({row.get("doc_id") for row in claims}),
        "reddit_claim_count": reddit,
        "store_claim_count": store,
        "expansion_claim_count": expansion,
        "phase5_claim_count": phase5,
        "reddit_claim_share": _share(reddit, len(claims)),
        "reddit_share": _share(reddit, len(claims)),
        "wishlist_explicit_claims": sum(1 for row in claims if row.get("wishlist_signal") == "explicit"),
        "wishlist_implied_claims": sum(1 for row in claims if row.get("wishlist_signal") == "implied"),
        "facets": dict(Counter(row["wishlist_facet"] for row in claims if row.get("wishlist_facet"))),
        "extractor": dict(Counter(row.get("extractor") for row in claims)),
        "gate_on_claims": dict(Counter(row.get("gate_label") for row in claims)),
    }


def quantify_area(area_id: str, clustered: list[dict[str, Any]], corpus: dict[str, Any]) -> dict[str, Any]:
    spec = AREAS[area_id]
    rows = [row for row in clustered if row.get("opportunity_id") == area_id]
    n = len(rows)
    reddit = [row for row in rows if _source_of(row) == "reddit"]
    play = [row for row in rows if _source_of(row) == "play_store"]
    app = [row for row in rows if _source_of(row) == "app_store"]
    expansion = [row for row in rows if _source_of(row) in EXPANSION_SOURCES]
    store = play + app
    docs = {row.get("doc_id") for row in rows}
    threads = {row.get("thread_id") for row in rows}
    urls = {row.get("url") for row in rows if row.get("url")}
    delay_yes = sum(1 for row in rows if row.get("delay_or_dropoff_signal") == "yes")
    price = sum(1 for row in rows if row.get("price_mentioned"))
    journey = sum(1 for row in rows if row.get("stage") in JOURNEY_STAGES)
    segments: Counter[str] = Counter()
    questions: Counter[int] = Counter()
    for row in rows:
        for item in row.get("segment_signals") or []:
            segments[str(item)] += 1
        for qid in row.get("discovery_question_ids") or []:
            questions[int(qid)] += 1
    return {
        "id": area_id,
        "title": spec["title"],
        "behavior": spec["behavior"],
        "journey_stage": spec["journey_stage"],
        "monetary": spec["monetary"],
        "metric_prior": spec["metric_prior"],
        "non_monetary_need": spec["non_monetary_need"],
        "store_only_ok": bool(spec.get("store_only_ok")),
        "claim_count": n,
        "reddit_claim_count": len(reddit),
        "play_claim_count": len(play),
        "app_claim_count": len(app),
        "store_claim_count": len(store),
        "expansion_claim_count": len(expansion),
        "phase5_claim_count": sum(1 for row in rows if row.get("wishlist_facet")),
        "doc_count": len(docs),
        "reddit_doc_count": len({row.get("doc_id") for row in reddit}),
        "store_doc_count": len({row.get("doc_id") for row in store}),
        "thread_count": len(threads),
        "url_count": len(urls),
        "in_scope_doc_share": _share(len(docs), int(corpus.get("in_scope_docs") or 0)),
        "claim_share": _share(n, int(corpus.get("claims_total") or 0)),
        "reddit_share": _share(len(reddit), n),
        "myntra_primary": sum(1 for row in rows if row.get("gate_label") == "myntra_primary"),
        "fashion_context": sum(1 for row in rows if row.get("gate_label") == "fashion_context"),
        "myntra_share": _share(sum(1 for row in rows if row.get("gate_label") == "myntra_primary"), n),
        "delay_yes": delay_yes,
        "delay_share": _share(delay_yes, n),
        "price_mentioned": price,
        "price_share": _share(price, n),
        "non_monetary_count": sum(1 for row in rows if row.get("non_monetary_need")),
        "non_monetary_share": _share(sum(1 for row in rows if row.get("non_monetary_need")), n),
        "extractor_groq": sum(1 for row in rows if row.get("extractor") == "groq"),
        "groq_share": _share(sum(1 for row in rows if row.get("extractor") == "groq"), n),
        "after_purchase": sum(1 for row in rows if row.get("after_purchase")),
        "after_purchase_share": _share(sum(1 for row in rows if row.get("after_purchase")), n),
        "title_echo": sum(1 for row in rows if row.get("title_echo")),
        "journey_stage_count": journey,
        "journey_stage_share": _share(journey, n),
        "wishlist_explicit": sum(1 for row in rows if row.get("wishlist_signal") == "explicit"),
        "wishlist_implied": sum(1 for row in rows if row.get("wishlist_signal") == "implied"),
        "facets": dict(Counter(row["wishlist_facet"] for row in rows if row.get("wishlist_facet"))),
        "stages": dict(Counter(row.get("stage") for row in rows)),
        "themes": dict(Counter(row.get("theme") for row in rows)),
        "segments": dict(segments),
        "questions": {str(key): value for key, value in sorted(questions.items())},
        "claim_ids": [row.get("claim_id") for row in rows],
        "doc_ids": sorted(doc for doc in docs if doc),
        "urls": sorted(url for url in urls if url),
    }


def quantify_all(
    clustered: list[dict[str, Any]],
    labeled: list[dict[str, Any]],
    raw_docs: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    corpus = corpus_stats(clustered, labeled, raw_docs)
    return corpus, [quantify_area(area_id, clustered, corpus) for area_id in AREAS]
