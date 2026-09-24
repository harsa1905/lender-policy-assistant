# flexicommercial — Policy Chunks
#
# source        : flexi
# documents     : flexicommercial Rate Card (15 May 2026)
#                 flexicommercial Credit Matrix — All Entities (8 December 2025)
#                 flexireplacement Policy (01 August 2024)
#                 flexipremium Low Start Loans Fact Sheet
#                 Mid-term Refinancing Fact Sheet
#                 Old Finance Meets New Fact Sheet
# effective     : 15 May 2026 (rate card); 8 December 2025 (credit matrix)
# licence       : not stated in source documents
# ABN           : 17 644 644 860 (flexicommercial Pty Ltd, a subsidiary of humm Group Limited)
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
# When flexicommercial publishes a new rate card or credit matrix:
# 1. Update the affected chunk(s) only
# 2. Bump `last_updated` and `version` in the file header
# 3. Re-embed only the changed chunks (use chunk_id to identify)
# 4. Do NOT change chunk_id values — they are the stable keys
#    used by the vector database

---

## chunk_id: flexi_flexipremium
**source:** flexi
**topic:** flexipremium_product
**intent:** PRICING
**lenders:** FLEXI
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, NON_PROPERTY_BACKED, ABN_4_6YR, ABN_OVER_6YR
**asset_class:** PRIMARY, SECONDARY
**doc_type:** ALL
**loan_size_band:** MEDIUM, LARGE
**answerable_questions:** What is flexipremium? What rates apply for primary and secondary assets? What time in business is required? Are sole traders eligible? What brokerage cap applies?
**confidence:** high
**last_verified:** 2026-07-29
**trigger_words:** flexipremium, flexi premium, flexicommercial premium rate, flexi established business rate, flexi 7.15%, flexi asset backed 4 years, flexi non-asset backed 8 years, flexi sole trader excluded

**Content:**

flexipremium is flexicommercial's product for more established businesses purchasing newer assets. Rates current as at 13 July 2026 (updated from a prior 15 May 2026 card — Primary dropped from 7.30% to 7.15%; Secondary unchanged).

**Current flexipremium rates (ex brokerage):**

| Amount funded (ex brokerage) | Primary | Secondary |
|-----------------------------|---------|-----------|
| $50,000 – $100,000 | 7.15% | 8.69% |
| $100,001 – $500,000 | 7.15% | 8.19% |
| $500,001+ | Please contact your flexicommercial BDM | Please contact your flexicommercial BDM |

**Eligibility criteria:**

*Eligible assets — new and used assets:*
- Primary: up to 5 years old (Contract Road Transport/Logistic businesses who operate 5 or more trucks can be considered)
- Secondary: up to 2 years old

*Time in business:*
- Asset backed: ABN and GST registered — minimum of 4 years
- Non-asset backed: ABN and GST registered — minimum of 8 years

*Eligible business structures:*
- Companies, Trusts, Partnerships (**Sole Traders are excluded**) trading continuously for the required time in business

**Notes:**
- Note 01: Maximum 3% brokerage applies to flexipremium deals
- Note 02: Add-ons for prime movers, private sales, refinances, non-asset backed, terms < 24 months, terms > 60 months apply as per the standard rate add-ons

The industry of Road Transport/Logistics includes contract road freight, transport services, road vehicle towing, log haulage service (road), furniture removal services and truck hire service. It does not include transport assets required to be used directly in a business such as construction services, heavy and civil engineering construction, building construction, agriculture; and civil work (i.e. tippers, dogs, agitators, and cranes).

---

## chunk_id: flexi_standard_rates
**source:** flexi
**topic:** standard_interest_rates
**intent:** PRICING
**lenders:** FLEXI
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, NON_PROPERTY_BACKED
**asset_class:** PRIMARY, SECONDARY, TERTIARY, PRIME_MOVER
**doc_type:** ALL
**loan_size_band:** MICRO, SMALL, MEDIUM, LARGE
**answerable_questions:** What are flexicommercial's standard base rates by amount and asset class? What add-ons apply for prime movers, private sales, or non-asset backed? What is the max brokerage?
**confidence:** high
**last_verified:** 2026-07-29
**trigger_words:** flexicommercial standard rate, flexi base rate, flexi primary rate, flexi secondary rate, flexi tertiary rate, flexi add-on, flexi prime mover loading, flexi non-asset backed loading, flexi brokerage

**Content:**

flexicommercial standard rates, current as at 13 July 2026 (updated from a prior 15 May 2026 card — see change note below). All rates ex brokerage.

