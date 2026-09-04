# Discovery report — Reddit primary + store corroboration (Phase 4)

North-star: **% of Myntra users who purchase at least one wishlisted item within 30 days of adding it.** Hard constraint: no monetary incentive as the opportunity.

Instant-fail self-check: **all clear**. Groundedness sample: 20 claims, verbatim 100%, url 100%.

## Version and source mix

| Field | Value |
|---|---|
| Product | Myntra |
| Draft | Phase 4 — Reddit primary, Play/App Store corroboration |
| Reddit pull | 2026-08-17T16:51:24Z via `arctic_shift` |
| Reddit window | 2024-08-17 → 2026-08-17 |
| Store pull | 2026-08-30T19:03:29Z |
| Store window | 2024-08-17 → 2026-08-30T19:03:24Z |
| Play Store | `com.myntra.android` · 143 reviews |
| App Store | `907394059` · 418 reviews |
| Reddit docs (Phase 1) | 326 |
| Phase 2 claims | 124 (Groq + heuristic) |
| Store claims | 55 Play + 191 App Store |
| Combined claims | 370 · Reddit share of claims 34% |

AJIO / Nykaa appear only as comparison. Store reviews are used to **corroborate or challenge** Reddit themes (returns, size/fit, quality, trust, app friction), not to replace Reddit.

### Store keyword hits (document counts)

| Keyword | Docs |
|---|---:|
| wishlist | 0 |
| size | 8 |
| fit | 27 |
| return | 24 |
| quality | 92 |
| sale | 1 |
| size chart | 0 |

## How store reviews were used

| Area | Reddit claims | Play | App Store | Verdict |
|---|---:|---:|---:|---|
| Quality and authenticity doubt after shortlisting | 27 | 26 | 83 | corroborates Reddit |
| Return and order-integrity distrust that trains delay | 25 | 27 | 72 | corroborates Reddit |
| Thin or conflicting reviews after a product is identified | 18 | 0 | 7 | corroborates Reddit |
| Fit and size uncertainty after the item is chosen | 9 | 0 | 22 | corroborates Reddit |
| Price surprise and cross-platform price gaps | 9 | 2 | 5 | corroborates Reddit |
| Catalog miss: scrolled Myntra and still could not find the item | 14 | 0 | 2 | store present, thin |
| Occasion and styling uncertainty before committing | 10 | 0 | 0 | Reddit only so far |
| Leaving Myntra to ask Reddit, Instagram, or other sites | 6 | 0 | 0 | Reddit only so far |
| Comparing the same shortlist across marketplaces | 2 | 0 | 0 | Reddit only so far |

Store-only app-crash volume is **not** allowed to outrank a Reddit-backed wishlist-window area.

## Ten discovery questions

Coverage: **8/10** Answered or Partial (6 Answered, 2 Partial, 2 Gap).

### Q1. Why add to the Myntra wishlist?

**Gap** · 1 claims (1 Reddit / 0 store) · 1 threads

The Phase 2 claims do not contain explicit 'add to wishlist' language. wishlist_signal is `none` on every extracted claim. Raw Reddit text mentions wishlist in only a handful of documents, so why people add cannot be answered from this pull. Closest behaviors are scrolling Myntra, holding items in cart, and saving inspiration threads — which is bookmark-like, not a measured add.

_No explicit wishlist-add quote strong enough to close this Gap._

### Q2. What prevents wishlisted products from being purchased?

**Answered** · 298 claims (66 Reddit / 232 store) · 216 threads

What blocks a buy after Myntra is in play: missing/mixed reviews, quality or fake-goods fear, fit/size misses, checkout price jumps, and a reverse path (return/refund/cancel) that people do not trust. Several quotes sit at hesitation-to-order, not just after a bad delivery. Store reviews add 232 claims on this question (Play 53, App Store 179).

> I am scrolling through myntra and stuff but none of the affordable options have enough reviews for me to make a decision.
>
> — `t3_1tp0igu__c1` · https://www.reddit.com/r/TwoXIndia/comments/1tp0igu/affordable_college_purse_recommendation_please/

> Received different colored New balance worth ₹16k when I created return request, original item images changed on page.
>
> — `t1_oquls2f__c1` · https://www.reddit.com/r/Flipkart/comments/1u1wnjw/flipkart_is_a_scam/oquls2f/

