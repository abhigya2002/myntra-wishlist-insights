"""Write the Reddit-only discovery report. No product pitch."""

from __future__ import annotations

from typing import Any

from config import MIN_RANKED_AREAS


def _md_quote(item: dict[str, Any]) -> str:
    quote = str(item.get("quote") or "").replace("\n", " ").strip()
    url = item.get("url") or ""
    claim_id = item.get("claim_id") or ""
    return f"> {quote}\n>\n> — `{claim_id}` · {url}"


def _pick_area_quotes(clustered: list[dict[str, Any]], area_id: str, n: int = 3) -> list[dict[str, Any]]:
    rows = [row for row in clustered if row.get("opportunity_id") == area_id]
    ranked = sorted(
        rows,
        key=lambda row: (
            0 if row.get("extractor") == "groq" else 1,
            0 if row.get("delay_or_dropoff_signal") == "yes" else 1,
            1 if row.get("after_purchase") else 0,
            1 if row.get("title_echo") else 0,
            -len(str(row.get("quote") or "")),
        ),
    )
    seen: set[str] = set()
    picked: list[dict[str, Any]] = []
    for row in ranked:
        url = str(row.get("url") or "")
        if url in seen:
            continue
        seen.add(url)
        picked.append(row)
        if len(picked) >= n:
            break
    return picked


def _metric_link(area: dict[str, Any]) -> str:
    stage = area.get("journey_stage") or "uncertainty_after_like"
    delay_pct = 100 * float(area.get("delay_share") or 0)
    after_pct = 100 * float(area.get("after_purchase_share") or 0)
    if area["id"] == "price_watch_and_checkout":
        return (
            "This sits on the path as **postpone**: the item is already chosen, then checkout "
            "math or a cheaper listing elsewhere stretches the gap past a 30-day window. "
            f"{delay_pct:.0f}% of its claims are tagged delay/drop-off. It is **not** ranked "
            "as a monetary incentive."
        )
    if area["id"] == "returns_and_order_trust":
        return (
            "Most quotes are **after a purchase or cancel**, not at wishlist-add. The metric "
            f"link is indirect: {after_pct:.0f}% read as after-purchase. If the reverse path "
            "looks broken, the next liked item is easier to leave unbought. That is weaker "
            "than review/fit hesitation-to-order, which is why this area is scored with a "
            "lower metric prior."
        )
    if area["id"] == "assortment_or_access_gap":
        return (
            "This often hits **before** a clean wishlist add (scrolled, found nothing). It can "
            "still starve 30-day conversion by never creating a convertible shortlist. Treat "
            "it as an upstream leak, not as 'saved then stalled'."
        )
    return (
        f"Journey placement: **{stage.replace('_', ' ')}**. "
        f"{delay_pct:.0f}% of claims in this area carry an explicit delay/drop-off tag. "
        "The behavior is residual uncertainty or a workaround after the product is already "
        "in play — the window between like/save and a 30-day purchase — not generic app hate."
    )


def _source_block(
    phase1: dict[str, Any],
    phase2: dict[str, Any],
    corpus: dict[str, Any],
) -> list[str]:
    window = phase1.get("time_window") or {}
    pulled = phase1.get("pulled_at") or "unknown"
    p2_at = phase2.get("ran_at") or "unknown"
    return [
        "## Version and source mix",
        "",
        "| Field | Value |",
        "|---|---|",
        "| Product | Myntra |",
        "| Draft | Phase 3 Reddit-only (Play/App Store not ingested) |",
        f"| Reddit pull | {pulled} via `{phase1.get('adapter') or 'unknown'}` |",
        f"| Time window | {window.get('start')} → {window.get('end')} ({window.get('duration_months')} months) |",
        f"| Raw Reddit docs | {corpus.get('raw_docs')} |",
        f"| Phase 2 labels | {corpus.get('labeled_docs')} "
        f"(in-scope {corpus.get('in_scope_docs')}: "
        f"myntra_primary {corpus.get('by_label', {}).get('myntra_primary', 0)}, "
        f"fashion_context {corpus.get('by_label', {}).get('fashion_context', 0)}) |",
        f"| Phase 2 run | {p2_at}, Groq + heuristic |",
        f"| Claims | {corpus.get('claims_total')} quote-backed "
        f"({corpus.get('extractor', {}).get('groq', 0)} Groq / "
        f"{corpus.get('extractor', {}).get('heuristic', 0)} heuristic) |",
        f"| Reddit share of this draft | {100 * float(corpus.get('reddit_share') or 0):.0f}% |",
        "| Other sources | None. Play Store, App Store, communities, social, YouTube, and product Q&A are **Gaps** for later phases. |",
        "",
        "Competitor names (AJIO, Nykaa, Flipkart, Amazon) appear only as comparison context.",
        "",
    ]


