# LifeX Policy Assistant — Technical Documentation

**Current state of the system as at 2026-08-20.** This supersedes
`Week4_Technical_Documentation.md`, which stays in place as the historical record of
that week's work — this document describes how the system behaves *now*.

Written to be read before a Q&A, so it explains **why** each decision was made, not just
what the code does. Section 11 is a prepared answer bank for likely judge questions.

---

## 1. The system in one paragraph

A broker asks a question in plain English. The system works out which of the 7 lenders
the question concerns, pulls **every** policy chunk belonging to those lenders out of a
vector database, and hands that material to GPT-5.5 with instructions to answer only from
what it was given. Before generating anything it checks two stores of previous answers —
one of human-reviewed corrections, one of prior AI answers — and serves a stored answer if
one genuinely matches. Answers are grounded in 63 policy chunks extracted from 25 lender
PDFs, every one of them human-approved before going live; the model is never asked to
recall lending policy from its own training.

**The one-sentence version for a judge:** *"It's retrieval-augmented generation over a
human-approved policy corpus, with a two-layer answer cache and a human correction loop —
the model only ever reasons over policy text we put in front of it."*

---

## 2. Architecture at a glance

```
25 lender PDFs
      │  (AI-drafted, human-approved — see §3)
      ▼
data/chunks/*.md ──ingest──► ChromaDB "lifex_policies" (63 chunks, bge-base embeddings)
                                        │
Broker question ────────────────────────┤
      │                                 │
      ├─ 1. Correction check   (only if mid-conversation)
      ├─ 2. Answer library     (only if a fresh question)   ── human-reviewed
      ├─ 3. Query cache        (only if a fresh question)   ── unreviewed
      └─ 4. Retrieve + generate  ── GPT-5.5, grounded in retrieved chunks
                                        │
                                        └──► answer + source chunk list
```

| Layer | File | Role |
|---|---|---|
| Data | `data/chunks/*.md` | 7 files, one per lender, 63 chunks total |
| Ingest | `src/ingest.py` | Parses chunks, embeds, rebuilds the vector DB |
| Retrieval + generation | `src/query.py` | Lender detection, retrieval, prompting, all classifiers |
| API | `src/api.py` | FastAPI endpoints, both caches, concurrency locks |
| Config | `src/config.py` | Every tunable, each with the reasoning behind its value |
| Chunk drafting | `scripts/draft_chunks.py` | PDF → draft chunks (see §3.3) |
| Table extraction | `scripts/table_geometry.py` | Deterministic table structure from PDF vector data |
| Frontend | `CMAP_PolicyAssistant_v7_2.html` | Single self-contained file, no build step |

**Models in use:**

| Model | Used for | Why this one |
|---|---|---|
| `BAAI/bge-base-en-v1.5` | embeddings | Runs locally, no API cost; upgraded from bge-small for better recall |
| `gpt-5.5` | writing the answer | Benchmarked head-to-head; see §10.3 |
| `gpt-4o-mini` | 5 narrow classifiers | Supports `temperature=0`, so its decisions are stable run to run (see §14) |
| `gpt-5` (vision) | drafting chunks from PDFs | Offline authoring step only — never in the answer path (§3.3) |

---

## 3. Data layer — how policy chunks are made

Each lender has one markdown file. A chunk is an atomic policy unit with a stable
`chunk_id`, structured metadata (lender, intent, asset class, doc type, trigger words),
and the actual policy content as prose and tables.

`chunk_id` must never change once assigned — it is the key ChromaDB and every saved answer
references.

**Chunks carry their own provenance and known conflicts.** Where two lender documents
disagree, the chunk records both figures and instructs that the conflict be surfaced rather
than silently resolved — e.g. Metro's EV price cap is $91,661 on the rate sheet and
$91,387 in the MetroEco booklet. The correct answer flags both.

### 3.1 Two generations of extraction pipeline — read this before §3.3

This has a history, and the history is the reason the current design looks the way it does.

**Generation 1 (Week 4) — built, piloted, and rolled back.** A straight automated PDF
extraction pipeline. It **silently corrupted figures** during extraction. For a system whose
entire purpose is quoting exact financial figures, silent corruption is the worst possible
failure — a wrong number that looks exactly like a right one. It was rolled back and
extraction went manual.

