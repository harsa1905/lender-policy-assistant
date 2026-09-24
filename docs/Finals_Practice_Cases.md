# Finals Practice Cases

Extra practice cases in the same shape as the supplied mock (`finals-QA - mock.docx`),
built to probe **more failure modes** than the three sample cases reach.

The mock's three cases each target a different capability, so these are grouped the
same way:

| Group | Mock case it extends | What it stresses |
|---|---|---|
| **A. Rate** | Case 1 (*"mainly test rate related"*) | rate-table selection, tier/band boundaries, stacking loadings, caps |
| **B. Memory** | Case 2 (*"memory dealing power in long chatting"*) | multi-turn context, unstated subjects, lender switching, corrections |
| **C. Special position** | Case 3 (*"special position related policy"*) | threshold edges, hard exclusions, product availability, conflicting source data |

**Every reference answer below was verified directly against the current chunk files**
(chunk ids listed per case), not written from memory. Where the corpus itself
disagrees with itself, that's called out as the expected answer — flagging the
conflict *is* the correct response, not picking a side silently.

> **Note on the mock's own answer key.** For Case 3 it gives BFS "20% deposit" flat.
> The chunk (`bfs_commercial_documentation`) actually says the New Business Ventures
> minimum deposit is **20% for Tier 3 and Tier 4** — i.e. tier-dependent, not
> universal. Our system answering "20% if Tier 3/4" is *more* precise than the key,
> not wrong. Worth knowing in case a judge marks against the flat figure.

---

## GROUP A — Rate related

### CASE A1 — Same question as mock Case 1, but electric
*(Mock Case 1 says "petrol or diesel", which suppresses every EV rate. This is the
inverse: the EV rates and discounts now **must** be applied.)*

**Question**
> I want to finance an electric passenger vehicle. What is the lowest displayed
> interest rate from each lender?

**Reference answer**

| Lender | Lowest rate | Basis |
|---|---|---|
| Westpac | **6.75%** | Xpress dealer ≤5yr, 24/36/48mo 7.75% **less the 1% EV discount** |
| Resimac | **7.54%** | PremiumPLUS electric vehicles (7.79% other tiers) |
| Metro | **7.20%** | Passenger/commercial <12t, >$20k dealer 8.20% **less 1% MetroEco** |
| BFS | **7.60%** | Ultra Prime commercial — no EV-specific discount exists |
| Angle | no EV-specific rate | prices off its normal profile/EOT-age table |
| Flexi | **not fundable** | passenger cars and SUVs excluded outright, EV or not |
| CFAL | no public rate card | pricing via CFAL Credit Manager |

**What it traps**
- Applying the EV discounts that mock Case 1 correctly *withheld* — a model that
  learned "don't mention EV rates" from Case 1 fails here.
- Flexi's passenger-car exclusion is **absolute**; being electric doesn't create a
  pathway.
- BFS/Angle have no EV discount — inventing one to match competitors is the failure.

**Verified against:** `westpac_xpress_rates`, `resimac_interest_rates`, `metro_interest_rates`,
`metro_eco`, `bfs_commercial_rates`, `flexi_exclusions`, `cfal_drivexpress_policy`

---

### CASE A2 — Stacking loadings that land exactly on the cap
**Question**
> Resimac deal: a PremiumPLUS client buying a classic car, 5 years old, through a
> private sale. What's the all-in rate?

**Reference answer**
Base: classic cars sit under motor vehicles; at 5 years old that's the **>3 years**
row = **8.24%** (PremiumPLUS).
Risk loadings, **+2% each and they stack**: classic car **+2%**, private sale **+2%**
= **+4%**.
The risk-loading cap is **4% per deal**, so the total sits **exactly at the cap** —
not over it, and nothing needs trimming.
**All-in: 8.24% + 4% = 12.24% p.a.** (brokerage loading is separate and excluded
from the 4% cap).
Worth adding: **classic cars are excluded from balloon payments**, so the balloon
must be 0 — the same limit the mock's own Case 2 key calls out.

**What it traps**
- Applying only one loading — the policy explicitly says multiple may apply.
- Mis-handling the cap: 4% is *at* the limit, not over it, so no reduction applies.
- Taking the PremiumPLUS discount by subtracting 0.25% from the Premium column
  instead of reading the PremiumPLUS column directly (the chunk warns about this).
