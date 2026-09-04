"""Play Store reviews. Prefers google-play-scraper; urllib batchexecute fallback."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from config import PLAY_APP_ID

USER_AGENT = "MyntraDiscoveryEngine/1.0 (Phase4 store ingest)"
BATCH_URL = "https://play.google.com/_/PlayStoreUi/data/batchexecute?hl={lang}&gl={country}"
REVIEWS_RE = re.compile(r"(\[.*\])", re.S)


class PlayStoreError(RuntimeError):
    """Play Store fetch failure."""


def _via_package(app_id: str, count: int, lang: str, country: str) -> list[dict[str, Any]]:
    from google_play_scraper import Sort, reviews as gp_reviews

    rows: list[dict[str, Any]] = []
    token = None
    remaining = count
    while remaining > 0:
        batch = min(remaining, 200)
        result, token = gp_reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=batch,
            continuation_token=token,
        )
        if not result:
            break
        rows.extend(result)
        remaining = count - len(rows)
        if token is None:
            break
    return rows[:count]


def _build_body(
    app_id: str,
    count: int,
    token: str | None,
) -> bytes:
    inner = [None, None, [2, None, count, [token, None, None, None, None, None], None], [app_id, 7]]
    wrapper = [[["UsvDTd", json.dumps(inner, separators=(",", ":")), None, "generic"]]]
    return urllib.parse.urlencode({"f.req": json.dumps(wrapper, separators=(",", ":"))}).encode("utf-8")


def _parse_batch(raw: str) -> tuple[list[list[Any]], str | None]:
    cleaned = raw.lstrip(")]}'").strip()
    match = REVIEWS_RE.search(cleaned)
    if not match:
        raise PlayStoreError("Play Store response had no review payload")
    outer = json.loads(match.group(1))
    try:
        blob = json.loads(outer[0][2])
    except (IndexError, TypeError, json.JSONDecodeError) as exc:
        raise PlayStoreError("Play Store payload shape changed") from exc
    items = blob[0] if blob and blob[0] else []
    token = None
    try:
        token = blob[-2][-1]
        if isinstance(token, list):
            token = None
    except (IndexError, TypeError):
        token = None
    return items, token


def _row_from_item(item: list[Any]) -> dict[str, Any] | None:
    if not isinstance(item, list) or len(item) < 5:
        return None
    review_id = str(item[0] or "")
    body = str(item[4] or "")
    if not review_id or not body:
        return None
    score = item[2] if len(item) > 2 else None
    created = None
    if len(item) > 5 and isinstance(item[5], list) and item[5]:
        try:
            created = datetime.fromtimestamp(int(item[5][0]), tz=timezone.utc)
        except (TypeError, ValueError, OSError):
            created = None
    version = None
    if len(item) > 10 and isinstance(item[10], str):
        version = item[10]
    return {
        "reviewId": review_id,
        "content": body,
        "score": score,
        "at": created,
        "reviewCreatedVersion": version,
        "thumbsUpCount": item[6] if len(item) > 6 else None,
    }


def _via_http(app_id: str, count: int, lang: str, country: str) -> list[dict[str, Any]]:
    url = BATCH_URL.format(lang=lang, country=country)
    rows: list[dict[str, Any]] = []
    token: str | None = None
    remaining = count
    while remaining > 0:
        batch = min(remaining, 150)
        body = _build_body(app_id, batch, token)
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            err = exc.read().decode("utf-8", errors="replace")
            raise PlayStoreError(f"HTTP {exc.code}: {err[:240]}") from exc
        except urllib.error.URLError as exc:
            raise PlayStoreError(str(exc)) from exc
        items, token = _parse_batch(raw)
        if not items:
            break
        for item in items:
            parsed = _row_from_item(item) if isinstance(item, list) else None
            if parsed:
                rows.append(parsed)
        remaining = count - len(rows)
        if not token:
            break
    return rows[:count]


def fetch_reviews(
    *,
    app_id: str = PLAY_APP_ID,
    count: int = 200,
    lang: str = "en",
    country: str = "in",
) -> tuple[list[dict[str, Any]], str]:
    try:
        rows = _via_package(app_id, count, lang, country)
        return rows, "google_play_scraper"
    except ImportError:
        rows = _via_http(app_id, count, lang, country)
        return rows, "batchexecute"
    except Exception as exc:
        try:
            rows = _via_http(app_id, count, lang, country)
            return rows, "batchexecute"
        except PlayStoreError:
            raise PlayStoreError(f"Play Store fetch failed: {exc}") from exc
