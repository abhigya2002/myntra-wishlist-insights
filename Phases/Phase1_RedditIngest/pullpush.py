"""Pullpush Reddit archive client. No Reddit API key.

Docs: https://api.pullpush.io/reddit/search/{submission|comment}/
See DOCS/reviewfetchingdocument.txt (ReviewLens Reddit pass).
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE = "https://api.pullpush.io/reddit/search"
DEFAULT_UA = "Mozilla/5.0 (compatible; MyntraDiscovery/1.0; research)"
PAGE_SIZE = 100


class PullpushError(RuntimeError):
    """HTTP or parse failure talking to Pullpush."""


class PullpushBlockedError(PullpushError):
    """Pullpush refused this client (agent / paid-scraping gate)."""


class PullpushClient:
    name = "pullpush"
    supports_site_wide = True
    def __init__(
        self,
        *,
        user_agent: str = DEFAULT_UA,
        sleep_s: float = 1.2,
        timeout_s: float = 30.0,
        max_retries: int = 5,
    ) -> None:
        self.user_agent = user_agent
        self.sleep_s = sleep_s
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.request_count = 0

    def search_submissions(self, **params: Any) -> list[dict[str, Any]]:
        return self._search("submission", params)

    def search_comments(self, **params: Any) -> list[dict[str, Any]]:
        return self._search("comment", params)

    def search_paginated(
        self,
        kind: str,
        *,
        after: int,
        before: int,
        max_items: int,
        **params: Any,
    ) -> list[dict[str, Any]]:
        """Walk newest → oldest using `before` as the cursor."""
        collected: list[dict[str, Any]] = []
        seen: set[str] = set()
        cursor_before = before
        search = self.search_submissions if kind == "submission" else self.search_comments

        while len(collected) < max_items:
            remaining = max_items - len(collected)
            batch = search(
                size=min(PAGE_SIZE, remaining),
                after=after,
                before=cursor_before,
                sort="desc",
                sort_type="created_utc",
                **params,
            )
            if not batch:
                break

            new_rows = []
            for row in batch:
                row_id = str(row.get("id") or "")
                if not row_id or row_id in seen:
                    continue
                seen.add(row_id)
                created = int(row.get("created_utc") or 0)
                if created and created < after:
                    continue
                new_rows.append(row)

            if not new_rows:
                break

            collected.extend(new_rows)
            oldest = min(int(row.get("created_utc") or 0) for row in batch)
            if oldest <= after or oldest >= cursor_before:
                break
            cursor_before = oldest

        return collected[:max_items]

    def _search(self, kind: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        query = {key: value for key, value in params.items() if value is not None and value != ""}
        query["size"] = min(int(query.get("size") or PAGE_SIZE), PAGE_SIZE)
        url = f"{BASE}/{kind}/?{urllib.parse.urlencode(query, doseq=True)}"
        payload = self._get_json(url)
        data = payload.get("data", [])
        if isinstance(data, list):
            return data
        return []

    def _get_json(self, url: str) -> dict[str, Any]:
        delay = max(self.sleep_s, 0.0)
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            if attempt > 1 or self.request_count:
                time.sleep(delay)
            request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                    body = response.read().decode("utf-8", errors="replace")
                self.request_count += 1
                return json.loads(body)
            except urllib.error.HTTPError as exc:
                last_error = exc
                err_body = exc.read().decode("utf-8", errors="replace")
                self.request_count += 1
                if exc.code == 429 and "does not provide free scraping resources for agents" in err_body:
                    raise PullpushBlockedError(err_body.strip()) from exc
                retry_after = _retry_after_seconds(exc)
                if exc.code in {429, 500, 502, 503, 504} and attempt < self.max_retries:
                    delay = max(retry_after or 0.0, min(max(self.sleep_s, 8.0) * attempt, 45.0))
                    print(f"  pullpush HTTP {exc.code}, retry in {delay:.1f}s (attempt {attempt})", flush=True)
                    continue
                raise PullpushError(f"HTTP {exc.code} for {url}: {err_body[:200]}") from exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < self.max_retries:
                    delay = min(max(self.sleep_s, 4.0) * attempt, 30.0)
                    continue
                raise PullpushError(f"Failed GET {url}: {exc}") from exc
        raise PullpushError(f"Failed GET {url}: {last_error}")


def _retry_after_seconds(exc: urllib.error.HTTPError) -> float | None:
    raw = exc.headers.get("Retry-After") if exc.headers else None
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None
