# Phase 4 — Play Store / App Store corroboration

**Done when:** the discovery report shows Reddit as primary and store reviews as volume/corroboration, with counts.

Adds the priority-2 adapter from [architecture.md](../../DOCS/architecture.md). Store reviews **corroborate or challenge** Reddit themes (returns, size charts, quality, trust, app friction). They do not replace Reddit.

Seeds from [source_spec.json](../Phase0_CorpusDesign/source_spec.json):

- Play Store: `com.myntra.android`
- App Store: `907394059` (Myntra Fashion Shopping App)
- Keywords: wishlist, size, fit, return, quality, sale, size chart

---

## Run

```text
pip install -r requirements.txt
python run.py --dry-run
python run.py
python run.py --no-ingest
python ingest.py --dry-run
```

`--force` re-pulls store reviews. `--skip-play` / `--skip-app` if one store is blocked.

Inputs:

```text
../Phase1_RedditIngest/data/raw/reddit_documents.jsonl
../Phase2_RelevanceAndExtraction/data/claims/reddit_claims.jsonl
../Phase2_RelevanceAndExtraction/data/labeled/reddit_labeled.jsonl
```

Outputs:

```text
data/raw/store_reviews.jsonl
data/claims/store_claims.jsonl
data/claims/combined_claims.jsonl
output/discovery-report.md
output/evidence-ledger.json
data/derived/corroboration.json
data/eval/INSTANT_FAIL.md
```

App Store uses the public iTunes RSS feed (no key). Play Store uses `google-play-scraper`, with a urllib fallback.

---

## Files

| File | Role |
|---|---|
| `run.py` | Full pipeline |
| `ingest.py` | Pull Play + App Store |
| `play_store.py` | Android reviews |
| `app_store.py` | iOS RSS reviews |
| `normalize.py` | Store row → architecture raw document |
| `extract.py` | Gate (Myntra app = `myntra_primary`) + keyword claims |
| `cluster_ext.py` | Phase 3 areas + `app_friction` |
| `quantify.py` | Reddit vs store counts |
| `corroborate.py` | Per-area verdict |
| `rank_ext.py` | Reddit-weighted rubric |
| `questions_ext.py` | Q1–10 on the combined set |
| `report.py` | Mixed-source draft |
| `evals_run.py` | Instant-fail + groundedness |
