# Metro Finance — Policy Chunks
#
# source        : metro
# documents     : Commercial Asset Finance Rate Sheet (01/04/2026)
#                 Passenger Vehicle Streamlined Product (R1)
#                 Trucks, Trailers & Wheeled Equipment Streamlined Product (R1)
#                 Agri Streamlined Product (R1)
#                 Other Equipment Streamlined Product (R1)
#                 Replacement Policy Streamlined Product (R1)
#                 Balloon / Residual Refinance Streamlined Product (R1)
#                 MetroEco Booklet
# effective     : 01 April 2026 (rate sheet); streamlined products R1
# licence       : not stated in source documents
# ABN           : 85 650 102 891
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
# When Metro publishes a new rate sheet or streamlined product update:
# 1. Update the affected chunk(s) only
# 2. Bump `last_updated` and `version` in the file header
# 3. Re-embed only the changed chunks (use chunk_id to identify)
# 4. Do NOT change chunk_id values — they are the stable keys
#    used by the vector database

---

## chunk_id: metro_interest_rates
**source:** metro
**topic:** interest_rates
**intent:** PRICING
**lenders:** METRO
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, NON_PROPERTY_BACKED
**asset_class:** MV_NEW, MV_USED, LCV, PRIMARY, SECONDARY
**doc_type:** ALL
**loan_size_band:** MICRO, SMALL, MEDIUM, LARGE
**answerable_questions:** What is Metro's rate for a passenger vehicle / heavy commercial / wheeled plant? What loadings apply for older assets or private sale? How does brokerage affect the rate?
**confidence:** high
**last_verified:** 2026-07-29
**trigger_words:** Metro rate, Metro interest rate, Metro prime rate, Metro pricing, Metro passenger vehicle rate, Metro heavy commercial rate, Metro wheeled plant rate, Metro loading, Metro brokerage rate

**Content:**

Metro Finance Commercial Asset Finance rate sheet, effective 20/07/2026 (updated from a prior 01/04/2026 sheet — see change note below). Rates shown for 24–60 month terms.

| Asset type | Amount | 24–60 months |
|-----------|--------|-------------|
| Passenger & Commercial Vehicles (<12t GVM) up to 5 years | > $20k | 8.20% |
| Passenger & Commercial Vehicles (<12t GVM) up to 5 years | > $10k < $20k | 9.00% |
| Heavy Commercial Vehicles (above 12t GVM) & trailers up to 5 years, AND Wheeled Plant & Equipment (up to 5 years) — now one shared rate | > $20k | 8.45% |
| Heavy Commercial Vehicles (above 12t GVM) & trailers up to 5 years, AND Wheeled Plant & Equipment (up to 5 years) — now one shared rate | > $10k < $20k | 10.15% |

**Change note (20/07/2026 sheet vs the prior 01/04/2026 sheet):** all rates decreased (Passenger/Commercial 8.35%→8.20% and 9.15%→9.00%), AND Heavy Commercial Vehicles and Wheeled Plant & Equipment — previously two separate rate rows (8.60%/10.30% and 8.65%/10.40%) — are now merged into a single shared rate (8.45%/10.15%). Don't quote the old split rates for Heavy Commercial vs Wheeled Plant; check which sheet is current before quoting.

**8.20% Prime Rate** — vehicle < 5 years old streamline product:
- Rate applies to dealer sale
- All passenger and commercial vehicles < 12t GVM
- Vehicles > $20k
- Call your BDM for rates over $250k

**Loadings (also reduced on the 20/07/2026 sheet):**
- Assets older than 5 years at beginning of term: add extra 0.25% (was 0.75% on the prior sheet)
- Assets older than 10 years at end of term: add extra 1.00% (was 1.50%)
- Private sale: add extra 0.25% (unchanged)
- Sale / hire backs: add extra 0.75% (unchanged)
- Other equipment: add 1% to wheeled equipment rate (was 2% on the prior sheet)
- 1% loading on vehicle streamlined non-property product (unchanged)
- Above rates applicable for 4% brokerage — add 0.5% base rate for every 1.0% of brokerage (unchanged)

**MetroEco note newly added to this rate sheet:** mentions a 1% discount for new EVs up to $91,661, 1% for eligible wheeled equipment, and 1% for batteries/chargers/solar (wheeled equipment rate +2% loading). This $91,661 EV cap does not match the $91,387 figure in the separate MetroEco product booklet (metro_eco chunk) — that booklet's own content is otherwise unchanged from its prior version, so this looks like a genuine cross-document figure conflict rather than an update to the booklet itself. Flag both figures and confirm the current cap with Metro directly rather than picking one.

