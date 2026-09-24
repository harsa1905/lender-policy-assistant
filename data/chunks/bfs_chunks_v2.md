# Branded Financial Services (BFS) — Policy Chunks
#
# source        : bfs
# document      : BFS Broker Product Guide
# effective     : 1 July 2026
# licence       : Australian Credit Licence 392188
# ABN           : 27 004 013 334
# last_updated  : 2026-07-01
# version       : 2.0
#
# metadata      : v2.0 adds structured taxonomy fields (lenders,
#                 borrower_profile, asset_class, doc_type,
#                 loan_size_band, answerable_questions, confidence,
#                 last_verified) aligned to docs/policy_chunks_v2.md
#
# UPDATE INSTRUCTIONS
# ─────────────────────────────────────────────────────────────────
# When BFS publishes a new rate card or policy update:
# 1. Update the affected chunk(s) only — check QuickSell for latest
# 2. Bump `last_updated` and `version` in the file header
# 3. Re-embed only the changed chunks (use chunk_id to identify)
# 4. Do NOT change chunk_id values — they are the stable keys

---

## chunk_id: bfs_customer_tiers
**source:** bfs
**topic:** customer_tiers
**intent:** ELIGIBILITY
**lenders:** BFS
**borrower_profile:** CONSUMER, COMMERCIAL, HIGH_CREDIT, MID_CREDIT, LOW_CREDIT, SUBPRIME, DISCHARGED_BANKRUPT
**asset_class:** MV_NEW, MV_USED, LCV, MOTORBIKE, CARAVAN
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** Which BFS tier does my Experian score qualify for? What deposit is required by tier? What are the auto-decline triggers? What RHI standards apply? What minimum income do non-resident visa holders need for PRIME vs BFS Plus?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** MIN_CREDIT_SCORE, DEPOSIT_REQUIRED
**trigger_words:** customer tier, Ultra Prime, Tier 1, Tier 2, Tier 3, Tier 4, BFS Plus, Experian, CCR score, credit score, eligibility, qualify, deposit required, PRIME, PLUS, visa, non-resident, temporary visa, work visa, visa holder, visa expiry

**Content:**

BFS uses a two-group system (PRIME and PLUS) based on Experian CCR score of the primary borrower or guarantor. BFS is the only lender in this group to serve both commercial AND individual consumer borrowers.

**PRIME Group:**

| Tier | Minimum Experian CCR Score | Notes |
|------|--------------------------|-------|
| Ultra Prime | 960 | Best rates; all products available |
| Tier 1 | 800 | Full product access |
| Tier 2 | 600 | Full product access |
| Tier 3 | 550 | + 20% deposit required |
| Tier 4 | 400 | + 20% deposit required; no commercial used contracts |

Note on Tier 3 and Tier 4: the **20% deposit applies to every application in these tiers** — consumer and commercial, new and used vehicles alike. It is not conditional on contract type. Tier 4's "no commercial used contracts" is a separate, additional restriction (Tier 4 borrowers cannot finance used vehicles on commercial contracts at all); it does **not** narrow or remove the deposit requirement for the applications Tier 4 can do.

**PLUS Group:**

| Tier | Minimum CCR | Notes |
|------|------------|-------|
| BFS Plus | 400 (consumer) / 550 (commercial used) | Passenger & light commercial vehicles only; 12–60 months max term |

**Which group applies:** PRIME (Ultra Prime–Tier 4) is the default product line — a standard applicant with no bankruptcy history and no other special circumstances is assessed under PRIME, using whichever tier their CCR score qualifies for (e.g. a plain CCR 420 consumer applicant is **Tier 4**, not BFS Plus). BFS Plus is a separate, secondary product line for applicants who need its specific accommodations — most notably the discharged-bankrupt pathway below, or an arrears history that would fail PRIME's stricter conduct standard (see Conduct/Arrears table) even though their CCR score alone would meet a PRIME threshold.

