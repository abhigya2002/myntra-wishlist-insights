# WishlistInsights

Streamlit app for Myntra superiors: grounded Q&A over the Part 1 discovery freeze, plus a management Pulse brief.

## Tabs

1. **Ask** — BM25 RAG chatbot (claims → report → derived → raw). Answers cite quote + URL / claim_id; refuses MVP pitches, coupons, and “raising wishlist cap raises sales.”
2. **Pulse** — deterministic management brief from Phase 5 derived JSON + Phase 6 freeze (also written to `output/pulse-report.md`).

## Setup

```bash
cd Apps/WishlistInsights
pip install -r requirements.txt
```

Groq key loads from `Phases/Phase2_RelevanceAndExtraction/.env` (same pattern as Phase 2). Optional: `Apps/WishlistInsights/.env`.

## Rebuild index

```bash
python build_index.py
```

Writes `data/index.jsonl` from Phase 6 freeze, Phase 5 claims/derived, and Phase 1/4/5 raw docs.

## Generate Pulse markdown

```bash
python pulse.py
```

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub (private is fine).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Settings:
   - **Main file path:** `Apps/WishlistInsights/app.py`
   - **Python version:** 3.11+ (default is fine)
4. Under **Advanced settings → Secrets**, paste:

```toml
GROQ_API_KEY = "gsk_..."
GROQ_MODEL = "llama-3.3-70b-versatile"
```

5. Deploy. The prebuilt `data/index.jsonl` and `output/pulse-report.md` ship with the repo so Ask + Pulse work on first boot.

Local secrets file (gitignored): copy `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml`.

