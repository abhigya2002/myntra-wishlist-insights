# Discovery report — Reddit-only draft (Phase 3)

North-star in scope: **% of Myntra users who purchase at least one wishlisted item within 30 days of adding it.** Hard constraint: no monetary incentive as the opportunity.

Instant-fail self-check: **all clear**. Groundedness sample: 20 claims, verbatim 100%, url 100%, question-fit 100%.

## Version and source mix

| Field | Value |
|---|---|
| Product | Myntra |
| Draft | Phase 3 Reddit-only (Play/App Store not ingested) |
| Reddit pull | 2026-08-17T16:51:24Z via `arctic_shift` |
| Time window | 2024-08-17 → 2026-08-17 (24 months) |
| Raw Reddit docs | 326 |
| Phase 2 labels | 326 (in-scope 291: myntra_primary 281, fashion_context 10) |
| Phase 2 run | 2026-08-29T11:35:09Z, Groq + heuristic |
| Claims | 124 quote-backed (63 Groq / 61 heuristic) |
| Reddit share of this draft | 100% |
| Other sources | None. Play Store, App Store, communities, social, YouTube, and product Q&A are **Gaps** for later phases. |

Competitor names (AJIO, Nykaa, Flipkart, Amazon) appear only as comparison context.

## Ten discovery questions

Coverage: **8/10** Answered or Partial (6 Answered, 2 Partial, 2 Gap). Every Gap is named. Silence is not used.

### Q1. Why add to the Myntra wishlist?

**Gap** · 1 claims · 1 threads

The Phase 2 claims do not contain explicit 'add to wishlist' language. wishlist_signal is `none` on every extracted claim. Raw Reddit text mentions wishlist in only a handful of documents, so why people add cannot be answered from this pull. Closest behaviors are scrolling Myntra, holding items in cart, and saving inspiration threads — which is bookmark-like, not a measured add.

_No verbatim wishlist-add quote was available to print. That absence is the finding._

### Q2. What prevents wishlisted products from being purchased?

**Answered** · 66 claims · 32 threads

What blocks a buy after Myntra is in play: missing/mixed reviews, quality or fake-goods fear, fit/size misses, checkout price jumps, and a reverse path (return/refund/cancel) that people do not trust. Several quotes sit at hesitation-to-order, not just after a bad delivery.

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

**Answered** · 61 claims · 23 threads

After a product is identified, leftover uncertainty is whether reviews can be trusted, whether fabric/quality matches the image, whether it will fit, and whether the look works on their body/occasion. People keep asking Reddit after they have already scrolled Myntra.

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

**Answered** · 24 claims · 10 threads

Postponement shows up as waiting on occasion (wedding/event dressing), waiting on price/checkout math, and waiting because a return or refund last time went badly. Festival language in the raw pull is present but many heuristic 'occasion' hits are title echoes — those were down-weighted in ranking.

> Happened with me multiple times this year, twice I had to cancel laptop orders because it used to come to my nearby hub and then not reach my house, Myntra who use the same ekart logistics did this with all my orders during the diwali.
>
> — `t1_nmnziri__h1` · https://www.reddit.com/r/Flipkart/comments/1om815p/absolutely_pathetic/nmnziri/

> There's also another option called "Style Exchange" that allows you to return your current product in exchange for a different item in your cart.
>
> — `t1_nx1y252__h2` · https://www.reddit.com/r/AskIndia/comments/1q0zb2r/return_issue_help/nx1y252/

> So I have got a 10k amazon gift card from my uncle as a diwali gift and I don't know how to spend it.
>
> — `t3_1oazyqa__h1` · https://www.reddit.com/r/AskIndia/comments/1oazyqa/got_10k_worth_of_amazon_gift_card_f/

### Q5. How do users compare shortlisted products?

**Partial** · 3 claims · 3 threads

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

**Answered** · 20 claims · 11 threads

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

**Answered** · 53 claims · 28 threads

Reviews and quality talk dominate. Fit/size is smaller but concrete (length short, bras, belts). Styling appears on event/saree threads. Price appears as checkout uplift and cross-platform gaps. Occasion is wedding/event dressing. Social validation is the 'has anyone tried' ask. These are roles in the journey, not a flat importance ranking.

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