**Base rates:**

| Base rate (ex brokerage) | Primary | Secondary | Tertiary |
|-------------------------|---------|-----------|----------|
| $10,000 – $20,000 | 12.60% | 13.50% | 14.10% |
| $20,001 – $150,000 | 8.35% | 8.85% | 12.10% |
| $150,001+ | 7.85% | 8.35% | 11.10% |

**Change note (13 July 2026 card vs the prior 15 May 2026 card):** the middle band structure changed — the old card had two separate bands ($20,001–$50,000 and $50,001–$150,000, at different rates); the new card merges these into one $20,001–$150,000 band. Don't quote the old two-band split for a deal in this range — check which card's rates are actually current before quoting.

**Add additional to base rates in each of the following:**

*Add 1.0% — each of the following independently triggers this add-on:*
- Prime Movers (excludes tippers, agitators, rigid bodies, etc.)
- Assets 11–15 years old at end of term
- Term of < 24 months
- Private sales and refinances

*Add 1.25%:*
- Term of > 60 months

*Add 1.50%:*
- Non-asset backed customers (increased from 1.25% on the prior 15 May 2026 card)

*Add 2.0%:*
- Assets > 15 to 20 years old at end of term

**Other pricing conditions:**
- Establishment fee of $495 applies to all products; $745 for private sales and refinances
- Minimum deal size of $10,000
- Maximum term of 7 years on Primary assets up to 3 years old; for all other assets the maximum term is 5 years

**Brokerage (included in Net Amount Financed):**

| Deal size | Max brokerage | Rate impact |
|-----------|--------------|-------------|
| < $50,000 | 8% | Add 0.5% to above rates for every 1% brokerage charged above 5% (up to 8%) |
| ≥ $50,000 | 6% | Add 0.5% to above rates for every 1% brokerage charged above 4% (up to 6%) |

Rates are subject to change without notice. flexicommercial reserves the right to adjust the rate in line with changes in cost of funds, or if the promotion is oversubscribed.

---

## chunk_id: flexi_credit_matrix
**source:** flexi
**topic:** credit_matrix_and_limits
**intent:** LOAN_LIMITS
**lenders:** FLEXI
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, NON_PROPERTY_BACKED, ABN_2_4YR
**asset_class:** PRIMARY, SECONDARY, TERTIARY
**doc_type:** ALL
**loan_size_band:** MICRO, SMALL, MEDIUM, LARGE, XLARGE
**answerable_questions:** How much can I borrow from flexicommercial by asset class? What ABN and GST duration is required? When is asset backing or a 20% deposit needed? What repayment history unlocks higher exposure?
**confidence:** high
**last_verified:** 2025-12-08
**trigger_words:** flexicommercial credit matrix, flexi exposure, flexi maximum loan, flexi $750K, flexi $500K, flexi $300K, flexi repayment history, flexi 20% deposit, flexi asset backed requirement

**Content:**

flexicommercial Credit Matrix — Companies, Trusts, Partnerships, Sole Traders. Effective 8 December 2025.

**Maximum exposures by asset class:**
- **Primary Assets** — up to $750K (individual transactions up to $500K)
- **Secondary Assets** — up to $500K (individual transactions up to $300K)
- **Tertiary Assets** — up to $300K (individual transactions up to $300K)

Exposure bands run: $10K–$20K, $20K–$50K, $50K–$150K, $150K–$300K, $300K–$500K, $500K–$750K.

**Requirements that apply across the bands** (requirements increase as the exposure band increases):
- ABN > 2 years
- GST registered > 2 years
- Asset backed with sufficient equity, or 20% deposit* — assessed on the proposed aggregate exposure, not just the new transaction
- Repayment history required (9 months) — applies at higher bands for primary and secondary assets
- Repayment history required (18 months) — applies at the highest bands for primary and tertiary assets

*Asset backing is a requirement for all transport operator/subcontractor transactions.

**Conditions:**
- Direct Debit*
- Director's Guarantees*
- Clear and acceptable credit reports on all Borrowers and Guarantors (dormant files will require additional information, e.g. bank statements)
- Used assets and Private Sale acceptable for Primary. Secondary and Tertiary assets on exception basis
- Primary assets not to exceed 20 years at end of term (trailers up to 30 years)
- Borrowers/Guarantors for transport operators/subcontractors must be asset backed with sufficient equity
- Standard term, residual value and fees to apply
- Repayments must be in advance

*Not required for Public companies or Private companies that are required to lodge annual financial statements with ASIC.