- Classic cars are also carved out of the 25-year motor-vehicle EOT age rule, so
  that cap can't be quoted for them either.

**Verified against:** `resimac_interest_rates` (loadings list, 4% cap, PremiumPLUS note)

---

### CASE A3 — Premium tier the client doesn't actually qualify for
**Question**
> A company with a 3-year-old ABN and GST registration, asset backed, wants
> $200,000 for a primary asset. What's flexicommercial's rate?

**Reference answer**
**7.85% p.a. ex brokerage** — the standard card's $150,001+ Primary rate.
They do **not** get flexipremium's 7.15%: flexipremium requires **4+ years** ABN and
GST for asset-backed customers (8+ years if non-asset-backed), and this client has
only 3 years.

**What it traps**
This is the inverse of the usual trap. The documented failure mode is quoting the
*standard* rate when the client qualifies for *premium* — so a model that over-corrects
will wrongly hand out 7.15% here. Tier eligibility has to be checked in both
directions. (Benchmarked 2026-08-18: gpt-5.6-terra failed the mirror-image version of
this on ~50% of runs, quoting 7.85% where 7.15% applied.)

**Verified against:** `flexi_flexipremium` (eligibility + rates), `flexi_standard_rates` (base table)

---

### CASE A4 — Add-ons on the standard card
**Question**
> flexicommercial, non-asset-backed customer, $80,000 primary asset, private sale,
> 72-month term. Build up the rate.

**Reference answer**
Base: $20,001–$150,000 Primary = **8.35%**
Add-ons, each triggering independently:
- Private sale: **+1.00%**
- Term over 60 months: **+1.25%**
- Non-asset backed: **+1.50%**

**All-in: 8.35% + 3.75% = 12.10% p.a. ex brokerage.**
(Note this client can't reach flexipremium at all — non-asset-backed needs 8+ years
ABN/GST.)

**What it traps**
- Three independent add-ons stacking; dropping any one gives a plausible-looking
  wrong number.
- Using the $150,001+ band (7.85%) for an $80k deal — wrong band.
- The non-asset-backed add-on was **increased to 1.50%** from 1.25% on the prior
  card; quoting 1.25% means reading a superseded rate sheet.

**Verified against:** `flexi_standard_rates` (bands + add-ons + change note)

---

## GROUP B — Memory / long chat

### CASE B1 — Three-turn chain, subject never repeated
*(Extends mock Case 2 by one more hop.)*

**Turn 1** — *Which lender supports classic cars?*
> Only **Resimac** clearly supports classic cars.

**Turn 2** — *What rate would a PremiumPLUS client get on a 5-year-old one?*
> Motor vehicle **>3 years** = **8.24%** PremiumPLUS, plus the **+2%** classic-car
> risk loading = **10.24%**.

**Turn 3** — *And if they buy it privately?*
> Adds a second **+2%** risk loading → **+4% total**, which is **exactly the 4% cap**.
> **12.24% p.a.**

**What it traps**
Neither turn 2 nor turn 3 names the lender, the asset, or the tier. Turn 3 says only
"privately" — the model has to carry *Resimac + classic car + PremiumPLUS + 5 years
old* forward across two hops, then know the new loading stacks onto the previous one
rather than replacing it.

**Verified against:** `resimac_asset_categories`, `resimac_interest_rates`

---

### CASE B2 — Lender switch, then a comparison that depends on both turns
**Turn 1** — *What's the maximum loan under BFS New Business Ventures?*
> **$100,000** total exposure.

**Turn 2** — *What about Angle's Start-Up product?*
> **$150,000** including brokerage.

**Turn 3** — *So for a $120,000 deal, which one works?*
> **Angle only.** $120k is over BFS's $100k New Business Ventures cap, but within
> Angle's $150k Start-Up cap — *provided* the business has been trading at least
> 3 months (Start-Up requires it) and can meet the 20% deposit.

**What it traps**
Turn 3 names neither lender and requires holding **two different figures from two
different turns** and comparing them against a new number introduced only in turn 3.
A model that resolves turn 3 against just the most recent turn will answer about
Angle alone and miss that BFS is excluded.

