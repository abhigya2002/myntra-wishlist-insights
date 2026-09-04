"""Update DOCS/architecture.md and DOCS/implementationplan.md after sign-off.

Phase 6 requires these docs to describe the engine that actually ran, not the
v0 proposal. Updates are idempotent: a marker comment avoids double-appending.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from config import ARCHITECTURE_PATH, IMPLEMENTATION_PATH, PHASES_DIR
from io_util import write_text

MARKER = "<!-- phase6-as-built -->"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _architecture_body(snapshot: dict[str, Any]) -> str:
    return f"""{MARKER}
# Architecture — AI Discovery Engine (Part 1)

**Status:** as-built after Phase 6 sign-off ({snapshot.get("frozen_at") or utc_now()}).

**Scope:** Part 1 only. This system discovers why Myntra wishlist adds fail to convert within 30 days. It does not propose a product solution, run interviews, or decompose the metric tree.

**Source of truth for the problem:** [Problem.md](Problem.md)

**How we know the engine is good:** [evals.md](evals.md)

**Frozen Part 1 output (for Parts 2–4):**
`Phases/Phase6_SignOff/output/discovery-report.md` + `Phases/Phase6_SignOff/output/evidence-ledger.json`

---

## 1. What the system is

A batch Python pipeline under `Phases/` that:

1. Pulls public conversations about Myntra and India online fashion shopping
2. Keeps **Reddit as the primary ranking evidence base** (store reviews corroborate)
3. Extracts quote-backed claims against the ten discovery questions
4. Clusters, quantifies, and ranks opportunity areas for 30-day wishlist → purchase conversion
5. Freezes the Phase 5 mixed-source draft at Phase 6 sign-off

It is not a sentiment dashboard, a review summarizer, or an MVP of a shopping feature.

```mermaid
flowchart TD
    p0[Phase0_source_spec]
    p1[Phase1_RedditIngest]
    p2[Phase2_RelevanceAndExtraction]
    p3[Phase3_RankedDraft]
    p4[Phase4_StoreReviews]
    p5[Phase5_OptionalExpansion]
    p6[Phase6_SignOff]

    p0 --> p1 --> p2 --> p3
    p2 --> p4
    p3 --> p4
    p4 --> p5
    p5 --> p6
```

---

## 2. Design principles (unchanged)

- Metric-tied, not vibe-tied.
- Reddit-first; stores corroborate, they do not replace Reddit on the ranked list.
- Evidence over opinion: verbatim quotes + URLs; fail closed without a quote.
- Price talk is evidence; discounts are out of scope as opportunities.
- Myntra is the product; AJIO/Nykaa are comparison only.
- Segments are earned.
- Wishlist adds are not assumed to be purchase intent.

---

## 3. As-built layout

```
Phases/
  Phase0_CorpusDesign/          source_spec.json
  Phase1_RedditIngest/          Arctic Shift (+ Pullpush fallback) → reddit_documents.jsonl
  Phase2_RelevanceAndExtraction/ Groq relevance gate + claim extraction
  Phase3_RankedDraft/           Reddit-only ranked draft
  Phase4_StoreReviews/          Play Store + App Store corroboration
  Phase5_OptionalExpansion/     Wishlist-language sweep for Q1/Q8 Gaps
  Phase6_SignOff/               Checklist, freeze, Part 2 handoff
DOCS/
  Problem.md  architecture.md  implementationplan.md  evals.md
```

### 3.1 Adapters that actually ran

| Adapter | Implementation | Notes |
|---|---|---|
| Reddit | `Phase1_RedditIngest/arctic_shift.py`, `pullpush.py` | Pullpush often blocked for agents; Arctic Shift is the working path. Keyword timeouts must be retried, not treated as “unsupported.” |
| Play Store | `Phase4_StoreReviews/play_store.py` | `google-play-scraper` with urllib fallback |
| App Store | `Phase4_StoreReviews/app_store.py` | iTunes RSS |
| Wishlist sweep | `Phase5_OptionalExpansion/archive.py`, `reddit_wishlist.py` | Brand-optional thread-first sweep; comments via `link_id` |
| YouTube | `Phase5_OptionalExpansion/youtube.py` | Skipped — no `YOUTUBE_API_KEY` |
| MouthShut / Quora | — | Declared skipped; block automated collection |

