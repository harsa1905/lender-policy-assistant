# CMAP Policy Assistant — Concept FAQ & Glossary

**Purpose.** This file explains the main concepts that appear across the seven lender
policies in plain words, and — crucially — lists the **synonyms and keywords** brokers use
for each concept. It serves two audiences:

- **The AI model:** when a broker's question uses an unfamiliar phrase, the model can map
  that phrase to the right concept here, then retrieve the correct policy chunk. The
  synonym lists are effectively a translation layer from "broker language" to
  "policy language".
- **The team:** when any of us hits an unfamiliar term in a policy, this is the quick
  reference that explains it and shows what else it might be called.

**How to read each entry.** Every concept has: a plain-English **explanation**, a list of
**also called / synonyms & keywords** (the phrases a broker might actually type), a
**per-lender note** where the lenders differ, and the **related chunk topics** to retrieve.

**Lenders covered:** Resimac · BFS (Branded Financial Services) · Westpac (Westpac
Equipment Finance) · CFAL (Capital Finance Australia) · Angle Finance · Metro Finance ·
flexicommercial.

---

## 1. Interest rate

**Explanation.** The annual percentage cost of the finance, charged per annum on the
amount financed. Each lender publishes a base or carded rate that varies by customer tier,
asset class, asset age, term, and sale type. Loadings (extra percentages) are then added
for higher-risk features, and brokerage above a threshold can also lift the rate.

**Also called / synonyms & keywords:** rate, interest, p.a., per annum, APR, pricing,
cost of finance, carded rate, base rate, headline rate, advertised rate, what's the rate,
how much interest, finance rate, lending rate.

**Per-lender notes.**
- *Resimac* — rate depends on tier (PremiumPLUS is 25bps cheaper) and asset class; EVs get
  the lowest rate (7.54%).
- *Westpac / CFAL* — "Xpress rate" is the fast-track dealer rate (e.g. 7.75% dealer car);
  CFAL publishes **no** public rate (confirm with the Credit Manager).
- *flexicommercial* — "flexipremium" is the low rate tier (7.30% primary) for established
  businesses; "standard rates" is the base card.
- *Angle / Metro* — profile-based and carded rates respectively; Metro's "prime rate" is
  8.35% for eligible vehicles.

**Related chunk topics:** interest_rates, standard_interest_rates, flexipremium_product,
xpress rates, drivexpress.

---

## 2. Risk loading

**Explanation.** An extra percentage added to the base rate because a deal has a
higher-risk feature (e.g. a private sale, an old asset, a prime mover). Multiple loadings
can stack, usually up to a capped maximum.

**Also called / synonyms & keywords:** loading, rate loading, add-on, surcharge, premium,
margin add, extra rate, uplift, rate bump, penalty rate, loading cap, "does that add to
the rate", risk premium.

**Per-lender notes.**
- *Resimac* — +2% per trigger (private sale, classic car, asset >16yr at EOT, prime mover);
  capped at 4% per deal.
- *Metro* — 0.75% (asset >5yr at start), 1.50% (>10yr at EOT), 0.25% (private sale), 0.75%
  (sale/hire back), +2% other equipment, 1% streamlined non-property.
- *flexicommercial* — +1.0% (prime movers, 11–15yr, <24mo term, private sale/refinance),
  +1.25% (non-asset-backed, >60mo), +2.0% (15–20yr at EOT).
- *Angle* — 1% loading for prime movers and for terms over 60 months.

**Related chunk topics:** interest_rates, standard_interest_rates.

---

## 3. Brokerage

**Explanation.** The commission the broker earns, built into the amount financed. Each
lender sets a maximum brokerage and a threshold above which charging more brokerage lifts
the customer's rate.

**Also called / synonyms & keywords:** commission, broker fee, broker commission, my cut,
origination commission, brokerage cap, max brokerage, brokerage loading, "how much can I
charge", "how much commission", points.

**Per-lender notes.**
- *Resimac* — max 8.8% (incl GST); no impact up to 5.5%, then +0.5% rate per 1% (or part).
- *BFS* — max broker margin +6% over base; clawback 100% if paid out <12 months.
- *Metro* — up to 4% with no impact; above 4% add 0.5% per 1%.
- *flexicommercial* — <$50k: max 8% (impact above 5%); ≥$50k: max 6% (impact above 4%);
  flexipremium max 3%; mid-term refinance max 1%.
