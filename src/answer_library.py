"""Persisted store of human-reviewed/corrected answers, served back at
query time and kept in sync with the chunks they were based on.

The frontend's Review tab already lets a reviewer edit an AI-generated
answer before approving it -- that's the "correct the chatbot" step. What
was missing: approved answers were only ever written to
answer_library.json, never read back, so a correction only ever benefited
whoever happened to still have it in their browser's session state. And
nothing tracked whether the chunk an approved answer was based on later
changed underneath it (a rate update, a threshold correction) -- a stale
correction would otherwise keep being served with no signal to anyone.

This module is the fix: save_entry() snapshots the exact chunk content an
answer depended on at approval time; find_best_match() serves matching
entries back at query time; and refresh_stale_entries() re-checks snapshots
against current chunk content whenever chunks change, using a narrow LLM
call (src.query.refresh_answer_with_new_chunk) to update just the outdated
numbers rather than silently keep serving something that no longer holds.

find_best_match()'s matching is two-stage, same as the query cache in
src/api.py (see QUERY_CACHE_PREFILTER_THRESHOLD's comment in config.py for
the calibration data behind this): embedding similarity alone doesn't
reliably separate genuine paraphrases from same-wording-different-detail
questions in this domain ("BFS Tier 2" vs "BFS Tier 3" scored higher than
several genuine paraphrase pairs), so it's used only as a cheap pre-filter.
The actual yes/no gate is src.query.questions_require_same_answer(), a
direct LLM comparison -- a wrongly-matched *human correction* would be just
as bad a failure as a wrongly-matched raw cache hit, so this gets the same
scrutiny even though every entry here already cleared a human review step.
"""
import json
import math
import os
import threading

from llama_index.core import Settings

from src.config import ANSWER_LIBRARY_PATH, ANSWER_LIBRARY_PREFILTER_THRESHOLD, ANSWER_LIBRARY_MAX_CANDIDATES
from src.ingest import get_all_chunk_blocks

_lock = threading.Lock()


def _embed(text: str):
    return Settings.embed_model.get_query_embedding(text)