**Increased exposure — maximum individual transaction for Primary Assets is now $500K:**
- **Primary and Secondary Assets:** after 9 payments have been made on either the flexicommercial contract or an asset finance contract with an approved lender. (Minimum contract amount $150K. Statement to be provided showing perfect conduct.) Applications can be considered to take the combined exposure to a maximum of $500K (individual transactions to a maximum of $500K). Individual transactions for secondary assets remain unchanged at $300K.
- **Primary Assets Only:** after 18 payments have been made on either the flexicommercial contract or an asset finance contract with an approved lender. (Minimum contract amount $250K. Statement to be provided showing perfect conduct.) Applications can be considered to take the combined exposure to a maximum of $750K (individual transactions to a maximum of $500K).
- **Tertiary Assets Only:** after 18 payments have been made on either the flexicommercial contract or a tertiary asset finance contract with an approved lender. (Minimum contract amount $150K. Statement to be provided showing perfect conduct.) Applications from asset backed customers can be considered to take the combined exposure to a maximum of $300K (individual transactions to a maximum of $300K).

**Approved lenders:** The big four banks (and their subsidiaries), BoQ, Judo Bank, Rabobank (and DLL), Suncorp, Bendigo Adelaide or Macquarie Bank, as well as large asset finance institutions limited to Metro Finance, Caterpillar Financial, CNH Capital, John Deere Financial, Paccar Financial and Toyota Finance.

---

## chunk_id: flexi_asset_categories
**source:** flexi
**topic:** asset_categories
**intent:** ASSET_ELIGIBILITY
**lenders:** FLEXI
**borrower_profile:** COMMERCIAL
**asset_class:** PRIMARY, SECONDARY, TERTIARY, PRIME_MOVER
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** Which category does an asset fall into at flexicommercial? What is the max asset age at end of term? Does flexi fund SUVs or passenger cars? What are Tier II assets?
**confidence:** high
**last_verified:** 2025-12-08
**trigger_words:** flexicommercial asset category, flexi primary asset, flexi secondary asset, flexi tertiary asset, flexi Tier II, flexi no SUV, flexi no passenger car, flexi no photocopier, flexi trailer 30 years

**Content:**

flexicommercial asset categories, per the Credit Matrix (effective 8 December 2025).

**Primary assets:**
- Agricultural machinery and equipment
- Materials handling / forklifts
- Access equipment (boom/scissor lifts) — exposures for forklift on-hire businesses are capped at $250K
- Light trucks < 3.5 tonnes — fully eligible, no upper weight restriction
- Heavy trucks > 3.5 tonnes (including well over 5.5 tonnes) — fully eligible, this is a normal, commonly-financed Primary asset category for flexicommercial, not an edge case
- Trailers and buses/coaches
- Commercial motor vehicles (utes, vans and 4WDs)
- Construction and earth moving equipment (non-mining)

Primary assets can be up to 20 years old at end of term (trailers — 30 years).

**The one exclusion that applies to road vehicles is specifically SUVs and passenger cars (this includes rental car businesses) — this does NOT extend to trucks of any weight, which remain fully financeable as shown above. Do not read the SUV/passenger-car exclusion as also excluding light or heavy trucks; they are different, unrelated vehicle categories.**

**Secondary assets:**
- Medical / dental / laboratory equipment
- Mining equipment
- Attachments for earthmoving
- Plant services (compressors and generators)
- Printing and packaging equipment
- Forestry machinery and equipment
- Engineering and toolmaking equipment
- Woodworking and metalworking equipment
- Mechanical workshop equipment
- Agricultural spraying drones
- Tier II trucks, buses, earthmoving, utes

Secondary assets can be up to 7 years old at end of term.

**Tertiary assets:**
- Drones
- Fitness equipment
- POS systems
- AV and video conferencing
- All IT assets (maximum exposure $50K; full doc acceptable for > $50K)
- Renewable energy (maximum exposure $50K; full doc acceptable for > $50K)
- Pallet racking
- Security system (hardware only)
- Fit outs
- Temporary fencing (maximum exposure $50K; full doc acceptable for > $50K)
- GPS attachments — limited to $100K for portable devices; applications for fixed devices require security over the host asset, unless the lend is limited to $50K for asset backed customers, $20K for non-asset backed customers
- Software
- Air conditioning units
- Cool rooms
- Spray booths
- Catering and hospitality equipment
- Food manufacturing equipment
- Portable buildings