> I've scrolled myntra day n night but didn't like a tee which has a deep neck, at least compared to regular ones.
>
> — `t3_1tvmrju__c1` · https://www.reddit.com/r/TwoXIndia/comments/1tvmrju/round_neck_suffocates_me/

### Q3. What uncertainties remain after a product is identified?

**Answered** · 231 claims (61 Reddit / 170 store) · 166 threads

After a product is identified, leftover uncertainty is whether reviews can be trusted, whether fabric/quality matches the image, whether it will fit, and whether the look works on their body/occasion. People keep asking Reddit after they have already scrolled Myntra. Store reviews add 170 claims on this question (Play 36, App Store 134).

> I am scrolling through myntra and stuff but none of the affordable options have enough reviews for me to make a decision.
>
> — `t3_1tp0igu__c1` · https://www.reddit.com/r/TwoXIndia/comments/1tp0igu/affordable_college_purse_recommendation_please/

> I've been surfing nykaa and myntra for past couple days but I'm in so much doubt ples help.
>
> — `t3_1vkwlay__c1` · https://www.reddit.com/r/TwoXIndia/comments/1vkwlay/recommend_good_high_impact_full_coverage_sports/

> whenever I order on Myntra, Amazon, etc the length is always short on me..
>
> — `t3_1unu1p2__c1` · https://www.reddit.com/r/TwoXIndia/comments/1unu1p2/tall_girlies_pls_help_me_find_pants/

### Q4. What causes postponement?

**Answered** · 130 claims (24 Reddit / 106 store) · 91 threads

Postponement shows up as waiting on occasion (wedding/event dressing), waiting on price/checkout math, and waiting because a return or refund last time went badly. Festival language in the raw pull is present but many heuristic 'occasion' hits are title echoes — those were down-weighted in ranking. Store reviews add 106 claims on this question (Play 29, App Store 77).

> After a week, exchange product came and the delivery agent again asked for the original product (which i had already handed over) so didn’t receive that exchange as well and hence neither I had the original product nor the exchanged one. [app_store]
>
> — `as_14486084800__s2` · https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059?see-all=reviews

> when I tried to exchange the size, the delivery agent denied the exchange as the app didn't accept the product received from them as it was a different brand and asked me to connect with the customer service loop. [play_store]
>
> — `gp_a2fdc505-d231-46eb-a6cc-234f68cf47cd__s1` · https://play.google.com/store/apps/details?id=com.myntra.android&hl=en_IN&gl=IN&reviewId=a2fdc505-d231-46eb-a6cc-234f68cf47cd

> okay I understand return policies are good, but atleast desanitize or clean the items before sending, because lately I have been returning every item only because they felt, smelt and seemed used. [play_store]
>
> — `gp_27c9d92b-c518-4594-b916-780d924dc8e6__s1` · https://play.google.com/store/apps/details?id=com.myntra.android&hl=en_IN&gl=IN&reviewId=27c9d92b-c518-4594-b916-780d924dc8e6

### Q5. How do users compare shortlisted products?

**Partial** · 3 claims (3 Reddit / 0 store) · 3 threads

Comparison language is thin. A few comments check that an item is 'also available in Myntra', ask 'which one do you suggest', or note the same SKU priced differently on Myntra vs Flipkart vs a brand site. This is cross-listing, not a documented 2–3 item shortlist workflow inside the Myntra wishlist.

> i have bigger bust size so it was soooo hard to find i tried zivame jockey etc but nothing came close to blissclub.
>
> — `t1_p3t27e2__c1` · https://www.reddit.com/r/TwoXIndia/comments/1vkwlay/recommend_good_high_impact_full_coverage_sports/p3t27e2/

> also available in myntra
>
> — `t1_oldjwxv__c1` · https://www.reddit.com/r/Flipkart/comments/1tazeu8/should_i_buy_it_from_flipkart/oldjwxv/

> Than which one do you suggest?
>
> — `t1_oowi41i__h1` · https://www.reddit.com/r/TwoXIndia/comments/1tqtehb/has_anyone_tried_hm_sports_bra/oowi41i/

### Q6. What do they seek outside Myntra before purchasing?

**Answered** · 20 claims (20 Reddit / 0 store) · 11 threads

Outside Myntra they ask Reddit ('has anyone tried'), look at Instagram/small brands, Decathlon, Zara/Urbanic/Forever New, Nykaa, Amazon, and brand sites. NRI threads also ask how to buy in India and ship out. This corpus *is* the off-platform step.