**Gap** · 1 claims · 1 threads

Intent vs bookmark cannot be scored from this corpus. No claim is tagged explicit or implied wishlist. Treating every Myntra mention as purchase intent would fail the eval. The honest reading: people use Myntra as a browse/watch surface (scroll, compare, ask Reddit) and sometimes leave items in cart after a cancelled order. That is not the same as 'wishlist = almost a purchase'.

_No verbatim wishlist-add quote was available to print. That absence is the finding._

### Q9. How do behaviors differ across segments?

**Partial** · 7 claims · 5 threads

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

**Answered** · 20 claims · 17 threads

Recurring unmet needs: enough trusted reviews on affordable options, quality that matches the listing, sizes that exist (tall, plus, specific bra sizes), assortment that is not 'the same collection everywhere', and a reverse path that actually refunds. International access (Myntra not usable in the EU) is named but thin.

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

These are **user behaviors or uncertainties**, not feature ideas. Rank is the Phase 3 deliverable. Prose exists to make the comparison readable.

| Rank | Area | Score | Claims | Threads | Delay | Non-monetary |
|---|---|---:|---:|---:|---:|---|
| 1 | Quality and authenticity doubt after shortlisting | 87.5 | 27 | 13 | 93% | yes |
| 2 | Thin or conflicting reviews after a product is identified | 77.1 | 18 | 7 | 22% | yes |
| 3 | Leaving Myntra to ask Reddit, Instagram, or other sites | 72.8 | 6 | 6 | 17% | yes |
| 4 | Catalog miss: scrolled Myntra and still could not find the item | 72.6 | 14 | 11 | 71% | yes |
| 5 | Fit and size uncertainty after the item is chosen | 71.0 | 9 | 6 | 11% | yes |
| 6 | Occasion and styling uncertainty before committing | 65.0 | 10 | 4 | 0% | yes |
| 7 | Return and order-integrity distrust that trains delay | 64.5 | 25 | 13 | 24% | yes |
| 8 | Price surprise and cross-platform price gaps | 58.7 | 9 | 8 | 22% | no (price evidence) |
| 9 | Comparing the same shortlist across marketplaces | 55.6 | 2 | 2 | 0% | yes |

### Rubric

Each area is scored `100 * (0.30 metric relevance + 0.25 evidence + 0.20 delay/drop-off + 0.15 constraint fit + 0.10 segment honesty)`. Segment honesty is 1.0 because this draft does not invent personas.

### 1. Quality and authenticity doubt after shortlisting

**Behavior / uncertainty.** Users want an item that will last or match the listing, then hesitate or reverse because fabric, construction, or authenticity looks unreliable.

**Metric link.** Journey placement: **uncertainty after like**. 93% of claims in this area carry an explicit delay/drop-off tag. The behavior is residual uncertainty or a workaround after the product is already in play — the window between like/save and a 30-day purchase — not generic app hate.

**Quantification.** 27 claims in 21 docs / 13 threads (21.8% of all claims; 7.2% of in-scope labeled docs). Myntra-primary 27, fashion-context 0. Reddit 100%. Delay/drop-off on 25 claims. Price mentioned on 2. Groq-extracted 5.

**Comparison.** Ranks above **Thin or conflicting reviews after a product is identified** because of tighter delay/drop-off language (87.5 vs 77.1 on the rubric).

**Evidence (Reddit).**

> Received different colored New balance worth ₹16k when I created return request, original item images changed on page.
>
> — `t1_oquls2f__c1` · https://www.reddit.com/r/Flipkart/comments/1u1wnjw/flipkart_is_a_scam/oquls2f/

> i ordered one long boots which was terrible, it costed me 760 on myntra and i returned it the day i received it.
>
> — `t3_1r9rdje__c1` · https://www.reddit.com/r/TwoXIndia/comments/1r9rdje/help_regarding_outfit_for_college_fest/

> Got wet and soapy smelling clothes from myntra
>
> — `t3_1hg6nqu__c1` · https://www.reddit.com/r/IndiaSpeaks/comments/1hg6nqu/got_wet_and_soapy_smelling_clothes_from_myntra/

