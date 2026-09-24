"""
Comprehensive scenario suite -- broader than run_quick_regression.py's
14-question smoke test, and covers ground the existing runners don't touch
at all: multi-turn follow-ups, chat corrections, the query cache, and the
answer library. Scenario data lives in tests/eval_scenarios.py; this file is
just the runner.

Five sections, run in order:
    1. Standalone accuracy  (~40 questions from ComplexQuestions.xlsx)
    2. Follow-up resolution (multi-turn, lender-switching conversations)
    3. Correction flow      (chat correction -> saved -> served back)
    4. Query cache          (paraphrase hit / near-miss reject)
    5. Answer library       (paraphrase hit / near-miss reject)

Sections 1-2 are structural/no-auto-score for content (same reasoning as
test_queries.py: don't heuristically grade answer quality). Sections 3-5 ARE
auto-checked, but only on mechanical facts a script can check honestly --
was the exact previously-served text reproduced verbatim (a real cache/
library hit always serves its saved answer unchanged, so exact-string
comparison is a legitimate check here, not a content-quality judgement.

IMPORTANT -- data safety: sections 1-5 all call /query, and /query appends
every fresh answer to data/query_cache.json whenever QUERY_CACHE_ENABLED is
on; sections 3 and 5 also write to data/answer_library.json. This runner
backs up both files before anything runs and restores them in a `finally`
block once everything is done (or if anything raises), so re-running this
suite never leaves test-only cache/correction/library entries sitting in
production data. Do not remove that backup/restore without replacing it
with something equally unconditional.

Usage:
    1. Start the backend: uvicorn src.api:app --port 8000
    2. python tests/run_full_eval.py                  # everything
    3. python tests/run_full_eval.py --standalone-only # section 1 only
    4. python tests/run_full_eval.py --scenarios-only  # sections 2-5 only
    5. python tests/run_full_eval.py --no-restore      # leave test entries in
       data/query_cache.json / data/answer_library.json instead of restoring
       the pre-run snapshot -- only for debugging this runner itself.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import PROJECT_ROOT, ANSWER_LIBRARY_PATH, QUERY_CACHE_PATH
from tests.run_complex_questions import load_questions
from tests.eval_scenarios import (
    STANDALONE_IDS,
    FOLLOWUP_SCENARIOS,
    CORRECTION_SCENARIOS,
    CACHE_SCENARIOS,
    LIBRARY_SCENARIOS,
)

API_BASE = "http://127.0.0.1:8000"
RESULTS_PATH = str(PROJECT_ROOT / "tests" / "full_eval_results.json")
ANSWERS_TXT_PATH = str(PROJECT_ROOT / "FullEval_Answers.txt")


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _post(path: str, body: dict, timeout: int = 90) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        API_BASE + path, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ask(question: str, history: list = None) -> dict:
    return _post("/query", {"question": question, "history": history or []})


# ---------------------------------------------------------------------------
# Data-file backup/restore -- see module docstring. Atomic writes (temp file
# + os.replace) so a concurrent reader (the live backend, reading these
# files fresh on every request) never sees a half-written file mid-restore.
# ---------------------------------------------------------------------------

def _snapshot(path: str):
    return Path(path).read_text(encoding="utf-8") if os.path.exists(path) else None


def _restore(path: str, snapshot):
    if snapshot is not None:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(snapshot)
        os.replace(tmp, path)
    elif os.path.exists(path):
        # The file didn't exist before this run created it -- full restore
        # means it goes back to not existing, not to an empty file.
        os.remove(path)


# ---------------------------------------------------------------------------
# 1. Standalone accuracy
# ---------------------------------------------------------------------------

def run_standalone(ids=None):
    all_q = load_questions()
    by_id = {q["id"]: q for q in all_q}
    ids = ids or STANDALONE_IDS
    missing = [i for i in ids if i not in by_id]
    if missing:
        print(f"Unknown question ID(s) in STANDALONE_IDS: {', '.join(missing)}")
        sys.exit(1)
    selected = [by_id[i] for i in ids]

    print(f"\n=== Standalone accuracy: {len(selected)} questions ===")
    results = []
    for i, q in enumerate(selected):
        try:
            data = _ask(q["question"])
            result = {
                **q,
                "model_answer": data["answer"],
                "sources": [s["chunk_id"] for s in data["sources"]],
                "response_time": data["response_time"],
                "from_cache": data["from_cache"],
                "answer_source": data.get("answer_source", "generated"),
            }
        except Exception as e:
            result = {**q, "model_answer": f"ERROR: {e}", "sources": [], "response_time": 0,
                      "from_cache": False, "answer_source": "error"}
        results.append(result)
        status = result["answer_source"] if result["from_cache"] else f"{result['response_time']:.1f}s"
        print(f"  [{i + 1}/{len(selected)}] {q['id']} ({q['complexity_type']}) done ({status})", flush=True)
    return results


# ---------------------------------------------------------------------------
# 2. Follow-up resolution
# ---------------------------------------------------------------------------

def run_followups():
    print(f"\n=== Follow-up resolution: {len(FOLLOWUP_SCENARIOS)} conversations ===")
    results = []
    for sc in FOLLOWUP_SCENARIOS:
        try:
            turn1 = _ask(sc["turn1_question"])
            history = [{"question": sc["turn1_question"], "answer": turn1["answer"]}]
            turn2 = _ask(sc["turn2_question"], history=history)
            sources2 = [s["chunk_id"] for s in turn2["sources"]]
            passed = any(cid.lower().startswith(sc["expected_prefix"]) for cid in sources2)
            results.append({**sc, "turn1_answer": turn1["answer"], "turn2_answer": turn2["answer"],
                             "turn2_sources": sources2, "passed": passed})
            print(f"  {sc['id']}: {'PASS' if passed else 'FAIL'} "
                  f"(expected a '{sc['expected_prefix']}' source in turn 2)")
        except Exception as e:
            results.append({**sc, "error": str(e), "passed": False})
            print(f"  {sc['id']}: ERROR ({e})")
    return results


# ---------------------------------------------------------------------------
# 3. Correction flow
# ---------------------------------------------------------------------------

def run_corrections():
    print(f"\n=== Correction flow: {len(CORRECTION_SCENARIOS)} scenarios ===")
    results = []
    for sc in CORRECTION_SCENARIOS:
        try:
            turn1 = _ask(sc["seed_question"])
            history = [{"question": sc["seed_question"], "answer": turn1["answer"]}]
            turn2 = _ask(sc["correction_message"], history=history)
            saved_ok = turn2.get("answer_source") == "correction_saved"

            # Read back the exact entry just saved, rather than guessing the
            # LLM's rewritten phrasing -- a library hit serves this verbatim,
            # so it's the real ground truth for the checks below.
            entries = json.loads(Path(ANSWER_LIBRARY_PATH).read_text(encoding="utf-8")) if os.path.exists(ANSWER_LIBRARY_PATH) else []
            saved_answer = entries[-1]["answer"] if entries else None

            paraphrase = _ask(sc["paraphrase_question"])
            paraphrase_hit = (
                paraphrase.get("answer_source") == "library"
                and saved_answer is not None
                and paraphrase["answer"] == saved_answer
            )

            near_miss = _ask(sc["near_miss_question"])
            near_miss_clean = saved_answer is None or near_miss["answer"] != saved_answer

            passed = saved_ok and paraphrase_hit and near_miss_clean
            results.append({
                **sc, "turn1_answer": turn1["answer"], "correction_ack": turn2["answer"],
                "saved_answer": saved_answer, "paraphrase_answer": paraphrase["answer"],
                "near_miss_answer": near_miss["answer"], "saved_ok": saved_ok,
                "paraphrase_hit": paraphrase_hit, "near_miss_clean": near_miss_clean, "passed": passed,
            })
            print(f"  {sc['id']}: {'PASS' if passed else 'FAIL'} "
                  f"(saved={saved_ok}, paraphrase_hit={paraphrase_hit}, near_miss_clean={near_miss_clean})")
        except Exception as e:
            results.append({**sc, "error": str(e), "passed": False})
            print(f"  {sc['id']}: ERROR ({e})")
    return results


# ---------------------------------------------------------------------------
# 4. Query cache
# ---------------------------------------------------------------------------

def run_cache_scenarios():
    print(f"\n=== Query cache: {len(CACHE_SCENARIOS)} scenarios ===")
    results = []
    for sc in CACHE_SCENARIOS:
        try:
            seed = _ask(sc["seed_question"])
            paraphrase = _ask(sc["paraphrase_question"])
            paraphrase_hit = (
                paraphrase.get("from_cache") is True
                and paraphrase.get("answer_source") == "cache"
                and paraphrase["answer"] == seed["answer"]
            )
            near_miss = _ask(sc["near_miss_question"])
            near_miss_clean = near_miss["answer"] != seed["answer"]
            passed = paraphrase_hit and near_miss_clean
            results.append({
                **sc, "seed_answer": seed["answer"], "paraphrase_answer": paraphrase["answer"],
                "near_miss_answer": near_miss["answer"], "paraphrase_hit": paraphrase_hit,
                "near_miss_clean": near_miss_clean, "passed": passed,
            })
            print(f"  {sc['id']}: {'PASS' if passed else 'FAIL'} "
                  f"(paraphrase_hit={paraphrase_hit}, near_miss_clean={near_miss_clean})")
        except Exception as e:
            results.append({**sc, "error": str(e), "passed": False})
            print(f"  {sc['id']}: ERROR ({e})")
    return results


# ---------------------------------------------------------------------------
# 5. Answer library
# ---------------------------------------------------------------------------

def run_library_scenarios():
    print(f"\n=== Answer library: {len(LIBRARY_SCENARIOS)} scenarios ===")
    results = []
    for sc in LIBRARY_SCENARIOS:
        try:
            _post("/answer-library/save", {
                "question": sc["seed_question"], "answer": sc["seed_answer"],
                "chunk_ids": sc.get("seed_chunk_ids", []),
            })
            paraphrase = _ask(sc["paraphrase_question"])
            paraphrase_hit = (
                paraphrase.get("answer_source") == "library"
                and paraphrase["answer"] == sc["seed_answer"]
            )
            near_miss = _ask(sc["near_miss_question"])
            near_miss_clean = near_miss["answer"] != sc["seed_answer"]
            passed = paraphrase_hit and near_miss_clean
            results.append({
                **sc, "paraphrase_answer": paraphrase["answer"], "near_miss_answer": near_miss["answer"],
                "paraphrase_hit": paraphrase_hit, "near_miss_clean": near_miss_clean, "passed": passed,
            })
            print(f"  {sc['id']}: {'PASS' if passed else 'FAIL'} "
                  f"(paraphrase_hit={paraphrase_hit}, near_miss_clean={near_miss_clean})")
        except Exception as e:
            results.append({**sc, "error": str(e), "passed": False})
            print(f"  {sc['id']}: ERROR ({e})")
    return results


# ---------------------------------------------------------------------------
# Transcript + summary
# ---------------------------------------------------------------------------

def write_transcript(all_results: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        if "standalone" in all_results:
            f.write("#" * 90 + "\n# STANDALONE ACCURACY -- grade manually against reference_answer\n" + "#" * 90 + "\n\n")
            for r in all_results["standalone"]:
                f.write(f"{'=' * 90}\n")
                f.write(f"{r['id']} | {r['complexity_type']} | {r['category']} | Lenders: {r['lenders_involved']}\n")
                f.write(f"{'=' * 90}\n\n")
                f.write(f"QUESTION:\n{r['question']}\n\n")
                f.write(f"MODEL ANSWER:\n{r['model_answer']}\n\n")
                f.write(f"REFERENCE ANSWER:\n{r['reference_answer']}\n\n")
                f.write(f"FAILURE MODE TO WATCH FOR:\n{r['failure_mode']}\n\n")
                f.write(f"Sources used: {', '.join(r['sources']) or 'none'}\n")
                f.write(f"Response time: {r['response_time']:.1f}s | answer_source: {r.get('answer_source')}\n\n")

        if "followups" in all_results:
            f.write("#" * 90 + "\n# FOLLOW-UP RESOLUTION\n" + "#" * 90 + "\n\n")
            for r in all_results["followups"]:
                f.write(f"{'=' * 90}\n{r['id']}: {'PASS' if r.get('passed') else 'FAIL'}\n{'=' * 90}\n\n")
                f.write(f"TURN 1: {r['turn1_question']}\n-> {r.get('turn1_answer', r.get('error', ''))}\n\n")
                f.write(f"TURN 2 (follow-up): {r['turn2_question']}\n-> {r.get('turn2_answer', '')}\n\n")
                f.write(f"Turn 2 sources: {', '.join(r.get('turn2_sources', []))}\n")
                f.write(f"Expected a source starting with '{r['expected_prefix']}': "
                        f"{'found' if r.get('passed') else 'NOT found'}\n\n")

        if "corrections" in all_results:
            f.write("#" * 90 + "\n# CORRECTION FLOW\n" + "#" * 90 + "\n\n")
            for r in all_results["corrections"]:
                f.write(f"{'=' * 90}\n{r['id']}: {'PASS' if r.get('passed') else 'FAIL'}\n{'=' * 90}\n\n")
                f.write(f"SEED QUESTION: {r['seed_question']}\n-> {r.get('turn1_answer', '')}\n\n")
                f.write(f"CORRECTION MESSAGE: {r['correction_message']}\n-> {r.get('correction_ack', '')}\n\n")
                f.write(f"SAVED ANSWER (what the library now has): {r.get('saved_answer')}\n\n")
                f.write(f"PARAPHRASE: {r['paraphrase_question']}\n-> {r.get('paraphrase_answer', '')}\n")
                f.write(f"  library hit (exact match to saved answer): {r.get('paraphrase_hit')}\n\n")
                f.write(f"NEAR-MISS: {r['near_miss_question']}\n-> {r.get('near_miss_answer', '')}\n")
                f.write(f"  correctly NOT served the correction's answer: {r.get('near_miss_clean')}\n\n")

        if "cache" in all_results:
            f.write("#" * 90 + "\n# QUERY CACHE\n" + "#" * 90 + "\n\n")
            for r in all_results["cache"]:
                f.write(f"{'=' * 90}\n{r['id']}: {'PASS' if r.get('passed') else 'FAIL'}\n{'=' * 90}\n\n")
                f.write(f"SEED: {r['seed_question']}\n-> {r.get('seed_answer', '')}\n\n")
                f.write(f"PARAPHRASE: {r['paraphrase_question']}\n-> {r.get('paraphrase_answer', '')}\n")
                f.write(f"  cache hit (exact match to seed answer): {r.get('paraphrase_hit')}\n\n")
                f.write(f"NEAR-MISS: {r['near_miss_question']}\n-> {r.get('near_miss_answer', '')}\n")
                f.write(f"  correctly NOT served the seed's cached answer: {r.get('near_miss_clean')}\n\n")

        if "library" in all_results:
            f.write("#" * 90 + "\n# ANSWER LIBRARY\n" + "#" * 90 + "\n\n")
            for r in all_results["library"]:
                f.write(f"{'=' * 90}\n{r['id']}: {'PASS' if r.get('passed') else 'FAIL'}\n{'=' * 90}\n\n")
                f.write(f"SEEDED DIRECTLY: {r['seed_question']}\n-> {r['seed_answer']}\n\n")
                f.write(f"PARAPHRASE: {r['paraphrase_question']}\n-> {r.get('paraphrase_answer', '')}\n")
                f.write(f"  library hit (exact match to seeded answer): {r.get('paraphrase_hit')}\n\n")
                f.write(f"NEAR-MISS: {r['near_miss_question']}\n-> {r.get('near_miss_answer', '')}\n")
                f.write(f"  correctly NOT served the seeded answer: {r.get('near_miss_clean')}\n\n")


def print_summary(all_results: dict):
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    if "standalone" in all_results:
        n = len(all_results["standalone"])
        errors = sum(1 for r in all_results["standalone"] if r["answer_source"] == "error")
        print(f"Standalone: {n} questions run ({errors} errored) -- grade manually against "
              f"reference_answer (see {ANSWERS_TXT_PATH}), or hand {RESULTS_PATH} to an LLM judge.")
    for key in ("followups", "corrections", "cache", "library"):
        if key in all_results:
            items = all_results[key]
            passed = sum(1 for r in items if r.get("passed"))
            print(f"{key.capitalize()}: {passed}/{len(items)} passed")
    print(f"\nRaw results: {RESULTS_PATH}")
    print(f"Transcript: {ANSWERS_TXT_PATH}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--standalone-only", action="store_true", help="Run only section 1 (standalone accuracy)")
    parser.add_argument("--scenarios-only", action="store_true", help="Skip section 1, run only sections 2-5")
    parser.add_argument("--no-restore", action="store_true",
                         help="Leave query_cache.json/answer_library.json as the eval left them, instead of "
                              "restoring the pre-run snapshot. Off by default -- see module docstring.")
    args = parser.parse_args()

    try:
        urllib.request.urlopen(f"{API_BASE}/health", timeout=3)
    except Exception:
        print(f"Backend isn't responding at {API_BASE} -- start it first:")
        print("  uvicorn src.api:app --port 8000")
        sys.exit(1)

    cache_snapshot = _snapshot(QUERY_CACHE_PATH)
    library_snapshot = _snapshot(ANSWER_LIBRARY_PATH)

    all_results = {}
    try:
        if not args.scenarios_only:
            all_results["standalone"] = run_standalone()
        if not args.standalone_only:
            all_results["followups"] = run_followups()
            all_results["corrections"] = run_corrections()
            all_results["cache"] = run_cache_scenarios()
            all_results["library"] = run_library_scenarios()
    finally:
        if not args.no_restore:
            _restore(QUERY_CACHE_PATH, cache_snapshot)
            _restore(ANSWER_LIBRARY_PATH, library_snapshot)
            print("\nRestored query_cache.json and answer_library.json to their pre-run state "
                  "(this eval's cache/correction/library entries are test-only, not meant to persist).")

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    write_transcript(all_results, ANSWERS_TXT_PATH)
    print_summary(all_results)


if __name__ == "__main__":
    main()