**Verified against:** `bfs_commercial_documentation`, `angle_start_up`

---

### CASE B3 — Correction mid-conversation, then a dependent follow-up
**Turn 1** — *What's Angle's establishment fee?*
> $649.

**Turn 2** — *That's out of date, it's actually $700 now.*
> Correction acknowledged and saved.

**Turn 3** — *So what's the total upfront cost with a 20% deposit on a $50,000 ute?*
> Should use the **corrected $700**, not the original $649 — deposit $10,000 plus
> the $700 establishment fee.

**What it traps**
Whether a correction actually propagates into *subsequent reasoning in the same
conversation*, rather than only being served back when the identical question is
asked again. (Note: the $700 here is a test value, not real policy.)

**Verified against:** `angle_fees_brokerage` (for the pre-correction $649 baseline)

---

## GROUP C — Special position / policy

### CASE C1 — Credit score exactly on the tier boundary
**Question**
> A BFS commercial applicant has an Experian CCR score of exactly 600. Another has
> 599. What changes between them?

**Reference answer**
- **600 → Tier 2.** Meets the Tier 2 minimum, no mandatory extra deposit.
- **599 → Tier 3.** Falls to the Tier 3 band (550+), which carries a **mandatory 20%
  deposit on every application** — consumer or commercial, new or used.

One point of score changes the deposit requirement entirely.

**What it traps**
Boundary handling: 600 is the Tier 2 *minimum*, so it qualifies rather than falling
short. The Tier 3 deposit is **not** conditional on contract type — the chunk states
this explicitly because it's easy to assume it only applies to used or commercial deals.

**Verified against:** `bfs_customer_tiers`

---

### CASE C2 — Threshold met exactly (no auto-decline)
**Question**
> A BFS consumer applicant has net monthly income of exactly $2,318. Is that an
> automatic decline?

**Reference answer**
**No.** The auto-decline triggers when net monthly income is **below** $2,318. At
exactly $2,318 the applicant meets the floor, so this trigger doesn't fire. Other
auto-decline triggers still apply independently (all guarantors CCR <400, <550 for
commercial used, current bankruptcy).

**What it traps**
The mirror of mock Case 3's logic. $2,200 is a decline; $2,318 is not. A model that
has learned "$2,318 → auto-decline" as an association rather than as a *threshold*
will decline this incorrectly.

**Verified against:** `bfs_customer_tiers`, `bfs_exclusions`

---

### CASE C3 — Allied health vs medical specialist limits
**Question**
> A physiotherapist with 5 years' experience wants $200,000 of new medical equipment
> under Westpac Medical. Does it fit?

**Reference answer**
**No.** A physiotherapist is an **Allied Health Practitioner**, and Allied Health has
a **single combined cap of <$150,000** covering motor vehicle, office equipment *and*
medical equipment — there is no separate higher medical-equipment limit for them.
$200,000 exceeds it. Their max cumulative approvals are **<$250,000**.

The **<$350,000** medical-equipment figure applies only to Medical Specialist / GP /
Dental / Vet — a different category with a **<$500,000** cumulative cap.

**What it traps**
The $350k figure sits in the same table and is very easy to grab. The distinction is
professional category, not asset type. The 5 years' experience is a deliberate
red herring — it satisfies the >3-year requirement, so it's *not* the blocker.

**Verified against:** `westpac_medical` (limits table + note)

---

### CASE C4 — Loan size vs total exposure
**Question**
> A Metro customer with 12 months of good repayment history wants a single $400,000
> truck. Their maximum exposure is $500,000 — so this fits, right?

**Reference answer**
**No — those are two different ceilings.** Under the Trucks/Trailers streamlined
product, a customer with 12 months' good history has a **maximum loan size of
$300,000** (dealer sale). $400,000 exceeds that, even though their **total exposure**
limit of $500,000 is higher. A deal must clear *both*: the per-transaction cap **and**
the aggregate exposure cap.
(Also note: prime movers are excluded from this streamlined product, and private-sale
transactions cap at $250,000.)

**What it traps**
A false premise stated confidently by the broker. Exposure and loan-size limits are
listed in adjacent columns of the same table and are routinely conflated — the
documented failure mode is answering "yes" off the larger number.

