"""Arctic Shift client tuned for Phase 5's keyword sweep.

The Phase 1 client treats any 422 as "keyword search unsupported" and retries
with the query dropped. Arctic Shift actually returns 422 for `Timeout. Maybe
slow down a bit`, so that path silently converts a keyword search into an
unfiltered recent-posts fetch — which is why Phase 1 surfaced one wishlist
document. Here 422 is a backoff, and keyword search is never dropped.

Verified parameter contract:
  posts/search    query=<terms>   requires subreddit or author
  comments/search body=<terms>    requires subreddit, author, link_id or parent_id
"""

from __future__ import annotations

import http.client
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

BASE = "https://arctic-shift.photon-reddit.com/api"
USER_AGENT = "Mozilla/5.0 (compatible; MyntraDiscovery/1.0; research)"
PAGE_LIMIT = 100
RETRY_CODES = {422, 429, 500, 502, 503, 504}


class ArchiveError(RuntimeError):
    """Arctic Shift refused the request for a non-retryable reason."""


def iso(stamp: int | float) -> str:
    return datetime.fromtimestamp(int(float(stamp)), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


class ArchiveClient:
    name = "arctic_shift"

    def __init__(self, *, sleep_s: float = 1.8, timeout_s: float = 45.0, max_retries: int = 3) -> None:
        self.sleep_s = sleep_s
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.requests = 0
        self.timeouts = 0

    def search(
        self,
        kind: str,
        *,
        subreddit: str,
        query: str,
        after: int,
        before: int,
        limit: int = PAGE_LIMIT,
    ) -> list[dict[str, Any]]:
        if kind == "submission":
            path, key = "posts/search", "query"
        else:
            path, key = "comments/search", "body"
        params = {
            "subreddit": subreddit,
            key: query,
            "after": iso(after),
            "before": iso(before),
            "limit": min(limit, PAGE_LIMIT),
            "sort": "desc",
        }
        url = f"{BASE}/{path}?{urllib.parse.urlencode(params)}"
        payload = self._get(url)
        data = payload.get("data")
        return data if isinstance(data, list) else []

    def _get(self, url: str) -> dict[str, Any]:
        delay = self.sleep_s
        for attempt in range(1, self.max_retries + 1):
            if self.requests:
                time.sleep(delay)
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                    body = response.read().decode("utf-8", errors="replace")
                self.requests += 1
                payload = json.loads(body)
                if isinstance(payload, dict) and payload.get("error"):
                    raise ArchiveError(str(payload["error"]))
                return payload if isinstance(payload, dict) else {"data": payload}
            except urllib.error.HTTPError as exc:
                self.requests += 1
                detail = exc.read().decode("utf-8", errors="replace")[:160]
                if exc.code in RETRY_CODES and attempt < self.max_retries:
                    if exc.code == 422:
                        self.timeouts += 1
                    delay = min(delay * 1.8, 15.0)
                    continue
                raise ArchiveError(f"HTTP {exc.code} for {url}: {detail}") from exc
            except (
                urllib.error.URLError,
                http.client.HTTPException,
                ConnectionError,
                TimeoutError,
                json.JSONDecodeError,
            ) as exc:
                # Arctic Shift drops the connection outright under load, which
                # surfaces as RemoteDisconnected rather than a URLError.
                if attempt < self.max_retries:
                    delay = min(delay * 1.8, 15.0)
                    continue
                raise ArchiveError(f"failed GET {url}: {exc}") from exc
        raise ArchiveError(f"retries exhausted for {url}")
