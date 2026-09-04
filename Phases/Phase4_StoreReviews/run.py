"""Phase 4 CLI: ingest stores → extract → merge Reddit → re-rank → report + evals."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PHASE4_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PHASE4_DIR))

from cluster_ext import cluster_claims  # noqa: E402
from config import (  # noqa: E402
    CLAIMS_PATH,
    CLUSTERS_PATH,
    COMBINED_CLAIMS_PATH,
    CORROBORATION_PATH,
    DEFAULT_APP_STORE_PAGES,
    DEFAULT_PLAY_COUNT,
    EVAL_SUMMARY_PATH,
    GROUNDEDNESS_PATH,
    INGEST_MANIFEST,
    INSTANT_FAIL_PATH,
    LABELED_PATH,
    LEDGER_PATH,
    MANIFEST_PATH,
    PHASE1_MANIFEST,
    PHASE1_RAW,
    PHASE2_CLAIMS,
    PHASE2_LABELED,
    PHASE2_MANIFEST,
    QUANT_PATH,
    QUESTIONS_PATH,
    RANKING_PATH,
    RAW_PATH,
    REPORT_PATH,
    RUBRIC_PATH,
)
from corroborate import corroboration_table  # noqa: E402
from evals_run import groundedness_sample, instant_fail_checks, write_eval_docs  # noqa: E402
from extract import extract_document, keyword_doc_count  # noqa: E402
from ingest import ingest as pull_stores  # noqa: E402
from io_util import index_by_id, read_json, read_jsonl, write_json, write_jsonl, write_text  # noqa: E402
from quantify import quantify_all  # noqa: E402
from questions_ext import answer_questions, coverage_summary  # noqa: E402
from rank_ext import rank_areas, rubric_payload  # noqa: E402
from report import render_report  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def attach_reddit_source(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for claim in claims:
        row = dict(claim)
        row.setdefault("source", "reddit")
        rows.append(row)
    return rows


def build_ledger(
    clustered: list[dict[str, Any]],
    ranked: list[dict[str, Any]],
    answers: list[dict[str, Any]],
) -> dict[str, Any]:
    entries = []
    for row in clustered:
        entries.append(
            {
                "claim_id": row.get("claim_id"),
                "doc_id": row.get("doc_id"),
                "url": row.get("url"),
                "quote": row.get("quote"),
                "source": row.get("source") or "reddit",
                "quote_verified": row.get("quote_verified"),
                "discovery_question_ids": row.get("discovery_question_ids"),
                "theme": row.get("theme"),
                "opportunity_id": row.get("opportunity_id"),
                "thread_id": row.get("thread_id"),
                "gate_label": row.get("gate_label"),
                "stage": row.get("stage"),
                "delay_or_dropoff_signal": row.get("delay_or_dropoff_signal"),
                "price_mentioned": row.get("price_mentioned"),
                "extractor": row.get("extractor"),
            }
        )
    return {
        "phase": 4,
        "product": "Myntra",
        "source_mix": ["reddit", "play_store", "app_store"],
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
    ingest: dict[str, Any],
) -> None:
    write_json(
        MANIFEST_PATH,
        {
            "phase": 4,
            "product": "Myntra",
            "draft": "reddit_primary_store_corroboration",
            "ran_at": utc_now(),
            "ingest": {
                "play": ingest.get("by_source", {}).get("play_store"),
                "app_store": ingest.get("by_source", {}).get("app_store"),
                "pulled_at": ingest.get("pulled_at"),
            },
            "corpus": corpus,
            "ranked_areas": len(ranked),
            "ranking": [
                {
                    "rank": row["rank"],
                    "id": row["id"],
                    "score": row["score"],
                    "reddit": row.get("reddit_claim_count"),
                    "store": row.get("store_claim_count"),
                }
                for row in ranked
            ],
            "question_coverage": coverage,
            "instant_fail_clear": evals.get("instant_fail_clear"),
            "files": {
                "report": str(REPORT_PATH),
                "ledger": str(LEDGER_PATH),
                "store_raw": str(RAW_PATH),
                "store_claims": str(CLAIMS_PATH),
            },
            "re_run": "python run.py",
        },
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 4 Myntra store corroboration + re-rank")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-ingest", action="store_true", help="reuse existing store raw file")
    parser.add_argument("--force", action="store_true", help="re-pull store reviews")
    parser.add_argument("--play-count", type=int, default=DEFAULT_PLAY_COUNT)
    parser.add_argument("--app-pages", type=int, default=DEFAULT_APP_STORE_PAGES)
    parser.add_argument("--skip-play", action="store_true")
    parser.add_argument("--skip-app", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.dry_run:
        print("Phase 4 dry-run")
        print(f"  reddit raw:    {PHASE1_RAW} exists={PHASE1_RAW.is_file()}")
        print(f"  reddit claims: {PHASE2_CLAIMS} exists={PHASE2_CLAIMS.is_file()}")
        print(f"  store raw:     {RAW_PATH} exists={RAW_PATH.is_file()}")
        print(f"  report -> {REPORT_PATH}")
        print("  steps: ingest Play/App Store -> extract -> merge Reddit -> rank -> report")
        return 0

    reddit_raw = read_jsonl(PHASE1_RAW)
    reddit_labeled = read_jsonl(PHASE2_LABELED)
    reddit_claims = attach_reddit_source(read_jsonl(PHASE2_CLAIMS))
    if not reddit_raw or not reddit_claims:
        raise SystemExit("Phase 1 raw docs and Phase 2 claims are required")

    need_pull = args.force or (not args.no_ingest and not RAW_PATH.is_file())
    if need_pull:
        ingest_payload = pull_stores(
            play_count=args.play_count,
            app_pages=args.app_pages,
            skip_play=args.skip_play,
            skip_app=args.skip_app,
        )
    else:
        ingest_payload = read_json(INGEST_MANIFEST)
        if not ingest_payload:
            ingest_payload = {"by_source": {}, "pulled_at": None}

    store_docs = read_jsonl(RAW_PATH)
    if not store_docs:
        raise SystemExit(f"no store reviews on disk: {RAW_PATH} (run without --no-ingest)")

    store_labeled: list[dict[str, Any]] = []
    store_claims: list[dict[str, Any]] = []
    for doc in store_docs:
        labeled, claims = extract_document(doc)
        store_labeled.append(labeled)
        store_claims.extend(claims)
    write_jsonl(LABELED_PATH, store_labeled)
    write_jsonl(CLAIMS_PATH, store_claims)

    combined_claims = reddit_claims + store_claims
    write_jsonl(COMBINED_CLAIMS_PATH, combined_claims)
    combined_labeled = reddit_labeled + store_labeled
    combined_docs = reddit_raw + store_docs
    docs_by_id = index_by_id(combined_docs)

    clustered = cluster_claims(combined_claims, docs_by_id)
    corpus, area_quant = quantify_all(clustered, combined_labeled, combined_docs)
    ranked = rank_areas(area_quant)
    answers = answer_questions(clustered)
    coverage = coverage_summary(answers)
    corr = corroboration_table(area_quant)
    keywords = keyword_doc_count(store_docs)

    ground = groundedness_sample(clustered, docs_by_id)
    draft = render_report(
        phase1=read_json(PHASE1_MANIFEST),
        phase2=read_json(PHASE2_MANIFEST),
        ingest=ingest_payload,
        corpus=corpus,
        ranked=ranked,
        answers=answers,
        coverage=coverage,
        clustered=clustered,
        corroboration=corr,
        evals={"instant_fail_clear": True, "groundedness": ground},
        keyword_docs=keywords,
    )
    instant = instant_fail_checks(
        report=draft,
        ranked=ranked,
        answers=answers,
        coverage=coverage,
        corpus=corpus,
        claims=clustered,
        corroboration=corr,
    )
    report = render_report(
        phase1=read_json(PHASE1_MANIFEST),
        phase2=read_json(PHASE2_MANIFEST),
        ingest=ingest_payload,
        corpus=corpus,
        ranked=ranked,
        answers=answers,
        coverage=coverage,
        clustered=clustered,
        corroboration=corr,
        evals={"instant_fail_clear": instant["clear"], "groundedness": ground},
        keyword_docs=keywords,
    )

    write_jsonl(CLUSTERS_PATH, clustered)
    write_json(QUANT_PATH, {"corpus": corpus, "areas": area_quant})
    write_json(RANKING_PATH, ranked)
    write_json(QUESTIONS_PATH, {"coverage": coverage, "answers": answers})
    write_json(CORROBORATION_PATH, corr)
    write_json(RUBRIC_PATH, rubric_payload(ranked))
    write_json(LEDGER_PATH, build_ledger(clustered, ranked, answers))
    write_text(REPORT_PATH, report)
    write_eval_docs(instant, ground, coverage, ranked)
    write_manifest(
        corpus=corpus,
        ranked=ranked,
        coverage=coverage,
        evals={"instant_fail_clear": instant["clear"]},
        ingest=ingest_payload,
    )

    print(
        f"Done. store_docs={len(store_docs)} store_claims={len(store_claims)} "
        f"combined={len(clustered)} ranked={len(ranked)} "
        f"coverage={coverage['answered_or_partial']}/10 "
        f"instant_fail={'clear' if instant['clear'] else 'FAILED'} "
        f"groundedness={ground['verbatim_pct']:.0%}",
        flush=True,
    )
    print(f"Wrote {REPORT_PATH}", flush=True)
    return 0 if instant["clear"] and coverage["pass_8_of_10"] and ground["pass_verbatim"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
