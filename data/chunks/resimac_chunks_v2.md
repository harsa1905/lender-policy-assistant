# Resimac Asset Finance — Policy Chunks
#
# source        : resimac
# document      : Commercial Auto and Equipment Product Guide
# effective     : 27 March 2026
# licence       : Australian Credit Licence 393031
# ABN           : 93 098 034 041
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
# When Resimac publishes a new rate card or policy update:
# 1. Update the affected chunk(s) only
# 2. Bump `last_updated` and `version` in the file header
# 3. Re-embed only the changed chunks (use chunk_id to identify)
# 4. Do NOT change chunk_id values — they are the stable keys
#    used by the vector database

---

## chunk_id: resimac_customer_tiers
**source:** resimac
**topic:** customer_tiers
**intent:** ELIGIBILITY
**lenders:** RESIMAC
**borrower_profile:** COMMERCIAL, ABN_1_2YR, ABN_2_4YR, ABN_4_6YR, ABN_OVER_6YR, PROPERTY_BACKED, RENTER, SPOUSE_OWNED
**asset_class:** ALL
**doc_type:** LOW_DOC, LITE_DOC, FULL_DOC
**loan_size_band:** ALL
**answerable_questions:** Which tier applies to my ABN age? Do I need to own property? What credit score do I need? What deposit if I don't own property?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** MIN_ABN, MIN_GST, PROPERTY_REQUIRED, DEPOSIT_REQUIRED
**trigger_words:** customer tier, PremiumPLUS, Premium, Standard, Basic, ABN duration, GST registered, property backed, renter, LWP, spouse owned, eligibility, qualify

**Content:**

Resimac uses four customer tiers. Tier determines interest rate, maximum loan amount, and accepted property types. All applicants must be commercial entities with a valid ABN and GST registration.

| Tier | Min ABN | Min GST | Accepted Property Types |
|------|---------|---------|------------------------|
| PremiumPLUS | > 6 years | > 3 years | Property-backed only |
| Premium | > 4 years | > 2 years | Property-backed only |
| Standard | > 2 years | > 1 year | Property-backed, Spouse-owned, Renter |
| Basic | > 1 year | > 1 year | Property-backed, Spouse-owned, Renter, LWP/other (no boarders) |

**Property-backed definition:**
- ≥ 25% of property resides in a guarantor's name
- Equity in property is at least 1× NAF (Net Amount Financed)
- No multiple or adverse encumbrances on the property

**Spouse-owned property:**
Does not constitute property backing, but can be used to waive a deposit requirement. Borrower must be legally married (not de facto).

**Non property-backed deposits:**
- Motor vehicles: 10% deposit required
- All other assets: 20% deposit required

**Credit scores (Equifax):**
Assessment uses the highest score among the company or any guarantor.

| Doc Type | Sole Trader | Company / Guarantor | Lower Threshold |
|---------|------------|-------------------|----------------|
| Low Doc | ≥ 650 | ≥ 600 | Score < 450 → referral or decline |
| Lite Doc | ≥ 600 | ≥ 550 | Score < 450 → referral or decline |
| Full Doc | ≥ 600 | ≥ 550 | Score < 450 → referral or decline |

**Hard exclusions:**
- No current bankrupts
- No discharged bankrupts within the last 10 years

---

## chunk_id: resimac_interest_rates
**source:** resimac
**topic:** interest_rates
**intent:** PRICING
**lenders:** RESIMAC
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, ABN_OVER_6YR
**asset_class:** MV_NEW, MV_USED, EV, PRIMARY, SECONDARY, TERTIARY
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What is the interest rate for a motor vehicle / EV / primary / secondary / tertiary asset? What risk loadings apply? How big is the PremiumPLUS discount?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** BASE_RATE, RISK_LOADING, EV_DISCOUNT
**trigger_words:** interest rate, rate, pricing, PremiumPLUS rate, motor vehicle rate, electric vehicle rate, primary asset rate, secondary asset rate, tertiary asset rate, risk loading, classic car, private sale rate, prime mover rate

**Content:**

Rates are subject to change without notification. All rates are per annum.

| Asset Category | PremiumPLUS | Premium / Standard / Basic |
|---------------|------------|---------------------------|
| Motor vehicles < 3 years | 7.64% | 7.89% |
| Motor vehicles > 3 years | 8.24% | 8.49% |
| **Electric vehicles** | **7.54%** | **7.79%** |
| Primary assets < 3 years | 8.39% | 8.64% |
| Primary assets > 3 years | 9.29% | 9.54% |
| Secondary assets | 12.39% | 12.64% |
| Tertiary assets | 14.09% | 14.34% |

