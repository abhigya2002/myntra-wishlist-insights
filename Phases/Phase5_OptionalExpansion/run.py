"""Phase 5 CLI: wishlist sweep → extract → merge Phases 2 and 4 → re-rank → report + evals."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PHASE5_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PHASE5_DIR))

from cluster_p5 import cluster_claims  # noqa: E402
from config import (  # noqa: E402
    CLAIMS_PATH,
    CLUSTERS_PATH,
    COMBINED_CLAIMS_PATH,
    DEFAULT_MAX_PER_QUERY,
    INGEST_MANIFEST,
    LABELED_PATH,
    LEDGER_PATH,
    MANIFEST_PATH,
    PHASE1_MANIFEST,
    PHASE1_RAW,
    PHASE2_CLAIMS,
    PHASE2_LABELED,
    PHASE2_MANIFEST,
    PHASE4_CLAIMS,
    PHASE4_DIR,
    PHASE4_INGEST_MANIFEST,
    PHASE4_LABELED,
    PHASE4_RAW,
    QUANT_PATH,
    QUESTIONS_PATH,
    RANKING_PATH,
    RAW_PATH,
    REPORT_PATH,
    RUBRIC_PATH,
    TRIGGER_GAPS,
    WISHLIST_PATH,
)
from evals_p5 import groundedness_sample, instant_fail_checks, write_eval_docs  # noqa: E402
from extract import extract_document, facet_counts  # noqa: E402
from ingest import ingest as pull_expansion  # noqa: E402
from io_util import index_by_id, read_json, read_jsonl, write_json, write_jsonl, write_text  # noqa: E402
from quantify_p5 import quantify_all  # noqa: E402
from questions_p5 import answer_questions, coverage_summary, wishlist_evidence  # noqa: E402
from rank_p5 import rank_areas, rubric_payload  # noqa: E402
from report import render_report  # noqa: E402

if str(PHASE4_DIR) not in sys.path:
    sys.path.append(str(PHASE4_DIR))

from corroborate import corroboration_table  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def with_source(claims: list[dict[str, Any]], default: str) -> list[dict[str, Any]]:
    rows = []
    for claim in claims:
        row = dict(claim)
        row.setdefault("source", default)
        rows.append(row)
    return rows


def build_ledger(
    clustered: list[dict[str, Any]],
    ranked: list[dict[str, Any]],
    answers: list[dict[str, Any]],
) -> dict[str, Any]:
    entries = [
        {
            "claim_id": row.get("claim_id"),
            "doc_id": row.get("doc_id"),
            "url": row.get("url"),
            "quote": row.get("quote"),
            "source": row.get("source") or "reddit",
            "quote_verified": row.get("quote_verified"),
            "discovery_question_ids": row.get("discovery_question_ids"),
            "theme": row.get("theme"),
            "wishlist_facet": row.get("wishlist_facet"),
            "opportunity_id": row.get("opportunity_id"),
            "thread_id": row.get("thread_id"),
            "gate_label": row.get("gate_label"),
            "stage": row.get("stage"),
            "delay_or_dropoff_signal": row.get("delay_or_dropoff_signal"),
            "price_mentioned": row.get("price_mentioned"),
            "extractor": row.get("extractor"),
        }
        for row in clustered
    ]
    return {
        "phase": 5,
        "product": "Myntra",
        "source_mix": ["reddit", "play_store", "app_store", "youtube"],
        "generated_at": utc_now(),
        "claims": len(entries),
        "ranked_area_ids": [row["id"] for row in ranked],
        "question_coverage": [row["coverage"] for row in answers],
        "entries": entries,
    }


def write_manifest(
    *,
    corpus: dict[str, Any],
    ranked: list[dict[str, Any]],
    coverage: dict[str, Any],
    evals: dict[str, Any],
    expansion: dict[str, Any],
    wishlist: dict[str, Any],
) -> None:
    write_json(
        MANIFEST_PATH,
        {
            "phase": 5,
            "product": "Myntra",
            "draft": "reddit_primary_store_corroboration_wishlist_expansion",
            "trigger_gaps": list(TRIGGER_GAPS),
            "ran_at": utc_now(),
            "expansion": {
                "pulled_at": expansion.get("pulled_at"),
                "documents": expansion.get("documents"),
                "by_source": expansion.get("by_source"),
                "skipped": expansion.get("skipped"),
            },
            "corpus": corpus,
            "wishlist_evidence": {
                "claims": wishlist.get("claims"),
                "threads": wishlist.get("threads"),
                "facets": wishlist.get("facets"),
                "reading": wishlist.get("reading"),
            },
            "ranked_areas": len(ranked),
            "ranking": [
                {"rank": row["rank"], "id": row["id"], "score": row["score"]} for row in ranked
            ],
            "question_coverage": coverage,
            "instant_fail_clear": evals.get("instant_fail_clear"),
            "files": {"report": str(REPORT_PATH), "ledger": str(LEDGER_PATH), "raw": str(RAW_PATH)},
            "re_run": "python run.py --no-ingest",
        },
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 5 Myntra wishlist expansion + re-rank")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-ingest", action="store_true", help="reuse the expansion raw file on disk")
    parser.add_argument("--force", action="store_true", help="re-pull even if raw exists")
    parser.add_argument("--max-per-query", type=int, default=DEFAULT_MAX_PER_QUERY)
    parser.add_argument("--max-subreddits", type=int, default=None)
    parser.add_argument(
        "--priority",
        action="store_true",
        help="sweep only the subreddits that have produced wishlist threads",
    )
    parser.add_argument("--fresh", action="store_true", help="discard documents already pulled")
    parser.add_argument("--skip-reddit", action="store_true")
    parser.add_argument("--skip-youtube", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.dry_run:
        print("Phase 5 dry-run")
        print(f"  trigger gaps:    {', '.join(TRIGGER_GAPS)}")
        print(f"  reddit claims:   {PHASE2_CLAIMS} exists={PHASE2_CLAIMS.is_file()}")
        print(f"  store claims:    {PHASE4_CLAIMS} exists={PHASE4_CLAIMS.is_file()}")
        print(f"  expansion raw:   {RAW_PATH} exists={RAW_PATH.is_file()}")
        print(f"  report -> {REPORT_PATH}")
        print("  steps: wishlist sweep -> extract -> merge Phase 2 + Phase 4 -> rank -> report")
        return 0

    reddit_raw = read_jsonl(PHASE1_RAW)
    reddit_labeled = read_jsonl(PHASE2_LABELED)
    reddit_claims = with_source(read_jsonl(PHASE2_CLAIMS), "reddit")
    if not reddit_raw or not reddit_claims:
        raise SystemExit("Phase 1 raw docs and Phase 2 claims are required")

    store_raw = read_jsonl(PHASE4_RAW)
    store_labeled = read_jsonl(PHASE4_LABELED)
    store_claims = read_jsonl(PHASE4_CLAIMS)
    if not store_claims:
        raise SystemExit("Phase 4 store claims are required; run Phase 4 first")

    need_pull = args.force or (not args.no_ingest and not RAW_PATH.is_file())
    if need_pull:
        expansion = pull_expansion(
            max_per_query=args.max_per_query,
            max_subreddits=args.max_subreddits,
            priority_only=args.priority,
            skip_reddit=args.skip_reddit,
            skip_youtube=args.skip_youtube,
            keep_existing=not args.fresh,
        )
    else:
        expansion = read_json(INGEST_MANIFEST) or {"by_source": {}, "skipped": {}, "pulled_at": None}

    expansion_docs = read_jsonl(RAW_PATH)
    if not expansion_docs:
        raise SystemExit(f"no expansion documents on disk: {RAW_PATH} (run without --no-ingest)")

    # A checkpointed pull can end without rewriting its manifest, so counts come
    # from the file that actually exists rather than from the last manifest.
    actual: dict[str, int] = {}
    for doc in expansion_docs:
        key = str(doc.get("source") or "unknown")
        actual["reddit_wishlist_sweep" if key == "reddit" else key] = actual.get(
            "reddit_wishlist_sweep" if key == "reddit" else key, 0
        ) + 1
    expansion = {**expansion, "documents": len(expansion_docs), "by_source": actual}

    expansion_labeled: list[dict[str, Any]] = []
    expansion_claims: list[dict[str, Any]] = []
    for doc in expansion_docs:
        labeled, claims = extract_document(doc)
        expansion_labeled.append(labeled)
        expansion_claims.extend(claims)
    write_jsonl(LABELED_PATH, expansion_labeled)
    write_jsonl(CLAIMS_PATH, expansion_claims)

    combined_claims = reddit_claims + store_claims + expansion_claims
    write_jsonl(COMBINED_CLAIMS_PATH, combined_claims)
    combined_labeled = reddit_labeled + store_labeled + expansion_labeled
    combined_docs = reddit_raw + store_raw + expansion_docs
    docs_by_id = index_by_id(combined_docs)

    clustered = cluster_claims(combined_claims, docs_by_id)
    corpus, area_quant = quantify_all(clustered, combined_labeled, combined_docs)
    ranked = rank_areas(area_quant)
    answers = answer_questions(clustered)
    coverage = coverage_summary(answers)
    corr = corroboration_table(area_quant)
    wishlist = wishlist_evidence(clustered)
    ground = groundedness_sample(clustered, docs_by_id)

    def build(instant_clear: bool) -> str:
        return render_report(
            phase1=read_json(PHASE1_MANIFEST),
            phase2=read_json(PHASE2_MANIFEST),
            store_ingest=read_json(PHASE4_INGEST_MANIFEST),
            expansion=expansion,
            corpus=corpus,
            ranked=ranked,
            answers=answers,
            coverage=coverage,
            clustered=clustered,
            corroboration=corr,
            wishlist=wishlist,
            evals={"instant_fail_clear": instant_clear, "groundedness": ground},
        )

    draft = build(True)
    instant = instant_fail_checks(
        report=draft,
        ranked=ranked,
        answers=answers,
        coverage=coverage,
        corpus=corpus,
        claims=clustered,
        corroboration=corr,
        wishlist=wishlist,
        expansion=expansion,
    )
    report = build(instant["clear"])

    write_jsonl(CLUSTERS_PATH, clustered)
    write_json(QUANT_PATH, {"corpus": corpus, "areas": area_quant})
    write_json(RANKING_PATH, ranked)
    write_json(QUESTIONS_PATH, {"coverage": coverage, "answers": answers})
    write_json(WISHLIST_PATH, wishlist)
    write_json(RUBRIC_PATH, rubric_payload(ranked))
    write_json(LEDGER_PATH, build_ledger(clustered, ranked, answers))
    write_text(REPORT_PATH, report)
    write_eval_docs(instant, ground, coverage, ranked, wishlist)
    write_manifest(
        corpus=corpus,
        ranked=ranked,
        coverage=coverage,
        evals={"instant_fail_clear": instant["clear"]},
        expansion=expansion,
        wishlist=wishlist,
    )

    print(
        f"Done. expansion_docs={len(expansion_docs)} expansion_claims={len(expansion_claims)} "
        f"facets={facet_counts(expansion_claims)} combined={len(clustered)} ranked={len(ranked)} "
        f"coverage={coverage['answered_or_partial']}/10 "
        f"instant_fail={'clear' if instant['clear'] else 'FAILED'} "
        f"groundedness={ground['verbatim_pct']:.0%}",
        flush=True,
    )
    print(f"Wrote {REPORT_PATH}", flush=True)
    return 0 if instant["clear"] and coverage["pass_8_of_10"] and ground["pass_verbatim"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
