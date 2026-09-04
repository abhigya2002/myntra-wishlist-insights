"""Groq chat-completions client. Key from GROQ_API_KEY."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

from config import groq_api_key, groq_model, MODEL_FALLBACKS

CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "You label Reddit evidence for a Myntra discovery engine. "
    "Reply with a single JSON object only. No markdown. No extra text."
)


class GroqError(RuntimeError):
    """Groq HTTP or parse failure."""


class GroqQuotaError(GroqError):
    """Daily quota exhausted; do not keep retrying this run."""


class GroqClient:
    def __init__(self, *, sleep_s: float = 2.5, timeout_s: float = 60.0, max_retries: int = 4) -> None:
        self.api_key = groq_api_key()
        if not self.api_key:
            raise GroqError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your Groq key."
            )
        self.model = groq_model()
        self.sleep_s = sleep_s
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.request_count = 0
        self._model_ok = self.model

    def generate_json(self, prompt: str) -> dict[str, Any]:
        last_error: Exception | None = None
        models = [self._model_ok] + [m for m in MODEL_FALLBACKS if m != self._model_ok]
        tried_models: set[str] = set()
        for model in models:
            if model in tried_models:
                continue
            tried_models.add(model)
            try:
                payload = self._post(model, prompt)
                self._model_ok = model
                return _parse_json_payload(payload)
            except GroqError as exc:
                last_error = exc
                if "404" in str(exc) or "not_found" in str(exc).lower() or "does not exist" in str(exc).lower():
                    continue
                raise
        raise GroqError(f"Groq failed: {last_error}")

    def _post(self, model: str, prompt: str) -> dict[str, Any]:
        body = json.dumps(
            {
                "model": model,
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            }
        ).encode("utf-8")
        delay = self.sleep_s
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            if self.request_count:
                time.sleep(delay)
            request = urllib.request.Request(
                CHAT_URL,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "MyntraDiscoveryEngine/1.0",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                    raw = response.read().decode("utf-8", errors="replace")
                self.request_count += 1
                return json.loads(raw)
            except urllib.error.HTTPError as exc:
                err = exc.read().decode("utf-8", errors="replace")
                self.request_count += 1
                last_error = GroqError(f"HTTP {exc.code}: {err[:300]}")
                if exc.code == 429 and _is_daily_quota(err):
                    raise GroqQuotaError(err[:240]) from exc
                if exc.code in {429, 500, 502, 503, 504} and attempt < self.max_retries:
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    if retry_after:
                        try:
                            delay = min(float(retry_after), 30.0)
                        except ValueError:
                            delay = min(max(self.sleep_s, 2.0) * attempt, 30.0)
                    else:
                        delay = min(max(self.sleep_s, 2.0) * attempt, 30.0)
                    continue
                raise last_error from exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = GroqError(str(exc))
                if attempt < self.max_retries:
                    delay = min(max(self.sleep_s, 2.0) * attempt, 20.0)
                    continue
                raise last_error from exc
        raise GroqError(str(last_error))


def _is_daily_quota(err: str) -> bool:
    lower = err.lower()
    return any(
        token in lower
        for token in (
            "per day",
            "tokens per day",
            "requests per day",
            "tpd",
            "rpd",
            "daily",
        )
    )


def _parse_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        text = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GroqError(f"Unexpected Groq payload: {str(payload)[:300]}") from exc
    if not isinstance(text, str):
        raise GroqError(f"Groq content was not text: {str(payload)[:300]}")
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise GroqError(f"Groq did not return JSON: {cleaned[:300]}") from exc
    if not isinstance(parsed, dict):
        raise GroqError("Groq JSON root must be an object")
    return parsed
