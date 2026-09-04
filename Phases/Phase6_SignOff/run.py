"""Phase 6 CLI: checklist → freeze → update DOCS → write sign-off artifacts."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

PHASE6_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PHASE6_DIR))

from checklist import render_process_evals, render_sign_off, run_checklist  # noqa: E402
from config import (  # noqa: E402
    CHECKLIST_JSON,
    CHECKLIST_MD,
    FROZEN_LEDGER,
    FROZEN_META,
    FROZEN_REPORT,
    MANIFEST_PATH,
    PART2_HANDOFF,
    PROCESS_EVALS_MD,
    SOURCE_LEDGER,
    SOURCE_REPORT,
)
from docs_update import update_docs  # noqa: E402
from freeze import freeze  # noqa: E402
from io_util import write_json, write_text  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 6 Part 1 sign-off")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--skip-docs",
        action="store_true",
        help="do not rewrite DOCS/architecture.md and implementationplan.md",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.dry_run:
        print("Phase 6 dry-run")
        print(f"  source report:  {SOURCE_REPORT} exists={SOURCE_REPORT.is_file()}")
        print(f"  source ledger:  {SOURCE_LEDGER} exists={SOURCE_LEDGER.is_file()}")
        print(f"  freeze -> {FROZEN_REPORT}")
        print(f"  freeze -> {FROZEN_LEDGER}")
        print("  steps: checklist -> freeze Phase 5 artifacts -> update DOCS -> SIGN_OFF.md")
        return 0

    result = run_checklist()
    meta = freeze()
    docs_paths = {}
    if not args.skip_docs:
        docs_paths = update_docs(
            {
                "frozen_at": meta["frozen_at"],
                "coverage": result.get("coverage") or {},
                "wishlist": result.get("wishlist") or {},
            }
        )

    write_json(CHECKLIST_JSON, result)
    write_text(CHECKLIST_MD, render_sign_off(result, frozen_report=FROZEN_REPORT, frozen_ledger=FROZEN_LEDGER))
    write_text(PROCESS_EVALS_MD, render_process_evals(result))
    write_json(
        MANIFEST_PATH,
        {
            "phase": 6,
            "product": "Myntra",
            "ran_at": utc_now(),
            "sign_off_clear": result["sign_off_clear"],
            "source_draft": result["source_draft"],
            "frozen": meta,
            "coverage": result.get("coverage"),
            "ranked_areas": result.get("ranked_areas"),
            "wishlist": result.get("wishlist"),
            "caveats": result.get("caveats"),
            "docs_updated": docs_paths,
            "files": {
                "sign_off": str(CHECKLIST_MD),
                "process_evals": str(PROCESS_EVALS_MD),
                "report": str(FROZEN_REPORT),
                "ledger": str(FROZEN_LEDGER),
                "freeze": str(FROZEN_META),
                "handoff": str(PART2_HANDOFF),
            },
            "re_run": "python run.py",
        },
    )

    status = "SIGNED OFF" if result["sign_off_clear"] else "NOT CLEAR"
    failed = [item["name"] for item in result["checklist"] + result["process_evals"] if not item["pass"]]
    print(
        f"Done. sign_off={status} ranked={result.get('ranked_areas')} "
        f"coverage={result.get('coverage', {}).get('answered_or_partial')}/10 "
        f"wishlist_claims={result.get('wishlist', {}).get('claims')}",
        flush=True,
    )
    if failed:
        print("Failed checks: " + "; ".join(failed), flush=True)
    print(f"Wrote {CHECKLIST_MD}", flush=True)
    print(f"Froze  {FROZEN_REPORT}", flush=True)
    if docs_paths:
        print(f"Updated {docs_paths.get('architecture')}", flush=True)
        print(f"Updated {docs_paths.get('implementationplan')}", flush=True)
    return 0 if result["sign_off_clear"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
