"""Optional YouTube comment pull (public comments only).

Needs a YouTube Data API v3 key in YOUTUBE_API_KEY. Without one this returns
nothing and the caller records a declared limitation rather than failing: the
implementation plan treats extra sources as optional, never as a goal.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable

from config import (
    YOUTUBE_API_KEY_ENV,
    YOUTUBE_MAX_COMMENTS,
    YOUTUBE_MAX_VIDEOS,
    YOUTUBE_QUERIES,
)

API = "https://www.googleapis.com/youtube/v3"


class YouTubeUnavailable(RuntimeError):
    """No API key, or the API refused the request."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def api_key() -> str | None:
    key = (os.environ.get(YOUTUBE_API_KEY_ENV) or "").strip()
    return key or None


def _get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "MyntraDiscovery/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:200]
        raise YouTubeUnavailable(f"HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise YouTubeUnavailable(str(exc)) from exc


def _search_videos(key: str, query: str, limit: int) -> list[dict[str, Any]]:
    payload = _get(
        "search",
        {
            "key": key,
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(limit, 25),
            "relevanceLanguage": "en",
            "regionCode": "IN",
        },
    )
    return payload.get("items", [])


def _comments(key: str, video_id: str, limit: int) -> list[dict[str, Any]]:
    payload = _get(
        "commentThreads",
        {
            "key": key,
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(limit, 100),
            "order": "relevance",
            "textFormat": "plainText",
        },
    )
    return payload.get("items", [])


def _document(item: dict[str, Any], video: dict[str, Any], query: str) -> dict[str, Any] | None:
    snippet = (item.get("snippet") or {}).get("topLevelComment", {}).get("snippet", {})
    text = (snippet.get("textOriginal") or "").strip()
    comment_id = item.get("id")
    if not text or not comment_id:
        return None
    video_id = (video.get("id") or {}).get("videoId") or ""
    video_title = (video.get("snippet") or {}).get("title") or ""
    return {
        "id": f"yt_{comment_id}",
        "source": "youtube",
        "url": f"https://www.youtube.com/watch?v={video_id}&lc={comment_id}",
        "captured_at": utc_now(),
        "created_at": snippet.get("publishedAt"),
        "title": video_title,
        "body": text,
        "thread_context": video_title,
        "language": None,
        "raw_metadata": {
            "query": query,
            "search_scope": "phase5_youtube",
            "video_id": video_id,
            "like_count": snippet.get("likeCount"),
            "spec_version": "1.0.0",
        },
    }


def pull(*, log: Callable[[str], None] = print) -> tuple[list[dict[str, Any]], str | None]:
    """Returns (documents, skip_reason). skip_reason is None on a real pull."""
    key = api_key()
    if not key:
        reason = f"no {YOUTUBE_API_KEY_ENV} in environment"
        log(f"  youtube: skipped ({reason})")
        return [], reason

    documents: dict[str, dict[str, Any]] = {}
    try:
        for query in YOUTUBE_QUERIES:
            for video in _search_videos(key, query, YOUTUBE_MAX_VIDEOS):
                video_id = (video.get("id") or {}).get("videoId")
                if not video_id:
                    continue
                for item in _comments(key, video_id, YOUTUBE_MAX_COMMENTS):
                    doc = _document(item, video, query)
                    if doc:
                        documents.setdefault(doc["id"], doc)
            log(f"  youtube [{query}]: {len(documents)} comments so far")
    except YouTubeUnavailable as exc:
        reason = str(exc)
        log(f"  youtube: stopped ({reason})")
        return list(documents.values()), reason

    return list(documents.values()), None
