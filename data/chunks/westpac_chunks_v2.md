# Westpac Equipment Finance (WEF) — Policy Chunks
#
# source        : westpac
# documents     : Key Financial Policies Q1 FY26
#                 Rate Chart 13 July 2026 (Xpress and Standard) -- re-issued from
#                 15 June 2026 with the same effective date only, all rates unchanged
#                 Equipment Finance Settlement Requirements Update (24 Feb 2025)
# effective     : 13 July 2026 (rates, re-confirmed -- no rate changes from 15 June 2026); 24 Feb 2025 (settlement update)
# licence       : Australian Credit Licence 233714
# ABN           : 33 007 457 141
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
# Westpac rates are valid for 7 days subject to settlement.
# Rate chunks must be updated every time a new rate sheet is issued.
# 1. Replace rate table content in westpac_xpress_rates and
#    westpac_standard_rates chunks only
# 2. Update `effective` date in the file header
# 3. Re-embed only the two rate chunks
# 4. Policy chunks (tiers, eligibility, settlement) update less
#    frequently — update only when policy documents change

---

## chunk_id: westpac_channels_overview
**source:** westpac
**topic:** channels_and_customer_types
**intent:** ELIGIBILITY
**lenders:** WESTPAC
**borrower_profile:** COMMERCIAL, NEW_CLIENT, EXISTING_CLIENT, PROPERTY_BACKED
**asset_class:** ALL
**doc_type:** LOW_DOC, FULL_DOC
**loan_size_band:** ALL
**answerable_questions:** Which Westpac channel suits me? What are the universal eligibility criteria? Do I need to sign an Affordability Declaration?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** MIN_ABN, PROPERTY_REQUIRED, MAX_LOAN
**trigger_words:** DriveXpress, Rollover, Replacement, Medical, channel, product type, new to bank, existing client, WEF history, which product, which channel, Westpac eligibility

**Content:**

Westpac WEF operates four specialist channels. Access and loan limits depend primarily on the borrower's relationship history with Westpac — not credit score alone.

**Universal eligibility criteria (all channels):**
- > 2 years in business with valid ABN and currently GST registered
- Statutory lodgements and payments (tax, GST, employee entitlements) up to date — no payment arrangements in place
- Where financial data is not obtained: verbal confirmation of compliance required
- All directors must guarantee the loan and have satisfactory credit bureau reports
- Borrower must sign an Affordability Declaration

---

## chunk_id: westpac_drivexpress
**source:** westpac
**topic:** drivexpress_policy
**intent:** ELIGIBILITY
**lenders:** WESTPAC
**borrower_profile:** COMMERCIAL, NEW_CLIENT, EXISTING_CLIENT, PROPERTY_BACKED
**asset_class:** MV_NEW, MV_USED, LCV, PRIMARY
**doc_type:** LOW_DOC
**loan_size_band:** MEDIUM, LARGE
**answerable_questions:** What is the DriveXpress limit for a new-to-bank vs existing client? Which assets are Category A/B/C? What is the DriveXpress exposure cap?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** MAX_LOAN, PROPERTY_REQUIRED, MIN_ABN
**trigger_words:** DriveXpress, fast approval, quick approval, no financials, simplified application, DriveXpress eligibility, new to bank DriveXpress, existing client DriveXpress, DriveXpress limit, DriveXpress exposure

**Content:**

DriveXpress is Westpac's fast-track, simplified approval channel. No financial statements are required if all fast-track criteria are met.

**Customer types and limits:**

| Customer Type | Max Loan | Eligible Goods | Max DriveXpress Exposure |
|--------------|---------|---------------|--------------------------|
| New to Business Bank (owns residential property + min. income $75k p.a.) | $150k | A, B & C | $250k |
| Existing Client (12 months current WEF history OR finalised WEF contract within last 12 months OR existing Westpac business lending) | $200k (A) / $300k (B) / $500k (C) | A / B / C | $750k |

**Asset categories:**

| Category | Age Limit | Sale Types | Assets |
|---------|----------|-----------|--------|
| A | Up to 5 years old | Dealer & Private Seller | MV car (not taxi/hire/import/exotic; price ≤ $250k), Light Commercial < 4.5T GVM |
| B | Up to 5 years old (cranes: up to 3 years) | Dealer only | Trucks > 4.5T, forklifts, telehandlers, boom/scissor/spider lifts, trailers, excavators, skid steers/wheel loaders, mobile/tight access cranes, backhoe loaders, graders, scrapers, dozers, rollers |
| C | Up to 7 years old | Dealer only | Tractors, headers, harvesters, cotton pickers, balers, mower conditioners, ploughs, seeders, sprayers, spreaders, all-terrain vehicles, feed wagons |

