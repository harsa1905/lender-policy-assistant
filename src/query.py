import json
import os
import re
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import chromadb
from openai import OpenAI
from src.config import (
    LLM_MODEL, RESOLVER_MODEL, REASONING_EFFORT, FANOUT_REASONING_EFFORT,
    TOP_K, CHROMA_DIR, OPENAI_API_KEY, EMBEDDING_MODEL,
)

# ── Initialise once at module load ──────────────────────────────────────────
print("Initialising embedding model and ChromaDB...")
_embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
Settings.embed_model = _embed_model
Settings.llm = None

_chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
_chroma_collection = _chroma_client.get_collection("lifex_policies")
_vector_store = ChromaVectorStore(chroma_collection=_chroma_collection)
_storage_context = StorageContext.from_defaults(vector_store=_vector_store)
_index = VectorStoreIndex.from_vector_store(
    _vector_store,
    storage_context=_storage_context
)
_openai_client = OpenAI(api_key=OPENAI_API_KEY)
print("Ready.\n")
# ────────────────────────────────────────────────────────────────────────────


def reload_index():
    """Re-point the module-level Chroma collection/index at the on-disk
    collection after it's been rebuilt by src.ingest.ingest_chunks() in this
    same process (e.g. via the /chunks/promote or /admin/reingest API
    endpoints). ingest_chunks() deletes and recreates the "lifex_policies"
    collection through its own chromadb client -- without this, the
    _chroma_collection/_index built once at module import time would keep
    referencing the now-deleted collection instead of the freshly rebuilt
    one, and every /query call after a promotion would break or silently
    serve stale data."""
    global _chroma_client, _chroma_collection, _vector_store, _storage_context, _index
    _chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    _chroma_collection = _chroma_client.get_collection("lifex_policies")
    _vector_store = ChromaVectorStore(chroma_collection=_chroma_collection)
    _storage_context = StorageContext.from_defaults(vector_store=_vector_store)
    _index = VectorStoreIndex.from_vector_store(
        _vector_store,
        storage_context=_storage_context
    )

# First keyword for each lender is its canonical name; the rest are product
# names / brand variants that also identify it. All matching is on word
# boundaries — "metro" must appear as its own word, so "metropolitan area"
# no longer falsely scopes a question to METRO, and CFAL's "DriveXpress"
# product no longer collides with Westpac's "xpress" (no word break before
# the x). The bare phrase "capital finance" was removed from CFAL for the
# same reason: "working capital finance" is ordinary broker vocabulary, not
# a lender mention.
LENDER_KEYWORDS = {
    "WESTPAC": ["westpac", "wef", "xpress"],
    "BFS": ["bfs", "branded financial", "bfs plus", "bfs prime"],
    "RESIMAC": ["resimac", "premiumplus", "premium plus"],
    "CFAL": ["cfal", "capital finance australia"],
    "ANGLE": ["angle", "angle finance"],
    "FLEXI": ["flexi", "flexicommercial", "flexipremium", "flexireplacement"],
    "METRO": ["metro", "metro finance", "metroeco"]
}


def _parse_retry_after(message: str, default: float = 5.0) -> float:
    m = re.search(r"try again in ([\d.]+)(ms|s)", message)
    if not m:
        return default
    value, unit = float(m.group(1)), m.group(2)
    seconds = value / 1000 if unit == "ms" else value
    return seconds + 0.5


def _word_match(keyword: str, text: str) -> bool:
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def _edit_distance(a: str, b: str) -> int:
    # Plain Levenshtein — small inputs (lender names vs question words), so
    # the simple DP is more than fast enough.
    if abs(len(a) - len(b)) > 1:
        return 2  # caller only cares about distance <= 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = curr
    return prev[-1]


def detect_lenders(question: str) -> list:
    """Return ALL lenders a question names, not just the first one found.

    "Compare Metro and Flexi for truck finance" names two lenders — the old
    single-lender return meant the second one's chunks were simply never
    retrieved, so comparison questions half-failed every time. A list keeps
    single-lender behaviour identical (len 1) while letting comparisons
    retrieve everything they actually mention.

    Every lender is checked on its own two tiers — canonical name ("westpac",
    "cfal", ...) then product/brand variant ("premiumplus", "metroeco",
    "flexicommercial", ...) — and the results are UNIONED across lenders,
    not gated. An earlier version returned early as soon as ANY lender
    matched tier 1, which meant a canonical mention of one lender (e.g.
    "Angle") silently suppressed a tier-2-only mention of another (e.g.
    "flexicommercial", which never matches FLEXI's tier-1 "flexi" — it's one
    unbroken word, so the word-boundary check on "flexi" fails partway
    through it). That single bug dropped FLEXI from most two-lender
    comparison questions that named it only by product name — confirmed via
    the 111-question complex eval (2026-07-22), where "Cross-lender
    comparison (2)" was the worst-scoring category specifically because of
    this. Fall back to single-typo fuzzy matching on canonical names >= 5
    chars ("westpak", "rezimac") only when NO lender matches on either tier
    at all. Short names (BFS, CFAL) are excluded from fuzzy matching: at 3-4
    letters, edit distance 1 collides with real words ("coal" is one edit
    from "cfal"), and their typo'd questions still get answered via the
    all-lender fan-out fallback.
    """
    q = question.lower()
    exact = {l for l, kws in LENDER_KEYWORDS.items() if _word_match(kws[0], q)}
    secondary = {
        l for l, kws in LENDER_KEYWORDS.items()
        if any(_word_match(kw, q) for kw in kws[1:])
    }
    combined = sorted(exact | secondary)
    if combined:
        return combined
    tokens = set(re.findall(r"[a-z]+", q))
    fuzzy = []
    for lender, kws in LENDER_KEYWORDS.items():
        name = kws[0]
        if len(name) >= 5 and any(
            len(t) >= 5 and _edit_distance(t, name) <= 1 for t in tokens
        ):
            fuzzy.append(lender)
    return fuzzy


def _chat_completion(model: str, prompt: str, max_output_tokens: int,
                     json_mode: bool = False, reasoning_effort: str = None):
    """One place for every OpenAI call — the GPT-5 family has a different
    calling convention (max_completion_tokens instead of max_tokens, no
    temperature parameter, reasoning_effort), and hardcoding one style at
    each call site is how the last model swap broke. Retries rate limits
    with the server-suggested backoff.
    """
    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    if model.startswith(("gpt-5", "o1", "o3", "o4")):
        # Reasoning tokens count against max_completion_tokens, so the cap
        # needs headroom beyond the visible answer or the answer gets
        # silently truncated by the model's own thinking.
        kwargs["max_completion_tokens"] = max_output_tokens + 512
        kwargs["reasoning_effort"] = reasoning_effort or REASONING_EFFORT
        # GPT-5's own output-length dial. Without it gpt-5-mini writes
        # 3-5k-char essays for one-line questions no matter what the prompt
        # says about brevity — the parameter is the mechanism that actually
        # constrains it, the prompt text alone is not.
        kwargs["verbosity"] = "low"
    else:
        kwargs["max_tokens"] = max_output_tokens
        kwargs["temperature"] = 0

    max_retries = 8
    cap_raised = False
    for attempt in range(max_retries):
        try:
            response = _openai_client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            content = choice.message.content or ""
            if (not content.strip() and choice.finish_reason == "length"
                    and "max_completion_tokens" in kwargs and not cap_raised):
                # All of max_completion_tokens went to internal reasoning
                # and none was left for the visible answer. Retry ONCE with
                # a doubled cap rather than returning an empty answer —
                # once only, so a runaway generation can't keep doubling
                # into an essay-length response.
                kwargs["max_completion_tokens"] *= 2
                cap_raised = True
                continue
            return content
        except Exception as e:
            is_rate_limit = "rate_limit" in str(e).lower() or "429" in str(e)
            if attempt < max_retries - 1 and is_rate_limit:
                time.sleep(_parse_retry_after(str(e)))
                continue
            raise
    return ""


