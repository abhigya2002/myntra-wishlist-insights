"""Grounded Groq chat with citations and solution/KPI guardrails."""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Any

import config
from retrieve import retrieve

CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are a grounded research assistant for Myntra product leadership.
You answer ONLY from the retrieved evidence chunks provided in the user message.

Hard rules:
1. Ground every factual claim in the evidence. Cite claim_id and/or URL when present.
2. If evidence is thin or missing, say clearly that evidence is insufficient — do not invent.
3. Never invent Myntra conversion rates, add-to-wishlist volumes, or internal KPI numbers.
4. Refuse solution pitches: no MVP ideas, coupons, discounts-as-fix, feature roadmaps, or
   claims that raising/removing the wishlist cap/ceiling would increase sales.
5. You may describe public-signal blockers between add and buy. Metric definition (do not fabricate numbers):
   numerator = buyers from wishlist; denominator = users who add.
6. Prefer claim-layer and derived facts over raw reviews when they conflict.
7. Keep answers concise (about 8–14 sentences unless the question needs a short list).
8. End with a short "Sources:" list of claim_ids / URLs you used.
"""

REFUSAL_PATTERNS = (
    r"\bmvp\b",
    r"\bcoupon",
    r"\bdiscount code",
    r"raise(ing)? (the )?wishlist (cap|ceiling|limit)",
    r"remov(e|ing) (the )?wishlist (cap|ceiling|limit)",
    r"wishlist (cap|ceiling|limit).{0,40}(sales|conversion|revenue)",
    r"(sales|conversion|revenue).{0,40}wishlist (cap|ceiling|limit)",
)


class ChatError(RuntimeError):
    """Chat or Groq failure."""


class GroqQuotaError(ChatError):
    """Daily quota exhausted."""


def _is_refusal_query(question: str) -> str | None:
    lower = question.lower()
    for pat in REFUSAL_PATTERNS:
        if re.search(pat, lower):
            return (
                "I can't help with solution pitches (MVP ideas, coupons, or claims that "
                "raising the wishlist cap would lift sales). I can summarize public evidence "
                "on wishlist behaviour and conversion blockers instead — ask about those."
            )
    return None


def _format_context(chunks: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for i, c in enumerate(chunks, 1):
        parts = [
            f"[{i}] id={c.get('id')}",
            f"layer={c.get('layer')}",
            f"source={c.get('source')}",
        ]
        if c.get("claim_id"):
            parts.append(f"claim_id={c['claim_id']}")
        if c.get("url"):
            parts.append(f"url={c['url']}")
        if c.get("opportunity_id"):
            parts.append(f"opportunity_id={c['opportunity_id']}")
        if c.get("wishlist_facet"):
            parts.append(f"wishlist_facet={c['wishlist_facet']}")
        header = " | ".join(parts)
        blocks.append(f"{header}\n{c.get('text') or ''}")
    return "\n\n".join(blocks)


def _post_groq(messages: list[dict[str, str]], *, temperature: float = 0.2) -> str:
    api_key = config.groq_api_key()
    if not api_key:
        raise ChatError(
            "GROQ_API_KEY is not set. Add it to Phases/Phase2_RelevanceAndExtraction/.env"
        )
    models = [config.groq_model()] + [
        m for m in config.MODEL_FALLBACKS if m != config.groq_model()
    ]
    last_error: Exception | None = None
    for model in models:
        body = json.dumps(
            {
                "model": model,
                "temperature": temperature,
                "messages": messages,
            }
        ).encode("utf-8")
        delay = 1.5
        for attempt in range(1, 4):
            request = urllib.request.Request(
                CHAT_URL,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "User-Agent": "WishlistInsights/1.0",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=90.0) as response:
                    raw = response.read().decode("utf-8", errors="replace")
                payload = json.loads(raw)
                return str(payload["choices"][0]["message"]["content"])
            except urllib.error.HTTPError as exc:
                err = exc.read().decode("utf-8", errors="replace")
                last_error = ChatError(f"HTTP {exc.code}: {err[:300]}")
                if exc.code == 429 and any(
                    t in err.lower() for t in ("per day", "tpd", "rpd", "daily")
                ):
                    raise GroqQuotaError(err[:240]) from exc
                if exc.code == 404 or "does not exist" in err.lower():
                    break  # try next model
                if exc.code in {429, 500, 502, 503, 504} and attempt < 3:
                    time.sleep(min(delay * attempt, 20.0))
                    continue
                raise last_error from exc
            except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
                last_error = ChatError(str(exc))
                if attempt < 3:
                    time.sleep(min(delay * attempt, 15.0))
                    continue
                raise last_error from exc
    raise ChatError(f"Groq failed: {last_error}")


def answer(
    question: str,
    *,
    history: list[dict[str, str]] | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    """Retrieve + generate. Returns answer, sources, refusal flag."""
    refusal = _is_refusal_query(question)
    if refusal:
        return {
            "answer": refusal,
            "sources": [],
            "refused": True,
            "insufficient": False,
        }

    chunks = retrieve(question, top_k=top_k)
    if not chunks:
        return {
            "answer": (
                "Evidence is insufficient for this question — no matching chunks in the "
                "Part 1 corpus index. Try rephrasing around wishlist behaviour, fit, "
                "returns, reviews, or price hesitation."
            ),
            "sources": [],
            "refused": False,
            "insufficient": True,
        }

    context = _format_context(chunks)
    user_block = (
        f"Question:\n{question}\n\n"
        f"Retrieved evidence (use only this):\n{context}\n\n"
        "Answer grounded in the evidence. Cite claim_id and URL where available. "
        "If the evidence does not support an answer, say so."
    )
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for turn in history[-6:]:
            role = turn.get("role")
            content = turn.get("content")
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_block})

    try:
        text = _post_groq(messages)
    except ChatError as exc:
        # Deterministic fallback: stitch top claim quotes
        lines = [
            "Groq unavailable — showing top retrieved evidence only:",
            str(exc),
            "",
        ]
        for c in chunks[:5]:
            cid = c.get("claim_id") or c.get("id")
            url = c.get("url") or "(no url)"
            preview = (c.get("text") or "")[:280]
            lines.append(f"- {cid}: {preview}")
            lines.append(f"  {url}")
        return {
            "answer": "\n".join(lines),
            "sources": chunks,
            "refused": False,
            "insufficient": False,
            "error": str(exc),
        }

    insufficient = bool(
        re.search(
            r"evidence is insufficient|insufficient evidence|not enough evidence|"
            r"cannot (answer|determine|confirm)|no (supporting )?evidence",
            text,
            re.I,
        )
    )
    return {
        "answer": text.strip(),
        "sources": chunks,
        "refused": False,
        "insufficient": insufficient,
    }


def main() -> None:
    q = "Why do people add to the Myntra wishlist — intent or bookmark?"
    result = answer(q)
    print(result["answer"])
    print("\n--- sources ---")
    for s in result["sources"][:5]:
        print(s.get("id"), s.get("claim_id"), s.get("url", "")[:80])


if __name__ == "__main__":
    main()