**DriveXpress criteria:**
- > 2 years in business with valid ABN and currently GST registered
- Statutory obligations up to date; no payment arrangements
- All directors to guarantee loan; satisfactory credit bureau reports
- Borrower signs Affordability Declaration
- Existing business customers must be in good standing with no capping
- DriveXpress Exposure = aggregate loan balances under this policy

**Documentation required:**
- Signed Affordability Declaration
- Satisfactory credit bureau reports (ASIC search is not part of DriveXpress's own criteria — it applies to Rollover and Replacement, not DriveXpress)
- If fast-track criteria NOT met: last 2 years financials + 2 years directors' ITRs → standard application

**Asset notes:**
- Modifications/accessories: funded amount must not exceed **10% of dealer invoice/purchase price**
- Tractor/yellow goods attachments must be funded **together** with the primary asset
- No minus equity on trade-ins

---

## chunk_id: westpac_rollover
**source:** westpac
**topic:** rollover_policy
**intent:** ROLLOVER_REPLACEMENT
**lenders:** WESTPAC
**borrower_profile:** COMMERCIAL, EXISTING_CLIENT
**asset_class:** MV_NEW, MV_USED, LCV, PRIMARY
**doc_type:** LOW_DOC
**loan_size_band:** LARGE, XLARGE
**answerable_questions:** Can I roll over an existing contract? What is the max loan if the original funder is Westpac vs another financier? Am I eligible if new to bank?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** MAX_LOAN, MIN_ABN
**trigger_words:** rollover, roll over, contract rollover, extend contract, refinance existing WEF, existing WEF contract, rollover eligibility, rollover limit, other financier rollover

**Content:**

The Rollover channel allows existing clients to extend or replace an existing equipment finance contract. **New-to-bank clients are not eligible.**

**Loan limits:**

| Original Funder | Max Loan | Eligible Goods |
|----------------|---------|---------------|
| Westpac | $500k | All (A, B & C) |
| Other financier (inspection required) | $250k | A & B (refer to DriveXpress) |

**Rollover criteria:**
- Borrower must have 12 months current WEF history OR finalised WEF contract within last 12 months
- > 2 years in business with valid ABN and currently GST registered
- Statutory obligations up to date; no payment arrangements
- Satisfactory credit bureau and ASIC search
- Contract being rolled must have been operating for > 12 months
- Borrower/guarantor and security position must be the same as original contract
- St.George Group EF residual values accepted

---

## chunk_id: westpac_replacement
**source:** westpac
**topic:** replacement_policy
**intent:** ROLLOVER_REPLACEMENT
**lenders:** WESTPAC
**borrower_profile:** COMMERCIAL, NEW_CLIENT, EXISTING_CLIENT, PROPERTY_BACKED
**asset_class:** MV_NEW, MV_USED, LCV, PRIMARY
**doc_type:** LOW_DOC
**loan_size_band:** MEDIUM, LARGE, XLARGE
**answerable_questions:** What is the Replacement limit for new vs existing clients? What repayment increase is allowed? Can I replace multiple contracts with one? What buses qualify?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** MAX_LOAN, MIN_ABN
**trigger_words:** replacement, replace contract, asset replacement, swap asset, replace truck, replace equipment, replacement policy, replace multiple contracts, replacement limit

**Content:**

The Replacement channel allows borrowers to replace a finalised or near-finalised equipment finance contract with a new one for a different asset.

**Loan limits:**

| Customer Type | Max Loan | Eligible Goods |
|--------------|---------|---------------|
| New Clients (owns residential property) | $150k | A & B |
| Existing Clients (12 months current WEF history or finalised EF contract within last 12 months) | $200k (A) / $650k (B & C) | A / B & C |

**Asset categories — Category A is the same as DriveXpress; Categories B and C differ:**

| Category | Details |
|---------|---------|
| A | Same as DriveXpress: MV car (not taxi/hire/import/exotic; price ≤ $250k), Light Commercial < 4.5T GVM — up to 5 years old |
| B | Broader than DriveXpress's Category B: trucks > 4.5T, trailers, forklifts/telehandlers, boom/scissor/spider lifts, backhoe loaders, dozers, **tippers, dump trucks (heavy duty)**, excavators, graders, scrapers, skid steers/wheel loaders, mobile/tight access cranes, rollers — up to 5 years old (cranes up to 3 years). Under Replacement, Category B **also includes** a separate agricultural-equipment list at a different age ceiling: tractors, headers, harvesters, cotton pickers, balers, mower conditioners, ploughs, seeders, sprayers, spreaders, **windrowers**, all-terrain vehicles, feed wagons — up to **7 years old**. (Under DriveXpress this agricultural list sits under Category C instead, and doesn't include windrowers.) |
| C (Replacement only) | Government / school / local route buses (excludes charter); up to 5 years old; up to **10-year loan term** |

