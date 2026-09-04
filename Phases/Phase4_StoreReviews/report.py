"""Mixed-source discovery report. Reddit primary; stores corroborate."""

from __future__ import annotations

from typing import Any

from config import MIN_RANKED_AREAS


def _md_quote(item: dict[str, Any]) -> str:
    quote = str(item.get("quote") or "").replace("\n", " ").strip()
    url = item.get("url") or ""
    claim_id = item.get("claim_id") or ""
    source = item.get("source") or ""
    tag = f" [{source}]" if source and source != "reddit" else ""
    return f"> {quote}{tag}\n>\n> — `{claim_id}` · {url}"


def _pick_quotes(clustered: list[dict[str, Any]], area_id: str, *, source: str | None, n: int) -> list[dict[str, Any]]:
    rows = [row for row in clustered if row.get("opportunity_id") == area_id]
    if source:
        rows = [row for row in rows if (row.get("source") or "reddit") == source]
    ranked = sorted(
        rows,
        key=lambda row: (
            0 if row.get("extractor") == "groq" else 1,
            0 if row.get("delay_or_dropoff_signal") == "yes" else 1,
            1 if row.get("after_purchase") else 0,
            -len(str(row.get("quote") or "")),
        ),
    )
    seen: set[str] = set()
    picked: list[dict[str, Any]] = []
    for row in ranked:
        key = str(row.get("url") or row.get("claim_id") or "")
        if key in seen:
            continue
        seen.add(key)
        picked.append(row)
        if len(picked) >= n:
            break
    return picked


def _metric_link(area: dict[str, Any]) -> str:
    stage = str(area.get("journey_stage") or "").replace("_", " ")
    delay_pct = 100 * float(area.get("delay_share") or 0)
    if area["id"] == "price_watch_and_checkout":
        return (
            "Postpone via checkout math or a cheaper listing. Price talk is evidence. "
            "A monetary incentive is not the opportunity. "
            f"Delay/drop-off on {delay_pct:.0f}% of claims."
        )
    if area["id"] == "returns_and_order_trust":
        return (
            "Store reviews add volume on refunds, pickups, and late delivery. "
            "That is mostly after a purchase. The wishlist-window link is indirect: "
            "if the reverse path looks broken, the next liked item is easier to leave unbought."
        )
    if area["id"] == "app_friction":
        return (
            "App crash/login can block checkout of a saved item, but this is app hygiene, "
            "not residual fashion uncertainty. Ranked only if Reddit also speaks to it; "
            "otherwise it stays a store-volume note."
        )
    if area["id"] == "assortment_or_access_gap":
        return (
            "Often hits before a clean wishlist add (scrolled, found nothing). "
            "Treat as an upstream leak, not 'saved then stalled'."
        )
    return (
        f"Journey placement: **{stage}**. {delay_pct:.0f}% of claims carry delay/drop-off. "
        "This is residual uncertainty after a product is in play — the 30-day window — "
        "not generic app hate."
    )


