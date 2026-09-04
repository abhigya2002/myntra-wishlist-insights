"""Phase 3 CLI: cluster → quantify → rank → Reddit-only discovery draft + evals."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PHASE3_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PHASE3_DIR))

from cluster import cluster_claims  # noqa: E402
from config import (  # noqa: E402
    CLUSTERS_PATH,
    EVAL_SUMMARY_PATH,
    GROUNDEDNESS_PATH,
    INSTANT_FAIL_PATH,
    LEDGER_PATH,
    MANIFEST_PATH,
    PHASE1_MANIFEST,
    PHASE1_RAW,
    PHASE2_CLAIMS,
    PHASE2_EVAL,
    PHASE2_LABELED,
    PHASE2_MANIFEST,
    QUANT_PATH,
    QUESTIONS_PATH,
    RANKING_PATH,
    REPORT_PATH,
    RUBRIC_PATH,
)
from evals_check import (  # noqa: E402
    groundedness_sample,
    instant_fail_checks,
    render_eval_notes,
    render_groundedness,
    render_instant_fail,
)
from load import index_by_id, read_json, read_jsonl, write_json, write_jsonl, write_text  # noqa: E402
from quantify import quantify_all  # noqa: E402
from questions import answer_questions, coverage_summary  # noqa: E402
from rank import rank_areas, rubric_payload  # noqa: E402
from report import render_report  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def gate_check_pending(text: str) -> bool:
    lower = text.lower()
    return "awaiting human" in lower or "|  |" in text or "checker: pending" in lower


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
                "quote_verified": row.get("quote_verified"),
                "discovery_question_ids": row.get("discovery_question_ids"),
                "theme": row.get("theme"),
                "opportunity_id": row.get("opportunity_id"),
                "thread_id": row.get("thread_id"),
                "gate_label": row.get("gate_label"),
                "stage": row.get("stage"),
                "delay_or_dropoff_signal": row.get("delay_or_dropoff_signal"),
                "price_mentioned": row.get("price_mentioned"),
                "non_monetary_need": row.get("non_monetary_need"),
                "segment_signals": row.get("segment_signals"),
                "extractor": row.get("extractor"),
                "confidence": row.get("confidence"),
            }
        )
    return {
        "phase": 3,
        "product": "Myntra",
        "source_mix": ["reddit"],
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
) -> None:
    write_json(
        MANIFEST_PATH,
        {
            "phase": 3,
            "product": "Myntra",
            "draft": "reddit_only",
            "ran_at": utc_now(),
            "inputs": {
                "raw": str(PHASE1_RAW),
                "labeled": str(PHASE2_LABELED),
                "claims": str(PHASE2_CLAIMS),
            },
            "corpus": corpus,
            "ranked_areas": len(ranked),
            "ranking": [{"rank": row["rank"], "id": row["id"], "score": row["score"]} for row in ranked],
            "question_coverage": coverage,
            "instant_fail_clear": evals.get("instant_fail_clear"),
            "groundedness": {
                "checked": (evals.get("groundedness") or {}).get("checked"),
                "verbatim_pct": (evals.get("groundedness") or {}).get("verbatim_pct"),
                "pass": (evals.get("groundedness") or {}).get("pass_verbatim"),
            },
            "files": {
                "report": str(REPORT_PATH),
                "ledger": str(LEDGER_PATH),
                "clusters": str(CLUSTERS_PATH),
                "ranking": str(RANKING_PATH),
                "instant_fail": str(INSTANT_FAIL_PATH),
                "groundedness": str(GROUNDEDNESS_PATH),
            },
            "re_run": "python run.py",
        },
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 3 Myntra Reddit-only ranked discovery draft")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.dry_run:
        print("Phase 3 dry-run")
        print(f"  raw:     {PHASE1_RAW} exists={PHASE1_RAW.is_file()}")
        print(f"  labeled: {PHASE2_LABELED} exists={PHASE2_LABELED.is_file()}")
        print(f"  claims:  {PHASE2_CLAIMS} exists={PHASE2_CLAIMS.is_file()}")
        print(f"  report -> {REPORT_PATH}")
        print(f"  ledger -> {LEDGER_PATH}")
        print("  steps: cluster -> quantify -> rank -> 10 questions -> report -> evals")
        return 0

    raw_docs = read_jsonl(PHASE1_RAW)
    labeled = read_jsonl(PHASE2_LABELED)
    claims = read_jsonl(PHASE2_CLAIMS)
    if not raw_docs:
        raise SystemExit(f"missing Phase 1 corpus: {PHASE1_RAW}")
    if not claims:
        raise SystemExit(f"missing Phase 2 claims: {PHASE2_CLAIMS}")

    docs_by_id = index_by_id(raw_docs)
    clustered = cluster_claims(claims, docs_by_id)
    corpus, area_quant = quantify_all(clustered, labeled, raw_docs)
    ranked = rank_areas(area_quant)
    answers = answer_questions(clustered)
    coverage = coverage_summary(answers)
    phase1 = read_json(PHASE1_MANIFEST)
    phase2 = read_json(PHASE2_MANIFEST)
    gate_notes = PHASE2_EVAL.read_text(encoding="utf-8") if PHASE2_EVAL.is_file() else ""
    pending = gate_check_pending(gate_notes) if gate_notes else True

    ground = groundedness_sample(clustered, docs_by_id)
    draft_report = render_report(
        phase1=phase1,
        phase2=phase2,
        corpus=corpus,
        ranked=ranked,
        answers=answers,
        coverage=coverage,
        clustered=clustered,
        evals={"instant_fail_clear": True, "groundedness": ground},
        phase2_gate_pending=pending,
    )
    instant = instant_fail_checks(
        report=draft_report,
        ranked=ranked,
        answers=answers,
        coverage=coverage,
        corpus=corpus,
        claims=clustered,
    )
    report = render_report(
        phase1=phase1,
        phase2=phase2,
        corpus=corpus,
        ranked=ranked,
        answers=answers,
        coverage=coverage,
        clustered=clustered,
        evals={"instant_fail_clear": instant["clear"], "groundedness": ground},
        phase2_gate_pending=pending,
    )

    write_jsonl(CLUSTERS_PATH, clustered)
    write_json(QUANT_PATH, {"corpus": corpus, "areas": area_quant})
    write_json(RANKING_PATH, ranked)
    write_json(QUESTIONS_PATH, {"coverage": coverage, "answers": answers})
    write_json(RUBRIC_PATH, rubric_payload(ranked))
    write_json(LEDGER_PATH, build_ledger(clustered, ranked, answers))
    write_text(REPORT_PATH, report)
    write_text(INSTANT_FAIL_PATH, render_instant_fail(instant))
    write_text(GROUNDEDNESS_PATH, render_groundedness(ground))
    write_text(EVAL_SUMMARY_PATH, render_eval_notes(instant, ground, coverage, ranked))
    write_manifest(corpus=corpus, ranked=ranked, coverage=coverage, evals={
        "instant_fail_clear": instant["clear"],
        "groundedness": ground,
    })

    print(
        f"Done. claims={len(clustered)} clustered={corpus['claims_clustered']} "
        f"ranked={len(ranked)} coverage={coverage['answered_or_partial']}/10 "
        f"instant_fail={'clear' if instant['clear'] else 'FAILED'} "
        f"groundedness={ground['verbatim_pct']:.0%}",
        flush=True,
    )
    print(f"Wrote {REPORT_PATH}", flush=True)
    print(f"Wrote {LEDGER_PATH}", flush=True)
    return 0 if instant["clear"] and coverage["pass_8_of_10"] and ground["pass_verbatim"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