def _questions_block(answers: list[dict[str, Any]], summary: dict[str, Any]) -> list[str]:
    lines = [
        "## Ten discovery questions",
        "",
        f"Coverage: **{summary['answered_or_partial']}/10** Answered or Partial "
        f"({summary['answered']} Answered, {summary['partial']} Partial, {summary['gap']} Gap). "
        "Every Gap is named. Silence is not used.",
        "",
    ]
    for row in answers:
        lines.append(f"### Q{row['id']}. {row['question']}")
        lines.append("")
        lines.append(f"**{row['coverage']}** · {row['claim_count']} claims · {row['thread_count']} threads")
        lines.append("")
        lines.append(row["answer"])
        lines.append("")
        if row.get("evidence") and row["coverage"] != "Gap":
            for item in row["evidence"]:
                lines.append(_md_quote(item))
                lines.append("")
        elif row["id"] in {1, 8}:
            lines.append(
                "_No verbatim wishlist-add quote was available to print. "
                "That absence is the finding._"
            )
            lines.append("")
    return lines


def _ranking_block(ranked: list[dict[str, Any]], clustered: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## Ranked opportunity areas",
        "",
        "These are **user behaviors or uncertainties**, not feature ideas. "
        "Rank is the Phase 3 deliverable. Prose exists to make the comparison readable.",
        "",
        "| Rank | Area | Score | Claims | Threads | Delay | Non-monetary |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in ranked:
        lines.append(
            f"| {row['rank']} | {row['title']} | {row['score']:.1f} | "
            f"{row['claim_count']} | {row['thread_count']} | "
            f"{100 * float(row['delay_share']):.0f}% | "
            f"{'no (price evidence)' if row['monetary'] else 'yes'} |"
        )
    lines.extend(["", "### Rubric", ""])
    lines.append(
        "Each area is scored `100 * (0.30 metric relevance + 0.25 evidence + "
        "0.20 delay/drop-off + 0.15 constraint fit + 0.10 segment honesty)`. "
        "Segment honesty is 1.0 because this draft does not invent personas."
    )
    lines.append("")
    for row in ranked:
        quotes = _pick_area_quotes(clustered, row["id"], 3)
        lines.append(f"### {row['rank']}. {row['title']}")
        lines.append("")
        lines.append(f"**Behavior / uncertainty.** {row['behavior']}")
        lines.append("")
        lines.append(f"**Metric link.** {_metric_link(row)}")
        lines.append("")
        lines.append(
            f"**Quantification.** {row['claim_count']} claims in {row['doc_count']} docs "
            f"/ {row['thread_count']} threads "
            f"({100 * float(row['claim_share']):.1f}% of all claims; "
            f"{100 * float(row['in_scope_doc_share']):.1f}% of in-scope labeled docs). "
            f"Myntra-primary {row['myntra_primary']}, fashion-context {row['fashion_context']}. "
            f"Reddit 100%. Delay/drop-off on {row['delay_yes']} claims. "
            f"Price mentioned on {row['price_mentioned']}. "
            f"Groq-extracted {row['extractor_groq']}."
        )
        lines.append("")
        lines.append(f"**Comparison.** {row['comparison']}")
        lines.append("")
        lines.append("**Evidence (Reddit).**")
        lines.append("")
        if quotes:
            for item in quotes:
                lines.append(_md_quote(item))
                lines.append("")
        else:
            lines.append("_No independent quote survived filters._")
            lines.append("")
        claim_ids = ", ".join(f"`{cid}`" for cid in (row.get("claim_ids") or [])[:12])
        extra = "" if len(row.get("claim_ids") or []) <= 12 else ", …"
        lines.append(f"Ledger claim ids: {claim_ids}{extra}")
        lines.append("")
    if len(ranked) < MIN_RANKED_AREAS:
        lines.append(
            f"_Warning: fewer than {MIN_RANKED_AREAS} comparable areas. "
            "This draft would fail the ranking eval._"
        )
        lines.append("")
    return lines


def _constraint_block(ranked: list[dict[str, Any]]) -> list[str]:
    non_mon = [row for row in ranked if not row.get("monetary")]
    monetary = [row for row in ranked if row.get("monetary")]
    lines = [
        "## What is not solvable with a discount",
        "",
        "Price and sale-waiting **are captured** when present. A coupon is **not** ranked.",
        "",
    ]
    if non_mon:
        names = "; ".join(f"{row['rank']}. {row['title']}" for row in non_mon[:6])
        lines.append(f"Non-monetary top areas: {names}.")
        lines.append("")
    if monetary:
        names = "; ".join(row["title"] for row in monetary)
        lines.append(
            f"Monetary evidence area ({names}): keep it as a description of delay, "
            "not as an intervention. The hard constraint still applies."
        )
        lines.append("")
    else:
        lines.append("No ranked area is a discount recommendation.")
        lines.append("")
    return lines


def _gaps_block(
    answers: list[dict[str, Any]],
    corpus: dict[str, Any],
    phase2_gate_pending: bool,
) -> list[str]:
    gaps = [row for row in answers if row["coverage"] == "Gap"]
    lines = ["## Gaps", ""]
    lines.append("### Named question Gaps")
    lines.append("")
    if gaps:
        for row in gaps:
            lines.append(f"- **Q{row['id']} {row['question']}** — {row['answer']}")
        lines.append("")
    else:
        lines.append("None.")
        lines.append("")
    lines.extend(
        [
            "### Source-mix Gaps (expected for a Reddit-only draft)",
            "",
            "- Play Store / App Store not ingested — app friction, size-chart UI, and trust-at-volume are untested.",
            "- Fashion/shopping communities beyond the Reddit pull are not ingested.",
            "- Instagram, YouTube hauls, and product Q&A are not ingested (Q6/Q7 may be under-counted).",
            "- Private WhatsApp / DMs are out of scope (interview territory, not ingest).",
            "",
            "### Corpus and process Gaps",
            "",
            f"- Explicit wishlist language is almost absent "
            f"({corpus.get('wishlist_explicit_claims')} explicit / "
            f"{corpus.get('wishlist_implied_claims')} implied wishlist signals on claims).",
            "- Phase 2 stopped Groq on daily quota; many later docs used heuristics "
            f"({corpus.get('extractor', {}).get('heuristic', 0)} heuristic claims). "
            "Re-run Phase 2 after quota reset if labels need to be sharpened.",
            "- Comparison of 2–3 saved items inside Myntra is thin (Q5 Partial).",
            "- Segments are thin and only ethnic/western and size-insecure are earned (Q9 Partial).",
        ]
    )
    if phase2_gate_pending:
        lines.append(
            "- Phase 2 15-doc human gate check is still pending in `GATE_CHECK.md` "
            "(evals.md §8). This draft still runs so ranking can be reviewed."
        )
    lines.append("")
    return lines


def _anti_solution_block() -> list[str]:
    return [
        "## What this draft is not",
        "",
        "This is a research ranking for later parts. It does **not** propose an MVP, "
        "an in-app feature, an interview guide, or a metric tree. AJIO/Nykaa are not "
        "the product under study.",
        "",
    ]


def render_report(
    *,
    phase1: dict[str, Any],
    phase2: dict[str, Any],
    corpus: dict[str, Any],
    ranked: list[dict[str, Any]],
    answers: list[dict[str, Any]],
    coverage: dict[str, Any],
    clustered: list[dict[str, Any]],
    evals: dict[str, Any],
    phase2_gate_pending: bool,
) -> str:
    instant = "all clear" if evals.get("instant_fail_clear") else "FAILED"
    ground = evals.get("groundedness") or {}
    lines = [
        "# Discovery report — Reddit-only draft (Phase 3)",
        "",
        "North-star in scope: **% of Myntra users who purchase at least one wishlisted item "
        "within 30 days of adding it.** Hard constraint: no monetary incentive as the opportunity.",
        "",
        f"Instant-fail self-check: **{instant}**. "
        f"Groundedness sample: {ground.get('checked', 0)} claims, "
        f"verbatim {ground.get('verbatim_pct', 0):.0%}, "
        f"url {ground.get('url_pct', 0):.0%}, "
        f"question-fit {ground.get('question_pct', 0):.0%}.",
        "",
    ]
    lines += _source_block(phase1, phase2, corpus)
    lines += _questions_block(answers, coverage)
    lines += _ranking_block(ranked, clustered)
    lines += _constraint_block(ranked)
    lines += _gaps_block(answers, corpus, phase2_gate_pending)
    lines += _anti_solution_block()
    lines += [
        "## How to re-run",
        "",
        "```text",
        "cd Phases/Phase3_RankedDraft",
        "python run.py --dry-run",
        "python run.py",
        "```",
        "",
        "Inputs: Phase 1 `reddit_documents.jsonl`, Phase 2 `reddit_claims.jsonl` + `reddit_labeled.jsonl`.",
        "Outputs: `output/discovery-report.md`, `output/evidence-ledger.json`, `data/derived/`.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"
