"""Build the 15-document gate sample required by evals.md."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from schema import GATE_LABELS, document_text


def pick_gate_sample(labeled: list[dict[str, Any]], n: int = 15, seed: int = 2) -> list[dict[str, Any]]:
    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in labeled:
        by_label[row.get("label") or "noise"].append(row)
    rng = random.Random(seed)
    sample: list[dict[str, Any]] = []
    remaining = list(GATE_LABELS)
    rng.shuffle(remaining)
    # round-robin so we are not all myntra_primary
    while len(sample) < n and any(by_label[label] for label in GATE_LABELS):
        progressed = False
        for label in remaining:
            bucket = by_label[label]
            if not bucket:
                continue
            rng.shuffle(bucket)
            sample.append(bucket.pop())
            progressed = True
            if len(sample) >= n:
                break
        if not progressed:
            break
    if len(sample) < n:
        leftover = [row for row in labeled if row["id"] not in {s["id"] for s in sample}]
        rng.shuffle(leftover)
        sample.extend(leftover[: n - len(sample)])
    return sample[:n]


def sample_rows_for_docs(
    sample_labeled: list[dict[str, Any]],
    docs_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for item in sample_labeled:
        doc = docs_by_id.get(item["id"], {})
        text = document_text(doc) if doc else f"{item.get('title') or ''}"
        rows.append(
            {
                "doc_id": item["id"],
                "url": item.get("url") or "",
                "subreddit": item.get("subreddit"),
                "kind": item.get("kind"),
                "system_label": item.get("label"),
                "heuristic_label": item.get("heuristic_label"),
                "extractor": item.get("extractor"),
                "gate_rationale": item.get("gate_rationale"),
                "excerpt": text[:600],
                "human_label": "",
                "agree": None,
                "notes": "",
            }
        )
    return rows


def write_eval_notes(
    path: Path,
    sample: list[dict[str, Any]],
    *,
    checked: bool,
    accuracy: float | None,
    checker: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# Gate sample check",
        "",
        "Required by [evals.md](../../../DOCS/evals.md) §8: ≥ 15 relevance-gate labels human-checked, accuracy recorded.",
        "",
        f"- Date: {now}",
        f"- Sample size: {len(sample)}",
        f"- Checker: {checker}",
        f"- Status: {'checked' if checked else 'awaiting human labels'}",
    ]
    if accuracy is not None:
        lines.append(f"- Accuracy (human == system): {accuracy:.0%} ({sum(1 for r in sample if r.get('agree'))}/{len(sample)})")
    lines += [
        "",
        "| # | doc_id | system | human | agree | notes |",
        "|---|---|---|---|---|---|",
    ]
    for index, row in enumerate(sample, start=1):
        agree = row.get("agree")
        agree_cell = "" if agree is None else ("yes" if agree else "no")
        notes = (row.get("notes") or "").replace("|", "/")
        lines.append(
            f"| {index} | `{row['doc_id']}` | {row.get('system_label')} | {row.get('human_label') or ''} | {agree_cell} | {notes} |"
        )
    lines += [
        "",
        "## Excerpts",
        "",
    ]
    for index, row in enumerate(sample, start=1):
        lines.append(f"### {index}. `{row['doc_id']}` — system `{row.get('system_label')}`")
        lines.append(f"URL: {row.get('url')}")
        lines.append("")
        lines.append("```")
        lines.append((row.get("excerpt") or "")[:500])
        lines.append("```")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
