# Source spec (Phase 0)

One-page ingest contract for the Myntra wishlist discovery engine. Canonical machine copy: `source_spec.json`.

**Product:** Myntra · **Priority source:** Reddit · **Window:** 2024-08-17 → 2026-08-17 (24 months, Asia/Kolkata) · **Why 24 months:** covers two Diwali cycles, two wedding peaks, EORS / Big Fashion Festival, and Republic Day / Independence Day / New Year sales.

Phase 1 pulls **Reddit only**. Rows below for stores / YouTube / communities are seeds for later phases, not current ingest.

---

## Reddit — where to search

| Tier | Subreddits | How Phase 1 uses them |
|---|---|---|
| Primary | IndianFashionAddicts, indianfashion, DesiFashionAdvice, IndianStreetFashion, IndianMakeupAddicts, TwoXIndia | First pass for branded and unbranded queries |
| India general | india, AskIndia, IndiaSpeaks, NRI, ABCDesis | Branded queries + unbranded shopping talk |
| City | mumbai, bangalore, delhi, hyderabad, Pune, Chennai, kolkata | Unbranded + metro segment *hypotheses* (not assumed true) |
| Global context | femalefashionadvice, malefashionadvice, plussize | Low priority; fashion_context only |
| Try if exists | Myntra, IndiaShopping, IndianConsumer, Flipkart, IndianWeddings, IndianStreetwear | Skip on 404; do not fail the run |

**Scope:** `myntra_named` queries run **site-wide and** in primary subs (Myntra threads are sparse). `behavior_unbranded` queries run in primary + India general + city only (global fashion is too noisy). Phase 1 starts with `--slice first` (site_wide + primary), then expands.

**Waves:** Phase 1 runs wave 1 first (named: site-wide + primary; unbranded: primary), dedupes by post id, then wave 2 (unbranded: India general + city) only if Q6/Q9 are thin. `try_if_exists` subs are not in the default job list; probe them separately and skip 404s.

**Pull shape:** submissions + comments. Keep Hinglish. Do not drop short comments (“runs small”). Log `query_id` + pull date on every raw doc. Skip private, deleted, and removed bodies.

---

## Reddit — what to search

**Myntra-named:** myntra; myntra wishlist; "added to wishlist" myntra; myntra "save for later"; myntra size; myntra "size chart"; myntra fit; "runs small" myntra; myntra quality; myntra "not worth"; myntra sale; myntra EORS; "price drop" myntra; "wait for sale" myntra; myntra vs ajio; "which one" myntra; "has anyone bought" myntra; myntra haul; myntra review; myntra wedding; myntra ethnic; myntra kurta; myntra "western wear"; myntra return; myntra "try and buy".

**Behavior, brand optional:** wishlist fashion india; "save for later" shopping india; online shopping size chart india; "runs small" online shopping india; "wait for sale" clothes india; ethnic wear fit online; "should I buy" dress india; "has anyone ordered" ethnic; wedding shopping online india; fake reviews myntra OR ajio.

Each query is tagged to discovery questions 1–10 in `source_spec.json`.

---

## Later-phase seeds (do not pull in Phase 1)

| Phase | Source | Seed |
|---|---|---|
| 4 | Play Store | `com.myntra.android` — wishlist, size, fit, return, quality, sale |
| 4 | App Store | Myntra Fashion Shopping App — same keywords |
| 5 | Communities | MouthShut Myntra; public Quora "Myntra wishlist/size/fit" |
| 5 | YouTube | "myntra haul", "myntra try on", "myntra sizing", "myntra review" |
| 5 | Social | Public posts only, and only if question Gaps remain |

AJIO / Nykaa appear only as comparison, never as the product under study.

---

## Do not ingest

Private WhatsApp / Telegram / Discord; Instagram or Facebook DMs and private groups; Reddit chat; Myntra account data (wishlists, orders, cart); anything behind login or paywall; scraped customer PII; non-public Facebook groups.

Off-platform research (WhatsApp, Instagram) is a **Part 3 interview topic**, not an ingest target.

---

## Repeatability

Phase 1 loads this spec, expands pull jobs (`python spec.py jobs`), writes raw docs with architecture fields (`id`, `source`, `url`, `captured_at`, `created_at`, `title`, `body`, `thread_context`, `raw_metadata`), and records query + window + pull timestamp. Relevance filtering is Phase 2 — do not pre-discard “maybe off-topic” Reddit hits.