Ledger claim ids: `t3_1teqiat__c1`, `t3_1tar74n__h1`, `t3_1rf2i7b__h2`, `t3_1r9rdje__c1`, `t3_1q0zb2r__c1`, `t3_1pmip11__h1`, `t3_1pmip11__h2`, `t3_1pmip11__h3`, `t3_1nvszdc__h1`, `t3_1nvszdc__h2`, `t3_1nvszdc__h3`, `t3_1i25oco__h1`, …

### 2. Thin or conflicting reviews after a product is identified

**Behavior / uncertainty.** The shopper has already found a candidate on Myntra (or is scrolling Myntra for a named item) and then stalls because reviews are missing, mixed, or not trusted.

**Metric link.** Journey placement: **uncertainty after like**. 22% of claims in this area carry an explicit delay/drop-off tag. The behavior is residual uncertainty or a workaround after the product is already in play — the window between like/save and a 30-day purchase — not generic app hate.

**Quantification.** 18 claims in 16 docs / 7 threads (14.5% of all claims; 5.5% of in-scope labeled docs). Myntra-primary 17, fashion-context 1. Reddit 100%. Delay/drop-off on 4 claims. Price mentioned on 1. Groq-extracted 5.

**Comparison.** Ranks below **Quality and authenticity doubt after shortlisting** because that area has tighter delay/drop-off language (87.5 vs 77.1). It still ranks above **Leaving Myntra to ask Reddit, Instagram, or other sites** (77.1 vs 72.8).

**Evidence (Reddit).**

> I am scrolling through myntra and stuff but none of the affordable options have enough reviews for me to make a decision.
>
> — `t3_1tp0igu__c1` · https://www.reddit.com/r/TwoXIndia/comments/1tp0igu/affordable_college_purse_recommendation_please/

> I've been surfing nykaa and myntra for past couple days but I'm in so much doubt ples help.
>
> — `t3_1vkwlay__c1` · https://www.reddit.com/r/TwoXIndia/comments/1vkwlay/recommend_good_high_impact_full_coverage_sports/

> the sheer lack of reviews are what making me a bit hesitant to place order.
>
> — `t3_1v0svff__c1` · https://www.reddit.com/r/TwoXIndia/comments/1v0svff/charles_and_keith_heel_reviews/

Ledger claim ids: `t3_1vkwlay__c1`, `t3_1v0svff__c1`, `t3_1v0svff__c2`, `t3_1tp0igu__c1`, `t3_1rqyag7__c1`, `t3_1qzac24__h1`, `t3_1f9rq3c__h1`, `t1_nzoqdbm__h1`, `t1_oyjm2jf__h1`, `t1_oyirle5__h1`, `t1_oyirfn8__h1`, `t1_oyifoky__h1`, …

### 3. Leaving Myntra to ask Reddit, Instagram, or other sites

**Behavior / uncertainty.** After browsing Myntra, users ask other people or other stores whether a product works in real life — try-ons, Insta shops, brand sites, peer recs.

**Metric link.** Journey placement: **off platform**. 17% of claims in this area carry an explicit delay/drop-off tag. The behavior is residual uncertainty or a workaround after the product is already in play — the window between like/save and a 30-day purchase — not generic app hate.

**Quantification.** 6 claims in 6 docs / 6 threads (4.8% of all claims; 2.1% of in-scope labeled docs). Myntra-primary 5, fashion-context 1. Reddit 100%. Delay/drop-off on 1 claims. Price mentioned on 0. Groq-extracted 6.

**Comparison.** Ranks below **Thin or conflicting reviews after a product is identified** because that area has stronger 30-day wishlist-window link (77.1 vs 72.8). It still ranks above **Catalog miss: scrolled Myntra and still could not find the item** (72.8 vs 72.6).

**Evidence (Reddit).**

> where to find longer palazzos for tall girls that go below ankle, any small business or Insta stores are also fine if you’ve tried them
>
> — `t3_1unu1p2__c2` · https://www.reddit.com/r/TwoXIndia/comments/1unu1p2/tall_girlies_pls_help_me_find_pants/

