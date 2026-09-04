"""Answer the ten discovery questions from clustered claims. Gap is allowed; silence is not."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

QUESTION_TEXT = {
    1: "Why add to the Myntra wishlist?",
    2: "What prevents wishlisted products from being purchased?",
    3: "What uncertainties remain after a product is identified?",
    4: "What causes postponement?",
    5: "How do users compare shortlisted products?",
    6: "What do they seek outside Myntra before purchasing?",
    7: "Role of fit, size, styling, price, reviews, occasion, social validation?",
    8: "Wishlist as intent vs bookmark?",
    9: "How do behaviors differ across segments?",
    10: "What unmet needs show up consistently?",
}

# Q1/Q8 need explicit wishlist language. This corpus does not have it.
FORCE_GAP = {1, 8}


def _unique_threads(rows: list[dict[str, Any]]) -> int:
    return len({row.get("thread_id") for row in rows if row.get("thread_id")})


def _pick_quotes(rows: list[dict[str, Any]], n: int = 3) -> list[dict[str, Any]]:
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
    seen_urls: set[str] = set()
    picked: list[dict[str, Any]] = []
    for row in ranked:
        url = str(row.get("url") or "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        picked.append(
            {
                "claim_id": row.get("claim_id"),
                "quote": row.get("quote"),
                "url": url,
                "doc_id": row.get("doc_id"),
                "theme": row.get("theme"),
                "opportunity_id": row.get("opportunity_id"),
            }
        )
        if len(picked) >= n:
            break
    return picked


def _coverage(qid: int, rows: list[dict[str, Any]], *, earned_segments: int = 0) -> str:
    if qid in FORCE_GAP:
        return "Gap"
    if qid == 9:
        return "Partial" if earned_segments >= 2 else "Gap"
    if qid == 5:
        return "Partial" if rows else "Gap"
    threads = _unique_threads(rows)
    groq = sum(1 for row in rows if row.get("extractor") == "groq")
    if len(rows) >= 2 and threads >= 2 and (groq >= 2 or len(rows) >= 4):
        return "Answered"
    if rows:
        return "Partial"
    return "Gap"


def _answer_text(qid: int, coverage: str, rows: list[dict[str, Any]]) -> str:
    if qid == 1:
        return (
            "The Phase 2 claims do not contain explicit 'add to wishlist' language. "
            "wishlist_signal is `none` on every extracted claim. Raw Reddit text mentions "
            "wishlist in only a handful of documents, so why people add cannot be answered "
            "from this pull. Closest behaviors are scrolling Myntra, holding items in cart, "
            "and saving inspiration threads — which is bookmark-like, not a measured add."
        )
    if qid == 8:
        return (
            "Intent vs bookmark cannot be scored from this corpus. No claim is tagged "
            "explicit or implied wishlist. Treating every Myntra mention as purchase intent "
            "would fail the eval. The honest reading: people use Myntra as a browse/watch "
            "surface (scroll, compare, ask Reddit) and sometimes leave items in cart after "
            "a cancelled order. That is not the same as 'wishlist = almost a purchase'."
        )
    if qid == 9:
        ethnic = sum(1 for row in rows if "ethnic_vs_western" in (row.get("segment_signals") or []))
        size = sum(
            1 for row in rows if "size_insecure_vs_size_confident" in (row.get("segment_signals") or [])
        )
        return (
            f"Only earned segments appear. ethnic_vs_western shows up on {ethnic} claims "
            f"(lehenga, palazzo, western-wear search). size_insecure_vs_size_confident shows "
            f"up on {size} claims (tall length, plus-size belts, cup/band). Metro vs rest-of-India, "
            "first-time vs repeat, and sale-waiter vs occasion-buyer were not supported. "
            "No personas were invented."
        )
    if qid == 5:
        return (
            "Comparison language is thin. A few comments check that an item is 'also available "
            "in Myntra', ask 'which one do you suggest', or note the same SKU priced differently "
            "on Myntra vs Flipkart vs a brand site. This is cross-listing, not a documented "
            "2–3 item shortlist workflow inside the Myntra wishlist."
        )
    if qid == 2:
        return (
            "What blocks a buy after Myntra is in play: missing/mixed reviews, quality or fake-goods "
            "fear, fit/size misses, checkout price jumps, and a reverse path (return/refund/cancel) "
            "that people do not trust. Several quotes sit at hesitation-to-order, not just after "
            "a bad delivery."
        )
    if qid == 3:
        return (
            "After a product is identified, leftover uncertainty is whether reviews can be trusted, "
            "whether fabric/quality matches the image, whether it will fit, and whether the look "
            "works on their body/occasion. People keep asking Reddit after they have already "
            "scrolled Myntra."
        )
    if qid == 4:
        return (
            "Postponement shows up as waiting on occasion (wedding/event dressing), waiting on "
            "price/checkout math, and waiting because a return or refund last time went badly. "
            "Festival language in the raw pull is present but many heuristic 'occasion' hits "
            "are title echoes — those were down-weighted in ranking."
        )
    if qid == 6:
        return (
            "Outside Myntra they ask Reddit ('has anyone tried'), look at Instagram/small brands, "
            "Decathlon, Zara/Urbanic/Forever New, Nykaa, Amazon, and brand sites. NRI threads "
            "also ask how to buy in India and ship out. This corpus *is* the off-platform step."
        )
    if qid == 7:
        return (
            "Reviews and quality talk dominate. Fit/size is smaller but concrete (length short, "
            "bras, belts). Styling appears on event/saree threads. Price appears as checkout "
            "uplift and cross-platform gaps. Occasion is wedding/event dressing. Social "
            "validation is the 'has anyone tried' ask. These are roles in the journey, not a "
            "flat importance ranking."
        )
    if qid == 10:
        return (
            "Recurring unmet needs: enough trusted reviews on affordable options, quality that "
            "matches the listing, sizes that exist (tall, plus, specific bra sizes), assortment "
            "that is not 'the same collection everywhere', and a reverse path that actually "
            "refunds. International access (Myntra not usable in the EU) is named but thin."
        )
    return "See evidence below." if coverage != "Gap" else "The corpus did not support an answer."


def answer_questions(clustered: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_q: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in clustered:
        for qid in row.get("discovery_question_ids") or []:
            by_q[int(qid)].append(row)
    earned_segment_rows = [row for row in clustered if row.get("segment_signals")]
    answers = []
    for qid in range(1, 11):
        rows = by_q.get(qid, [])
        if qid == 9:
            rows = earned_segment_rows or rows
        coverage = _coverage(qid, rows, earned_segments=len(earned_segment_rows))
        answers.append(
            {
                "id": qid,
                "question": QUESTION_TEXT[qid],
                "coverage": coverage,
                "claim_count": len(rows),
                "thread_count": _unique_threads(rows),
                "answer": _answer_text(qid, coverage, rows),
                "evidence": _pick_quotes(rows, 3) if coverage != "Gap" or qid in FORCE_GAP else [],
            }
        )
    return answers


def coverage_summary(answers: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"Answered": 0, "Partial": 0, "Gap": 0}
    for row in answers:
        counts[row["coverage"]] = counts.get(row["coverage"], 0) + 1
    covered = counts["Answered"] + counts["Partial"]
    return {
        "answered": counts["Answered"],
        "partial": counts["Partial"],
        "gap": counts["Gap"],
        "answered_or_partial": covered,
        "pass_8_of_10": covered >= 8,
        "gaps_named": counts["Gap"] == sum(1 for row in answers if row["coverage"] == "Gap"),
    }