**Brokerage:**
- Advertised rates applicable for brokerage up to 4%
- Above 4.0%: add 0.5% for every 1% brokerage

**Loan sizes:** Single assets $1m and customer exposure $2m.

**Fees:** Metro minimum $275; maximum $450 excluding split 50/50.

---

## chunk_id: metro_passenger_vehicle_streamlined
**source:** metro
**topic:** passenger_vehicle_streamlined_product
**intent:** SPECIAL_PROGRAMS
**lenders:** METRO
**borrower_profile:** COMMERCIAL, NEW_CLIENT, EXISTING_CLIENT, PROPERTY_BACKED, NON_PROPERTY_BACKED, SPOUSE_OWNED
**asset_class:** MV_NEW, MV_USED, LCV
**doc_type:** LOW_DOC
**loan_size_band:** MEDIUM, LARGE
**answerable_questions:** What is Metro's passenger vehicle streamlined limit by property status? What exposure applies to new vs existing customers? What deposit for non-property backed? What are taxi/Uber limits?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Metro passenger vehicle, Metro streamlined vehicle, Metro car loan, Metro 3.5t GVM, Metro non-property backed vehicle, Metro taxi Uber, Metro spouse property vehicle

**Content:**

Metro's Passenger Vehicle Streamlined Product covers vehicles under 3.5t GVM. Property equity must be scaled to be greater than the NAF.

| Property ownership | Maximum loan size | Maximum Metro exposure (incl. existing) |
|-------------------|------------------|----------------------------------------|
| In the borrower or guarantor's name | $150,000 (dealer and private sale); $200,000 for customers with 12 months good repayment history with Metro (dealer and private sales) | New Metro customers $250,000; $500,000 exposure for customers with 12 months good repayment history with Metro; $750,000 exposure for customers with 24 months good repayment history with Metro |
| In spouse's name | $150,000 (dealer and private sale) | $150,000 |
| Non-property backed (motor vehicles only) | $100,000 (dealer sale only, 30% deposit required) | $100,000 |

**Other criteria:**
- Business GST registration: registered 2 years continuously
- Comparable credit reference on a current or previous asset finance (within the last 12 months). 12 months mortgage statements acceptable (if no reference available) for amounts up to $100,000
- Age of asset at end of term: no older than 12 years at end of term
- Credit reference from reputable finance company running at least 12 months with satisfactory conduct
- Supplier can be a licensed dealer or private sale (no sale/hire back)
- Satisfactory Equifax on applicant and guarantors
- Goods being purchased are of the type normally used by the business as part of its normal trading activities
- For increased streamline exposure, applicant required to have a current Metro contract or a contract paid out within the past 6 months
- Credit reserves the right to request further information
- Maximum $500,000 in a 12 month period under streamlined
- Taxi / Uber / ride share applications: maximum customer exposure $250,000 and must be property backed

---

## chunk_id: metro_trucks_trailers_streamlined
**source:** metro
**topic:** trucks_trailers_wheeled_equipment_streamlined
**intent:** SPECIAL_PROGRAMS
**lenders:** METRO
**borrower_profile:** COMMERCIAL, NEW_CLIENT, EXISTING_CLIENT, PROPERTY_BACKED, NON_PROPERTY_BACKED, SPOUSE_OWNED
**asset_class:** PRIMARY, LCV
**doc_type:** LOW_DOC
**loan_size_band:** MEDIUM, LARGE
**answerable_questions:** What is Metro's truck and trailer streamlined limit? Are prime movers included? What is the max asset age at end of term? What eligible assets qualify?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Metro truck, Metro trailer, Metro wheeled equipment, Metro heavy commercial, Metro yellow goods, Metro earthmoving, Metro material handling, Metro excludes prime movers

**Content:**

Metro's Trucks, Trailers & Wheeled Equipment Streamlined Product covers medium & heavy commercial vehicles above 3.5t GVM, **excluding prime movers**. Property equity must be scaled to be greater than the NAF.