- *Angle* — up to 8% (incl GST); no loading for commission up to 8%.

**Related chunk topics:** fees_and_brokerage, fees, fees_and_commission.

---

## 4. Balloon / residual

**Explanation.** A lump sum deferred to the end of the loan term, reducing the monthly
repayments. Expressed as a percentage of the amount financed. Larger balloons are allowed
on shorter terms and newer assets; some asset classes can't have a balloon at all.

**Also called / synonyms & keywords:** balloon, balloon payment, residual, residual value,
RV, final payment, end-of-term payment, lump sum, deferred payment, balloon percentage,
"what balloon can I put on", nil balloon, 0% balloon.

**Per-lender notes.**
- *Resimac* — commercial only (excludes secondary, tertiary, classic cars); 36mo 50%/40%,
  48mo 45%/35%, 60mo 40%/30% (new / used-and-primary).
- *Angle* — max balloon 40% (36mo), 40% (48mo), 30% (60mo); 0% only at max EOT ages.
- *Metro* — many streamlined products are "no balloons or residuals" for long-EOT lends;
  a dedicated Balloon/Residual Refinance product exists (OCR, medium confidence).
- *flexicommercial* — standard residual value applies per policy.

**Related chunk topics:** asset_categories, loan_structure_and_terms,
balloon_residual_refinance.

---

## 5. NAF (Net Amount Financed)

**Explanation.** The amount actually financed, excluding fees and brokerage. Loan-size
limits and many caps are expressed against NAF, not the total contract value.

**Also called / synonyms & keywords:** NAF, net amount financed, amount financed, loan
amount, financed amount, principal, lend amount, "how much can I borrow", loan size,
amount funded, ex-brokerage amount.

**Per-lender notes.**
- *Resimac* — max NAF per passenger vehicle $250k; per motorbike $75k.
- *flexicommercial* — rates quoted on "amount funded (ex brokerage)".
- *Metro* — "scaled equity to be greater than the NAF" is the property-backing test.

**Related chunk topics:** loan_limits, credit_matrix_and_limits, loan_structure_and_terms.

---

## 6. Exposure limit vs loan limit

**Explanation.** Two different ceilings that are easy to confuse. **Loan (transaction)
limit** = the most that can be financed in a single deal. **Exposure limit** = the most a
customer can owe across *all* their contracts with that lender combined. A deal can pass
the transaction limit but fail the aggregate exposure cap.

**Also called / synonyms & keywords:** exposure, total exposure, aggregate exposure,
customer exposure, combined exposure, overall limit, "how much total", exposure cap,
transaction limit, per-deal limit, individual transaction, single transaction, "across all
their loans".

**Per-lender notes.**
- *Resimac* — SME $500k, large corporate $750k, A-rated/govt $2m total exposure; Low Doc
  aggregate $400k.
- *Westpac / CFAL* — DriveXpress per-deal by category (A/B/C) vs aggregate DriveXpress
  exposure ($750k existing).
- *flexicommercial* — Primary $750K total but individual transactions capped at $500K.
- *Metro* — exposure ladder $250k (new) / $500k (12mo) / $750k (24mo), including existing.

**Related chunk topics:** loan_limits, credit_matrix_and_limits, drivexpress,
passenger_vehicle_streamlined.

---

## 7. Property-backed / asset-backed

**Explanation.** Whether the borrower (or a guarantor) owns real property or sufficient
assets, used as a strength signal. Property-backed borrowers get better tiers, higher
limits and often no deposit. "Asset-backed" is the flexicommercial/Metro phrasing for the
same idea.

**Also called / synonyms & keywords:** property backed, asset backed, home owner,
homeowner, owns property, property owner, real estate backing, equity, bricks and mortar,
security property, non-property backed, non-asset backed, renter, no property, "do they
own a house", spousal property, spouse-owned.

**Per-lender notes.**
- *Resimac* — property-backed = ≥25% in a guarantor's name, equity ≥1× NAF, no adverse
  encumbrances; PremiumPLUS/Premium are property-backed only; spouse-owned (legally
  married, not de facto) waives a deposit but isn't property backing.
- *Angle* — spousal property accepted (marriage cert / Medicare / joint utility);
  non-property owners need 20% deposit.