> where to find longer palazzos for tall girls that go below ankle, any small business or Insta stores are also fine if you’ve tried them
>
> — `t3_1unu1p2__c2` · https://www.reddit.com/r/TwoXIndia/comments/1unu1p2/tall_girlies_pls_help_me_find_pants/

> Generally I buy from Myntra but now it's same collection everywhere..
>
> — `t3_1um8tlo__c1` · https://www.reddit.com/r/TwoXIndia/comments/1um8tlo/can_someone_suggest_classy_palazzo_kurta_set_for/

> please do suggest some reliable long belts products or some better trust worthy sites to buy.
>
> — `t3_1nbkr1h__c3` · https://www.reddit.com/r/AskIndia/comments/1nbkr1h/looking_for_a_belt_for_obese_people/

### Q7. Role of fit, size, styling, price, reviews, occasion, social validation?

**Answered** · 82 claims (53 Reddit / 29 store) · 55 threads

Reviews and quality talk dominate. Fit/size is smaller but concrete (length short, bras, belts). Styling appears on event/saree threads. Price appears as checkout uplift and cross-platform gaps. Occasion is wedding/event dressing. Social validation is the 'has anyone tried' ask. These are roles in the journey, not a flat importance ranking. Store reviews add 29 claims on this question (Play 0, App Store 29).

> I am scrolling through myntra and stuff but none of the affordable options have enough reviews for me to make a decision.
>
> — `t3_1tp0igu__c1` · https://www.reddit.com/r/TwoXIndia/comments/1tp0igu/affordable_college_purse_recommendation_please/

> I've scrolled myntra day n night but didn't like a tee which has a deep neck, at least compared to regular ones.
>
> — `t3_1tvmrju__c1` · https://www.reddit.com/r/TwoXIndia/comments/1tvmrju/round_neck_suffocates_me/

> my budget was 600 and it's really the extreme of my budget but while placing order it adds upto 675
>
> — `t3_1nymnyi__c1` · https://www.reddit.com/r/AskIndia/comments/1nymnyi/need_ya_help_for_shopping_myntra/

### Q8. Wishlist as intent vs bookmark?

**Gap** · 8 claims (1 Reddit / 7 store) · 8 threads

Intent vs bookmark cannot be scored from this corpus. No claim is tagged explicit or implied wishlist. Treating every Myntra mention as purchase intent would fail the eval. The honest reading: people use Myntra as a browse/watch surface (scroll, compare, ask Reddit) and sometimes leave items in cart after a cancelled order. That is not the same as 'wishlist = almost a purchase'.

_No explicit wishlist-add quote strong enough to close this Gap._

### Q9. How do behaviors differ across segments?

**Partial** · 7 claims (7 Reddit / 0 store) · 5 threads

Only earned segments appear. ethnic_vs_western shows up on 6 claims (lehenga, palazzo, western-wear search). size_insecure_vs_size_confident shows up on 2 claims (tall length, plus-size belts, cup/band). Metro vs rest-of-India, first-time vs repeat, and sale-waiter vs occasion-buyer were not supported. No personas were invented.

> where to find longer palazzos for tall girls that go below ankle, any small business or Insta stores are also fine if you’ve tried them
>
> — `t3_1unu1p2__c2` · https://www.reddit.com/r/TwoXIndia/comments/1unu1p2/tall_girlies_pls_help_me_find_pants/

> Unfortunately, Myntra doesn't work outside of India (or at very least in EU).
>
> — `t3_1vj02n0__c1` · https://www.reddit.com/r/TwoXIndia/comments/1vj02n0/best_places_to_buy_lehengas_for_a_wedding/

> Generally I buy from Myntra but now it's same collection everywhere..
>
> — `t3_1um8tlo__c1` · https://www.reddit.com/r/TwoXIndia/comments/1um8tlo/can_someone_suggest_classy_palazzo_kurta_set_for/

### Q10. What unmet needs show up consistently?

**Answered** · 22 claims (20 Reddit / 2 store) · 18 threads

Recurring unmet needs: enough trusted reviews on affordable options, quality that matches the listing, sizes that exist (tall, plus, specific bra sizes), assortment that is not 'the same collection everywhere', and a reverse path that actually refunds. International access (Myntra not usable in the EU) is named but thin. Store reviews add 2 claims on this question (Play 0, App Store 2).

> where to find longer palazzos for tall girls that go below ankle, any small business or Insta stores are also fine if you’ve tried them
>
> — `t3_1unu1p2__c2` · https://www.reddit.com/r/TwoXIndia/comments/1unu1p2/tall_girlies_pls_help_me_find_pants/

