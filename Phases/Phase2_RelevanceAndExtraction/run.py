"""Phase 2 CLI: relevance gate + quote-backed claims on the Reddit corpus."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PHASE2_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PHASE2_DIR.parent / "Phase1_RedditIngest"))
sys.path.insert(0, str(PHASE2_DIR))

from analyze import analysis_prompt, heuristic_gate, merge_llm_result  # noqa: E402
from config import (  # noqa: E402
    CACHE_PATH,
    CLAIMS_PATH,
    EVAL_NOTES_PATH,
    LABELED_PATH,
    LEGACY_CACHE_PATH,
    MANIFEST_PATH,
    PHASE1_RAW,
    SAMPLE_PATH,
    groq_model,
    key_status,
)
from groq_client import GroqClient, GroqError, GroqQuotaError  # noqa: E402
from sample import pick_gate_sample, sample_rows_for_docs, write_eval_notes  # noqa: E402


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_cache(*paths: Path) -> dict[str, dict[str, Any]]:
    cache: dict[str, dict[str, Any]] = {}
    for path in paths:
        for row in load_jsonl(path):
            doc_id = row.get("id")
            if doc_id and isinstance(row.get("payload"), dict) and doc_id not in cache:
                cache[doc_id] = row["payload"]
    return cache


def append_cache(path: Path, doc_id: str, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"id": doc_id, "payload": payload}, ensure_ascii=False) + "\n")


def analyze_corpus(
    docs: list[dict[str, Any]],
    *,
    use_groq: bool,
    limit: int | None,
    force: bool,
    sleep_s: float = 2.5,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    if limit:
        docs = docs[:limit]
    cache = {} if force else load_cache(CACHE_PATH, LEGACY_CACHE_PATH)
    client: GroqClient | None = None
    if use_groq:
        client = GroqClient(sleep_s=sleep_s)
        print(
            f"Groq: on  model={client._model_ok}  key={key_status()}  cached={len(cache)}  sleep={sleep_s}s",
            flush=True,
        )
    else:
        print(f"Groq: off  key={key_status()}  (heuristic gate + heuristic claims)", flush=True)

    labeled_rows: list[dict[str, Any]] = []
    claims_rows: list[dict[str, Any]] = []
    stats = {
        "docs": 0,
        "llm_calls": 0,
        "llm_errors": 0,
        "claims_kept": 0,
        "claims_dropped_unverified": 0,
    }

    for index, doc in enumerate(docs, start=1):
        stats["docs"] += 1
        heuristic_label, heuristic_reason = heuristic_gate(doc)
        llm_payload = cache.get(doc["id"])
        if client and llm_payload is None:
            try:
                llm_payload = client.generate_json(analysis_prompt(doc, heuristic_label))
                stats["llm_calls"] += 1
                append_cache(CACHE_PATH, doc["id"], llm_payload)
            except GroqQuotaError as exc:
                stats["llm_errors"] += 1
                print("  Groq daily quota exhausted; remaining docs use heuristic.", flush=True)
                print(f"  ({exc})", file=sys.stderr)
                client = None
                llm_payload = None
            except GroqError as exc:
                stats["llm_errors"] += 1
                print(f"  warn {doc['id']}: {exc}", file=sys.stderr)
                llm_payload = None
        labeled, claims = merge_llm_result(doc, heuristic_label, heuristic_reason, llm_payload)
        labeled_rows.append(labeled)
        claims_rows.extend(claims)
        stats["claims_kept"] += len(claims)
        if index % 25 == 0 or index == len(docs):
            print(
                f"  {index}/{len(docs)} labeled={labeled['label']} claims_so_far={len(claims_rows)}",
                flush=True,
            )

    if client:
        stats["llm_calls"] = client.request_count
    return labeled_rows, claims_rows, stats


def write_manifest(
    labeled: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    stats: dict[str, int],
    *,
    used_groq: bool,
) -> None:
    by_label: dict[str, int] = {}
    for row in labeled:
        label = row.get("label") or "unknown"
        by_label[label] = by_label.get(label, 0) + 1
    by_q: dict[str, int] = {}
    verified = 0
    for claim in claims:
        if claim.get("quote_verified"):
            verified += 1
        for qid in claim.get("discovery_question_ids") or []:
            key = str(qid)
            by_q[key] = by_q.get(key, 0) + 1
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "phase": 2,
        "product": "Myntra",
        "llm": "groq" if used_groq else None,
        "groq": used_groq,
        "groq_key": key_status(),
        "model": groq_model() if used_groq else None,
        "ran_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "input_corpus": str(PHASE1_RAW),
        "docs_labeled": len(labeled),
        "by_label": by_label,
        "claims": len(claims),
        "claims_quote_verified": verified,
        "gate_sample_n": 15,
        "gate_sample_checked": EVAL_NOTES_PATH.is_file(),
        "claims_by_question": dict(sorted(by_q.items(), key=lambda item: int(item[0]))),
        "stats": stats,
        "files": {
            "labeled": str(LABELED_PATH),
            "claims": str(CLAIMS_PATH),
            "gate_sample": str(SAMPLE_PATH),
            "eval_notes": str(EVAL_NOTES_PATH),
        },
        "re_run": "python run.py",
    }
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 2 Myntra relevance gate + claim extraction")
    parser.add_argument("--input", type=Path, default=PHASE1_RAW)
    parser.add_argument("--limit", type=int, default=None, help="process only the first N docs")
    parser.add_argument(
        "--no-groq",
        "--no-llm",
        "--no-gemini",
        action="store_true",
        dest="no_llm",
        help="heuristic only, even if a key is set",
    )
    parser.add_argument("--force", action="store_true", help="ignore LLM cache")
    parser.add_argument(
        "--sleep",
        type=float,
        default=2.5,
        help="seconds between Groq calls (free llama-3.3-70b ~30/min)",
    )
    parser.add_argument("--sample-only", action="store_true", help="rebuild 15-doc sample from existing labeled file")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.dry_run:
        print("Phase 2 dry-run")
        print(f"  input: {args.input}")
        print(f"  groq_key: {key_status()}")
        print(f"  model: {groq_model()}")
        print(f"  labeled -> {LABELED_PATH}")
        print(f"  claims  -> {CLAIMS_PATH}")
        print("  gate labels: myntra_primary | fashion_context | competitor_only | noise")
        print("  claims fail closed: quote must be a verbatim span in the source doc")
        print("  after run: 15-doc gate sample written for human check")
        return 0

    if args.sample_only:
        labeled = load_jsonl(LABELED_PATH)
        docs = {row["id"]: row for row in load_jsonl(args.input)}
        if not labeled:
            print("No labeled file yet. Run without --sample-only.", file=sys.stderr)
            return 1
        sample_labeled = pick_gate_sample(labeled, n=15)
        sample = sample_rows_for_docs(sample_labeled, docs)
        write_jsonl(SAMPLE_PATH, sample)
        write_eval_notes(EVAL_NOTES_PATH, sample, checked=False, accuracy=None, checker="pending")
        print(f"Wrote {SAMPLE_PATH} and {EVAL_NOTES_PATH}")
        return 0

    docs = load_jsonl(args.input)
    if not docs:
        print(f"No Phase 1 corpus at {args.input}", file=sys.stderr)
        return 1
    use_groq = (not args.no_llm) and key_status() == "set"
    if not args.no_llm and key_status() != "set":
        print("GROQ_API_KEY missing — running heuristic gate/extract. Add .env to enable Groq.")

    labeled, claims, stats = analyze_corpus(
        docs,
        use_groq=use_groq,
        limit=args.limit,
        force=args.force,
        sleep_s=args.sleep,
    )
    write_jsonl(LABELED_PATH, labeled)
    write_jsonl(CLAIMS_PATH, claims)
    docs_by_id = {row["id"]: row for row in docs}
    sample_labeled = pick_gate_sample(labeled, n=15)
    sample = sample_rows_for_docs(sample_labeled, docs_by_id)
    write_jsonl(SAMPLE_PATH, sample)
    write_eval_notes(EVAL_NOTES_PATH, sample, checked=False, accuracy=None, checker="pending")
    write_manifest(labeled, claims, stats, used_groq=use_groq)

    print(f"Done. labeled={len(labeled)} claims={len(claims)} groq={use_groq}", flush=True)
    print(f"Wrote {LABELED_PATH}")
    print(f"Wrote {CLAIMS_PATH}")
    print(f"Wrote {SAMPLE_PATH} (15-doc gate sample — fill human_label in GATE_CHECK.md)")
    return 0 if labeled else 1


if __name__ == "__main__":
    raise SystemExit(main())
