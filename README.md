# Myntra Wishlist Insights

Grounded discovery research on **why Myntra shoppers add to wishlist but do not buy**, plus a Streamlit app for leadership Q&A and a management Pulse brief.

North-star metric (definition only — **no invented rates**):

> **Numerator** = buyers from wishlist · **Denominator** = users who add  
> This repo reports **public-signal blockers** that sit between add and buy, not internal conversion %.

---

## What’s in this repo

| Area | Path | Status |
|---|---|---|
| Part 1 discovery pipeline (Phases 0–6) | [`Phases/`](Phases/) | **Signed off / frozen** |
| Canonical freeze package | [`Phases/Phase6_SignOff/output/`](Phases/Phase6_SignOff/output/) | Report + evidence ledger |
| Streamlit RAG app (Ask + Pulse) | [`Apps/WishlistInsights/`](Apps/WishlistInsights/) | Ready to run / deploy |
| Stitch UI references | [`Apps/Myntra Stich 1/`](Apps/Myntra%20Stich%201/), [`Apps/Myntra Stich 2/`](Apps/Myntra%20Stich%202/) | Design + HTML samples |
| Part 2 metric tree | `Part 2/` (local; not in this remote by default) | Paused |

---

## Product context

Myntra leadership needs evidence on wishlist behaviour and conversion friction **without**:

- inventing internal conversion percentages  
- pitching MVPs, coupons, or “raising the wishlist cap raises sales”  
- treating every wishlist add as purchase intent  

Part 1 answers ten discovery questions from **public** sources (Reddit primary; Play Store / App Store corroboration; wishlist-language expansion).

---

## Part 1 — pipeline (done)

```text
Phase 0  Corpus design (source spec)
Phase 1  Reddit ingest
Phase 2  Relevance gate + claim extraction (Groq)
Phase 3  Reddit-only ranked draft
Phase 4  Play / App Store corroboration
Phase 5  Wishlist sweep (Q1 / Q8 gaps)
Phase 6  Evals + sign-off → freeze
```

### Freeze snapshot

| Field | Value |
|---|---|
| Frozen at | 2026-08-31 |
| Question coverage | **10/10** (6 Answered, 4 Partial, 0 Gap) |
| Corpus (approx.) | 988 raw docs · 380 claims |
| Mix | Reddit 427 docs · Play 143 · App Store 418 |
| Wishlist-language claims | 10 across 5 threads (thin but decisive on intent vs bookmark) |

**Canonical outputs**

- [`discovery-report.md`](Phases/Phase6_SignOff/output/discovery-report.md)  
- [`evidence-ledger.json`](Phases/Phase6_SignOff/output/evidence-ledger.json)  
- [`PART2_HANDOFF.md`](Phases/Phase6_SignOff/output/PART2_HANDOFF.md)  

### Top ranked public-signal areas

1. `quality_uncertainty`  
2. `fit_size_uncertainty`  
3. `returns_and_order_trust`  
4. `review_thinness`  
5. `wishlist_intent_ambiguity`  
6. `price_watch_and_checkout`  
7. `off_platform_research`  
8. `assortment_or_access_gap`  
9. `occasion_and_styling_uncertainty`  
10. `cross_listing_compare`  

### Wishlist reading (Q1 / Q8 — Partial)

Bookmark-style saving (archive / inspiration / show-and-tell) outweighs stated buy intent. An add is a **weak default signal of intent**. The corpus does **not** establish that raising or removing a saved-item ceiling would increase purchases.

---

## App — Wishlist Insights

Streamlit app with Myntra-inspired UI (Montserrat + Inter, magenta→orange accents):

1. **Ask** — BM25 RAG over claims → report sections → derived facts → raw docs. Groq generates grounded answers with citations (`claim_id` / URL). Refuses solution pitches and invented KPIs.  
2. **Pulse** — Deterministic management brief from Phase 5 derived JSON + Phase 6 freeze (`output/pulse-report.md`).

### Run locally

```bash
cd Apps/WishlistInsights
pip install -r requirements.txt
python build_index.py          # rebuild data/index.jsonl if needed
python pulse.py                # refresh output/pulse-report.md
streamlit run app.py
```

**API key:** set `GROQ_API_KEY` in:

- `Phases/Phase2_RelevanceAndExtraction/.env`, or  
- `Apps/WishlistInsights/.streamlit/secrets.toml` (see `secrets.toml.example`)

Never commit real keys (`.env` / `secrets.toml` are gitignored).

### Deploy (Streamlit Community Cloud)

| Setting | Value |
|---|---|
| Repository | `abhigya2002/myntra-wishlist-insights` |
| Branch | `main` |
| Main file | `Apps/WishlistInsights/app.py` |

**Secrets** (Cloud → Settings → Secrets):

```toml
GROQ_API_KEY = "gsk_..."
GROQ_MODEL = "llama-3.3-70b-versatile"
```

Prebuilt `data/index.jsonl` and `output/pulse-report.md` ship with the repo so Ask + Pulse work on first boot.

More detail: [`Apps/WishlistInsights/README.md`](Apps/WishlistInsights/README.md)

---

## Honesty constraints (non-negotiable)

- No invented Myntra conversion % or internal add/order volumes  
- Pulse frames **public-signal blockers** between add and buy  
- Chat refuses MVP pitches, coupons, and “wishlist cap → sales” claims  
- Answers must cite quote + URL / `claim_id`, or say evidence is insufficient  
- Q1 and Q8 remain **Partial** on a thin wishlist base — do not treat them as fully Answered  

---

## Repo layout

```text
Apps/
  WishlistInsights/     # Streamlit Ask + Pulse
  Myntra Stich 1/       # Chat UI Stitch design + HTML
  Myntra Stich 2/       # Pulse UI Stitch design + HTML
Phases/
  Phase0_… → Phase6_…   # Part 1 pipeline + freeze
```

---

## What’s next (out of scope for this freeze)

- Part 2 metric-tree work (paused locally)  
- Hosting/SSO beyond Streamlit Community Cloud  
- Expanding the Reddit wishlist sweep  
- Internal analytics dashboards  

---

## License / access

Private research repository. Do not redistribute evidence quotes beyond intended internal use without checking source terms (Reddit / store review ToS).
