"""
Scenario data for tests/run_full_eval.py -- kept separate from the runner so
the scenario definitions (what to ask, what's expected) are easy to scan and
extend without wading through request/response plumbing.

Five categories:

1. STANDALONE_IDS -- question IDs pulled from ComplexQuestions.xlsx (the same
   111-question bank run_complex_questions.py uses). ~40 questions, chosen to
   cover every complexity_type, every one of the 7 lenders multiple times,
   and every category (PRICING, ELIGIBILITY, EXCLUSIONS, etc.) -- broader
   than run_quick_regression.py's 14-question smoke set, but well short of
   the full 111 (that's still the right tool for a milestone/competition
   checkpoint, not this). No auto-scoring on these, same reasoning as
   test_queries.py's docstring -- grade model_answer against reference_answer
   yourself, or hand the transcript to an LLM judge.

2. FOLLOWUP_SCENARIOS -- multi-turn conversations testing _resolve_followup()
   (src/query.py): does a follow-up like "what about Resimac?" correctly
   pull in the new lender's chunks rather than staying stuck on turn 1's
   lender? This IS auto-checked, but structurally (did retrieval touch a
   chunk_id with the expected lender prefix), never by judging whether the
   answer's *content* is good -- that distinction matters, see this
   project's test_queries.py docstring for why content-scoring was rejected.

3. CORRECTION_SCENARIOS -- exercises detect_and_apply_correction() end to
   end: broker corrects the assistant's last answer, the correction is
   saved to the answer library and immediately servable, a paraphrase of the
   original question hits that saved correction verbatim, and a near-miss
   (same structure, different tier/asset/channel) does NOT get served the
   correction meant for something else.

4. CACHE_SCENARIOS -- same paraphrase-hit / near-miss-reject shape, but for
   the query cache (src/api.py's _find_cached, unreviewed fresh answers).
   Near-miss pairs here are deliberately picked from facts already verified
   elsewhere in this project to have genuinely different correct answers
   (not just superficially different wording) -- see each scenario's
   comment for the source. A near-miss test is only meaningful if the two
   correct answers actually differ; picking two questions that happen to
   share the same true answer would make a false "FAIL" look like a caching
   bug when it isn't.

5. LIBRARY_SCENARIOS -- same shape again, for the answer library
   (answer_library.find_best_match), seeded directly via
   POST /answer-library/save instead of going through a chat correction.
   Since the seed answer text is fully author-controlled here (not
   LLM-generated), near-miss pairs don't need real-world grounding the way
   CACHE_SCENARIOS' do -- any two distinguishable topics work.

IMPORTANT: running the mutating scenarios (3-5) writes real entries into
data/answer_library.json and data/query_cache.json. run_full_eval.py backs
up and restores both files around the whole run specifically so this suite
can be re-run any time without leaving test-only entries in production data
-- see that file's docstring before changing the backup/restore logic.
"""

# ---------------------------------------------------------------------------
# 1. Standalone accuracy -- ~40 of the 111-question bank, broader than the
# 14-question quick-regression set. Every complexity_type appears at least
# 3 times, every lender appears at least twice, calculation/rate questions
# are deliberately over-represented per this suite's "different rates" brief.
# ---------------------------------------------------------------------------
STANDALONE_IDS = [
    # Cross-lender comparison (2)
    "CQ-003",  # Angle, Flexi -- known rate-table ambiguity regression
    "CQ-001",  # Westpac, CFAL
    "CQ-005",  # BFS, Westpac
    "CQ-096",  # Angle, Resimac -- known adjacent-attribute regression
    "CQ-106",  # Flexi, Resimac

    # Cross-lender comparison (3+)
    "CQ-088",  # Westpac, CFAL, Angle, Metro -- known bus-coverage regression
    "CQ-006",  # Westpac, CFAL, Metro
    "CQ-008",  # BFS, Resimac, CFAL

    # Multi-filter (single lender)
    "CQ-011",  # Resimac -- known headline-vs-breakdown calc regression
    "CQ-099",  # Westpac -- known exact-cap edge case regression
    "CQ-012",  # BFS
    "CQ-060",  # Flexi

    # Conditional scenario chain
    "CQ-092",  # BFS
    "CQ-016",  # Resimac
    "CQ-018",  # Metro
    "CQ-017",  # BFS (FEES)

    # Negative / trap constraint
    "CQ-023",  # Flexi
    "CQ-021",  # Metro
    "CQ-064",  # BFS

    # Best-fit recommendation (fan-out, no lender named)
    "CQ-102",  # known fan-out latency watch
    "CQ-026",
    "CQ-093",
    "CQ-073",  # FEES

    # Calculation / arithmetic
    "CQ-108",  # Resimac -- known headline-vs-breakdown calc regression
    "CQ-029",  # Metro
    "CQ-032",  # BFS
    "CQ-033",  # Angle
    "CQ-062",  # Flexi (FEES)

    # Ambiguous / needs clarification
    "CQ-076",  # fan-out
    "CQ-034",  # Angle
    "CQ-094",  # Metro

    # Contradiction detection
    "CQ-069",  # CFAL
    "CQ-037",  # Resimac
    "CQ-067",  # Metro

    # Cross-lender + multi-filter
    "CQ-089",  # Resimac, Westpac -- known fan-out latency watch
    "CQ-098",  # fan-out (EXCLUSIONS)
    "CQ-041",  # Westpac, CFAL, Metro
    "CQ-079",  # Westpac, Resimac, Flexi

    # Policy-interaction edge case
    "CQ-095",  # CFAL
    "CQ-048",  # Westpac (SETTLEMENT)
    "CQ-083",  # BFS (DOCUMENTATION)
    "CQ-111",  # Resimac (SETTLEMENT)
    "CQ-080",  # Angle (LOAN_LIMITS)
]


