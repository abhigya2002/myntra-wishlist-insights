"""Phase 5 discovery report: Reddit primary, stores corroborate, wishlist sweep closes Q1/Q8."""

from __future__ import annotations

from typing import Any

from config import MIN_RANKED_AREAS, TRIGGER_GAPS

STORE_SOURCES = frozenset({"play_store", "app_store"})

FACET_LABEL = {
    "why_add": "generic 'it is on my wishlist'",
    "archive": "saved without buying (archive / inspiration / show-and-tell)",
    "intent": "stated or completed intent to buy",
    "sale_park": "parked to wait for a sale",
    "ceiling": "list has grown past being usable",
    "fit_block": "fit or size blocks the save",
    "compare_block": "asking others to help choose",
}


def _md_quote(item: dict[str, Any]) -> str:
    quote = str(item.get("quote") or "").replace("\n", " ").strip()
    url = item.get("url") or ""
    claim_id = item.get("claim_id") or ""
    source = item.get("source") or ""
    facet = item.get("wishlist_facet")
    tags = []
    if source and source != "reddit":
        tags.append(source)
    if facet:
        tags.append(facet)
    tag = f" [{' · '.join(tags)}]" if tags else ""
    return f"> {quote}{tag}\n>\n> — `{claim_id}` · {url}"


