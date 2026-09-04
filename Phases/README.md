# Phases

Master folder for Part 1 implementation. Each phase lives in its own subfolder. Do not mix phase code.

| Folder | Phase | Status |
|---|---|---|
| [Phase0_CorpusDesign](Phase0_CorpusDesign/) | 0 — Corpus design (source spec) | Done |
| [Phase1_RedditIngest](Phase1_RedditIngest/) | 1 — Reddit ingest (Arctic Shift / Pullpush) | Done |
| [Phase2_RelevanceAndExtraction](Phase2_RelevanceAndExtraction/) | 2 — Relevance gate + claims (Groq) | Done |
| [Phase3_RankedDraft](Phase3_RankedDraft/) | 3 — Reddit-only ranked draft | Done |
| [Phase4_StoreReviews](Phase4_StoreReviews/) | 4 — Play / App Store corroboration | Done |
| [Phase5_OptionalExpansion](Phase5_OptionalExpansion/) | 5 — Wishlist sweep for the Q1/Q8 Gaps | Done (sweep truncated; Q1/Q8 Partial) |
| [Phase6_SignOff](Phase6_SignOff/) | 6 — Part 1 evals sign-off | Done |

Problem, architecture, evals, and the implementation plan stay in `DOCS/`. This folder holds executable specs, adapters, and phase outputs.

**Part 1 frozen package:** [Phase6_SignOff/output/](Phase6_SignOff/output/)  
(`discovery-report.md`, `evidence-ledger.json`, `PART2_HANDOFF.md`)

**Current contract for ingest:** [Phase0_CorpusDesign/source_spec.json](Phase0_CorpusDesign/source_spec.json)