def render_report(
    *,
    phase1: dict[str, Any],
    phase2: dict[str, Any],
    ingest: dict[str, Any],
    corpus: dict[str, Any],
    ranked: list[dict[str, Any]],
    answers: list[dict[str, Any]],
    coverage: dict[str, Any],
    clustered: list[dict[str, Any]],
    corroboration: list[dict[str, Any]],
    evals: dict[str, Any],
    keyword_docs: dict[str, int],
) -> str:
    instant = "all clear" if evals.get("instant_fail_clear") else "FAILED"
    ground = evals.get("groundedness") or {}
    window = phase1.get("time_window") or {}
    store_window = ingest.get("time_window") or {}
    by_docs = corpus.get("by_source_docs") or {}
    by_claims = corpus.get("by_source_claims") or {}
    lines = [
        "# Discovery report — Reddit primary + store corroboration (Phase 4)",
        "",
        "North-star: **% of Myntra users who purchase at least one wishlisted item "
        "within 30 days of adding it.** Hard constraint: no monetary incentive as the opportunity.",
        "",
        f"Instant-fail self-check: **{instant}**. "
        f"Groundedness sample: {ground.get('checked', 0)} claims, "
        f"verbatim {ground.get('verbatim_pct', 0):.0%}, "
        f"url {ground.get('url_pct', 0):.0%}.",
        "",
        "## Version and source mix",
        "",
        "| Field | Value |",
        "|---|---|",
        "| Product | Myntra |",
        "| Draft | Phase 4 — Reddit primary, Play/App Store corroboration |",
        f"| Reddit pull | {phase1.get('pulled_at') or 'unknown'} via `{phase1.get('adapter') or 'unknown'}` |",
        f"| Reddit window | {window.get('start')} → {window.get('end')} |",
        f"| Store pull | {ingest.get('pulled_at') or 'unknown'} |",
        f"| Store window | {store_window.get('start')} → {store_window.get('end')} |",
        f"| Play Store | `{ingest.get('play_app_id')}` · {by_docs.get('play_store', 0)} reviews |",
        f"| App Store | `{ingest.get('app_store_id')}` · {by_docs.get('app_store', 0)} reviews |",
        f"| Reddit docs (Phase 1) | {by_docs.get('reddit', 0)} |",
        f"| Phase 2 claims | {by_claims.get('reddit', 0)} (Groq + heuristic) |",
        f"| Store claims | {by_claims.get('play_store', 0)} Play + {by_claims.get('app_store', 0)} App Store |",
        f"| Combined claims | {corpus.get('claims_total')} · Reddit share of claims "
        f"{100 * float(corpus.get('reddit_claim_share') or 0):.0f}% |",
        "",
        "AJIO / Nykaa appear only as comparison. Store reviews are used to **corroborate or challenge** "
        "Reddit themes (returns, size/fit, quality, trust, app friction), not to replace Reddit.",
        "",
        "### Store keyword hits (document counts)",
        "",
        "| Keyword | Docs |",
        "|---|---:|",
    ]
    for key, value in keyword_docs.items():
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## How store reviews were used",
        "",
        "| Area | Reddit claims | Play | App Store | Verdict |",
        "|---|---:|---:|---:|---|",
    ]
    labels = {
        "corroborates": "corroborates Reddit",
        "thin_store": "store present, thin",
        "reddit_only": "Reddit only so far",
        "store_only": "store-only (not ranked as a Reddit replacement)",
        "thin": "too thin",
    }
    for row in corroboration:
        lines.append(
            f"| {row['title']} | {row['reddit_claims']} | {row['play_claims']} | "
            f"{row['app_claims']} | {labels.get(row['verdict'], row['verdict'])} |"
        )
    lines += [
        "",
        "Store-only app-crash volume is **not** allowed to outrank a Reddit-backed wishlist-window area.",
        "",
        "## Ten discovery questions",
        "",
        f"Coverage: **{coverage['answered_or_partial']}/10** Answered or Partial "
        f"({coverage['answered']} Answered, {coverage['partial']} Partial, {coverage['gap']} Gap).",
        "",
    ]
    for row in answers:
        lines.append(f"### Q{row['id']}. {row['question']}")
        lines.append("")
        lines.append(
            f"**{row['coverage']}** · {row['claim_count']} claims "
            f"({row.get('reddit_claims', 0)} Reddit / {row.get('store_claims', 0)} store) · "
            f"{row['thread_count']} threads"
        )
        lines.append("")
        lines.append(row["answer"])
        lines.append("")
        if row.get("evidence") and row["coverage"] != "Gap":
            for item in row["evidence"]:
                lines.append(_md_quote(item))
                lines.append("")
        elif row["id"] in {1, 8}:
            lines.append("_No explicit wishlist-add quote strong enough to close this Gap._")
            lines.append("")
    lines += [
        "## Ranked opportunity areas",
        "",
        "Behaviors / uncertainties, not features. Rank is the deliverable. "
        "Evidence strength is **Reddit-weighted**; store counts are corroboration.",
        "",
        "| Rank | Area | Score | Reddit | Store | Delay | Non-monetary |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in ranked:
        lines.append(
            f"| {row['rank']} | {row['title']} | {row['score']:.1f} | "
            f"{row.get('reddit_claim_count', 0)} | {row.get('store_claim_count', 0)} | "
            f"{100 * float(row.get('delay_share') or 0):.0f}% | "
            f"{'no (price evidence)' if row.get('monetary') else 'yes'} |"
        )
    lines += [
        "",
        "Rubric: `100 * (0.30 metric + 0.25 evidence + 0.20 delay + 0.15 constraint + 0.10 segment)` "
        "with a +3 corroboration bonus when Reddit ≥ 2 and store ≥ 3.",
        "",
    ]
    if len(ranked) < MIN_RANKED_AREAS:
        lines.append(f"_Warning: fewer than {MIN_RANKED_AREAS} ranked areas._")
        lines.append("")
    for row in ranked:
        reddit_quotes = _pick_quotes(clustered, row["id"], source="reddit", n=2)
        store_quotes = [
            item
            for item in clustered
            if item.get("opportunity_id") == row["id"]
            and (item.get("source") or "") in {"play_store", "app_store"}
        ]
        store_quotes = _pick_quotes(store_quotes, row["id"], source=None, n=2) if store_quotes else []
        lines.append(f"### {row['rank']}. {row['title']}")
        lines.append("")
        lines.append(f"**Behavior / uncertainty.** {row['behavior']}")
        lines.append("")
        lines.append(f"**Metric link.** {_metric_link(row)}")
        lines.append("")
        lines.append(
            f"**Quantification.** {row['claim_count']} claims "
            f"({row.get('reddit_claim_count', 0)} Reddit, "
            f"{row.get('play_claim_count', 0)} Play, "
            f"{row.get('app_claim_count', 0)} App Store) "
            f"in {row['doc_count']} docs / {row['thread_count']} threads. "
            f"Reddit share of this area {100 * float(row.get('reddit_share') or 0):.0f}%. "
            f"Delay/drop-off on {row.get('delay_yes', 0)}. Price mentioned on {row.get('price_mentioned', 0)}."
        )
        lines.append("")
        lines.append(f"**Comparison.** {row['comparison']}")
        lines.append("")
        lines.append("**Evidence (Reddit first).**")
        lines.append("")
        if reddit_quotes:
            for item in reddit_quotes:
                lines.append(_md_quote(item))
                lines.append("")
        else:
            lines.append("_No Reddit quote in this area._")
            lines.append("")
        if store_quotes:
            lines.append("**Store corroboration.**")
            lines.append("")
            for item in store_quotes:
                lines.append(_md_quote(item))
                lines.append("")
        claim_ids = ", ".join(f"`{cid}`" for cid in (row.get("claim_ids") or [])[:10])
        extra = "" if len(row.get("claim_ids") or []) <= 10 else ", …"
        lines.append(f"Ledger claim ids: {claim_ids}{extra}")
        lines.append("")
    non_mon = [row for row in ranked if not row.get("monetary")]
    monetary = [row for row in ranked if row.get("monetary")]
    lines += [
        "## What is not solvable with a discount",
        "",
        "Price/sale-waiting is captured when present. A coupon is not ranked.",
        "",
    ]
    if non_mon:
        lines.append("Non-monetary top areas: " + "; ".join(f"{row['rank']}. {row['title']}" for row in non_mon[:6]) + ".")
        lines.append("")
    if monetary:
        lines.append(
            "Monetary evidence area ("
            + "; ".join(row["title"] for row in monetary)
            + "): description of delay, not an intervention."
        )
        lines.append("")
    gaps = [row for row in answers if row["coverage"] == "Gap"]
    lines += ["## Gaps", "", "### Named question Gaps", ""]
    if gaps:
        for row in gaps:
            lines.append(f"- **Q{row['id']} {row['question']}** — {row['answer']}")
        lines.append("")
    else:
        lines.append("None.")
        lines.append("")
    lines += [
        "### Source-mix remaining Gaps",
        "",
        "- Fashion/shopping communities, Instagram, YouTube, and product Q&A are still not ingested (Phase 5 only if needed).",
        "- Private WhatsApp / DMs stay out of scope.",
        "- Store reviews are short and app-centric; they under-count styling, occasion, and off-platform research (Q6/Q7/Q9).",
        "",
        "## What this draft is not",
        "",
        "Not an MVP, interview plan, or metric tree. Myntra remains the product under study.",
        "",
        "## How to re-run",
        "",
        "```text",
        "cd Phases/Phase4_StoreReviews",
        "python run.py --dry-run",
        "python run.py",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"
