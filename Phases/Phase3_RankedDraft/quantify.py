"""Counts, co-occurrence, and source mix for each opportunity area."""

from __future__ import annotations

from collections import Counter
from typing import Any

from cluster import AREAS
from config import IN_SCOPE_LABELS


def _share(part: int, whole: int) -> float:
    return round(part / whole, 4) if whole else 0.0


def corpus_stats(
    claims: list[dict[str, Any]],
    labeled: list[dict[str, Any]],
    raw_docs: list[dict[str, Any]],
) -> dict[str, Any]:
    in_scope = [row for row in labeled if row.get("label") in IN_SCOPE_LABELS]
    by_label = Counter(row.get("label") or "unknown" for row in labeled)
    by_source = Counter((row.get("source") or "reddit") for row in raw_docs)
    clustered = [row for row in claims if row.get("opportunity_id")]
    return {
        "raw_docs": len(raw_docs),
        "labeled_docs": len(labeled),
        "in_scope_docs": len(in_scope),
        "by_label": dict(by_label),
        "by_source": dict(by_source),
        "claims_total": len(claims),
        "claims_clustered": len(clustered),
        "claims_unclustered": len(claims) - len(clustered),
        "claim_docs": len({row.get("doc_id") for row in claims}),
        "reddit_share": 1.0 if raw_docs and all(s == "reddit" for s in by_source) else _share(
            by_source.get("reddit", 0), sum(by_source.values())
        ),
        "wishlist_explicit_claims": sum(1 for row in claims if row.get("wishlist_signal") == "explicit"),
        "wishlist_implied_claims": sum(1 for row in claims if row.get("wishlist_signal") == "implied"),
        "extractor": dict(Counter(row.get("extractor") for row in claims)),
        "gate_on_claims": dict(Counter(row.get("gate_label") for row in claims)),
    }


def quantify_area(
    area_id: str,
    clustered: list[dict[str, Any]],
    corpus: dict[str, Any],
) -> dict[str, Any]:
    spec = AREAS[area_id]
    rows = [row for row in clustered if row.get("opportunity_id") == area_id]
    n = len(rows)
    docs = {row.get("doc_id") for row in rows}
    threads = {row.get("thread_id") for row in rows}
    urls = {row.get("url") for row in rows if row.get("url")}
    delay_yes = sum(1 for row in rows if row.get("delay_or_dropoff_signal") == "yes")
    price = sum(1 for row in rows if row.get("price_mentioned"))
    non_mon = sum(1 for row in rows if row.get("non_monetary_need"))
    groq = sum(1 for row in rows if row.get("extractor") == "groq")
    after = sum(1 for row in rows if row.get("after_purchase"))
    title_echo = sum(1 for row in rows if row.get("title_echo"))
    myntra = sum(1 for row in rows if row.get("gate_label") == "myntra_primary")
    fashion = sum(1 for row in rows if row.get("gate_label") == "fashion_context")
    journey_stages = {"why_add", "uncertainty_after_like", "postpone", "compare", "off_platform"}
    journey = sum(1 for row in rows if row.get("stage") in journey_stages)
    stages = Counter(row.get("stage") for row in rows)
    themes = Counter(row.get("theme") for row in rows)
    segments: Counter[str] = Counter()
    questions: Counter[int] = Counter()
    for row in rows:
        for item in row.get("segment_signals") or []:
            segments[str(item)] += 1
        for qid in row.get("discovery_question_ids") or []:
            questions[int(qid)] += 1
    in_scope = int(corpus.get("in_scope_docs") or 0)
    return {
        "id": area_id,
        "title": spec["title"],
        "behavior": spec["behavior"],
        "journey_stage": spec["journey_stage"],
        "monetary": spec["monetary"],
        "metric_prior": spec["metric_prior"],
        "non_monetary_need": spec["non_monetary_need"],
        "claim_count": n,
        "doc_count": len(docs),
        "thread_count": len(threads),
        "url_count": len(urls),
        "in_scope_doc_share": _share(len(docs), in_scope),
        "claim_share": _share(n, int(corpus.get("claims_total") or 0)),
        "myntra_primary": myntra,
        "fashion_context": fashion,
        "myntra_share": _share(myntra, n),
        "reddit_share": 1.0,
        "delay_yes": delay_yes,
        "delay_share": _share(delay_yes, n),
        "price_mentioned": price,
        "price_share": _share(price, n),
        "non_monetary_count": non_mon,
        "non_monetary_share": _share(non_mon, n),
        "extractor_groq": groq,
        "groq_share": _share(groq, n),
        "after_purchase": after,
        "after_purchase_share": _share(after, n),
        "title_echo": title_echo,
        "journey_stage_count": journey,
        "journey_stage_share": _share(journey, n),
        "wishlist_explicit": sum(1 for row in rows if row.get("wishlist_signal") == "explicit"),
        "wishlist_implied": sum(1 for row in rows if row.get("wishlist_signal") == "implied"),
        "stages": dict(stages),
        "themes": dict(themes),
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
    areas = [quantify_area(area_id, clustered, corpus) for area_id in AREAS]
    return corpus, areas