**Generation 2 (current) — AI drafts, a human approves.** The lesson from Gen 1 was not
"automation can't do this." It was **"automation must not be the last step."** The current
pipeline keeps the speed benefit and removes the failure mode by making a human the gate
rather than the typist.

So: *chunks are no longer hand-typed, but no chunk has ever gone live unread.* Both halves
of that sentence matter, and a judge may well probe the seam between them.

### 3.2 What a chunk file looks like going in

Ingest is deliberately dumb: `src/ingest.py` parses the markdown, embeds each chunk, and
rebuilds the collection. There is no cleverness at ingest time — everything that determines
answer quality happens upstream, at authoring, where a person can see it.

### 3.3 The current pipeline — draft, review, promote

```
lender PDFs ──► 3 views per page ──► gpt-5 vision ──► draft chunks
                                                          │
                                              side-by-side diff in the UI
                                                          │
                                          human ticks what they approve
                                                          │
                                    validate ──► merge ──► re-ingest ──► live
```

**Endpoints:** `POST /chunks/draft` produces the draft; `POST /chunks/promote` applies the
approved subset.

**The model gets three views of every page**, because any one alone is insufficient:

| View | What it contributes | Why it alone isn't enough |
|---|---|---|
| Rendered page image (2.5× zoom) | Layout, and figures printed *inside* graphics | A vision model cannot reliably tell a 2-row merge from a 3-row merge from pixels |
| Vector table geometry | Exact row/column boundaries and merged cells, read from the PDF's own line data | Only works on tables with *stroked* borders — see limitation below |
| Exact digital text layer | Character-for-character verification of every digit | Carries no structure — a text layer doesn't say which column a number is in |

The table-geometry step exists because of a measured failure: across **six** different
model/config combinations, an LLM could not reliably read merged-cell structure off a real
BFS rate table from pixels. Reading it from the PDF's vector data turns *"guess whether
this is merged"* into *"here is what is actually merged, transcribe accordingly."*

**Known limitation, and it is a real one.** `table_geometry.py` detects tables whose borders
are **stroked** (thin filled rectangles acting as line segments). Some rate cards draw no
strokes at all — every cell is a filled block and the "border" is just where two fills meet.
Measured 2026-08-19: the **Angle rate card** (98 drawings, all filled) yields 0 horizontal
and 1 vertical line; the **Westpac rate chart** (26 drawings) likewise yields nothing. Both
return empty — and both are among the most rate-critical documents in the corpus. On those
pages the model falls back to image + text only, which is exactly where human review earns
its keep.

A fix for this was implemented and **reverted**: it produced phantom 31×40 grids and
destroyed column association on Westpac. Because the prompt tells the model to *trust* the
geometry report, a wrong report is worse than no report. Shipping nothing beat shipping
noise.

**Three safeguards in the pipeline:**

- **Truncation is refused, not returned.** If the drafting call comes back with
  `finish_reason == "length"`, `draft_chunks.py` raises rather than handing back a draft
  that silently stops mid-table.
- **Drafted chunks arrive unticked.** The review UI defaults every checkbox to *off*, so
  approving is a positive act. Nothing can reach the live file by someone clicking through
  a dialog.
- **Validation before replacement.** A malformed draft cannot leave the live chunk file
  broken.

**Audit result.** A full audit of all 63 live chunks against their source PDFs produced 11
flags, every one of which was explained on inspection, and **zero transcription errors**.
One flag nearly went the wrong way: `$91,661` is absent from Metro's text layer, and the
chunk was almost reported as fabricated — until the page was rendered and the figure was
found inside a green MetroEco graphic. The chunk was right and the audit was wrong. That
false-positive mode is now documented in `scripts/audit_chunks_vs_pdfs.py`.

---

## 4. Retrieval — we deliberately do *not* use top-k

This is the single most counter-intuitive design decision and a likely judge question.