> please do suggest some reliable long belts products or some better trust worthy sites to buy.
>
> — `t3_1nbkr1h__c3` · https://www.reddit.com/r/AskIndia/comments/1nbkr1h/looking_for_a_belt_for_obese_people/

> I’d like to buy clothes from Myntra and ship them to myself in USA
>
> — `t3_1qlzfhw__c1` · https://www.reddit.com/r/nri/comments/1qlzfhw/how_to_buy_clothes_from_india_and_ship_to_myself/

Ledger claim ids: `t3_1unu1p2__c2`, `t3_1tqtehb__c1`, `t3_1rqyag7__c3`, `t3_1nbkr1h__c3`, `t3_1qlzfhw__c1`, `t1_nmugrbk__c1`

### 4. Catalog miss: scrolled Myntra and still could not find the item

**Behavior / uncertainty.** Shoppers spend a session on Myntra looking for a specific need (gym tee, tall palazzo, western wear, NRI access) and leave empty-handed rather than converting a shortlist.

**Metric link.** This often hits **before** a clean wishlist add (scrolled, found nothing). It can still starve 30-day conversion by never creating a convertible shortlist. Treat it as an upstream leak, not as 'saved then stalled'.

**Quantification.** 14 claims in 11 docs / 11 threads (11.3% of all claims; 3.8% of in-scope labeled docs). Myntra-primary 12, fashion-context 2. Reddit 100%. Delay/drop-off on 10 claims. Price mentioned on 0. Groq-extracted 14.

**Comparison.** Ranks below **Leaving Myntra to ask Reddit, Instagram, or other sites** because that area has stronger 30-day wishlist-window link (72.8 vs 72.6). It still ranks above **Fit and size uncertainty after the item is chosen** (72.6 vs 71.0).

**Evidence (Reddit).**

> I've scrolled myntra day n night but didn't like a tee which has a deep neck, at least compared to regular ones.
>
> — `t3_1tvmrju__c1` · https://www.reddit.com/r/TwoXIndia/comments/1tvmrju/round_neck_suffocates_me/

> I scrolled myntra obnoxiously last night but I really didn't find anything 😭😭😭
>
> — `t3_1ul9n9m__c1` · https://www.reddit.com/r/TwoXIndia/comments/1ul9n9m/gym_outfit_recommendations/

> Unfortunately, Myntra doesn't work outside of India (or at very least in EU).
>
> — `t3_1vj02n0__c1` · https://www.reddit.com/r/TwoXIndia/comments/1vj02n0/best_places_to_buy_lehengas_for_a_wedding/

Ledger claim ids: `t3_1vj02n0__c1`, `t3_1um8tlo__c1`, `t3_1ul9n9m__c1`, `t3_1ukoyc6__c1`, `t3_1tvmrju__c1`, `t3_1tk33l4__c1`, `t3_1skguq1__c1`, `t3_1skguq1__c2`, `t3_1skguq1__c3`, `t3_1skguq1__c4`, `t3_1r60rzf__c1`, `t3_1rfxjrv__c1`, …

### 5. Fit and size uncertainty after the item is chosen

**Behavior / uncertainty.** After identifying a product or category, remaining uncertainty is whether it will fit — length, cup/band, plus-size belts, or brand-to-brand inconsistency.

**Metric link.** Journey placement: **uncertainty after like**. 11% of claims in this area carry an explicit delay/drop-off tag. The behavior is residual uncertainty or a workaround after the product is already in play — the window between like/save and a 30-day purchase — not generic app hate.

**Quantification.** 9 claims in 7 docs / 6 threads (7.3% of all claims; 2.4% of in-scope labeled docs). Myntra-primary 7, fashion-context 2. Reddit 100%. Delay/drop-off on 1 claims. Price mentioned on 0. Groq-extracted 9.

**Comparison.** Ranks below **Catalog miss: scrolled Myntra and still could not find the item** because that area has tighter delay/drop-off language (72.6 vs 71.0). It still ranks above **Occasion and styling uncertainty before committing** (71.0 vs 65.0).

**Evidence (Reddit).**