**Key difference from DriveXpress:** don't assume Replacement's Category B/C split matches DriveXpress's — Replacement adds tippers/dump trucks to the heavy-equipment list, folds the agricultural-equipment list into "B" (at 7 years, with windrowers added) rather than "C", and reserves "C" solely for buses.

**Replacement criteria:**
- > 2 years in business with valid ABN and currently GST registered
- Statutory obligations up to date; no payment arrangements
- Borrower(s) and guarantor(s) have satisfactory credit bureau reports and ASIC search
- Monthly repayments within **125% of payment being replaced** (new-to-bank customers)
- Monthly repayments within **150% of payment being replaced** (existing customers)
- Ability to replace multiple contracts with one singular contract or vice versa (e.g. replace a truck for 2 trailers)
- Contract being replaced must have been finalised within the last **6 months / on settlement**
- Contract being replaced must have been operating for a **minimum of 12 months** and conducted within arrangements
- Borrower(s) and guarantor(s) must be the same as, or additional to, the contract being replaced

---

## chunk_id: westpac_medical
**source:** westpac
**topic:** medical_channel_policy
**intent:** MEDICAL_PROGRAMS
**lenders:** WESTPAC
**borrower_profile:** COMMERCIAL, MEDICAL_PROFESSIONAL, NEW_CLIENT, PROPERTY_BACKED
**asset_class:** MV_NEW, MV_USED, MEDICAL_EQUIP, OFFICE_EQUIP
**doc_type:** LOW_DOC
**loan_size_band:** MEDIUM, LARGE
**answerable_questions:** What are the Medical channel limits for specialists vs allied health? Which professions qualify? Are pharmacists included? What are cumulative approval caps?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** MAX_LOAN, PROPERTY_REQUIRED
**trigger_words:** medical, doctor, GP, dental, dentist, vet, veterinarian, allied health, physiotherapist, optometrist, chiropractor, audiologist, podiatrist, psychologist, speech pathologist, medical equipment loan, medical specialist, medical channel

**Content:**

The Medical channel provides specialist finance for healthcare professionals with reduced documentation requirements.

**Eligible professions:**
- Medical Specialist, GP, Dental and Vet (higher limits)
- Allied Health Practitioners: Occupational Therapists, Optometrists, Osteopaths, Physiotherapists, Chiropractors, Audiologist, Pathology services, Podiatrist, Psychologist, Speech Pathologist
- **Excluded:** Pharmacists

**Loan limits:**

| Asset Type | Medical Specialist / GP / Dental / Vet | Allied Health Practitioner |
|-----------|--------------------------------------|--------------------------|
| Motor vehicle (≤ 5 years old) + New office equipment and fittings | < $250,000 (combined cap for these two) | < $150,000 (combined cap — see note below) |
| New medical equipment | < $350,000 (separate, additional cap) | included in the < $150,000 combined cap above |
| **Max cumulative approvals** | **< $500,000** | **< $250,000** |

**Note:** For Medical Specialist/GP/Dental/Vet, motor vehicle and office equipment share one combined $250,000 cap, while new medical equipment has its own separate $350,000 cap. For Allied Health Practitioners there is no separate/higher medical-equipment limit — motor vehicle, office equipment, and medical equipment all draw from a single combined $150,000 cap.

**Medical channel criteria:**
- **> 3 years industry experience** (required for both Medical Specialist/GP/Dental/Vet and Allied Health Practitioner)
- Borrower / Guarantor credit bureau satisfactory
- In business > 2 years and registered for GST
- Statutory obligations up to date; no payment arrangements
- New clients: Borrower/Guarantor owns residential property + minimum annual income $75k
- Sale and hire back permitted where < 30 days past date of acquisition
- Private sale permitted for motor vehicles
- Borrower must sign Affordability Declaration

**Eligible Allied Health Practitioners include:**
Occupational Therapists, Optometrists, Osteopaths, Physiotherapists, Chiropractors, Audiologist, Pathology services, Podiatrist, Psychologist and Speech Pathologist. Pharmacists are NOT included.

---