**Standard RAG** embeds the question, retrieves the top *k* most similar chunks (typically
5), and passes those to the model. **We don't do that.** Once the lenders are identified,
we retrieve **every chunk belonging to those lenders** (`ALL_LENDER_CHUNKS_K = 20` per
lender, above any lender's actual chunk count).

**Why:** each lender has only ~8–10 chunks (~5–6k tokens). The entire pool fits in the
prompt at negligible cost. Under top-k, a correct chunk ranked one position past the cutoff
is simply *never seen* by the model, and no amount of prompt engineering can recover it —
the failure is invisible and unfixable. By retrieving everything for the relevant lenders,
**a retrieval miss becomes structurally impossible**; embedding similarity now only decides
the *order* chunks appear in, never whether they appear at all.

This also let us delete the cross-encoder reranker entirely — its load time, ~1GB of RAM,
and its own known failure mode of demoting correct chunks. It existed only to fix ranking
near the top-k cutoff, and there is no cutoff any more.

**Lender detection** (`detect_lenders`) matches in tiers: canonical name → product/brand
variant (`premiumplus`, `flexicommercial`, `metroeco`) → single-typo fuzzy match as a last
resort. Results are **unioned**, not gated on first match — an earlier version returned as
soon as one lender matched, which silently dropped a second lender mentioned only by
product name. That was the single largest source of failures in the 111-question eval.

**If no lender is named**, the question fans out across all 7 lenders (~63 chunks). This is
the expensive path and is handled specially — see §7. Note the failure direction: an
undetected lender means *more* chunks are read, never fewer. The worst case is slow, not
wrong-lender.

---

## 5. The four answer paths

Every request goes through `_query_impl` in `src/api.py`, which tries paths in a **fixed
order**. Understanding this order is essential.

```
1. CORRECTION      — only when mid-conversation. Is the broker correcting us?
2. ANSWER LIBRARY  — only for a fresh question. Human-reviewed answer on file?
3. QUERY CACHE     — only for a fresh question. Previous AI answer on file?
4. GENERATE        — retrieve chunks, ask GPT-5.5, then cache the result
```

Two rules explain most of the behaviour:

- **The correction check only runs when there IS conversation history.** A correction is
  a reply to something — it can't be the first message.
- **Both caches are skipped entirely when there IS history.** A follow-up like *"and for a
  used one?"* only means something inside its own conversation; matching it against a
  stranger's cached standalone question would return something that doesn't address it.
  For the same reason, a follow-up's answer is **never written to the cache** — it was
  written for a context the next asker won't have.

`answer_source` in the API response tells you which path produced the answer:
`generated`, `cache`, `library`, or `correction_saved`.

---

## 6. The two caches — how they differ and why there are two

This trips people up, so: **there are two server-side stores, and they are not the same
thing.** (The frontend also keeps its own small local list for its Review tab — that's a
third, separate thing and is not authoritative.)

| | **Query cache** | **Answer library** |
|---|---|---|
| File | `data/query_cache.json` | `data/answer_library.json` |
| Contains | Raw AI answers, unreviewed | Human-reviewed or human-corrected answers |
| Written by | Automatically, on every fresh answer | Broker correction in chat, or approval in the Review tab |
| Trust level | Same as any AI answer | Higher — a person signed off |
| Checked | **Second** | **First** |
| Purpose | Speed and cost | Correctness — a human fixed something |

**Why the library is checked first:** if a broker has explicitly corrected an answer, that
correction must beat an older unreviewed cached answer for the same question. If the order
were reversed, a correction could be silently shadowed by the very answer it was meant to
replace. This ordering is now covered by two regression scenarios (COMBO-1, COMBO-7).

### 6.1 How a cache match is decided — the two-stage gate

Both stores use the **same** two-stage matching, and the reason is a real measurement, not
a preference.

**Stage 1 — embedding similarity as a cheap pre-filter** (threshold 0.75). Narrows the
whole store to a handful of plausible candidates, best first.

**Stage 2 — a direct LLM comparison** (`questions_require_same_answer`) on up to 3
candidates. This is the actual yes/no decision.

**Why not just use a similarity threshold?** Because we measured it and it doesn't work for
this domain. Genuine paraphrases and dangerous near-misses **overlap in score**:

- *"BFS Tier 2's minimum credit score"* vs *"BFS **Tier 3's** minimum credit score"* →
  **0.93** similarity, but completely different correct answers
- Genuine paraphrases scored as low as **0.78**

No single threshold separates those. A value high enough to exclude the near-miss would
reject nearly every real paraphrase. So similarity is used only for the job it's reliable
at — excluding the obviously unrelated — and a model that can actually read both questions
makes the call.

The gate is deliberately **conservative**: a missed cache hit costs a few seconds and a
fraction of a cent; a wrongly-served cached answer hands a broker a confidently wrong
financial figure with nothing to flag it. It also returns "no match" on any internal error,
so a failure can never *open* the gate.

### 6.2 Deduplication — both stores, now

Both stores **purge any gate-equivalent entry before appending**, so there is exactly one
entry per distinct question — always the newest.

For the query cache, this was not theoretical: repeated evaluation runs accumulated several
entries for the same question with no recency signal, and ranking picked between them
essentially at random. Three entries existed for one question, one of them a stale wrong
answer from before a rate update, and it was being served roughly a third of the time.

The answer library had the same bug in mirror image — correcting the same question twice
left two entries and served the **first** correction, because `find_best_match` returns the
highest-*similarity* entry rather than the newest. **Fixed 2026-08-19** by applying the same
dedup-on-write pattern (`save_entry` in `src/answer_library.py`). Scenario COMBO-6, which
was previously left deliberately failing to document the bug, now passes.

One subtlety worth knowing: both stores assign new ids as `max(existing ids) + 1`, not
`len() + 1`. With dedup removing entries, those two diverge, and `len()+1` would eventually
reissue a live id.

### 6.3 Cache lifetime — what clears it and what doesn't

**The query cache survives backend restarts.** The server holds no cache state in memory at
all: `_find_cached` calls `_load_query_cache()` inside the lookup, so the JSON file is
re-read from disk on **every query**. The file *is* the cache. Restarting the process, or
rebooting the machine, does not touch it.

| Action | Effect on query cache |
|---|---|
| Restart backend / reboot | **Nothing** — persists |
| **Reset cache** button (Usage & cost view) | Clears all entries |
| `POST /query-cache/clear` | Same |
| `/chunks/promote` | Clears **only** entries citing changed chunks |
| `/answer-library/refresh` | Clears **all** (nothing records which chunks moved) |

Note the deliberate asymmetry: **the Reset control does not clear corrections.** There is no
button in the UI that can destroy the answer library — that requires editing
`data/answer_library.json` by hand. Corrections are human work nothing else can reconstruct.

Writes are atomic (temp file + `os.replace`), so a concurrent reader never sees a
half-written file — which matters when several people query at once.

**Scaling note:** because the file is re-read and re-parsed per query, lookup cost grows
with cache size. At ~130 entries / 3.4 MB this costs roughly 50–100 ms per query — invisible
against an 8 s generate. It would become worth revisiting somewhere north of 10 MB.

**Operational history:** the cache was cleared on 2026-08-18 because it held answers
generated *before* that day's reasoning fix — every pre-fix entry was stale by construction.
It is safe to clear at any time: it is purely regenerable, and the only cost is that the
next ask of each question pays full latency once. Consider pre-warming it from the question
bank before a demo.

---

## 7. Reasoning-effort routing — the speed/accuracy dial

GPT-5 family models take a `reasoning_effort` parameter. We use two settings:

| Situation | Effort | Rationale |
|---|---|---|
| A lender was named | `low` | Raised from `minimal` after a reproducible bug: on rate build-ups the model stated a headline figure before working out the right table row, then derived a *different* number in its own shown working and never reconciled the two |
| No lender named (fan-out) | `none` **or** `low`, decided per question | `low` over ~63 chunks is materially slower, so a classifier decides whether this particular question actually needs it |

**The classifier was broadened on 2026-08-18 after it caused a wrong answer.** It
originally split on *"does this rank a number across lenders?"* versus *"is it a simple
yes/no eligibility scan?"* — and sent eligibility scans down the cheap path.

The failure: *"Carpenter registered ABN and GST last week, wants a ute, which lender can he
choose?"* reads as an eligibility scan → ran at `none` → recommended **Angle** (whose
Start-Up product requires 3 months' trading, which the client fails) while dismissing
**BFS** (whose New Business Ventures pathway explicitly covers *"less than 12 months ABN"*,
which the client meets). The answer even quoted BFS's requirement and then concluded the
opposite.

Diagnosed by elimination: retrieval was fine (the BFS chunk *was* retrieved), and scoped to
a single lender the model got **both** lenders right. A controlled A/B with identical
retrieval and effort as the only variable settled it — `none` answered Angle, `low`
answered BFS correctly.

**The axis was wrong.** It was never ranking-versus-eligibility; it's *whether a specific
customer figure has to be tested against each lender's own threshold*. Deciding which side
of a threshold "last week" falls on is as demanding as picking a cheapest rate. Pure
category lookups (*"which lenders finance trucks"*) still take the cheap path, preserving
the latency win.

---

## 8. Conversation handling

### 8.1 Follow-ups

`_resolve_followup` rewrites a follow-up into a standalone question using the last 3 turns,
and separately flags whether the broker is asking for *more detail* (as opposed to asking
something new). Everything downstream — lender detection, retrieval — then treats it like a
fresh question.

The detail flag matters because "keep it brief" and "give me more detail" are direct
opposites; with both in the prompt, brevity wins and the answer comes back as a reworded
copy. So the brevity instruction is switched **off in code** for that one turn.

### 8.2 Corrections

`detect_and_apply_correction` decides whether the broker is correcting us and, if so,
produces the corrected answer for immediate saving. Per project decision, chat corrections
go live **immediately** — unlike Review-tab answers, which wait for approval.

Two safeguards worth knowing:

- **It must quote a specific replacement value from the broker's own message.** Pure
  skepticism — *"are you sure?"*, *"that doesn't sound right"* — saves nothing. This is
  load-bearing: an earlier version that just asked for a true/false verdict **invented**
  replacement figures for skeptical messages. Requiring a quote suppressed that.
- **When correcting a follow-up, the previous turn is re-resolved first.** Otherwise
  correcting the answer to *"what about CFAL?"* would save the literal string *"what about
  CFAL?"* as the question and attach the *previous* lender's chunk ids — the correction
  would be unfindable and point at the wrong sources.

Verified 2026-08-18: a correction propagates into **later reasoning in the same
conversation**, not just into a repeat of the same question.

**A correction does not edit the chunk.** It is stored as an answer-level override in the
answer library. The underlying policy file is unchanged — updating that is the
draft/review/promote path in §3.3. This is a common point of confusion: the two mechanisms
sit at different layers and have different trust models.

---

## 9. Other behaviours worth knowing

**Conversational messages skip retrieval.** *"Are you online?"*, *"hi"*, *"what can you
help with?"* previously fanned out across all 7 lenders, returning a meaningless 60+ source
list tagged with whichever lender happened to score highest. A narrow check now short-
circuits these with a direct reply and **zero sources**. It only runs when no lender was
detected, and deliberately fails toward "this is a real question" — a vague-but-genuine
question like *"best rate?"* still goes through the full pipeline.

**The source display collapses.** The frontend shows `N lenders · M sources` with a
per-lender expandable list, instead of every chunk id concatenated into one unreadable
string.

**Portrait layout is supported.** The frontend adapts via `@media (orientation: portrait)`,
for the competition's three vertical displays.

**Concurrency.** `/query` takes a read lock; `/chunks/promote` takes a write lock while
rebuilding the index, so a query can never read a half-rebuilt collection. Cache and
library writes are atomic (temp file + `os.replace`), so a concurrent reader never sees a
half-written file.

**Answer staleness — both stores, handled differently.** A chunk change has to reach every
answer already built on the old content, and the two stores get opposite treatment because
they're worth different amounts:

- **Answer library:** entries snapshot the chunk content they were based on, so
  `refresh_stale_entries` re-checks each affected one and either auto-updates it or flags it
  `needs_review`. Flagged entries are **never served automatically**. These are human
  corrections, so the effort to preserve them is justified.
- **Query cache:** entries citing a changed chunk are **deleted outright**
  (`_invalidate_query_cache_for_chunks`). Cache entries record their source chunk_ids, so
  this is precise rather than a blanket wipe. They're unreviewed LLM output, so there's
  nothing to salvage and regenerating costs one question's latency.

`/chunks/promote` does both and reports the counts. `/answer-library/refresh` (the manual
path, used after editing chunks by hand) refreshes the library the same way but **clears the
cache entirely** — nothing recorded which chunks moved, and cache entries don't snapshot
content, so there's no way to tell which are stale.

> **Operational note:** running `python src/ingest.py` while the backend is up deletes and
> recreates the Chroma collection out from under the running process, which then 500s until
> restarted. `/chunks/promote` avoids this by re-ingesting in-process and calling
> `reload_index()`. If you re-ingest by hand, restart the backend afterwards.

---

## 10. Evaluation

### 10.1 Test suites

| Suite | What it covers |
|---|---|
| `tests/run_quick_regression.py` | 14-question smoke test — every complexity type, every lender |
| `tests/run_complex_questions.py` | Full 125-question adversarial bank |
| `tests/run_full_eval.py` | 43 questions + follow-ups, corrections, cache, library |
| `tests/run_combination_eval.py` | 12 scenarios testing how those mechanisms **interact** |
| `tests/run_finals_practice.py` | 15 competition-style cases (see `Finals_Practice_Cases.md`) |

**Nothing is auto-scored on answer quality.** An earlier version scored by keyword overlap
against a gold answer, which gave false confidence — it marked a *wrong lender's* answer
correct because it shared enough words. Answers are graded by a human or an LLM judge with
the reference in front of it. The automated assertions only check mechanically verifiable
facts: which path served the answer, which lender's chunks were retrieved, whether a saved
answer was reproduced verbatim.

### 10.2 Current results

| Suite | Result |
|---|---|
| 125-question adversarial bank | **92/125 fully correct · 3.70 / 4 average** |
| Finals practice cases | **15/15** (one with a minor caveat) |
| Combination eval | **12/12** |
| Quick regression | **14/14** |

**The 125-question bank in detail.** Graded 1–4 against a reference, then every low score
re-checked by hand against the source policy documents:

| Score | As graded | After reference errors corrected |
|---|---|---|
| 4 — fully correct | 84 | **92** |
| 3 — minor issues | 29 | 28 |
| 2 — partly wrong | 9 | 5 |
| 1 — incorrect | 3 | **0** |
| **Average** | 3.55 | **3.70** |

The right-hand column reflects 8 questions where the *reference answer* was verified wrong
against the source policy and the system was right (§10.4).

**The most useful number is not the average.** Of the 125, **7% had errors, and none were
fabricated figures.** Every remaining failure is a judgement call — excess caution, or
answering when it should have asked a clarifying question.

**Strongest and weakest question types** (corrected basis):

| Complexity type | Avg | n |
|---|---|---|
| Negative / trap constraint | **4.00** | 11 |
| Calculation / arithmetic | **3.92** | 12 |
| Multi-filter (single lender) | 3.87 | 15 |
| Contradiction detection | 3.82 | 11 |
| … | | |
| Cross-lender comparison (2) | 3.47 | 15 |
| Cross-lender comparison (3+) | **3.43** | 7 |
| Ambiguous / needs clarification | **3.40** | 5 |

It is strongest exactly where being wrong costs most — traps and rate arithmetic — and
weakest on multi-lender synthesis and knowing when to ask a clarifying question.

**The 5 remaining sub-3 answers** are CQ-028 (best-fit), CQ-076 (ambiguous), CQ-083
(policy-interaction edge case), CQ-088 and CQ-089 (cross-lender). All scored 2; none scored
1. The clustering is consistent with the table above rather than scattered.

> **Caveat on the judge's `fell_for_trap` flag:** it marked 15 questions, but **6 of those
> were reference errors, not model errors**. The genuine count is 9. The flag inherits the
> judge's mistakes, so don't quote the raw 15.

### 10.3 Model selection

`gpt-5.5` was benchmarked against `gpt-5.6-terra` (cheaper, faster) on 11 questions drawn
from this project's own failure history. Terra was faster on **all 11** (avg 6.5s vs 8.7s,
−25%) — but on *"which lender is cheapest"* it quoted Flexi's **standard** rate instead of
the **flexipremium** rate and therefore named the wrong cheapest lender, on **2 of 4** runs.
gpt-5.5 got it right 4/4. It also added unverified qualifiers ("assuming brokerage is 5.5%
or less") that appear nowhere in the source.

**Decision: stay on gpt-5.5.** A coin-flip on the cheapest-rate question is disqualifying
regardless of speed, and rate accuracy is what the competition emphasises.

That 4-run comparison doubles as the system's **run-to-run repeatability measurement** on
the hardest question type — see §14.

### 10.4 Reference data goes stale — a real lesson

The 111-question reference bank was frozen around 2026-07-22, but the policy chunks were
corrected several times afterwards. Reference answers have now been found wrong **17 times
in total** while the system was right:

- **9 found 2026-08-18** — Flexi's rate dropped 7.30%→7.15%, Metro's rate sheet changed, and
  a CFAL rule turned out to belong to a different lender entirely
- **8 more found during the 125-question grading** — CQ-007, 013, 030, 032, 043, 093, 104,
  107

**Practical rule: when the system disagrees with a reference answer, check the chunk file
before assuming the system is wrong.**

---

## 11. Likely judge questions — prepared answers

**"How do you stop it hallucinating figures?"**
Three layers. The model only sees policy text we retrieved and is instructed to ground
every figure in it. Retrieval can't miss relevant chunks because we pass the lender's
entire chunk set, not a top-k slice. And every answer returns the exact chunk ids it drew
on, so any figure is traceable back to a source document. It's also explicitly instructed
that if the excerpts don't contain a figure, it should say so rather than produce one.
Across 125 adversarial questions, **not one error was an invented figure**.

**"Why not fine-tune a model on the policies?"**
Policies change. A rate card update would need retraining, and a fine-tuned model gives no
way to tell whether an answer came from current policy or a memorised old version. With
retrieval, updating a policy is editing a markdown file and re-running ingest — and the
answer cites which chunk it used.

**"Is the chunk extraction automated or manual?"**
Both, in sequence — and the order is the whole point. A vision model drafts chunks from the
PDF; a person reviews a side-by-side diff and ticks what they approve; only then does it go
live. We built a fully automated pipeline first, in Week 4, and rolled it back because it
silently corrupted figures. The lesson wasn't "don't automate" — it was "don't let
automation be the last step." **Automation drafts, people approve.**

**"What happens when a lender changes a rate? Don't the old answers stick around?"**
Both stores are handled, and differently on purpose. Saved *corrections* are re-checked
one by one: each snapshotted the chunk text it was based on, so a narrow LLM call decides
whether it still holds, and it's either updated or flagged `needs_review` (flagged entries
are never served). *Cached* answers that cited a changed chunk are simply **dropped** —
they're unreviewed, so there's nothing worth preserving and regenerating costs one
question. Promoting through the UI does both automatically and reports the counts. The
Metro and Flexi rate changes in §10.4 went through exactly this path.

