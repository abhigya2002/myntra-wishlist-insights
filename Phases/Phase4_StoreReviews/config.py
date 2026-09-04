"""Phase 4 paths and store-app seeds from Phase 0."""

from __future__ import annotations

from pathlib import Path

PHASE4_DIR = Path(__file__).resolve().parent
PHASES_DIR = PHASE4_DIR.parent
PHASE0_DIR = PHASES_DIR / "Phase0_CorpusDesign"
PHASE1_DIR = PHASES_DIR / "Phase1_RedditIngest"
PHASE2_DIR = PHASES_DIR / "Phase2_RelevanceAndExtraction"
PHASE3_DIR = PHASES_DIR / "Phase3_RankedDraft"

PHASE0_SPEC = PHASE0_DIR / "source_spec.json"
PHASE1_RAW = PHASE1_DIR / "data" / "raw" / "reddit_documents.jsonl"
PHASE1_MANIFEST = PHASE1_DIR / "data" / "raw" / "manifest.json"
PHASE2_LABELED = PHASE2_DIR / "data" / "labeled" / "reddit_labeled.jsonl"
PHASE2_CLAIMS = PHASE2_DIR / "data" / "claims" / "reddit_claims.jsonl"
PHASE2_MANIFEST = PHASE2_DIR / "data" / "manifest.json"
PHASE2_EVAL = PHASE2_DIR / "data" / "eval" / "GATE_CHECK.md"

DATA_DIR = PHASE4_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
LABELED_PATH = DATA_DIR / "labeled" / "store_labeled.jsonl"
CLAIMS_PATH = DATA_DIR / "claims" / "store_claims.jsonl"
COMBINED_CLAIMS_PATH = DATA_DIR / "claims" / "combined_claims.jsonl"
DERIVED_DIR = DATA_DIR / "derived"
EVAL_DIR = DATA_DIR / "eval"
OUTPUT_DIR = PHASE4_DIR / "output"

RAW_PATH = RAW_DIR / "store_reviews.jsonl"
PULL_LOG_PATH = RAW_DIR / "pull_log.jsonl"
INGEST_MANIFEST = RAW_DIR / "manifest.json"

CLUSTERS_PATH = DERIVED_DIR / "clusters.jsonl"
QUANT_PATH = DERIVED_DIR / "quantification.json"
RANKING_PATH = DERIVED_DIR / "ranking.json"
QUESTIONS_PATH = DERIVED_DIR / "questions.json"
CORROBORATION_PATH = DERIVED_DIR / "corroboration.json"
RUBRIC_PATH = DERIVED_DIR / "rubric.json"
MANIFEST_PATH = DATA_DIR / "manifest.json"

REPORT_PATH = OUTPUT_DIR / "discovery-report.md"
LEDGER_PATH = OUTPUT_DIR / "evidence-ledger.json"

INSTANT_FAIL_PATH = EVAL_DIR / "INSTANT_FAIL.md"
GROUNDEDNESS_PATH = EVAL_DIR / "GROUNDEDNESS.md"
EVAL_SUMMARY_PATH = EVAL_DIR / "EVAL_NOTES.md"

PLAY_APP_ID = "com.myntra.android"
APP_STORE_ID = "907394059"
APP_STORE_NAME = "Myntra Fashion Shopping App"
PLAY_URL = f"https://play.google.com/store/apps/details?id={PLAY_APP_ID}&hl=en_IN&gl=IN"
APP_STORE_URL = f"https://apps.apple.com/in/app/myntra-fashion-shopping-app/id{APP_STORE_ID}"

STORE_KEYWORDS = ("wishlist", "size", "fit", "return", "quality", "sale", "size chart")
IN_SCOPE_LABELS = frozenset({"myntra_primary", "fashion_context"})
MIN_RANKED_AREAS = 5
GROUNDEDNESS_SAMPLE_N = 20
GROUNDEDNESS_SEED = 4
DEFAULT_PLAY_COUNT = 200
DEFAULT_APP_STORE_PAGES = 10
