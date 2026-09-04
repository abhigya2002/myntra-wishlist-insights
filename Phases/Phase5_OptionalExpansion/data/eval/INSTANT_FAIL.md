# Instant-fail table (evals.md §2)

Overall: **CLEAR**

| Check | Result | Note |
|---|---|---|
| Output is ranked, not a sentiment dump | PASS | 10 ranked areas |
| Opportunity areas are not a product pitch | PASS | no MVP pitch language |
| Claims have verbatim quotes and source URLs | PASS | missing_quote=0 missing_url=0 |
| Reddit is the primary evidence base for ranked areas | PASS | every ranked area has Reddit claims; reddit_claims=134 |
| Play/App Store used as corroboration, not the whole story | PASS | corroboration rows with store=6 |
| Discount is not ranked as the opportunity | PASS | no coupon intervention in the ranked list |
| Every wishlist add is not treated as purchase intent | PASS | Q8=Partial |
| Segments are not asserted without quotes | PASS | Q9 stays earned-only |
| Myntra is the product | PASS | Myntra subject |
| All ten discovery questions are attempted | PASS | answered_or_partial=10/10 |
| Source counts appear in the report | PASS | store counts present |
| Expansion is justified by named Gaps, not curiosity | PASS | trigger=['Q1 why add to wishlist', 'Q8 wishlist as intent vs bookmark'] |
| Wishlist evidence is quantified, not asserted | PASS | wishlist_claims=10 threads=5 |
| No causal promise about lifting a saved-item ceiling | PASS | ceiling is reported as behaviour with direction unproven |
| Skipped sources are declared, not hidden | PASS | skipped=['youtube', 'communities'] |
| Q1 and Q8 improved on evidence, not on wording | PASS | Q1=Partial Q8=Partial |
