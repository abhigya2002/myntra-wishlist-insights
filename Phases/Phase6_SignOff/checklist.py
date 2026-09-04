"""Part 1 sign-off checklist (evals.md §9) plus process evals (§8).

Checks Phase 5 artifacts as the canonical mixed-source draft. Items are
pass/fail with notes; the overall sign-off is clear only when every required
item passes.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from config import (
    MIN_COVERAGE,
    MIN_GATE_SAMPLE,
    MIN_RANKED_AREAS,
    PHASE1_RAW,
    PHASE2_CLAIMS,
    PHASE2_GATE_CHECK,
    PHASE2_LABELED,
    PHASE4_RAW,
    SOURCE_EVAL_NOTES,
    SOURCE_GROUNDEDNESS,
    SOURCE_INSTANT_FAIL,
    SOURCE_LEDGER,
    SOURCE_MANIFEST,
    SOURCE_QUESTIONS,
    SOURCE_RANKING,
    SOURCE_REPORT,
    SOURCE_WISHLIST,
)
from io_util import count_jsonl, read_json


def _item(name: str, ok: bool, note: str, *, required: bool = True) -> dict[str, Any]:
    return {"name": name, "pass": ok, "note": note, "required": required}


def _parse_groundedness(text: str, eval_notes: str) -> bool:
    if "| Groundedness sample | PASS |" in eval_notes:
        return True
    if not text:
        return False
    # Phase 5 table uses "PASS" on each bar row when clear.
    fail_cells = re.findall(r"\|[^|\n]+\|[^|\n]+\|[^|\n]+\|\s*FAIL\s*\|", text)
    return "Sample size:" in text and "PASS" in text and not fail_cells


def _gate_accuracy(text: str) -> tuple[bool, str]:
    if "Status: checked" not in text:
        return False, "GATE_CHECK.md not marked checked"
    match = re.search(r"Accuracy \(human == system\):\s*([\d.]+)%\s*\((\d+)/(\d+)\)", text)
    if not match:
        return False, "accuracy line missing"
    pct, ok_n, total = float(match.group(1)), int(match.group(2)), int(match.group(3))
    passed = total >= MIN_GATE_SAMPLE and ok_n == total
    return passed, f"{ok_n}/{total} ({pct:.0f}%), sample>={MIN_GATE_SAMPLE}"


def run_checklist() -> dict[str, Any]:
    manifest = read_json(SOURCE_MANIFEST)
    ranking = read_json(SOURCE_RANKING) if SOURCE_RANKING.is_file() else []
    if isinstance(ranking, dict):
        ranking = ranking.get("ranked") or ranking.get("areas") or []
    questions_payload = read_json(SOURCE_QUESTIONS)
    coverage = questions_payload.get("coverage") or manifest.get("question_coverage") or {}
    answers = questions_payload.get("answers") or []
    wishlist = read_json(SOURCE_WISHLIST) or manifest.get("wishlist_evidence") or {}
    corpus = manifest.get("corpus") or {}

    report = SOURCE_REPORT.read_text(encoding="utf-8") if SOURCE_REPORT.is_file() else ""
    instant_text = SOURCE_INSTANT_FAIL.read_text(encoding="utf-8") if SOURCE_INSTANT_FAIL.is_file() else ""
    ground_text = SOURCE_GROUNDEDNESS.read_text(encoding="utf-8") if SOURCE_GROUNDEDNESS.is_file() else ""
    gate_text = PHASE2_GATE_CHECK.read_text(encoding="utf-8") if PHASE2_GATE_CHECK.is_file() else ""
    eval_notes = SOURCE_EVAL_NOTES.read_text(encoding="utf-8") if SOURCE_EVAL_NOTES.is_file() else ""

    instant_clear = (
        bool(manifest.get("instant_fail_clear"))
        or "Overall: **CLEAR**" in instant_text
        or "Overall: CLEAR" in instant_text
    )
    ground_ok = _parse_groundedness(ground_text, eval_notes)

    covered = int(coverage.get("answered_or_partial") or 0)
    gaps = int(coverage.get("gap") or 0)
    coverage_ok = covered >= MIN_COVERAGE and bool(coverage.get("pass_8_of_10", covered >= MIN_COVERAGE))
    # Gaps must be named when present; Phase 5 has 0 gaps.
    gaps_named = gaps == 0 or (
        "## Gaps" in report and (gaps == 0 or "Q" in report.split("## Gaps", 1)[-1][:800])
    )

    ranked_n = len(ranking) if isinstance(ranking, list) else int(manifest.get("ranked_areas") or 0)
    has_comparison = all(bool(row.get("comparison")) for row in ranking) if ranking else False
    if not ranking and ranked_n >= MIN_RANKED_AREAS:
        has_comparison = "Comparison" in report or "**Comparison.**" in report

    reddit_claims = int(corpus.get("reddit_claim_count") or 0)
    ranked_have_reddit = True
    if ranking:
        ranked_have_reddit = all(int(row.get("reddit_claim_count") or 0) >= 1 for row in ranking)
    reddit_primary = ranked_have_reddit and reddit_claims > 0 and "Reddit" in report

    non_monetary = []
    monetary = []
    for row in ranking if isinstance(ranking, list) else []:
        if row.get("monetary"):
            monetary.append(row.get("id") or row.get("title"))
        else:
            non_monetary.append(row.get("id") or row.get("title"))
    coupon_pitch = bool(
        re.search(r"\b(we should|recommend|offer)\b.{0,40}\b(coupon|cashback|discount)\b", report, re.I)
    )
    non_mon_ok = (len(non_monetary) >= 1 or "Non-monetary" in report) and not coupon_pitch

    q1 = next((a for a in answers if a.get("id") == 1), {})
    q8 = next((a for a in answers if a.get("id") == 8), {})
    wishlist_claims = int(wishlist.get("claims") or 0)
    intent_ok = (
        q8.get("coverage") in {"Partial", "Answered"}
        and wishlist_claims >= 1
        and (
            "bookmark" in str(q8.get("answer") or "").lower()
            or "bookmark" in str(wishlist.get("reading") or "").lower()
            or "Bookmark-style" in report
        )
    )

    no_solution = (
        "Not an MVP" in report or "What this draft is not" in report
    ) and not bool(
        re.search(
            r"\b(we should build|our mvp|build an mvp|recommend building|"
            r"here is (an |the )?interview plan|proposed mvp)\b",
            report,
            re.I,
        )
    )

    path_recorded = SOURCE_REPORT.is_file() and SOURCE_LEDGER.is_file()

    items = [
        _item(
            "Instant-fail table is all clear",
            instant_clear,
            f"Phase 5 instant_fail_clear={manifest.get('instant_fail_clear')}; "
            f"INSTANT_FAIL.md={'CLEAR' if 'CLEAR' in instant_text else 'missing/failed'}",
        ),
        _item(
            "Question coverage ≥ 8/10 Answered or Partial; Gaps named",
            coverage_ok and gaps_named,
            f"answered_or_partial={covered}/10 gaps={gaps} gaps_named={gaps_named}",
        ),
        _item(
            "Reddit is the primary evidence base",
            reddit_primary,
            f"reddit_claims={reddit_claims}; every ranked area has Reddit claims={ranked_have_reddit}",
        ),
        _item(
            "20-claim groundedness sample passed",
            ground_ok and SOURCE_GROUNDEDNESS.is_file(),
            "Phase 5 GROUNDEDNESS.md / EVAL_NOTES",
        ),
        _item(
            "≥ 5 ranked opportunity areas with quantification and comparison",
            ranked_n >= MIN_RANKED_AREAS and (has_comparison or "**Comparison.**" in report),
            f"ranked={ranked_n} comparison_fields={has_comparison}",
        ),
        _item(
            "Non-monetary opportunities identified (or price-dominance named without a coupon pitch)",
            non_mon_ok,
            f"non_monetary={len(non_monetary)} monetary={len(monetary)} coupon_pitch={coupon_pitch}",
        ),
        _item(
            "Intent vs bookmark addressed with evidence",
            intent_ok,
            f"Q1={q1.get('coverage')} Q8={q8.get('coverage')} wishlist_claims={wishlist_claims} "
            f"reading={wishlist.get('reading')}",
        ),
        _item(
            "No solution / MVP / interview plan presented as the Part 1 output",
            no_solution,
            "report states draft is not an MVP / interview plan",
        ),
        _item(
            "Discovery report path recorded for Parts 2–4",
            path_recorded,
            f"report={SOURCE_REPORT} ledger={SOURCE_LEDGER}",
        ),
    ]

    gate_ok, gate_note = _gate_accuracy(gate_text)
    process = [
        _item("Raw corpus retained", PHASE1_RAW.is_file() and count_jsonl(PHASE1_RAW) > 0,
              f"Phase1 Reddit docs={count_jsonl(PHASE1_RAW)}; Phase4 store={count_jsonl(PHASE4_RAW)}"),
        _item("Relevance labels exist", PHASE2_LABELED.is_file() and count_jsonl(PHASE2_LABELED) > 0,
              f"Phase2 labeled={count_jsonl(PHASE2_LABELED)}; claims={count_jsonl(PHASE2_CLAIMS)}"),
        _item(
            "Sample of relevance-gate labels human-checked (≥ 15)",
            gate_ok,
            gate_note,
        ),
        _item(
            "Report version notes source mix and date of pull",
            "Version and source mix" in report and ("pulled" in report.lower() or "pull" in report.lower()),
            "Phase 5 discovery-report source mix table",
        ),
        _item(
            "Re-run path is documented",
            "How to re-run" in report or "python run.py" in report,
            "re-run section in Phase 5 report / phase READMEs",
            required=True,
        ),
    ]

    required_pass = all(item["pass"] for item in items if item["required"])
    process_pass = all(item["pass"] for item in process if item["required"])
    return {
        "sign_off_clear": required_pass and process_pass,
        "checklist": items,
        "process_evals": process,
        "source_draft": "phase5_reddit_primary_store_corroboration_wishlist_expansion",
        "coverage": coverage,
        "ranked_areas": ranked_n,
        "wishlist": {
            "claims": wishlist_claims,
            "threads": wishlist.get("threads"),
            "reading": wishlist.get("reading"),
            "q1": q1.get("coverage"),
            "q8": q8.get("coverage"),
        },
        "caveats": _caveats(wishlist, coverage, report),
    }


def _caveats(wishlist: dict[str, Any], coverage: dict[str, Any], report: str) -> list[str]:
    notes: list[str] = []
    if wishlist.get("claims", 0) < 20:
        notes.append(
            f"Q1/Q8 are Partial on a thin wishlist base "
            f"({wishlist.get('claims', 0)} claims / {wishlist.get('threads', 0)} threads). "
            "Direction is evidence-backed; strength is limited because the Phase 5 sweep was truncated."
        )
    if int(coverage.get("partial") or 0) > 0:
        notes.append(
            f"{coverage.get('partial')} discovery questions remain Partial "
            "(acceptable under evals.md; not silent Gaps)."
        )
    if "truncated" in report.lower() or "stopped before" in report.lower():
        notes.append(
            "Phase 5 standing limitations note a truncated wishlist sweep; "
            "re-running Phase 5 with --force can extend the corpus later."
        )
    notes.append(
        "No internal Myntra wishlist→purchase conversion rate is available. "
        "Part 1 ranks opportunity areas from public evidence only."
    )
    return notes


def render_sign_off(result: dict[str, Any], *, frozen_report: Path, frozen_ledger: Path) -> str:
    status = "SIGNED OFF" if result["sign_off_clear"] else "NOT CLEAR"
    lines = [
        "# Part 1 sign-off (evals.md §9)",
        "",
        f"**Status: {status}**",
        "",
        f"Canonical draft: Phase 5 (`{result['source_draft']}`).",
        "",
        "## Checklist",
        "",
        "| Check | Result | Note |",
        "|---|---|---|",
    ]
    for item in result["checklist"]:
        mark = "PASS" if item["pass"] else "FAIL"
        lines.append(f"| {item['name']} | {mark} | {item['note']} |")
    lines += [
        "",
        "## Frozen artifacts for Parts 2–4",
        "",
        f"- Discovery report: `{frozen_report}`",
        f"- Evidence ledger: `{frozen_ledger}`",
        "",
        "## Caveats carried into Part 2",
        "",
    ]
    for note in result.get("caveats") or []:
        lines.append(f"- {note}")
    lines += [
        "",
        "## What this sign-off is not",
        "",
        "- Not an MVP, interview plan, or metric tree.",
        "- Not a claim that wishlist conversion % was measured inside Myntra.",
        "- Not permission to treat Partial questions as Answered.",
        "",
    ]
    return "\n".join(lines)


def render_process_evals(result: dict[str, Any]) -> str:
    lines = [
        "# Process evals (evals.md §8)",
        "",
        "| Check | Result | Note |",
        "|---|---|---|",
    ]
    for item in result["process_evals"]:
        mark = "PASS" if item["pass"] else "FAIL"
        lines.append(f"| {item['name']} | {mark} | {item['note']} |")
    lines.append("")
    return "\n".join(lines)