**"When a broker corrects it, does that change the policy document?"**
No — and deliberately. A correction is an answer-level override stored in the answer
library; the policy chunk is untouched. Changing policy goes through draft/review/promote.
Different layers, different trust models: a correction is one broker's fix to one answer,
a chunk change is a change to the source of truth for everyone.

**"What if two source documents disagree?"**
It surfaces both and says to confirm, rather than silently picking one. Metro's EV cap
appears as $91,661 on the rate sheet and $91,387 in the booklet; Angle's Start-Up minimum
credit score is 550 on the flyer and 500 on the rate card. Both are handled this way, and
both are tested.

**"How accurate is it?"**
3.70 out of 4 across 125 adversarial questions, 92 fully correct; 15/15 on competition-style
practice cases; 14/14 on the regression suite; 12/12 on the interaction suite. But the more
useful answer is that we track *specific failure modes* rather than a single number — it is
strongest on traps (4.00) and rate arithmetic (3.92), weakest on multi-lender synthesis
(3.43) and knowing when to ask a clarifying question (3.40).

**"How do you know it isn't just memorising the test set?"**
The reference answers were verified against source chunks independently of what the system
outputs — and when they disagreed, the *references* turned out wrong **17 times**. We also
routinely find and fix errors the test bank didn't contain.

