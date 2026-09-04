"""Pull public Myntra Play Store and App Store reviews into the raw corpus."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PHASE4_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PHASE4_DIR))

from app_store import AppStoreError, fetch_reviews as fetch_app_store  # noqa: E402
from config import (  # noqa: E402
    APP_STORE_ID,
    DEFAULT_APP_STORE_PAGES,
    DEFAULT_PLAY_COUNT,
    INGEST_MANIFEST,
    PHASE0_SPEC,
    PLAY_APP_ID,
    PULL_LOG_PATH,
    RAW_PATH,
    STORE_KEYWORDS,
)
from io_util import append_jsonl, read_json, write_json, write_jsonl  # noqa: E402
from normalize import app_store_document, in_window, play_document, utc_now  # noqa: E402
from play_store import PlayStoreError, fetch_reviews as fetch_play  # noqa: E402


def load_window() -> tuple[str, str]:
    spec = read_json(PHASE0_SPEC)
    window = spec.get("time_window") or {}
    start = str(window.get("start") or "2024-08-17")
    end = utc_now()
    return start, end


def _dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    kept: list[dict[str, Any]] = []
    for row in rows:
        key = str(row.get("id") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        kept.append(row)
    return kept


def ingest(
    *,
    play_count: int,
    app_pages: int,
    skip_play: bool,
    skip_app: bool,
) -> dict[str, Any]:
    start, end = load_window()
    PULL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if PULL_LOG_PATH.is_file():
        PULL_LOG_PATH.unlink()
    documents: list[dict[str, Any]] = []
    stats = {
        "play_fetched": 0,
        "play_kept": 0,
        "app_fetched": 0,
        "app_kept": 0,
        "outside_window": 0,
        "play_backend": None,
        "errors": [],
    }

    if not skip_play:
        try:
            raw_play, backend = fetch_play(app_id=PLAY_APP_ID, count=play_count)
            stats["play_fetched"] = len(raw_play)
            stats["play_backend"] = backend
            meta = {
                "query_id": "play_recent",
                "query": " ".join(STORE_KEYWORDS),
                "lang": "en",
                "country": "in",
                "spec_version": "1.0.0",
            }
            for row in raw_play:
                doc = play_document(row, meta)
                if not doc:
                    continue
                if not in_window(doc.get("created_at"), start, end):
                    stats["outside_window"] += 1
                    continue
                documents.append(doc)
                stats["play_kept"] += 1
            append_jsonl(
                PULL_LOG_PATH,
                {"store": "play_store", "backend": backend, "fetched": len(raw_play), "kept": stats["play_kept"], "at": utc_now()},
            )
        except PlayStoreError as exc:
            stats["errors"].append(f"play_store: {exc}")
            append_jsonl(PULL_LOG_PATH, {"store": "play_store", "error": str(exc), "at": utc_now()})

    if not skip_app:
        try:
            raw_app = fetch_app_store(app_id=APP_STORE_ID, country="in", pages=app_pages)
            stats["app_fetched"] = len(raw_app)
            meta = {
                "query_id": "appstore_recent",
                "query": " ".join(STORE_KEYWORDS),
                "lang": "en",
                "country": "in",
                "app_id": APP_STORE_ID,
                "spec_version": "1.0.0",
            }
            for row in raw_app:
                doc = app_store_document(row, meta)
                if not doc:
                    continue
                if not in_window(doc.get("created_at"), start, end):
                    stats["outside_window"] += 1
                    continue
                documents.append(doc)
                stats["app_kept"] += 1
            append_jsonl(
                PULL_LOG_PATH,
                {"store": "app_store", "fetched": len(raw_app), "kept": stats["app_kept"], "at": utc_now()},
            )
        except AppStoreError as exc:
            stats["errors"].append(f"app_store: {exc}")
            append_jsonl(PULL_LOG_PATH, {"store": "app_store", "error": str(exc), "at": utc_now()})

    documents = _dedupe(documents)
    write_jsonl(RAW_PATH, documents)
    payload = {
        "phase": 4,
        "product": "Myntra",
        "sources": ["play_store", "app_store"],
        "play_app_id": PLAY_APP_ID,
        "app_store_id": APP_STORE_ID,
        "time_window": {"start": start, "end": end},
        "pulled_at": utc_now(),
        "document_count": len(documents),
        "by_source": {
            "play_store": sum(1 for row in documents if row.get("source") == "play_store"),
            "app_store": sum(1 for row in documents if row.get("source") == "app_store"),
        },
        "stats": stats,
        "files": {"documents": str(RAW_PATH), "pull_log": str(PULL_LOG_PATH)},
        "re_run": "python ingest.py",
    }
    write_json(INGEST_MANIFEST, payload)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 4 Play/App Store ingest")
    parser.add_argument("--play-count", type=int, default=DEFAULT_PLAY_COUNT)
    parser.add_argument("--app-pages", type=int, default=DEFAULT_APP_STORE_PAGES)
    parser.add_argument("--skip-play", action="store_true")
    parser.add_argument("--skip-app", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.dry_run:
        start, end = load_window()
        print("Phase 4 ingest dry-run")
        print(f"  play: {PLAY_APP_ID} count={args.play_count}")
        print(f"  app store: {APP_STORE_ID} pages={args.app_pages}")
        print(f"  window: {start} -> {end}")
        print(f"  raw -> {RAW_PATH}")
        return 0
    payload = ingest(
        play_count=args.play_count,
        app_pages=args.app_pages,
        skip_play=args.skip_play,
        skip_app=args.skip_app,
    )
    print(
        f"Done. docs={payload['document_count']} "
        f"play={payload['by_source']['play_store']} "
        f"app={payload['by_source']['app_store']}",
        flush=True,
    )
    if payload["stats"]["errors"]:
        for err in payload["stats"]["errors"]:
            print(f"  warn {err}", flush=True)
    print(f"Wrote {RAW_PATH}", flush=True)
    return 0 if payload["document_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
