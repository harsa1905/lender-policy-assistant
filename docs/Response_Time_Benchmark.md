# Response Time Benchmark — Multi-Lender Questions

Measured 2026-08-07, `gpt-5.5` / `REASONING_EFFORT="low"` (the config used whenever one or
more lenders are named in the question — see `src/config.py`).

## 3-lender questions (real, live-measured)

Ran all 10 questions in the test bank that name exactly 3 lenders
(`ComplexQuestions.xlsx`, categories "Cross-lender comparison (3+)" and
"Cross-lender + multi-filter"), end-to-end against the live backend.

| Question | Lenders | Time |
|---|---|---|
| CQ-008 | BFS, Resimac, CFAL | 5.9s |
| CQ-055 | Resimac, BFS, Angle | 7.3s |
| CQ-007 | Resimac, Angle, Flexi | 7.8s |
| CQ-041 | Westpac, CFAL, Metro | 8.6s |
| CQ-079 | Westpac, Resimac, Flexi | 10.0s |
| CQ-006 | Westpac, CFAL, Metro | 10.3s |
| CQ-103 | Metro, Resimac, Angle | 11.5s |
| CQ-009 | Westpac, CFAL, Angle | 12.2s |
| CQ-010 | Angle, Metro, Flexi | 11.2s |
| CQ-042 | Resimac, Angle, BFS | 15.1s |

**Average: ~10.0s. Range: 5.9s – 15.1s.**

Simple yes/no scans across 3 lenders (CQ-008) land at the low end; questions that stack
extra filters on top of the comparison (deposit type, ABN age, dollar thresholds — CQ-042)
push toward the high end.

## Practical bounds

- **Floor: ~4–6s.** Any question naming a lender always uses the `"low"` reasoning tier
  (not the cheaper fan-out path, which only applies when *no* lender is named), so it
  won't go much below a plain yes/no comparison.
- **Ceiling under normal load: ~15–20s.** Scales with how many filters/conditions have to
  be checked per lender before the model can compare or rank them.
- **Rare worst case: well over a minute.** If OpenAI rate-limits the request,
  `_chat_completion` retries up to 8 times with backoff. Uncommon, but it's the actual
  theoretical ceiling, not the ~15–20s practical one.
- A "give me more detail" follow-up on any answer deliberately gets a doubled output-token
  budget and will run longer than the original — that's an intentional design choice
  (elaboration answers are allowed to be longer), not a slowdown.

## Machine comparison: is the new laptop faster?

**No — same-question, same-config testing shows it's running slower**, not faster.

| | Old laptop | This laptop |
|---|---|---|
| CQ-006 (exact same question, same `gpt-5.5`/`low` config) | 5.3s | 10.3s |

Nearly 2x slower on an identical question with identical model settings — so the
difference is the machine, not the pipeline.

**Likely cause:** this laptop is ARM64. Python 3.14 doesn't yet have ARM64 Windows wheels
for several core dependencies (`pandas`, `torch`, `scipy`, `onnxruntime`), so the working
environment here runs the **x64** Python build under Windows' built-in emulation instead
of native ARM64. The retrieval step's local embedding model (`bge-base`, via
`sentence-transformers`/`torch`) does CPU inference on this machine for every query — that
step is exposed to the emulation overhead. The actual OpenAI API call that generates the
answer isn't affected by local machine speed, but the local embedding/retrieval scoring
that happens before it is, and that's the most likely source of the gap.
