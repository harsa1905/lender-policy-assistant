# Demo Operator Guide

For whoever is driving the assistant live. Judges supply the questions, so this
is not a script to memorise — it is how to **operate** the system fluently and
answer for it afterwards.

Companion to `Technical_Documentation.md` (the deep reference). This one is
for the room.

---

## 1. Before you start

```bash
uvicorn src.api:app --port 8000                                  # backend
ngrok http 8000   # only if presenting off this laptop
```

Check `/health` returns **7 lenders, 63 chunks**. Open
`CMAP_PolicyAssistant_v7_2.html`.

**Pre-warm if you get any advance sight of the questions.** A repeat question
returns in ~1s instead of 15–25s. If you get no advance sight, skip it — see §3
for how to cover the wait.

---

## 2. What to expect, by question shape

| The judge's question | Time | Why |
|---|---|---|
| Names one lender ("What is BFS's…") | **3–7s** | Only that lender's chunks are read |
| Names two or three lenders | **6–12s** | Several lenders' chunks |
| Names **no** lender ("which lender is cheapest…") | **15–25s** | Reads all 7 lenders — ~63 chunks — and reasons carefully |
| Already asked this session | **~1s** | Served from cache |
| "hi", "are you online?" | instant | Skips retrieval entirely, returns no sources |

**Read the question before you hit enter.** If it names no lender, you know
you have ~20 seconds to fill — start talking (§3).

---

## 3. Filling the wait on a slow question

Say what it is doing, because it is genuinely the interesting part:

> "No lender was named there, so it's reading all seven lenders' policies —
> about sixty documents' worth — and working through them one at a time rather
> than guessing from the first match."

Then, when it lands, **point at the source chip**: "N lenders · M sources".
Expand it. That is your grounding story in one gesture.

---

## 4. Follow-ups — the strongest thing to demonstrate

The system carries context, so you never need to repeat the subject. These all
work:

| What you type | What it does |
|---|---|
| `what about Westpac?` | Switches lender, keeps the topic |
| `and Metro?` | Same, chains up to three turns |
| `give me more detail` | Re-mines the **same** sources for specifics it left out |
| `just tell me about Angle` | Narrows a panel answer to one lender |
| `what key limit should I check?` | Carries the whole prior context with no subject named |

**The demo moment:** ask something about one lender, then type only
`what about Resimac?`. Say out loud that you never repeated the asset or the
question — that is what the judges should notice.

**Use `give me more detail` if an answer feels too short.** The system is
deliberately concise; that command is the intended way to go deeper, and it
re-reads the same policy rather than inventing more.

---

## 5. Corrections — read this carefully

This is the most impressive feature and the easiest to get wrong live.

### It only saves if you state the replacement value

| You type | Result |
|---|---|
| `No, that's wrong — Angle's establishment fee is actually $700.` | ✅ **Saves** |
| `Actually the max term is 72 months, not 60.` | ✅ **Saves** |
| `Are you sure about that?` | ❌ Nothing saved |
| `That doesn't sound right, can you check?` | ❌ Nothing saved |

The second pair is **deliberate**, not a bug. The system will not invent a
replacement figure from vague doubt — it needs you to supply the value. If a
judge tries "are you sure?" and nothing saves, that is the safety behaviour
working, and worth saying so.

### What success looks like

> *"Got it — I've corrected that and saved it, so future questions like this
> will get the updated answer."*

### The full 30-second demo

1. Ask: `What is Angle's establishment fee?` → answers **$649**
2. Correct: `That's out of date — it's actually $700 now.`
3. Start a **new chat**, then ask a **paraphrase**: `How much does Angle charge to set up a loan?`
4. It returns **$700** — the corrected figure, not the original

Step 3 matters: use a *paraphrase*, not the identical question, so you are
showing it understood the question rather than string-matched it.

### Cleaning up afterwards

A correction persists. The **Reset cache** button (Usage & cost) deliberately
does **not** remove it — corrections are protected from accidental wipes. To
clear a test correction, empty `data/answer_library.json` and restart.

---

## 6. If something goes wrong

| Symptom | Do this |
|---|---|
| Answer takes >30s | Wait — it is retry backoff, not a crash. Keep talking. It will land. |
| "Could not reach the backend" | Check the uvicorn window is still running; check `/health`. |
| Tunnel dead (works locally, not for others) | Restart ngrok. Frontend needs no change. |
| An answer looks wrong | Say you'll check the source. **Do not** promise a fix live — our reference answers turned out wrong more often than the system did. |
| Backend 500s after someone re-ingests | Restart the backend. Re-ingesting outside the app invalidates its index handle. |

---

## 7. Q&A — likely questions and short answers

**"How do you stop it making up numbers?"**
It only sees policy text we retrieved, and it returns the exact chunk IDs it
used, so every figure is traceable. We tested 125 adversarial questions: 7%
had errors, and **none** were invented figures — they were judgement calls.

**"How do you know it isn't just memorising your test set?"**
Our reference answers were written independently from the source documents.
When the system disagreed with them, **the references were wrong 17 times**.
We keep finding errors the test bank never contained.

**"Why not fine-tune a model on the policies?"**
Policy changes. A rate update would mean retraining, and you could never tell
whether an answer came from current policy or a memorised old version. Here,
updating a policy is editing a file — and the answer cites which one.

**"What happens when a lender changes a rate?"**
Upload the new PDF, review the drafted changes, promote. Saved corrections
that depended on that policy are re-checked automatically; cached answers
built on it are dropped. Nothing stale survives silently.

**"What if two of the lender's own documents disagree?"**
It surfaces both and says to confirm. Metro's EV cap is $91,661 on the rate
sheet and $91,387 in the booklet — we flag both rather than pick one.

**"How accurate is it?"**
3.70 out of 4 across 125 adversarial questions; 92 fully correct. More useful:
it is strongest on traps and rate arithmetic — exactly where being wrong costs
most — and weakest on multi-lender synthesis and knowing when to ask a
clarifying question.

**"Why is it sometimes slow?"**
Only when no lender is named: it reads all seven lenders' policies rather than
guessing. We tested the fast version and it got a threshold question wrong, so
we chose correctness on that path.

**"What does it cost?"**
Roughly 1–5 cents per new question. Repeats are free. Embeddings run locally.

**"What's the weakest part?"**
Chunk curation is manual — deliberately, after an automated pipeline silently
corrupted figures. And it is concise by default, so you sometimes have to ask
for more detail.

**"Could a broker rely on this without checking?"**
It cites its sources on every answer, and flags anything it can't confirm
rather than guessing. It is built to make checking fast, not to remove it.

---

## 8. Three things to say if you get the chance

1. **"We don't use top-K retrieval."** Standard RAG takes the 5 best-matching
   chunks; a correct chunk ranked 6th is invisible and unrecoverable. Each
   lender only has 8–10 chunks, so we pass all of them — a retrieval miss is
   structurally impossible.

2. **"We measured instead of assuming."** We tried a cheaper, faster model. It
   was 25% quicker but named the wrong cheapest lender on half its runs, so we
   kept the slower one.

3. **"Automation drafts, people approve."** Nothing reaches the live policy
   file until a human reads a side-by-side diff and ticks it.
