"""Apply human labels to the 15-doc gate sample and record accuracy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from config import EVAL_NOTES_PATH, SAMPLE_PATH
from sample import write_eval_notes
from schema import GATE_LABELS


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Write human gate labels into the 15-doc sample")
    parser.add_argument(
        "--labels",
        required=True,
        help="comma-separated 15 labels in sample order (myntra_primary,fashion_context,...)",
    )
    parser.add_argument("--checker", default="implementer")
    args = parser.parse_args()
    labels = [part.strip() for part in args.labels.split(",") if part.strip()]
    sample = load_jsonl(SAMPLE_PATH)
    if len(labels) != len(sample):
        raise SystemExit(f"need {len(sample)} labels, got {len(labels)}")
    for label in labels:
        if label not in GATE_LABELS:
            raise SystemExit(f"invalid label: {label}")
    agrees = 0
    for row, human in zip(sample, labels):
        row["human_label"] = human
        row["agree"] = human == row.get("system_label")
        if row["agree"]:
            agrees += 1
            row["notes"] = row.get("notes") or "human agrees with system"
        else:
            row["notes"] = row.get("notes") or "human override"
    write_jsonl(SAMPLE_PATH, sample)
    write_eval_notes(
        EVAL_NOTES_PATH,
        sample,
        checked=True,
        accuracy=agrees / len(sample) if sample else 0.0,
        checker=args.checker,
    )
    print(f"Checked {len(sample)}  accuracy={agrees}/{len(sample)}")
    print(f"Wrote {EVAL_NOTES_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