## chunk_id: westpac_xpress_rates
**source:** westpac
**topic:** xpress_interest_rates
**intent:** PRICING
**lenders:** WESTPAC
**borrower_profile:** COMMERCIAL
**asset_class:** MV_NEW, MV_USED, EV, LCV, PRIMARY
**doc_type:** LOW_DOC
**loan_size_band:** ALL
**answerable_questions:** What is the Xpress rate for a car by term (dealer vs private sale)? What is the heavy-equipment Xpress rate? What EV discount applies? What is the max brokerage?
**confidence:** high
**last_verified:** 2026-07-29
**policy_fields:** BASE_RATE, EV_DISCOUNT, PRIVATE_SALE_LOADING, BROKERAGE_MAX
**trigger_words:** Xpress rate, DriveXpress rate, car rate, light commercial rate, motor vehicle rate, truck rate, heavy equipment rate, Xpress pricing, fast track rate, dealer rate, private sale Xpress rate, electric vehicle Xpress rate, EV Xpress

**Content:**

**VALID FROM: Monday 13 July 2026** (re-issued from 15 June 2026 — same effective date reset only, all rates below unchanged)
Rates valid for 7 days subject to settlement within this period.
Excludes: Novated Leases / Sale & Hirebacks.
Brokerage limited to a maximum of **3%**.

**Cars & Light Commercial Vehicles (< 4.5T GVM):**

| Channel | Term | Rate |
|---------|------|------|
| Licensed Dealers — up to 5 years old | 24 / 36 / 48 months | **7.75%** |
| Licensed Dealers — up to 5 years old | 60 months | **7.85%** |
| Private Sales — up to 5 years old | 24 / 36 / 48 months | **8.17%** |
| Private Sales — up to 5 years old | 60 months | **8.37%** |

**Trucks / Commercial Vehicles > 4.5T, Forklifts, Telehandlers, Boom/Scissor/Spider Lifts, Trailers, Excavators, Skid Steer/Wheel Loaders, Backhoe Loaders, Graders, Scrapers, Dozers and Rollers (Licensed Dealers, up to 5 years old):**

| Term | Rate |
|------|------|
| 24 / 36 / 48 months | **8.17%** |
| 60 months | **8.37%** |

**Agricultural Equipment (Tractors, Headers, Harvesters, Cotton Pickers, Balers, Mower Conditioners, Ploughs, Seeders, Sprayers, Spreaders, All-Terrain Vehicles and Feed Wagons — Licensed Dealers, up to 7 years old):**
Rate: same as heavy equipment category above.

**Mobile/Tight Access Cranes (Licensed Dealers, up to 3 years old):**
Rate: same as heavy equipment category above.

**Electric Vehicle discount:** Reduce applicable rate by **–1%** for all electric vehicles.

*Xpress Private Sales applicable for Cars/Light Commercial only.*

---

## chunk_id: westpac_standard_rates
**source:** westpac
**topic:** standard_wef_interest_rates
**intent:** PRICING
**lenders:** WESTPAC
**borrower_profile:** COMMERCIAL
**asset_class:** MV_NEW, MV_USED, EV, PRIMARY
**doc_type:** FULL_DOC
**loan_size_band:** MICRO, SMALL, MEDIUM
**answerable_questions:** What is the standard rate for a new motor vehicle / plant by amount and term? What is the used-vehicle loading? What EV discount applies?
**confidence:** high
**last_verified:** 2026-07-29
**policy_fields:** BASE_RATE, EV_DISCOUNT
**trigger_words:** standard WEF rate, hire purchase rate, commercial loan rate, finance lease rate, new motor vehicle rate, new plant equipment rate, standard rate table, monthly repayment rate, $15k rate, $20k rate, $50k rate, $150k rate, used vehicle loading

**Content:**

**VALID FROM: Monday 13 July 2026** (re-issued from 15 June 2026 — same effective date reset only, all rates below unchanged)
Rates valid for 7 days subject to settlement within this period.
Product types: **Hire Purchase, Commercial Loan and Finance Lease**.
Rates quoted are for **MONTHLY repayment structures only**.
Rates exclude Xpress deals.
Rates can be used for brokerage up to **3%**; base rate for additional brokerage (up to **4%**) by negotiation.

**New Motor Vehicles — Up to 4 Years Old (Cars, Vans, Utes, Trucks and Trailers):**

| Amount Financed | 24–36 months | 48 months | 60 months |
|----------------|-------------|----------|----------|
| $15,000–$20,000 | 9.97% | 9.97% | 10.17% |
| $20,000–$50,000 | 8.42% | 8.52% | 8.67% |
| $50,000–$150,000 | 8.32% | 8.42% | 8.62% |
| $150,000+ | By negotiation | By negotiation | By negotiation |