**PremiumPLUS discount:** 25 basis points below Premium/Standard/Basic rates — this note explains *why* the PremiumPLUS column is 0.25% lower, it is not a separate calculation step. Always read a PremiumPLUS client's rate directly from the PremiumPLUS column of the correct age-band row above (e.g. a 4-year-old motor vehicle is ">3 years", so PremiumPLUS = 8.24% directly) — do not take the Premium/Standard/Basic figure from that row and subtract 0.25% yourself, and never borrow a rate from a different age-band row.

**Risk loading of +2% applies to:**
- Private sales
- Classic cars
- Assets with age > 16 years at end of term
- Prime movers

**Risk loading rules:**
- Multiple loadings may apply per deal
- Maximum risk loading capped at **4%** per deal
- Excludes brokerage loading

**Electric vehicle benefit:** EVs qualify for the lowest rate in the range AND extended loan terms up to 84 months (Green Goods).

---

## chunk_id: resimac_loan_limits
**source:** resimac
**topic:** loan_limits
**intent:** LOAN_LIMITS
**lenders:** RESIMAC
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, EXISTING_CLIENT
**asset_class:** MV_NEW, MV_USED, EV, PRIMARY, SECONDARY, TERTIARY, MOTORBIKE
**doc_type:** LOW_DOC, LITE_DOC, FULL_DOC
**loan_size_band:** MEDIUM, LARGE, XLARGE
**answerable_questions:** How much can I borrow by tier and doc type? What is the max NAF per vehicle / motorbike? What are the total exposure limits? What loan terms are available?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** MAX_LOAN, MAX_TERM
**trigger_words:** maximum loan, how much can I borrow, loan limit, NAF, net amount financed, $250k, $300k, $400k, $450k, loan term, 84 months, exposure limit, SME, large corporate

**Content:**

NAF = Net Amount Financed (excludes fees and brokerage).

**PremiumPLUS and Premium:**

| Asset Category | Low Doc | Lite Doc | Full Doc |
|---------------|---------|---------|---------|
| Motor vehicles | $300k | $400k | $450k |
| Electric vehicles | $300k | $400k | $450k |
| Primary assets | $300k | $400k | $450k |
| Secondary assets | $300k | $400k | $450k |
| Tertiary assets | — | $400k | $450k |

**Standard:**

| Asset Category | Low Doc | Lite Doc | Full Doc |
|---------------|---------|---------|---------|
| Motor vehicles | $200k | $300k | $400k |
| Electric vehicles | $200k | $300k | $400k |
| Primary assets | $200k | $300k | $400k |
| Secondary assets | $200k | $300k | $400k |
| Tertiary assets | — | $300k | $400k |

**Basic:**

| Asset Category | Low Doc | Lite Doc | Full Doc |
|---------------|---------|---------|---------|
| Motor vehicles | $100k | $150k | $200k |
| Electric vehicles | $100k | $150k | $200k |
| Primary assets | $100k | $150k | $200k |
| Secondary assets | $100k | $150k | $200k |
| Tertiary assets | — | $150k | $200k |

**Individual asset caps:**
- Max NAF per passenger vehicle: **$250k**
- Max NAF per motorbike: **$75k**

**Exposure limits (total across all contracts):** this is a DIFFERENT, unrelated number from the Full Doc NAF caps above — it is the ceiling on a customer's entire combined Resimac lending across every contract they hold, not what a single deal can be. A single transaction is always capped by the per-tier NAF table above ($450k max for PremiumPLUS/Premium Full Doc on one deal) regardless of how much exposure headroom the customer has left.
- SME: $500k
- Large corporate: $750k
- Private school / club / association: $500k
- S&P 'A' rated or Moody's 'A2' rated: $2m
- Government / Sovereign entities: $2m

**Low Doc aggregate exposure:** $400k maximum for existing property-backed clients with 12 months perfect repayment history on a Resimac Asset Finance contract.

**Loan terms:**
- Standard: 12–60 months
- Green Goods (EV / sustainable assets): up to **84 months**

---