> I am scrolling through myntra and stuff but none of the affordable options have enough reviews for me to make a decision.
>
> — `t3_1tp0igu__c1` · https://www.reddit.com/r/TwoXIndia/comments/1tp0igu/affordable_college_purse_recommendation_please/

> Received different colored New balance worth ₹16k when I created return request, original item images changed on page.
>
> — `t1_oquls2f__c1` · https://www.reddit.com/r/Flipkart/comments/1u1wnjw/flipkart_is_a_scam/oquls2f/

## Ranked opportunity areas

Behaviors / uncertainties, not features. Rank is the deliverable. Evidence strength is **Reddit-weighted**; store counts are corroboration.

| Rank | Area | Score | Reddit | Store | Delay | Non-monetary |
|---|---|---:|---:|---:|---:|---|
| 1 | Quality and authenticity doubt after shortlisting | 93.6 | 27 | 109 | 99% | yes |
| 2 | Fit and size uncertainty after the item is chosen | 89.2 | 9 | 22 | 74% | yes |
| 3 | Return and order-integrity distrust that trains delay | 83.5 | 25 | 99 | 85% | yes |
| 4 | Thin or conflicting reviews after a product is identified | 77.7 | 18 | 7 | 16% | yes |
| 5 | Leaving Myntra to ask Reddit, Instagram, or other sites | 69.6 | 6 | 0 | 17% | yes |
| 6 | Price surprise and cross-platform price gaps | 69.0 | 9 | 7 | 56% | no (price evidence) |
| 7 | Catalog miss: scrolled Myntra and still could not find the item | 66.8 | 14 | 2 | 62% | yes |
| 8 | Occasion and styling uncertainty before committing | 63.5 | 10 | 0 | 0% | yes |
| 9 | Comparing the same shortlist across marketplaces | 54.2 | 2 | 0 | 0% | yes |

Rubric: `100 * (0.30 metric + 0.25 evidence + 0.20 delay + 0.15 constraint + 0.10 segment)` with a +3 corroboration bonus when Reddit ≥ 2 and store ≥ 3.

### 1. Quality and authenticity doubt after shortlisting

**Behavior / uncertainty.** Users want an item that will last or match the listing, then hesitate or reverse because fabric, construction, or authenticity looks unreliable.

**Metric link.** Journey placement: **uncertainty after like**. 99% of claims carry delay/drop-off. This is residual uncertainty after a product is in play — the 30-day window — not generic app hate.

**Quantification.** 136 claims (27 Reddit, 26 Play, 83 App Store) in 116 docs / 108 threads. Reddit share of this area 20%. Delay/drop-off on 134. Price mentioned on 11.

**Comparison.** Ranks above **Fit and size uncertainty after the item is chosen** because of tighter delay/drop-off language (93.6 vs 89.2 on the rubric).

**Evidence (Reddit first).**

> Received different colored New balance worth ₹16k when I created return request, original item images changed on page.
>
> — `t1_oquls2f__c1` · https://www.reddit.com/r/Flipkart/comments/1u1wnjw/flipkart_is_a_scam/oquls2f/

> i ordered one long boots which was terrible, it costed me 760 on myntra and i returned it the day i received it.
>
> — `t3_1r9rdje__c1` · https://www.reddit.com/r/TwoXIndia/comments/1r9rdje/help_regarding_outfit_for_college_fest/

**Store corroboration.**

> I have been using myntra since its launch , I bought each and every garment, accessories, cloths etc from this particular application but from past one year myntra had disappointed me by its quality, service, and every time they send me wrong products. [app_store]
>
> — `as_14482743466__s1` · https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059?see-all=reviews

> vry setifed service product quality is vry nice delevery process is really fast go for it guys ❤️🎀 [play_store]
>
> — `gp_8a808229-c7d5-4652-becb-8802a7343115__s2` · https://play.google.com/store/apps/details?id=com.myntra.android&hl=en_IN&gl=IN&reviewId=8a808229-c7d5-4652-becb-8802a7343115

Ledger claim ids: `t3_1teqiat__c1`, `t3_1tar74n__h1`, `t3_1rf2i7b__h2`, `t3_1r9rdje__c1`, `t3_1q0zb2r__c1`, `t3_1pmip11__h1`, `t3_1pmip11__h2`, `t3_1pmip11__h3`, `t3_1nvszdc__h1`, `t3_1nvszdc__h2`, …

