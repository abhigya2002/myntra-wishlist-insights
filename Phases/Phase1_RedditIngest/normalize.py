"""Map Pullpush rows to the architecture raw-document shape."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from typing import Any

REMOVED = {"", "[deleted]", "[removed]", "[removed by reddit]"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def from_created_utc(value: Any) -> str | None:
    try:
        stamp = int(float(value))
    except (TypeError, ValueError):
        return None
    if stamp <= 0:
        return None
    return datetime.fromtimestamp(stamp, tz=timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value)).replace("\r\n", "\n").strip()
    return text


def is_removed(*parts: str) -> bool:
    return all(part.strip().lower() in REMOVED for part in parts if True)


def reddit_url(permalink: str | None, fallback_id: str | None = None, kind: str = "submission") -> str:
    if permalink:
        if permalink.startswith("http"):
            return permalink
        return "https://www.reddit.com" + permalink
    if fallback_id and kind == "submission":
        return f"https://www.reddit.com/comments/{fallback_id}"
    return ""


def bare_link_id(link_id: str | None) -> str:
    if not link_id:
        return ""
    return link_id.split("_", 1)[-1]


def thread_title_from_permalink(permalink: str | None) -> str:
    if not permalink:
        return ""
    parts = [p for p in permalink.split("/") if p]
    # /r/sub/comments/<post>/<slug>/...
    try:
        idx = parts.index("comments")
        slug = parts[idx + 2] if len(parts) > idx + 2 else ""
    except (ValueError, IndexError):
        return ""
    return slug.replace("_", " ")


def submission_document(row: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any] | None:
    post_id = str(row.get("id") or "")
    title = clean_text(row.get("title"))
    body = clean_text(row.get("selftext"))
    if not post_id or is_removed(title, body):
        return None
    if title.lower() in REMOVED and body.lower() in REMOVED:
        return None
    url = reddit_url(row.get("permalink"), post_id, "submission")
    return {
        "id": f"t3_{post_id}",
        "source": "reddit",
        "url": url,
        "captured_at": utc_now(),
        "created_at": from_created_utc(row.get("created_utc")),
        "title": title,
        "body": body,
        "thread_context": title,
        "language": None,
        "raw_metadata": {
            **meta,
            "kind": "submission",
            "reddit_id": post_id,
            "subreddit": row.get("subreddit") or meta.get("subreddit"),
            "score": row.get("score"),
            "num_comments": row.get("num_comments"),
            "over_18": row.get("over_18"),
        },
    }


def comment_document(
    row: dict[str, Any],
    meta: dict[str, Any],
    *,
    parent_title: str = "",
) -> dict[str, Any] | None:
    comment_id = str(row.get("id") or "")
    body = clean_text(row.get("body"))
    if not comment_id or body.lower() in REMOVED:
        return None
    permalink = row.get("permalink")
    title = clean_text(row.get("link_title")) or parent_title or thread_title_from_permalink(permalink)
    url = reddit_url(permalink, comment_id, "comment")
    link_id = bare_link_id(str(row.get("link_id") or ""))
    return {
        "id": f"t1_{comment_id}",
        "source": "reddit",
        "url": url,
        "captured_at": utc_now(),
        "created_at": from_created_utc(row.get("created_utc")),
        "title": title,
        "body": body,
        "thread_context": title,
        "language": None,
        "raw_metadata": {
            **meta,
            "kind": "comment",
            "reddit_id": comment_id,
            "subreddit": row.get("subreddit") or meta.get("subreddit"),
            "score": row.get("score"),
            "link_id": link_id or None,
            "parent_id": row.get("parent_id"),
        },
    }


_JOB_SAFE = re.compile(r"[^a-zA-Z0-9._-]+")


def job_id(query_id: str, scope: str, subreddit: str | None, kind: str) -> str:
    target = subreddit or "site_wide"
    return _JOB_SAFE.sub("_", f"{query_id}__{scope}__{target}__{kind}")
