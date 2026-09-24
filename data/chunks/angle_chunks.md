# Angle Finance — Policy Chunks
#
# source        : angle
# documents     : Angle Finance Rate Card (April 2026, Version 02.04.26)
#                 Angle Finance Start-Up Product Flyer (January)
#                 Angle Finance Full Doc — Minimum Requirements Checklist
#                 Angle Finance Prime Movers Product Flyer
# effective     : April 2026 (rate card); product flyers undated unless noted
# licence       : not stated in source documents
# ABN           : not stated in source documents
# last_updated  : 2026-07-09
# version       : 2.0
#
# metadata      : v2.0 adds structured taxonomy fields (lenders,
#                 borrower_profile, asset_class, doc_type,
#                 loan_size_band, answerable_questions, confidence,
#                 last_verified) aligned to docs/policy_chunks_v2.md
#
# UPDATE INSTRUCTIONS
# ─────────────────────────────────────────────────────────────────
# When Angle publishes a new rate card or policy update:
# 1. Update the affected chunk(s) only
# 2. Bump `last_updated` and `version` in the file header
# 3. Re-embed only the changed chunks (use chunk_id to identify)
# 4. Do NOT change chunk_id values — they are the stable keys
#    used by the vector database

---

## chunk_id: angle_doc_types
**source:** angle
**topic:** documentation_tiers
**intent:** DOCUMENTATION
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, SPOUSE_OWNED, ABN_2_4YR, ABN_4_6YR, ABN_OVER_6YR
**asset_class:** MV_NEW, MV_USED, PRIMARY, SECONDARY, TERTIARY
**doc_type:** LOW_DOC, MID_DOC, FULL_DOC
**loan_size_band:** SMALL, MEDIUM, LARGE
**answerable_questions:** What documents does Angle require for Low Doc / Mid Doc / Full Doc? What credit score do I need at each tier? What is the max exposure per doc type? When are ATO portals required?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Angle Low Doc, Angle Mid Doc, Angle Full Doc, Angle documents, Angle checklist, Angle credit score, ATO portal Angle, Angle credit reference, Angle documentation requirements

**Content:**

Angle Finance operates three documentation tiers. Requirements scale with exposure.

**Low Doc and Mid Doc guidelines:**

| Applicant | Low Doc (< $100k) | Low Doc (> $100k – $250k) | Mid Doc (< $500k) |
|-----------|-------------------|---------------------------|-------------------|
| ABN | 2+ years | 2+ years | 2+ years |
| GST registration | Not essential | 1+ years | 1+ years |
| Credit score (Veda 1:1) | 550+ (Corporate & Individual) | Corporate 550+; Individual 600+ | 650+ (Individual & Corporate) |
| Property status | Property backed or Non-Property Owner (spousal property accepted) | Property backed (spousal property accepted) | Property backed (spousal property accepted) |
| Asset types (max finance amount) | Primary & Secondary $100k; Motor Vehicles $100k; Tertiary $50k | Primary & Secondary $250k; Motor Vehicles $200k | Primary & Secondary $500k; Motor Vehicles $250k; Tertiary $250k |
| Credit references | Not essential | Asset Finance Credit Reference or Mortgage Statements | Asset Finance Credit Reference or Mortgage Statements |
| Max EOT — Primary | 25 yrs | 25 yrs | 25 yrs |
| Max EOT — Secondary | 15 yrs | 15 yrs | 15 yrs |
| Max EOT — Tertiary | 10 yrs | Tertiary not applicable | 10 yrs |

Motor Vehicle maximum asset price is $250k.