**"Will it give the same answer twice?"** — see §14.

**"Why does it sometimes take 15–20 seconds?"**
Only when no lender is named, so it reads all 7 lenders' policies (~63 chunks) and does
careful step-by-step reasoning. Naming a lender takes it to ~3–7s. It's a deliberate
trade: that slow path is where the hardest questions live, and rushing it produced wrong
answers (§7).

**"What's the cost per question?"**
Roughly $0.01–$0.05 for a generated answer; cached and library answers are effectively
free. Embeddings run locally at no API cost.

**"What's the weakest part?"**
Three honest ones. **Multi-lender synthesis** is the weakest measured category (3.43) — the
more lenders in play, the more room to drop a constraint. **Knowing when to ask a clarifying
question** is weakest of all (3.40); it errs toward answering. And **table geometry can't
read block-drawn tables** (§3.3), which affects two of the most rate-critical documents in
the corpus — human review is what covers that gap, so the pipeline is only as good as the
person at the diff. The correction-matching gate is also deliberately conservative, so it
sometimes misses a genuine paraphrase and answers fresh instead.

---

## 12. Operating it live — see also

For driving the assistant in front of an audience (what to expect by question
shape, how to trigger follow-ups and corrections, what to do when something
breaks, and a Q&A answer bank), see **`Demo_Operator_Guide.md`**. It covers the
operational details this document deliberately leaves out.

