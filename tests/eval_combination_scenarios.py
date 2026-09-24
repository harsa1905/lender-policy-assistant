"""
Combination scenarios -- multi-step conversations that exercise the
INTERACTIONS between the pipeline's mechanisms, rather than each mechanism
on its own.

tests/eval_scenarios.py already covers each mechanism in isolation (a
follow-up, a correction, a cache hit, a library hit). What it can't reach is
the behaviour that only emerges when they meet: does a human correction
actually override an older cached answer for the same question? Does a
correction made after a lender-switching follow-up attach to the RIGHT
lender? Do follow-ups really bypass the caches the way the code claims?
Those are the paths where a regression would be both most damaging and least
visible, because every individual part still passes its own test.

Derived from reading src/api.py::_query_impl and src/query.py directly, not
from guessing. The ordering facts these scenarios pin down:

  1. detect_and_apply_correction runs FIRST, and only when history is non-empty.
  2. answer_library.find_best_match runs BEFORE _find_cached -- so a saved
     human correction outranks an unreviewed cached answer for the same question.
  3. BOTH library and cache lookups are skipped entirely when history is
     non-empty ("if not request.history") -- follow-ups always answer fresh.
  4. The cache is only WRITTEN for standalone questions (same guard), so a
     follow-up's answer never enters it.
  5. detect_and_apply_correction re-resolves the previous turn through
     _resolve_followup when len(history) > 1, so a correction to a follow-up
     is saved against the resolved standalone question, not the literal
     "what about CFAL?" text.
  6. query_policies short-circuits to _handle_meta_question only when NO
     lender is detected, and returns zero sources when it does.

Every expectation below is mechanical -- an answer_source string, a chunk_id
prefix, a verbatim string match against an earlier step, a count of library
entries. Nothing here grades answer QUALITY; that stays a human/LLM-judge
job, for the reasons in tests/test_queries.py's docstring.

CORRECTION VALUES ARE DELIBERATELY FABRICATED. Each correction states an
invented figure with a distinctive marker so later steps can assert on it
verbatim. These scenarios test the save/retrieve/scope MACHINERY, not
whether the figure is real policy -- and the runner restores both data files
afterwards, so nothing invented here survives the run.
"""

# Each scenario is a list of steps executed in order against one backend.
# The runner snapshots data/query_cache.json and data/answer_library.json
# before EACH scenario and restores them after, so scenarios are hermetic and
# order-independent -- a failure in one can't cascade into the next.
#
# Step actions:
#   ask           -- standalone question (history cleared first, then this
#                    turn is recorded as the new conversation)
#   follow_up     -- sent WITH the accumulated conversation history
#   correct       -- identical HTTP call to follow_up; named separately so the
#                    scenario reads as what it's testing
#   seed_library  -- POST /answer-library/save directly (no chat involved)
#   reset         -- clear the conversation, so the next ask is standalone
#   clear_cache   -- empty the query cache. Scenarios that reason about cache
#                    state need their precondition stated, not inherited from
#                    whatever an earlier suite happened to leave cached.
#
# Optional "as": <name> stores that step's answer for later comparison.
#
# Expectations (all optional, all mechanical):
#   answer_source        -- exact string: generated | cache | library | correction_saved
#   from_cache           -- bool
#   sources_empty        -- bool
#   source_prefix        -- at least one chunk_id starts with this
#   no_source_prefix     -- NO chunk_id starts with this (cross-lender leak check)
#   answer_equals        -- verbatim match against a named earlier step
#   answer_not_equals    -- differs from a named earlier step
#   answer_contains      -- literal substring (only used for the fabricated
#                           correction markers, which are author-controlled)
#   answer_not_contains  -- literal substring must be absent
#   library_delta        -- how many entries the library grew by on this step
#   library_last_question_not     -- newest library entry's question != this literal
#   library_last_question_matches -- newest library entry's question contains this (case-insensitive)
#   library_last_chunk_prefix     -- newest library entry's chunk_ids start with this
#   cache_cluster_max    -- at most N cache entries whose question equals this step's