def _resolve_followup(question: str, history: list) -> tuple:
    """Turn a follow-up message into (standalone_question, wants_more_detail).

    Follow-ups are conversational — "details", "what about westpac?", "and for
    a used one?" — and every keyword-list / previous-question-fallback attempt
    at interpreting them broke on the next phrasing nobody predicted ("more
    detail" matched but "details" didn't; a follow-up naming a different lender
    kept the old lender's scope). Understanding phrasing is the one thing the
    LLM is reliably good at, so a single small call does both jobs at once:
    rewrite the message into a question that stands on its own (which then
    drives lender detection and retrieval exactly like a fresh question), and
    flag whether the broker is asking for elaboration on the previous answer
    rather than asking something new.
    """
    recent = "\n\n".join(
        f"Broker: {h['question']}\nAssistant: {h['answer']}" for h in history[-3:]
    )
    classify_prompt = f"""Conversation between a finance broker and a lending-policy assistant:

{recent}

The broker's latest message: "{question}"

Rewrite that latest message as one fully self-contained question that could be understood with no conversation history — resolve pronouns and implied subjects from the conversation (e.g. "what about westpac?" after a question about truck financing becomes "can Westpac finance trucks over 5.5 tonnes?").

Special cases:
- If the latest message is only asking to elaborate, expand, or give more detail on the previous answer (however it's phrased), the standalone question is just the previous question restated, and wants_more_detail is true.
- If the latest message is only asking to reformat the previous answer (shorter, simpler, as a list...), the standalone question is also the previous question restated, and wants_more_detail is false.
- If the latest message already stands on its own, keep it as-is.

Consistency check (a confirmed bug this exists to prevent): wants_more_detail can only be true when the standalone_question you just wrote is the SAME question as before, word-for-word or a plain restatement — it means "give a fuller answer to that exact same question." If you changed ANY concrete detail in the standalone_question (a different lender, a different number/threshold/amount, a different asset, a different term), that is a NEW question with its own normal-depth answer, not elaboration — set wants_more_detail to false even if the broker's phrasing sounds like a follow-up ("what about...", "and..."). Example: previous question "which lenders finance trucks over 5.5 tonnes?", latest message "what about over 4.4 tonnes?" — the threshold changed, so standalone_question is "which lenders finance trucks over 4.4 tonnes?" and wants_more_detail is false. Contrast with latest message "give me more on that" for the same previous question — standalone_question stays "which lenders finance trucks over 5.5 tonnes?" (unchanged) and wants_more_detail is true.

Reply with only JSON: {{"standalone_question": "...", "wants_more_detail": true or false}}"""
    try:
        raw = _chat_completion(RESOLVER_MODEL, classify_prompt,
                               max_output_tokens=200, json_mode=True)
        parsed = json.loads(raw)
        standalone = str(parsed.get("standalone_question") or "").strip()
        if not standalone:
            return question, False
        return standalone, bool(parsed.get("wants_more_detail"))
    except Exception:
        # If the classifier call itself fails (network, malformed JSON), the
        # question still gets answered — just without follow-up resolution,
        # same as before this existed.
        return question, False


def _classify_fanout_effort(question: str) -> str:
    """For a fan-out question (no lender named), decide whether it needs
    careful step-by-step reasoning (REASONING_EFFORT, "low") or is a
    straightforward category lookup (FANOUT_REASONING_EFFORT, "none").

    Same rationale as _resolve_followup just above: a keyword list
    ("cheapest", "lowest"...) misses phrasings like "which one's the better
    deal" that carry no literal ranking word but still need a comparison —
    understanding intent is what the LLM is for, not pattern matching.
    Built after a confirmed bug: at "minimal" effort on a genuine ranking
    question, the model sometimes named a lender's rate as cheapest without
    checking it actually met every constraint in the question (e.g. a term
    length the discounted rate doesn't extend to) — the same failure mode
    "low" was originally raised to fix for single-lender calculations, just
    showing up in cross-lender ranking instead. A/B tested 2026-07-27: at
    "low" effort the model correctly excluded a lender whose discount only
    applied at a shorter term than asked for; at "minimal" it didn't always.

    BROADENED 2026-08-18 beyond ranking, after the ranking-only split
    produced a confirmed wrong answer on an ELIGIBILITY question. "Carpenter
    registered ABN and GST last week, wants a ute, which lender can he
    choose?" classified as a simple eligibility scan -> "none", and came back
    recommending the one lender the client is actually ineligible for (Angle
    Start-Up needs 3 months' trading) while dismissing the one that fits (BFS
    New Business Ventures explicitly covers "less than 12 months ABN").
    Controlled A/B on that exact question with identical retrieval (63
    chunks) and effort as the only variable: "none" answered Angle, "low"
    answered BFS and correctly ruled Angle out on the 3-month rule. The
    "none" answer even quoted BFS's "less than 12 months ABN" requirement --
    which one week satisfies -- and then concluded the opposite, which is
    what insufficient reasoning depth looks like rather than missing data.

    So the real axis was never ranking-vs-eligibility: it's whether a
    specific customer figure has to be tested against each lender's own
    threshold. Working out which side of a threshold "last week" falls on is
    as demanding as picking a cheapest rate, and now gets the same effort.
    Pure category lookups ("which lenders finance trucks") stay on the cheap
    path -- that's what preserves the fan-out latency win this constant
    exists for; see FANOUT_REASONING_EFFORT's comment in config.py.
    """
    classify_prompt = f"""A finance broker asked a policy assistant this question, with no specific lender named — the assistant will scan across all 7 lenders on the panel to answer it:

"{question}"

Decide whether answering it correctly needs careful step-by-step reasoning, or whether it's a straightforward lookup across the lenders.

Answer TRUE (needs careful reasoning) if EITHER applies:
1. It requires comparing a specific number across lenders and picking one out as the best/cheapest/highest/lowest — even if words like "cheapest" or "best" aren't used literally (e.g. "which one's the better deal", "who should I go with for this").
2. The question gives a SPECIFIC customer detail or figure — an ABN/GST age, a credit score, a loan amount, an asset age, a term length, a deposit, an income — that has to be tested against each lender's own threshold to work out who actually qualifies. Deciding which side of a threshold a customer falls on is exactly where a quick scan goes wrong: e.g. "ABN registered last week" has to be checked against one lender's "minimum 3 months trading" (fails it) and another's "less than 12 months ABN" (passes it) — those cut in opposite directions and are easy to get backwards.

Answer FALSE (straightforward) only when it's a pure category lookup with no customer-specific figure to test against thresholds — e.g. "which lenders finance trucks", "who can do software", "which lenders offer balloon payments".

Reply with only JSON: {{"needs_deeper_reasoning": true or false}}"""
    try:
        raw = _chat_completion(RESOLVER_MODEL, classify_prompt,
                               max_output_tokens=60, json_mode=True)
        parsed = json.loads(raw)
        return REASONING_EFFORT if parsed.get("needs_deeper_reasoning") else FANOUT_REASONING_EFFORT
    except Exception:
        # Fail toward correctness, not speed, on a classifier hiccup — an
        # occasional slow answer is a smaller cost than a wrong answer.
        return REASONING_EFFORT


