# Phase 6 — Part 1 sign-off

Phase 6 is the final gate in [DOCS/implementationplan.md](../../DOCS/implementationplan.md)
and [DOCS/evals.md](../../DOCS/evals.md) §9. It does not ingest new sources. It:

1. Scores the Part 1 checklist against the **Phase 5** mixed-source draft
2. Freezes `discovery-report.md` + `evidence-ledger.json` for Parts 2–4
3. Rewrites [architecture.md](../../DOCS/architecture.md) and
   [implementationplan.md](../../DOCS/implementationplan.md) to describe the engine that ran

## Canonical draft

Sign-off freezes Phase 5 (Reddit primary + store corroboration + wishlist expansion),
not the earlier Reddit-only Phase 3 draft.

| Source | Path |
|---|---|
| Report | `../Phase5_OptionalExpansion/output/discovery-report.md` |
| Ledger | `../Phase5_OptionalExpansion/output/evidence-ledger.json` |
| Evals | `../Phase5_OptionalExpansion/data/eval/` |

## Run

```text
cd Phases/Phase6_SignOff
python run.py --dry-run
python run.py
```

`--skip-docs` checks and freezes without rewriting `DOCS/`.

## Outputs

| Path | Contents |
|---|---|
| `output/discovery-report.md` | Frozen copy of the Phase 5 report |
| `output/evidence-ledger.json` | Frozen evidence ledger |
| `output/freeze.json` | sha256 fingerprints + source paths |
| `output/PART2_HANDOFF.md` | Paths and caveats for Parts 2–4 |
| `data/eval/SIGN_OFF.md` | Checklist with PASS/FAIL |
| `data/eval/PROCESS_EVALS.md` | evals.md §8 process checks |
| `data/manifest.json` | Machine-readable sign-off result |

## Done when

Every item on the Part 1 sign-off checklist is PASS, process evals are PASS, and the
frozen package exists. Caveats (thin Q1/Q8, no internal conversion rate) are recorded
in `SIGN_OFF.md` and the handoff — they do not block sign-off when coverage and
instant-fail bars are met.