- *flexicommercial* — asset-backed (4yr ABN) vs non-asset-backed (8yr ABN) for flexipremium;
  transport operators must be asset-backed.
- *Metro* — "scaled equity greater than the NAF"; non-property backed is MV-only, 30% deposit.

**Related chunk topics:** customer_tiers, property_ownership_and_deposits,
credit_matrix_and_limits.

---

## 8. Deposit

**Explanation.** Cash the borrower contributes up front, reducing the amount financed.
Usually required when the borrower is not property/asset-backed, or for higher-risk tiers.

**Also called / synonyms & keywords:** deposit, down payment, upfront, contribution,
cash in, equity contribution, "money down", "how much do they need to put in", 10% deposit,
20% deposit, 30% deposit, no deposit, deposit waiver.

**Per-lender notes.**
- *Resimac* — non-property backed: 10% (motor vehicles) / 20% (all other assets).
- *Angle* — non-property owners: 20% deposit.
- *Metro* — non-property backed MV: 30% deposit, dealer sale only.
- *BFS* — no-deposit up to 120% LVR; high-value ($250k–$400k) needs 20% deposit.
- *flexicommercial* — asset backing "or 20% deposit" per the credit matrix.

**Related chunk topics:** property_ownership_and_deposits, customer_tiers,
loan_limits_terms.

---

## 9. Documentation tiers (Low Doc / Lite Doc / Full Doc / Mid Doc)

**Explanation.** How much financial paperwork the deal needs. "Low Doc" is the lightest
(ID + basic statements), scaling up to "Full Doc" (full financials/tax returns). The
lighter the doc, the lower the loan-size ceiling. Naming varies by lender (Resimac uses
Lite Doc; Angle uses Mid Doc).

