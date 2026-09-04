"""BM25 retrieval over data/index.jsonl with claim/report/derived layer boost."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi

import config

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?", re.I)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


def load_chunks(path: Path | None = None) -> list[dict[str, Any]]:
    index_path = path or config.INDEX_PATH
    if not index_path.is_file():
        raise FileNotFoundError(
            f"Index missing at {index_path}. Run: python build_index.py"
        )
    chunks: list[dict[str, Any]] = []
    with index_path.open(encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    if not chunks:
        raise ValueError(f"Index empty: {index_path}")
    return chunks


@lru_cache(maxsize=1)
def _get_engine() -> tuple[BM25Okapi, tuple[dict[str, Any], ...]]:
    chunks = tuple(load_chunks())
    corpus_tokens = [tokenize(c.get("text") or "") for c in chunks]
    return BM25Okapi(corpus_tokens), chunks


def clear_cache() -> None:
    _get_engine.cache_clear()


def retrieve(
    query: str,
    *,
    top_k: int | None = None,
    layer_boost: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Return top-k chunks with BM25 score * layer boost."""
    k = top_k if top_k is not None else config.TOP_K
    boosts = layer_boost or config.LAYER_BOOST
    bm25, chunks = _get_engine()
    tokens = tokenize(query)
    if not tokens:
        return []
    scores = bm25.get_scores(tokens)
    ranked: list[tuple[float, int]] = []
    for i, raw in enumerate(scores):
        layer = str(chunks[i].get("layer") or "raw")
        boosted = float(raw) * float(boosts.get(layer, 1.0))
        if boosted > 0:
            ranked.append((boosted, i))
    ranked.sort(key=lambda x: x[0], reverse=True)
    results: list[dict[str, Any]] = []
    for score, i in ranked[:k]:
        row = dict(chunks[i])
        row["score"] = round(score, 4)
        results.append(row)
    return results


def smoke_queries() -> list[tuple[str, list[dict[str, Any]]]]:
    queries = [
        "wishlist intent vs bookmark archive inspiration",
        "fit size uncertainty after choosing item",
        "returns refund order integrity distrust delay",
        "sale wait price drop park wishlist",
        "wishlist cap ceiling saved item limit",
    ]
    return [(q, retrieve(q, top_k=5)) for q in queries]


def main() -> None:
    for query, hits in smoke_queries():
        print(f"\n=== {query}")
        for h in hits:
            preview = (h.get("text") or "")[:120].replace("\n", " ")
            print(
                f"  [{h.get('score'):.3f}] {h.get('layer')} "
                f"{h.get('id')} :: {preview}..."
            )


if __name__ == "__main__":
    main()