# ---------------------------------------------------------------------------
# 2. Follow-up resolution -- each is (turn1, turn2), checking that turn2's
# retrieval picked up the expected lender's chunks after _resolve_followup()
# rewrites it into a standalone question.
# ---------------------------------------------------------------------------
FOLLOWUP_SCENARIOS = [
    {
        "id": "FUP-1",
        "turn1_question": "What's Angle's rate for a primary asset with property backing and 8+ year ABN?",
        "turn2_question": "what about for Resimac?",
        "expected_prefix": "resimac_",
    },
    {
        "id": "FUP-2",
        "turn1_question": "Does BFS fund passenger vehicles under 4.5 tonnes GVM?",
        "turn2_question": "and Flexi?",
        "expected_prefix": "flexi_",
    },
    {
        "id": "FUP-3",
        "turn1_question": "What deposit does Angle require for a Start-Up applicant?",
        "turn2_question": "is that different at CFAL?",
        "expected_prefix": "cfal_",
    },
    {
        "id": "FUP-4",
        "turn1_question": "What is Resimac's private sale loading?",
        "turn2_question": "can you give more detail on that?",
        # Elaboration, not a lender switch -- should stay on Resimac, not
        # wander to an unrelated lender.
        "expected_prefix": "resimac_",
    },
    {
        "id": "FUP-5",
        "turn1_question": "Which panel lenders can finance a $200k primary asset for a property-backed established company?",
        "turn2_question": "just tell me about Metro specifically",
        "expected_prefix": "metro_",
    },
]


# ---------------------------------------------------------------------------
# 3. Correction flow -- turn2's correction_message deliberately states a
# specific, fabricated replacement value (the point is testing the save/
# retrieve/scope mechanism, not asserting real-world policy facts). The
# runner reads the *actual* saved answer back from answer_library.json
# after turn2 rather than guessing the LLM's exact rewritten phrasing, then
# checks the paraphrase gets that exact text back and the near-miss doesn't.
# ---------------------------------------------------------------------------
CORRECTION_SCENARIOS = [
    {
        "id": "CORR-1",
        "seed_question": "What is Angle's minimum ABN age for the Start-Up program?",
        "correction_message": "No, that's wrong -- Angle's Start-Up program actually has no minimum ABN age at all (0 days is fine). Please save that correction.",
        "paraphrase_question": "What's the minimum ABN age required for Angle's Start-Up program?",
        "near_miss_question": "What is Angle's minimum ABN age for its standard (non-Start-Up) primary asset profile?",
    },
    {
        "id": "CORR-2",
        "seed_question": "What is Westpac's EV discount on Xpress dealer rates?",
        "correction_message": "Actually that's outdated -- the Westpac Xpress EV discount was increased to 1.5% off, not 1%. Please correct and save that.",
        "paraphrase_question": "How much of a discount does Westpac give for EVs under Xpress?",
        "near_miss_question": "What is Westpac's EV discount under the Replacement channel (not Xpress)?",
    },
    {
        "id": "CORR-3",
        "seed_question": "What is Flexi's loading for a term over 60 months on a Primary asset?",
        "correction_message": "That's incorrect -- the correct loading for flexicommercial Primary assets over 60 months is 1.00%, not what you said. Please save that correction.",
        "paraphrase_question": "What loading does flexicommercial apply to a Primary asset financed over 60 months?",
        "near_miss_question": "What is Flexi's loading for a term over 60 months on a Secondary asset?",
    },
]


