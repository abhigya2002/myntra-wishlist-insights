"""Phase 0 source spec: load, validate, and expand Reddit pull jobs for Phase 1."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

SPEC_PATH = Path(__file__).resolve().parent / "source_spec.json"

REQUIRED_ROOT_KEYS = (
    "phase",
    "version",
    "product",
    "priority_source",
    "time_window",
    "discovery_questions",
    "reddit",
    "do_not_ingest",
)

REQUIRED_QUERY_KEYS = ("id", "query", "bucket", "discovery_questions")
VALID_BUCKETS = {"myntra_named", "behavior_unbranded"}
VALID_SCOPES = {"site_wide", "primary", "india_general", "city", "global_context", "try_if_exists"}
QUESTION_IDS = set(range(1, 11))


class SpecError(ValueError):
    """Source spec failed validation."""


def load_spec(path: Path | None = None) -> dict[str, Any]:
    spec_path = path or SPEC_PATH
    with spec_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_spec(spec: dict[str, Any]) -> list[str]:
    """Return a list of error strings. Empty means valid."""
    errors: list[str] = []

    for key in REQUIRED_ROOT_KEYS:
        if key not in spec:
            errors.append(f"missing root key: {key}")
    if errors:
        return errors

    if spec["phase"] != 0:
        errors.append(f"phase must be 0, got {spec['phase']!r}")
    if spec["product"] != "Myntra":
        errors.append(f"product must be Myntra, got {spec['product']!r}")
    if spec["priority_source"] != "reddit":
        errors.append(f"priority_source must be reddit, got {spec['priority_source']!r}")

    window = spec["time_window"]
    try:
        start = date.fromisoformat(window["start"])
        end = date.fromisoformat(window["end"])
        if start >= end:
            errors.append("time_window.start must be before time_window.end")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"invalid time_window dates: {exc}")

    questions = spec["discovery_questions"]
    expected = {str(i) for i in range(1, 11)}
    if set(questions) != expected:
        errors.append("discovery_questions must have keys 1 through 10")

    reddit = spec["reddit"]
    tiers = reddit.get("subreddit_tiers", {})
    for tier_name in ("primary", "india_general", "city"):
        names = tiers.get(tier_name)
        if not names:
            errors.append(f"reddit.subreddit_tiers.{tier_name} must be a non-empty list")

    scope_map = reddit.get("search_scope", {})
    for bucket, scopes in scope_map.items():
        if bucket not in VALID_BUCKETS:
            errors.append(f"unknown search_scope bucket: {bucket}")
        for scope in scopes:
            if scope not in VALID_SCOPES:
                errors.append(f"unknown search scope {scope!r} on bucket {bucket}")

    first_slice = reddit.get("phase1_first_slice")
    if not first_slice or not first_slice.get("include_scopes"):
        errors.append("reddit.phase1_first_slice.include_scopes is required")
    else:
        for scope in first_slice["include_scopes"]:
            if scope not in VALID_SCOPES:
                errors.append(f"unknown phase1_first_slice scope: {scope}")

    queries = reddit.get("queries", [])
    if not queries:
        errors.append("reddit.queries is empty")

    seen_ids: set[str] = set()
    for index, query in enumerate(queries):
        prefix = f"queries[{index}]"
        for key in REQUIRED_QUERY_KEYS:
            if key not in query:
                errors.append(f"{prefix} missing {key}")
        if "id" in query:
            if query["id"] in seen_ids:
                errors.append(f"duplicate query id: {query['id']}")
            seen_ids.add(query["id"])
        bucket = query.get("bucket")
        if bucket not in VALID_BUCKETS:
            errors.append(f"{prefix} invalid bucket: {bucket!r}")
        for qid in query.get("discovery_questions", []):
            if qid not in QUESTION_IDS:
                errors.append(f"{prefix} discovery question {qid} not in 1-10")

    if spec["priority_source"] == "reddit" and not spec.get("do_not_ingest"):
        errors.append("do_not_ingest must list exclusions")

    return errors


def _subreddits_for_scope(spec: dict[str, Any], scope: str) -> list[str | None]:
    if scope == "site_wide":
        return [None]
    tiers = spec["reddit"]["subreddit_tiers"]
    return list(tiers[scope])


def expand_pull_jobs(spec: dict[str, Any], slice_name: str = "full") -> list[dict[str, Any]]:
    """Expand queries x search scopes into concrete Phase 1 pull jobs.

    A job with subreddit=None means site-wide Reddit search.
    slice_name='first' keeps only site_wide + primary (see phase1_first_slice).
    """
    if slice_name not in {"full", "first"}:
        raise SpecError(f"slice_name must be 'full' or 'first', got {slice_name!r}")

    reddit = spec["reddit"]
    scope_map: dict[str, list[str]] = reddit["search_scope"]
    allowed_scopes = None
    if slice_name == "first":
        allowed_scopes = set(reddit["phase1_first_slice"]["include_scopes"])

    jobs: list[dict[str, Any]] = []
    for query in reddit["queries"]:
        for scope in scope_map[query["bucket"]]:
            if allowed_scopes is not None and scope not in allowed_scopes:
                continue
            for subreddit in _subreddits_for_scope(spec, scope):
                jobs.append(
                    {
                        "pull_job_id": _job_id(query["id"], scope, subreddit),
                        "query_id": query["id"],
                        "query": query["query"],
                        "bucket": query["bucket"],
                        "discovery_questions": query["discovery_questions"],
                        "search_scope": scope,
                        "subreddit": subreddit,
                        "include_comments": reddit["include_comments"],
                        "window_start": spec["time_window"]["start"],
                        "window_end": spec["time_window"]["end"],
                        "spec_version": spec["version"],
                        "slice": slice_name,
                    }
                )
    return jobs


def _job_id(query_id: str, scope: str, subreddit: str | None) -> str:
    target = subreddit or "site_wide"
    return f"{query_id}__{scope}__{target}"


def queries_for_question(spec: dict[str, Any], question_id: int) -> list[dict[str, Any]]:
    if question_id not in QUESTION_IDS:
        raise SpecError(f"question_id must be 1-10, got {question_id}")
    return [
        query
        for query in spec["reddit"]["queries"]
        if question_id in query["discovery_questions"]
    ]


def summary_lines(spec: dict[str, Any], jobs: list[dict[str, Any]]) -> list[str]:
    reddit = spec["reddit"]
    named = sum(1 for q in reddit["queries"] if q["bucket"] == "myntra_named")
    unbranded = sum(1 for q in reddit["queries"] if q["bucket"] == "behavior_unbranded")
    tiers = reddit["subreddit_tiers"]
    lines = [
        f"product: {spec['product']}",
        f"phase: {spec['phase']}  spec_version: {spec['version']}",
        f"priority_source: {spec['priority_source']}",
        f"window: {spec['time_window']['start']} -> {spec['time_window']['end']} "
        f"({spec['time_window']['duration_months']} months, {spec['time_window']['timezone']})",
        f"queries: {len(reddit['queries'])} ({named} myntra_named, {unbranded} behavior_unbranded)",
        f"subreddits: primary={len(tiers['primary'])} india_general={len(tiers['india_general'])} "
        f"city={len(tiers['city'])} global_context={len(tiers['global_context'])} "
        f"try_if_exists={len(tiers['try_if_exists'])}",
        f"pull_jobs: {len(jobs)}",
        f"do_not_ingest: {len(spec['do_not_ingest'])} exclusions",
        "later_phase_seeds: play_store, app_store, communities, youtube, social (not Phase 1)",
    ]
    return lines


def _print_jobs(jobs: list[dict[str, Any]]) -> None:
    for job in jobs:
        target = job["subreddit"] or "site_wide"
        questions = ",".join(str(q) for q in job["discovery_questions"])
        print(
            f"{job['pull_job_id']}\t{job['bucket']}\tr/{target}\t"
            f"q={questions}\t{job['query']}"
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 0 source spec tools")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="validate source_spec.json")
    sub.add_parser("summary", help="print corpus-design summary")
    jobs_parser = sub.add_parser("jobs", help="print expanded Phase 1 pull jobs")
    jobs_parser.add_argument(
        "--slice",
        choices=("first", "full"),
        default="full",
        help="first = site_wide + primary only; full = all scopes",
    )
    query_parser = sub.add_parser("queries", help="list queries tagged to a discovery question")
    query_parser.add_argument("--question", type=int, required=True, choices=range(1, 11))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    spec = load_spec()
    errors = validate_spec(spec)
    if errors:
        print("source_spec.json is invalid:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    if args.command == "validate":
        print(f"OK  {SPEC_PATH.name}  version={spec['version']}  queries={len(spec['reddit']['queries'])}")
        return 0

    jobs = expand_pull_jobs(spec)
    first_jobs = expand_pull_jobs(spec, slice_name="first")

    if args.command == "summary":
        for line in summary_lines(spec, jobs):
            print(line)
        print(f"phase1_first_slice_jobs: {len(first_jobs)}")
        return 0

    if args.command == "jobs":
        _print_jobs(expand_pull_jobs(spec, slice_name=args.slice))
        return 0

    if args.command == "queries":
        question = spec["discovery_questions"][str(args.question)]
        print(f"Q{args.question}: {question}")
        for query in queries_for_question(spec, args.question):
            print(f"  {query['id']}\t{query['bucket']}\t{query['query']}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
