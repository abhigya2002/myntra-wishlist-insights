"""Map store reviews onto the architecture raw-document shape."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from config import APP_STORE_NAME, APP_STORE_URL, PLAY_APP_ID, PLAY_URL, STORE_KEYWORDS

_WS = re.compile(r"\s+")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean(value: Any) -> str:
    return _WS.sub(" ", str(value or "")).strip()


def keyword_hits(text: str) -> list[str]:
    lower = text.lower()
    return [token for token in STORE_KEYWORDS if token in lower]


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        stamp = value
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return stamp.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except ValueError:
        return text


def in_window(created_at: str | None, start: str, end: str) -> bool:
    if not created_at:
        return True
    try:
        stamp = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        lo = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
        hi = datetime.fromisoformat(end.replace("Z", "+00:00"))
        if hi.tzinfo is None:
            hi = hi.replace(tzinfo=timezone.utc)
        return lo <= stamp <= hi
    except ValueError:
        return True


def play_document(row: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any] | None:
    review_id = _clean(row.get("reviewId") or row.get("review_id") or "")
    body = _clean(row.get("content") or row.get("body") or "")
    if not review_id or len(body) < 8:
        return None
    title = _clean(row.get("title") or "") or body[:80]
    created = _iso(row.get("at") or row.get("created_at"))
    url = f"{PLAY_URL}&reviewId={review_id}"
    hits = keyword_hits(f"{title} {body}")
    return {
        "id": f"gp_{review_id}",
        "source": "play_store",
        "url": url,
        "captured_at": utc_now(),
        "created_at": created,
        "title": title,
        "body": body,
        "thread_context": f"Myntra Android app ({PLAY_APP_ID})",
        "language": meta.get("lang") or "en",
        "raw_metadata": {
            **meta,
            "kind": "store_review",
            "store": "play_store",
            "app_id": PLAY_APP_ID,
            "review_id": review_id,
            "rating": row.get("score") or row.get("rating"),
            "app_version": row.get("reviewCreatedVersion") or row.get("appVersion"),
            "thumbs_up": row.get("thumbsUpCount"),
            "keyword_hits": hits,
        },
    }


def app_store_document(row: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any] | None:
    review_id = _clean(row.get("id") or "")
    body = _clean(row.get("content") or row.get("body") or "")
    if not review_id or len(body) < 8:
        return None
    title = _clean(row.get("title") or "") or body[:80]
    created = _iso(row.get("updated") or row.get("created_at"))
    url = f"{APP_STORE_URL}?see-all=reviews"
    hits = keyword_hits(f"{title} {body}")
    return {
        "id": f"as_{review_id}",
        "source": "app_store",
        "url": url,
        "captured_at": utc_now(),
        "created_at": created,
        "title": title,
        "body": body,
        "thread_context": APP_STORE_NAME,
        "language": meta.get("lang") or "en",
        "raw_metadata": {
            **meta,
            "kind": "store_review",
            "store": "app_store",
            "app_id": meta.get("app_id"),
            "review_id": review_id,
            "rating": row.get("rating"),
            "app_version": row.get("version"),
            "author": row.get("author"),
            "keyword_hits": hits,
        },
    }