**NB: the only Tertiary-asset exclusions are photocopiers, MFDs and scaffolding — this does not affect the Tier II categories below (which sit under Secondary), all of which remain normally fundable.**

**Tier II asset categories and brands** (fully eligible, not excluded by the note above) include (by category): trucks (e.g. Foton), buses (e.g. Bonluck), utes/vans/4WD (e.g. Dongfeng), materials handling (e.g. Hangcha), construction/earthmoving (e.g. Boleo). Tier II includes (but is not limited to) Chinese branded equipment and electric trucks.

---

## chunk_id: flexi_replacement_policy
**source:** flexi
**topic:** flexireplacement_policy
**intent:** ROLLOVER_REPLACEMENT
**lenders:** FLEXI
**borrower_profile:** COMMERCIAL, EXISTING_CLIENT, PROPERTY_BACKED
**asset_class:** PRIMARY
**doc_type:** ALL
**loan_size_band:** LARGE
**answerable_questions:** What is flexireplacement? What is the maximum transaction size? What repayment increase is allowed? How long must the old facility have run? Can it be used for balloon refinance?
**confidence:** high
**last_verified:** 2024-08-01
**trigger_words:** flexireplacement, flexi replacement, flexi replace asset, flexi 125%, flexi balloon refinance, flexi 18 months facility, flexi approved lender replacement, flexi 90 days settlement

**Content:**

flexireplacement is flexicommercial's asset replacement policy (information current as at 01 August 2024). To be read in conjunction with the current flexicommercial Credit Matrix All Entities and the flexicommercial Rate Card.

**Conditions:**
- Maximum transaction size / aggregated exposure (includes existing matrix exposure): **$500K**
- Proposed repayment not to exceed **125%** of that being replaced
- **Primary assets only** — age limits as per Matrix Policy. Dealer or Private Sales acceptable
- Asset to be financed must be core business equipment. The asset does not necessarily need to be like-for-like with the replaced asset

**The facility to be replaced must be:**
- With an approved lender
- Either current, or paid in full within the last three months, after having been established for **18 months or more**. (A current statement confirming conduct and repayment is required. Proof of the previous agreement, including terms and conditions, is also required, plus written confirmation that the previous facility has been repaid, or will be repaid if the asset is to be traded in.)

**New facility requirements:**
- Clear and acceptable Equifax credit history on all Borrowers and Guarantors
- Borrowing and Guarantee parties on the old and new facility to be identical
- Settlement of the new facility must be made within **90 days** of the expiry of the old facility

**Balloon refinances:** flexireplacement can be used for balloon refinances up to $500K (inspection and valuation required if > $300K).

**Approved lenders:** ANZ, CBA, NAB, Westpac, BOQ, Suncorp, Bendigo Adelaide, Macquarie Bank, Judo Bank, and also Angle Finance, Caterpillar Finance Australia, DLL, Dynamoney, Earlypay, John Deere Financial, Kubota Australia Finance, Mercedes Benz Financial Services, Moneytech, Morris Finance, Nissan Financial Services, Pepper Money, Scotpac, Shift, Toyota Finance, Volvo Finance, Westlawn Finance.

---

## chunk_id: flexi_refinance_products
**source:** flexi
**topic:** refinancing_and_low_start
**intent:** ROLLOVER_REPLACEMENT
**lenders:** FLEXI
**borrower_profile:** COMMERCIAL, EXISTING_CLIENT
**asset_class:** PRIMARY, SECONDARY
**doc_type:** ALL
**loan_size_band:** MEDIUM, LARGE
**answerable_questions:** What is flexi's mid-term refinancing? What is a Low Start Loan? What is "Old Finance Meets New"? What brokerage applies to a mid-term refinance?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** flexi mid-term refinancing, flexi Low Start Loan, flexi 50% repayments, Old Finance Meets New, flexi bundled refinance, flexi cash flow, flexi 1% brokerage refinance

**Content:**

flexicommercial offers three cash-flow-focused refinancing and repayment products.

**Mid-term Refinancing** — refinancing framework:
- At least **12 months** into the term of the current contract
- Terms of up to 5 years considered
- Satisfactory repayment history with no material arrears. A small number of non-systemic dishonours may be acceptable
- Deal to be refinanced at the net book value — that is, no early termination costs to apply
- Standard interest rates apply
- Mid-term refinances are subject to normal flexicommercial credit policy
- **Brokerage limited to 1.0%** (speak to your flexi BDM if the complexity of the deal warrants a higher brokerage)

