"""Deterministic Pulse report for senior management (+ optional short Groq blurb)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config

try:
    from chat import ChatError, _post_groq
except Exception:  # pragma: no cover - chat import side effects only if used
    ChatError = RuntimeError  # type: ignore

    def _post_groq(*_a: Any, **_k: Any) -> str:  # type: ignore
        raise ChatError("chat unavailable")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _claim_lookup() -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    if config.FREEZE_LEDGER.is_file():
        for entry in (_read_json(config.FREEZE_LEDGER).get("entries") or []):
            cid = entry.get("claim_id")
            if cid:
                by_id[str(cid)] = entry
    if config.PHASE5_CLAIMS.is_file():
        with config.PHASE5_CLAIMS.open(encoding="utf-8-sig") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                cid = row.get("claim_id")
                if cid and str(cid) not in by_id:
                    by_id[str(cid)] = row
    return by_id


def _quote_for_area(area: dict[str, Any], claims: dict[str, dict[str, Any]]) -> tuple[str, str, str]:
    """Return (quote, url, claim_id) for first available claim on the area."""
    for cid in area.get("claim_ids") or []:
        row = claims.get(str(cid))
        if not row:
            continue
        quote = str(row.get("quote") or "").strip()
        url = str(row.get("url") or "").strip()
        if quote:
            return quote, url, str(cid)
    return "", "", ""


def _exec_blurb(ranked_ids: list[str], coverage: dict[str, Any]) -> str:
    """Optional short LLM blurb that must name ranked area ids; falls back to template."""
    fallback = (
        f"Public discovery freeze covers {coverage.get('answered_or_partial', 10)}/10 "
        f"questions (Answered/Partial). Top ranked blocker areas: "
        + ", ".join(ranked_ids[:5])
        + ". This brief reports public-signal friction between wishlist add and purchase — "
        "not internal conversion rates."
    )
    prompt = (
        "Write 2–3 sentences for a Myntra leadership pulse. "
        "Name these ranked area ids exactly: "
        + ", ".join(ranked_ids[:6])
        + ". "
        "Do not invent conversion percentages or internal volumes. "
        "Do not propose MVPs, coupons, or wishlist-cap changes. "
        f"Coverage: {coverage.get('answered')} Answered, {coverage.get('partial')} Partial, "
        f"{coverage.get('gap')} Gap."
    )
    try:
        text = _post_groq(
            [
                {
                    "role": "system",
                    "content": (
                        "You write terse exec blurbs. Stay factual. "
                        "Never invent KPIs. Never pitch solutions."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        # Ensure area ids appear; else use fallback
        if sum(1 for aid in ranked_ids[:3] if aid in text) >= 2:
            return text.strip()
    except Exception:
        pass
    return fallback


def build_pulse_markdown(*, use_llm_blurb: bool = True) -> str:
    ranking = _read_json(config.RANKING_PATH)
    questions = _read_json(config.QUESTIONS_PATH)
    wishlist = _read_json(config.WISHLIST_EVIDENCE_PATH)
    quant = _read_json(config.QUANTIFICATION_PATH)
    freeze = _read_json(config.FREEZE_META) if config.FREEZE_META.is_file() else {}
    claims = _claim_lookup()

    ranking_sorted = sorted(ranking, key=lambda a: int(a.get("rank") or 999))
    ranked_ids = [str(a.get("id")) for a in ranking_sorted]
    coverage = questions.get("coverage") or {}
    corpus = quant.get("corpus") or {}
    by_docs = corpus.get("by_source_docs") or {}
    by_claims = corpus.get("by_source_claims") or {}
    facets = wishlist.get("facets") or {}

    frozen_at = freeze.get("frozen_at") or "unknown"
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    blurb = (
        _exec_blurb(ranked_ids, coverage)
        if use_llm_blurb
        else (
            f"Public discovery freeze covers {coverage.get('answered_or_partial')}/10 "
            f"questions. Top areas: {', '.join(ranked_ids[:5])}."
        )
    )

    lines: list[str] = []
    lines.append("# Wishlist Insights — Management Pulse")
    lines.append("")
    lines.append(f"_Generated: {generated} · Part 1 freeze: {frozen_at}_")
    lines.append("")
    lines.append("## 1. Executive snapshot")
    lines.append("")
    lines.append(blurb)
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    lines.append(f"| Corpus docs (raw) | {corpus.get('raw_docs')} |")
    lines.append(f"| Claims total | {corpus.get('claims_total')} |")
    lines.append(
        f"| Source docs | Reddit {by_docs.get('reddit')} · "
        f"Play {by_docs.get('play_store')} · App Store {by_docs.get('app_store')} |"
    )
    lines.append(
        f"| Question coverage | {coverage.get('answered_or_partial')}/10 "
        f"({coverage.get('answered')} Answered, {coverage.get('partial')} Partial, "
        f"{coverage.get('gap')} Gap) |"
    )
    lines.append("| Sign-off | Phase 6 freeze (canonical Part 1) |")
    lines.append("")
    lines.append(
        "**Metric definition (no invented rates):** numerator = buyers from wishlist; "
        "denominator = users who add. This pulse reports *public-signal blockers* that "
        "sit between add and buy — not internal conversion %."
    )
    lines.append("")

    lines.append("## 2. Wishlist pulse")
    lines.append("")
    lines.append(
        f"{wishlist.get('claims')} wishlist-language claims across "
        f"{wishlist.get('threads')} threads / {wishlist.get('docs')} docs."
    )
    lines.append("")
    lines.append("| Facet | Claims |")
    lines.append("|---|---:|")
    for facet, n in facets.items():
        lines.append(f"| {facet} | {n} |")
    lines.append("")
    lines.append(f"**Reading.** {wishlist.get('reading')}")
    lines.append("")
    lines.append(f"**Not established.** {wishlist.get('not_established')}")
    lines.append("")

    # Q1 / Q8 status
    q_by_id = {int(a["id"]): a for a in (questions.get("answers") or []) if "id" in a}
    for qid in (1, 8):
        ans = q_by_id.get(qid)
        if not ans:
            continue
        lines.append(
            f"**Q{qid} ({ans.get('coverage')}).** {ans.get('question')} — "
            f"{ans.get('claim_count')} claims. {ans.get('answer')}"
        )
        lines.append("")

    lines.append("## 3. Conversion blockers (public signals)")
    lines.append("")
    lines.append(
        "Ranked areas from Phase 5. Each includes one grounded quote from the freeze ledger / claims."
    )
    lines.append("")
    for area in ranking_sorted[:8]:
        aid = area.get("id")
        title = area.get("title")
        rank = area.get("rank")
        quote, url, cid = _quote_for_area(area, claims)
        lines.append(
            f"### #{rank} `{aid}` — {title}"
        )
        lines.append("")
        lines.append(
            f"{area.get('behavior')} "
            f"(claims={area.get('claim_count')}: "
            f"reddit={area.get('reddit_claim_count')}, "
            f"play={area.get('play_claim_count')}, "
            f"app={area.get('app_claim_count')})."
        )
        lines.append("")
        if quote:
            lines.append(f"> {quote}")
            lines.append(">")
            lines.append(f"> — `{cid}` · {url}")
        else:
            lines.append("_No quote resolved for this area in the local claim index._")
        lines.append("")

    lines.append("## 4. What appears to help conversion")
    lines.append("")
    intent_samples = (wishlist.get("samples") or {}).get("intent") or []
    if intent_samples:
        lines.append(
            "Named intent / completed-purchase wishlist evidence is thin "
            f"({len(intent_samples)} sample(s) in the wishlist sweep):"
        )
        lines.append("")
        for item in intent_samples:
            lines.append(f"> {item.get('quote')}")
            lines.append(">")
            lines.append(f"> — `{item.get('claim_id')}` · {item.get('url')}")
            lines.append("")
    else:
        lines.append(
            "No strong public evidence in this corpus for what *helps* wishlist→buy conversion. "
            "Intent-facet samples are thin; do not infer product fixes from silence."
        )
        lines.append("")
    lines.append(
        "Sale-park behaviour shows price-drop waiting, which is a delay pattern — not proof that "
        "discounts are the non-monetary opportunity under study."
    )
    lines.append("")

    lines.append("## 5. Opinion by channel")
    lines.append("")
    lines.append("| Channel | Docs | Claims |")
    lines.append("|---|---:|---:|")
    lines.append(
        f"| Reddit | {by_docs.get('reddit', 0)} | {by_claims.get('reddit', 0)} |"
    )
    lines.append(
        f"| Play Store | {by_docs.get('play_store', 0)} | {by_claims.get('play_store', 0)} |"
    )
    lines.append(
        f"| App Store | {by_docs.get('app_store', 0)} | {by_claims.get('app_store', 0)} |"
    )
    lines.append("")
    lines.append(
        "Store reviews corroborate Reddit themes on quality, returns, fit, and reviews; "
        "wishlist-language evidence remains Reddit-primary and thin."
    )
    lines.append("")

    lines.append("## 6. What we cannot measure")
    lines.append("")
    lines.append("- Internal wishlist add volume, purchase-from-wishlist counts, or conversion %.")
    lines.append("- Causal effect of raising/removing a saved-item ceiling on sales.")
    lines.append("- Coupon / monetary incentive impact (out of scope for this discovery).")
    lines.append(
        f"- Q1 and Q8 remain **Partial** on a thin wishlist base "
        f"({wishlist.get('claims')} claims / {wishlist.get('threads')} threads)."
    )
    lines.append("")

    lines.append("## 7. How to refresh")
    lines.append("")
    lines.append("1. Rebuild the RAG index: `python build_index.py` (from `Apps/WishlistInsights/`).")
    lines.append("2. Regenerate this brief: `python pulse.py`.")
    lines.append(
        "3. Optional later: re-pull Phase 5 wishlist expansion if Gaps reopen — do not expand "
        "scope casually; Part 1 freeze stays canonical until a new sign-off."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "_Sources: Phase 6 `discovery-report.md` / `evidence-ledger.json`; "
        "Phase 5 `ranking.json`, `questions.json`, `wishlist_evidence.json`, `quantification.json`._"
    )
    lines.append("")
    return "\n".join(lines)


def write_pulse(*, use_llm_blurb: bool = True) -> Path:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    md = build_pulse_markdown(use_llm_blurb=use_llm_blurb)
    config.PULSE_REPORT_PATH.write_text(md, encoding="utf-8")
    return config.PULSE_REPORT_PATH


def main() -> None:
    path = write_pulse(use_llm_blurb=True)
    print(f"Wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