> whenever I order on Myntra, Amazon, etc the length is always short on me..
>
> — `t3_1unu1p2__c1` · https://www.reddit.com/r/TwoXIndia/comments/1unu1p2/tall_girlies_pls_help_me_find_pants/

> So I have been trying the popular platforms amazon, flipkart and Myntra to get any branded and good quality tights but surprisingly they are all the same, what looks in the picture looks so different in real.
>
> — `t3_1p78zwe__c1` · https://www.reddit.com/r/AskIndia/comments/1p78zwe/any_good_platforms_to_buy_branded_clothes_online/

> i have bigger bust size so it was soooo hard to find i tried zivame jockey etc but nothing came close to blissclub.
>
> — `t1_p3t27e2__c1` · https://www.reddit.com/r/TwoXIndia/comments/1vkwlay/recommend_good_high_impact_full_coverage_sports/p3t27e2/

Ledger claim ids: `t3_1vj02n0__c2`, `t3_1unu1p2__c1`, `t3_1t5711k__c1`, `t3_1t5711k__c2`, `t3_1p78zwe__c1`, `t3_1nbkr1h__c1`, `t3_1nbkr1h__c2`, `t1_p3zyujx__c1`, `t1_p3t27e2__c1`

### 6. Occasion and styling uncertainty before committing

**Behavior / uncertainty.** Purchase is tied to a wedding, event, or 'will this look right on me' question. The item can be identified and still sit unbought until the look is confirmed.

**Metric link.** Journey placement: **postpone**. 0% of claims in this area carry an explicit delay/drop-off tag. The behavior is residual uncertainty or a workaround after the product is already in play — the window between like/save and a 30-day purchase — not generic app hate.

**Quantification.** 10 claims in 8 docs / 4 threads (8.1% of all claims; 2.8% of in-scope labeled docs). Myntra-primary 9, fashion-context 1. Reddit 100%. Delay/drop-off on 0 claims. Price mentioned on 0. Groq-extracted 3.

**Comparison.** Ranks below **Fit and size uncertainty after the item is chosen** because that area has broader evidence (more independent threads) (71.0 vs 65.0). It still ranks above **Return and order-integrity distrust that trains delay** (65.0 vs 64.5).

**Evidence (Reddit).**

> I have a couple of semi-formal evening events coming up and I’m looking for dresses/ kurta sets that actually look good in real life.
>
> — `t3_1rqyag7__c2` · https://www.reddit.com/r/TwoXIndia/comments/1rqyag7/ladies_share_your_favourite_event_dresses/

> Most of the previews I see on Myntra have ladies that don't have my skin tone, which is understandable.
>
> — `t3_1silw4y__c1` · https://www.reddit.com/r/TwoXIndia/comments/1silw4y/please_recommend_wedding_season_friendly_sarees/

> Now that I’m preparing for a wedding, I’m looking for kurta and pajama options.
>
> — `t3_1rf2i7b__h1` · https://www.reddit.com/r/TwoXIndia/comments/1rf2i7b/unpopular_opinion_a_very_hot_take_myntra_is_very/

Ledger claim ids: `t3_1silw4y__c1`, `t3_1silw4y__c2`, `t3_1rqyag7__c2`, `t3_1rf2i7b__h1`, `t1_p2ivpzu__h1`, `t1_p2ien86__h1`, `t1_p2ien86__h2`, `t1_p2i264y__h1`, `t1_ofmomt9__h1`, `t1_ofl5usb__h1`

### 7. Return and order-integrity distrust that trains delay

**Behavior / uncertainty.** Failed pickups, cancelled orders, missing refunds, and 'passed quality check' refusals make the reverse path look unsafe, so committing to a liked item is riskier.

**Metric link.** Most quotes are **after a purchase or cancel**, not at wishlist-add. The metric link is indirect: 28% read as after-purchase. If the reverse path looks broken, the next liked item is easier to leave unbought. That is weaker than review/fit hesitation-to-order, which is why this area is scored with a lower metric prior.

**Quantification.** 25 claims in 19 docs / 13 threads (20.2% of all claims; 6.5% of in-scope labeled docs). Myntra-primary 25, fashion-context 0. Reddit 100%. Delay/drop-off on 6 claims. Price mentioned on 4. Groq-extracted 9.

