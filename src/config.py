import os
from pathlib import Path
from dotenv import load_dotenv

# Single source of truth for "where is the project" — every path below is
# derived from this, so the project can be cloned/copied anywhere (a
# teammate's machine, a different drive letter) and still resolve correctly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DATA_DIR = str(PROJECT_ROOT / "data" / "documents")
# Lives inside the project (not a sibling folder) because it's fully
# regenerable from data/chunks/*.md via `python src/ingest.py` — nothing
# here is hand-authored, so there's no migration cost to keeping it local.
CHROMA_DIR = str(PROJECT_ROOT / "chroma_db")

# bge-small (33M params) is what the "0.90-0.96 band" recall problem above
# was calibrated against — it's the reason a cross-encoder reranker had to
# exist at all: the reranker can only re-score chunks bge-small's first pass
# already found, so a chunk missed entirely at that stage is unrecoverable.
# bge-base (109M params) is the same BAAI family (drop-in via
# HuggingFaceEmbedding, no new network dependency, no API cost) and scores
# meaningfully higher on retrieval benchmarks. Chosen over bge-large
# (335M) given this machine's prior history of memory-pressure issues
# (see chat history) — base is a safer size increase, not the largest one.
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
# Answering model. Originally benchmarked head-to-head on 5 known-ground-truth
# questions (2026-07-22): gpt-4o-mini made 3 factual errors with the
# full-corpus context, gpt-5-mini was correct but verbose and slow
# (2-14s, up to 4k-char answers), gpt-5 was correct on everything,
# fastest of the GPT-5 family here (2.4-7.4s), and the only one that
# reliably followed the verdict-first/brevity instructions.
#
# Switched gpt-5 -> gpt-5.5 on 2026-07-31 after a second head-to-head, this
# time across 11 questions (one per complexity type in the 111-question
# stress bank): identical correctness on 10/11, and gpt-5.5 caught a real
# gap gpt-5 missed on the 11th (CQ-102, "cheapest lender for a $200k primary
# asset") — gpt-5 quoted Flexi's standard-tier rate (7.85%) and missed the
# cheaper flexipremium tier entirely (7.15%, this project's own corrected
# rate), while gpt-5.5 correctly identified flexipremium as the applicable
# tier. gpt-5.5 was also faster on every single question tested, often by
# 2x+. ~$0.01-0.05 per question at gpt-5 input pricing — irrelevant against
# the budget, and gpt-5.5 is the same non-mini/non-pro tier so priced
# similarly.
LLM_MODEL = "gpt-5.5"
# Small utility model for the follow-up resolver — rewrites "details" /
# "what about westpac?" into standalone questions. Kept on gpt-4o-mini
# deliberately: GPT-5 family models ignore temperature, so the same
# follow-up resolves to a different standalone question run to run — for
# the answerer that variance is tolerable, but the resolver feeds lender
# detection, where a differently-worded rewrite can change which lenders
# get retrieved at all. 4o-mini at temperature=0 is stable and was already
# proven at this job.
RESOLVER_MODEL = "gpt-4o-mini"
# For GPT-5 family models only: how much internal reasoning to spend.
# Raised from "minimal" to "low" on 2026-07-25 after finding a reproducible
# bug at "minimal": on multi-step rate calculations, the model would state a
# headline number before it had actually worked out the right table row,
# then correctly derive a DIFFERENT number in its own shown breakdown and
# never reconcile the two (e.g. answering "9.64% p.a." as the headline while
# the working two lines later computes "12.64% + 2.00% = 14.64%"). Verified
# 3/3 that "low" eliminates this; latency cost is real (~2-3x slower per
# query, 2-3s -> 6-8s) but was judged worth it over silently wrong headline
# numbers on calculation questions.
REASONING_EFFORT = "low"
# Scoped back down for the one case where "low" cost far more than 2-3x:
# when NO lender is named, retrieval fans out across all 7 lenders (up to
# ~140 chunks vs ~8-20 for a single named lender), and "low" effort over
# that much context measured 20-56s per question — 3-8x worse than the
# single-lender case, for a question type (broad eligibility scans: "which
# lenders can do X", "best-fit across the panel") that's mostly yes/no
# verdicts, not the numeric rate build-ups "low" was raised to fix. Falls
# back to the cheapest tier specifically for that no-lender-detected
# fan-out path.
#
# Was "minimal" under gpt-5 -- gpt-5.5 doesn't support that value at all
# (hard 400 error; its scale is none/low/medium/high/xhigh, no "minimal").
# Re-benchmarked "none" vs "low" head-to-head on 6 genuine fan-out questions
# before picking "none": both gave equivalent-quality answers with no
# regressions vs the old gpt-5/minimal baseline, but "none" was faster in
# 4/6 cases and never worse -- "none" is the correct like-for-like mapping
# of "minimal"'s original intent (cheapest/fastest tier for this
# mostly-yes/no question type), not an arbitrary substitute.
FANOUT_REASONING_EFFORT = "none"