| Property ownership | Maximum loan size | Maximum Metro exposure (incl. existing) |
|-------------------|------------------|----------------------------------------|
| In the borrower or guarantor's name | $250,000 dealer and private sale for new customers; $300,000 for customers with 12 months good repayment history with Metro. Maximum transaction size of $250,000 for private sales | New Metro customers $250,000; $500,000 exposure for customers with 12 months good repayment history with Metro; $750,000 exposure for customers with 24 months good repayment history with Metro |
| In spouse's name | $150,000 (dealer and private sale) | $150,000 |
| Non-property backed (motor vehicles only) | $100,000 (dealer sale only, 30% deposit required) | $100,000 |

**Other criteria:**
- Business GST registration: registered 2 years continuously
- Comparable credit reference on a current or previous asset finance (within the last 12 months on similar assets)
- Age of asset at end of term: no older than 15 years at end of term — no balloons or residuals for lends out to 15 years at end of term
- Credit reference from reputable finance company running at least 12 months with satisfactory conduct
- Supplier can be a licensed dealer or private sale (no sale/hire back)
- Satisfactory Equifax on applicant and guarantors
- Goods being purchased are of the type normally used by the business as part of its normal trading activities
- For increased streamline exposure, applicant required to have a current Metro contract or a contract paid out within the past 6 months
- Maximum $500,000 in a 12 month period under streamlined

**Eligible assets:** 3.5t GVM +, vehicles, trailers, earthmoving equipment, yellow goods, material handling equipment.

---

## chunk_id: metro_agri_streamlined
**source:** metro
**topic:** agri_streamlined_product
**intent:** SPECIAL_PROGRAMS
**lenders:** METRO
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, EXISTING_CLIENT, ABN_OVER_6YR
**asset_class:** PRIMARY, TERTIARY
**doc_type:** LOW_DOC
**loan_size_band:** MEDIUM, LARGE
**answerable_questions:** What is Metro's agri streamlined limit? What GST registration is required for agri? What is the minimum farm size? Which agricultural assets are excluded? What repayment frequency applies to Agri streamlined?
**confidence:** high
**last_verified:** 2026-07-29
**trigger_words:** Metro agri, Metro agriculture, Metro tractor, Metro harvester, Metro farm, Metro primary producer, Metro implements, Metro dairy excluded, Metro irrigation excluded, Metro monthly payments only

**Content:**

Metro's Agri Streamlined Product. Property equity must be scaled to be greater than the NAF.