**New Plant and Equipment (Excluding Computers, Fixtures & Fittings):**

| Amount Financed | 24–36 months | 48 months | 60 months |
|----------------|-------------|----------|----------|
| $15,000–$20,000 | 10.22% | 10.36% | 10.56% |
| $20,000–$50,000 | 8.72% | 8.86% | 9.06% |
| $50,000–$150,000 | 8.52% | 8.62% | 8.82% |
| $150,000+ | By negotiation | By negotiation | By negotiation |

**Adjustments:**
- Used motor vehicles between **4 to 10 years old**: ADD **0.75%** to applicable rate
- **Electric vehicles**: reduce applicable rate by **–1%**
- For all other terms and structures: call for a quote

---

## chunk_id: westpac_settlement
**source:** westpac
**topic:** settlement_requirements
**intent:** SETTLEMENT
**lenders:** WESTPAC
**borrower_profile:** COMMERCIAL
**asset_class:** MV_NEW, MV_USED, LCV, PRIMARY
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What is required to settle? When is a Certificate of Currency needed and what is the fleet-policy exemption? When is a PPSR search not required?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** PPSR
**trigger_words:** settlement, PPSR, VIN, Certificate of Currency, CoC, fleet policy, insurance, settlement documents, biometrics, QuickSell, DriveOnline, settle loan Westpac, what do I need to settle

**Content:**

**Standard settlement requirements (all channels):**
- All payout documents submitted via QuickSell / DriveOnline
- Completion of biometrics (link provided in approval confirmation)
- Vehicle must be insured with Westpac noted as an interested party; insurance details loaded in QuickSell / DriveOnline
- Vehicle tax invoice or private sale agreement
- Documents to support any other conditions of approval
- Loan documents must be fully signed (ink signature or e-sign)

**Certificate of Currency (CoC) — assets above $150k:**
- CoC required to confirm insurance details
- Must note Westpac's interest
- **Updated rule (effective 24 February 2025):** Where the CoC confirms the policy is a "fleet policy", there is no longer a requirement to include the specific asset VIN/serial number on the CoC. Applies to motor vehicles only — does not apply to any other asset types.

**PPSR — Updated rule (effective 24 February 2025):**
Where the financed asset is a motor vehicle with a VIN and the sale is a buyback or private sale:
- A PPSR company search over the private seller or customer is **no longer required**
- This removes the need for a PPSR deed of release in most cases

**Conditions for PPSR exemption:**
- The asset must have a VIN (all other serial number types such as PIN, HIN, VH number etc. follow the existing process)
- A search on the day before or the day of the sale/lease must not disclose another registration over that VIN

---

## chunk_id: westpac_exclusions
**source:** westpac
**topic:** exclusions_and_restrictions
**intent:** EXCLUSIONS
**lenders:** WESTPAC
**borrower_profile:** COMMERCIAL
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** Is this loan structure or asset excluded? Are private sales allowed for heavy equipment? What geographic restrictions apply? What if DriveXpress criteria aren't met?
**confidence:** high
**last_verified:** 2026-06-28
**policy_fields:** ASSET_AGE_MAX
**trigger_words:** excluded, not eligible, novated lease, sale and hireback, charter bus, import car, exotic car, taxi, hire car, repairable writeoff, minus equity, remote area, very remote, private sale excluded, Westpac exclusions

**Content:**

**Excluded loan structures (all channels):**
- Novated leases
- Sale and hirebacks (exception: Medical channel permits if < 30 days past acquisition date)

**Excluded vehicles/assets:**
- Taxis and hire cars
- Imported and exotic cars (Category A)
- Computers and IT hardware (excluded from Standard Plant & Equipment rates)
- Fixtures and fittings (excluded from Standard Plant & Equipment rates)
- Charter buses (Replacement channel Category C accepts government/school/local route buses only)

**Private sale restrictions:**
- Private sales available for **Category A assets only** (passenger cars and light commercial < 4.5T GVM)
- Not available for Category B (heavy equipment) or Category C (agriculture)

**Asset-specific restrictions:**
- Modifications and aftermarket accessories: funded portion must not exceed **10% of dealer invoice/purchase price**
- Tractor/yellow goods attachments: cannot be funded separately; must be funded together with the primary asset
- No minus equity on trade-ins

**If DriveXpress criteria not met:**
- Must apply via standard application process
- Last 2 years financials + 2 years directors' ITRs required