**flexipremium Low Start Loans** — an easier start with 50% repayments:
- For new flexipremium facilities, a Low Start Loan lets the business start their term paying **50% repayments for the first 3 months**, then catch that up gradually over time
- Conditions:
  - Customer must qualify for flexipremium
  - No cashflow lenders on file (e.g. Prospa, Moula)
  - Must have an existing commercial asset finance facility with an approved lender

*Example:* $500K for a new excavator over 60 months (with a 20% residual) — standard repayments $8,400/month; Low Start repayments $4,200/month for the first 3 months, then catch-up repayments of $9,196/month thereafter.

**Old Finance Meets New** — bundling an existing finance agreement into a new contract with additional equipment, allowing a business to both pay off their existing asset and purchase a new one, with the net result of reduced repayments.

*Example:* an existing excavator with $2,075/month repayments, 2 years to go and a $46K payout, bundled into a new $146K, 5-year facility for 2 excavators with a new repayment of $3,029/month.

---

## chunk_id: flexi_fees
**source:** flexi
**topic:** fees_and_brokerage
**intent:** FEES
**lenders:** FLEXI
**borrower_profile:** COMMERCIAL
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What is flexicommercial's establishment fee? What is the maximum brokerage? What is the minimum deal size? What fee applies to private sales and refinances?
**confidence:** high
**last_verified:** 2026-05-15
**trigger_words:** flexicommercial fee, flexi establishment fee, flexi $495, flexi $745, flexi brokerage cap, flexi minimum deal size, flexi private sale fee

**Content:**

**Fees:**
- Establishment fee of **$495** applies to all products
- **$745** for private sales and refinances
- Minimum deal size of **$10,000**
- Private sales and refinances also carry a separate **+1.0% interest rate loading** on top of the standard base rate (in addition to the higher $745 establishment fee) — see standard rate add-ons for details

**Brokerage (included in Net Amount Financed):**

| Deal size | Max brokerage | Rate impact |
|-----------|--------------|-------------|
| < $50,000 | 8% | Add 0.5% to base rates for every 1% brokerage charged above 5% (up to 8%) |
| ≥ $50,000 | 6% | Add 0.5% to base rates for every 1% brokerage charged above 4% (up to 6%) |

**Product-specific brokerage limits:**
- flexipremium deals: maximum **3%** brokerage
- Mid-term refinances: brokerage limited to **1.0%**

---

## chunk_id: flexi_exclusions
**source:** flexi
**topic:** exclusions_and_restrictions
**intent:** EXCLUSIONS
**lenders:** FLEXI
**borrower_profile:** COMMERCIAL, SELF_EMPLOYED
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What assets will flexicommercial not fund? Are sole traders eligible for flexipremium? Are SUVs financed? What restrictions apply to transport operators?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** flexicommercial excluded, flexi not funded, flexi no SUV, flexi no passenger car, flexi no photocopier, flexi no scaffolding, flexi sole trader, flexi transport operator asset backed, flexi cashflow lender

**Content:**

**Excluded assets — flexicommercial does not fund:**
- SUVs or passenger cars (this includes rental car businesses)
- Photocopiers
- MFDs (multi-function devices)
- Scaffolding

**Excluded business structures:**
- Sole Traders are excluded from **flexipremium** (the standard Credit Matrix does cover Companies, Trusts, Partnerships and Sole Traders)

**Restrictions and conditions:**
- Asset backing is a requirement for **all transport operator/subcontractor transactions** — borrowers/guarantors must be asset backed with sufficient equity
- Used assets and Private Sale are acceptable for Primary assets; Secondary and Tertiary assets on an exception basis
- Primary assets not to exceed 20 years at end of term (trailers up to 30 years)
- Secondary assets: up to 7 years old at end of term
- Low Start Loans: no cashflow lenders on file (e.g. Prospa, Moula)
- Repayments must be in advance
- Direct debit and director's guarantees required (not required for Public companies, or Private companies that must lodge annual financial statements with ASIC)

**Exposure caps within categories:**
- Forklift on-hire businesses: exposures capped at $250K
- All IT assets, renewable energy, temporary fencing: maximum exposure $50K (full doc acceptable for > $50K)
- GPS attachments: limited to $100K for portable devices; fixed devices require security over the host asset unless limited to $50K (asset backed) or $20K (non-asset backed)

**General note:** flexicommercial reserves the right to request additional information if deemed necessary. Lending criteria, fees and T&Cs apply; all applications are subject to the Financier's lending and credit criteria, and approval is at the sole discretion of the Financier.