**Also called / synonyms & keywords:** low doc, lite doc, mid doc, full doc, no doc,
light doc, documentation, docs required, paperwork, financials, "what do I need to apply",
ATO portal, BAS, bank statements, financial statements, tax returns, accountant-prepared,
streamlined (Metro's low-doc-style products), doc tier, easy doc.

**Per-lender notes.**
- *Resimac* — Low / Lite / Full; Low Doc **not** available for tertiary assets.
- *Angle* — Low Doc (<$100k / $100k–$250k bands) / Mid Doc (<$500k) / Full Doc; prime
  movers can't use Low Doc.
- *Metro* — "streamlined products" are effectively low-doc (credit-reference based).
- *CFAL* — **no** Low Doc at all; documentation scales with transaction size.
- *BFS* — documentation types include New Business Ventures (<12mo ABN, $100k cap).

**Related chunk topics:** documentation, documentation_tiers, credit_matrix_and_limits,
documentation_matrix.

---

## 10. Customer tier / credit tier

**Explanation.** A banding of borrowers by strength (ABN age, GST age, credit score,
property status) that sets the rate, the maximum loan and sometimes the accepted property
types. Better tier = better pricing and higher limits.

**Also called / synonyms & keywords:** tier, customer tier, credit tier, grade, band,
pricing tier, PremiumPLUS / Premium / Standard / Basic (Resimac), Ultra Prime / Tier 1–4 /
BFS Plus (BFS), "which tier", "what grade", customer grade, risk grade, profile.

**Per-lender notes.**
- *Resimac* — PremiumPLUS / Premium / Standard / Basic, on ABN age + GST + property + score.
- *BFS* — Ultra Prime (960) / Tier 1 (800) / Tier 2 (600) / Tier 3 (550) / Tier 4 (400) /
  BFS Plus — scored on **Experian CCR**.
- *Angle* — profile-based (8yr/4yr ABN profiles) rather than named tiers.

**Related chunk topics:** customer_tiers.

---

## 11. Credit bureau / credit score (Equifax vs Experian)

**Explanation.** The credit-reporting agency whose score the lender uses to assess an
applicant. This matters because a score from one bureau does **not** translate directly to
another — a key source of errors when comparing lenders.

**Also called / synonyms & keywords:** credit score, credit bureau, Equifax, Experian,
CCR, comprehensive credit reporting, Veda (old name for Equifax), Veda 1:1, credit rating,
score, credit check, credit file, bureau score, "what score do they need".

**Per-lender notes.**
- *Resimac* — **Equifax**; uses the highest score among company/guarantors.
- *Metro* — **Equifax** ("satisfactory Equifax on applicants and guarantors").
- *BFS* — **Experian CCR** (Tier thresholds 400–960).
- *Angle* — **Veda 1:1** (Veda = Equifax's former name); 500–650 thresholds.

**Related chunk topics:** customer_tiers, documentation.

---

## 12. ABN / GST registration age

**Explanation.** How long the business has held an Australian Business Number and been
registered for GST. Longer registration = better tier and lower rate. Many products have a
minimum ABN/GST age; "start-up" products exist for businesses below the usual minimums.

**Also called / synonyms & keywords:** ABN age, ABN duration, years trading, time in
business, GST registered, GST registration, business age, "how long have they been
trading", established business, new business, ABN months, trading history, continuously
registered.

**Per-lender notes.**
- *Resimac* — PremiumPLUS >6yr ABN/>3yr GST; down to Basic >1yr.
- *flexicommercial* — flexipremium asset-backed 4yr, non-asset-backed 8yr; matrix >2yr.
- *Angle* — standard 2+yr ABN; Start-Up product for ABN <2yr.
- *Metro* — GST registered 2yr (most streamlined); Agri needs >5yr GST.
- *BFS* — New Business Ventures for <12 months ABN.

**Related chunk topics:** customer_tiers, credit_matrix_and_limits, start_up_product,
agri_streamlined_product.

---

## 13. Asset classes (Primary / Secondary / Tertiary)

**Explanation.** A three-way grouping of equipment by how easily it holds value and
resells. **Primary** = big, liquid assets (trucks, trailers, earthmoving) → best rates and
highest limits. **Secondary** = specialised gear (medical, engineering, generators) →
higher rates. **Tertiary** = soft/low-resale assets (IT, AV, fit-outs) → highest rates,
lowest limits, often no Low Doc.

**Also called / synonyms & keywords:** primary asset, secondary asset, tertiary asset,
asset class, asset category, asset type, asset tier, hard assets, soft assets, yellow
goods, "what category is", "how do you classify", primary/secondary/tertiary.

**Per-lender notes.**
- *Resimac* — primary (heavy trucks >4.5T, trailers, buses, prime movers, caravans),
  secondary (generators, medical, CNC), tertiary (AV, conveyors, skip bins, GPS).
- *flexicommercial* — detailed category lists; **does not fund SUVs/passenger cars,
  photocopiers, MFDs, scaffolding**; Tier II = Chinese-branded/electric trucks.
- *Angle* — primary / secondary / tertiary with EOT ages 25 / 15 / 10 years.

**Related chunk topics:** asset_categories, interest_rates, loan_limits.

---

## 14. Asset age at end of term (EOT)

**Explanation.** How old the asset will be when the loan finishes (asset's current age +
loan term). Lenders cap this to avoid financing an asset past its useful life. Also affects
whether a balloon is allowed and whether a rate loading applies.

**Also called / synonyms & keywords:** end of term, EOT, asset age, age at end of term,
maximum asset age, "how old can the asset be", age limit, years at end of term, asset
maturity, oldest asset, useful life.

**Per-lender notes.**
- *Resimac* — motor vehicles 25yr, primary 25yr, secondary 10yr, tertiary 5yr; >16yr at
  EOT triggers +2% loading.
- *Angle* — primary 25yr, secondary 15yr, tertiary 10yr.
- *Metro* — passenger 12yr, trucks/equipment 15yr at EOT (no balloon on long-EOT lends).
- *flexicommercial* — primary 20yr (trailers 30yr), secondary 7yr.

**Related chunk topics:** asset_categories, loan_structure_and_terms,
trucks_trailers_wheeled_equipment_streamlined.

---

## 15. Loan term

**Explanation.** How long the loan runs, in months. Longer terms lower the monthly
repayment but usually need newer assets, and terms over 60 months often trigger a rate
loading. Green/EV assets sometimes get extended terms.

**Also called / synonyms & keywords:** term, loan term, duration, months, repayment
period, how long, 36/48/60/72/84 months, contract length, "over how many years", tenor,
finance period.

**Per-lender notes.**
- *Resimac* — standard 12–60 months; Green Goods (EV/sustainable) up to 84 months.
- *Angle* — standard 36–60; primary assets 36–72; primary MV 36–84; >60mo adds 1%.
- *flexicommercial* — max 7yr on primary ≤3yr old, otherwise 5yr; >60mo adds 1.25%.
- *Metro* — streamlined products commonly 24–60 months; Agri max 60 months.
- *BFS* — >60mo term needs vehicle ≤7yr at start; ≤60mo allows up to 15yr.

**Related chunk topics:** loan_limits, loan_structure_and_terms, loan_limits_terms.

---

## 16. Private sale vs dealer sale

**Explanation.** Whether the asset is bought from a private seller or a licensed dealer.
Private sales carry more risk (no dealer warranty, verification needed), so they usually
attract a rate loading, a higher fee, and an inspection requirement. Some fast-track
products are dealer-only.

**Also called / synonyms & keywords:** private sale, private seller, dealer sale, dealer,
licensed dealer, sale type, "buying privately", "from a dealer", non-dealer, party-to-party,
private purchase, inspection required, Verimoto, Redbook, DoxAI.

**Per-lender notes.**
- *Resimac* — private sale +2% risk loading; private-sale fee $695.
- *Metro* — private sale +0.25% loading.
- *Westpac Xpress* — private sales for cars/light-commercial only (not heavy equipment).
- *Angle* — no rate loading for private sales; inspection via Verimoto/Redbook/Olasio.
- *BFS* — private sale +0.50% loading; inspection (DoxAI/Redbook); capped at $150k PRIME.

**Related chunk topics:** interest_rates, settlement_requirements, private_sales.

---

## 17. Sale and hire back / sale and buyback

**Explanation.** Where a business sells an asset it already owns to the financier and
leases it back to free up cash. Higher risk, so it's often loaded or outright excluded
(especially under streamlined/low-doc products).

**Also called / synonyms & keywords:** sale and hire back, sale & hire back, S&HB, sale
and buyback, sale and leaseback, sell and lease back, refinance owned asset, cash-out on
owned equipment, equity release, "sell it to you and lease it back".

**Per-lender notes.**
- *Resimac* — sale and buyback only for PremiumPLUS/Premium, dealership sales, asset bought
  within last 30 days, case-by-case; private-sale/buyback fee $695.
- *Metro* — no sale/hire back under streamlined; 0.75% loading on non-streamlined.
- *BFS* — sale and buyback and sale and leaseback are **excluded purposes**.

**Related chunk topics:** exclusions_and_restrictions, exclusions, interest_rates.

---

## 18. Replacement / rollover / refinance / mid-term refinance

**Explanation.** Related but distinct ways to change existing finance. **Replacement** =
swap an old contract for a new one (often with a repayment-increase cap like 125%).
**Rollover** = Westpac-group term for replacing within the group. **Refinance** = pay out
and re-finance an asset, sometimes from another lender. **Mid-term refinance** = refinance
partway through a term to lower repayments.

**Also called / synonyms & keywords:** replacement, replace contract, rollover, roll over,
refinance, re-finance, mid-term refinance, balloon refinance, residual refinance, top-up,
bundle, "swap the loan", "pay out and re-do", "lower the repayments", net book value,
Old Finance Meets New.

**Per-lender notes.**
- *Westpac / CFAL* — Replacement (125% new-to-bank / 150% existing) and Rollover ($250k
  other financier / $500k Westpac; existing clients only).
- *Metro* — Replacement Policy (125% cap, replaced contract 36+ months); Balloon/Residual
  Refinance (final 12 months, prime movers included).
- *flexicommercial* — flexireplacement ($500K, 125%, 18-month established, primary only);
  Mid-term Refinancing (1% brokerage, 12+ months in); Old Finance Meets New (bundle).
- *Angle* — boarders & mid-term refinance require Mid Doc or Full Doc.

**Related chunk topics:** replacement, rollover, replacement_policy,
balloon_residual_refinance, flexireplacement_policy, refinancing_and_low_start.

---

## 19. PPSR (Personal Property Securities Register)

**Explanation.** The national register where a financier records its security interest in
a financed asset, protecting its claim if the borrower defaults or on-sells. Registration
is standard; searches check for existing claims (encumbrances) over an asset.

**Also called / synonyms & keywords:** PPSR, PPS register, security interest, registration,
encumbrance, encumbrance check, prior interest, lien, charge over asset, "register the
security", "clear title", PPSR search, PPSR fee.

**Per-lender notes.**
- *Resimac* — required on all financed assets; PPSR fees at cost.
- *Angle* — satisfactory PPSR by Angle; existing encumbrances on used cars removed pre-settlement.
- *Westpac* — from 24 Feb 2025, no PPSR company search over a private seller for VIN motor
  vehicles when day-of-sale search is clear.

**Related chunk topics:** settlement, settlement_requirements.

---

## 20. Certificate of Currency (CoC)

**Explanation.** Proof that the financed asset is insured, naming the financier's interest.
Usually required above a value threshold and before settlement funds are released.

**Also called / synonyms & keywords:** Certificate of Currency, CoC, proof of insurance,
insurance certificate, comprehensive insurance, "is it insured", insurance confirmation,
noted interest, insurance requirement.

**Per-lender notes.**
- *Resimac* — CoC required for NAF over $100k; insurance required on all deals.
- *Angle* — CoC for assets over $100k.
- *Westpac* — CoC asset-detail requirements tied to $150k threshold.

**Related chunk topics:** settlement, settlement_requirements.

---

## 21. Guarantor / director / shareholder requirements

**Explanation.** Who must personally stand behind the loan and meet residency/AML checks.
Typically all directors and major shareholders must be guarantors and be Australian
citizens or permanent residents.

**Also called / synonyms & keywords:** guarantor, director, shareholder, personal
guarantee, director's guarantee, PG, guarantee, "who signs", residency, citizen, permanent
resident, PR, AML, KYC, beneficial owner, 25% shareholder, 40% shareholder.

**Per-lender notes.**
- *Resimac* — all directors and >40% shareholders must be citizens/PRs residing in
  Australia and be guarantors; >25% shareholders complete AML; guarantee may be waived for
  large corporate/clubs/schools/charities.
- *flexicommercial* — director's guarantees required (waived for public/ASIC-lodging
  companies).
- *Angle* — prime movers Company & Trust only.

**Related chunk topics:** documentation, credit_matrix_and_limits.

---

## 22. Streamlined product (Metro-specific concept)

**Explanation.** Metro's term for its low-documentation, credit-reference-based product
suite, split by asset type (passenger vehicle, trucks/trailers, agri, other equipment,
replacement, balloon refinance, MetroEco). Each has its own limits, asset-age caps and
eligibility. There's a $500k-per-12-months streamlined cap overall.

**Also called / synonyms & keywords:** streamlined, streamline, Metro streamlined,
low-doc Metro, Metro product, streamline exposure, streamlined cap, streamlined product,
"which Metro product", carded product.

**Per-lender notes.**
- *Metro* — Passenger Vehicle (<3.5t), Trucks/Trailers/Wheeled (>3.5t, no prime movers),
  Agri (>5yr GST, 40ha farm), Other Equipment (no private sale, ≤3yr, $100k),
  Replacement (125%, 36mo), Balloon/Residual Refinance (final 12mo), MetroEco (green).

**Related chunk topics:** passenger_vehicle_streamlined, trucks_trailers_wheeled_equipment_streamlined,
agri_streamlined_product, other_equipment_streamlined_product, replacement_policy,
balloon_residual_refinance, metroeco_green_products.

---

## 23. Green / EV / sustainable asset programs

**Explanation.** Discounted or extended-term finance for electric vehicles, solar,
batteries and other low-emission assets. Often a rate discount plus longer terms and
specific eligibility (fully electric, new/demo, dealer).

**Also called / synonyms & keywords:** EV, electric vehicle, electric truck, green,
sustainable, MetroEco, Green Goods, solar, battery, charger, low emission, net zero, CEFC,
eco, clean energy, novated EV, FBT exemption, "electric car rate", green discount.

**Per-lender notes.**
- *Resimac* — EV lowest rate (7.54%/7.79%) + Green Goods terms up to 84 months.
- *Westpac / CFAL* — 1% rate reduction for EVs.
- *Metro* — MetroEco: EV discount, electric trucks -1% (property owners only, new,
  ≤$700k exposure), solar up to 7-year term, CEFC-backed.

**Related chunk topics:** interest_rates, metroeco_green_products, xpress rates.

---

## 24. Start-up / new business finance

**Explanation.** Products for businesses that don't meet the usual minimum ABN/GST age.
They trade a lower loan cap and extra conditions (deposit, industry experience, bank
statements) for access.

**Also called / synonyms & keywords:** start-up, startup, start up, new business, new ABN,
young business, ABN under 2 years, new venture, New Business Ventures, "just started
trading", fledgling business, first-time borrower.

**Per-lender notes.**
- *Angle* — Start-Up: ABN <2yr, trading 3+ months, ≤$150k incl brokerage, 550+ score,
  20% deposit, industry experience, 6-month bank statements.
- *BFS* — New Business Ventures: <12 months ABN, ≤$100k exposure, 90-day bank statements.

**Related chunk topics:** start_up_product, commercial_documentation.

---

## 25. Excluded assets & purposes

**Explanation.** Assets a lender will never finance, and loan purposes it won't fund (e.g.
debt consolidation, cash-out). Critical to check first — no tier, score or property backing
overrides an exclusion.