### 3.2 Models

- **Groq** chat completions for Phase 2 gate + extraction (`llama-3.3-70b-versatile` with fallbacks). Key in `Phase2_RelevanceAndExtraction/.env`.
- **Heuristic extractors** for store reviews (Phase 4) and wishlist facets (Phase 5).
- Ranking is a **scored rubric** (not an LLM judge): metric 0.30, evidence 0.25, delay 0.20, constraint 0.15, segment 0.10. Phase 4/5 weight Reddit in the evidence factor.

### 3.3 Claim schema (as implemented)

Matches architecture §3.4. Phase 5 adds optional `wishlist_facet`:
`ceiling` | `archive` | `intent` | `sale_park` | `why_add` | `fit_block` | `compare_block`.

### 3.4 Opportunity areas (as ranked in the frozen draft)

Behaviors, not features. Phase 5 ranked list includes the original Phase 3 areas plus:
- `wishlist_intent_ambiguity` — shortlists and daydreams share one list
- `wishlist_ceiling` — list outgrows the shopper (present in code; **0 claims** in the frozen corpus)
- `app_friction` — store-volume; ranked only with Reddit support

---

## 4. Data flow (as run)

1. Phase 0 freezes queries, tiers, and the 24-month window in `source_spec.json`.
2. Phase 1 pulls Reddit into `reddit_documents.jsonl`.
3. Phase 2 labels + extracts; human gate sample in `GATE_CHECK.md` (15/15).
4. Phase 3 produces the Reddit-only draft + evals.
5. Phase 4 ingests store reviews, merges claims, re-ranks with Reddit primary.
6. Phase 5 runs only because Q1/Q8 were Gaps; wishlist sweep + re-rank.
7. Phase 6 checks evals.md §8–§9, freezes report + ledger, updates these docs.

---

## 5. Trust and provenance

- Every ranked opportunity points to claim IDs and URLs in the evidence ledger.
- Instant-fail and groundedness samples live under each phase’s `data/eval/`.
- Claims that cannot be recovered verbatim from the stored document do not ship.

---

## 6. Deliberately not ingested

- Private WhatsApp / Telegram / Discord / DMs
- Myntra account data (wishlists, orders, carts) — no internal conversion rate
- YouTube comments (no API key at run time)
- MouthShut / Quora (automation blocked)
- Full 27-subreddit wishlist sweep was truncated (disk / rate limits); Partial Q1/Q8 reflect that

---

## 7. Out of scope (still)

- Myntra in-app MVP, interview tooling, metric tree instrumentation
- Continuous production scraping
- Treating “raise the wishlist cap” as proven to raise purchases
"""


def _implementation_body(snapshot: dict[str, Any]) -> str:
    cov = snapshot.get("coverage") or {}
    wl = snapshot.get("wishlist") or {}
    return f"""{MARKER}
# Implementation Plan — AI Discovery Engine (Part 1)

**Status:** as-built after Phase 6 sign-off ({snapshot.get("frozen_at") or utc_now()}).

**Reads:** [Problem.md](Problem.md) · [architecture.md](architecture.md) · [evals.md](evals.md)

**Rule:** Do not start Parts 2–7 until Part 1 is signed off. Phase 6 has frozen the discovery package below.

**Frozen package:** `Phases/Phase6_SignOff/output/`
(`discovery-report.md`, `evidence-ledger.json`, `PART2_HANDOFF.md`)

---

## 1. Outcome (achieved)

A working Part 1 pipeline that:

- Ingested public Reddit + Play/App Store reviews (+ Phase 5 wishlist expansion)
- Extracted quote-backed claims against the ten discovery questions
- Produced a ranked set of opportunity areas tied to 30-day wishlist → purchase conversion
- Left an evidence ledger so every claim can be traced
- Passed evals.md instant-fail, coverage, and groundedness bars (see Phase 6 `SIGN_OFF.md`)

Coverage at freeze: **{cov.get("answered_or_partial", "?")}/10** Answered or Partial
(Answered {cov.get("answered", "?")}, Partial {cov.get("partial", "?")}, Gap {cov.get("gap", "?")}).

Wishlist evidence at freeze: **{wl.get("claims", "?")} claims / {wl.get("threads", "?")} threads** — {wl.get("reading", "")}
(Q1={wl.get("q1")}, Q8={wl.get("q8")}).