**Verified against:** `metro_trucks_trailers_streamlined`

---

### CASE C5 — Remote area: which lender actually has the rule
**Question**
> My client is in a Remote area and is non-asset-backed. What deposit will BFS want,
> and what about CFAL?

**Reference answer**
- **BFS:** under PRIME, non-asset-backed applicants in remote areas require a
  **20% deposit**. Two carve-outs sit alongside it and a complete answer names them:
  **"Very Remote"** areas are not available **at all, across every tier**, and
  **BFS Plus is excluded from remote-area lending entirely**, with no deposit-based
  workaround.
- **CFAL:** **no such rule exists.** A Remote/Very Remote geographic restriction used
  to appear in CFAL's material but was verified as belonging to **Resimac's and BFS's**
  product guides, not CFAL's, and was removed. There is no CFAL geography-based
  deposit or exclusion to apply — CFAL is assessed on its normal criteria (2+ years
  ABN, current GST registration).

**What it traps**
Cross-lender contamination of a rule that genuinely exists at one lender and
genuinely does not at another. The correct answer requires saying "this doesn't apply
to CFAL" rather than reaching for the nearest similar-sounding policy.

**Verified against:** `bfs_exclusions`, `cfal_exclusions` (removal note)

---

### CASE C6 — Hard exclusion vs soft condition
**Question**
> My client wants flexicommercial to fund a passenger car for their business. They
> can put down a 50% deposit and they've been trading 10 years. Does that get it over
> the line?

**Reference answer**
**No.** flexicommercial does not fund passenger cars or SUVs **at all** — it's a hard
asset exclusion, not a credit condition. A larger deposit, longer trading history, or
stronger profile cannot satisfy it, because none of those change what the asset is.
Commercial vehicles (utes, vans, 4WDs) *are* fundable as primary assets, so the
alternative is a different asset — or a different lender.

**What it traps**
The question is loaded with genuinely strong mitigants to invite a "yes, with
conditions". The distinction between an exclusion that rules a lender out entirely
and a condition the customer can meet is one the answering prompt calls out
explicitly.

**Verified against:** `flexi_exclusions`, `flexi_asset_categories`

---

### CASE C7 — A product tier that doesn't exist
**Question**
> What are CFAL's Low Doc requirements for a $150,000 transaction?

**Reference answer**
**CFAL has no Low Doc option at all.** The premise is false. CFAL's documentation
requirements scale with **transaction size** instead, and all financial statements
must be no more than **18 months old** (P&L and balance sheet), for all related
companies and trusts.

**What it traps**
Assuming documentation tiers are standardised across the panel because most lenders
have some Low/Lite/Full Doc structure. The right move is to reject the premise, not
to describe CFAL's smallest-transaction requirements as though they were "Low Doc".

**Verified against:** `cfal_documentation_matrix`

---

### CASE C8 — The corpus contradicts itself
**Question**
> What's the maximum vehicle price for Metro's MetroEco electric vehicle discount?

**Reference answer**
**Flag the conflict rather than pick one.** Metro's own documents disagree: the rate
sheet states **$91,661**, while the separate MetroEco product booklet states
**$91,387**. Both are current Metro material and the booklet is otherwise unchanged,
so this is a genuine cross-document conflict rather than one superseding the other.
The correct answer surfaces both figures and says to confirm the current cap with
Metro directly.

**What it traps**
Silently picking one figure — or averaging/reconciling them — looks confident and is
wrong. This mirrors the Angle Start-Up 500 vs 550 credit-score conflict, which the
system already handles well, so it tests whether that behaviour generalises.

**Verified against:** `metro_interest_rates` (conflict note), `metro_eco`

---

## Suggested use

1. Run Group A first — the mock says Case 1 is *"mainly test rate related"*, so rate
   accuracy is the highest-value thing to be sure of.
2. Group B must be run as **real multi-turn conversations**, not as separate
   questions. Turn 3 in B1/B2 is meaningless without turns 1–2 in history.
3. Group C cases are mostly single questions and can be spot-checked quickly.
4. For any disagreement, check the chunk file before assuming the system is wrong —
   the reference bank in `ComplexQuestions.xlsx` went stale three times this way
   (see the 2026-08-18 refresh commit).
