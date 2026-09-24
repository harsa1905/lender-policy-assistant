# Lender Policy Assistant

A self-improving AI knowledge system that answers asset finance brokers' lender policy questions
in plain English, grounded in human-approved policy text, with the source sections cited on every
answer.

Built for LifeX Asset Finance's **Industry AI Challenge 2026**, a University of Sydney Business
School industry placement based on LifeX's CreditMAP platform. **Winning team.**

---

## What it does

A broker asks a question in plain English. The system works out which lenders the question is
about, pulls **every** policy section belonging to those lenders, and asks the model to answer
using only that text. The answer comes back with the list of sections it was drawn from, so any
figure can be traced to its source.

Before generating anything, it checks two stores of earlier answers: human-reviewed corrections
first, then previous machine answers. A genuine match is replayed in a second or two instead of
being regenerated.

The corpus is 63 structured policy sections drawn from 25 publicly published lender documents
across seven lenders, and every section was approved by a person before going live.

---

## Why it is built this way

The interesting parts are the places where the standard approach was wrong for this domain.

- **No top-k retrieval.** Standard RAG passes the few most similar chunks to the model. Here each
  lender has only eight to ten sections, so the whole set for the relevant lenders fits in the
  prompt. A retrieval miss becomes structurally impossible rather than silently invisible.
- **No reranker.** Once there was no cutoff, the cross-encoder reranker had nothing to do. Removing
  it freed about 1GB of memory and a failure mode where it demoted correct sections.
- **Two answer stores, checked in a fixed order.** Human-reviewed answers are checked before
  unreviewed cached ones, so a broker's correction can never be shadowed by the stale answer it
  replaced.
- **A two-stage match before reusing an answer.** Embedding similarity alone could not separate a
  dangerous near-miss (0.93) from a genuine paraphrase (as low as 0.78), so similarity only
  shortlists candidates and a model reads both questions before an answer is reused.
- **Automation drafts, a person approves.** The first extraction pipeline was fully automated and
  silently corrupted figures, so it was rolled back. The replacement drafts each section from three
  views of every page (rendered image, PDF vector table geometry, exact text layer) and nothing
  goes live until someone approves it. A full audit found zero transcription errors.

The full reasoning, including what was tried and reverted, is in
[`docs/Technical_Documentation.md`](docs/Technical_Documentation.md).

---

## Results

| Suite | Result |
|---|---|
| 125-question adversarial bank | **3.70 / 4**, 92 fully correct |
| Finals practice cases | 15 / 15 |
| Combination scenarios | 12 / 12 |
| Quick regression | 14 / 14 |

The 3.70 is the corrected figure. As originally graded it was 3.55, and it rose after eight
reference answers were checked against the source documents and found to be wrong, with the system
right. Seven per cent of answers contained an error, and none of those errors was an invented
figure.

The weakest areas are synthesis across three or more lenders, and knowing when to ask a clarifying
question instead of answering.

---

## Stack

| Layer | Choice |
|---|---|
| API | Python, FastAPI |
| Vector store | ChromaDB |
| Embeddings | `BAAI/bge-base-en-v1.5`, run locally at no API cost |
| Answers | GPT-5.5 |
| Routing classifiers | gpt-4o-mini at temperature 0, so routing is stable run to run |
| Section drafting | GPT-5 vision, offline only, never in the answer path |
| Frontend | A single self-contained HTML file, no build step |

---

## Repository layout

```
src/                 retrieval, answering, API and the answer library
scripts/             section drafting, table geometry, source audit, report builders
tests/               regression, adversarial, combination and finals evaluation suites
data/chunks/         the approved policy sections, one file per lender
docs/                technical documentation, operator guide, practice cases
CMAP_PolicyAssistant_v7_2.html    the frontend
```

---

## Run it locally

```bash
pip install -r requirements.txt
cp .env.example .env          # add your OPENAI_API_KEY
python src/ingest.py          # build the vector store
uvicorn src.api:app --port 8000
```

Then open `CMAP_PolicyAssistant_v7_2.html` in a browser. It points at `http://127.0.0.1:8000`.

Quick check that everything is wired up:

```bash
python tests/run_quick_regression.py
```

---

## Team

Built by a team of five University of Sydney students.

- **Sameep (Harsameep Khurana):** the backend, covering retrieval, answering, both answer stores,
  the drafting and review pipeline and the evaluation harness, plus part of the frontend
- **Jiani:** project lead, UX, compliance and quality
- **Maksim:** finance and lender policy
- **Samyak and Umair:** full-stack development

---

## Notes

The lender policy documents behind the corpus are published publicly by the lenders themselves.
The code is shared here with the team's agreement, as a portfolio copy of the finished project.

© 2026 the project team. All rights reserved.
