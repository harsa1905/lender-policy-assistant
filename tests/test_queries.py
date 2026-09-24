"""
Runs the scenario question bank (policy_question_bank.xlsx, 41 questions
across 6 lenders) against the live backend and saves the raw results for
manual grading.

Usage:
    1. Start the backend: uvicorn src.api:app --port 8000
    2. python tests/test_queries.py

There's no auto-scoring here on purpose. An earlier version of this script
scored answers by keyword/number overlap against a gold answer, which is
exactly the kind of heuristic that gave false confidence during this
project (e.g. scoring a wrong lender's answer as correct because it happened
to share enough words with the reference). The current question bank also
has no exact chunk_id column to check retrieval against directly. Read the
reference_answer against model_answer yourself, or hand the output file to
an LLM to grade — don't trust a keyword-match score to replace that.
"""
import json
import os
import sys
import time
import urllib.request

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl
from src.config import SCENARIO_QUESTION_BANK_PATH, PROJECT_ROOT

API_URL = "http://127.0.0.1:8000/query"
RESULTS_PATH = str(PROJECT_ROOT / "tests" / "last_run_results.json")


def load_questions():
    wb = openpyxl.load_workbook(SCENARIO_QUESTION_BANK_PATH)
    ws = wb["Question Bank"]
    questions = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[3]:
            questions.append({
                "id": row[0], "lender": row[1], "category": row[2],
                "question": row[3], "reference_answer": row[4], "source_ref": row[5],
            })
    return questions


def run_one(question_text: str):
    body = json.dumps({"question": question_text}).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_all(questions=None):
    questions = questions or load_questions()
    print(f"Loaded {len(questions)} questions from {SCENARIO_QUESTION_BANK_PATH}", flush=True)

    results = []
    for i, q in enumerate(questions):
        try:
            data = run_one(q["question"])
            result = {
                **q,
                "model_answer": data["answer"],
                "sources": [s["chunk_id"] for s in data["sources"]],
                "response_time": data["response_time"],
                "from_cache": data["from_cache"],
            }
        except Exception as e:
            result = {**q, "model_answer": f"ERROR: {e}", "sources": [], "response_time": 0, "from_cache": False}

        results.append(result)
        status = "CACHED" if result.get("from_cache") else f"{result['response_time']:.1f}s"
        print(f"[{i+1}/{len(questions)}] {q['id']} done ({status})", flush=True)

        with open(RESULTS_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    print(f"\nAll done. Results saved to {RESULTS_PATH}")
    print("Grade each answer against its reference_answer yourself — no auto-score is produced.")
    return results


if __name__ == "__main__":
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3)
    except Exception:
        print("Backend isn't responding at http://127.0.0.1:8000 — start it first:")
        print("  uvicorn src.api:app --port 8000")
        sys.exit(1)

    run_all()
