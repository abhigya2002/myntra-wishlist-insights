"""Phase 1: Reddit ingest for Myntra.

Re-runnable from Phase 0 source_spec.json. Collection follows
DOCS/reviewfetchingdocument.txt (three-pass Reddit). Primary API is Pullpush;
if Pullpush refuses agents, Arctic Shift is used with the same Myntra-only
passes. Never fetches AJIO/Nykaa as the product under study.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PHASE1_DIR = Path(__file__).resolve().parent
PHASE0_DIR = PHASE1_DIR.parent / "Phase0_CorpusDesign"
DATA_DIR = PHASE1_DIR / "data" / "raw"

if str(PHASE0_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE0_DIR))

from spec import load_spec, validate_spec  # noqa: E402

from arctic_shift import ArcticShiftClient, ArcticShiftError  # noqa: E402
from corpus import Corpus  # noqa: E402
from myntra_filter import MYNTRA_RE, ensure_myntra_query, keep_document  # noqa: E402
from normalize import (  # noqa: E402
    bare_link_id,
    comment_document,
    job_id,
    submission_document,
    utc_now,
)
from pullpush import PullpushBlockedError, PullpushClient, PullpushError  # noqa: E402


def window_epochs(spec: dict[str, Any]) -> tuple[int, int]:
    start = spec["time_window"]["start"]
    end = spec["time_window"]["end"]
    after = int(datetime.fromisoformat(start).replace(tzinfo=timezone.utc).timestamp())
    end_dt = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
    before = int(end_dt.timestamp())
    return after, before


def myntra_named_queries(spec: dict[str, Any]) -> list[dict[str, Any]]:
    return [query for query in spec["reddit"]["queries"] if query["bucket"] == "myntra_named"]


def ingest_subreddits(spec: dict[str, Any]) -> list[str]:
    """Subreddits searched when site-wide archive search is unavailable.

    Primary fashion subs first, then India general / city / try-if-exists.
    All queries still require Myntra in the document (see myntra_filter).
    """
    tiers = spec["reddit"]["subreddit_tiers"]
    ordered = []
    seen: set[str] = set()
    for tier in ("primary", "india_general", "city", "try_if_exists"):
        for name in tiers.get(tier, []):
            if name not in seen:
                seen.add(name)
                ordered.append(name)
    return ordered


def tag_spec_queries(corpus: Corpus, spec: dict[str, Any]) -> None:
    """Attach matching myntra_named query ids after fetch (for query logging)."""
    queries = myntra_named_queries(spec)
    for document in corpus.documents():
        blob = f"{document.get('title','')} {document.get('body','')}".lower()
        matched = []
        for query in queries:
            terms = [t for t in MYNTRA_RE.sub(" ", query["query"].lower()).replace('"', " ").split() if t]
            if query["id"] == "mn_brand" or (terms and all(term in blob for term in terms)):
                matched.append(query["id"])
        meta = document.setdefault("raw_metadata", {})
        existing = meta.get("query_id")
        ids = list(dict.fromkeys(([existing] if existing else []) + matched))
        meta["matched_query_ids"] = ids


def base_meta(spec: dict[str, Any], query: dict[str, Any], *, scope: str, subreddit: str | None, kind: str, pass_name: str) -> dict[str, Any]:
    return {
        "query_id": query["id"],
        "query": query["query"],
        "search_scope": scope,
        "subreddit": subreddit,
        "pull_job_id": job_id(query["id"], scope, subreddit, kind),
        "spec_version": spec["version"],
        "pass_name": pass_name,
        "discovery_questions": query.get("discovery_questions", []),
    }


def add_submission(corpus: Corpus, row: dict[str, Any], meta: dict[str, Any], stats: dict[str, int]) -> None:
    document = submission_document(row, meta)
    if document is None:
        stats["skipped_removed"] += 1
        return
    if not keep_document(
        title=document["title"],
        body=document["body"],
        url=document["url"],
        thread_context=document["thread_context"],
    ):
        stats["skipped_not_myntra"] += 1
        return
    if corpus.add(document):
        stats["kept"] += 1
    else:
        stats["duplicate"] += 1


def add_comment(
    corpus: Corpus,
    row: dict[str, Any],
    meta: dict[str, Any],
    stats: dict[str, int],
    *,
    parent_title: str = "",
    in_myntra_thread: bool = False,
) -> None:
    document = comment_document(row, meta, parent_title=parent_title)
    if document is None:
        stats["skipped_removed"] += 1
        return
    if not keep_document(
        title=document["title"],
        body=document["body"],
        url=document["url"],
        thread_context=document["thread_context"],
        in_myntra_thread=in_myntra_thread,
    ):
        stats["skipped_not_myntra"] += 1
        return
    if corpus.add(document):
        stats["kept"] += 1
    else:
        stats["duplicate"] += 1


def new_stats() -> dict[str, int]:
    return {
        "kept": 0,
        "duplicate": 0,
        "skipped_not_myntra": 0,
        "skipped_removed": 0,
        "api_errors": 0,
    }


def primary_subreddits(spec: dict[str, Any]) -> list[str]:
    return list(spec["reddit"]["subreddit_tiers"]["primary"])


def _safe_page(
    client: Any,
    kind: str,
    stats: dict[str, int],
    **kwargs: Any,
) -> list[dict[str, Any]]:
    try:
        return client.search_paginated(kind, **kwargs)
    except (PullpushError, ArcticShiftError) as exc:
        stats["api_errors"] += 1
        print(f"  warn: {exc}", file=sys.stderr)
        return []


def run_reviewlens(
    spec: dict[str, Any],
    client: Any,
    args: argparse.Namespace,
) -> tuple[Corpus, dict[str, int], list[dict[str, Any]]]:
    """Three-pass collection from the ReviewLens Reddit fetcher, Myntra-only."""
    corpus = Corpus()
    stats = new_stats()
    log: list[dict[str, Any]] = []
    after, before = window_epochs(spec)
    queries = myntra_named_queries(spec)
    brand = next(query for query in queries if query["id"] == "mn_brand")
    specific = [query for query in queries if query["id"] != "mn_brand"]
    if args.query_ids:
        wanted = set(args.query_ids)
        specific = [query for query in specific if query["id"] in wanted]
        brand_run = "mn_brand" in wanted
    else:
        brand_run = True

    site_wide = bool(getattr(client, "supports_site_wide", True))
    primary = primary_subreddits(spec)
    sub_jobs = primary if site_wide else ingest_subreddits(spec)

    def record(pass_name: str, query: dict[str, Any], kind: str, scope: str, subreddit: str | None, fetched: int) -> None:
        log.append(
            {
                "captured_at": utc_now(),
                "pass_name": pass_name,
                "query_id": query["id"],
                "query": ensure_myntra_query(query["query"]),
                "kind": kind,
                "search_scope": scope,
                "subreddit": subreddit,
                "fetched": fetched,
            }
        )

    # Pass 1 — subreddit submissions (fashion communities) + site-wide brand catch.
    print(f"Pass 1: Myntra submissions via {getattr(client, 'name', 'client')}")
    if brand_run and site_wide:
        rows = _safe_page(
            client,
            "submission",
            stats,
            q=ensure_myntra_query(brand["query"]),
            after=after,
            before=before,
            max_items=args.max_brand,
        )
        meta = base_meta(spec, brand, scope="site_wide", subreddit=None, kind="submission", pass_name="pass1_sitewide")
        for row in rows:
            add_submission(corpus, row, meta, stats)
        record("pass1_sitewide", brand, "submission", "site_wide", None, len(rows))
        print(f"  site-wide submissions q=myntra: {len(rows)}")

    if brand_run:
        for subreddit in sub_jobs:
            rows = _safe_page(
                client,
                "submission",
                stats,
                q=ensure_myntra_query(brand["query"]),
                subreddit=subreddit,
                after=after,
                before=before,
                max_items=args.max_per_subreddit,
            )
            meta = base_meta(spec, brand, scope="primary", subreddit=subreddit, kind="submission", pass_name="pass1_subreddit")
            for row in rows:
                add_submission(corpus, row, meta, stats)
            record("pass1_subreddit", brand, "submission", "primary", subreddit, len(rows))
            print(f"  r/{subreddit} submissions: {len(rows)}")

    # Pass 2 — comment search. Site-wide per spec query when the API allows it;
    # otherwise q=myntra per ingest subreddit (Arctic Shift requires a subreddit).
    print("Pass 2: Myntra comment search")
    if site_wide:
        comment_queries = ([brand] if brand_run else []) + specific
        for query in comment_queries:
            q = ensure_myntra_query(query["query"])
            cap = args.max_brand if query["id"] == "mn_brand" else args.max_per_query
            rows = _safe_page(
                client,
                "comment",
                stats,
                q=q,
                after=after,
                before=before,
                max_items=cap,
            )
            meta = base_meta(spec, query, scope="site_wide", subreddit=None, kind="comment", pass_name="pass2_comments")
            for row in rows:
                add_comment(corpus, row, meta, stats)
            record("pass2_comments", query, "comment", "site_wide", None, len(rows))
            print(f"  comments {query['id']}: {len(rows)}")
    elif brand_run:
        for subreddit in sub_jobs:
            rows = _safe_page(
                client,
                "comment",
                stats,
                q=ensure_myntra_query(brand["query"]),
                subreddit=subreddit,
                after=after,
                before=before,
                max_items=args.max_per_subreddit,
            )
            meta = base_meta(spec, brand, scope="primary", subreddit=subreddit, kind="comment", pass_name="pass2_comments")
            for row in rows:
                add_comment(corpus, row, meta, stats)
            record("pass2_comments", brand, "comment", "primary", subreddit, len(rows))
            print(f"  r/{subreddit} comments: {len(rows)}")

    # Pass 3 — extra comments from the two highest-priority fashion subs (Pullpush only;
    # Arctic Shift already searched every ingest subreddit in pass 2).
    if site_wide and brand_run:
        print("Pass 3: comments in top primary subreddits")
        for subreddit in primary[:2]:
            rows = _safe_page(
                client,
                "comment",
                stats,
                q=ensure_myntra_query(brand["query"]),
                subreddit=subreddit,
                after=after,
                before=before,
                max_items=args.max_per_subreddit,
            )
            meta = base_meta(spec, brand, scope="primary", subreddit=subreddit, kind="comment", pass_name="pass3_subreddit_comments")
            for row in rows:
                add_comment(corpus, row, meta, stats)
            record("pass3_subreddit_comments", brand, "comment", "primary", subreddit, len(rows))
            print(f"  r/{subreddit} comments: {len(rows)}")

    if not args.skip_thread_comments:
        _expand_thread_comments(spec, client, args, corpus, stats, log, after, before)

    return corpus, stats, log


def _expand_thread_comments(
    spec: dict[str, Any],
    client: Any,
    args: argparse.Namespace,
    corpus: Corpus,
    stats: dict[str, int],
    log: list[dict[str, Any]],
    after: int,
    before: int,
) -> None:
    print("Pass 4: comments on kept Myntra threads")
    submissions = corpus.submissions()[: args.max_threads]
    for document in submissions:
        reddit_id = document["raw_metadata"].get("reddit_id")
        if not reddit_id:
            continue
        try:
            rows = client.search_comments(
                link_id=bare_link_id(str(reddit_id)),
                size=min(100, args.max_thread_comments),
                after=after,
                before=before,
                sort="desc",
                sort_type="created_utc",
            )
        except (PullpushError, ArcticShiftError) as exc:
            stats["api_errors"] += 1
            print(f"  warn: thread {reddit_id}: {exc}", file=sys.stderr)
            continue
        meta = {
            **document["raw_metadata"],
            "kind": "comment",
            "pass_name": "pass4_thread",
            "pull_job_id": job_id(
                document["raw_metadata"].get("query_id") or "mn_brand",
                "thread",
                document["raw_metadata"].get("subreddit"),
                "comment",
            ),
        }
        kept_before = stats["kept"]
        for row in rows[: args.max_thread_comments]:
            add_comment(
                corpus,
                row,
                meta,
                stats,
                parent_title=document["title"],
                in_myntra_thread=True,
            )
        fetched = len(rows[: args.max_thread_comments])
        log.append(
            {
                "captured_at": utc_now(),
                "pass_name": "pass4_thread",
                "query_id": document["raw_metadata"].get("query_id") or "mn_brand",
                "query": "thread",
                "kind": "comment",
                "search_scope": "thread",
                "subreddit": document["raw_metadata"].get("subreddit"),
                "fetched": fetched,
            }
        )
        print(f"  thread {reddit_id}: fetched {fetched} kept +{stats['kept'] - kept_before}")


def write_outputs(
    spec: dict[str, Any],
    corpus: Corpus,
    stats: dict[str, int],
    log: list[dict[str, Any]],
    out_dir: Path,
    args: argparse.Namespace,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    docs_path = out_dir / "reddit_documents.jsonl"
    log_path = out_dir / "pull_log.jsonl"
    manifest_path = out_dir / "manifest.json"

    corpus.write_jsonl(docs_path)
    with log_path.open("w", encoding="utf-8") as handle:
        for row in log:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    kinds: dict[str, int] = {}
    subreddits: dict[str, int] = {}
    for document in corpus.documents():
        meta = document.get("raw_metadata") or {}
        kind = meta.get("kind") or "unknown"
        kinds[kind] = kinds.get(kind, 0) + 1
        sub = meta.get("subreddit") or "unknown"
        subreddits[sub] = subreddits.get(sub, 0) + 1

    manifest = {
        "phase": 1,
        "product": "Myntra",
        "source": "reddit",
        "adapter": getattr(args, "backend_used", "pullpush"),
        "mode": "reviewlens_myntra",
        "spec_version": spec["version"],
        "time_window": spec["time_window"],
        "pulled_at": utc_now(),
        "document_count": len(corpus),
        "by_kind": kinds,
        "by_subreddit": dict(sorted(subreddits.items(), key=lambda item: (-item[1], item[0]))),
        "stats": stats,
        "api_requests": None,
        "files": {
            "documents": str(docs_path),
            "pull_log": str(log_path),
        },
        "cli": {
            "max_brand": args.max_brand,
            "max_per_query": args.max_per_query,
            "max_per_subreddit": args.max_per_subreddit,
            "skip_thread_comments": args.skip_thread_comments,
        },
        "myntra_only": True,
        "re_run": "python ingest.py",
    }
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return manifest_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 1 Myntra Reddit ingest (Pullpush)")
    parser.add_argument("--out", type=Path, default=DATA_DIR, help="raw corpus directory")
    parser.add_argument("--sleep", type=float, default=4.0, help="seconds between Pullpush calls (Pullpush ~1000/hour)")
    parser.add_argument("--max-brand", type=int, default=150, help="cap for q=myntra site-wide")
    parser.add_argument("--max-per-query", type=int, default=40, help="cap for each named discovery query")
    parser.add_argument("--max-per-subreddit", type=int, default=50, help="cap per primary subreddit")
    parser.add_argument("--max-thread-comments", type=int, default=50)
    parser.add_argument("--max-threads", type=int, default=40, help="max Myntra submissions to expand")
    parser.add_argument("--skip-thread-comments", action="store_true")
    parser.add_argument(
        "--query-ids",
        nargs="*",
        default=None,
        help="optional subset of spec query ids (e.g. mn_brand mn_wishlist)",
    )
    parser.add_argument(
        "--backend",
        choices=("auto", "pullpush", "arctic_shift"),
        default="auto",
        help="auto tries Pullpush (ReviewLens), then Arctic Shift if agents are blocked",
    )
    parser.add_argument("--dry-run", action="store_true", help="print planned passes and exit")
    parser.add_argument(
        "--expand-threads",
        action="store_true",
        help="load existing reddit_documents.jsonl and fetch comments on kept Myntra threads",
    )
    return parser


def dry_run(spec: dict[str, Any], args: argparse.Namespace) -> int:
    queries = myntra_named_queries(spec)
    after, before = window_epochs(spec)
    print("Phase 1 dry-run (Myntra only)")
    print(f"  backend: {args.backend} (Pullpush first; Arctic Shift if Pullpush blocks agents)")
    print(f"  window: {spec['time_window']['start']} -> {spec['time_window']['end']} ({after}..{before})")
    print(f"  named queries: {len(queries)}")
    print(f"  primary subreddits: {', '.join(primary_subreddits(spec))}")
    print(f"  ingest subreddits if no site-wide: {', '.join(ingest_subreddits(spec))}")
    print("  pass 1: submissions q=myntra (site-wide if API allows, else each ingest subreddit)")
    print("  pass 2: comments for myntra_named queries (site-wide) or q=myntra per subreddit")
    print("  pass 3: comments q=myntra in top 2 primary subreddits (Pullpush only)")
    print("  pass 4: thread comments on kept Myntra submissions" + (" (skipped)" if args.skip_thread_comments else ""))
    print("  behavior_unbranded queries: not fetched (Myntra-only Phase 1)")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    spec = load_spec()
    errors = validate_spec(spec)
    if errors:
        print("Phase 0 source_spec.json is invalid:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    if spec["product"] != "Myntra":
        print("Refusing to ingest: spec product is not Myntra", file=sys.stderr)
        return 1

    if args.dry_run:
        return dry_run(spec, args)

    client: Any
    if args.backend == "arctic_shift":
        client = ArcticShiftClient(sleep_s=min(args.sleep, 1.5))
    elif args.backend == "pullpush":
        client = PullpushClient(sleep_s=args.sleep)
    else:
        print("Trying Pullpush (ReviewLens primary)...")
        probe = PullpushClient(sleep_s=args.sleep, max_retries=1)
        try:
            probe.search_submissions(q="myntra", size=1, subreddit="india")
            client = PullpushClient(sleep_s=args.sleep)
            print("Using Pullpush")
        except PullpushBlockedError as exc:
            print(f"Pullpush blocked agents; falling back to Arctic Shift. ({exc})")
            client = ArcticShiftClient(sleep_s=min(args.sleep, 1.5))
        except PullpushError as exc:
            print(f"Pullpush failed ({exc}); falling back to Arctic Shift.")
            client = ArcticShiftClient(sleep_s=min(args.sleep, 1.5))

    args.backend_used = getattr(client, "name", args.backend)
    print(f"Ingest start  product=Myntra  adapter={args.backend_used}  out={args.out}")
    if args.expand_threads:
        docs_path = args.out / "reddit_documents.jsonl"
        corpus = Corpus.load_jsonl(docs_path)
        if not len(corpus):
            print(f"No existing corpus at {docs_path}", file=sys.stderr)
            return 1
        stats = new_stats()
        log: list[dict[str, Any]] = []
        after, before = window_epochs(spec)
        print(f"Expanding threads from {len(corpus.submissions())} submissions")
        args.skip_thread_comments = False
        _expand_thread_comments(spec, client, args, corpus, stats, log, after, before)
        tag_spec_queries(corpus, spec)
        manifest_path = write_outputs(spec, corpus, stats, log, args.out, args)
    else:
        corpus, stats, log = run_reviewlens(spec, client, args)
        tag_spec_queries(corpus, spec)
        manifest_path = write_outputs(spec, corpus, stats, log, args.out, args)

    # patch request count into manifest
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["api_requests"] = client.request_count
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Done. documents={len(corpus)} kept={stats['kept']} not_myntra={stats['skipped_not_myntra']} "
          f"removed={stats['skipped_removed']} errors={stats['api_errors']} requests={client.request_count}")
    print(f"Wrote {args.out / 'reddit_documents.jsonl'}")
    print(f"Wrote {manifest_path}")
    return 0 if len(corpus) else 1


if __name__ == "__main__":
    raise SystemExit(main())
