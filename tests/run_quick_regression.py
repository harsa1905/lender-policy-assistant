"""
Runs a small, curated subset of the 111-question complex bank against the
live backend — for verifying a fix without paying for the full suite every
time. The full suite has been run in full 9+ times over this project's
life; most of those runs were checking one specific fix, not a milestone.

The default set (14 questions) covers every complexity_type in the bank,
every one of the 7 lenders, three fan-out ("All") questions (the expensive
retrieve-the-whole-corpus path), and every question that has previously
caught a real regression in this project: CQ-003 (Angle rate-table
ambiguity), CQ-011/CQ-108 (rate calc headline-vs-breakdown mismatch),
CQ-088 (Angle bus-coverage cross-lender contamination), CQ-096
(adjacent-attribute comparison), CQ-099 (exact-cap edge case), CQ-089/
CQ-102 (fan-out latency).

Usage:
    1. Start the backend: uvicorn src.api:app --port 8000
    2. python tests/run_quick_regression.py                    # default 14-question set
    3. python tests/run_quick_regression.py --ids CQ-003,CQ-096 # explicit questions
    4. python tests/run_quick_regression.py --lender BFS        # every question touching BFS

Run the full 111-question suite (run_complex_questions.py) before a
milestone/competition checkpoint, not after every small chunk fix. No
auto-scoring here either (see test_queries.py for why) — read the results
yourself or hand tests/quick_results.json to Claude to grade.
"""
import argparse
import sys
import urllib.request
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import PROJECT_ROOT
from tests.run_complex_questions import load_questions, run_all

RESULTS_PATH = str(PROJECT_ROOT / "tests" / "quick_results.json")
ANSWERS_TXT_PATH = str(PROJECT_ROOT / "QuickRegression_Answers.txt")

DEFAULT_QUICK_SET = [
    "CQ-003",  # Cross-lender comparison (2) | Angle, Flexi        | rate-table ambiguity regression
    "CQ-011",  # Multi-filter (single lender) | Resimac             | headline-vs-breakdown calc regression
    "CQ-023",  # Negative / trap constraint   | Flexi
    "CQ-069",  # Contradiction detection      | CFAL
    "CQ-076",  # Ambiguous / needs clarification | All (fan-out)
    "CQ-088",  # Cross-lender comparison (3+) | Westpac, CFAL, Angle, Metro | bus-coverage regression
    "CQ-089",  # Cross-lender + multi-filter  | Resimac, Westpac    | fan-out latency watch
    "CQ-092",  # Conditional scenario chain   | BFS
    "CQ-095",  # Policy-interaction edge case | CFAL
    "CQ-096",  # Cross-lender comparison (2)  | Angle, Resimac      | adjacent-attribute regression
    "CQ-098",  # Cross-lender + multi-filter  | All (fan-out)
    "CQ-099",  # Multi-filter (single lender) | Westpac             | exact-cap edge case regression
    "CQ-102",  # Best-fit recommendation      | All (fan-out)       | latency watch
    "CQ-108",  # Calculation / arithmetic     | Resimac             | headline-vs-breakdown calc regression
]


def select_questions(args, all_questions):
    by_id = {q["id"]: q for q in all_questions}

    if args.ids:
        wanted = [i.strip() for i in args.ids.split(",")]
        missing = [i for i in wanted if i not in by_id]
        if missing:
            print(f"Unknown question ID(s): {', '.join(missing)}")
            sys.exit(1)
        return [by_id[i] for i in wanted]

    if args.lender:
        selected = [q for q in all_questions
                   if args.lender.lower() in (q["lenders_involved"] or "").lower()]
        if not selected:
            print(f"No questions found mentioning lender '{args.lender}'")
            sys.exit(1)
        return selected

    return [by_id[i] for i in DEFAULT_QUICK_SET]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ids", help="Comma-separated question IDs to run instead of the default 14-question set")
    parser.add_argument("--lender", help="Run every question whose lenders_involved mentions this lender")
    args = parser.parse_args()

    try:
        urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3)
    except Exception:
        print("Backend isn't responding at http://127.0.0.1:8000 — start it first:")
        print("  uvicorn src.api:app --port 8000")
        sys.exit(1)

    selected = select_questions(args, load_questions())
    print(f"Running {len(selected)} question(s) — quick regression, not the full 111.\n")
    run_all(selected, results_path=RESULTS_PATH, answers_txt_path=ANSWERS_TXT_PATH)


if __name__ == "__main__":
    main()