def _check_profile_threshold(question: str, context: str) -> str:
    """Prototype: a general-purpose replacement for one-off prompt bullets
    like "check ABN/GST tenure when the broker says 'first asset finance'".

    That bullet fixed a real bug (a first-time-borrower question got an
    unqualified "yes" from Resimac despite retrieving the exact chunk with
    the ABN/GST tenure gate) — but it's a hardcoded rule for ONE field on
    ONE kind of table, and the same silent-skip failure could just as easily
    happen on a credit-score minimum, a deposit minimum, an asset-age limit,
    or a trading-history requirement neither of us has hit in testing yet.
    Growing the prompt one named-field bullet at a time doesn't scale and
    dilutes the model's attention across an ever-larger instruction list.

    This does the same job structurally instead of by name: given the
    question and the actual retrieved excerpts, ask a small model whether
    there's ANY tier/threshold table gated by the customer's own profile,
    and whether the question's wording places the customer against it. If
    so, it returns one concrete sentence to inject directly into the
    answering prompt — the same mechanism as _classify_fanout_effort, doing
    the narrow "check this one thing" job an LLM is reliable at, rather than
    asking one giant prompt to notice every such table itself.
    """
    check_prompt = f"""A finance broker asked a lending-policy assistant this question:

"{question}"

Here are the policy excerpts the assistant retrieved to answer it:

{context}

Look ONLY for eligibility gates in these excerpts that are structured as a tier, band, or threshold tied to the CUSTOMER'S OWN profile or history — things like a minimum ABN age, a minimum GST registration age, a minimum credit score, a minimum deposit, or a minimum trading history. Ignore asset-level facts like loan caps, asset age limits, or rates — those aren't customer-profile gates.

If you find such a table AND the broker's question states or clearly implies where the customer sits against it (e.g. "first asset finance deal", "new business", "just started", "been trading 5 years", a stated credit score, a stated deposit) — write ONE short, concrete sentence naming the specific threshold and whether the customer's stated/implied position clears it, fails it, or is genuinely unclear. Write it as something to state plainly in the answer, not a note to yourself.

If there's no such customer-profile threshold table here, or the question gives no signal about the customer's position against one, reply with an empty note — don't manufacture a check that doesn't apply.

Reply with only JSON: {{"note": "..."}}"""
    try:
        raw = _chat_completion(RESOLVER_MODEL, check_prompt,
                               max_output_tokens=150, json_mode=True)
        parsed = json.loads(raw)
        return str(parsed.get("note") or "").strip()
    except Exception:
        return ""


def refresh_answer_with_new_chunk(question: str, current_answer: str,
                                   old_chunk_text: str, new_chunk_text: str) -> dict:
    """Check whether a previously human-corrected library answer still holds
    after its source chunk was edited, and if not, produce an updated
    version with just the outdated facts replaced.

    This exists for the answer library's promote-time refresh: a broker
    correction saved against chunk content that later changes (a rate
    update, a threshold change) would otherwise silently go stale with no
    signal to anyone. Deliberately narrow and conservative rather than
    freely rewriting the answer -- a wrong "helpful" rewrite is worse than
    leaving a stale answer flagged for a human, so the model is asked to
    change only what the chunk update actually requires and to say so
    plainly when it isn't sure.

    Returns {"status": "unchanged"|"updated"|"unclear", "updated_answer":
    str|None, "note": str} -- "unchanged" means the chunk edit didn't
    actually affect anything this answer stated (e.g. a different section of
    the same chunk changed); "updated" means updated_answer replaces the old
    one; "unclear" means don't auto-apply anything, surface for review.
    """
    prompt = f"""A broker asked a lending-policy assistant this question:

"{question}"

This is the previously-approved, human-corrected answer that was given:

{current_answer}

That answer was based on this policy chunk:

--- OLD CHUNK CONTENT ---
{old_chunk_text}

The chunk has since been edited to this:

--- NEW CHUNK CONTENT ---
{new_chunk_text}

Decide whether the approved answer above is still accurate given the new chunk content.

- If nothing the answer actually states was affected by the edit (the changed part of the chunk is unrelated to what this answer covers), respond with status "unchanged".
- If a number, rate, threshold, date, or eligibility fact the answer states has changed in the new chunk, respond with status "updated" and provide the full corrected answer text, preserving the original wording and structure exactly except for the specific outdated facts -- change only what the chunk update actually requires, don't rewrite unrelated phrasing.
- If you cannot confidently tell whether the answer is still accurate (the change is structural, ambiguous, or the answer's claim can't be cleanly mapped to a single new value), respond with status "unclear" and explain why in one sentence -- do not guess.

Reply with only JSON: {{"status": "unchanged" or "updated" or "unclear", "updated_answer": "..." or null, "note": "..."}}"""
    try:
        raw = _chat_completion(RESOLVER_MODEL, prompt, max_output_tokens=800, json_mode=True)
        parsed = json.loads(raw)
        status = parsed.get("status")
        if status not in ("unchanged", "updated", "unclear"):
            return {"status": "unclear", "updated_answer": None, "note": "Refresh check returned an unrecognised status."}
        return {
            "status": status,
            "updated_answer": parsed.get("updated_answer") if status == "updated" else None,
            "note": str(parsed.get("note") or "").strip(),
        }
    except Exception as e:
        # A failed check should never silently keep serving a possibly-stale
        # answer as if it were still verified -- surface it for review.
        return {"status": "unclear", "updated_answer": None, "note": f"Refresh check failed: {type(e).__name__}"}


