# Phase 0 — Corpus design

**Done when:** a source spec exists (queries, subreddits, window, exclusions) so Phase 1 ingest is repeatable.

No model. No scraping. This folder is the contract Phase 1 loads.

| File | Role |
|---|---|
| [SOURCE_SPEC.md](SOURCE_SPEC.md) | One-page human spec |
| [source_spec.json](source_spec.json) | Canonical machine spec |
| [spec.py](spec.py) | Load, validate, print pull jobs |

```text
python spec.py validate
python spec.py summary
python spec.py jobs --slice first
python spec.py jobs --slice full
python spec.py queries --question 8
```

Phase 1 must read `source_spec.json` (via `spec.load_spec()`) rather than hard-coding queries. If the corpus design changes, change the JSON here and re-validate.
