# Phase 1 — Reddit ingest (Myntra)

**Done when:** a Reddit corpus is on disk and can be re-run from the Phase 0 source spec.

Pulls **public** Reddit submissions and comments about **Myntra only**. Collection follows the three-pass pattern in [`DOCS/reviewfetchingdocument.txt`](../../DOCS/reviewfetchingdocument.txt):

1. Subreddit submissions
2. Comment search for product + discovery queries
3. Extra comments in the top fashion subreddits
4. Thread comments under kept Myntra posts (`link_id`)

**Primary API:** [Pullpush](https://api.pullpush.io) (no Reddit API key), as in the ReviewLens note.  
**Fallback:** [Arctic Shift](https://arctic-shift.photon-reddit.com/search) if Pullpush refuses automated agents. Arctic Shift cannot search site-wide (`query` requires a subreddit), so the fallback walks Phase 0 ingest subreddits with `q=myntra`.

AJIO, Nykaa, and other apps are dropped unless the same document also names Myntra. Unbranded Phase 0 queries (`behavior_unbranded`) are **not** fetched.

---

## Run

```text
python ingest.py --dry-run
python ingest.py
python ingest.py --backend arctic_shift
```

Outputs (from the last run: 326 documents, 90 submissions + 236 comments, Arctic Shift fallback because Pullpush refuses agents):

```text
data/raw/reddit_documents.jsonl
data/raw/pull_log.jsonl
data/raw/manifest.json
```

Useful flags:

```text
python ingest.py --max-per-subreddit 50 --max-threads 40 --sleep 4
python ingest.py --expand-threads --backend arctic_shift --max-threads 40
```

Each raw row matches the architecture document: `id`, `source`, `url`, `captured_at`, `created_at`, `title`, `body`, `thread_context`, `language`, `raw_metadata` (includes `subreddit`, `query_id`, `query`, `pull_job_id`, `spec_version`). Dedupes by Reddit id and URL.

---

## Files

| File | Role |
|---|---|
| `ingest.py` | CLI + ReviewLens-style passes |
| `pullpush.py` | Pullpush client (ReviewLens primary) |
| `arctic_shift.py` | Archive fallback when Pullpush blocks agents |
| `myntra_filter.py` | Product filter (Myntra required, competitor-only dropped) |
| `normalize.py` | API row → raw document |
| `corpus.py` | JSONL store + id/URL dedupe |
