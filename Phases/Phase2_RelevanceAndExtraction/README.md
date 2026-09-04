# Phase 2 — Relevance gate + extraction

**Done when:** `data/claims` has quote-backed rows and a 15-doc gate sample is checked.

Two mixed steps from [architecture.md](../../DOCS/architecture.md), on the Phase 1 Reddit corpus:

1. **Relevance gate** — `myntra_primary` | `fashion_context` | `competitor_only` | `noise`
2. **Structured extraction** — claims with a **verbatim quote** and discovery question ids 1–10. Fail closed: if the quote is not in the source document, there is no claim.

LLM calls use **Groq** (`llama-3.3-70b-versatile` by default). Put the key in `.env` (see `.env.example`). `GROQ_API_KEY` from [console.groq.com/keys](https://console.groq.com/keys). Without a key, the same pipeline runs on heuristics so labeling still exists; claims will be lower confidence.

---

## Run

```text
copy .env.example .env
# edit .env and set GROQ_API_KEY

python run.py --dry-run
python run.py
python run.py --no-groq
python run.py --sample-only
python apply_human_check.py --labels myntra_primary,...
```

Human-check the 15-doc sample (evals.md §8) via `data/eval/GATE_CHECK.md`.

Outputs:

```text
data/labeled/reddit_labeled.jsonl
data/claims/reddit_claims.jsonl
data/eval/gate_sample.jsonl
data/eval/GATE_CHECK.md
data/manifest.json
```

Groq raw responses are cached in `data/cache/groq_raw.jsonl` so a re-run can skip completed docs. The previous Gemini cache (`data/cache/gemini_raw.jsonl`) is still read so those 11 docs are not recalled.

---

## Files

| File | Role |
|---|---|
| `run.py` | CLI |
| `analyze.py` | Heuristic gate/extract + LLM prompt + merge |
| `groq_client.py` | `api.groq.com/openai/v1/chat/completions` JSON calls |
| `schema.py` | Labels, claim fields, quote recovery |
| `sample.py` | 15-doc stratified gate sample |
| `apply_human_check.py` | Record 15 human gate labels + accuracy |
| `config.py` | Paths and key loading |
| `.env.example` | Key slot (`GROQ_API_KEY`) |
