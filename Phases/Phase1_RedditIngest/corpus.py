"""JSONL corpus with URL / Reddit-id dedupe."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Corpus:
    def __init__(self) -> None:
        self._by_id: dict[str, dict[str, Any]] = {}
        self._by_url: dict[str, str] = {}
        self.dropped_duplicate = 0

    def add(self, document: dict[str, Any]) -> bool:
        doc_id = document["id"]
        url = document.get("url") or ""
        if doc_id in self._by_id:
            self._merge_metadata(self._by_id[doc_id], document)
            self.dropped_duplicate += 1
            return False
        if url and url in self._by_url:
            existing = self._by_id[self._by_url[url]]
            self._merge_metadata(existing, document)
            self.dropped_duplicate += 1
            return False
        self._by_id[doc_id] = document
        if url:
            self._by_url[url] = doc_id
        return True

    def documents(self) -> list[dict[str, Any]]:
        return list(self._by_id.values())

    def submissions(self) -> list[dict[str, Any]]:
        return [doc for doc in self._by_id.values() if doc.get("raw_metadata", {}).get("kind") == "submission"]

    def __len__(self) -> int:
        return len(self._by_id)

    def write_jsonl(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for document in self.documents():
                handle.write(json.dumps(document, ensure_ascii=False) + "\n")

    @classmethod
    def load_jsonl(cls, path: Path) -> "Corpus":
        corpus = cls()
        if not path.exists():
            return corpus
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    corpus.add(json.loads(line))
        return corpus

    @staticmethod
    def _merge_metadata(existing: dict[str, Any], incoming: dict[str, Any]) -> None:
        old_meta = existing.setdefault("raw_metadata", {})
        new_meta = incoming.get("raw_metadata") or {}
        for key in ("query_id", "query", "pull_job_id", "search_scope", "pass_name"):
            combined_key = f"{key}s" if not key.endswith("s") else key
            values = []
            for source in (old_meta, new_meta):
                if source.get(key):
                    values.append(source[key])
                extra = source.get(combined_key)
                if isinstance(extra, list):
                    values.extend(extra)
            # keep original scalar; store the union
            unique = []
            for value in values:
                if value not in unique:
                    unique.append(value)
            old_meta[combined_key] = unique