---

## 2. Build strategy (what we did)

Shipped Reddit vertical slice (Phases 0–3), then store corroboration (Phase 4), then a **conditional** wishlist expansion (Phase 5) because Q1/Q8 were Gaps. Phase 6 signed off.

Stack: Python scripts + Groq for Phase 2. No n8n / Zapier.

---

## 3. Repo layout (actual)

```
DOCS/                          problem, architecture, plan, evals
Phases/
  Phase0_CorpusDesign/
  Phase1_RedditIngest/
  Phase2_RelevanceAndExtraction/
  Phase3_RankedDraft/
  Phase4_StoreReviews/
  Phase5_OptionalExpansion/
  Phase6_SignOff/
```

Each phase owns its `data/` and (from Phase 3 up) `output/` and `data/eval/`.

---

## 4. Phases (status)

| Phase | Folder | Status |
|---|---|---|
| 0 Corpus design | `Phase0_CorpusDesign` | Done — `source_spec.json` |
| 1 Reddit ingest | `Phase1_RedditIngest` | Done — Arctic Shift primary |
| 2 Relevance + claims | `Phase2_RelevanceAndExtraction` | Done — Groq + heuristic; gate 15/15 |
| 3 Reddit ranked draft | `Phase3_RankedDraft` | Done — 9 areas, 8/10 coverage |
| 4 Store corroboration | `Phase4_StoreReviews` | Done — Play + App Store |
| 5 Wishlist expansion | `Phase5_OptionalExpansion` | Done — truncated sweep; Q1/Q8 Partial |
| 6 Part 1 sign-off | `Phase6_SignOff` | Done — checklist + freeze |

### Re-run commands

```text
cd Phases/Phase1_RedditIngest && python run.py
cd Phases/Phase2_RelevanceAndExtraction && python run.py
cd Phases/Phase3_RankedDraft && python run.py
cd Phases/Phase4_StoreReviews && python run.py --no-ingest
cd Phases/Phase5_OptionalExpansion && python run.py --no-ingest
cd Phases/Phase6_SignOff && python run.py
```

Phase 5 full sweep (optional, extends corpus): `python run.py --force` (needs free disk on C: for shell temp files).

---

## 5. Work that remains out of this plan

| Not now | Why |
|---|---|
| Metric decomposition (Part 2) | Starts from the frozen discovery package |
| User interviews (Part 3) | Validates after ranking |
| Problem / MVP (Parts 4–5) | Solutioning |
| Success metrics for a product (Parts 6–7) | No product yet |
| Private WhatsApp / DMs | Interview territory |
| Internal Myntra conversion telemetry | Not in public corpus |

---

## 6. Order of operations (complete)

- [x] Phase 0: source spec
- [x] Phase 1: Reddit raw corpus
- [x] Phase 2: labels + quote-backed claims
- [x] Phase 3: Reddit-only ranked draft + evals
- [x] Phase 4: Play/App Store corroboration
- [x] Phase 5: wishlist expansion for Q1/Q8 Gaps
- [x] Phase 6: sign-off; architecture + this plan updated

---

## 7. Sources skipped and why

- YouTube comments — no `YOUTUBE_API_KEY` in environment at pull time
- MouthShut / Quora — block automated collection; named as limitations
- Full wishlist subreddit tier list — sweep truncated; Partial Q1/Q8 are honest about thin base
- Private groups / Myntra account data — out of scope by architecture

---

## 8. Next

Open Part 2 using `Phases/Phase6_SignOff/output/PART2_HANDOFF.md`. Do not re-open Part 1 ranking unless the frozen sha256 fingerprints change via an intentional re-freeze.
"""


def update_docs(snapshot: dict[str, Any]) -> dict[str, str]:
    """Rewrite architecture + implementation plan to the as-built versions."""
    arch = _architecture_body(snapshot)
    plan = _implementation_body(snapshot)
    write_text(ARCHITECTURE_PATH, arch)
    write_text(IMPLEMENTATION_PATH, plan)
    return {
        "architecture": str(ARCHITECTURE_PATH),
        "implementationplan": str(IMPLEMENTATION_PATH),
        "phases_root": str(PHASES_DIR),
    }
