"""Phase 5 paths and the wishlist-language sweep contract.

Phase 5 is conditional (implementationplan.md). It runs because Q1 and Q8
(wishlist as intent vs bookmark) were Gaps after Phases 3-4, and the Part 1
sign-off checklist requires intent vs bookmark to be addressed with evidence.
"""

from __future__ import annotations

from pathlib import Path

PHASE5_DIR = Path(__file__).resolve().parent
PHASES_DIR = PHASE5_DIR.parent
PHASE0_DIR = PHASES_DIR / "Phase0_CorpusDesign"
PHASE1_DIR = PHASES_DIR / "Phase1_RedditIngest"
PHASE2_DIR = PHASES_DIR / "Phase2_RelevanceAndExtraction"
PHASE3_DIR = PHASES_DIR / "Phase3_RankedDraft"
PHASE4_DIR = PHASES_DIR / "Phase4_StoreReviews"

PHASE0_SPEC = PHASE0_DIR / "source_spec.json"
PHASE1_RAW = PHASE1_DIR / "data" / "raw" / "reddit_documents.jsonl"
PHASE1_MANIFEST = PHASE1_DIR / "data" / "raw" / "manifest.json"
PHASE2_LABELED = PHASE2_DIR / "data" / "labeled" / "reddit_labeled.jsonl"
PHASE2_CLAIMS = PHASE2_DIR / "data" / "claims" / "reddit_claims.jsonl"
PHASE2_MANIFEST = PHASE2_DIR / "data" / "manifest.json"
PHASE4_RAW = PHASE4_DIR / "data" / "raw" / "store_reviews.jsonl"
PHASE4_LABELED = PHASE4_DIR / "data" / "labeled" / "store_labeled.jsonl"
PHASE4_CLAIMS = PHASE4_DIR / "data" / "claims" / "store_claims.jsonl"
PHASE4_INGEST_MANIFEST = PHASE4_DIR / "data" / "raw" / "manifest.json"

DATA_DIR = PHASE5_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_PATH = RAW_DIR / "expansion_documents.jsonl"
PULL_LOG_PATH = RAW_DIR / "pull_log.jsonl"
INGEST_MANIFEST = RAW_DIR / "manifest.json"

LABELED_PATH = DATA_DIR / "labeled" / "expansion_labeled.jsonl"
CLAIMS_PATH = DATA_DIR / "claims" / "expansion_claims.jsonl"
COMBINED_CLAIMS_PATH = DATA_DIR / "claims" / "combined_claims.jsonl"

DERIVED_DIR = DATA_DIR / "derived"
CLUSTERS_PATH = DERIVED_DIR / "clusters.jsonl"
QUANT_PATH = DERIVED_DIR / "quantification.json"
RANKING_PATH = DERIVED_DIR / "ranking.json"
QUESTIONS_PATH = DERIVED_DIR / "questions.json"
WISHLIST_PATH = DERIVED_DIR / "wishlist_evidence.json"
RUBRIC_PATH = DERIVED_DIR / "rubric.json"
MANIFEST_PATH = DATA_DIR / "manifest.json"

EVAL_DIR = DATA_DIR / "eval"
INSTANT_FAIL_PATH = EVAL_DIR / "INSTANT_FAIL.md"
GROUNDEDNESS_PATH = EVAL_DIR / "GROUNDEDNESS.md"
EVAL_SUMMARY_PATH = EVAL_DIR / "EVAL_NOTES.md"

OUTPUT_DIR = PHASE5_DIR / "output"
REPORT_PATH = OUTPUT_DIR / "discovery-report.md"
LEDGER_PATH = OUTPUT_DIR / "evidence-ledger.json"

IN_SCOPE_LABELS = frozenset({"myntra_primary", "fashion_context"})
MIN_RANKED_AREAS = 5
GROUNDEDNESS_SAMPLE_N = 20
GROUNDEDNESS_SEED = 5

# Why Phase 5 ran. Named in the report so the expansion is not open-ended.
TRIGGER_GAPS = ("Q1 why add to wishlist", "Q8 wishlist as intent vs bookmark")

# Wishlist-language sweep. Brand-optional on purpose: architecture.md 3.3 says
# prefer recall for wishlist / buy-later behavior even when Myntra is not named.
WISHLIST_QUERIES: tuple[dict[str, object], ...] = (
    {"id": "wl_myntra", "query": "myntra wishlist", "questions": [1, 8], "brand_required": True},
    {"id": "wl_limit", "query": "wishlist limit", "questions": [1, 8], "brand_required": False},
    {"id": "wl_full", "query": "wishlist full", "questions": [1, 8], "brand_required": False},
    {"id": "wl_cap", "query": "wishlist cap", "questions": [1, 8], "brand_required": False},
    {"id": "wl_added", "query": "added to wishlist", "questions": [1, 8], "brand_required": False},
    {"id": "wl_save_later", "query": "save for later", "questions": [1, 8], "brand_required": False},
    {"id": "wl_clear", "query": "clear wishlist", "questions": [8], "brand_required": False},
    {"id": "wl_never_buy", "query": "wishlist never buy", "questions": [2, 8], "brand_required": False},
    {"id": "wl_sale_watch", "query": "wishlist wait for sale", "questions": [4, 8], "brand_required": False},
    {"id": "wl_bookmark", "query": "wishlist bookmark shopping", "questions": [1, 8], "brand_required": False},
)

# Broad recall: every tier from the Phase 0 spec, not just the Phase 1 slice.
SWEEP_TIERS = ("primary", "india_general", "city", "try_if_exists", "global_context")

# Subreddits where wishlist threads actually turned up in the first pass, plus the
# shopping-specific ones. Used by --priority to buy most of the recall for a
# fraction of the wall-clock; city and general-India subs produced nothing.
PRIORITY_SUBREDDITS = (
    "IndianFashionAddicts",
    "indianfashion",
    "DesiFashionAdvice",
    "IndianStreetFashion",
    "TwoXIndia",
    "IndiaShopping",
    "Myntra",
    "femalefashionadvice",
)

DEFAULT_MAX_PER_QUERY = 40
DEFAULT_SLEEP_S = 1.2

# Optional sources. Skipped cleanly (and named as Gaps) when unavailable.
YOUTUBE_API_KEY_ENV = "YOUTUBE_API_KEY"
YOUTUBE_QUERIES = ("myntra haul", "myntra try on", "myntra sizing", "myntra review")
YOUTUBE_MAX_VIDEOS = 6
YOUTUBE_MAX_COMMENTS = 60