def questions_require_same_answer(question: str, candidate_question: str) -> bool:
    """Narrow LLM gate for the query cache: decides whether two questions
    are close enough to share a cached answer.

    Built after calibrating embedding similarity directly against this
    domain's questions and finding it isn't reliable enough to gate a cache
    alone: "BFS Tier 2's minimum credit score" vs "BFS Tier 3's minimum
    credit score" scored 0.93 cosine similarity on bge-base -- higher than
    several genuine paraphrase pairs -- despite having different correct
    answers. Embedding similarity is still used as a cheap pre-filter (its
    low end cleanly separates unrelated questions, ~0.35-0.40 measured), but
    the actual yes/no gate is this direct comparison, which can see that
    "Tier 2" and "Tier 3" are different in a way a cosine score can't.

    Deliberately conservative: only answer true when confident nothing in
    either question could change the answer. A missed cache hit costs a few
    seconds and a small API charge; a wrongly-served cached answer costs a
    broker a wrong financial figure with no indication anything's off.
    """
    prompt = f"""Two questions asked of a lending-policy assistant covering 7 lenders:

Question A: "{question}"
Question B: "{candidate_question}"

Question B already has a saved, trusted answer. Decide whether Question A would get the EXACT SAME correct answer -- not just a similar or related one.

Answer false if there is ANY SUBSTANTIVE difference between the two questions that could change the correct answer -- a different lender, product, tier or plan level, asset class or age, borrower profile (property-backed vs not, ABN/GST age, credit score), loan amount or band, sale type (dealer vs private), term length, or any other detail a lending policy could condition on. Examples that must be answered false: "Tier 2" vs "Tier 3", "primary asset" vs "secondary asset", "property-backed" vs "non-property-backed" -- these look structurally identical but name a different value for something the policy conditions on.

Answer true for genuine paraphrases -- same lender, same product/tier, same asset, same every other detail, just worded differently. This includes ordinary rewording that does NOT change what's being asked:
- Abbreviations and their expansions ("EVs" = "electric vehicles", "CCR score" = "credit score" when the same lender/tier is named in both -- when a lender is stated, assume "credit score" refers to whatever specific score type that lender actually uses, not a genuinely different metric)
- A lender's short name vs its full name/brand variant ("Angle" = "Angle Finance", "flexi" = "flexicommercial") -- these name the identical lender, never treat them as possibly different
- Different verbs for the same capability question ("can X finance Y" = "does X do Y" = "does X fund Y") -- these all ask the same eligibility question, not different ones
- Synonyms for the same concept ("fund" = "finance", "max" = "maximum", "docs" = "documentation")
- Reordered clauses, different question phrasing, singular vs plural ("a prime mover" = "prime movers" when asking generally, not about a specific count), formatting of numbers ("$300k" = "$300,000")
Don't manufacture a substantive difference out of a wording choice like these, even when several appear in the same pair -- multiple simultaneous cosmetic differences are still just cosmetic. If every concrete detail (lender, tier, asset, profile, amount, etc.) is genuinely the same and only the phrasing differs, answer true.

If you are unsure whether a difference is substantive (changes the answer) or just cosmetic (same answer, different words), answer false -- a missed cache hit costs a few seconds re-asking the model; a wrongly-served cached answer hands a broker a confidently wrong financial figure with nothing to flag it. But don't default to false out of caution on a difference you can see is purely cosmetic.

Reply with only JSON: {{"same_answer": true or false}}"""
    try:
        raw = _chat_completion(RESOLVER_MODEL, prompt, max_output_tokens=30, json_mode=True)
        parsed = json.loads(raw)
        return bool(parsed.get("same_answer"))
    except Exception:
        # A failed check must never silently allow a cache hit through.
        return False


def get_retriever(where_filter=None, top_k=TOP_K):
    if where_filter:
        return _index.as_retriever(
            similarity_top_k=top_k,
            vector_store_kwargs={"where": where_filter}
        )
    return _index.as_retriever(similarity_top_k=top_k)


# Comfortably above the chunk count of any single lender (currently 8-10).
# Asking for more than a lender has just returns everything that lender has,
# scored and relevance-ordered.
ALL_LENDER_CHUNKS_K = 20

# The explicit go-through-every-lender checklist instructions were built for
# gpt-4o-mini, which reliably stopped after 3-5 of the 7 lenders without
# them. Toggleable so the same experiment can be re-run against future
# models: with a stronger answering model these may be unnecessary — or
# still load-bearing. Decide from measurement, not vibes.
ENUMERATION_GUARDRAILS = True


def _merge(target: dict, nodes) -> None:
    for n in nodes:
        target[n.metadata.get("chunk_id")] = n


def retrieve_nodes(question: str, lenders: list, log):
    """Retrieve EVERY chunk for each relevant lender, relevance-ordered.

    This replaces the old union/rerank/fan-out machinery entirely. That
    machinery existed to squeeze the right 5 chunks out of a lender's pool
    under a tight TOP_K — and its failure mode was that a correct chunk
    ranked one place past the cutoff simply never reached the model, which
    is unrecoverable no matter how good the prompt is. But each lender only
    has ~8-10 hand-curated chunks (~5-6k tokens), so the whole pool fits in
    the prompt at negligible cost: include everything, and let embedding
    scores decide only the ORDER chunks appear in, never whether they appear
    at all. A retrieval miss for a scoped lender is now structurally
    impossible, which also makes the cross-encoder reranker (its load time,
    its ~1GB of RAM, its known demote-a-correct-chunk failure mode)
    unnecessary — it existed solely to fix ranking near the old cutoff.
    """
    if not lenders:
        log("No lender detected — including every lender's chunks")
        lenders = list(LENDER_KEYWORDS)
    seen = {}
    for lender_code in lenders:
        _merge(seen, get_retriever(
            {"lenders": {"$eq": lender_code}},
            top_k=ALL_LENDER_CHUNKS_K,
        ).retrieve(question))
    if len(lenders) == 1:
        return sorted(seen.values(), key=lambda n: n.score or 0, reverse=True)
    # Multi-lender: keep per-lender retrieval order; the caller groups the
    # chunks under per-lender headings, so cross-lender score ordering
    # doesn't matter here.
    return list(seen.values())