**Low Doc checklist:**
- 1 form of ID (Driver's Licence or Passport)
- Asset & Liabilities statement
- Credit Reference or Mortgage Statements for $100k+

**Mid Doc checklist:**
- 6 months bank statements. Pre-qualification guidelines:
  - No dishonoured payments for financial obligations (e.g. loan or lease repayments)
  - Maximum of 1 non-financial dishonour
  - Average monthly revenue of $20,000 across the 6-month period
  - Average running balance must be at least 10% of monthly revenue
- ATO Portals for $250k+

**Full Doc checklist:**
- FY2024 + FY2023 accountant-prepared financials
- Commitment Schedule
- ATO Portals for $250k+
- Detailed business background + list of major clients

Deals over $500k refer to the Full Doc checklist on MyHub.

**Full Doc — minimum requirements by transaction size:**

| Requirement | Under $250k | $250k–$500k | $500k–$1m | Over $1m |
|------------|:-----------:|:-----------:|:---------:|:--------:|
| 6 months+ bank statements OR FY2024 + FY2023 accountant-prepared financials | ✓ | — | — | — |
| FY2024 + FY2023 accountant-prepared financials only | — | ✓ | ✓ | ✓ |
| Commitment Schedule | ✓ | ✓ | ✓ | ✓ |
| Current ATO portal statements (last 12 months good payment history) | — | ✓ | ✓ | ✓ |
| Detailed business background + list of major clients | — | ✓ | ✓ | ✓ |
| Aged Debtor + Creditor listing | — | — | ✓ | ✓ |
| Cashflow projections (if available) | — | — | — | ✓ |

Under $250k: bank statements/financials + Commitment Schedule only (no ATO portals or business background). $250k–$500k: financials-only + Commitment Schedule + ATO portals + business background. $500k–$1m: same plus Aged Debtor + Creditor listing. Over $1m: same plus cashflow projections.

---

## chunk_id: angle_400k_low_doc
**source:** angle
**topic:** low_doc_400k_program
**intent:** SPECIAL_PROGRAMS
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, SPOUSE_OWNED, ABN_OVER_6YR
**asset_class:** MV_NEW, MV_USED, PRIMARY, SECONDARY
**doc_type:** LOW_DOC
**loan_size_band:** LARGE
**answerable_questions:** What is Angle's $400k Low Doc program? What credit score and ABN age qualify? Which assets and applicants are excluded? Which lenders count as an accepted credit reference?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Angle $400k Low Doc, 400K Low Doc, Angle big low doc, Angle low doc checklist, Angle proven track record, Angle accepted lender credit reference

**Content:**

Angle Finance offers Low Doc up to $400k for customers with a proven track record.

**$400k Low Doc checklist:**
- 3+ years ABN & GST registered
- Credit score 600+ (Corporate & Individual, Veda 1.1)
- Minimum 12-months Asset Finance Credit Reference (from Angle Finance or a Tier 1 / Tier 2 Asset Finance Provider)
- Max transaction size of $400k
- Property backed — spousal property accepted
- Asset types: Primary & Secondary
- Max EOT: Primary 25 yrs & Secondary 15 yrs
- ATO Portals for $250k+

Motor Vehicle maximum asset price remains unchanged. Multiple vehicles accepted.

**Exclusions from the $400k Low Doc program:**
- Sole traders
- Tertiary assets
- Prime Movers
- Buses

Note: this bare "Buses" exclusion is the ONLY place any of Angle's documentation mentions buses at all. It rules buses out of this specific $400k Low Doc program — it is not a statement that buses are a Primary (or any other) asset category for Angle generally, and must not be read or repeated as one. Don't describe buses as a fundable Angle asset anywhere else based on this line.

**Accepted lenders for the $400k Low Doc credit reference:**
Westpac / Capital Finance, NAB, ANZ, CBA, BOQ, Judo, DLL, Suncorp, Bendigo / Adelaide Bank, Macquarie Bank, Flexi Commercial, Metro Finance, Pepper Money, Toyota Finance.

**Credit reference definitions:**
- Asset finance credit reference: loan running 6 months+, 50%+ of finance amount, and no missed repayments
- Mortgage statements: loan running 6+ months and no missed repayments. Must be in the applicant's name — spouse's mortgage statements are not accepted.

---

## chunk_id: angle_interest_rates
**source:** angle
**topic:** interest_rates
**intent:** PRICING
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, NON_PROPERTY_BACKED
**asset_class:** PRIMARY, SECONDARY, TERTIARY, PRIME_MOVER
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What rate does Angle charge for primary / secondary / tertiary assets by end-of-term age? What is the prime mover rate? What loadings apply? What has no rate loading?
**confidence:** high
**last_verified:** 2026-07-26
**trigger_words:** Angle rate, Angle interest rate, Angle pricing, Angle primary asset rate, Angle secondary rate, Angle tertiary rate, Angle prime mover rate, Angle start-up rate, Angle rate loading, Angle property backed rate

**Content:**

Angle Finance Rate Card, April 2026 (Version 02.04.26). All rates per annum.

**Profile-based headline rates:**

| Profile | Property backed | Non-property backed |
|---------|----------------|---------------------|
| 8+ year ABN, 4+ year GST; primary assets only; new assets (YOM 2023); entity types sole trader, company, trust, partnership; strong credit score | 7.79% | 8.79% |
| 4+ year ABN, 2+ year GST; primary & secondary assets; end of term 10 years; entity types sole trader, company, trust, partnership; strong credit score | 8.29% | 9.29% |

If the client's profile matches one of the two rows in the Profile-based headline rates table above (by ABN/GST age, asset type and age), use that rate and stop there — do not also look up a rate in the Standard rate card below for the same client. The Standard rate card below is the fallback for clients who don't match either headline-profile row, not an alternative to check every time.

**Standard rate card — for 2+ year ABN & 1+ year GST registration, by asset class, property status, and end-of-term (EOT) age:**

| Asset class | Owner status | 10 years (EOT) | 15 years (EOT) | 20 years (EOT) | 25 years (EOT) |
|------------|-------------|---------------|---------------|---------------|---------------|
| Primary assets | Property Owner | 8.39% | 9.65% | 10.65% | 12.65% (NEW) |
| Primary assets | Non-Property Owner | 10.95% | 11.45% | 17.15% | — |
| Secondary assets | Property Owner | 11.35% | 13.35% (NEW) | — | — |
| Secondary assets | Non-Property Owner | 12.15% | — | — | — |
| Tertiary assets | Property Owner | 11.85% | — | — | — |
| Tertiary assets | Non-Property Owner | 17.85% | — | — | — |

Read the row for the correct asset class AND the correct property-owner status — these are two independent rows per asset class, not sub-bands of one row. A non-property-backed client asking about a primary asset at 15yr EOT is 11.45%, not 9.65% (that's the property-owner rate).

**Prime Movers:** starting from 9.39%. A 1% rate loading applies to standard primary asset rates.

**Start-Up rates:**
- < 2 year ABN: 11.35% / 17.35%
- ≥ 2 year ABN, < 1 year / no GST: 11.35% / 17.35%

**No rate loading applies for:**
- Private sales
- Business continuity
- Commission up to 8%
- Property in spouse's name

A+ deals receive priority assessment with an average turnaround time of 2 hours.

**Term-based loading:** 1% rate loading applicable for terms over 60 months. Customer must be property backed to qualify.

---

## chunk_id: angle_loan_structure
**source:** angle
**topic:** loan_structure_and_terms
**intent:** LOAN_LIMITS
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED
**asset_class:** MV_NEW, MV_USED, PRIMARY, SECONDARY, TERTIARY
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What loan terms does Angle offer? What balloon percentages apply by term? What total exposure does my credit score allow? What are the maximum asset ages?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Angle loan term, Angle balloon, Angle residual, Angle exposure, Angle credit score exposure, Angle maximum loan, Angle EOT, Angle end of term

**Content:**

**Loan structure by deal type:**

| Deal type | Standard terms | Primary assets | Primary MV | Balloon refinance |
|-----------|---------------|----------------|-----------|-------------------|
| Terms | 36–60 months | 36–72* months | 36–84* months | 12+ months |

*A 1% rate loading is applicable for terms over 60 months. Customer must be property backed to qualify.

**Maximum balloon by loan term:**

| Loan term | 36 months | 48 months | 60 months | 72 months | 84 months |
|-----------|:---------:|:---------:|:---------:|:---------:|:---------:|
| Max. balloon | 40% | 40% | 30% | — | — |

EOT 25 years primary assets & EOT 15 years secondary assets: 0% balloon only.

**Total exposure — credit score determines total exposure:**
- Credit score 500 = < $150,000
- Credit score 550 = < $250,000
- Credit score 650 = > $250,000

Large ticket deals over $500,000+ have credit score flexibility. Credit scores < 650 can be considered with financial assessment — speak to your BDM to determine if the customer profile qualifies.

**Maximum asset age at end of term:**
- Primary assets: 25 years
- Secondary assets: 15 years
- Tertiary assets: 10 years

**Account conduct with Angle:** For multiple Low Doc deals, the applicant's first loan must have been running with Angle for 6 months with good account conduct. If the loan has been running for less than 6 months and a second Low Doc loan is sought, speak to your BDM.

---

## chunk_id: angle_start_up
**source:** angle
**topic:** start_up_product
**intent:** SPECIAL_PROGRAMS
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL, NEW_BUSINESS, NON_PROPERTY_BACKED
**asset_class:** PRIMARY
**doc_type:** NEW_BIZ
**loan_size_band:** MEDIUM
**answerable_questions:** Can a new business under 2 years ABN get finance from Angle? What is the Start-Up loan limit, deposit and credit score? What bank statements are needed? What qualifying questions apply?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Angle Start-Up, Angle startup, Angle new business, ABN under 2 years Angle, Angle 20% deposit, Angle industry experience, Angle bank statement serviceability

**Content:**

Angle's Start-Up product serves new business owners with an ABN under 2 years.

**Quick qualifying checklist:**
- Business operating minimum 3 months and actively trading
- Loans to a maximum of $150,000, including brokerage
- Minimum credit score (Veda 1:1): 550+
- 20% deposit on all applications
- Previous industry experience required
- Bank statements must demonstrate serviceability

Note: the Rate Card's Start-Up qualifying criteria states a 500+ credit score; the Start-Up flyer states 550+. Confirm the current threshold with Angle where a deal sits near the boundary.

**Bank statement requirements:** Minimum 6 months required, unless the ABN has been trading for less than 6 months.

**Customer eligibility questions** — a customer qualifies when the answer is *yes* to all of the below:
- Can the customer demonstrate an average bank balance over the last 3–6 months equal to at least 10%–20% of the loan amount, excluding ATO refunds, asset sales, business loans, PAYG income and director cash injections?
- Do the customer's bank statements show clean conduct, with no overdraws, dishonours, debt collection payments, superannuation withdrawals or ATO payment arrangements?
- Can the customer provide proof of previous industry experience, such as PAYG employment history, prior work contracts or relevant qualifications?
- Is the customer purchasing a primary asset? Examples include wood chippers, tippers, excavators, ride-on lawn mowers and caravans.

---

## chunk_id: angle_prime_movers
**source:** angle
**topic:** prime_movers_product
**intent:** SPECIAL_PROGRAMS
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, ABN_OVER_6YR
**asset_class:** PRIME_MOVER, PRIMARY
**doc_type:** MID_DOC, FULL_DOC
**loan_size_band:** LARGE
**answerable_questions:** Does Angle finance prime movers? What entity types and ABN age qualify? What rate loading applies? Can I get a fleet credit limit? Is Low Doc available for prime movers?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Angle prime mover, Angle truck fleet, Angle fleet credit limit, prime mover rate Angle, Angle prime mover criteria, Angle no sole trader prime mover

**Content:**

Angle Finance finances Prime Movers, starting from 8.99% (the rate card shows prime movers starting from 9.39%; confirm the current rate with Angle).

**Qualifying criteria:**
- Company & Trust only — no sole traders or individual partnerships
- Minimum 5 years ABN & GST (business continuity — speak to your BDM)
- Strong credit score: 600+
- Maximum asset age: up to EOT 20 years
- Property backed (standard rules apply; spousal property accepted)
- Bank statements or full financial assessment
- Comparable asset finance credit reference required
- A 1% rate loading will apply to standard primary asset rates

**Key features:**
- Ability to apply for a fleet credit limit and draw down additional trucks as required — finance a fleet, not just one truck
- No rate loading for private sales

**Documentation:** Prime Movers can be done under Mid Doc or Full Doc. **Low Doc is not an option**, as bank statements or financials, plus ATO portals, are required.

**Exclusions:** No sole traders or individual partnerships.

---

## chunk_id: angle_property_and_deposits
**source:** angle
**topic:** property_ownership_and_deposits
**intent:** ELIGIBILITY
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, NON_PROPERTY_BACKED, SPOUSE_OWNED
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** Does Angle accept spousal property? What deposit do non-property owners pay? What proof of property ownership is required? How are boarders treated?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Angle property ownership, Angle spousal property, Angle deposit, Angle non-property owner, Angle 20% deposit, Angle rates notice, Angle boarders

**Content:**

**Property ownership rules:**
- Non-property owners require a 20% deposit.
- Spousal property is accepted as asset backed. Marriage certificate, Medicare card or joint utility bill required to support evidence of relationship.
- Residential / Commercial property in the borrower's name is accepted as asset backed.
- Rates notice required for proof of property ownership (within the last 3 months, or alongside a recent utility bill).
- Boarders and mid-term refinance require Mid Doc or Full Doc assessment.

**Business & asset purpose:** Commentary is required confirming the nature of the business and how the asset will be utilised within the business. If the asset being purchased does not align to the business or business purpose, an accountant's letter may be requested.

**Credit file:**
- Working capital and recent similar asset lender enquiries may require further information, which could include 6 months bank statements.
- Credit files under 12 months cannot be considered.

---

## chunk_id: angle_fees_brokerage
**source:** angle
**topic:** fees_and_brokerage
**intent:** FEES
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What fees does Angle charge? What is the establishment fee? What is the maximum brokerage? Is there an origination fee?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Angle fees, Angle establishment fee, Angle brokerage, Angle origination fee, Angle account keeping fee, Angle commission

**Content:**

**Angle Finance fees:**
- Establishment fee (dealer or private sale): $649, financed into the loan or direct debit at settlement
- Account keeping fee: $4.95 monthly or $1 weekly
- Origination fee: up to $1,400 (incl GST) — capitalised within the loan

**Brokerage:**
- Up to 8% (incl GST)
- No rate loading applies for commission up to 8%

---

## chunk_id: angle_settlement
**source:** angle
**topic:** settlement_requirements
**intent:** SETTLEMENT
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL
**asset_class:** MV_NEW, MV_USED, PRIMARY, SECONDARY, TERTIARY
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What does Angle require at settlement? When is a Certificate of Currency needed? What inspection is required for private sales? How are PPSR encumbrances handled?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Angle settlement, Angle PPSR, Angle Certificate of Currency, Angle private sale inspection, Verimoto, Redbook Angle, Angle Docusign, Angle tax invoice

**Content:**

**Settlement details:**
- All approval conditions to be provided prior to document generation
- Request for contracts via the Angle Loan Portal
- Documents sent via DocuSign & prepared by Angle
- Private sales — inspection via Verimoto / Redbook / Olasio / Broker Inspection
- Private sales must have current and active registration
- Tax invoice — noting year, make, model, VIN/serial & odometer/hours
- Unaccredited suppliers — please supply a current bank statement for accreditation
- Certificate of Currency for assets > $100k
- Satisfactory PPSR (to be conducted by Angle Finance)
- All existing PPSR encumbrances on used cars must be removed prior to settlement

---

## chunk_id: angle_exclusions
**source:** angle
**topic:** exclusions_and_restrictions
**intent:** EXCLUSIONS
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL, SUBPRIME
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** Who is not accepted by Angle? Are taxi or Uber drivers eligible? What credit defaults are disqualifying? What is the minimum credit score?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Angle excluded, Angle not accepted, Angle taxi Uber, Angle credit default, Angle minimum credit score, Angle non-accepted assets, Angle credit file under 12 months

**Content:**

**Not accepted applicants / assets:**
- Financial defaults on credit files (paid/unpaid), except telco or utilities (paid up to $2,500)
- Applicants with credit scores below 500
- Taxi & Uber drivers
- Non-accepted assets: visit the Angle asset search engine on MyHub
- Credit files under 12 months cannot be considered

**Program-specific exclusions:**
- $400k Low Doc: excludes sole traders, tertiary assets, prime movers and buses
- Prime Movers: no sole traders or individual partnerships; Low Doc is not available
- Start-Up: primary assets only

**General note:** Angle Finance reserves the right to request additional information. Rates and pricing remain at Angle's discretion and are subject to change without notice.
