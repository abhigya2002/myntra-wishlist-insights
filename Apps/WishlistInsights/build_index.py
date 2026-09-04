"""Build local BM25 corpus index (JSONL) from Phase 6 freeze + Phase 5 + raw docs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterator

import config

SECTION_RE = re.compile(r"(?m)^(#{1,3})\s+(.+)$")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    if not path.is_file():
        return
    with path.open(encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _chunk(
    *,
    chunk_id: str,
    text: str,
    source: str,
    url: str = "",
    layer: str,
    opportunity_id: str | None = None,
    theme: str | None = None,
    wishlist_facet: str | None = None,
    claim_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    cleaned = " ".join((text or "").split()).strip()
    if len(cleaned) < 20:
        return None
    row: dict[str, Any] = {
        "id": chunk_id,
        "text": cleaned,
        "source": source,
        "url": url or "",
        "layer": layer,
    }
    if opportunity_id:
        row["opportunity_id"] = opportunity_id
    if theme:
        row["theme"] = theme
    if wishlist_facet:
        row["wishlist_facet"] = wishlist_facet
    if claim_id:
        row["claim_id"] = claim_id
    if extra:
        row.update(extra)
    return row


def chunks_from_claims() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _iter_jsonl(config.PHASE5_CLAIMS):
        claim_id = str(row.get("claim_id") or "")
        quote = str(row.get("quote") or "")
        theme = row.get("theme")
        facet = row.get("wishlist_facet") or (
            row.get("wishlist_signal") if row.get("wishlist_signal") not in (None, "none") else None
        )
        text = f"Claim {claim_id}: {quote}"
        meta_bits = []
        if theme:
            meta_bits.append(f"theme={theme}")
        if facet:
            meta_bits.append(f"wishlist_facet={facet}")
        opp = row.get("opportunity_id")
        if opp:
            meta_bits.append(f"opportunity={opp}")
        if meta_bits:
            text = f"{text} [{' · '.join(meta_bits)}]"
        chunk = _chunk(
            chunk_id=f"claim::{claim_id}",
            text=text,
            source=str(row.get("source") or "claim"),
            url=str(row.get("url") or ""),
            layer="claim",
            opportunity_id=str(opp) if opp else None,
            theme=str(theme) if theme else None,
            wishlist_facet=str(facet) if facet else None,
            claim_id=claim_id,
        )
        if chunk:
            out.append(chunk)
    return out


def chunks_from_ledger() -> list[dict[str, Any]]:
    """Supplement claims with ledger entries that may carry opportunity_id."""
    if not config.FREEZE_LEDGER.is_file():
        return []
    ledger = _read_json(config.FREEZE_LEDGER)
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for entry in ledger.get("entries") or []:
        claim_id = str(entry.get("claim_id") or "")
        if not claim_id or claim_id in seen:
            continue
        seen.add(claim_id)
        # Prefer Phase 5 claims for quote text; ledger adds opportunity/facet if useful
        quote = str(entry.get("quote") or "")
        opp = entry.get("opportunity_id")
        theme = entry.get("theme")
        facet = entry.get("wishlist_facet")
        text = f"Ledger {claim_id}: {quote}"
        if opp:
            text += f" [opportunity={opp}]"
        chunk = _chunk(
            chunk_id=f"ledger::{claim_id}",
            text=text,
            source=str(entry.get("source") or "ledger"),
            url=str(entry.get("url") or ""),
            layer="claim",
            opportunity_id=str(opp) if opp else None,
            theme=str(theme) if theme else None,
            wishlist_facet=str(facet) if facet else None,
            claim_id=claim_id,
        )
        if chunk:
            out.append(chunk)
    return out


def chunks_from_report() -> list[dict[str, Any]]:
    if not config.FREEZE_REPORT.is_file():
        return []
    md = config.FREEZE_REPORT.read_text(encoding="utf-8-sig")
    matches = list(SECTION_RE.finditer(md))
    out: list[dict[str, Any]] = []
    if not matches:
        chunk = _chunk(
            chunk_id="report::full",
            text=md[: config.REPORT_SECTION_MAX],
            source="discovery-report",
            url="",
            layer="report",
        )
        return [chunk] if chunk else []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        title = match.group(2).strip()
        body = md[start:end].strip()
        if len(body) > config.REPORT_SECTION_MAX:
            body = body[: config.REPORT_SECTION_MAX] + "…"
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or f"sec{i}"
        chunk = _chunk(
            chunk_id=f"report::{i:03d}::{slug}",
            text=body,
            source="discovery-report",
            url="",
            layer="report",
            extra={"section": title},
        )
        if chunk:
            out.append(chunk)
    return out


def chunks_from_derived() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    if config.RANKING_PATH.is_file():
        ranking = _read_json(config.RANKING_PATH)
        for area in ranking:
            aid = area.get("id")
            title = area.get("title")
            behavior = area.get("behavior")
            rank = area.get("rank")
            text = (
                f"Ranked area #{rank} id={aid}: {title}. "
                f"Behavior: {behavior}. "
                f"Claims={area.get('claim_count')} "
                f"(reddit={area.get('reddit_claim_count')}, "
                f"play={area.get('play_claim_count')}, "
                f"app_store={area.get('app_claim_count')})."
            )
            chunk = _chunk(
                chunk_id=f"derived::rank::{aid}",
                text=text,
                source="ranking.json",
                layer="derived",
                opportunity_id=str(aid) if aid else None,
            )
            if chunk:
                out.append(chunk)

    if config.QUESTIONS_PATH.is_file():
        questions = _read_json(config.QUESTIONS_PATH)
        coverage = questions.get("coverage") or {}
        cov_text = (
            f"Question coverage: answered={coverage.get('answered')}, "
            f"partial={coverage.get('partial')}, gap={coverage.get('gap')}, "
            f"answered_or_partial={coverage.get('answered_or_partial')}, "
            f"pass_8_of_10={coverage.get('pass_8_of_10')}."
        )
        chunk = _chunk(
            chunk_id="derived::questions::coverage",
            text=cov_text,
            source="questions.json",
            layer="derived",
        )
        if chunk:
            out.append(chunk)
        for ans in questions.get("answers") or []:
            qid = ans.get("id")
            text = (
                f"Q{qid}: {ans.get('question')} "
                f"Coverage={ans.get('coverage')}. "
                f"Answer: {ans.get('answer')}"
            )
            chunk = _chunk(
                chunk_id=f"derived::q::{qid}",
                text=text,
                source="questions.json",
                layer="derived",
            )
            if chunk:
                out.append(chunk)
            for i, ev in enumerate((ans.get("evidence") or [])[:3]):
                quote = ev.get("quote") or ""
                cid = ev.get("claim_id") or f"q{qid}_ev{i}"
                chunk = _chunk(
                    chunk_id=f"derived::q::{qid}::ev::{cid}",
                    text=f"Q{qid} evidence ({cid}): {quote}",
                    source=str(ev.get("source") or "questions.json"),
                    url=str(ev.get("url") or ""),
                    layer="derived",
                    claim_id=str(ev.get("claim_id") or "") or None,
                    theme=str(ev.get("theme")) if ev.get("theme") else None,
                    wishlist_facet=str(ev.get("wishlist_facet")) if ev.get("wishlist_facet") else None,
                    opportunity_id=str(ev.get("opportunity_id")) if ev.get("opportunity_id") else None,
                )
                if chunk:
                    out.append(chunk)

    if config.WISHLIST_EVIDENCE_PATH.is_file():
        wl = _read_json(config.WISHLIST_EVIDENCE_PATH)
        facets = wl.get("facets") or {}
        facet_str = ", ".join(f"{k}={v}" for k, v in facets.items())
        text = (
            f"Wishlist evidence: claims={wl.get('claims')}, threads={wl.get('threads')}, "
            f"docs={wl.get('docs')}. Facets: {facet_str}. "
            f"Reading: {wl.get('reading')} "
            f"Not established: {wl.get('not_established')}"
        )
        chunk = _chunk(
            chunk_id="derived::wishlist::summary",
            text=text,
            source="wishlist_evidence.json",
            layer="derived",
            theme="wishlist",
        )
        if chunk:
            out.append(chunk)
        samples = wl.get("samples") or {}
        for facet, items in samples.items():
            for i, item in enumerate(items):
                cid = item.get("claim_id") or f"{facet}_{i}"
                chunk = _chunk(
                    chunk_id=f"derived::wishlist::{facet}::{cid}",
                    text=f"Wishlist facet {facet}: {item.get('quote')}",
                    source="wishlist_evidence.json",
                    url=str(item.get("url") or ""),
                    layer="derived",
                    claim_id=str(item.get("claim_id") or "") or None,
                    wishlist_facet=facet,
                )
                if chunk:
                    out.append(chunk)

    if config.QUANTIFICATION_PATH.is_file():
        quant = _read_json(config.QUANTIFICATION_PATH)
        corpus = quant.get("corpus") or {}
        by_src = corpus.get("by_source_docs") or {}
        by_claims = corpus.get("by_source_claims") or {}
        text = (
            f"Corpus quantification: raw_docs={corpus.get('raw_docs')}, "
            f"claims_total={corpus.get('claims_total')}, "
            f"docs by source reddit={by_src.get('reddit')} play={by_src.get('play_store')} "
            f"app_store={by_src.get('app_store')}; "
            f"claims by source reddit={by_claims.get('reddit')} "
            f"play={by_claims.get('play_store')} app_store={by_claims.get('app_store')}."
        )
        chunk = _chunk(
            chunk_id="derived::quant::corpus",
            text=text,
            source="quantification.json",
            layer="derived",
        )
        if chunk:
            out.append(chunk)

    return out


def chunks_from_raw() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    sources = (
        (config.PHASE1_RAW, "phase1_reddit"),
        (config.PHASE4_RAW, "phase4_store"),
        (config.PHASE5_RAW, "phase5_expansion"),
    )
    for path, label in sources:
        for row in _iter_jsonl(path):
            doc_id = str(row.get("id") or "")
            title = str(row.get("title") or "")
            body = str(row.get("body") or "")
            text = f"{title}\n{body}".strip()
            if len(text) > config.RAW_BODY_MAX:
                text = text[: config.RAW_BODY_MAX] + "…"
            chunk = _chunk(
                chunk_id=f"raw::{label}::{doc_id}",
                text=text,
                source=str(row.get("source") or label),
                url=str(row.get("url") or ""),
                layer="raw",
                extra={"doc_id": doc_id},
            )
            if chunk:
                out.append(chunk)
    return out


def build_chunks() -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    chunks.extend(chunks_from_claims())
    # Ledger duplicates claim quotes; keep only ledger rows whose claim_id is absent from claims
    claim_ids = {c.get("claim_id") for c in chunks if c.get("claim_id")}
    for ledger_chunk in chunks_from_ledger():
        if ledger_chunk.get("claim_id") in claim_ids:
            # Enrich existing claim chunk with opportunity_id if missing
            continue
        chunks.append(ledger_chunk)
    # Enrich claim chunks from ledger opportunity_id
    ledger_by_id: dict[str, dict[str, Any]] = {}
    if config.FREEZE_LEDGER.is_file():
        for entry in (_read_json(config.FREEZE_LEDGER).get("entries") or []):
            cid = entry.get("claim_id")
            if cid:
                ledger_by_id[str(cid)] = entry
    for chunk in chunks:
        if chunk.get("layer") != "claim":
            continue
        cid = chunk.get("claim_id")
        entry = ledger_by_id.get(str(cid or ""))
        if not entry:
            continue
        if not chunk.get("opportunity_id") and entry.get("opportunity_id"):
            chunk["opportunity_id"] = entry["opportunity_id"]
            chunk["text"] = chunk["text"] + f" [opportunity={entry['opportunity_id']}]"
        if not chunk.get("wishlist_facet") and entry.get("wishlist_facet"):
            chunk["wishlist_facet"] = entry["wishlist_facet"]

    chunks.extend(chunks_from_report())
    chunks.extend(chunks_from_derived())
    chunks.extend(chunks_from_raw())

    # Deduplicate by id
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for c in chunks:
        cid = c["id"]
        if cid in seen:
            continue
        seen.add(cid)
        unique.append(c)
    return unique


def write_index(chunks: list[dict[str, Any]]) -> Path:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with config.INDEX_PATH.open("w", encoding="utf-8") as fh:
        for row in chunks:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return config.INDEX_PATH


def main() -> None:
    chunks = build_chunks()
    path = write_index(chunks)
    by_layer: dict[str, int] = {}
    for c in chunks:
        by_layer[c["layer"]] = by_layer.get(c["layer"], 0) + 1
    print(f"Wrote {len(chunks)} chunks -> {path}")
    for layer, n in sorted(by_layer.items()):
        print(f"  {layer}: {n}")


if __name__ == "__main__":
    main()
