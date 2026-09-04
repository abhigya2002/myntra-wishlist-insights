"""Arctic Shift Reddit archive client.

Pullpush is the ReviewLens primary API, but it currently refuses automated
agents. Arctic Shift is the same job (public historical posts/comments) with
subreddit-scoped search — `query` cannot be used site-wide.
Docs: https://arctic-shift.photon-reddit.com/search
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

BASE = "https://arctic-shift.photon-reddit.com/api"
DEFAULT_UA = "Mozilla/5.0 (compatible; MyntraDiscovery/1.0; research)"
PAGE_SIZE = 100


class ArcticShiftError(RuntimeError):
    """HTTP or parse failure talking to Arctic Shift."""


def _iso(value: int | float | str) -> str:
    if isinstance(value, str) and not value.isdigit():
        return value
    stamp = int(float(value))
    return datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


class ArcticShiftClient:
    name = "arctic_shift"
    supports_site_wide = False

    def __init__(
        self,
        *,
        user_agent: str = DEFAULT_UA,
        sleep_s: float = 1.2,
        timeout_s: float = 45.0,
        max_retries: int = 4,
    ) -> None:
        self.user_agent = user_agent
        self.sleep_s = sleep_s
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.request_count = 0

    def search_submissions(self, **params: Any) -> list[dict[str, Any]]:
        mapped = self._map_params("posts", params)
        return self._search("posts/search", mapped)

    def search_comments(self, **params: Any) -> list[dict[str, Any]]:
        mapped = self._map_params("comments", params)
        return self._search("comments/search", mapped)

    def search_paginated(
        self,
        kind: str,
        *,
        after: int,
        before: int,
        max_items: int,
        **params: Any,
    ) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        seen: set[str] = set()
        cursor_before: int | str = before
        search = self.search_submissions if kind == "submission" else self.search_comments
        params = dict(params)
        keyword_disabled = False

        while len(collected) < max_items:
            remaining = max_items - len(collected)
            try:
                batch = search(
                    limit=min(PAGE_SIZE, remaining),
                    after=_iso(after),
                    before=_iso(cursor_before),
                    sort="desc",
                    **params,
                )
            except ArcticShiftError as exc:
                message = str(exc)
                if (
                    kind == "submission"
                    and params.get("q")
                    and not keyword_disabled
                    and ("422" in message or "400" in message)
                ):
                    print("  arctic-shift: keyword search unsupported, fetching then Myntra-filtering", flush=True)
                    params.pop("q", None)
                    keyword_disabled = True
                    continue
                if "422" in message or "400" in message:
                    break
                raise
            if not batch:
                break

            new_rows = []
            for row in batch:
                row_id = str(row.get("id") or "")
                if not row_id or row_id in seen:
                    continue
                seen.add(row_id)
                created = int(float(row.get("created_utc") or 0))
                if created and created < int(after):
                    continue
                new_rows.append(row)
            if not new_rows:
                break
            collected.extend(new_rows)
            oldest = min(int(float(row.get("created_utc") or 0)) for row in batch)
            if oldest <= int(after) or oldest >= int(float(cursor_before)):
                break
            cursor_before = oldest
        return collected[:max_items]

    @staticmethod
    def _map_params(kind: str, params: dict[str, Any]) -> dict[str, Any]:
        mapped: dict[str, Any] = {}
        for key, value in params.items():
            if value is None or value == "":
                continue
            if key == "q":
                mapped["query" if kind == "posts" else "body"] = value
            elif key == "size":
                mapped["limit"] = value
            elif key in {"after", "before"}:
                mapped[key] = _iso(value) if not isinstance(value, str) else value
            elif key == "sort_type":
                continue
            else:
                mapped[key] = value
        return mapped

    def _search(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        query = {key: value for key, value in params.items() if value is not None and value != ""}
        if "limit" in query:
            query["limit"] = min(int(query["limit"]), PAGE_SIZE)
        url = f"{BASE}/{path}?{urllib.parse.urlencode(query, doseq=True)}"
        payload = self._get_json(url)
        data = payload.get("data", [])
        if isinstance(data, list):
            return data
        return []

    def _get_json(self, url: str) -> dict[str, Any]:
        delay = self.sleep_s
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            if attempt > 1 or self.request_count:
                time.sleep(delay)
            request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                    body = response.read().decode("utf-8", errors="replace")
                self.request_count += 1
                payload = json.loads(body)
                if isinstance(payload, dict) and payload.get("error"):
                    raise ArcticShiftError(str(payload["error"]))
                return payload if isinstance(payload, dict) else {"data": payload}
            except urllib.error.HTTPError as exc:
                last_error = exc
                err_body = exc.read().decode("utf-8", errors="replace")
                self.request_count += 1
                if exc.code in {429, 500, 502, 503, 504} and attempt < self.max_retries:
                    delay = min(max(self.sleep_s, 4.0) * attempt, 30.0)
                    print(f"  arctic-shift HTTP {exc.code}, retry in {delay:.1f}s", flush=True)
                    continue
                raise ArcticShiftError(f"HTTP {exc.code} for {url}: {err_body[:200]}") from exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < self.max_retries:
                    delay = min(max(self.sleep_s, 4.0) * attempt, 30.0)
                    continue
                raise ArcticShiftError(f"Failed GET {url}: {exc}") from exc
        raise ArcticShiftError(f"Failed GET {url}: {last_error}")
