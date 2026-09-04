"""App Store customer reviews via the public iTunes RSS feed. No API key."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from config import APP_STORE_ID

RSS_URL = (
    "https://itunes.apple.com/{country}/rss/customerreviews/page={page}"
    "/id={app_id}/sortBy=mostRecent/json"
)
USER_AGENT = "MyntraDiscoveryEngine/1.0 (Phase4 store ingest)"


class AppStoreError(RuntimeError):
    """iTunes RSS failure."""


def _get(url: str, timeout_s: float = 30.0) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        raise AppStoreError(f"HTTP {exc.code}: {err[:240]}") from exc
    except urllib.error.URLError as exc:
        raise AppStoreError(str(exc)) from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AppStoreError("iTunes RSS was not JSON") from exc


def _label(entry: dict[str, Any], key: str) -> str:
    node = entry.get(key)
    if isinstance(node, dict):
        return str(node.get("label") or "")
    return str(node or "")


def _parse_entry(entry: dict[str, Any]) -> dict[str, Any] | None:
    if "im:rating" not in entry:
        return None
    ident = entry.get("id")
    review_id = ""
    if isinstance(ident, dict):
        review_id = str(ident.get("label") or "")
        attrs = ident.get("attributes") or {}
        if isinstance(attrs, dict) and attrs.get("im:id"):
            review_id = str(attrs["im:id"])
    content = entry.get("content")
    body = ""
    if isinstance(content, dict):
        body = str(content.get("label") or "")
    elif isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("attributes", {}).get("type") == "text":
                body = str(item.get("label") or "")
                break
    author = entry.get("author") or {}
    name = author.get("name") if isinstance(author, dict) else None
    return {
        "id": review_id,
        "title": _label(entry, "title"),
        "content": body,
        "updated": _label(entry, "updated"),
        "rating": _label(entry, "im:rating"),
        "version": _label(entry, "im:version"),
        "author": _label(name, "label") if isinstance(name, dict) else str(name or ""),
    }


def fetch_reviews(
    *,
    app_id: str = APP_STORE_ID,
    country: str = "in",
    pages: int = 10,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for page in range(1, max(pages, 1) + 1):
        url = RSS_URL.format(country=country, page=page, app_id=app_id)
        payload = _get(url)
        feed = payload.get("feed") or {}
        entries = feed.get("entry") or []
        if isinstance(entries, dict):
            entries = [entries]
        page_hits = 0
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            parsed = _parse_entry(entry)
            if not parsed or not parsed["id"] or parsed["id"] in seen:
                continue
            seen.add(parsed["id"])
            rows.append(parsed)
            page_hits += 1
        if page_hits == 0:
            break
    return rows
