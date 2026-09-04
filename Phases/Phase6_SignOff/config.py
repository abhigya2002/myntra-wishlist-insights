"""Phase 6 paths. Sign-off freezes the Phase 5 mixed-source draft as Part 1 output."""

from __future__ import annotations

from pathlib import Path

PHASE6_DIR = Path(__file__).resolve().parent
PHASES_DIR = PHASE6_DIR.parent
PROJECT_DIR = PHASES_DIR.parent
DOCS_DIR = PROJECT_DIR / "DOCS"

PHASE0_DIR = PHASES_DIR / "Phase0_CorpusDesign"
PHASE1_DIR = PHASES_DIR / "Phase1_RedditIngest"
PHASE2_DIR = PHASES_DIR / "Phase2_RelevanceAndExtraction"
PHASE3_DIR = PHASES_DIR / "Phase3_RankedDraft"
PHASE4_DIR = PHASES_DIR / "Phase4_StoreReviews"
PHASE5_DIR = PHASES_DIR / "Phase5_OptionalExpansion"

# Canonical Part 1 draft is the Phase 5 report (Reddit + stores + wishlist expansion).
SOURCE_REPORT = PHASE5_DIR / "output" / "discovery-report.md"
SOURCE_LEDGER = PHASE5_DIR / "output" / "evidence-ledger.json"
SOURCE_MANIFEST = PHASE5_DIR / "data" / "manifest.json"
SOURCE_RANKING = PHASE5_DIR / "data" / "derived" / "ranking.json"
SOURCE_QUESTIONS = PHASE5_DIR / "data" / "derived" / "questions.json"
SOURCE_WISHLIST = PHASE5_DIR / "data" / "derived" / "wishlist_evidence.json"
SOURCE_INSTANT_FAIL = PHASE5_DIR / "data" / "eval" / "INSTANT_FAIL.md"
SOURCE_GROUNDEDNESS = PHASE5_DIR / "data" / "eval" / "GROUNDEDNESS.md"
SOURCE_EVAL_NOTES = PHASE5_DIR / "data" / "eval" / "EVAL_NOTES.md"

PHASE1_RAW = PHASE1_DIR / "data" / "raw" / "reddit_documents.jsonl"
PHASE1_MANIFEST = PHASE1_DIR / "data" / "raw" / "manifest.json"
PHASE2_LABELED = PHASE2_DIR / "data" / "labeled" / "reddit_labeled.jsonl"
PHASE2_CLAIMS = PHASE2_DIR / "data" / "claims" / "reddit_claims.jsonl"
PHASE2_GATE_CHECK = PHASE2_DIR / "data" / "eval" / "GATE_CHECK.md"
PHASE4_RAW = PHASE4_DIR / "data" / "raw" / "store_reviews.jsonl"

DATA_DIR = PHASE6_DIR / "data"
EVAL_DIR = DATA_DIR / "eval"
MANIFEST_PATH = DATA_DIR / "manifest.json"
CHECKLIST_JSON = EVAL_DIR / "checklist.json"
CHECKLIST_MD = EVAL_DIR / "SIGN_OFF.md"
PROCESS_EVALS_MD = EVAL_DIR / "PROCESS_EVALS.md"

OUTPUT_DIR = PHASE6_DIR / "output"
FROZEN_REPORT = OUTPUT_DIR / "discovery-report.md"
FROZEN_LEDGER = OUTPUT_DIR / "evidence-ledger.json"
FROZEN_META = OUTPUT_DIR / "freeze.json"
PART2_HANDOFF = OUTPUT_DIR / "PART2_HANDOFF.md"

ARCHITECTURE_PATH = DOCS_DIR / "architecture.md"
IMPLEMENTATION_PATH = DOCS_DIR / "implementationplan.md"
EVALS_PATH = DOCS_DIR / "evals.md"

MIN_RANKED_AREAS = 5
MIN_COVERAGE = 8
MIN_GATE_SAMPLE = 15