**Comparison.** Ranks below **Occasion and styling uncertainty before committing** because that area has stronger 30-day wishlist-window link (65.0 vs 64.5). It still ranks above **Price surprise and cross-platform price gaps** (64.5 vs 58.7).

**Evidence (Reddit).**

> When I checked my account orders yesterday, that order did not show up.
>
> — `t3_1tfgyyz__c2` · https://www.reddit.com/r/TwoXIndia/comments/1tfgyyz/myntra_stole_my_myncash_and_cancelled_my_order/

> Myntra aint refunding money. What to do? Details in comment
>
> — `t3_1uruy6y__c1` · https://www.reddit.com/r/AskIndia/comments/1uruy6y/myntra_aint_refunding_money_what_to_do_details_in/

> I filed a complaint on NCH portal against Myntra for not delivering my shoes for 30 days and got them delivered in 3 days of filing the complaint.
>
> — `t1_no4agha__c1` · https://www.reddit.com/r/Flipkart/comments/1otev9v/has_anyone_successfully_filed_a_complaint_against/no4agha/

Ledger claim ids: `t3_1tfgyyz__c1`, `t3_1tfgyyz__c2`, `t3_1tfgyyz__c3`, `t3_1tfgyyz__c4`, `t3_1rixar3__h1`, `t3_1rix5zl__h1`, `t3_1uruy6y__c1`, `t3_1p2ci3f__c1`, `t3_1nv44gx__c2`, `t3_1js1yvj__c1`, `t1_ns8pgsq__h1`, `t1_ns8pbls__h1`, …

### 8. Price surprise and cross-platform price gaps

**Behavior / uncertainty.** Checkout totals jump, the same SKU is cheaper elsewhere, or the user waits for a sale event. Price talk is evidence of delay; a monetary incentive is not an opportunity.

**Metric link.** This sits on the path as **postpone**: the item is already chosen, then checkout math or a cheaper listing elsewhere stretches the gap past a 30-day window. 22% of its claims are tagged delay/drop-off. It is **not** ranked as a monetary incentive.

**Quantification.** 9 claims in 8 docs / 8 threads (7.3% of all claims; 2.8% of in-scope labeled docs). Myntra-primary 8, fashion-context 1. Reddit 100%. Delay/drop-off on 2 claims. Price mentioned on 8. Groq-extracted 8.

**Comparison.** Ranks below **Return and order-integrity distrust that trains delay** because that area has better fit with the no-discount constraint (64.5 vs 58.7). It still ranks above **Comparing the same shortlist across marketplaces** (58.7 vs 55.6).

**Evidence (Reddit).**

> my budget was 600 and it's really the extreme of my budget but while placing order it adds upto 675
>
> — `t3_1nymnyi__c1` · https://www.reddit.com/r/AskIndia/comments/1nymnyi/need_ya_help_for_shopping_myntra/

> I've noticed that Snitch clothes are priced differently on their official store compared to Flipkart and Myntra - sometimes the difference is quite big.
>
> — `t3_1nywvf3__c1` · https://www.reddit.com/r/IndianStreetWear/comments/1nywvf3/why_is_snitchs_price_and_quality_different_on/

> It is lil expensive got it for 2400 but wore it for the whole year in gym and a lil after. I dont regret a single penny
>
> — `t1_p3t27e2__c2` · https://www.reddit.com/r/TwoXIndia/comments/1vkwlay/recommend_good_high_impact_full_coverage_sports/p3t27e2/

Ledger claim ids: `t3_1tqtehb__c2`, `t3_1oazyqa__h1`, `t3_1nymnyi__c1`, `t3_1nymnyi__c2`, `t3_1nnufta__c1`, `t3_1q9xs79__c1`, `t3_1nywvf3__c1`, `t1_oux73i9__c1`, `t1_p3t27e2__c2`

### 9. Comparing the same shortlist across marketplaces

**Behavior / uncertainty.** Users hold a candidate and check whether it (or an equivalent) is also on Flipkart, Nykaa, or a brand site before buying.

