"""Phase 3 paths. Reads Phase 1 raw docs and Phase 2 claims/labels."""

from __future__ import annotations

from pathlib import Path

PHASE3_DIR = Path(__file__).resolve().parent
PHASES_DIR = PHASE3_DIR.parent
PROJECT_DIR = PHASES_DIR.parent
PHASE1_DIR = PHASES_DIR / "Phase1_RedditIngest"
PHASE2_DIR = PHASES_DIR / "Phase2_RelevanceAndExtraction"

PHASE1_RAW = PHASE1_DIR / "data" / "raw" / "reddit_documents.jsonl"
PHASE1_MANIFEST = PHASE1_DIR / "data" / "raw" / "manifest.json"
PHASE2_LABELED = PHASE2_DIR / "data" / "labeled" / "reddit_labeled.jsonl"
PHASE2_CLAIMS = PHASE2_DIR / "data" / "claims" / "reddit_claims.jsonl"
PHASE2_MANIFEST = PHASE2_DIR / "data" / "manifest.json"
PHASE2_EVAL = PHASE2_DIR / "data" / "eval" / "GATE_CHECK.md"

DATA_DIR = PHASE3_DIR / "data"
DERIVED_DIR = DATA_DIR / "derived"
EVAL_DIR = DATA_DIR / "eval"
OUTPUT_DIR = PHASE3_DIR / "output"

CLUSTERS_PATH = DERIVED_DIR / "clusters.jsonl"
QUANT_PATH = DERIVED_DIR / "quantification.json"
RANKING_PATH = DERIVED_DIR / "ranking.json"
QUESTIONS_PATH = DERIVED_DIR / "questions.json"
RUBRIC_PATH = DERIVED_DIR / "rubric.json"
MANIFEST_PATH = DATA_DIR / "manifest.json"

REPORT_PATH = OUTPUT_DIR / "discovery-report.md"
LEDGER_PATH = OUTPUT_DIR / "evidence-ledger.json"

INSTANT_FAIL_PATH = EVAL_DIR / "INSTANT_FAIL.md"
GROUNDEDNESS_PATH = EVAL_DIR / "GROUNDEDNESS.md"
EVAL_SUMMARY_PATH = EVAL_DIR / "EVAL_NOTES.md"

IN_SCOPE_LABELS = frozenset({"myntra_primary", "fashion_context"})
MIN_RANKED_AREAS = 5
GROUNDEDNESS_SAMPLE_N = 20
GROUNDEDNESS_SEED = 3