Two mechanics from it are worth repeating here, because they surprise people:

- **A correction only saves when the message states the replacement value.**
  "That's wrong, it's actually 7.15%" saves; "are you sure?" deliberately does
  not, because the system will not invent a figure from vague doubt (§8.2).
- **The Reset cache control does not clear corrections.** It empties the query
  cache only. Corrections are human work that nothing else can reconstruct, so
  they are protected from an accidental wipe (§6.3).

---

## 13. Running it

```bash
python src/ingest.py                          # rebuild the vector DB after any chunk edit
uvicorn src.api:app --port 8000               # start the backend
python tests/run_quick_regression.py          # 14-question smoke test
python tests/run_finals_practice.py           # competition-style cases
python scripts/build_finals_report.py         # regenerate the shareable results page
python scripts/build_technical_doc_html.py    # regenerate the HTML version of this doc
```

**Public tunnel** (only needed when presenting from another machine):

```powershell
ngrok http 8000
```

> **Run ngrok from PowerShell, not Git Bash.** The Store install lives at
> `%LOCALAPPDATA%\Microsoft\WindowsApps\ngrok.exe`, which is an App Execution Alias — a
> reparse point Windows shells resolve but Bash cannot execute. From Bash it fails with
> `Permission denied` (exit 126), which looks like a permissions problem and isn't.