def detect_and_apply_correction(question: str, history: list):
    """Check whether the broker's latest message is correcting the
    assistant's previous answer -- as opposed to a new question, a
    follow-up about something else, or a "give me more detail" request --
    and if so, produce the corrected answer ready to save into the answer
    library immediately (per-project decision: chat corrections go live
    right away, unlike Review-tab entries which wait for approval).

    Returns None if this isn't a correction. Otherwise a dict:
    {"original_question": str, "corrected_answer": str, "chunk_ids": [...]}
    -- the caller (api.py's /query handler) is responsible for actually
    calling answer_library.save_entry with this.

    Deliberately narrow, same pattern as _resolve_followup/
    _check_profile_threshold: one small classifier call rather than folding
    "was this a correction?" detection into the main answering prompt.
    """
    if not history:
        return None
    prev = history[-1]
    prompt = f"""Conversation between a finance broker and a lending-policy assistant:

Broker: {prev['question']}
Assistant: {prev['answer']}

The broker's next message: "{question}"

Decide whether the broker's next message is CORRECTING the assistant -- explicitly or clearly stating that the previous answer was wrong, inaccurate, or outdated, AND asserting what the correct information actually is.

This is NOT a correction (answer false):
- A new question, even about a related or different lender/topic ("what about Metro instead?", "and Westpac?") -- these are follow-up questions, not corrections, even though they change the subject rather than repeating it.
- A request for more detail, clarification, or reformatting of the same answer.
- Mere skepticism, doubt, or a request to double-check or re-verify, WITHOUT the broker's message itself stating a specific replacement fact -- e.g. "are you sure about that?", "can you double check that rate?", "that doesn't sound right, can you confirm?". These express doubt but supply no new value to correct to, so there is nothing to save -- answer false even though the broker may be right to be suspicious.

This IS a correction (answer true) ONLY when the broker's own message states or unambiguously implies the specific correct value itself -- e.g. "no, that's wrong, the actual rate is 7.15%", "actually the max term is 72 months, not 60", "that's incorrect, BFS doesn't offer that at all." The replacement fact must come from the broker's message, not be inferred or invented by you.

First, extract the specific new value or fact the broker's message ITSELF states, quoting it directly from their message ("broker_stated_value"). If their message doesn't actually contain a specific replacement value -- only doubt, a question, or a request to verify -- leave this null; do not paraphrase, infer, or invent one just because the assistant's answer might plausibly be wrong.

Only if broker_stated_value is non-null: write out the FULL corrected version of the assistant's last answer, keeping everything that wasn't wrong exactly as it was, and changing only what broker_stated_value actually addresses. Never introduce a number or fact that isn't traceable to broker_stated_value.

Reply with only JSON: {{"broker_stated_value": "..." or null, "is_correction": true or false, "corrected_answer": "..." or null}}"""
    try:
        raw = _chat_completion(RESOLVER_MODEL, prompt, max_output_tokens=600, json_mode=True)
        parsed = json.loads(raw)
        # broker_stated_value is the load-bearing check, not is_correction --
        # forcing the model to first quote something concrete from the
        # broker's own message (rather than jump straight to a verdict)
        # is what actually suppresses the fabrication failure mode measured
        # during testing (gpt-4o-mini invented a specific replacement number
        # for pure-skepticism messages like "are you sure about that?" when
        # only asked for a true/false verdict directly).
        if not parsed.get("broker_stated_value") or not parsed.get("is_correction") or not parsed.get("corrected_answer"):
            return None
    except Exception:
        # A failed classifier call should fall through to the normal
        # pipeline, not silently drop what might be a real correction.
        return None

    # Conversation history only carries {question, answer}, not chunk_ids,
    # so re-retrieve to snapshot what prev["answer"] was actually based on --
    # retrieval is deterministic and nothing chunk-wise has changed between
    # the previous turn and now within the same conversation, so this
    # reproduces the same sources that answer actually drew on.
    #
    # prev["question"] is whatever the broker literally typed for that turn,
    # not the resolved standalone question query_policies() actually
    # retrieved against -- if that turn was itself a follow-up ("what about
    # westpac?"), running detect_lenders on it directly can find the wrong
    # lender (or none) and attach the wrong chunk_ids to this correction.
    # Re-run the same resolution step against the history that was available
    # at the time (everything before prev) to reconstruct what was actually
    # retrieved for it -- _resolve_followup is on RESOLVER_MODEL at
    # temperature=0, already relied on elsewhere in this file as stable
    # enough to reproduce the same resolution deterministically.
    prev_question = prev["question"]
    if len(history) > 1:
        prev_question, _ = _resolve_followup(prev_question, history[:-1])

    lenders = detect_lenders(prev_question)
    nodes = retrieve_nodes(prev_question, lenders, lambda *a, **k: None)
    chunk_ids = list(dict.fromkeys(
        node.metadata.get("chunk_id") for node in nodes if node.metadata.get("chunk_id")
    ))

    return {
        "original_question": prev_question,
        "corrected_answer": parsed["corrected_answer"],
        "chunk_ids": chunk_ids,
    }


def _handle_meta_question(question: str, history: list):
    """Check whether this message is conversational/meta -- a greeting,
    "are you online?", "what can you help with?", small talk -- rather than
    an actual policy question, and if so produce the reply directly.

    Returns None if this is a real policy question (fall through to the
    normal retrieval pipeline). Otherwise a short reply string, ready to
    return as-is.

    Only ever called when detect_lenders() found no lender (see
    query_policies) -- any question naming a lender is obviously a real
    policy question, so this narrow check only needs to run on the rarer
    branch that would otherwise trigger a full 7-lender fan-out. Before this
    existed, EVERY no-lender message (including "are you online?") fanned
    out to all 7 lenders' chunks (~60+), which is why a plain greeting could
    come back tagged with an essentially-arbitrary lender (whichever chunk
    scored highest in that dump) and a huge, meaningless source list.

    Combined detect+respond in one small call, same pattern as
    detect_and_apply_correction -- and just as deliberately conservative in
    the failure direction: a real policy question wrongly treated as meta
    would get a useless non-answer instead of the broker's actual answer,
    so this fails toward "not meta" (returns None, falls through to the
    normal pipeline) on anything ambiguous or on a classifier error.
    """
    recent = ""
    if history:
        recent = "\n\nRecent conversation so far (most recent last):\n" + "\n\n".join(
            f"Broker: {h['question']}\nYou: {h['answer']}" for h in history[-3:]
        )
    prompt = f"""You are the pre-check for a lending-policy assistant that covers 7 lenders on its panel: Resimac, BFS, CFAL, Westpac, Angle, Flexi, Metro.

The broker's message: "{question}"{recent}

Decide: is this an actual policy question that needs looking up specific lender content (a rate, an eligibility rule, a document requirement, an exclusion, a comparison, anything concerning lending policy) -- OR is it conversational/meta (a greeting, asking if you're online or working, asking what you can help with or who you are, thanks/acknowledgement, small talk, or something unrelated to lending policy entirely)?

A vague, underspecified, or very short message still counts as a REAL policy question (not meta) if it's actually asking about lending/finance in some way -- e.g. "best rate?" or "BFS?" with nothing else still needs the real pipeline (which already knows how to ask a clarifying question when there's not enough to work with). Only mark something meta when it isn't attempting to ask a lending policy question at all.

If it's a real policy question, or you're not sure, reply is null -- do not attempt to answer it yourself here.

If it's genuinely conversational/meta, write a short, natural one-to-two-sentence reply the way the assistant would actually say it -- friendly, no policy content, no invented numbers. Mention that you're the LifeX Policy Assistant covering the 7 panel lenders above only where that's actually relevant to what was asked (e.g. "are you online?", "what can you help with?") -- a simple "thanks!" just gets an equally simple acknowledgement, not a re-pitch of what you do.

Reply with only JSON: {{"is_meta": true or false, "reply": "..." or null}}"""
    try:
        raw = _chat_completion(RESOLVER_MODEL, prompt, max_output_tokens=150, json_mode=True)
        parsed = json.loads(raw)
        if not parsed.get("is_meta") or not parsed.get("reply"):
            return None
        return parsed["reply"]
    except Exception:
        return None


