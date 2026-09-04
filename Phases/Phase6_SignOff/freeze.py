"""Freeze Phase 5 discovery report + evidence ledger as the Part 1 handoff."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import (
    FROZEN_LEDGER,
    FROZEN_META,
    FROZEN_REPORT,
    PART2_HANDOFF,
    SOURCE_LEDGER,
    SOURCE_MANIFEST,
    SOURCE_REPORT,
    SOURCE_WISHLIST,
)
from io_util import copy_file, read_json, write_json, write_text


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def freeze() -> dict[str, Any]:
    if not SOURCE_REPORT.is_file():
        raise SystemExit(f"missing Phase 5 report: {SOURCE_REPORT}")
    if not SOURCE_LEDGER.is_file():
        raise SystemExit(f"missing Phase 5 ledger: {SOURCE_LEDGER}")

    copy_file(SOURCE_REPORT, FROZEN_REPORT)
    copy_file(SOURCE_LEDGER, FROZEN_LEDGER)

    meta = {
        "frozen_at": utc_now(),
        "source_phase": 5,
        "source_report": str(SOURCE_REPORT),
        "source_ledger": str(SOURCE_LEDGER),
        "source_manifest": str(SOURCE_MANIFEST),
        "frozen_report": str(FROZEN_REPORT),
        "frozen_ledger": str(FROZEN_LEDGER),
        "report_sha256": sha256(FROZEN_REPORT),
        "ledger_sha256": sha256(FROZEN_LEDGER),
        "bytes": {
            "report": FROZEN_REPORT.stat().st_size,
            "ledger": FROZEN_LEDGER.stat().st_size,
        },
    }
    write_json(FROZEN_META, meta)

    manifest = read_json(SOURCE_MANIFEST)
    wishlist = read_json(SOURCE_WISHLIST) or manifest.get("wishlist_evidence") or {}
    coverage = manifest.get("question_coverage") or {}
    ranking = manifest.get("ranking") or []

    handoff = "\n".join(
        [
            "# Part 2 handoff — frozen Part 1 discovery package",
            "",
            "This package is the only Part 1 input for Parts 2–4. Do not re-rank from memory;",
            "use the frozen report and ledger.",
            "",
            "## Paths",
            "",
            f"- Discovery report: `{FROZEN_REPORT}`",
            f"- Evidence ledger: `{FROZEN_LEDGER}`",
            f"- Freeze metadata: `{FROZEN_META}`",
            "",
            "## Fingerprints",
            "",
            f"- report sha256: `{meta['report_sha256']}`",
            f"- ledger sha256: `{meta['ledger_sha256']}`",
            f"- frozen_at: {meta['frozen_at']}",
            "",
            "## Snapshot",
            "",
            f"- Ranked areas: {manifest.get('ranked_areas')}",
            f"- Question coverage: {coverage.get('answered_or_partial')}/10 "
            f"(Answered {coverage.get('answered')}, Partial {coverage.get('partial')}, "
            f"Gap {coverage.get('gap')})",
            f"- Wishlist evidence: {wishlist.get('claims')} claims / {wishlist.get('threads')} threads "
            f"— {wishlist.get('reading')}",
            "",
            "## Top ranked opportunity area ids",
            "",
        ]
    )
    for row in ranking[:10]:
        handoff += f"- #{row.get('rank')}: `{row.get('id')}` (score {row.get('score')})\n"
    handoff += "\n".join(
        [
            "",
            "## Explicit non-goals for Part 2 readers",
            "",
            "- Do not treat Partial Q1/Q8 as fully Answered.",
            "- Do not invent a Myntra internal conversion rate from this ledger.",
            "- Do not start an MVP / interview plan from a single store-only theme.",
            "",
        ]
    )
    write_text(PART2_HANDOFF, handoff)
    return meta
