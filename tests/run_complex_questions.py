"""
Runs the 111-question complex/stress-test bank (ComplexQuestions.xlsx) against
the live backend, saves raw results to tests/complex_results.json, and writes
a plain-text transcript of every question/reference/model-answer to
ComplexQuestions_Answers.txt in the project root.

Usage:
    1. Start the backend: uvicorn src.api:app --port 8000
    2. python tests/run_complex_questions.py

No auto-scoring here (see test_queries.py for why) — that's a separate step,
grade_complex_questions.py.
"""
import json
import os
import sys
import urllib.request

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl
from src.config import COMPLEX_QUESTION_BANK_PATH, PROJECT_ROOT

API_URL = "http://127.0.0.1:8000/query"
RESULTS_PATH = str(PROJECT_ROOT / "tests" / "complex_results.json")
ANSWERS_TXT_PATH = str(PROJECT_ROOT / "ComplexQuestions_Answers.txt")


def load_questions():
    wb = openpyxl.load_workbook(COMPLEX_QUESTION_BANK_PATH, data_only=True)
    ws = wb["ComplexQuestions"]
    questions = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[4]:
            questions.append({
                "id": row[0], "complexity_type": row[1], "lenders_involved": row[2],
                "category": row[3], "question": row[4], "reference_answer": row[5],
                "source_chunk_ids": row[6], "failure_mode": row[7],
            })
    return questions


def run_one(question_text: str):
    body = json.dumps({"question": question_text}).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    # Complex multi-hop questions retrieve more chunks and reason more —
    # give them more headroom than the 41-question bank's default.
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def write_answers_txt(results, answers_txt_path=None):
    with open(answers_txt_path or ANSWERS_TXT_PATH, "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"{'=' * 90}\n")
            f.write(f"{r['id']} | {r['complexity_type']} | {r['category']} | Lenders: {r['lenders_involved']}\n")
            f.write(f"{'=' * 90}\n\n")
            f.write(f"QUESTION:\n{r['question']}\n\n")
            f.write(f"MODEL ANSWER:\n{r['model_answer']}\n\n")
            f.write(f"REFERENCE ANSWER:\n{r['reference_answer']}\n\n")
            f.write(f"FAILURE MODE TO WATCH FOR:\n{r['failure_mode']}\n\n")
            f.write(f"Sources used: {', '.join(r['sources']) or 'none'}\n")
            f.write(f"Response time: {r['response_time']:.1f}s\n\n")


def run_all(questions=None, results_path=None, answers_txt_path=None):
    questions = questions or load_questions()
    results_path = results_path or RESULTS_PATH
    answers_txt_path = answers_txt_path or ANSWERS_TXT_PATH
    print(f"Loaded {len(questions)} questions from {COMPLEX_QUESTION_BANK_PATH}", flush=True)

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
            result = {**q, "model_answer": f"ERROR: {e}", "sources": [],
                     "response_time": 0, "from_cache": False}

        results.append(result)
        status = "CACHED" if result.get("from_cache") else f"{result['response_time']:.1f}s"
        print(f"[{i+1}/{len(questions)}] {q['id']} ({q['complexity_type']}) done ({status})", flush=True)

        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    write_answers_txt(results, answers_txt_path)
    print(f"\nAll done. Raw results: {results_path}")
    print(f"Answers transcript: {answers_txt_path}")
    return results


if __name__ == "__main__":
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3)
    except Exception:
        print("Backend isn't responding at http://127.0.0.1:8000 — start it first:")
        print("  uvicorn src.api:app --port 8000")
        sys.exit(1)

    run_all()