**Also called / synonyms & keywords:** excluded, exclusion, not eligible, can't finance,
won't fund, prohibited, ineligible, blacklist, "do you do", "will you finance",
debt consolidation, cash out, top-up, refinance cash, restricted assets.

**Per-lender notes.**
- *Resimac* — excludes fixtures/fittings, software, gym/hospitality equipment, food trucks,
  livestock, ride-share/taxi, IT hardware, shipping containers, artwork, gaming machines,
  and more; no consumer loans (commercial ABN only).
- *BFS* — excluded purposes: debt consolidation, cash raising, top-up, sale and buyback,
  sale and leaseback, mid-term refinancing.
- *flexicommercial* — no SUVs/passenger cars (incl. rental fleets), photocopiers, MFDs,
  scaffolding.
- *Metro* — Other Equipment excludes IT/AV/telephony, mining, intangibles; Agri excludes
  dairy, irrigation, sheds/silos, forestry.
- *Angle* — excludes taxi/Uber drivers, credit scores <500, financial defaults.

**Related chunk topics:** exclusions, exclusions_and_restrictions.

---

## 26. Loan-to-value ratio (LVR) & maximum lend

**Explanation.** How much the lender will advance relative to the asset's value. Above 100%
means financing extras (fees, insurance) on top of the asset price. Higher LVRs need
stronger applicants or a deposit.