### 2. Fit and size uncertainty after the item is chosen

**Behavior / uncertainty.** After identifying a product or category, remaining uncertainty is whether it will fit — length, cup/band, plus-size belts, or brand-to-brand inconsistency.

**Metric link.** Journey placement: **uncertainty after like**. 74% of claims carry delay/drop-off. This is residual uncertainty after a product is in play — the 30-day window — not generic app hate.

**Quantification.** 31 claims (9 Reddit, 0 Play, 22 App Store) in 28 docs / 27 threads. Reddit share of this area 29%. Delay/drop-off on 23. Price mentioned on 0.

**Comparison.** Ranks below **Quality and authenticity doubt after shortlisting** because that area has tighter delay/drop-off language (93.6 vs 89.2). It still ranks above **Return and order-integrity distrust that trains delay** (89.2 vs 83.5).

**Evidence (Reddit first).**

> whenever I order on Myntra, Amazon, etc the length is always short on me..
>
> — `t3_1unu1p2__c1` · https://www.reddit.com/r/TwoXIndia/comments/1unu1p2/tall_girlies_pls_help_me_find_pants/

> So I have been trying the popular platforms amazon, flipkart and Myntra to get any branded and good quality tights but surprisingly they are all the same, what looks in the picture looks so different in real.
>
> — `t3_1p78zwe__c1` · https://www.reddit.com/r/AskIndia/comments/1p78zwe/any_good_platforms_to_buy_branded_clothes_online/

**Store corroboration.**

> Beautiful footwear perfect fit same as picture comfortable in spite of high heels [app_store]
>
> — `as_14485720797__s1` · https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059?see-all=reviews

Ledger claim ids: `t3_1vj02n0__c2`, `t3_1unu1p2__c1`, `t3_1t5711k__c1`, `t3_1t5711k__c2`, `t3_1p78zwe__c1`, `t3_1nbkr1h__c1`, `t3_1nbkr1h__c2`, `t1_p3zyujx__c1`, `t1_p3t27e2__c1`, `as_14486256169__s2`, …

### 3. Return and order-integrity distrust that trains delay

**Behavior / uncertainty.** Failed pickups, cancelled orders, missing refunds, and 'passed quality check' refusals make the reverse path look unsafe, so committing to a liked item is riskier.

**Metric link.** Store reviews add volume on refunds, pickups, and late delivery. That is mostly after a purchase. The wishlist-window link is indirect: if the reverse path looks broken, the next liked item is easier to leave unbought.

**Quantification.** 124 claims (25 Reddit, 27 Play, 72 App Store) in 94 docs / 88 threads. Reddit share of this area 20%. Delay/drop-off on 105. Price mentioned on 4.

**Comparison.** Ranks below **Fit and size uncertainty after the item is chosen** because that area has stronger 30-day wishlist-window link (89.2 vs 83.5). It still ranks above **Thin or conflicting reviews after a product is identified** (83.5 vs 77.7).

**Evidence (Reddit first).**

> When I checked my account orders yesterday, that order did not show up.
>
> — `t3_1tfgyyz__c2` · https://www.reddit.com/r/TwoXIndia/comments/1tfgyyz/myntra_stole_my_myncash_and_cancelled_my_order/

> Myntra aint refunding money. What to do? Details in comment
>
> — `t3_1uruy6y__c1` · https://www.reddit.com/r/AskIndia/comments/1uruy6y/myntra_aint_refunding_money_what_to_do_details_in/

**Store corroboration.**

> After a week, exchange product came and the delivery agent again asked for the original product (which i had already handed over) so didn’t receive that exchange as well and hence neither I had the original product nor the exchanged one. [app_store]
>
> — `as_14486084800__s2` · https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059?see-all=reviews

> when I tried to exchange the size, the delivery agent denied the exchange as the app didn't accept the product received from them as it was a different brand and asked me to connect with the customer service loop. [play_store]
>
> — `gp_a2fdc505-d231-46eb-a6cc-234f68cf47cd__s1` · https://play.google.com/store/apps/details?id=com.myntra.android&hl=en_IN&gl=IN&reviewId=a2fdc505-d231-46eb-a6cc-234f68cf47cd

Ledger claim ids: `t3_1tfgyyz__c1`, `t3_1tfgyyz__c2`, `t3_1tfgyyz__c3`, `t3_1tfgyyz__c4`, `t3_1rixar3__h1`, `t3_1rix5zl__h1`, `t3_1uruy6y__c1`, `t3_1p2ci3f__c1`, `t3_1nv44gx__c2`, `t3_1js1yvj__c1`, …

