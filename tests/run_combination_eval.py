"""
Runs the combination scenarios in tests/eval_combination_scenarios.py --
multi-step conversations that test how the pipeline's mechanisms interact,
rather than each one alone (that's tests/run_full_eval.py's job).

Usage:
    1. Start the backend: uvicorn src.api:app --port 8000
    2. python tests/run_combination_eval.py
    3. python tests/run_combination_eval.py --ids COMBO-2,COMBO-6
    4. python tests/run_combination_eval.py --no-restore   # debugging only

DATA SAFETY -- read before changing anything below. These scenarios write
real corrections and cache entries, including deliberately FABRICATED policy
figures. Two layers of protection:

  * Whole-run: data/query_cache.json and data/answer_library.json are
    snapshotted before the first scenario and restored in a finally block,
    so an invented "$711 establishment fee" can never survive into the data
    a broker actually queries.
  * Per-scenario: both files are ALSO snapshotted and restored around each
    individual scenario. That makes scenarios hermetic -- one scenario's
    saved correction can't satisfy or break the next one's assertions, so a
    failure means what it says instead of being an artefact of run order.

Every assertion is mechanical (an answer_source string, a chunk_id prefix, a
verbatim comparison, an entry count). Nothing here scores answer quality --
see tests/test_queries.py's docstring for why that stays a human job.
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import PROJECT_ROOT, ANSWER_LIBRARY_PATH, QUERY_CACHE_PATH
from tests.eval_combination_scenarios import COMBINATION_SCENARIOS

API_BASE = "http://127.0.0.1:8000"
RESULTS_PATH = str(PROJECT_ROOT / "tests" / "combination_eval_results.json")
TRANSCRIPT_PATH = str(PROJECT_ROOT / "CombinationEval_Transcript.txt")


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def _post(path: str, body: dict, timeout: int = 120) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        API_BASE + path, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# Snapshot / restore (see module docstring)
# ---------------------------------------------------------------------------

def _snapshot(path: str):
    return Path(path).read_text(encoding="utf-8") if os.path.exists(path) else None


def _restore(path: str, snapshot):
    if snapshot is None:
        if os.path.exists(path):
            # Didn't exist before this run created it -- full restore means
            # back to not existing, not to an empty file.
            os.remove(path)
        return
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(snapshot)
    os.replace(tmp, path)


def _load_library() -> list:
    if os.path.exists(ANSWER_LIBRARY_PATH):
        with open(ANSWER_LIBRARY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _load_cache() -> list:
    if os.path.exists(QUERY_CACHE_PATH):
        with open(QUERY_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# ---------------------------------------------------------------------------
# Assertions -- each returns a list of human-readable failure strings
# ---------------------------------------------------------------------------

def _check(expect: dict, data: dict, named: dict, step: dict,
           library_before: int, library_after: int) -> list:
    failures = []
    chunk_ids = [s["chunk_id"] for s in data.get("sources", [])]
    answer = data.get("answer", "")

    if "answer_source" in expect:
        actual = data.get("answer_source")
        if actual != expect["answer_source"]:
            failures.append(f"answer_source: expected {expect['answer_source']!r}, got {actual!r}")

    if "from_cache" in expect and data.get("from_cache") is not expect["from_cache"]:
        failures.append(f"from_cache: expected {expect['from_cache']}, got {data.get('from_cache')}")

    if "sources_empty" in expect:
        is_empty = len(chunk_ids) == 0
        if is_empty is not expect["sources_empty"]:
            failures.append(
                f"sources_empty: expected {expect['sources_empty']}, got {is_empty} ({len(chunk_ids)} sources)"
            )

    if "source_prefix" in expect:
        pfx = expect["source_prefix"]
        if not any(c.lower().startswith(pfx) for c in chunk_ids):
            failures.append(f"source_prefix: no chunk_id starting with {pfx!r} (got {chunk_ids[:8]})")

    if "no_source_prefix" in expect:
        pfx = expect["no_source_prefix"]
        leaked = [c for c in chunk_ids if c.lower().startswith(pfx)]
        if leaked:
            failures.append(f"no_source_prefix: {pfx!r} should be absent but found {leaked[:5]}")

    if "answer_equals" in expect:
        ref = named.get(expect["answer_equals"])
        if ref is None:
            failures.append(f"answer_equals: no earlier step named {expect['answer_equals']!r}")
        elif answer != ref:
            failures.append(f"answer_equals: differs from step {expect['answer_equals']!r}")

    if "answer_not_equals" in expect:
        ref = named.get(expect["answer_not_equals"])
        if ref is None:
            failures.append(f"answer_not_equals: no earlier step named {expect['answer_not_equals']!r}")
        elif answer == ref:
            failures.append(f"answer_not_equals: identical to step {expect['answer_not_equals']!r}")

    if "answer_contains" in expect and expect["answer_contains"] not in answer:
        failures.append(f"answer_contains: {expect['answer_contains']!r} not in answer")

    if "answer_not_contains" in expect and expect["answer_not_contains"] in answer:
        failures.append(f"answer_not_contains: {expect['answer_not_contains']!r} leaked into answer")

    if "library_delta" in expect:
        actual_delta = library_after - library_before
        if actual_delta != expect["library_delta"]:
            failures.append(f"library_delta: expected {expect['library_delta']}, got {actual_delta}")

    needs_entry = any(k.startswith("library_last") for k in expect)
    if needs_entry:
        entries = _load_library()
        if not entries:
            failures.append("library_last_*: library is empty")
        else:
            last = entries[-1]
            if "library_last_question_not" in expect:
                if last.get("question", "").strip().lower() == expect["library_last_question_not"].strip().lower():
                    failures.append(
                        f"library_last_question_not: saved question is the raw "
                        f"{expect['library_last_question_not']!r} (never resolved to a standalone question)"
                    )
            if "library_last_question_matches" in expect:
                if expect["library_last_question_matches"].lower() not in last.get("question", "").lower():
                    failures.append(
                        f"library_last_question_matches: {expect['library_last_question_matches']!r} "
                        f"not in saved question {last.get('question', '')!r}"
                    )
            if "library_last_chunk_prefix" in expect:
                pfx = expect["library_last_chunk_prefix"]
                cids = last.get("chunk_ids") or []
                if not any(c.lower().startswith(pfx) for c in cids):
                    failures.append(
                        f"library_last_chunk_prefix: no saved chunk_id starting with {pfx!r} (got {cids[:8]})"
                    )

    if "cache_cluster_max" in expect:
        q = step.get("question", "").strip().lower()
        matches = [e for e in _load_cache() if e.get("question", "").strip().lower() == q]
        if len(matches) > expect["cache_cluster_max"]:
            failures.append(
                f"cache_cluster_max: {len(matches)} cache entries for this exact question, "
                f"expected at most {expect['cache_cluster_max']}"
            )

    return failures


# ---------------------------------------------------------------------------
# Scenario execution
# ---------------------------------------------------------------------------

def run_scenario(scenario: dict) -> dict:
    print(f"\n{scenario['id']}: {scenario['title']}")

    conversation = []   # [{question, answer}] -- the running chat history
    named = {}          # step "as" name -> that step's answer
    step_records = []
    scenario_failures = []

    for i, step in enumerate(scenario["steps"], start=1):
        action = step["do"]

        if action == "reset":
            conversation = []
            step_records.append({"step": i, "do": "reset"})
            continue

        if action == "clear_cache":
            # Makes a scenario's cache precondition explicit instead of
            # inheriting whatever previous runs happened to leave behind.
            # Scenarios that reason about cache state (does this hit? did
            # that get written?) are otherwise unrunnable in isolation: a
            # question cached by an earlier suite makes "expected generated,
            # got cache" look like a bug when it's just run history. Safe
            # because the runner snapshots and restores this file per
            # scenario anyway.
            tmp = QUERY_CACHE_PATH + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump([], f)
            os.replace(tmp, QUERY_CACHE_PATH)
            step_records.append({"step": i, "do": "clear_cache"})
            print(f"  [{i}] clear_cache")
            continue

        library_before = len(_load_library())

        try:
            if action == "seed_library":
                _post("/answer-library/save", {
                    "question": step["question"],
                    "answer": step["answer"],
                    "chunk_ids": step.get("chunk_ids", []),
                })
                step_records.append({
                    "step": i, "do": action, "question": step["question"],
                    "answer": step["answer"], "failures": [],
                })
                print(f"  [{i}] seed_library: {step['question'][:60]!r}")
                continue

            if action == "ask":
                conversation = []
                data = _post("/query", {"question": step["question"], "history": []})
            elif action in ("follow_up", "correct"):
                data = _post("/query", {
                    "question": step["question"],
                    "history": [{"question": h["question"], "answer": h["answer"]} for h in conversation[-3:]],
                })
            else:
                raise ValueError(f"unknown step action {action!r}")

        except Exception as e:
            msg = f"HTTP/transport error: {type(e).__name__}: {e}"
            scenario_failures.append(f"step {i} ({action}): {msg}")
            step_records.append({"step": i, "do": action, "question": step.get("question"),
                                 "error": msg, "failures": [msg]})
            print(f"  [{i}] {action}: ERROR -- {msg}")
            continue

        conversation.append({"question": step["question"], "answer": data["answer"]})
        if step.get("as"):
            named[step["as"]] = data["answer"]

        library_after = len(_load_library())
        failures = _check(step.get("expect", {}), data, named, step, library_before, library_after)
        if failures:
            scenario_failures.extend(f"step {i} ({action}): {f}" for f in failures)

        step_records.append({
            "step": i, "do": action, "question": step["question"],
            "answer": data["answer"],
            "answer_source": data.get("answer_source"),
            "from_cache": data.get("from_cache"),
            "sources": [s["chunk_id"] for s in data.get("sources", [])],
            "expect": step.get("expect", {}),
            "failures": failures,
        })

        status = "ok" if not failures else f"FAIL ({len(failures)})"
        src = data.get("answer_source", "?")
        n_src = len(data.get("sources", []))
        print(f"  [{i}] {action}: {status} [{src}, {n_src} sources] {step['question'][:55]!r}")
        for f in failures:
            print(f"        - {f}")

    passed = not scenario_failures
    print(f"  => {scenario['id']}: {'PASS' if passed else 'FAIL'}")

    return {
        "id": scenario["id"], "title": scenario["title"], "why": scenario["why"],
        "passed": passed, "failures": scenario_failures, "steps": step_records,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def write_transcript(results: list, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write("#" * 90 + "\n")
        f.write("# COMBINATION EVAL -- mechanism interactions\n")
        f.write("#" * 90 + "\n\n")
        for r in results:
            f.write("=" * 90 + "\n")
            f.write(f"{r['id']}: {r['title']}\n")
            f.write(f"RESULT: {'PASS' if r['passed'] else 'FAIL'}\n")
            f.write("=" * 90 + "\n\n")
            f.write(f"WHY THIS MATTERS:\n{r['why']}\n\n")
            for s in r["steps"]:
                if s["do"] == "reset":
                    f.write("--- [conversation reset] ---\n\n")
                    continue
                if s["do"] == "clear_cache":
                    f.write("--- [query cache cleared] ---\n\n")
                    continue
                f.write(f"[{s['step']}] {s['do'].upper()}: {s.get('question', '')}\n")
                if s.get("error"):
                    f.write(f"    ERROR: {s['error']}\n\n")
                    continue
                f.write(f"    -> {s.get('answer', '')}\n")
                if s.get("answer_source") is not None:
                    f.write(f"    answer_source: {s['answer_source']} | from_cache: {s.get('from_cache')}\n")
                    f.write(f"    sources ({len(s.get('sources', []))}): {', '.join(s.get('sources', [])[:12]) or 'none'}\n")
                if s.get("expect"):
                    f.write(f"    expected: {s['expect']}\n")
                if s.get("failures"):
                    for fail in s["failures"]:
                        f.write(f"    FAIL: {fail}\n")
                f.write("\n")
            if r["failures"]:
                f.write("ALL FAILURES:\n")
                for fail in r["failures"]:
                    f.write(f"  - {fail}\n")
            f.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ids", help="Comma-separated scenario IDs to run instead of all")
    parser.add_argument("--no-restore", action="store_true",
                        help="Leave query_cache.json/answer_library.json as the run left them. "
                             "Debugging only -- these scenarios save FABRICATED policy figures.")
    args = parser.parse_args()

    try:
        urllib.request.urlopen(f"{API_BASE}/health", timeout=5)
    except Exception:
        print(f"Backend isn't responding at {API_BASE} -- start it first:")
        print("  uvicorn src.api:app --port 8000")
        sys.exit(1)

    scenarios = COMBINATION_SCENARIOS
    if args.ids:
        wanted = [i.strip() for i in args.ids.split(",")]
        by_id = {s["id"]: s for s in COMBINATION_SCENARIOS}
        missing = [i for i in wanted if i not in by_id]
        if missing:
            print(f"Unknown scenario ID(s): {', '.join(missing)}")
            sys.exit(1)
        scenarios = [by_id[i] for i in wanted]

    print(f"Running {len(scenarios)} combination scenario(s).")

    run_cache_snapshot = _snapshot(QUERY_CACHE_PATH)
    run_library_snapshot = _snapshot(ANSWER_LIBRARY_PATH)

    results = []
    try:
        for scenario in scenarios:
            # Per-scenario isolation, so one scenario's saved corrections
            # can't satisfy or break the next one's assertions.
            sc_cache = _snapshot(QUERY_CACHE_PATH)
            sc_library = _snapshot(ANSWER_LIBRARY_PATH)
            try:
                results.append(run_scenario(scenario))
            finally:
                if not args.no_restore:
                    _restore(QUERY_CACHE_PATH, sc_cache)
                    _restore(ANSWER_LIBRARY_PATH, sc_library)
    finally:
        if not args.no_restore:
            _restore(QUERY_CACHE_PATH, run_cache_snapshot)
            _restore(ANSWER_LIBRARY_PATH, run_library_snapshot)
            print("\nRestored query_cache.json and answer_library.json to their pre-run state "
                  "(these scenarios save deliberately fabricated figures -- none of it persists).")

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    write_transcript(results, TRANSCRIPT_PATH)

    passed = sum(1 for r in results if r["passed"])
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for r in results:
        print(f"  {'PASS' if r['passed'] else 'FAIL'}  {r['id']}: {r['title']}")
        for fail in r["failures"]:
            print(f"          - {fail}")
    print(f"\n{passed}/{len(results)} scenarios passed")
    print(f"Raw results: {RESULTS_PATH}")
    print(f"Transcript: {TRANSCRIPT_PATH}")


if __name__ == "__main__":
    main()