## chunk_id: resimac_documentation
**source:** resimac
**topic:** documentation
**intent:** DOCUMENTATION
**lenders:** RESIMAC
**borrower_profile:** COMMERCIAL, SELF_EMPLOYED, VISA_HOLDER
**asset_class:** ALL
**doc_type:** LOW_DOC, LITE_DOC, FULL_DOC
**loan_size_band:** ALL
**answerable_questions:** What documents are required for Low/Lite/Full Doc? What are the Lite Doc turnover conditions? Who must be a guarantor? When must privacy consent be signed?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** DOC_TYPE
**trigger_words:** documents required, Low Doc, Lite Doc, Full Doc, ATO portal, BAS, bank statements, financial statements, tax returns, asset liability statement, privacy consent, what do I need to apply

**Content:**

Three documentation tiers apply across all customer tiers.

| Document | Low Doc | Lite Doc | Full Doc |
|---------|---------|---------|---------|
| Application + privacy consent | ✓ | ✓ | ✓ |
| Asset and liability statement | ✓ | ✓ | ✓ |
| 12 months running ATO portals | — | ✓ | ✓ |
| Two most recent BAS portals | — | ✓ | ✓ |
| 90-day bank statements | — | On request | ✓ |
| Financial accounts / tax returns | — | — | ✓ |

Each tier is a superset of the one before it: Low Doc needs only the application and Asset & Liability Statement; Lite Doc adds 12 months of ATO portals and the two most recent BAS portals (bank statements only if specifically requested); Full Doc adds full financial accounts/tax returns on top of everything Lite Doc requires.

**Privacy consent requirement:**
Must be signed within **90 days** of application and must specifically note:
*'Resimac Asset Finance (resimacassetfinance.com.au)'*

**Lite Doc additional conditions:**
- ATO debt must be < 10% of annual turnover
- ATO debt must be under an established payment arrangement in place for > 3 months
- BAS must show annualised minimum turnover > 2.5× asset purchase price

**Directors and shareholders:**
- All directors and all > 40% shareholders must be Australian Citizens or Permanent Residents residing in Australia
- All must be guarantors to the loan
- All > 25% shareholders must complete Resimac AML procedures
- Guarantee requirement may be waived for large corporate, clubs, private schools, charities and associations

**Cash flow lenders:** Any enquiries from cashflow lenders within the last 6 months may require Lite Doc or bank sweep, subject to profile.

**Credit references:**
- Loans < $100k: Asset finance statements (6+ months, no missed repayments) OR mortgage statements (6+ months, no missed repayments; must be in applicant or guarantor name)
- Loans > $100k: Asset finance statements (6+ months, no missed repayments; must be for 50% of requested NAF if Low Doc)

**Active credit file:** Applicants must be established with active credit files and regular industry-related enquiries available.

---

## chunk_id: resimac_fees_brokerage
**source:** resimac
**topic:** fees_and_brokerage
**intent:** FEES
**lenders:** RESIMAC
**borrower_profile:** COMMERCIAL
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What are the setup and monthly fees? What is the max brokerage? How does brokerage above 5.5% affect the rate?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** BROKERAGE_MAX
**trigger_words:** fees, setup fee, account keeping fee, monthly fee, PPSR fee, brokerage, private sale fee, introducer fee, cost

**Content:**

**Standard fees:**
- Monthly account keeping fee: **$4.95**
- Setup fee: **$495**
- Private sale / sale and buyback fee: **$695**
- PPSR fee(s): at cost (pass-through)

**Brokerage (inclusive of GST):**
- Standard rates applicable up to **5.5%** with no rate impact
- Above 5.5%: equivalent of 0.5% rate increase for every 1% increase in brokerage (or part thereof)
- Maximum brokerage: **8.8%**
- Introducer documentation fee: up to **$990**
- If private sale / sale and buyback: introducer documentation fee up to **$880**

---

## chunk_id: resimac_asset_categories
**source:** resimac
**topic:** asset_categories
**intent:** ASSET_ELIGIBILITY
**lenders:** RESIMAC
**borrower_profile:** COMMERCIAL
**asset_class:** MV_NEW, MV_USED, EV, LCV, PRIMARY, SECONDARY, TERTIARY, CARAVAN, MOTORBIKE
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** Which category does an asset fall into? What is the max asset age at end of term? What balloon percentages apply by term?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** ASSET_AGE_MAX
**trigger_words:** motor vehicle, passenger vehicle, light truck, light commercial, van, ute, classic car, motorbike, motorcycle, primary asset, heavy truck, trailer, bus, coach, excavator, construction, farming, agriculture, materials handling, prime mover, caravan, secondary asset, generator, compressor, medical equipment, CNC, landscaping, tertiary asset, audio visual, conveyor, skip bin, medical laser, GPS, what assets can be financed, eligible assets