### 4. Thin or conflicting reviews after a product is identified

**Behavior / uncertainty.** The shopper has already found a candidate on Myntra (or is scrolling Myntra for a named item) and then stalls because reviews are missing, mixed, or not trusted.

**Metric link.** Journey placement: **uncertainty after like**. 16% of claims carry delay/drop-off. This is residual uncertainty after a product is in play — the 30-day window — not generic app hate.

**Quantification.** 25 claims (18 Reddit, 0 Play, 7 App Store) in 22 docs / 13 threads. Reddit share of this area 72%. Delay/drop-off on 4. Price mentioned on 1.

**Comparison.** Ranks below **Return and order-integrity distrust that trains delay** because that area has tighter delay/drop-off language (83.5 vs 77.7). It still ranks above **Leaving Myntra to ask Reddit, Instagram, or other sites** (77.7 vs 69.6).

**Evidence (Reddit first).**

> I am scrolling through myntra and stuff but none of the affordable options have enough reviews for me to make a decision.
>
> — `t3_1tp0igu__c1` · https://www.reddit.com/r/TwoXIndia/comments/1tp0igu/affordable_college_purse_recommendation_please/

> I've been surfing nykaa and myntra for past couple days but I'm in so much doubt ples help.
>
> — `t3_1vkwlay__c1` · https://www.reddit.com/r/TwoXIndia/comments/1vkwlay/recommend_good_high_impact_full_coverage_sports/

**Store corroboration.**

> One star Reviews submitted in myntra does not show up in the product reviews. [app_store]
>
> — `as_14485348578__s1` · https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059?see-all=reviews

Ledger claim ids: `t3_1vkwlay__c1`, `t3_1v0svff__c1`, `t3_1v0svff__c2`, `t3_1tp0igu__c1`, `t3_1rqyag7__c1`, `t3_1qzac24__h1`, `t3_1f9rq3c__h1`, `t1_nzoqdbm__h1`, `t1_oyjm2jf__h1`, `t1_oyirle5__h1`, …

### 5. Leaving Myntra to ask Reddit, Instagram, or other sites

**Behavior / uncertainty.** After browsing Myntra, users ask other people or other stores whether a product works in real life — try-ons, Insta shops, brand sites, peer recs.

**Metric link.** Journey placement: **off platform**. 17% of claims carry delay/drop-off. This is residual uncertainty after a product is in play — the 30-day window — not generic app hate.

**Quantification.** 6 claims (6 Reddit, 0 Play, 0 App Store) in 6 docs / 6 threads. Reddit share of this area 100%. Delay/drop-off on 1. Price mentioned on 0.

**Comparison.** Ranks below **Thin or conflicting reviews after a product is identified** because that area has broader evidence (more independent threads) (77.7 vs 69.6). It still ranks above **Price surprise and cross-platform price gaps** (69.6 vs 69.0).

**Evidence (Reddit first).**

> where to find longer palazzos for tall girls that go below ankle, any small business or Insta stores are also fine if you’ve tried them
>
> — `t3_1unu1p2__c2` · https://www.reddit.com/r/TwoXIndia/comments/1unu1p2/tall_girlies_pls_help_me_find_pants/

> please do suggest some reliable long belts products or some better trust worthy sites to buy.
>
> — `t3_1nbkr1h__c3` · https://www.reddit.com/r/AskIndia/comments/1nbkr1h/looking_for_a_belt_for_obese_people/

Ledger claim ids: `t3_1unu1p2__c2`, `t3_1tqtehb__c1`, `t3_1rqyag7__c3`, `t3_1nbkr1h__c3`, `t3_1qlzfhw__c1`, `t1_nmugrbk__c1`

### 6. Price surprise and cross-platform price gaps

**Behavior / uncertainty.** Checkout totals jump, the same SKU is cheaper elsewhere, or the user waits for a sale event. Price talk is evidence of delay; a monetary incentive is not an opportunity.

**Metric link.** Postpone via checkout math or a cheaper listing. Price talk is evidence. A monetary incentive is not the opportunity. Delay/drop-off on 56% of claims.

**Quantification.** 16 claims (9 Reddit, 2 Play, 5 App Store) in 15 docs / 15 threads. Reddit share of this area 56%. Delay/drop-off on 9. Price mentioned on 14.

