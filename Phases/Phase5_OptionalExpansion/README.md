# Phase 5 — Optional expansion (wishlist sweep)

Phase 5 is conditional in `DOCS/implementationplan.md`: run it only if important Gaps
survive Phases 3 and 4. Two did, and they are the two the north-star metric is built on:

- **Q1** Why do users add fashion products to their Myntra wishlist?
- **Q8** When is the wishlist genuine purchase intent versus bookmarking?

Both were Gaps because the corpus had almost no wishlist language: one of 326 Phase 1
Reddit documents and zero of 561 Phase 4 store reviews contained the word *wishlist*.
The Part 1 sign-off checklist requires intent vs bookmark to be addressed with evidence,
so the expansion targets that language and stops there. Extra sources are not a goal.

## What changed versus Phase 1

Phase 1 searched Myntra-named queries and kept documents that named Myntra. Two changes:

1. **Brand-optional.** `architecture.md` §3.3 asks for recall on wishlist and buy-later
   behaviour even when Myntra is not named, so a wishlist thread in an Indian fashion
   subreddit is in scope as `fashion_context`. Competitor-only text is still dropped.
2. **Thread-first.** Arctic Shift's comment keyword search times out, so the sweep finds
   wishlist *threads* by post search and then pulls each thread's comments by `link_id`.
   Comments inside a wishlist thread are on-topic even when they never repeat the word.

`archive.py` exists because the Phase 1 client treats every HTTP 422 as "keyword search
unsupported" and retries with the query dropped, turning a keyword search into an
unfiltered fetch of recent posts. Arctic Shift returns 422 for `Timeout. Maybe slow down
a bit`. Here 422 is a backoff and the query is never dropped.

## Claim facets

Every Phase 5 claim carries a `wishlist_facet` so the report can separate things that
normally get collapsed into "wishlist adds":

| Facet | Meaning |
|---|---|
| `why_add` | generic "it's on my wishlist", no reason stated |
| `archive` | saved without buying: inspiration, purges, months-old lists, public lists |
| `intent` | a save the person converted or plainly means to |
| `sale_park` | parked to wait for a sale event |
| `ceiling` | the list has grown past being usable |
| `fit_block` | fit or size is what stops the save from converting |
| `compare_block` | asking other people to help choose |

`archive` versus `intent` is the Q8 answer. `ceiling` is evidence for archive behaviour;
it is **not** evidence that a larger list would produce more purchases, and `evals_p5.py`
instant-fails the report if it ever makes that causal claim.

## Two new opportunity areas

Both are behaviours, not features. "Raise the cap" would be a solution and belongs to
Part 5, not to discovery.

- **`wishlist_intent_ambiguity`** — the wishlist holds shortlists and daydreams in the
  same place, so an add is a weak and inconsistent intent signal.
- **`wishlist_ceiling`** — the saved list outgrows the shopper who made it.

## Files

| File | Role |
|---|---|
| `config.py` | paths, sweep queries, trigger Gaps |
| `archive.py` | Arctic Shift client with correct 422 handling |
| `reddit_wishlist.py` | wishlist thread sweep + thread comment pull |
| `youtube.py` | optional YouTube comments, skipped cleanly without an API key |
| `ingest.py` | orchestrates the pull and records skipped sources |
| `extract.py` | relevance gate + faceted, quote-backed claims |
| `cluster_p5.py` | Phase 3/4 areas plus the two wishlist areas |
| `quantify_p5.py` | counts split by Reddit / store / expansion |
| `rank_p5.py` | Reddit-weighted rubric |
| `questions_p5.py` | ten questions; Q1/Q8 answers generated from facet counts |
| `report.py` | the discovery report |
| `evals_p5.py` | instant-fail table, groundedness sample |
| `run.py` | CLI |

## Run

```text
cd Phases/Phase5_OptionalExpansion
python run.py --dry-run
python run.py                 # pulls, then builds the report
python run.py --no-ingest     # rebuild from the raw file on disk
```

`--priority` sweeps only the eight subreddits that have actually produced wishlist
threads, which buys most of the recall for a fraction of the wall-clock; the city and
general-India tiers produced nothing. The sweep checkpoints after every subreddit and
merges with whatever is already on disk, so an interrupted pull is never lost and a
re-run adds rather than replaces. Use `--fresh` to start over.

The sweep is slow on purpose: Arctic Shift rate-limits, and the client backs off rather
than dropping queries. A full pull across all subreddit tiers takes roughly an hour.

**Current corpus is a truncated pull.** The full-tier sweep has not completed, so Q1 and
Q8 sit at Partial on a small number of threads. Re-running `python run.py --force` will
extend the corpus rather than replace it.

Optional sources:

- **YouTube** needs `YOUTUBE_API_KEY`. Without it the pull is skipped and named in the
  report's declared limitations.
- **MouthShut / Quora** are named in the Phase 0 spec but block automated collection.
  They are recorded as a declared limitation rather than a silent hole.

## Outputs

| Path | Contents |
|---|---|
| `output/discovery-report.md` | expanded ranked draft |
| `output/evidence-ledger.json` | every claim with quote, URL, facet, area |
| `data/derived/wishlist_evidence.json` | the intent-vs-bookmark split as counts |
| `data/eval/INSTANT_FAIL.md` | instant-fail table |
| `data/eval/GROUNDEDNESS.md` | groundedness sample |
| `data/eval/EVAL_NOTES.md` | eval summary |

Phase 5 does not claim Part 1 sign-off. Phase 6 is sign-off.