Frontend: open `CMAP_PolicyAssistant_v7_2.html` — no build step. Point `API_BASE` at the
ngrok URL for a shared demo, or `127.0.0.1:8000` for local.

**Before a demo:** confirm `/health` returns 7 lenders and 63 chunks, and consider
pre-warming the query cache so the first questions aren't slow. The cache persists across
restarts (§6.3), so anything already warmed stays warmed.

---

## 14. Determinism — will it give the same answer twice?

A likely judge question, and the honest answer has two halves.

**Three of the four answer paths are byte-identical every time.** Corrections, answer-library
hits and query-cache hits all replay stored text — that's why a repeat returns in ~1–2s
instead of 8–25s. Only path 4 re-runs the model.

**Fresh generation is not deterministic, and cannot be made so.** GPT-5 family models
**ignore `temperature`** — there is no determinism dial to set. Ask a genuinely new question
twice and the wording will differ.

**But what varies is the phrasing, not the inputs.** Everything that decides *what the model
sees* is deterministic by design:

- **Retrieval has no ranking cutoff.** Every chunk for the detected lenders goes in, every
  time. There is no top-k boundary for run-to-run variation to move something across.
- **The classifiers are pinned.** Lender detection and the follow-up resolver run on
  `gpt-4o-mini` at `temperature=0` — chosen deliberately for exactly this reason. A
  differently-worded rewrite could change which lenders get retrieved at all, so that step
  is not allowed to drift. (`config.py` documents this at `RESOLVER_MODEL`.)

So the model receives an identical prompt each run and re-words the answer from it.

**The measurement:** in the §10.3 bake-off, the same question was run 4 times per model.
`gpt-5.5` answered correctly **4/4**; the cheaper model **2/4**. That 4/4 is the
repeatability figure, and it was taken on the hardest question type — cheapest-rate across
the whole panel, no lender named.

> **Demo honesty note.** If someone asks the same question twice to "test consistency," the
> second answer comes from cache — identical, in about a second, proving nothing about the
> model. Say so, and offer the real test instead: ask it a *different way* and check whether
> the figures match.