**Auto-decline triggers (no resubmission available):**
- All individuals and guarantors CCR < 400 (consumer + commercial new/demo)
- All individuals and guarantors CCR < 550 (commercial used)
- Currently bankrupt
- Consumer net monthly income < $2,318

**Discharged bankrupt pathway (BFS Plus only):**
- 20% deposit required
- More than 12 months since discharge
- No adverse credit history since discharge

**Non-resident visa holders:**
- **PRIME:** minimum income **$100,000** p.a.; loan term must end one month before visa expiry; Low Doc is not available to visa holders.
- **BFS Plus:** minimum income **$50,000** p.a. (the lower bar than PRIME); loan term must end one month before visa expiry.
- Visa holders must be legally able to drive in Australia, including converting to a local licence where required by the state; an international-licence driver needs evidence of insurance at settlement.

**CCR Repayment History (RHI) standards:**

| Tier | Last 3 months | Last 12 months |
|------|--------------|---------------|
| PRIME (Ultra Prime–Tier 2) | No arrears at all | ≤ 30 days in arrears; no financial defaults |
| BFS Plus | ≤ 30 days in arrears | ≤ 60 days in arrears; no financial defaults |

---

## chunk_id: bfs_commercial_rates
**source:** bfs
**topic:** commercial_interest_rates
**intent:** PRICING
**lenders:** BFS
**borrower_profile:** COMMERCIAL, HIGH_CREDIT, MID_CREDIT, LOW_CREDIT
**asset_class:** MV_NEW, MV_USED, LCV
**doc_type:** LOW_DOC, FULL_DOC
**loan_size_band:** ALL
**answerable_questions:** What is the commercial base rate by tier and vehicle age? What is the max broker margin and rate cap? What is the non-asset-backed loading?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** BASE_RATE, RISK_LOADING, PRIVATE_SALE_LOADING
**trigger_words:** commercial rate, commercial loan rate, business loan rate, ABN rate, base rate, new vehicle commercial, used vehicle commercial, 2022 commercial, 2017 commercial, 2016 commercial, commercial pricing, Ultra Prime rate, Tier 1 rate, Tier 2 rate, Tier 3 rate, Tier 4 rate

**Content:**

Commercial pricing shows **base rates**. Broker may add margin up to a maximum of +6% above base, plus applicable loadings below — for PRIME tiers, the combined base + margin + loadings is not capped at 17.15%; that figure is BFS Plus's own flat maximum rate (see below), not a ceiling on PRIME pricing.

| Vehicle Age | Ultra Prime | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|-------------|------------|--------|--------|--------|--------|
| New and Demo | 7.60% | 8.25% | 8.50% | 10.15% | 11.50% |
| Used 2022–2026 | 7.60% | 8.95% | 10.45% | 12.50% | Not available |
| Used 2017–2021 | 7.60% | 10.30% | 11.35% | 12.90% | Not available |
| Used 2016 and older | 9.55% | 11.05% | 11.80% | 13.40% | Not available |