def query_policies(question: str, verbose: bool = True, history: list = None):
    def log(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    history = history or []
    # Follow-ups only make sense in light of the conversation ("details",
    # "what about westpac?"). Resolve them into a standalone question once,
    # up front, and everything downstream — lender detection, retrieval —
    # treats it exactly like a fresh question. The wants-more-detail flag
    # matters separately because a "keep it brief" instruction and a "give
    # me more detail" request are direct opposites; when both are in the
    # prompt at once the repeated brevity instruction wins and the answer
    # comes back a reworded copy of the last one, so the brevity instruction
    # has to actually be switched off in code for this one turn.
    retrieval_question = question
    more_detail_requested = False
    if history:
        retrieval_question, more_detail_requested = _resolve_followup(question, history)

    log(f"\nQuestion: {question}")
    if retrieval_question != question:
        log(f"Resolved to: {retrieval_question}")
    log("-" * 60)

    lenders = detect_lenders(retrieval_question)
    log(f"Detected lender(s): {', '.join(lenders) if lenders else 'None (searching all)'}")

    if not lenders:
        meta_reply = _handle_meta_question(retrieval_question, history)
        if meta_reply is not None:
            log("Detected a conversational/meta message — skipping retrieval")
            log(f"\nAnswer:\n{meta_reply}")
            return meta_reply, []

    nodes = retrieve_nodes(retrieval_question, lenders, log)

    log(f"\nRetrieved {len(nodes)} chunks:")
    for i, node in enumerate(nodes):
        chunk_id = node.metadata.get('chunk_id', 'unknown')
        lender_tag = node.metadata.get('lenders', 'unknown')
        intent_tag = node.metadata.get('topic_intent', 'unknown')
        score = node.score
        log(f"  [{i+1}] {chunk_id} | {lender_tag} | {intent_tag} | score: {score:.3f}")

    lender_checklist = None
    single_lender_pitfall = ""
    if len(lenders) == 1:
        # Single lender — a flat, relevance-ordered list is fine, the model
        # only has one lender's material to reason about.
        context = ""
        for node in nodes:
            chunk_id = node.metadata.get('chunk_id', 'unknown')
            lender_tag = node.metadata.get('lenders', 'unknown')
            context += f"\n[Source: {chunk_id} | Lender: {lender_tag}]\n{node.text}\n"
        # The full known_pitfalls block below is deliberately scoped to
        # multi-lender questions only (unconditional bullets previously
        # measurably hurt single-lender arithmetic questions — noise the
        # model doesn't need when it's just working a rate build-up). But
        # a CFAL-only question loses the ONE fact that would let it catch
        # a broker quoting Westpac's rate as if it were CFAL's (confirmed
        # gap: a broker asking about CFAL's "7.75%" gets correctly told
        # not to trust that figure, but never told whose rate it actually
        # is, because Westpac's chunk is never retrieved for a CFAL-only
        # question). CFAL doesn't have its own public rates to build up
        # arithmetically, so this doesn't carry the same noise risk the
        # scoping comment above was written to avoid.
        if lenders == ["CFAL"]:
            single_lender_pitfall = "\nWorth knowing: CFAL publishes no public interest rate card at all — pricing must come from the CFAL Credit Manager. If the broker mentions a specific rate as if it might be CFAL's (e.g. a headline figure like 7.75%), that number belongs to a different lender on this panel (most likely Westpac, whose Xpress dealer-car rate this often is) — say so and don't confirm or quote it as CFAL's.\n"
    else:
        # Multiple lenders (a named comparison, or no lender detected → all
        # seven): a flat mixed list left the model skipping lenders when
        # asked to enumerate them — a relevant chunk buried in the middle of
        # a mixed pile is easy to miss even though it's present. Grouping
        # the excerpts under a per-lender heading gives the model the same
        # one-lender-at-a-time structure the prompt explicitly asks it to
        # follow.
        by_lender = {}
        for node in nodes:
            lender_tag = node.metadata.get('lenders', 'unknown')
            by_lender.setdefault(lender_tag, []).append(node)
        context = ""
        for lender_tag in sorted(by_lender):
            context += f"\n=== {lender_tag} ===\n"
            for node in by_lender[lender_tag]:
                chunk_id = node.metadata.get('chunk_id', 'unknown')
                context += f"\n[Source: {chunk_id}]\n{node.text}\n"
        # A generic "go through every lender" instruction wasn't concrete
        # enough on its own — the model kept quietly stopping after 3-5 of
        # the 7 lenders even with the excerpts grouped by lender above.
        # Naming the exact lenders present turns it into a checklist instead
        # of something the model has to notice for itself.
        lender_checklist = ", ".join(sorted(by_lender))

    # Prototype general-purpose replacement for one-off "check field X
    # against threshold Y" prompt bullets — see _check_profile_threshold's
    # docstring. Runs unconditionally (single- or multi-lender) since a
    # tenure/threshold gate can matter either way (e.g. comparing two
    # lenders' minimum ABN age for the same customer).
    threshold_note = _check_profile_threshold(retrieval_question, context)
    threshold_block = f"\nWorth checking: {threshold_note}\n" if threshold_note else ""

    checklist_block = ""
    if lender_checklist and ENUMERATION_GUARDRAILS:
        if more_detail_requested:
            brevity_instruction = "The broker just asked for more detail than your last answer had, so this is the one case where brevity is NOT the goal — go back into these same excerpts and surface specifics you left out last time for each lender (secondary numbers, extra conditions, exceptions), so this answer is noticeably fuller than before, not a reworded copy of it. Do NOT respond by asking clarifying questions — even if your last answer asked some, the broker chose to ask for detail instead of answering them, so give the fuller information now; where something is unspecified, briefly cover the relevant scenarios instead of asking which one applies."
        else:
            # Replaced 2026-07-27: the old version forced one line/clause per
            # lender ("ANGLE — Yes-with-conditions: ...") which reliably kept
            # every lender in the answer but reads like a compliance form, not
            # a broker talking. A/B tested a conversational, verdict-grouped
            # version against the strict per-lender one on 3 fan-out
            # questions (which lenders finance trucks >5.5T / buses /
            # software) — both variants named every lender in every run,
            # zero silent drops, because the completeness instruction above
            # (go through the list one lender at a time before writing
            # anything) is what actually forces the check; this instruction
            # only ever controlled the OUTPUT format, not the checking. Kept
            # the "still needs to be named somewhere" rule explicit below so
            # grouping by verdict doesn't quietly become an excuse to drop one.
            # Tightened 2026-07-27: the verdict-grouped version above still let
            # depth creep back in — "fold in a genuinely different number or
            # condition" per lender, applied across 6-7 lenders, added back up
            # to the same dense wall of reasoning this was meant to replace
            # (confirmed complaint: "which lenders can finance trucks over 5.5
            # tonnes" came back as a paragraph of ABN years/credit scores/
            # loadings per lender — technically grouped by verdict, still not
            # how a broker actually talks). The fix isn't grouping, it's
            # depth: naming who's in each group IS the answer for a plain
            # yes/no scan; supporting mechanics only belong in if the broker
            # will otherwise be confused or if it's literally the figure being
            # compared (a ranking question's numbers stay — that's not extra
            # depth, that's the answer).
            brevity_instruction = "Write this the way a broker would actually say it out loud on a quick call — group lenders by verdict ('X, Y and Z can do this; A and B can't'). For a plain yes/no eligibility scan, that grouping IS usually the whole answer: just name who's in each group, nothing more. Every lender on the list above still needs to be named somewhere, but naming them is enough — don't also justify each one with a clause of its own eligibility mechanics (ABN years, credit score thresholds, specific loadings, age limits); stacked across several lenders that turns a quick verdict into a wall of reasoning nobody asked for, and it reads like a compliance form again even when it's grouped by verdict. The broker will ask if they want the mechanics behind a specific one. Add a short reason only when it's genuinely necessary: a hard exclusion worth knowing by name (e.g. 'BFS is vehicles under 4.5T only, so no'), or the actual number the broker's question was about (a rate, a cap, an age limit — if that figure is literally what's being compared or ranked, keep it). It's the routine surrounding mechanics that get cut, not the thing that was actually asked. When in doubt, leave detail out — a short, clear answer beats a paragraph justifying every entry on it.\n\nOne required exception, non-negotiable regardless of how short the rest of the answer is: if the broker names ONE specific attribute to compare (e.g. \"primary asset age\") and your excerpts show the SAME lenders' figures for closely-related categories too (secondary/tertiary assets, a different term band, etc.), and those related figures actually differ between the lenders — you must still add that as a single short line. This is a previously-confirmed failure mode (concluding lenders \"match\" after checking only the named attribute, while a closely-related figure sitting right there in the same excerpt quietly differs), and trimming it for brevity is not acceptable. Worked example: \"Both cap primary assets at 25yr EOT — but Angle's secondary/tertiary caps (15/10yr) are higher than Resimac's (10/5yr).\" That second sentence is required, not optional padding, even in an otherwise two-line answer."
        # Found via the 111-question complex eval (2026-07-22): the checklist
        # below this point was written for yes/no eligibility fan-out ("which
        # lenders can finance X?") and reliably got every lender a verdict.
        # But "which lender is cheapest" / "compare X across the panel"
        # questions need a DIFFERENT specific fact extracted per lender (a
        # rate, a fee, an age limit) before any ranking or recommendation is
        # possible — and without being told that explicitly, the model would
        # rank/recommend after checking only 2-3 lenders' figures, missing the
        # actual cheapest one sitting in a chunk it never went back to. Rather
        # than classify the question as "eligibility" vs "comparison" (another
        # brittle keyword judgment call), one instruction covers both: extract
        # whatever specific fact is being asked about for every lender in the
        # list first, and only reason/compare/rank once that extraction is
        # complete for all of them.
        # Sourced from Policy_Concept_FAQ.md (2026-07-22, team-provided glossary
        # of cross-lender terminology traps). Cross-checked its ~27 concepts
        # against the actual chunk files first — every fact in it already
        # exists in the chunks, so this isn't new policy data. What it does
        # have is a concise naming of the exact confusions the complex eval
        # caught the model making (CFAL/Westpac rate conflation, bureau
        # mixups) — pulling those into short concrete facts here, rather than
        # the abstract "don't blend lenders' rules" instruction alone, gives
        # the model something specific to check instead of just a general
        # warning. Kept short and scoped to multi-lender questions only —
        # the same scoping mistake from the last round (unconditional bullets
        # measurably hurting single-lender arithmetic questions) is exactly
        # what this avoids.
        known_pitfalls = """
Known cross-lender mixups worth double-checking here:
- Credit bureaus differ and scores don't transfer between lenders: Resimac and Metro use Equifax, BFS uses Experian CCR, Angle uses Veda 1:1 (Veda is Equifax's former name). A score good enough for one lender says nothing about another.
- CFAL publishes no public interest rate card at all — pricing must come from the CFAL Credit Manager. CFAL shares its DriveXpress fast-track channel and eligibility rules with Westpac, but that does NOT mean it shares Westpac's rate — never fill in a CFAL rate by copying Westpac's.
- "Exposure limit" and "loan/transaction limit" are different ceilings: a loan limit caps what a single deal can be; an exposure limit caps everything a customer owes across all contracts with that lender combined. A deal can fit under one and still fail the other.
- Documentation tier names and availability aren't standard across the panel — CFAL has no Low Doc option at all (documentation scales with transaction size instead); other lenders each use their own mix of Low/Lite/Mid/Full Doc. Don't assume a lender offers a tier just because a different one does.
"""
        checklist_block = f"""
The excerpts below cover more than one lender: {lender_checklist}. Before writing anything, go through this exact list one lender at a time and pull out the ONE specific thing the broker's question is actually asking about for each — a yes/no verdict, a rate, a fee, an age limit, whatever it is — even if a lender seems irrelevant at first glance; a lender's answer can be buried in the middle of a long, mixed set of excerpts and is easy to skip past. Only after you've done that for every lender should you write the comparison, ranking, or recommendation the broker asked for. If the question asks which is cheapest/best/highest, that answer is only as good as whether you actually pulled that same figure for every lender on the list, not just the first ones that came to mind — don't rank or recommend based on a partial scan. Skipping this check for even one lender is how the actual cheapest option, or a lender that's actually eligible, quietly gets left out.
{brevity_instruction}
{known_pitfalls}"""

    history_block = ""
    if history:
        turns = "\n\n".join(
            f"Broker: {h['question']}\nYou: {h['answer']}" for h in history[-3:]
        )
        history_block = f"""
Recent conversation so far (most recent last):
{turns}
"""

    prompt = f"""You are a friendly, experienced finance broker at LifeX Asset Finance, helping a colleague get the policy details they need quickly.

Answer using the policy excerpts below, in plain, natural language — like a broker talking to a colleague, not a compliance document. Do not cite chunk IDs, file names, or source labels in your answer; just give the information itself. (The excerpts are tagged with source info for your own reference only — leave that out of what you say back.)

Lead with the direct answer to exactly what was asked, then only the details that genuinely bear on it — a focused reply a busy colleague can absorb at a glance, not everything the excerpts contain about the lender. Leave out side-topics (fees, settlement steps, unrelated channels) unless they were asked about or directly change the answer; the broker will ask a follow-up if they want more. Exception 1: if the question needs a calculation (a rate build-up, a fee stack, an exposure check), work through the breakdown FIRST and put the final total LAST, as the one number that follows from what you just showed — do not open with a total before you've derived it, since a wrong headline followed by correct-looking working is worse than no headline. Exception 2: if the question gives close to nothing to work with — no asset type, no amount, no borrower profile, nothing that narrows down which product or rate even plausibly applies — the direct answer IS a clarifying question; a real broker can't quote from that little. Ask it the way a broker actually would (1-2 short questions, in plain conversation, not a formal list) and stop there. This is genuinely rare — most questions already give an asset, an amount, or a profile detail that's enough to answer directly (see the fuller version of this rule below); don't manufacture a reason to ask on a question that already has enough in it to work with.
{history_block}
{checklist_block}{single_lender_pitfall}{threshold_block}
If the broker's latest message is a follow-up to the conversation above (e.g. "make it shorter", "what about for a used vehicle instead?", "and eligibility?"), use that conversation only to understand what they're asking — never as a source of facts by itself. Three cases:
- Pure reformatting ("make it shorter", "say that again more simply"): reuse what you already said, no new facts needed.
- Asking for more detail/elaboration ("give me more detail", "can you elaborate", "go deeper", "tell me more"): this means your previous answer was too thin, not that it was wrong — go back into the SAME policy excerpts and pull out specifics you left out last time (secondary numbers, extra conditions, exceptions, caveats), so the new answer is genuinely fuller, not a reworded restatement of the same facts. Do not answer a detail request with clarifying questions — even if your previous answer asked some, the broker asked for detail instead of answering them, so cover the relevant scenarios briefly rather than asking which applies. If the excerpts don't actually contain anything beyond what you already said, say so plainly rather than padding the answer with reworded filler.
- Anything else — including switching to a different lender, product, or asset ("can Westpac do it?", "what about for a truck instead?"): treat it as a new question and ground every fact and figure ONLY in the policy excerpts below for what's being asked now. Do not carry over a specific number, threshold, or detail from your previous answer unless it's also directly supported by the current excerpts — even if the topic sounds similar, a different lender can have a completely different figure. If the current excerpts don't cover it, say so (or give a clearly-flagged estimate) rather than reuse a figure from earlier in the conversation.

When the broker's OWN question is missing a detail that changes the answer (as opposed to the excerpts lacking the figure entirely — see below), the test is whether the question ALREADY gives you enough to reach for a specific, defensible answer, not whether more detail could theoretically sharpen it further — almost any question could be refined further, and that alone is never a reason to ask instead of answering:
- The question already specifies enough to identify a clear scenario (an asset category, an amount, new/used, dealer/private, the borrower profile) even if a few peripheral details are still open: answer it directly the way the excerpts cover that scenario, naming any one remaining assumption in a short clause if it matters. This is the common case — most questions that give a real amount, asset type, and borrower profile belong here, including panel-wide "which is cheapest" questions once those basics are given. Do NOT invent a further split (e.g. a vehicle-weight threshold, a sub-category the question never raised) as a reason to ask instead of answering — if the excerpts let you answer the scenario as described, answer it.
- The question gives close to nothing to work with — no asset type, no amount, no profile, nothing that narrows which lender's product or which rate band even plausibly applies (e.g. "what's the best rate you've got" with no asset named at all): here, and only here, ask 1-2 short questions to get the minimum needed to answer at all, the way a broker actually would, and stop — no hedged wall of options standing in for the question you should have just asked.
- If the excerpts genuinely don't have the figure at all — not a broker-question ambiguity, the data just isn't in what you were given — say so plainly rather than inventing one.

Keep the tone warm and conversational, but stay grounded in the source material — never invent a specific number that isn't either directly in the excerpts or a reasonable, clearly-flagged estimate from them.

Before answering, double-check these common mistakes:
- Distinct numeric concepts that live in the same excerpt are not interchangeable — e.g. a limit on a single transaction is a different thing from a total/aggregate exposure limit "across all contracts", even when both appear in the same table or chunk. Match the number to what's actually being asked (a single deal vs. a customer's overall position), not just to whichever figure is nearby.
- For yes/no eligibility questions, re-read the actual condition in the excerpt against the broker's specific scenario before answering — don't assume a match just because similar wording appears in both the question and the policy text. Check whether the customer's situation satisfies the condition or violates it; those are opposites, and sharing the same words (e.g. "no payment arrangement") doesn't mean they agree.
- If an excerpt lists more than one condition that can each independently trigger their own charge, loading, or requirement (e.g. an age-at-start-of-term loading and a separate age-at-end-of-term loading), check the scenario against every one of them individually — they can all apply at once and stack. Don't stop as soon as you find one that matches.
- When a question needs a calculation (a rate build-up, a fee stack, an exposure check), work it out step by step first, and only state a headline total once you've actually derived it from that working — never open with a number and figure out the breakdown afterward. If you show a breakdown, the headline number MUST equal what that breakdown adds up to; a headline that doesn't match your own shown math is worse than no headline at all.
- Don't assume a lender covers an asset just because a broader, superficially-similar category exists in their excerpts — if the specific asset the broker asked about is never actually named anywhere in that lender's excerpts (not even as an example within a category), say that isn't clearly supported rather than inferring it fits. This cuts both ways: an asset explicitly listed within a category (even briefly, e.g. "generators and compressors" under Secondary assets) is covered; an asset that only appears as something a specific program excludes, with no other mention, is not thereby confirmed eligible elsewhere.
- If a lender's own excerpt says non-listed assets must be checked against an external tool or system not included in what you have (e.g. Angle's note to "visit the Angle asset search engine on MyHub" for non-accepted assets), and the specific asset the broker asked about isn't otherwise named anywhere in that lender's excerpts, don't guess yes or no — say plainly that it isn't confirmable from these excerpts and that the broker should check that external system directly. A confident-sounding guess is worse than admitting the limit of what's here, especially when the lender's own policy already points to exactly where to check instead.
{'''- Not every exclusion is negotiable. A HARD exclusion (the asset type or borrower type this lender simply doesn't finance at all, e.g. "motor vehicles only" ruling out a truck or piece of equipment) cannot be satisfied by a bigger deposit, a higher tier, or extra documentation — it rules the lender out completely, full stop. That's different from a SOFT condition (a deposit requirement, a tier threshold, a doc-type minimum) which the customer can actually meet. Don't write a hard exclusion up as if it were just another condition to satisfy.
- A rule, threshold, number, OR category-membership claim that belongs to ONE lender's excerpt must never be applied to a different lender unless that same thing is also explicitly stated in THAT lender's own excerpt. This includes phrases like "X is a Primary/Secondary asset" — if lender A's excerpt says an asset type is fundable under a category and lender B's excerpt never says that, don't write B's line as if B's excerpt said it too, even if B has a similarly-named category. Re-check which excerpt a specific claim actually came from before writing it next to a different lender's name — this applies to descriptive facts just as much as it applies to numbers.
- If the broker is asking which lender(s) can do something (e.g. "which lenders can finance X?"), the excerpts below may cover several different lenders at once. Work through every lender that appears in the excerpts one at a time and give each one its own clear yes/no/condition, rather than mentioning only the first few that come to mind or summarizing the rest away — a lender is easy to accidentally skip when it's a small part of a long, mixed set of excerpts, but omitting one that's actually eligible is as wrong as saying an ineligible one qualifies. Keep each one's mention brief — a short clause or line with the verdict and the key number, not a full paragraph of eligibility criteria per lender.
- If the broker asks you to compare one specific named attribute between lenders (e.g. "compare the max asset age for a primary asset"), and the same excerpt that answers that also lists the equivalent figure for other closely-related categories (e.g. secondary/tertiary assets, when only primary was asked about), check those other figures too before concluding the lenders "match" — two lenders agreeing on the one attribute asked about doesn't mean they agree everywhere, and a one-line note on a real divergence you already have in front of you is worth including.
''' if ENUMERATION_GUARDRAILS and lender_checklist else ''}
Policy excerpts:
{context}

Broker's question: {question}{f'''
(In the context of the conversation, this means: "{retrieval_question}" — the excerpts above were retrieved for that.)''' if retrieval_question != question else ''}

Answer:"""
    # A genuine "more detail" request is explicitly asked (in the prompt
    # above) to expand on every lender with specifics left out the first time
    # — that answer is legitimately longer than a normal one, so it gets a
    # higher output cap. The normal cap is a safety ceiling, not the length
    # control (the brevity instructions are) — sized so a condition-heavy
    # 7-lender answer can't get cut off mid-sentence.
    max_response_tokens = 2000 if more_detail_requested else 1000

    # Scoped-lender questions keep the higher "low" effort (a deterministic
    # signal already computed above). For the no-lender fan-out case, a
    # blanket "minimal" turned out to be too low specifically for ranking
    # questions ("which lender is cheapest") — see _classify_fanout_effort's
    # docstring for the confirmed bug and A/B test. Rather than reintroduce
    # "low" for every fan-out question (the 20-56s latency blowout
    # FANOUT_REASONING_EFFORT was built to avoid), a small classifier call
    # decides per-question whether this specific fan-out needs the deeper
    # effort or can stay cheap — same pattern as _resolve_followup just
    # above, chosen for the same reason: understanding intent isn't
    # something a keyword list does reliably.
    effort = REASONING_EFFORT if lenders else _classify_fanout_effort(retrieval_question)
    answer = _chat_completion(LLM_MODEL, prompt, max_output_tokens=max_response_tokens,
                              reasoning_effort=effort)
    log(f"\nAnswer:\n{answer}")

    return answer, nodes


if __name__ == "__main__":
    print("LifeX Policy Assistant - type 'quit' to exit\n")
    while True:
        question = input("Your question: ")
        if question.lower() == "quit":
            break
        if question.strip():
            query_policies(question)
            print()