**Content:**

**Motor Vehicles:**
- Passenger vehicles
- Light trucks
- Light commercial vehicles (vans, utes)
- Classic cars (+2% risk loading applies)
- Motorbikes (max NAF $75k per unit)

**Primary Assets:**
- Heavy trucks > 4.5T GVM
- Trailers
- Buses and coaches
- Small yellow goods and excavators
- Construction and earth-moving equipment
- Farming and agriculture equipment
- Materials handling and access equipment
- Prime movers (+2% risk loading; always requires property-backed guarantor)
- Caravans

**Secondary Assets:**
- Generators and compressors
- Engineering and toolmaking equipment
- Medical equipment
- Woodworking and metalworking equipment
- CNC and edge benders
- Landscaping and groundskeeping (motorised only)
- Attachments for earthmoving machinery

**Tertiary Assets:**
- Audio visual equipment
- Conveyors
- Wine and beer industry and processing equipment
- Skip bins
- Medical lasers
- Testing and calibration equipment
- GPS units (must be detachable)

**Maximum asset age at end of term:**
- Motor vehicles (excl. classic): **25 years**
- Primary assets: **25 years**
- Secondary assets: **10 years**
- Tertiary assets: **5 years**

**Balloon payments (commercial only — excludes Secondary, Tertiary and Classic cars):**

| Term | New vehicles (0–3 yrs) | Used vehicles & Primary |
|------|----------------------|------------------------|
| 36 months | 50% | 40% |
| 48 months | 45% | 35% |
| 60 months | 40% | 30% |

---

## chunk_id: resimac_exclusions
**source:** resimac
**topic:** exclusions
**intent:** EXCLUSIONS
**lenders:** RESIMAC
**borrower_profile:** COMMERCIAL, DISCHARGED_BANKRUPT
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** Is this asset excluded? Can I get a consumer loan? Is sale and buyback allowed? Are discharged bankrupts accepted?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** ASSET_AGE_MAX
**trigger_words:** excluded assets, not eligible, cannot finance, gym equipment, hospitality equipment, software, food truck, livestock, ride share, taxi, racking, IT hardware, office furniture, fixtures fittings, refrigeration, artwork, vending machine, gaming machine, shipping container, demountable, scaffolding, repairable writeoff, sale and buyback

**Content:**

**Excluded assets — cannot be financed under any circumstances:**
- Fixtures and fittings
- Cool rooms and spray booths
- Intangible assets
- Refrigeration equipment
- Gym equipment
- Hospitality equipment
- Software
- Scaffolding, racking and temporary fencing
- Food trucks
- Artwork
- Vending and gaming machines
- Livestock
- Ride-share vehicles, taxis and repairable write-offs
- Demountables and shipping containers
- Racking
- Office furniture
- Electric or motor vehicles used for hire/rental purposes
- IT hardware

**Excluded loan structures:**
- No personal / consumer loans (commercial ABN holders only)
- Sale and buyback: only for PremiumPLUS or Premium; dealership sales only; asset purchased within last 30 days of receiving the application; assessed case-by-case

**Excluded applicants:**
- Current bankrupts
- Discharged bankrupts within the last 10 years

**Documentation exclusions:**
- Low Doc not available for Tertiary asset category
- Tertiary assets require Lite Doc minimum

---

## chunk_id: resimac_settlement
**source:** resimac
**topic:** settlement
**intent:** SETTLEMENT
**lenders:** RESIMAC
**borrower_profile:** COMMERCIAL
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What is required before settlement? When is a Certificate of Currency needed? How are valuations handled? Is PPSR registration required?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** PPSR
**trigger_words:** settlement, PPSR, insurance, Certificate of Currency, CoC, privacy consent, asset registration, serialised, valuation, what happens at settlement, settle loan

**Content:**

**Pre-settlement requirements:**
- Privacy consent signed within 90 days of application
- All assets must be serialised, identifiable and registered prior to settlement (where applicable)
- Insurance is required on all deals
- Certificate of Currency (proof of insurance) required for NAF amounts > $100k

**Valuations:**
- Completed in-house where possible
- External valuations may be required at customer cost for luxury assets or high-value motor vehicles

**Asset use requirement:**
- Asset must be used by the business as part of its normal trading activities

**PPSR registration:**
- Required on all financed assets; PPSR fee(s) charged at cost

**References:**
- Obtained where available at the sole discretion of Resimac Asset Finance