COMBINATION_SCENARIOS = [
    {
        "id": "COMBO-1",
        "title": "A saved correction overrides an older cached answer for the same question",
        "why": (
            "find_best_match runs before _find_cached in _query_impl. If that order ever "
            "flips, a broker's explicit correction would be silently shadowed by the "
            "unreviewed cached answer it was meant to replace -- the single worst outcome "
            "this pipeline can produce, and completely invisible from either mechanism's "
            "own isolated test."
        ),
        "steps": [
            {"do": "clear_cache"},
            {"do": "ask", "question": "What is Angle's establishment fee?",
             "as": "original", "expect": {"answer_source": "generated"}},
            {"do": "reset"},
            # Prove it really is cached now, so the final step is a genuine
            # library-vs-cache contest rather than a cache miss.
            {"do": "ask", "question": "What is Angle's establishment fee?",
             "expect": {"answer_source": "cache", "answer_equals": "original"}},
            {"do": "correct",
             "question": "That's out of date -- Angle's establishment fee is actually $711 flat (COMBOMARKERONE). Please save that correction.",
             "expect": {"answer_source": "correction_saved", "library_delta": 1}},
            {"do": "reset"},
            # Assert on the corrected VALUE, not the marker. The correction
            # prompt rewrites the previous answer changing only what the
            # broker's stated value covers, and is told not to introduce
            # anything not traceable to it -- so a parenthetical marker gets
            # dropped in the rewrite even though the figure is applied. The
            # figure is the thing that matters anyway.
            {"do": "ask", "question": "How much does Angle charge as an establishment fee?",
             "expect": {"answer_source": "library",
                        "answer_contains": "711",
                        "answer_not_contains": "649"}},
        ],
    },
    {
        "id": "COMBO-2",
        "title": "A correction made after a lender-switching follow-up attaches to the switched lender",
        "why": (
            "detect_and_apply_correction re-runs _resolve_followup over history[:-1] to "
            "reconstruct what the previous turn actually asked. Without that, correcting "
            "the answer to 'what about CFAL?' would save the literal string 'what about "
            "CFAL?' as the question and attach Angle's chunk_ids -- so the correction "
            "would never be found again, and would point at the wrong lender's sources. "
            "This path had a confirmed bug before and is only reachable by combining a "
            "follow-up with a correction."
        ),
        "steps": [
            {"do": "ask", "question": "What is Angle's minimum ABN age for the Start-Up program?",
             "expect": {"answer_source": "generated", "source_prefix": "angle_"}},
            {"do": "follow_up", "question": "what about CFAL?",
             "expect": {"answer_source": "generated", "source_prefix": "cfal_",
                        "no_source_prefix": "angle_"}},
            {"do": "correct",
             "question": "No, that's wrong -- CFAL actually requires a 4 year ABN minimum (COMBOMARKERTWO), not what you said. Please save that.",
             "expect": {
                 "answer_source": "correction_saved",
                 "library_delta": 1,
                 # The saved question must be the RESOLVED standalone form,
                 # never the raw follow-up text.
                 "library_last_question_not": "what about CFAL?",
                 "library_last_question_matches": "cfal",
                 "library_last_chunk_prefix": "cfal_",
             }},
            {"do": "reset"},
            # The saved question is turn 2 resolved into standalone form, so
            # it carries the Start-Up context turn 1 established. A bare
            # "what ABN age does CFAL require?" is genuinely a different
            # question (general policy vs one program) and the gate is right
            # to reject it -- verified directly: that pairing returns False
            # 3/3, while a true paraphrase returns True 3/3. So this asks a
            # real paraphrase of what was actually saved.
            {"do": "ask", "question": "What minimum ABN age does CFAL require for its Start-Up program?",
             "expect": {"answer_source": "library", "answer_contains": "4 year"}},
        ],
    },
    {
        "id": "COMBO-3",
        "title": "Follow-ups bypass the cache even when their resolved question is cached",
        "why": (
            "_query_impl gates both lookups behind 'if not request.history'. A follow-up "
            "that happens to resolve to an already-cached question must still answer fresh "
            "in context -- serving the standalone cached answer would drop the conversation's "
            "framing. Only testable by seeding the cache and then approaching the same "
            "question through a conversation."
        ),
        "steps": [
            {"do": "clear_cache"},
            {"do": "ask", "question": "What is Resimac's private sale loading?",
             "as": "standalone", "expect": {"answer_source": "generated"}},
            {"do": "reset"},
            {"do": "ask", "question": "What is Resimac's private sale loading?",
             "expect": {"answer_source": "cache"}},
            {"do": "reset"},
            # Now reach the same subject through a conversation instead.
            {"do": "ask", "question": "What is Metro's private sale loading?",
             "expect": {"answer_source": "generated"}},
            {"do": "follow_up", "question": "and what about Resimac's?",
             "expect": {"answer_source": "generated", "from_cache": False,
                        "source_prefix": "resimac_"}},
        ],
    },
    {
        "id": "COMBO-4",
        "title": "Pure skepticism is not treated as a correction",
        "why": (
            "detect_and_apply_correction requires the broker's message to state a concrete "
            "replacement value (broker_stated_value) before saving anything. A false "
            "positive here writes a FABRICATED figure into the answer library and serves it "
            "to brokers as a reviewed correction -- a documented past failure of this exact "
            "classifier. Doubt with no stated value must fall through to the normal pipeline."
        ),
        "steps": [
            # No answer_source expectation here on purpose: whether this
            # opening question is answered fresh or from a pre-existing cache
            # entry is incidental to what the scenario tests, and asserting
            # it just makes the case fail depending on what happened to be
            # cached before the run.
            {"do": "ask", "question": "What is BFS's Tier 2 minimum credit score requirement?"},
            {"do": "follow_up", "question": "are you sure about that?",
             "expect": {"library_delta": 0}},
            {"do": "follow_up", "question": "hmm, that doesn't sound right to me -- can you double check it?",
             "expect": {"library_delta": 0}},
            {"do": "follow_up", "question": "where did you get that from?",
             "expect": {"library_delta": 0}},
        ],
    },
    {
        "id": "COMBO-5",
        "title": "A correction for one lender does not leak to the same question about another",
        "why": (
            "Corrections are matched by the same two-stage gate as the cache, and "
            "'X's max exposure' vs 'Y's max exposure' is exactly the same-structure/"
            "different-detail shape that raw embedding similarity cannot separate. A leak "
            "here hands a broker one lender's corrected figure under another lender's name."
        ),
        "steps": [
            {"do": "ask", "question": "What is Metro's maximum customer exposure for a customer with 12 months of good repayment history?",
             "expect": {"answer_source": "generated"}},
            {"do": "correct",
             "question": "That's wrong -- Metro's maximum exposure at 12 months history is actually $560,000 (COMBOMARKERFIVE). Save that please.",
             "expect": {"answer_source": "correction_saved", "library_delta": 1}},
            {"do": "reset"},
            # Same question shape, different lender -- must NOT get Metro's correction.
            {"do": "ask", "question": "What is Flexi's maximum customer exposure for a customer with 12 months of good repayment history?",
             "expect": {"answer_not_contains": "COMBOMARKERFIVE"}},
            {"do": "reset"},
            # Same lender, genuinely different metric -- also must not get it.
            {"do": "ask", "question": "What is Metro's maximum single loan size for a passenger vehicle?",
             "expect": {"answer_not_contains": "COMBOMARKERFIVE"}},
        ],
    },
    {
        "id": "COMBO-6",
        "title": "Correcting the same question twice serves the SECOND correction",
        "why": (
            "Regression guard for a bug this scenario originally caught and which is now "
            "fixed. save_entry() used to append unconditionally, and find_best_match() "
            "returns the highest-SIMILARITY gate-passing entry rather than the newest -- so "
            "two corrections to one question left two live entries and the FIRST one kept "
            "being served (measured: step 7 returned the 5% correction after 6% had been "
            "saved over it). save_entry() now purges gate-equivalent entries before "
            "appending, so one question keeps exactly one entry. A broker who corrects the "
            "same figure twice has every reason to expect the later value to stick."
        ),
        "steps": [
            {"do": "ask", "question": "What is Westpac's maximum brokerage on Xpress deals?",
             "expect": {"answer_source": "generated"}},
            {"do": "correct",
             "question": "That's wrong -- Westpac's Xpress brokerage cap is actually 5% (COMBOMARKERSIXA). Please save that.",
             "expect": {"answer_source": "correction_saved", "library_delta": 1}},
            {"do": "reset"},
            {"do": "ask", "question": "What is Westpac's maximum brokerage on Xpress deals?",
             "expect": {"answer_source": "library", "answer_contains": "COMBOMARKERSIXA"}},
            {"do": "correct",
             "question": "Correction again -- the Xpress brokerage cap is actually 6% (COMBOMARKERSIXB), not 5%. Save that.",
             # Net ZERO, not +1: this correction supersedes the previous one,
             # so save_entry purges that entry and appends this one. A delta
             # of +1 here would mean both corrections are live again -- which
             # is exactly the bug, so this assertion is load-bearing.
             "expect": {"answer_source": "correction_saved", "library_delta": 0}},
            {"do": "reset"},
            # The newer correction must win.
            {"do": "ask", "question": "What is Westpac's maximum brokerage on Xpress deals?",
             "expect": {"answer_source": "library",
                        "answer_contains": "COMBOMARKERSIXB",
                        "answer_not_contains": "COMBOMARKERSIXA"}},
        ],
    },
    {
        "id": "COMBO-7",
        "title": "A seeded library entry outranks a cached answer for the same question",
        "why": (
            "COMBO-1 reaches this ordering through a chat correction; this reaches it "
            "through the Review-tab path (/answer-library/save) instead, so the precedence "
            "is pinned down for BOTH ways an entry can enter the library. The seeded answer "
            "is author-controlled, so the assertion is an exact string match rather than a "
            "marker substring."
        ),
        "steps": [
            {"do": "clear_cache"},
            {"do": "ask", "question": "What is CFAL's minimum ABN age requirement?",
             "as": "cached_version", "expect": {"answer_source": "generated"}},
            {"do": "reset"},
            {"do": "ask", "question": "What is CFAL's minimum ABN age requirement?",
             "expect": {"answer_source": "cache"}},
            {"do": "seed_library",
             "question": "What is CFAL's minimum ABN age requirement?",
             "answer": "CFAL requires a minimum ABN age of 2 years and current GST registration (COMBOMARKERSEVEN, reviewed entry).",
             "chunk_ids": []},
            {"do": "reset"},
            {"do": "ask", "question": "What is CFAL's minimum ABN age requirement?",
             "expect": {"answer_source": "library",
                        "answer_contains": "COMBOMARKERSEVEN",
                        "answer_not_equals": "cached_version"}},
        ],
    },
    {
        "id": "COMBO-8",
        "title": "A three-lender follow-up chain keeps landing on the newest lender",
        "why": (
            "_resolve_followup only sees history[-3:]. Across a chain of switches the risk "
            "is drift -- turn 3 quietly answering about turn 1's lender because the rewrite "
            "carried the wrong subject forward. Asserting both the expected lender's chunks "
            "and the ABSENCE of the earlier lenders' catches drift in either direction."
        ),
        "steps": [
            {"do": "ask", "question": "What is Angle's maximum asset age at end of term for a primary asset?",
             "expect": {"source_prefix": "angle_"}},
            {"do": "follow_up", "question": "what about Resimac?",
             "expect": {"source_prefix": "resimac_", "no_source_prefix": "angle_"}},
            {"do": "follow_up", "question": "and Metro?",
             "expect": {"source_prefix": "metro_", "no_source_prefix": "resimac_"}},
        ],
    },
    {
        "id": "COMBO-9",
        "title": "An elaboration follow-up stays on the same lender and says something new",
        "why": (
            "'give me more detail' takes a different prompt branch from a lender switch: it "
            "must re-mine the SAME excerpts rather than re-retrieve elsewhere, and must not "
            "come back as a reworded copy of the previous answer (a confirmed past failure "
            "when the brevity instruction and the detail request fought each other). Both "
            "halves are mechanically checkable."
        ),
        "steps": [
            {"do": "ask", "question": "What is Resimac's private sale loading?",
             "as": "brief", "expect": {"source_prefix": "resimac_"}},
            {"do": "follow_up", "question": "give me more detail on that",
             "expect": {"source_prefix": "resimac_", "answer_not_equals": "brief"}},
        ],
    },
    {
        "id": "COMBO-10",
        "title": "Conversational messages skip retrieval; underspecified real questions do not",
        "why": (
            "_handle_meta_question only fires when no lender is detected, which is also the "
            "full-panel fan-out branch. The risk runs both ways: a greeting that fans out to "
            "all 7 lenders returns a meaningless 60-source list under an arbitrary lender tag "
            "(the reported bug), while a genuine but vague question wrongly classed as small "
            "talk gets a useless non-answer instead of a clarifying question."
        ),
        "steps": [
            {"do": "ask", "question": "are you online?",
             "expect": {"sources_empty": True}},
            {"do": "reset"},
            {"do": "ask", "question": "hey there",
             "expect": {"sources_empty": True}},
            {"do": "reset"},
            {"do": "ask", "question": "what can you help me with?",
             "expect": {"sources_empty": True}},
            {"do": "reset"},
            # Vague, but genuinely a policy question -- must reach the pipeline.
            {"do": "ask", "question": "best rate?",
             "expect": {"sources_empty": False}},
            {"do": "reset"},
            {"do": "ask", "question": "what deposit is needed?",
             "expect": {"sources_empty": False}},
        ],
    },
    {
        "id": "COMBO-11",
        "title": "Repeated paraphrases of one question do not accumulate cache entries",
        "why": (
            "_append_to_query_cache now purges gate-equivalent entries before appending. "
            "Before that fix, running an eval twice left several entries for the same "
            "question with no recency signal, and _find_cached's similarity ranking picked "
            "between them effectively at random -- which is how a stale wrong answer got "
            "served alongside two correct ones. This asserts the cluster stays at one entry."
        ),
        "steps": [
            {"do": "clear_cache"},
            {"do": "ask", "question": "What is BFS's Tier 3 minimum credit score?",
             "expect": {"answer_source": "generated"}},
            {"do": "reset"},
            {"do": "ask", "question": "What's the minimum credit score BFS needs for Tier 3?"},
            {"do": "reset"},
            {"do": "ask", "question": "For BFS Tier 3, what minimum credit score is required?",
             "expect": {"cache_cluster_max": 1}},
        ],
    },
    {
        "id": "COMBO-12",
        "title": "A follow-up's answer never enters the query cache",
        "why": (
            "The cache write is behind the same 'not request.history' guard as the lookups. "
            "If a follow-up's answer were cached, it would later be served to a STANDALONE "
            "asker -- an answer written for a conversation's context, handed to someone who "
            "never had that context. Reachable only by answering something as a follow-up "
            "first and then asking it cold."
        ),
        "steps": [
            {"do": "clear_cache"},
            {"do": "ask", "question": "What is Flexi's establishment fee?",
             "expect": {"answer_source": "generated"}},
            {"do": "follow_up", "question": "what about Angle's establishment fee?",
             "expect": {"answer_source": "generated", "source_prefix": "angle_"}},
            {"do": "reset"},
            # If the follow-up had been cached, this would come back as a cache hit.
            {"do": "ask", "question": "What is Angle's establishment fee?",
             "expect": {"answer_source": "generated"}},
        ],
    },
]