def _cosine_similarity(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def load_entries() -> list:
    if os.path.exists(ANSWER_LIBRARY_PATH):
        with open(ANSWER_LIBRARY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_entries(entries: list):
    os.makedirs(os.path.dirname(ANSWER_LIBRARY_PATH), exist_ok=True)
    # Atomic replace, not an in-place truncate -- a concurrent reader (a
    # find_best_match call from another request) should never see a
    # half-written file. Same pattern as the query cache in src/api.py.
    tmp_path = ANSWER_LIBRARY_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    os.replace(tmp_path, ANSWER_LIBRARY_PATH)


def find_best_match(question: str):
    """Best-matching library entry for this question, or None if nothing
    clears the two-stage gate (see module docstring). Entries flagged
    "needs_review" are never served automatically -- a correction already
    known to be possibly-stale is worse to hand back silently than just
    answering fresh from the live chunks."""
    # Imported here, not at module top -- same reasoning as the deferred
    # import in refresh_stale_entries() below: avoid paying src.query's
    # import-time OpenAI client/embedding/Chroma init cost for callers that
    # only need save_entry().
    from src.query import questions_require_same_answer

    q_embedding = _embed(question)
    scored = []
    for entry in load_entries():
        if entry.get("status") == "needs_review":
            continue
        embedding = entry.get("question_embedding")
        if not embedding:
            continue  # entries saved before this field existed
        score = _cosine_similarity(q_embedding, embedding)
        if score >= ANSWER_LIBRARY_PREFILTER_THRESHOLD:
            scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)

    for _, entry in scored[:ANSWER_LIBRARY_MAX_CANDIDATES]:
        if questions_require_same_answer(question, entry["question"]):
            return entry
    return None


def save_entry(question: str, answer: str, chunk_ids: list) -> dict:
    """Save a (possibly human-corrected) answer. Snapshots the exact current
    content of every chunk_id it depends on -- that snapshot is the baseline
    refresh_stale_entries() compares against later to detect drift.

    Any existing entry the matching gate considers the SAME question is
    removed first, so one question keeps exactly one entry: the newest.
    Without that, correcting the same figure twice left both corrections
    live, and find_best_match returns the highest-SIMILARITY survivor rather
    than the most recent one -- so the superseded answer could keep being
    served, and which one won was effectively arbitrary. A broker who
    corrects the same number twice has every reason to expect the second
    correction to stick; this is what makes that true. Same
    dedupe-on-write rule the query cache uses (_append_to_query_cache in
    src/api.py), applied here for the same reason.

    needs_review entries are purged alongside current ones. They're already
    never served, and a fresh human correction supersedes a stale flag --
    leaving them behind would just accumulate dead rows.
    """
    from src.query import questions_require_same_answer

    with _lock:
        entries = load_entries()
        q_embedding = _embed(question)

        survivors = []
        for existing in entries:
            embedding = existing.get("question_embedding")
            if embedding:
                score = _cosine_similarity(q_embedding, embedding)
                if score >= ANSWER_LIBRARY_PREFILTER_THRESHOLD and questions_require_same_answer(
                    question, existing.get("question", "")
                ):
                    continue  # superseded by the answer being saved now
            survivors.append(existing)

        all_blocks = get_all_chunk_blocks()
        entry = {
            # Highest existing id + 1, NOT len(entries) + 1 -- entries can
            # now be removed above, so a length-based id would collide with
            # one already in the file and break every id-based reference
            # (the refresh endpoint's results, the frontend's review list).
            "id": max((e.get("id", 0) for e in survivors), default=0) + 1,
            "question": question,
            "answer": answer,
            "chunk_ids": chunk_ids,
            "question_embedding": q_embedding,
            "chunk_snapshots": {cid: all_blocks[cid] for cid in chunk_ids if cid in all_blocks},
            "status": "current",
            "note": "",
        }
        survivors.append(entry)
        _save_entries(survivors)
        return entry


def refresh_stale_entries(changed_chunk_ids: set = None) -> list:
    """Compare every entry's chunk_snapshots against CURRENT chunk content.
    For any chunk_id whose content has actually changed, ask the narrow
    refresh check (src.query.refresh_answer_with_new_chunk) whether the
    saved answer still holds, and update it in place if so.

    changed_chunk_ids restricts which entries get examined at all (the cheap,
    precise path right after /chunks/promote, which already knows exactly
    what it just changed). Pass None to check every entry against the full
    current chunk set (the path after a manual chunk edit + re-ingest, where
    nothing recorded what changed).

    Returns the entries that were actually updated or newly flagged, so a
    caller can log or surface the ripple effect of a chunk change.
    """
    # Imported here, not at module top -- src.query does a real network
    # call at import time (constructing the OpenAI client) and initialises
    # the embedding model/Chroma connection; deferring the import means
    # importing this module for save_entry()/find_best_match() alone (e.g.
    # from a lightweight script) doesn't pay that cost unless a refresh is
    # actually requested.
    from src.query import refresh_answer_with_new_chunk

    with _lock:
        entries = load_entries()
        current_blocks = get_all_chunk_blocks()
        touched = []
        any_snapshot_changed = False

        for entry in entries:
            snapshots = entry.get("chunk_snapshots") or {}
            if not snapshots:
                continue
            if changed_chunk_ids is not None and not (set(snapshots) & changed_chunk_ids):
                continue

            diffs = {
                cid: current_blocks[cid]
                for cid in snapshots
                if current_blocks.get(cid, snapshots[cid]) != snapshots[cid]
            }
            if not diffs:
                continue

            # If several of an entry's chunks changed at once, stop at the
            # first one that actually requires an update or flag -- layering
            # multiple partial automatic rewrites on top of each other risks
            # producing a final answer nobody actually reviewed end to end.
            entry_flagged = False
            for cid, new_content in diffs.items():
                old_content = snapshots[cid]
                result = refresh_answer_with_new_chunk(
                    entry["question"], entry["answer"], old_content, new_content
                )
                if result["status"] == "unchanged":
                    entry["chunk_snapshots"][cid] = new_content
                    any_snapshot_changed = True
                    continue
                elif result["status"] == "updated":
                    entry["answer"] = result["updated_answer"]
                    entry["chunk_snapshots"][cid] = new_content
                    entry["status"] = "auto_updated"
                    entry["note"] = result["note"]
                else:  # unclear
                    entry["status"] = "needs_review"
                    entry["note"] = result["note"]
                touched.append(entry)
                entry_flagged = True
                break

            if not entry_flagged:
                any_snapshot_changed = True

        if touched or any_snapshot_changed:
            _save_entries(entries)
        return touched
