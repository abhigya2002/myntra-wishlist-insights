# Phase 3 — First ranked draft (Reddit-only)

**Done when:** a Reddit-only draft exists that would pass [evals.md](../../DOCS/evals.md) except possibly source-mix gaps (those must be named).

Cluster Phase 2 claims → quantify → rank with the rubric in evals.md. Write `output/discovery-report.md` that:

1. Attempts all ten discovery questions (Gap is allowed; silence is not)
2. Lists ≥ 5 opportunity areas with quantification and comparison
3. Distinguishes wishlist as intent vs bookmark if the corpus allows it
4. Does not pitch a product or a discount

Play/App Store is **not** ingested here. That Gap is named in the report.

---

## Run

```text
python run.py --dry-run
python run.py
```

Inputs (already on disk from earlier phases):

```text
../Phase1_RedditIngest/data/raw/reddit_documents.jsonl
../Phase2_RelevanceAndExtraction/data/labeled/reddit_labeled.jsonl
../Phase2_RelevanceAndExtraction/data/claims/reddit_claims.jsonl
```

Outputs:

```text
output/discovery-report.md
output/evidence-ledger.json
data/derived/clusters.jsonl
data/derived/quantification.json
data/derived/ranking.json
data/derived/questions.json
data/eval/INSTANT_FAIL.md
data/eval/GROUNDEDNESS.md
data/eval/EVAL_NOTES.md
data/manifest.json
```

No Groq key is required. Ranking is deterministic from Phase 2 claims.

---

## Files

| File | Role |
|---|---|
| `run.py` | CLI |
| `cluster.py` | Theme → opportunity area (behavior, not feature) |
| `quantify.py` | Counts, delay share, price vs non-monetary, Reddit share |
| `rank.py` | Rubric scores + written comparison |
| `questions.py` | Q1–10 Answered / Partial / Gap |
| `report.py` | Discovery report |
| `evals_check.py` | Instant-fail table + 20-claim groundedness sample |
| `load.py` | JSONL I/O + Phase 2 quote check |
| `config.py` | Paths |
