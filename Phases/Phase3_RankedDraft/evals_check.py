"""Instant-fail table and 20-claim groundedness sample from evals.md."""

from __future__ import annotations

import random
import re
from typing import Any

from config import GROUNDEDNESS_SAMPLE_N, GROUNDEDNESS_SEED, MIN_RANKED_AREAS
from load import recover_verbatim_quote

QUESTION_IDS = set(range(1, 11))

PITCH_RE = re.compile(
    r"\b(we should build|build an mvp|our mvp|recommend a coupon|"
    r"offer cashback|feature we will ship)\b",
    re.I,
)
DISCOUNT_TITLE_RE = re.compile(r"^(give |offer ).*(discount|coupon|cashback)", re.I)


def _yes_no(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def groundedness_sample(
    claims: list[dict[str, Any]],
    docs_by_id: dict[str, dict[str, Any]],
    n: int = GROUNDEDNESS_SAMPLE_N,
    seed: int = GROUNDEDNESS_SEED,
) -> dict[str, Any]:
    pool = [row for row in claims if row.get("claim_id")]
    rng = random.Random(seed)
    if len(pool) <= n:
        sample = list(pool)
    else:
        sample = rng.sample(pool, n)
    rows = []
    verbatim_ok = 0
    url_ok = 0
    q_ok = 0
    quote_ok = 0
    for claim in sample:
        doc = docs_by_id.get(str(claim.get("doc_id") or ""), {})
        quote = str(claim.get("quote") or "")
        recovered = recover_verbatim_quote(quote, doc) if doc else None
        has_quote = bool(quote.strip())
        has_url = bool(str(claim.get("url") or "").strip()) and bool(claim.get("doc_id"))
        qids = [int(item) for item in (claim.get("discovery_question_ids") or []) if str(item).isdigit()]
        qids_ok = bool(qids) and all(qid in QUESTION_IDS for qid in qids)
        if recovered:
            verbatim_ok += 1
        if has_url:
            url_ok += 1
        if qids_ok:
            q_ok += 1
        if has_quote:
            quote_ok += 1
        rows.append(
            {
                "claim_id": claim.get("claim_id"),
                "doc_id": claim.get("doc_id"),
                "url": claim.get("url"),
                "verbatim": bool(recovered),
                "url_ok": has_url,
                "has_quote": has_quote,
                "questions_ok": qids_ok,
            }
        )
    total = len(sample) or 1
    return {
        "checked": len(sample),
        "verbatim_ok": verbatim_ok,
        "url_ok": url_ok,
        "quote_ok": quote_ok,
        "questions_ok": q_ok,
        "verbatim_pct": verbatim_ok / total,
        "url_pct": url_ok / total,
        "quote_pct": quote_ok / total,
        "question_pct": q_ok / total,
        "pass_verbatim": (verbatim_ok / total) >= 0.90,
        "pass_url": url_ok == len(sample),
        "pass_quote": quote_ok == len(sample),
        "pass_questions": (q_ok / total) >= 0.80,
        "sample": rows,
    }


def instant_fail_checks(
    *,
    report: str,
    ranked: list[dict[str, Any]],
    answers: list[dict[str, Any]],
    coverage: dict[str, Any],
    corpus: dict[str, Any],
    claims: list[dict[str, Any]],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, why: str) -> None:
        checks.append({"name": name, "pass": ok, "note": why})

    ranking_present = len(ranked) >= MIN_RANKED_AREAS and "Ranked opportunity areas" in report
    add(
        "Output is ranked, not a sentiment dump",
        ranking_present,
        f"{len(ranked)} ranked areas with scores" if ranking_present else "ranking missing or < 5",
    )
    pitch = bool(PITCH_RE.search(report))
    add("Opportunity areas are not a product pitch", not pitch, "no MVP or feature-pitch language")
    missing_quote = sum(1 for row in claims if not str(row.get("quote") or "").strip())
    missing_url = sum(1 for row in claims if not str(row.get("url") or "").strip())
    add(
        "Claims have verbatim quotes and source URLs",
        missing_quote == 0 and missing_url == 0,
        f"missing_quote={missing_quote} missing_url={missing_url}",
    )
    reddit_primary = float(corpus.get("reddit_share") or 0) >= 0.99
    add("Reddit is the primary evidence base", reddit_primary, f"reddit_share={corpus.get('reddit_share')}")
    discount_ranked = any(DISCOUNT_TITLE_RE.search(str(row.get("title") or "")) for row in ranked)
    add(
        "Discount is not ranked as the opportunity",
        not discount_ranked,
        "no ranked area is a coupon/cashback intervention",
    )
    q8 = next((row for row in answers if row["id"] == 8), {})
    wishlist_not_all_intent = q8.get("coverage") == "Gap" or "not the same as" in str(q8.get("answer") or "")
    add(
        "Every wishlist add is not treated as purchase intent",
        wishlist_not_all_intent,
        "Q8 is a named Gap; intent is not assumed",
    )
    invented = "persona" in report.lower() and "invented" in report.lower()
    add(
        "Segments are not asserted without quotes",
        invented or "No personas were invented" in report,
        "Q9 states segments are earned or absent",
    )
    ajio_hero = bool(re.search(r"ajio is the product|protagonist is ajio|nykaa growth", report, re.I))
    add("Myntra is the product (AJIO/Nykaa are comparison only)", not ajio_hero, "Myntra remains the subject")
    questions_attempted = all(f"### Q{i}." in report for i in range(1, 11))
    add(
        "All ten discovery questions are attempted",
        questions_attempted and bool(coverage.get("pass_8_of_10")),
        f"answered_or_partial={coverage.get('answered_or_partial')}/10",
    )
    passed = all(item["pass"] for item in checks)
    return {"clear": passed, "checks": checks}


def render_instant_fail(result: dict[str, Any]) -> str:
    lines = [
        "# Instant-fail table (evals.md §2)",
        "",
        f"Overall: **{'CLEAR' if result['clear'] else 'FAILED'}**",
        "",
        "| Check | Result | Note |",
        "|---|---|---|",
    ]
    for item in result["checks"]:
        lines.append(f"| {item['name']} | {_yes_no(item['pass'])} | {item['note']} |")
    lines.append("")
    return "\n".join(lines)


def render_groundedness(result: dict[str, Any]) -> str:
    lines = [
        "# Groundedness sample (evals.md §4)",
        "",
        f"Sample size: {result['checked']} (seed={GROUNDEDNESS_SEED})",
        "",
        "| Check | Value | Bar | Result |",
        "|---|---|---|---|",
        f"| Quote verbatim in stored doc | {result['verbatim_pct']:.0%} | ≥ 90% | {_yes_no(result['pass_verbatim'])} |",
        f"| URL / doc id resolves | {result['url_pct']:.0%} | 100% | {_yes_no(result['pass_url'])} |",
        f"| discovery_question_ids present and in 1–10 | {result['question_pct']:.0%} | ≥ 80% | {_yes_no(result['pass_questions'])} |",
        f"| No claim without a quote | {result['quote_pct']:.0%} | 100% | {_yes_no(result['pass_quote'])} |",
        "",
        "| claim_id | doc_id | verbatim | url | questions |",
        "|---|---|---|---|---|",
    ]
    for row in result["sample"]:
        lines.append(
            f"| `{row['claim_id']}` | `{row['doc_id']}` | "
            f"{'yes' if row['verbatim'] else 'NO'} | "
            f"{'yes' if row['url_ok'] else 'NO'} | "
            f"{'yes' if row['questions_ok'] else 'NO'} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_eval_notes(
    instant: dict[str, Any],
    ground: dict[str, Any],
    coverage: dict[str, Any],
    ranked: list[dict[str, Any]],
) -> str:
    ground_pass = (
        ground["pass_verbatim"] and ground["pass_url"] and ground["pass_quote"] and ground["pass_questions"]
    )
    lines = [
        "# Phase 3 eval notes",
        "",
        "Reddit-only draft. Source-mix Gaps for Play/App Store are expected and named in the report.",
        "",
        "| Eval | Result |",
        "|---|---|",
        f"| Instant-fail table | {'CLEAR' if instant['clear'] else 'FAILED'} |",
        f"| Question coverage ≥ 8/10 | {'PASS' if coverage.get('pass_8_of_10') else 'FAIL'} "
        f"({coverage.get('answered_or_partial')}/10) |",
        f"| Groundedness sample | {'PASS' if ground_pass else 'FAIL'} |",
        f"| Ranked areas ≥ 5 with comparison | {'PASS' if len(ranked) >= MIN_RANKED_AREAS else 'FAIL'} "
        f"({len(ranked)}) |",
        "",
        "Part 1 sign-off is **not** claimed. Phase 4+ still required for source mix.",
        "",
    ]
    return "\n".join(lines)
