"""Instant-fail + groundedness for the mixed-source draft."""

from __future__ import annotations

import sys
from typing import Any

from config import MIN_RANKED_AREAS, PHASE3_DIR

if str(PHASE3_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE3_DIR))

from evals_check import (  # noqa: E402
    DISCOUNT_TITLE_RE,
    PITCH_RE,
    groundedness_sample,
    render_eval_notes,
    render_groundedness,
    render_instant_fail,
)


def instant_fail_checks(
    *,
    report: str,
    ranked: list[dict[str, Any]],
    answers: list[dict[str, Any]],
    coverage: dict[str, Any],
    corpus: dict[str, Any],
    claims: list[dict[str, Any]],
    corroboration: list[dict[str, Any]],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, why: str) -> None:
        checks.append({"name": name, "pass": ok, "note": why})

    add(
        "Output is ranked, not a sentiment dump",
        len(ranked) >= MIN_RANKED_AREAS and "Ranked opportunity areas" in report,
        f"{len(ranked)} ranked areas",
    )
    add("Opportunity areas are not a product pitch", not PITCH_RE.search(report), "no MVP pitch language")
    missing_quote = sum(1 for row in claims if not str(row.get("quote") or "").strip())
    missing_url = sum(1 for row in claims if not str(row.get("url") or "").strip())
    add(
        "Claims have verbatim quotes and source URLs",
        missing_quote == 0 and missing_url == 0,
        f"missing_quote={missing_quote} missing_url={missing_url}",
    )
    reddit_on_rank = all(int(row.get("reddit_claim_count") or 0) >= 1 for row in ranked) if ranked else False
    reddit_claims = int(corpus.get("reddit_claim_count") or 0)
    store_claims = int(corpus.get("store_claim_count") or 0)
    add(
        "Reddit is the primary evidence base for ranked areas",
        reddit_on_rank and reddit_claims > 0,
        f"every ranked area has Reddit claims; reddit_claims={reddit_claims} store_claims={store_claims}",
    )
    store_used = any(int(row.get("store_claims") or 0) >= 1 for row in corroboration)
    add(
        "Play/App Store used as corroboration, not the whole story",
        store_used and "corroborate" in report.lower(),
        f"corroboration rows with store={sum(1 for row in corroboration if row.get('store_claims'))}",
    )
    add(
        "Discount is not ranked as the opportunity",
        not any(DISCOUNT_TITLE_RE.search(str(row.get("title") or "")) for row in ranked),
        "no coupon intervention in the ranked list",
    )
    q8 = next((row for row in answers if row["id"] == 8), {})
    add(
        "Every wishlist add is not treated as purchase intent",
        q8.get("coverage") == "Gap" or "bookmark" in str(q8.get("answer") or "").lower(),
        f"Q8={q8.get('coverage')}",
    )
    add(
        "Segments are not asserted without quotes",
        "No personas were invented" in report or "earned" in report.lower(),
        "Q9 stays earned-only",
    )
    add("Myntra is the product", "myntra" in report.lower() and "protagonist is ajio" not in report.lower(), "Myntra subject")
    add(
        "All ten discovery questions are attempted",
        all(f"### Q{i}." in report for i in range(1, 11)) and bool(coverage.get("pass_8_of_10")),
        f"answered_or_partial={coverage.get('answered_or_partial')}/10",
    )
    add("Source counts appear in the report", "Play Store" in report and "App Store" in report, "store counts present")
    return {"clear": all(item["pass"] for item in checks), "checks": checks}


def write_eval_docs(instant: dict[str, Any], ground: dict[str, Any], coverage: dict[str, Any], ranked: list[dict[str, Any]]) -> None:
    from config import EVAL_SUMMARY_PATH, GROUNDEDNESS_PATH, INSTANT_FAIL_PATH
    from io_util import write_text

    write_text(INSTANT_FAIL_PATH, render_instant_fail(instant))
    write_text(GROUNDEDNESS_PATH, render_groundedness(ground))
    ground_pass = (
        ground["pass_verbatim"] and ground["pass_url"] and ground["pass_quote"] and ground["pass_questions"]
    )
    notes = "\n".join(
        [
            "# Phase 4 eval notes",
            "",
            "Mixed-source draft. Reddit is primary; Play/App Store corroborate Reddit themes.",
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
            "Part 1 sign-off is **not** claimed. Phase 5 is optional if Gaps remain. Phase 6 is sign-off.",
            "",
        ]
    )
    write_text(EVAL_SUMMARY_PATH, notes)