CHUNKS_DIR = str(PROJECT_ROOT / "data" / "chunks")
METADATA_PATH = str(PROJECT_ROOT / "data" / "Metadata" / "Metadata.csv")
QUESTION_BANK_PATH = str(PROJECT_ROOT / "data" / "Metadata" / "QuestionBank.xlsx")
# The current scenario-based bank (41 questions, no exact chunk_id column —
# graded by reading the answer against reference_answer, not auto-scored).
SCENARIO_QUESTION_BANK_PATH = str(PROJECT_ROOT / "policy_question_bank.xlsx")
# 111-question stress-test set (2026-07-22): cross-lender comparisons,
# multi-filter, contradiction detection, negative/trap constraints, etc. —
# harder and more adversarial than the 41-question scenario bank above.
COMPLEX_QUESTION_BANK_PATH = str(PROJECT_ROOT / "ComplexQuestions.xlsx")
GROUND_TRUTH_PATH = str(PROJECT_ROOT / "data" / "Metadata" / "GroundTruth.xlsx")
ANSWER_LIBRARY_PATH = str(PROJECT_ROOT / "data" / "answer_library.json")
QUERY_CACHE_PATH = str(PROJECT_ROOT / "data" / "query_cache.json")
# Was disabled entirely (threshold 0.97, calibrated against bge-small and
# never redone after the bge-base swap). Directly calibrated on 2026-08-08
# against real bge-base scores for this domain's questions -- and found
# something worse than "needs a new number": genuine paraphrases and
# dangerous near-misses actually OVERLAP in score. "BFS Tier 2's minimum
# credit score" vs "BFS Tier 3's minimum credit score" scored 0.93 cosine
# similarity -- higher than several genuine paraphrase pairs (as low as
# 0.78) -- despite having different correct answers. No single threshold
# separates them; a value high enough to exclude the near-misses would also
# reject nearly every real paraphrase.
#
# So embedding similarity is no longer the gate on its own -- it's a cheap
# PRE-FILTER only (its low end cleanly separates unrelated questions,
# ~0.35-0.40 measured, so it's reliable for that narrower job). The actual
# yes/no decision is src.query.questions_require_same_answer(), a direct
# LLM comparison of the two questions that can see "Tier 2" isn't "Tier 3"
# in a way a cosine score can't. This constant is that pre-filter floor,
# not a similarity-is-good-enough threshold -- keep it low and let the LLM
# gate do the real work.
QUERY_CACHE_PREFILTER_THRESHOLD = 0.75
# How many pre-filtered candidates (highest similarity first) get checked
# against the LLM gate before giving up and answering fresh. Bounds the
# worst-case extra latency/cost of a cache-miss to a few small classifier
# calls, not an unbounded scan.
QUERY_CACHE_MAX_CANDIDATES = 3
QUERY_CACHE_ENABLED = True

# Every answer_library.json entry has already been through a human
# review/approval step in the frontend's Review tab (or was stated directly
# by a broker as a correction) before it's ever saved -- a fundamentally
# different trust level than caching every unreviewed LLM output, so it was
# safe to serve these back at query time even before this got the same
# two-stage treatment as the query cache above.
#
# Checked directly against the query cache's calibration data (2026-08-08)
# before deciding whether to bother: at the OLD plain threshold (0.97),
# none of the measured near-miss pairs actually reached it (highest was
# 0.9685), so this wasn't silently unsafe the way the query cache was.
# But none of the genuine paraphrase pairs reached 0.97 either (highest was
# 0.9564) -- meaning the threshold was so conservative it likely almost
# never fired for anything short of near-identical wording, undermining the
# actual point of reusing a human-reviewed answer. Same two-stage fix
# applied for that reason: better recall on real paraphrases, not because
# the old version was actively serving wrong answers.
ANSWER_LIBRARY_PREFILTER_THRESHOLD = 0.75
ANSWER_LIBRARY_MAX_CANDIDATES = 3
ANSWER_LIBRARY_ENABLED = True

# Each chunk in data/chunks/*.md is already a hand-curated atomic unit with
# its own chunk_id, lender/intent/trigger-word metadata — SentenceSplitter's
# job here is only to be a safety net, never to actually re-split one.
# 1024 was too tight for that: it silently fragmented longer chunks (e.g.
# angle_doc_types at ~3800 chars) into multiple pieces that share a
# chunk_id but each hold only part of the content, so retrieval could
# return one half without the other. Sized well above the longest current
# chunk (~3800 chars) with real headroom for future edits.
CHUNK_SIZE = 4096
CHUNK_OVERLAP = 100
TOP_K = 5