**Also called / synonyms & keywords:** LVR, loan to value, loan-to-value ratio, advance
rate, max lend, lend ratio, 120% LVR, over-advance, "how much against the asset",
Glass's value, retail value, asset value.

**Per-lender notes.**
- *BFS* — no-deposit LVR up to 120% (Glass's Retail Value on used vehicles).
- *Resimac / Metro / Angle* — expressed via deposit rules and NAF caps rather than a
  headline LVR.

**Related chunk topics:** loan_limits_terms, property_ownership_and_deposits.

---

## 27. Comparable credit reference

**Explanation.** Evidence the applicant has successfully run a similar loan before — used
by low-doc/streamlined products in place of full financials. Usually a recent asset-finance
contract with clean conduct.

**Also called / synonyms & keywords:** credit reference, comparable credit, comparable
reference, prior loan, previous finance, repayment history, clean conduct, "have they
borrowed before", asset finance reference, mortgage statement reference, similar asset.

**Per-lender notes.**
- *Metro* — comparable credit reference on a current/previous asset finance within the last
  12 months (on similar assets).
- *Angle* — 12-month Asset Finance Credit Reference from an accepted lender for $400k Low
  Doc; loan running 6+ months, 50%+ of finance amount, no missed repayments.
- *Resimac* — asset-finance or mortgage statements (6+ months, no missed repayments).

**Related chunk topics:** low_doc_400k_program, documentation, passenger_vehicle_streamlined.

---

## How the model should use this file

1. Read the broker's question and identify the **concept(s)** involved by matching against
   the *synonyms & keywords* lists above (e.g. "how much can they put in" → Deposit;
   "sell it to you and lease it back" → Sale and hire back).
2. Use the **per-lender note** to pick the right lender's rule and the **related chunk
   topics** to retrieve the exact policy chunk from the vector store.
3. If the concept differs across lenders (bureau, deposit %, EOT age), retrieve **each**
   lender's chunk rather than assuming they match — this is where cross-lender
   contamination happens.
4. If a question spans several concepts (a complex broker query), map **all** of them and
   retrieve all the relevant chunks before answering.

*This FAQ is a navigation and disambiguation aid. The authoritative figures always live in
the lender `*_chunks.md` policy files and Metadata.csv — quote those, not this summary.*
