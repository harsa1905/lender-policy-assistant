"""
Grades tests/complex_results.json against the CMAP 2026 four-point rubric
(same rubric as GroundTruth.xlsx: 4 = completely right, 3 = correct with
minor mistakes, 2 = incorrect but contains some true information, 1 =
completely wrong), using an LLM judge given the reference answer, the
model's answer, and the documented failure mode each question is designed
to trip.

This is a judgment call worth being explicit about: an LLM grading another
LLM's answers is not perfectly objective. The rubric and reference answer
are given verbatim so the grader has a fixed target rather than its own
opinion, and the raw Q&A transcript (ComplexQuestions_Answers.txt) is kept
alongside the scores specifically so a human can spot-check any grade.

Usage:
    python tests/grade_complex_questions.py
"""
import json
import os
import re
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from src.config import OPENAI_API_KEY, PROJECT_ROOT

# A model independent of the answerer (gpt-5) grades here, so the same
# model isn't marking its own homework.
GRADER_MODEL = "gpt-4o"

RESULTS_PATH = str(PROJECT_ROOT / "tests" / "complex_results.json")
GRADES_PATH = str(PROJECT_ROOT / "tests" / "complex_grades.json")

_client = OpenAI(api_key=OPENAI_API_KEY)

RUBRIC = """4/4 — Completely right: fully correct and complete.
3/4 — Correct but contains some minor mistakes.
2/4 — Incorrect in general, but contains some true information.
1/4 — Completely wrong: the information is incorrect."""


def _parse_retry_after(message: str, default: float = 5.0) -> float:
    m = re.search(r"try again in ([\d.]+)(ms|s)", message)
    if not m:
        return default
    value, unit = float(m.group(1)), m.group(2)
    return (value / 1000 if unit == "ms" else value) + 0.5


def grade_one(item: dict) -> dict:
    prompt = f"""You are grading a RAG assistant's answer to a hard broker policy question, against a fixed rubric and reference answer.

Rubric:
{RUBRIC}

Question ({item['complexity_type']}, lenders: {item['lenders_involved']}):
{item['question']}

Reference (gold-standard) answer:
{item['reference_answer']}

This question was specifically designed to test: {item['failure_mode']}

Model's actual answer:
{item['model_answer']}

Score the model's answer 1-4 against the reference answer's facts (not against writing style — a differently-worded answer that states the same facts is still a 4). Also say whether the model fell for the documented failure mode/trap above (true/false) — a "fell_for_trap" of true generally implies a lower score, but judge the score on factual correctness first.

Reply with only JSON: {{"score": 1-4, "fell_for_trap": true or false, "rationale": "one or two sentences on what was right/wrong"}}"""

    max_retries = 6
    for attempt in range(max_retries):
        try:
            response = _client.chat.completions.create(
                model=GRADER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=300,
                temperature=0,
            )
            parsed = json.loads(response.choices[0].message.content)
            return {
                "score": int(parsed.get("score", 0)),
                "fell_for_trap": bool(parsed.get("fell_for_trap", False)),
                "rationale": str(parsed.get("rationale", "")),
            }
        except Exception as e:
            is_rate_limit = "rate_limit" in str(e).lower() or "429" in str(e)
            if attempt < max_retries - 1 and is_rate_limit:
                time.sleep(_parse_retry_after(str(e)))
                continue
            return {"score": 0, "fell_for_trap": None, "rationale": f"GRADING ERROR: {e}"}


def grade_all():
    with open(RESULTS_PATH, encoding="utf-8") as f:
        results = json.load(f)
    print(f"Loaded {len(results)} results from {RESULTS_PATH}", flush=True)

    graded = []
    for i, item in enumerate(results):
        grade = grade_one(item)
        graded.append({**item, **grade})
        print(f"[{i+1}/{len(results)}] {item['id']} -> score {grade['score']}"
              f"{' (FELL FOR TRAP)' if grade['fell_for_trap'] else ''}", flush=True)
        with open(GRADES_PATH, "w", encoding="utf-8") as f:
            json.dump(graded, f, indent=2)

    print(f"\nAll done. Grades saved to {GRADES_PATH}")
    return graded


if __name__ == "__main__":
    grade_all()