def _pick_quotes(rows: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    ranked = sorted(
        rows,
        key=lambda row: (
            0 if row.get("wishlist_facet") else 1,
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


def _area_rows(clustered: list[dict[str, Any]], area_id: str, *, source: str | None = None) -> list[dict[str, Any]]:
    rows = [row for row in clustered if row.get("opportunity_id") == area_id]
    if source == "reddit":
        rows = [row for row in rows if (row.get("source") or "reddit") == "reddit"]
    elif source == "store":
        rows = [row for row in rows if (row.get("source") or "") in STORE_SOURCES]
    return rows


def _metric_link(area: dict[str, Any]) -> str:
    stage = str(area.get("journey_stage") or "").replace("_", " ")
    delay_pct = 100 * float(area.get("delay_share") or 0)
    if area["id"] == "wishlist_intent_ambiguity":
        return (
            "This sits directly on the north-star. The metric counts adds in its denominator "
            "and purchases in its numerator, so any add made for inspiration, sale-watching, "
            "or sharing depresses the ratio without anything having gone wrong. "
            f"Delay/drop-off on {delay_pct:.0f}% of claims."
        )
    if area["id"] == "wishlist_ceiling":
        return (
            "Evidence that saved lists are archives rather than shortlists: people lose track "
            "of what they saved and purge in bulk. **Direction is unproven.** A shopper who "
            "saves past the point of usefulness is evidence that adding is already decoupled "
            "from buying, so a larger list is not established to raise purchases and could "
            "enlarge the denominator instead."
        )
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
            "not residual fashion uncertainty. Ranked only if Reddit also speaks to it."
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
    store_ingest: dict[str, Any],
    expansion: dict[str, Any],
    corpus: dict[str, Any],
    ranked: list[dict[str, Any]],
    answers: list[dict[str, Any]],
    coverage: dict[str, Any],
    clustered: list[dict[str, Any]],
    corroboration: list[dict[str, Any]],
    wishlist: dict[str, Any],
    evals: dict[str, Any],
) -> str:
    instant = "all clear" if evals.get("instant_fail_clear") else "FAILED"
    ground = evals.get("groundedness") or {}
    window = phase1.get("time_window") or {}
    by_docs = corpus.get("by_source_docs") or {}
    by_claims = corpus.get("by_source_claims") or {}
    facets = wishlist.get("facets") or {}

    lines = [
        "# Discovery report — Reddit primary + store corroboration + wishlist expansion (Phase 5)",
        "",
        "North-star: **% of Myntra users who purchase at least one wishlisted item "
        "within 30 days of adding it.** Hard constraint: no monetary incentive as the opportunity.",
        "",
        f"Instant-fail self-check: **{instant}**. "
        f"Groundedness sample: {ground.get('checked', 0)} claims, "
        f"verbatim {ground.get('verbatim_pct', 0):.0%}, "
        f"url {ground.get('url_pct', 0):.0%}.",
        "",
        "## Why this expansion ran",
        "",
        "Phase 5 is conditional. It ran for two named Gaps that survived Phases 3 and 4: "
        + ", ".join(f"**{gap}**" for gap in TRIGGER_GAPS)
        + ".",
        "",
        "Phases 1–4 produced a corpus in which one Reddit document and zero store reviews "
        "contained the word *wishlist*, so the question the north-star is built on could not "
        "be answered. The expansion targets wishlist language specifically and stops there; "
        "extra sources are not a goal.",
        "",
        "## Version and source mix",
        "",
        "| Field | Value |",
        "|---|---|",
        "| Product | Myntra |",
        "| Draft | Phase 5 — Reddit primary, store corroboration, wishlist expansion |",
        f"| Reddit pull (Phase 1) | {phase1.get('pulled_at') or 'unknown'} |",
        f"| Reddit window | {window.get('start')} → {window.get('end')} |",
        f"| Store pull (Phase 4) | {store_ingest.get('pulled_at') or 'unknown'} |",
        f"| Expansion pull (Phase 5) | {expansion.get('pulled_at') or 'unknown'} |",
        f"| Reddit docs | {by_docs.get('reddit', 0)} |",
        f"| Play Store reviews | {by_docs.get('play_store', 0)} |",
        f"| App Store reviews | {by_docs.get('app_store', 0)} |",
        f"| YouTube comments | {by_docs.get('youtube', 0)} |",
        f"| Claims total | {corpus.get('claims_total')} "
        f"({by_claims.get('reddit', 0)} Reddit, {corpus.get('store_claim_count', 0)} store) |",
        f"| Wishlist-language claims (new in Phase 5) | {corpus.get('phase5_claim_count', 0)} |",
        f"| Reddit share of claims | {100 * float(corpus.get('reddit_claim_share') or 0):.0f}% |",
        "",
        "AJIO / Nykaa appear only as comparison. Play Store and App Store reviews **corroborate or "
        "challenge** Reddit themes; they do not replace Reddit.",
        "",
        "## Wishlist evidence (Q1 / Q8)",
        "",
        f"{wishlist.get('claims', 0)} wishlist-language claims across "
        f"{wishlist.get('threads', 0)} independent threads and {wishlist.get('docs', 0)} documents.",
        "",
        "| What the save is for | Claims |",
        "|---|---:|",
    ]
    for facet, count in sorted(facets.items(), key=lambda item: -item[1]):
        lines.append(f"| {FACET_LABEL.get(facet, facet)} | {count} |")

    bookmark_share = wishlist.get("bookmark_share_of_decided")
    lines += ["", f"**Reading.** {wishlist.get('reading')}"]
    if bookmark_share is not None:
        lines.append("")
        lines.append(
            f"Of the claims that state a reason either way, {100 * float(bookmark_share):.0f}% describe "
            "saving without buying and "
            f"{100 * float(wishlist.get('intent_share_of_decided') or 0):.0f}% describe a save that "
            "converted or was meant to. An add is therefore a weak default signal of intent."
        )
    lines += [
        "",
        "**On the saved-item ceiling.** "
        + str(wishlist.get("not_established")),
        "",
        "Raising or removing a ceiling would be a *solution*, and solutions are out of scope for "
        "this part of the work. What the evidence supports is the behaviour: saved lists become "
        "archives that their owners stop navigating.",
        "",
    ]
    for facet in ("archive", "intent", "ceiling"):
        samples = (wishlist.get("samples") or {}).get(facet) or []
        if not samples:
            continue
        lines.append(f"**{FACET_LABEL.get(facet, facet).capitalize()}**")
        lines.append("")
        for item in samples:
            lines.append(_md_quote({**item, "wishlist_facet": facet}))
            lines.append("")

    lines += [
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
            f"({row.get('reddit_claims', 0)} Reddit / {row.get('store_claims', 0)} store / "
            f"{row.get('phase5_claims', 0)} wishlist-sweep) · {row['thread_count']} threads"
        )
        lines.append("")
        lines.append(row["answer"])
        lines.append("")
        if row.get("evidence"):
            for item in row["evidence"]:
                lines.append(_md_quote(item))
                lines.append("")
        elif row["coverage"] == "Gap":
            lines.append("_No quote in this corpus closes this question._")
            lines.append("")

    lines += [
        "## Ranked opportunity areas",
        "",
        "Behaviors / uncertainties, not features. Rank is the deliverable. "
        "Evidence strength is **Reddit-weighted**; store counts are corroboration.",
        "",
        "| Rank | Area | Score | Reddit | Store | Wishlist | Delay | Non-monetary |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in ranked:
        lines.append(
            f"| {row['rank']} | {row['title']} | {row['score']:.1f} | "
            f"{row.get('reddit_claim_count', 0)} | {row.get('store_claim_count', 0)} | "
            f"{row.get('phase5_claim_count', 0)} | "
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
        reddit_quotes = _pick_quotes(_area_rows(clustered, row["id"], source="reddit"), 2)
        store_quotes = _pick_quotes(_area_rows(clustered, row["id"], source="store"), 2)
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
        lines.append(
            "Non-monetary top areas: "
            + "; ".join(f"{row['rank']}. {row['title']}" for row in non_mon[:6])
            + "."
        )
        lines.append("")
    if monetary:
        lines.append(
            "Monetary evidence area ("
            + "; ".join(row["title"] for row in monetary)
            + "): description of delay, not an intervention."
        )
        lines.append("")

    gaps = [row for row in answers if row["coverage"] == "Gap"]
    skipped = expansion.get("skipped") or {}
    lines += ["## Gaps", "", "### Named question Gaps", ""]
    if gaps:
        for row in gaps:
            lines.append(f"- **Q{row['id']} {row['question']}** — {row['answer']}")
        lines.append("")
    else:
        lines.append("None. Every question reached Answered or Partial.")
        lines.append("")
    lines += ["### Sources named in the spec but not ingested", ""]
    if skipped:
        for name, reason in skipped.items():
            lines.append(f"- **{name}** — {reason}")
    else:
        lines.append("- None.")
    lines += [
        "",
        "### Standing limitations",
        "",
        f"- Q1 and Q8 rest on {wishlist.get('claims', 0)} wishlist claims across "
        f"{wishlist.get('threads', 0)} threads, which is why both are Partial rather than "
        "Answered. The sweep was stopped before every subreddit tier was covered, so this is "
        "a floor on the available wishlist evidence, not a ceiling.",
        "- No claim in this corpus mentions a saved-item cap or ceiling. The absence is "
        "reported as an absence: it is weak evidence that hitting a limit is not a widely "
        "voiced complaint, and it is not evidence about what lifting one would do.",
        "- Segments stay earned-only. No personas were invented.",
        "- Wishlist claims come from public discussion, not from Myntra's own wishlist data, "
        "so no add-to-purchase rate can be computed here. That is a Part 2 measurement task.",
        "- Store reviews are short and app-centric; they under-count styling, occasion, and "
        "off-platform research (Q6/Q7/Q9).",
        "- Private WhatsApp / DMs stay out of scope.",
        "",
        "## What this draft is not",
        "",
        "Not an MVP, interview plan, or metric tree. Myntra remains the product under study. "
        "No opportunity here is stated as a feature to build.",
        "",
        "## How to re-run",
        "",
        "```text",
        "cd Phases/Phase5_OptionalExpansion",
        "python run.py --dry-run",
        "python run.py --no-ingest",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"