**Primary Equipment (in the borrower or guarantor's name):**
- $10,000 minimum; $250,000 maximum dealer/private sale
- $300,000 maximum for customers with 12 months good history of repayments with Metro
- Maximum Metro exposure: new Metro customers $250,000; Metro customers with 12 months history $500,000; $750,000 exposure for customers with 24 months good repayment history with Metro
- Business GST registration: GST registered > 5 years
- Comparable credit reference on a current or a previous asset finance (within the last 12 months on a similar asset)
- Age of asset: no older than 15 years at end of term — no balloons or residuals for lends out to 15 years at end of term
- Maximum term 60 months
- Eligible assets: tractors, harvesters, wheeled handling equipment, self-propelled mower conditioners, self-propelled sprayers

**Implements / Tertiary Equipment (in the borrower or guarantor's name):**
- $10,000 minimum; $150,000 maximum dealer/private sale
- New and existing Metro customers: $150,000
- Business GST registration: GST registered > 5 years
- Comparable credit reference on a current or a previous asset finance (within the last 12 months on a similar asset)
- Age of asset: no older than 15 years at end of term
- Maximum term 60 months / nil balloon
- Eligible assets: tillage seeding, spraying, grain handling hay & silage

**Non-eligible assets and conditions:**
- Must be genuine primary producer
- Minimum farm size 40 ha
- Maximum $500,000 in a 12 month period under streamlined
- No sale/hire back
- Satisfactory Equifax on applicants/guarantors
- Goods being purchased are of the type normally used by the business as part of its normal trading activities
- Goods are required to be serial numbered and cannot be fixed
- **Monthly payments only** (no other repayment frequency under this streamlined product)
- Excluded: sheds, silos, yards; testing and measurement equipment (can be done under "Other Equipment" streamlined policy < $100k); dairy equipment; irrigation equipment; bikes & ATVs (ATVs can be done under "Other Equipment" streamlined policy < $100k); forestry industry and assets

---

## chunk_id: metro_other_equipment_streamlined
**source:** metro
**topic:** other_equipment_streamlined_product
**intent:** SPECIAL_PROGRAMS
**lenders:** METRO
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED
**asset_class:** SECONDARY, TERTIARY
**doc_type:** LOW_DOC
**loan_size_band:** SMALL, MEDIUM
**answerable_questions:** What is Metro's Other Equipment streamlined limit? What asset age applies? Which equipment is eligible vs non-eligible? Is private sale allowed?
**confidence:** high
**last_verified:** 2026-07-29
**trigger_words:** Metro other equipment, Metro tools of trade, Metro manufacturing equipment, Metro workshop equipment, Metro non-eligible equipment, Metro no private sale equipment, Metro CNC, Metro drones, Metro racking, Metro scaffolding

**Content:**

Metro's Other Equipment Streamlined Product. Property equity must be scaled to be greater than the NAF.

**Primary Equipment (in the borrower or guarantor's name):**
- Age of asset: no older than 3 years; asset must be serial numbered
- Maximum loan size: $10,000 minimum; $100,000 maximum
- Maximum Metro exposure: $100,000 including current Metro exposure
- Comparable credit reference: registered 2 years continuously; comparable credit reference on a current or previous asset finance (within the last 12 months on similar assets)

**Conditions:**
- Credit reference from reputable finance company running at least 12 months with satisfactory conduct
- Must be from a recognised supplier (**no private sale or sale/hire back**)
- Satisfactory Equifax on applicant and guarantors
- For increased streamline exposure, applicant required to have a current Metro contract or a contract paid out within the past 6 months
- Maximum term 60 months nil
- Credit reserves the right to request further information
- Goods being purchased are of the type normally used by the business as part of its normal trading activities

**Eligible assets:** tools of trade; earthmoving & construction equipment; manufacturing & workshop equipment; agricultural and forestry equipment. Eligible Equipment Guide (illustrative, not exhaustive): attachments, surveying equipment, large engineering equipment, manufacturing lines, packing/robotic packaging/wrapping/weighing equipment, workshop equipment, vacuum excavators, CNC, dust extractors, dustless sandblasters, edge banders, lasers, lathes, machining centres, ATVs, augers, pumps and power equipment, direction drills, farming implements & machinery, feeding equipment, grain handling, portable dipping/testing, GPS equipment, generators/welders/pumps/plumbing equipment, dynamometers, radios (UHF/VF/HF), routers, medical and dental equipment, panel saws.

**Non-eligible assets:** fixtures & fittings; IT, AV, telephony & printing; retail, health/beauty & fitness; mining; intangible assets. Also (illustrative, not exhaustive): air conditioning units & ducting, audio visual equipment, blinds, carpets, catering, coffee machines, desks, display units, drones, furniture, gym equipment, kitchen, LED lighting, partitions, printers, racking (fixed and freestanding), safes and strong rooms, scaffolding, solar (has its own MetroEco product — see metro_eco).

---

## chunk_id: metro_replacement_policy
**source:** metro
**topic:** replacement_policy
**intent:** ROLLOVER_REPLACEMENT
**lenders:** METRO
**borrower_profile:** COMMERCIAL, NEW_CLIENT, EXISTING_CLIENT, PROPERTY_BACKED, NON_PROPERTY_BACKED, SPOUSE_OWNED
**asset_class:** MV_NEW, MV_USED, LCV, PRIMARY
**doc_type:** LOW_DOC
**loan_size_band:** MEDIUM, LARGE
**answerable_questions:** What is Metro's replacement policy limit? What repayment increase is allowed? How long must the replaced contract have run? Are prime movers excluded?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Metro replacement, Metro replace contract, Metro 125%, Metro refinance replacement, Metro 36 months contract, Metro replacement criteria

**Content:**

Metro's Replacement Policy Streamlined Product.

| Property ownership | Maximum loan size | Maximum Metro exposure (incl. existing) |
|-------------------|------------------|----------------------------------------|
| In the borrower or guarantor's name | $150,000 for passenger vehicles & light commercial (dealer and private sales); $300,000 for medium & heavy commercial (excludes prime movers), trailers & wheeled equipment (dealer sales). Maximum transaction size of $250,000 for private sales | $300,000 (new customers); $500,000 exposure for customers with 12 months of good repayment history with Metro; $750,000 exposure for customers with 24 months good repayment history with Metro |
| In spouse's name | $150,000 | $150,000 |
| Non-property backed | $100,000 for both dealer & private sales | $100,000 |

**Criteria:**
- Business GST registration: must have ABN with current GST registration (does not need to be 24 months)
- Comparable credit reference: satisfactory credit reference on account being refinanced. Contracts being replaced must have run for a **minimum of 36 months**
- Age of asset at end of term: passenger vehicles and light commercials — no older than 12 years at end of term; all other equipment — no older than 15 years at end of term (no balloons or residuals for lends out to 15 years at end of term)

**Replacement criteria:**
- New loan amount not to exceed **125%** of the original loan amount of the contract being replaced, **or**
- Proposed monthly repayment does not exceed **125%** of the monthly repayment of the contract being replaced

**Conditions:**
- Credit reference from reputable finance company running at least 12 months with satisfactory conduct
- Supplier can be a licensed dealer or private sale (no sale/hire back)
- Satisfactory Equifax on applicants and guarantors
- Goods being purchased are of the type normally used by the business as part of its normal trading activities
- For increased streamline exposure, applicant required to have a current Metro contract or a contract paid out within the past 6 months
- Maximum $500,000 in a 12 month period under streamlined

---

## chunk_id: metro_balloon_refinance
**source:** metro
**topic:** balloon_residual_refinance
**intent:** ROLLOVER_REPLACEMENT
**lenders:** METRO
**borrower_profile:** COMMERCIAL, NEW_CLIENT, EXISTING_CLIENT, PROPERTY_BACKED, NON_PROPERTY_BACKED, SPOUSE_OWNED
**asset_class:** MV_NEW, MV_USED, PRIMARY, PRIME_MOVER
**doc_type:** LOW_DOC
**loan_size_band:** MEDIUM, LARGE
**answerable_questions:** Can I refinance a balloon or residual with Metro? What is the limit? Are prime movers included? When must the account being replaced be?
**confidence:** medium
**last_verified:** 2026-07-09
**trigger_words:** Metro balloon refinance, Metro residual refinance, Metro balloon, Metro final 12 months, Metro prime movers included balloon, Metro no inspection

**Content:**

Metro's Balloon / Residual Refinance Streamlined Product.

| Property ownership | Maximum loan size | Maximum Metro exposure (incl. existing) |
|-------------------|------------------|----------------------------------------|
| In the borrower or guarantor's name | $150,000 | $300,000 (new customers); $500,000 exposure for customers with 12 months good repayment history with Metro; $750,000 exposure for customers with 24 months good repayment history with Metro |
| In spouse's name | $150,000 | $150,000 |
| Non-property backed | $150,000 | $150,000 |

**Criteria:**
- Business GST registration: registered 2 years continuously
- Comparable credit reference: satisfactory credit reference on the account being refinanced
- Age of asset at end of term: passenger vehicles and light commercials — no older than 12 years at end of term; all other equipment — no older than 15 years at end of term (no balloons or residuals for lends out to 15 years at end of term)
- **Account being replaced must be in its final 12 months**
- For motor vehicles & wheeled equipment only — **prime movers included**

**Conditions:**
- Credit reference from reputable finance company running at least 12 months
- **No inspection required**
- Satisfactory Equifax on applicant and guarantors
- Goods being purchased are of the type normally used by the business as part of its normal trading activities & legitimate commercial purposes
- For increased streamline exposure, applicant required to have a current Metro contract or a contract paid out within the past 6 months
- Credit reserves the right to request further information
- Maximum $500,000 in a 12 month period under streamlined

*Note: this chunk is transcribed from a scanned source document (OCR). Verify exact figures with Metro before relying on them for a live deal.*

---

## chunk_id: metro_eco
**source:** metro
**topic:** metroeco_green_products
**intent:** SPECIAL_PROGRAMS
**lenders:** METRO
**borrower_profile:** COMMERCIAL, CONSUMER, PROPERTY_BACKED
**asset_class:** EV, PRIMARY, SOLAR
**doc_type:** LOW_DOC
**loan_size_band:** MEDIUM, LARGE
**answerable_questions:** What is MetroEco? What discount applies to electric vehicles and trucks? What loan terms are available for EVs and solar? What is the max loan amount for an EV?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** MetroEco, Metro electric vehicle, Metro EV, Metro electric truck, Metro solar, Metro battery, Metro charger, Metro green, Metro CEFC, Metro rate discount

**Content:**

MetroEco is Metro Finance's green product suite, supported by a relationship with the CEFC, covering electric vehicles, electric trucks, and solar/batteries/chargers.

**MetroEco Electric Vehicles & Chargers:**
- Bundle assets on the one application and get the vehicle carded rate
- MetroEco rate discount applies
- Approvals valid for 90 days
- FBT exemptions apply to novated leasing

| | Commercial | Consumer | Novated |
|---|-----------|---------|--------|
| Loan amount | Up to $91,387.00 on vehicles | Up to $91,387.00 on vehicles | Up to $91,387.00 on vehicles |
| Loan term | 60 months — max EOT 5 years | 84 months — max EOT 7 years | 60 months — max EOT 5 years |
| Age of asset | New or Demo | New or Demo | New or Demo |
| Supplier | Dealer | Dealer | Dealer |

The loan term depends on which of these three borrower types the applicant is: a **Consumer** borrower gets up to 84 months (max 7-year end-of-term) — the longest of the three. A **Commercial** business borrower or a **Novated** lease both get up to 60 months (max 5-year end-of-term) instead. If the borrower type isn't stated, give both the Consumer and Commercial figures rather than assuming one.

Eligibility: electric vehicle, where the vehicle is solely powered by electricity and uses an external electrical plug to charge the battery. Demonstrator electric motor vehicle not more than 12 months old, and odometer not more than 5,000 km.

**Cross-document conflict:** the separate Commercial Rate Sheet (effective 20/07/2026, see metro_interest_rates) states this same EV loan cap as **$91,661**, not $91,387. This booklet's own content is unchanged from its prior version; the rate sheet's figure is more recently dated. Flag both figures rather than confidently quoting one — confirm the current cap with Metro directly.

**MetroEco Electric Trucks (streamlined product) — 1% MetroEco rate discount applies:**
- Brand new assets only; dealer sale
- Up to $250,000 for new customers
- Up to $300,000 for customers with 12 months good repayment history with Metro
- ABN & GST registered for a minimum of 2 years continuously
- Comparable credit reference on a current or previous asset finance facility (within the last 12 months on similar assets)
- Battery Electric Trucks only — 3.5t GVM and above
- Property owners only
- $600,000 maximum transaction size with full financials
- $700,000 maximum (electric truck) exposure
- Excludes biofuel powered or hybrid

**Solar / Batteries / Chargers (streamlined product):**
- Up to 7-year finance term (solar only)
- Bundle assets on the one loan application
- No loadings on 6 & 7 year loan terms
- MetroEco rate discount applies
- Approvals valid for 90 days

---

## chunk_id: metro_exclusions
**source:** metro
**topic:** exclusions_and_restrictions
**intent:** EXCLUSIONS
**lenders:** METRO
**borrower_profile:** COMMERCIAL
**asset_class:** ALL
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What does Metro not finance? Is sale and hire back allowed? What is the streamlined annual cap? Which equipment is non-eligible?
**confidence:** high
**last_verified:** 2026-07-09
**trigger_words:** Metro excluded, Metro not eligible, Metro sale hire back, Metro streamlined cap, Metro non-eligible assets, Metro prime mover exclusion, Metro forestry excluded

**Content:**

**Universal streamlined conditions:**
- No sale/hire back across streamlined products (a sale/hire back loading of 0.75% appears on the rate sheet for non-streamlined deals)
- Maximum $500,000 in a 12 month period under streamlined
- Satisfactory Equifax on applicants and guarantors
- Goods being purchased must be of the type normally used by the business as part of its normal trading activities
- Credit reserves the right to request further information

**Product-specific exclusions:**
- Trucks/Trailers streamlined: **excludes prime movers**
- Other Equipment streamlined: **no private sale or sale/hire back**; must be from a recognised supplier
- Agri streamlined: excludes sheds, silos, yards; testing and measurement equipment; dairy equipment; irrigation equipment; bikes & ATVs; forestry industry and assets. Must be a genuine primary producer with minimum farm size 40 ha. Goods must be serial numbered and cannot be fixed
- Passenger Vehicle streamlined: taxi / Uber / ride share applications capped at $250,000 customer exposure and must be property backed
- MetroEco Electric Trucks: excludes biofuel powered or hybrid; property owners only

**Non-eligible equipment (Other Equipment):** fixtures & fittings; IT, AV, telephony & printing; retail, health/beauty & fitness; mining; intangible assets; air conditioning units & ducting; audio visual equipment; blinds; carpets; catering; coffee machines.

**Non-property backed:** motor vehicles only, dealer sale only, 30% deposit required (streamlined vehicle and truck products); capped at $100,000.