Ultra Prime's base rate is a flat 7.60% covering New/Demo, Used 2022–2026, AND Used 2017–2021 alike -- verified against the source PDF's own vector-line table geometry: there is no dividing line between these three rows in the Ultra Prime column (unlike every other tier's column, which does have dividers there), confirming they're genuinely one merged cell, not three separate values. It only steps up to 9.55% for Used 2016 and older.

Tier 4's "Not available" is likewise one merged cell -- it spans ALL THREE used-vehicle rows (Used 2022–2026, Used 2017–2021, AND Used 2016 and older), not just one of them, matching the general rule below.

**Note:** Tier 4 does not accept commercial used vehicle contracts at all -- only New and Demo (11.50%).

**Commercial rate adjustments:**
- Maximum broker margin above base: **+6%**
- Non-asset backed loading: **+1.85%** (Tier 1–4 only; does not apply to Ultra Prime)
- Private sale loading: **+0.50%**
- Discount of up to **2%** may be applied to the maximum rate

**BFS Plus (commercial):** Maximum rate 17.15% across all vehicle categories.

---

## chunk_id: bfs_consumer_rates
**source:** bfs
**topic:** consumer_interest_rates
**intent:** PRICING
**lenders:** BFS
**borrower_profile:** CONSUMER, HIGH_CREDIT, MID_CREDIT, LOW_CREDIT, SUBPRIME
**asset_class:** MV_NEW, MV_USED, LCV, MOTORBIKE, CARAVAN
**doc_type:** FULL_DOC
**loan_size_band:** ALL
**answerable_questions:** What is the consumer max rate by tier and vehicle age? What loadings and discounts apply? What is the BFS Plus max rate?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** BASE_RATE, RISK_LOADING, PRIVATE_SALE_LOADING
**trigger_words:** consumer rate, personal loan rate, individual rate, personal vehicle rate, not for business, consumer pricing, personal car loan rate, consumer Ultra Prime, consumer Tier 1

**Content:**

Consumer pricing shows **maximum rates** (borrower pays at or below the listed rate). BFS is the only lender in this group with a consumer (personal use) product.

| Vehicle Age | Ultra Prime | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|-------------|------------|--------|--------|--------|--------|
| New and Demo | 9.15% | 9.29% | 10.15% | 11.50% | 12.50% |
| Used 2022–2026 | 9.15% | 9.75% | 10.55% | 12.00% | 13.20% |
| Used 2017–2021 | 9.15% | 10.35% | 11.35% | 12.25% | 13.70% |
| Used 2016 and older | 10.15% | 11.35% | 11.65% | 13.00% | 13.90% |

Ultra Prime's max rate is a single flat 9.15% covering New/Demo through Used 2017–2021 (it only steps up to 10.15% for Used 2016 and older).

**Consumer rate adjustments:**
- Discount of up to **2%** may be applied to the maximum rate
- Non-asset backed loading: **+1.25%** (Tier 1–4 only; does not apply to Ultra Prime)
- Private sale loading: **+0.50%**

**BFS Plus (consumer):** Maximum rate 17.15% across all vehicle categories.

**Best Interest Duty (BID):** Brokers subject to BID obligations must use this guide and pricing in line with those requirements.

---

## chunk_id: bfs_loan_limits_terms
**source:** bfs
**topic:** loan_limits_and_terms
**intent:** LOAN_LIMITS
**lenders:** BFS
**borrower_profile:** CONSUMER, COMMERCIAL, HIGH_CREDIT, MID_CREDIT
**asset_class:** MV_NEW, MV_USED, LCV, MOTORBIKE, CARAVAN
**doc_type:** ALL
**loan_size_band:** SMALL, MEDIUM, LARGE
**answerable_questions:** How much can I borrow (PRIME vs BFS Plus)? What is the high-value loan range? What are the max terms and max vehicle age? What LVR applies?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** MAX_LOAN, MAX_TERM, ASSET_AGE_MAX
**trigger_words:** maximum loan, how much can I borrow, loan limit, $250k, $150k, $100k, $400k, high value loan, loan term, 84 months, vehicle age, maximum vehicle age, 15 years, 7 years

**Content:**

**PRIME (all tiers):**
- Standard loans: $5,000–**$250,000**
- Private sales: $5,000–**$150,000**
- High value loans: **$250,000–$400,000** (Ultra Prime–Tier 2 only; assessed case-by-case; minimum 20% deposit; asset-backed applicants only). "Ultra Prime–Tier 2" is an inclusive range spanning three tiers, not just the Ultra Prime tier alone — per the tier table above (Ultra Prime 960 / Tier 1 800 / Tier 2 600), any applicant scoring **600 or higher** (Ultra Prime, Tier 1, or Tier 2) qualifies for High Value lending. A CCR of 850 (Tier 1) qualifies just as much as a 960.

**BFS Plus:**
- $5,000–**$100,000**

**Loan terms:**
- PRIME: **12–84 months**
- BFS Plus: **12–60 months**
- May be reduced for courier, ride-share or rental vehicles

**Maximum vehicle age:**
- PRIME (terms ≤ 60 months): **15 years** at start of term
- PRIME (terms > 60 months): **7 years** at start of term
- BFS Plus: **15 years** at start of term

**LVR:**
- Maximum **120%** for no-deposit applications
- Glass's Retail Value applied to used vehicles

---

## chunk_id: bfs_balloons
**source:** bfs
**topic:** balloon_payments
**intent:** LOAN_LIMITS
**lenders:** BFS
**borrower_profile:** COMMERCIAL, HIGH_CREDIT, MID_CREDIT
**asset_class:** MV_NEW, MV_USED, LCV
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What balloon percentage can BFS offer? Does balloon availability differ by tier or term? Are BFS Plus or Tier 3/4 deals eligible for a balloon?
**confidence:** high
**last_verified:** 2026-07-29
**policy_fields:** MAX_LOAN
**trigger_words:** balloon, balloon payment, residual, balloon percentage, Ultra Prime balloon, Tier 1 balloon, Tier 2 balloon, Tier 3 balloon, Tier 4 balloon, BFS Plus balloon

**Content:**

Balloon payments (**commercial only**; excludes courier and ride-share deals) are available for Ultra Prime, Tier 1, and Tier 2 — the same shared table applies to all three of those tiers:

| Vehicle Age | 36 Month Term | 48 Month Term | 60 Month Term |
|------------|---------------|---------------|---------------|
| 0–3 years | 50% | 40% | 30% |
| 3–5 years | 30% | 25% | 20% |

**Not available** for: Tier 3, Tier 4, or BFS Plus — no balloon option exists at these tiers/products regardless of vehicle age or term.

---

## chunk_id: bfs_commercial_documentation
**source:** bfs
**topic:** commercial_documentation
**intent:** DOCUMENTATION
**lenders:** BFS
**borrower_profile:** COMMERCIAL, SELF_EMPLOYED, NEW_BUSINESS, VISA_HOLDER
**asset_class:** MV_NEW, MV_USED, LCV
**doc_type:** LOW_DOC, FULL_DOC, NEW_BIZ
**loan_size_band:** SMALL, MEDIUM, LARGE
**answerable_questions:** What documents are required for commercial Low Doc / Full Doc / New Business Ventures? What trading history and deposit apply? What income evidence is needed above $100k?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** DOC_TYPE, MIN_ABN
**trigger_words:** commercial documents, business documents, Low Doc commercial, Full Doc commercial, New Business Ventures, ABN documents, financial declaration, trading history, income evidence, bank statements, financial statements, what do I need for commercial loan

**Content:**

**Three commercial documentation types:**

| | Low Doc | Full Doc | New Business Ventures |
|--|---------|---------|----------------------|
| **Available tiers** | Ultra Prime–Tier 2 only | Ultra Prime–Tier 4, BFS Plus | Ultra Prime–Tier 4 only |
| **Max loan size** | $150k (total exposure) | $250k standard / $400k high value | $100k (total exposure) |
| **Trading history** | 2+ years ABN + GST registered | 12+ months ABN | Less than 12 months ABN |
| **Min deposit** | 0% | 20% for Tier 3 and 4 | 20% for Tier 3 and 4 |

Each "TierA–TierB" entry above is an inclusive range, not a single tier: Low Doc's "Ultra Prime–Tier 2 only" means Ultra Prime, Tier 1, **and** Tier 2 can all use Low Doc (Tier 3 and Tier 4 cannot); Full Doc and New Business Ventures cover every PRIME tier (Ultra Prime through Tier 4).

The **Trading history** row mixes two kinds of threshold, which is easy to read backwards. Low Doc's "2+ years" and Full Doc's "12+ months" are **minimums** — the business must have at least that much history. New Business Ventures' "Less than 12 months ABN" is a **maximum**: it is the product *for* businesses too new to meet the other two. So a **10-month ABN qualifies** for New Business Ventures, and an 18-month ABN does **not** (that business would use Full Doc instead). Never read the "12 months" in the New Business Ventures column as a minimum ABN age the customer has to exceed — a shorter trading history makes a business *more* eligible for this product, not less.

**Income evidence:**

| Type | Low Doc | Full Doc ≤ $100k | Full Doc > $100k | New Business Ventures |
|------|---------|----------------|----------------|----------------------|
| Required | Business Customer Financial Declaration (signed) | 90-day bank statements | 2 years signed externally prepared financials (≤ 18 months old) + management accounts if financials > 18 months old + 90-day bank statements | 90-day bank statements + copy of run contract (couriers) |

**Residency:**
- Low Doc: guarantor must be Australian citizen or permanent resident only
- Full Doc / New Business Ventures: loan term must end one month before visa expiry

**Commercial loans to individuals (ABN holders):**
Vehicle must be confirmed for business use — letter from an accountant or tax returns required.

---

## chunk_id: bfs_consumer_documentation
**source:** bfs
**topic:** consumer_documentation
**intent:** DOCUMENTATION
**lenders:** BFS
**borrower_profile:** CONSUMER, SELF_EMPLOYED
**asset_class:** MV_NEW, MV_USED, LCV, MOTORBIKE, CARAVAN
**doc_type:** FULL_DOC
**loan_size_band:** ALL
**answerable_questions:** What income evidence is required for PAYG / self-employed / rental / pension? How are affordability, board, and mortgage payments assessed? What is needed for settlement?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** DOC_TYPE
**trigger_words:** consumer documents, personal loan documents, PAYG, payslip, rental income, superannuation income, pension, Centrelink, self-employed income, tax return, individual tax return, personal income, spouse income, mortgage payment, affordability, bank statements consumer

**Content:**

Consumer loans are for individuals where the vehicle is for **personal use** (not business use).

**PAYG Income:**
- Most recent payslip including YTD figures
- July/August payslips: a June payslip or annual statement also required
- Casual employment: minimum 3 months with the same employer/agency

**Non-Wage / Salary Income:**

| Type | Required Documents |
|------|-------------------|
| Rental income | Rental income statement or bank statements (shaded to 80%) |
| Superannuation | Super statement or bank statements showing regular credits |
| Benefits / Pensions | Must be ongoing and sustainable; Centrelink statement or statement from administering body |

**Self-Employment Income:**
- Loan ≤ $100k: most recent individual tax return or Notice of Assessment
- Loan > $100k: 2 years signed externally prepared year-end financials (≤ 18 months old) + most recent tax return or Notice of Assessment + management accounts if financials > 18 months old

**Affordability considerations:**

| Item | Rule |
|------|------|
| Spouse income | May be used for splitting joint expenses (individual borrowers only); proof of income + privacy consent required |
| Board expense | Higher of declared or $400/month applied |
| Mortgage payments | Balance must be disclosed; higher of actual payment or calculated over 30 years at RBA cash rate + 3% |
| Capacity buffer | 2.5% buffer of net monthly income required; higher of declared payments or 4% of credit limit per month |

**Standard documentation — For Approval:**
- Evidence of income
- 90-day bank statements via bankstatements.com.au (mandatory for all BFS Plus applications; consumer on request or where required)
- Motorcycles and caravans: invoice must be provided upfront for asset to be loaded in QuickSell

**Standard documentation — For Settlement:**
- All payout documents submitted via QuickSell
- Completion of biometrics (link in approval confirmation)
- Vehicle insured with BFS noted as interested party; insurance details loaded in QuickSell
- Vehicle tax invoice or private sale agreement
- Fully signed loan documents (ink signature or e-sign)

---

## chunk_id: bfs_vehicle_types
**source:** bfs
**topic:** vehicle_types_and_asset_rules
**intent:** ASSET_ELIGIBILITY
**lenders:** BFS
**borrower_profile:** CONSUMER, COMMERCIAL
**asset_class:** MV_NEW, MV_USED, LCV, MOTORBIKE, CARAVAN
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What vehicles can BFS finance? Can I finance a motorcycle / caravan / campervan? What conditions apply to electric motorcycles? Does BFS finance heavy equipment? Can BFS Plus lend in a remote area?
**confidence:** high
**last_verified:** 2026-07-29
**policy_fields:** ASSET_AGE_MAX
**trigger_words:** vehicle types, eligible vehicles, passenger vehicle, light commercial, motorcycle, motorhome, campervan, caravan, camper trailer, Tier 4 vehicle, BFS Plus vehicle, electric motorcycle, ride share vehicle, hire car, what vehicles can be financed, eligible assets BFS

**Content:**

BFS finances **motor vehicles only** (all under 4.5T GVM). No heavy equipment, plant or agriculture. This is a hard ceiling, not a starting point: **any truck, van, or vehicle at or above 4.5 tonnes GVM is outside BFS's eligibility entirely** — including trucks well over 5 or 6 tonnes, which BFS cannot finance under any product or tier. BFS is a lender for lighter vehicles only, not a heavy-truck lender.

**PRIME (Ultra Prime–Tier 3) — accepted vehicles:**
- New, demo and used passenger vehicles
- Light commercial vehicles (< 4.5T GVM)
- Motorcycles
- Motorhomes
- Campervans
- Caravans and camper trailers
- Limited appetite: vehicles used for ride-share, hire and rental (term may be reduced)

**Tier 4:**
- Passenger vehicles and light commercial vehicles only
- No commercial contracts for used vehicles

**BFS Plus:**
- Passenger vehicles and light commercial vehicles only

**Motorcycle additional conditions:**
- Invoice must be provided upfront for the asset to be loaded in QuickSell
- Independent valuation may be required for private sales
- Maximum term: **60 months**; no balloon payments
- Must be registered; on-road 2, 3 or 4 wheels
- Electric motorcycles: accepted if maximum speed > 80 km/h

**Caravan, Campervan, Camper Trailer additional conditions:**
- Invoice must be provided upfront for the asset to be loaded in QuickSell
- Independent valuation may be required for private sales
- Leisure use only (not to be used as primary residence)
- Commercial use requires a letter from an accountant confirming business use

**Remote areas:**
- Defined as "Remote" per ABS 2021 Remoteness Area classification
- Not available in "Very Remote" areas
- Prime: non-asset backed in remote areas requires 20% deposit
- BFS Plus: remote area lending not available at all, under any circumstances (no deposit-based workaround)

---

## chunk_id: bfs_exclusions
**source:** bfs
**topic:** exclusions
**intent:** EXCLUSIONS
**lenders:** BFS
**borrower_profile:** CONSUMER, COMMERCIAL, SUBPRIME, DISCHARGED_BANKRUPT
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** Is this loan purpose excluded (debt consolidation, cash-out, refinance)? What triggers an auto-decline? Are interlock licences accepted? Is a learner licence accepted? What can't Tier 4 / BFS Plus do? Can BFS Plus lend in a remote area?
**confidence:** high
**last_verified:** 2026-07-29
**policy_fields:** PRIVATE_SALE_LOADING
**trigger_words:** excluded, not eligible, debt consolidation, cash raising, top-up loan, sale and buyback, sale and leaseback, mid-term refinance, interlock licence, learner licence, co-borrower, auto decline, bankrupt, current bankrupt, ride share excluded, very remote, remote area, BFS Plus remote

**Content:**

**Excluded loan purposes (all tiers — no exceptions):**
- Debt consolidation
- Cash raising
- Top-up loans
- Sale and buyback
- Sale and leaseback
- Mid-term refinancing

**Auto-decline (no resubmission available):**
- All individuals and guarantors CCR < 400 (consumer + commercial new/demo)
- All individuals and guarantors CCR < 550 (commercial used)
- Currently bankrupt
- Consumer net monthly income < $2,318 per month

**Driver licence exclusions:**
- Licences with interlock conditions: **NOT accepted**
- Australian learner licence: accepted only with a co-borrower, and only for passenger vehicles (not commercial vehicles or motorcycles)

**Geographic exclusions:**
- "Very Remote" areas per ABS 2021 classification: not available (all tiers)
- BFS Plus: remote area lending excluded entirely, even where not "Very Remote" (see bfs_vehicle_types)

**Tier-specific exclusions:**
- Tier 4: no commercial contracts for used vehicles
- BFS Plus: commercial contracts on used vehicles require minimum CCR 550 (not the standard 400 — see bfs_customer_tiers); passenger and light commercial only; no high-value loans; no Low Doc; remote area lending excluded entirely

---

## chunk_id: bfs_private_sales
**source:** bfs
**topic:** private_sales
**intent:** ASSET_ELIGIBILITY
**lenders:** BFS
**borrower_profile:** CONSUMER, COMMERCIAL
**asset_class:** MV_NEW, MV_USED, LCV, MOTORBIKE
**doc_type:** ALL
**loan_size_band:** SMALL, MEDIUM
**answerable_questions:** What is required for a private sale? What rate loading and loan cap apply? What is the private-sale establishment fee?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** PRIVATE_SALE_LOADING
**trigger_words:** private sale, buying from private seller, private vendor, not from dealer, individual seller, private purchase, arm's length, DoxAI, Redbook, vehicle inspection, private sale rate

**Content:**

**Private sale conditions (all tiers):**
- Vehicle inspection report required: DoxAI Asset Verification via DoxAI Portal (preferred) or Redbook
- Must be an arm's length transaction
- Additional requirements: refer to Private Sale requirements document in QuickSell documents library

**Rate loading:** +0.50% on both commercial and consumer rates.

**Loan size limit (private sales):** Maximum $150k (PRIME tiers).

**Establishment fee (private sale):**
- Consumer private sale: $625 (vs $525 standard)
- Commercial private sale: $675 (vs $575 standard)

---

## chunk_id: bfs_fees_and_commission
**source:** bfs
**topic:** fees_and_commission
**intent:** FEES
**lenders:** BFS
**borrower_profile:** CONSUMER, COMMERCIAL
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What establishment / PPSR / account fees apply? What is the early termination fee (consumer vs commercial)? When is commission clawed back?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** BROKERAGE_MAX
**trigger_words:** fees, establishment fee, origination fee, PPSR fee, account maintenance fee, variation fee, statement fee, early termination fee, break fee, clawback, commission, brokerage, refund commission

**Content:**

**Fee schedule:**

| Fee | Amount |
|-----|--------|
| Establishment fee — Consumer | $525 |
| Establishment fee — Consumer Private Sale | $625 |
| Establishment fee — Commercial | $575 |
| Establishment fee — Commercial Private Sale | $675 |
| Origination fee | Max $1,650 (added to loan; paid to introducer) |
| PPSR registration fee | $6 |
| Account maintenance — monthly/quarterly/half-yearly/yearly | $10.00 per month |
| Account maintenance — fortnightly | $4.62 per fortnight |
| Account maintenance — weekly | $2.31 per week |
| Variation fee | $60 per variation |
| Statement fee | $15 per paper statement |
| Early termination admin fee — Consumer | $70 |
| Early termination admin fee — Commercial | $85 |

**Early termination fee — Consumer:**
In addition to the $70 admin fee: $750 minus $12 for each month (or $5.52/fortnight or $2.76/week) that a repayment has been made since the loan date (maximum $750).

**Early termination fee — Commercial:**
In addition to the $85 admin fee: 35% of the amount of interest payable for the remainder of the term, OR 15% if repayment is due to refinancing with BFS. Calculated on request.

**Commission and clawback:**

| Trigger | Action |
|---------|--------|
| Contract terminated or paid in full within **12 months** | 100% of all commissions and incentives refunded to BFS |
| Repossession or loan write-off within **24 months** | 100% of commission refunded to BFS |
| Brokerage | 75% overs net of GST (see calculator in QuickSell) |