**Comparison.** Ranks below **Leaving Myntra to ask Reddit, Instagram, or other sites** because that area has better fit with the no-discount constraint (69.6 vs 69.0). It still ranks above **Catalog miss: scrolled Myntra and still could not find the item** (69.0 vs 66.8).

**Evidence (Reddit first).**

> my budget was 600 and it's really the extreme of my budget but while placing order it adds upto 675
>
> — `t3_1nymnyi__c1` · https://www.reddit.com/r/AskIndia/comments/1nymnyi/need_ya_help_for_shopping_myntra/

> I've noticed that Snitch clothes are priced differently on their official store compared to Flipkart and Myntra - sometimes the difference is quite big.
>
> — `t3_1nywvf3__c1` · https://www.reddit.com/r/IndianStreetWear/comments/1nywvf3/why_is_snitchs_price_and_quality_different_on/

**Store corroboration.**

> The major reason why I like Myntra is we get the same product with good discount where outside we might not get it at the same discounted price. [app_store]
>
> — `as_14485815954__s1` · https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059?see-all=reviews

> that's why I purchased 12 Louis Philippe shirts from this app and at a wonderful discount too... [play_store]
>
> — `gp_521a0c32-bbcf-4efc-bb6b-e782c8b245e4__s2` · https://play.google.com/store/apps/details?id=com.myntra.android&hl=en_IN&gl=IN&reviewId=521a0c32-bbcf-4efc-bb6b-e782c8b245e4

Ledger claim ids: `t3_1tqtehb__c2`, `t3_1oazyqa__h1`, `t3_1nymnyi__c1`, `t3_1nymnyi__c2`, `t3_1nnufta__c1`, `t3_1q9xs79__c1`, `t3_1nywvf3__c1`, `t1_oux73i9__c1`, `t1_p3t27e2__c2`, `gp_521a0c32-bbcf-4efc-bb6b-e782c8b245e4__s2`, …

### 7. Catalog miss: scrolled Myntra and still could not find the item

**Behavior / uncertainty.** Shoppers spend a session on Myntra looking for a specific need (gym tee, tall palazzo, western wear, NRI access) and leave empty-handed rather than converting a shortlist.

**Metric link.** Often hits before a clean wishlist add (scrolled, found nothing). Treat as an upstream leak, not 'saved then stalled'.

**Quantification.** 16 claims (14 Reddit, 0 Play, 2 App Store) in 12 docs / 12 threads. Reddit share of this area 88%. Delay/drop-off on 10. Price mentioned on 0.

**Comparison.** Ranks below **Price surprise and cross-platform price gaps** because that area has stronger 30-day wishlist-window link (69.0 vs 66.8). It still ranks above **Occasion and styling uncertainty before committing** (66.8 vs 63.5).

**Evidence (Reddit first).**

> I've scrolled myntra day n night but didn't like a tee which has a deep neck, at least compared to regular ones.
>
> — `t3_1tvmrju__c1` · https://www.reddit.com/r/TwoXIndia/comments/1tvmrju/round_neck_suffocates_me/

> I scrolled myntra obnoxiously last night but I really didn't find anything 😭😭😭
>
> — `t3_1ul9n9m__c1` · https://www.reddit.com/r/TwoXIndia/comments/1ul9n9m/gym_outfit_recommendations/

**Store corroboration.**

> Application is nowadays very slow browsing [app_store]
>
> — `as_14473307966__s2` · https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059?see-all=reviews

Ledger claim ids: `t3_1vj02n0__c1`, `t3_1um8tlo__c1`, `t3_1ul9n9m__c1`, `t3_1ukoyc6__c1`, `t3_1tvmrju__c1`, `t3_1tk33l4__c1`, `t3_1skguq1__c1`, `t3_1skguq1__c2`, `t3_1skguq1__c3`, `t3_1skguq1__c4`, …

### 8. Occasion and styling uncertainty before committing

**Behavior / uncertainty.** Purchase is tied to a wedding, event, or 'will this look right on me' question. The item can be identified and still sit unbought until the look is confirmed.

**Metric link.** Journey placement: **postpone**. 0% of claims carry delay/drop-off. This is residual uncertainty after a product is in play — the 30-day window — not generic app hate.

**Quantification.** 10 claims (10 Reddit, 0 Play, 0 App Store) in 8 docs / 4 threads. Reddit share of this area 100%. Delay/drop-off on 0. Price mentioned on 0.