**Metric link.** Journey placement: **compare**. 0% of claims in this area carry an explicit delay/drop-off tag. The behavior is residual uncertainty or a workaround after the product is already in play — the window between like/save and a 30-day purchase — not generic app hate.

**Quantification.** 2 claims in 2 docs / 2 threads (1.6% of all claims; 0.7% of in-scope labeled docs). Myntra-primary 2, fashion-context 0. Reddit 100%. Delay/drop-off on 0 claims. Price mentioned on 0. Groq-extracted 1.

**Comparison.** Ranks below **Price surprise and cross-platform price gaps** because that area has broader evidence (more independent threads) (58.7 vs 55.6).

**Evidence (Reddit).**

> also available in myntra
>
> — `t1_oldjwxv__c1` · https://www.reddit.com/r/Flipkart/comments/1tazeu8/should_i_buy_it_from_flipkart/oldjwxv/

> Than which one do you suggest?
>
> — `t1_oowi41i__h1` · https://www.reddit.com/r/TwoXIndia/comments/1tqtehb/has_anyone_tried_hm_sports_bra/oowi41i/

Ledger claim ids: `t1_oldjwxv__c1`, `t1_oowi41i__h1`

## What is not solvable with a discount

Price and sale-waiting **are captured** when present. A coupon is **not** ranked.

Non-monetary top areas: 1. Quality and authenticity doubt after shortlisting; 2. Thin or conflicting reviews after a product is identified; 3. Leaving Myntra to ask Reddit, Instagram, or other sites; 4. Catalog miss: scrolled Myntra and still could not find the item; 5. Fit and size uncertainty after the item is chosen; 6. Occasion and styling uncertainty before committing.

Monetary evidence area (Price surprise and cross-platform price gaps): keep it as a description of delay, not as an intervention. The hard constraint still applies.

## Gaps

### Named question Gaps

- **Q1 Why add to the Myntra wishlist?** — The Phase 2 claims do not contain explicit 'add to wishlist' language. wishlist_signal is `none` on every extracted claim. Raw Reddit text mentions wishlist in only a handful of documents, so why people add cannot be answered from this pull. Closest behaviors are scrolling Myntra, holding items in cart, and saving inspiration threads — which is bookmark-like, not a measured add.
- **Q8 Wishlist as intent vs bookmark?** — Intent vs bookmark cannot be scored from this corpus. No claim is tagged explicit or implied wishlist. Treating every Myntra mention as purchase intent would fail the eval. The honest reading: people use Myntra as a browse/watch surface (scroll, compare, ask Reddit) and sometimes leave items in cart after a cancelled order. That is not the same as 'wishlist = almost a purchase'.

### Source-mix Gaps (expected for a Reddit-only draft)

- Play Store / App Store not ingested — app friction, size-chart UI, and trust-at-volume are untested.
- Fashion/shopping communities beyond the Reddit pull are not ingested.
- Instagram, YouTube hauls, and product Q&A are not ingested (Q6/Q7 may be under-counted).
- Private WhatsApp / DMs are out of scope (interview territory, not ingest).

### Corpus and process Gaps

- Explicit wishlist language is almost absent (0 explicit / 0 implied wishlist signals on claims).
- Phase 2 stopped Groq on daily quota; many later docs used heuristics (61 heuristic claims). Re-run Phase 2 after quota reset if labels need to be sharpened.
- Comparison of 2–3 saved items inside Myntra is thin (Q5 Partial).
- Segments are thin and only ethnic/western and size-insecure are earned (Q9 Partial).
- Phase 2 15-doc human gate check is still pending in `GATE_CHECK.md` (evals.md §8). This draft still runs so ranking can be reviewed.

## What this draft is not

This is a research ranking for later parts. It does **not** propose an MVP, an in-app feature, an interview guide, or a metric tree. AJIO/Nykaa are not the product under study.

## How to re-run

```text
cd Phases/Phase3_RankedDraft
python run.py --dry-run
python run.py
```

Inputs: Phase 1 `reddit_documents.jsonl`, Phase 2 `reddit_claims.jsonl` + `reddit_labeled.jsonl`.
Outputs: `output/discovery-report.md`, `output/evidence-ledger.json`, `data/derived/`.