# ---------------------------------------------------------------------------
# 4. Query cache -- near-miss pairs grounded in facts already verified
# elsewhere in this project (see each comment), so a "FAIL" here means the
# cache actually reused a wrong answer, not that the two questions
# coincidentally share a real answer.
# ---------------------------------------------------------------------------
CACHE_SCENARIOS = [
    {
        "id": "CACHE-1",
        # Grounded in CQ-095's reference answer: Remote -> 20% deposit,
        # Very Remote -> not available at all. Qualitatively different
        # answers (a number vs. "not available"), not just a different number.
        "seed_question": "What is CFAL's deposit requirement for a Remote area, non-asset-backed client?",
        "paraphrase_question": "For a non-asset-backed CFAL client in a Remote area, what deposit is required?",
        "near_miss_question": "What is CFAL's deposit requirement for a Very Remote area, non-asset-backed client?",
    },
    {
        "id": "CACHE-2",
        # Grounded in CQ-108's reference answer: Resimac secondary asset
        # base rate is tier-dependent -- Standard 12.64%, PremiumPLUS 12.39%.
        "seed_question": "What is Resimac's Standard tier secondary asset base rate?",
        "paraphrase_question": "What's the base rate for a secondary asset under Resimac's Standard tier?",
        "near_miss_question": "What is Resimac's PremiumPLUS tier secondary asset base rate?",
    },
    {
        "id": "CACHE-3",
        # The project's own calibration example (see QUERY_CACHE_PREFILTER_THRESHOLD's
        # comment in src/config.py): BFS Tier 2 vs Tier 3 minimum credit score
        # scores ~0.93 cosine similarity despite having different correct answers.
        "seed_question": "What is BFS's Tier 2 minimum credit score requirement?",
        "paraphrase_question": "What's the minimum credit score BFS requires for Tier 2?",
        "near_miss_question": "What is BFS's Tier 3 minimum credit score requirement?",
    },
]


# ---------------------------------------------------------------------------
# 5. Answer library -- seeded directly via /answer-library/save, so
# seed_answer is exactly what should come back on a paraphrase hit.
# ---------------------------------------------------------------------------
LIBRARY_SCENARIOS = [
    {
        "id": "LIB-1",
        "seed_question": "What is Metro's minimum deposit for a MetroEco EV loan?",
        "seed_answer": "Metro requires a 10% minimum deposit for MetroEco-eligible EV loans, per this test entry.",
        "seed_chunk_ids": [],
        "paraphrase_question": "For a MetroEco EV loan, what's the minimum deposit Metro needs?",
        "near_miss_question": "What is Metro's minimum deposit for a non-EV commercial vehicle loan?",
    },
    {
        "id": "LIB-2",
        "seed_question": "What is Flexi's maximum term for a Primary asset under 3 years old?",
        "seed_answer": "flexicommercial allows up to 7 years (84 months) for a Primary asset under 3 years old, per this test entry.",
        "seed_chunk_ids": [],
        "paraphrase_question": "What's the max term flexicommercial offers on a Primary asset that's under 3 years old?",
        "near_miss_question": "What is Flexi's maximum term for a Secondary asset under 3 years old?",
    },
    {
        "id": "LIB-3",
        # Near-miss grounded in CQ-088's reference: charter buses are
        # explicitly excluded from the Replacement channel bus category.
        "seed_question": "What is CFAL's maximum loan term under the Replacement channel for a government bus?",
        "seed_answer": "CFAL allows up to a 10-year loan term under the Replacement channel for an eligible government/school/local route bus, per this test entry.",
        "seed_chunk_ids": [],
        "paraphrase_question": "Under CFAL's Replacement channel, what's the max loan term for a government bus?",
        "near_miss_question": "What is CFAL's maximum loan term under the Replacement channel for a charter bus?",
    },
]