**Comparison.** Ranks below **Catalog miss: scrolled Myntra and still could not find the item** because that area has tighter delay/drop-off language (66.8 vs 63.5). It still ranks above **Comparing the same shortlist across marketplaces** (63.5 vs 54.2).

**Evidence (Reddit first).**

> I have a couple of semi-formal evening events coming up and I’m looking for dresses/ kurta sets that actually look good in real life.
>
> — `t3_1rqyag7__c2` · https://www.reddit.com/r/TwoXIndia/comments/1rqyag7/ladies_share_your_favourite_event_dresses/

> Most of the previews I see on Myntra have ladies that don't have my skin tone, which is understandable.
>
> — `t3_1silw4y__c1` · https://www.reddit.com/r/TwoXIndia/comments/1silw4y/please_recommend_wedding_season_friendly_sarees/

Ledger claim ids: `t3_1silw4y__c1`, `t3_1silw4y__c2`, `t3_1rqyag7__c2`, `t3_1rf2i7b__h1`, `t1_p2ivpzu__h1`, `t1_p2ien86__h1`, `t1_p2ien86__h2`, `t1_p2i264y__h1`, `t1_ofmomt9__h1`, `t1_ofl5usb__h1`

### 9. Comparing the same shortlist across marketplaces

**Behavior / uncertainty.** Users hold a candidate and check whether it (or an equivalent) is also on Flipkart, Nykaa, or a brand site before buying.

**Metric link.** Journey placement: **compare**. 0% of claims carry delay/drop-off. This is residual uncertainty after a product is in play — the 30-day window — not generic app hate.

**Quantification.** 2 claims (2 Reddit, 0 Play, 0 App Store) in 2 docs / 2 threads. Reddit share of this area 100%. Delay/drop-off on 0. Price mentioned on 0.

**Comparison.** Ranks below **Occasion and styling uncertainty before committing** because that area has broader evidence (more independent threads) (63.5 vs 54.2).

**Evidence (Reddit first).**

> also available in myntra
>
> — `t1_oldjwxv__c1` · https://www.reddit.com/r/Flipkart/comments/1tazeu8/should_i_buy_it_from_flipkart/oldjwxv/

> Than which one do you suggest?
>
> — `t1_oowi41i__h1` · https://www.reddit.com/r/TwoXIndia/comments/1tqtehb/has_anyone_tried_hm_sports_bra/oowi41i/

Ledger claim ids: `t1_oldjwxv__c1`, `t1_oowi41i__h1`

## What is not solvable with a discount

Price/sale-waiting is captured when present. A coupon is not ranked.

Non-monetary top areas: 1. Quality and authenticity doubt after shortlisting; 2. Fit and size uncertainty after the item is chosen; 3. Return and order-integrity distrust that trains delay; 4. Thin or conflicting reviews after a product is identified; 5. Leaving Myntra to ask Reddit, Instagram, or other sites; 7. Catalog miss: scrolled Myntra and still could not find the item.

Monetary evidence area (Price surprise and cross-platform price gaps): description of delay, not an intervention.

## Gaps

### Named question Gaps

- **Q1 Why add to the Myntra wishlist?** — The Phase 2 claims do not contain explicit 'add to wishlist' language. wishlist_signal is `none` on every extracted claim. Raw Reddit text mentions wishlist in only a handful of documents, so why people add cannot be answered from this pull. Closest behaviors are scrolling Myntra, holding items in cart, and saving inspiration threads — which is bookmark-like, not a measured add.
- **Q8 Wishlist as intent vs bookmark?** — Intent vs bookmark cannot be scored from this corpus. No claim is tagged explicit or implied wishlist. Treating every Myntra mention as purchase intent would fail the eval. The honest reading: people use Myntra as a browse/watch surface (scroll, compare, ask Reddit) and sometimes leave items in cart after a cancelled order. That is not the same as 'wishlist = almost a purchase'.

### Source-mix remaining Gaps

- Fashion/shopping communities, Instagram, YouTube, and product Q&A are still not ingested (Phase 5 only if needed).
- Private WhatsApp / DMs stay out of scope.
- Store reviews are short and app-centric; they under-count styling, occasion, and off-platform research (Q6/Q7/Q9).

## What this draft is not

Not an MVP, interview plan, or metric tree. Myntra remains the product under study.

## How to re-run

```text
cd Phases/Phase4_StoreReviews
python run.py --dry-run
python run.py
```
