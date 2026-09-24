"""
Runs the practice cases in docs/Finals_Practice_Cases.md against the live
backend, so they can be graded against the verified reference answers in
that document.

Case shapes mirror the supplied finals mock (finals-QA - mock.docx):
  Group A  rate questions            -- single turn
  Group B  long-chat / memory        -- REAL multi-turn conversations; turn 3
                                        is meaningless without turns 1-2 in
                                        history, which is the whole point
  Group C  special-position policy   -- single turn

Reference answers live in the markdown doc, not here -- this file is the
harness. Each was verified directly against the chunk files (chunk ids are
listed per case in the doc); do not "fix" a case here to match the system's
output without checking the chunk first, which is exactly how
ComplexQuestions.xlsx went stale three times.

DATA SAFETY: case B3 sends a chat correction with a deliberately fabricated
establishment fee ($700), which the pipeline saves straight into the answer
library. Both data files are snapshotted before the run and restored in a
finally block, so nothing invented here survives.

Usage:
    1. Start the backend: uvicorn src.api:app --port 8000
    2. python tests/run_finals_practice.py
    3. python tests/run_finals_practice.py --ids A1,B1,C4
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import PROJECT_ROOT, ANSWER_LIBRARY_PATH, QUERY_CACHE_PATH

API_BASE = "http://127.0.0.1:8000"
RESULTS_PATH = str(PROJECT_ROOT / "tests" / "finals_practice_results.json")
TRANSCRIPT_PATH = str(PROJECT_ROOT / "FinalsPractice_Answers.txt")

# turns: list of question strings. More than one = a real conversation.
CASES = [
    # ---------------- GROUP A -- rate ----------------
    {"id": "A1", "group": "A. Rate", "title": "Lowest rate per lender for an ELECTRIC passenger vehicle",
     "turns": ["I want to finance an electric passenger vehicle. What is the lowest displayed interest rate from each lender?"],
     "expect": "Westpac 6.75% (7.75 less 1% EV), Resimac 7.54% PP, Metro 7.20% (8.20 less 1% MetroEco), "
               "BFS 7.60% with no EV discount, Angle no EV-specific rate, Flexi not fundable (passenger cars "
               "excluded), CFAL no public rate card."},

    {"id": "A2", "group": "A. Rate", "title": "Stacking loadings landing exactly on the 4% cap",
     "turns": ["Resimac deal: a PremiumPLUS client buying a classic car, 5 years old, through a private sale. What's the all-in rate?"],
     "expect": "8.24% base (>3yr MV, PremiumPLUS column read directly) + 2% classic + 2% private sale = 4%, "
               "exactly at the 4% cap -> 12.24%. Balloon must be 0 (classic cars excluded from balloons)."},

    {"id": "A3", "group": "A. Rate", "title": "Premium tier the client does NOT qualify for",
     "turns": ["A company with a 3-year-old ABN and GST registration, asset backed, wants $200,000 for a primary asset. What's flexicommercial's rate?"],
     "expect": "7.85% standard ($150,001+ Primary). NOT 7.15% -- flexipremium needs 4+ years ABN/GST asset-backed."},

    {"id": "A4", "group": "A. Rate", "title": "Three independent add-ons on the standard card",
     "turns": ["flexicommercial, non-asset-backed customer, $80,000 primary asset, private sale, 72-month term. Build up the rate."],
     "expect": "8.35% base ($20,001-$150,000 Primary) + 1.00% private sale + 1.25% term >60mo + 1.50% "
               "non-asset-backed = 12.10%. (Also cannot reach flexipremium: non-asset-backed needs 8+ years.)"},

    # ---------------- GROUP B -- memory / long chat ----------------
    {"id": "B1", "group": "B. Memory", "title": "Three-turn chain, subject never repeated",
     "turns": [
         "Which lender supports classic cars?",
         "What rate would a PremiumPLUS client get on a 5-year-old one?",
         "And if they buy it privately?",
     ],
     "expect": "T1 Resimac only. T2 8.24% + 2% classic = 10.24%. T3 second +2% stacks to the 4% cap -> 12.24%."},

    {"id": "B2", "group": "B. Memory", "title": "Lender switch, then a comparison needing both earlier turns",
     "turns": [
         "What's the maximum loan under BFS New Business Ventures?",
         "What about Angle's Start-Up product?",
         "So for a $120,000 deal, which one works?",
     ],
     "expect": "T1 $100k. T2 $150k incl brokerage. T3 Angle only -- $120k exceeds BFS's $100k cap but fits "
               "Angle's $150k, subject to 3 months trading and 20% deposit."},

    {"id": "B3", "group": "B. Memory", "title": "Mid-chat correction must propagate into later reasoning",
     "turns": [
         "What's Angle's establishment fee?",
         "That's out of date, it's actually $700 now.",
         "So what's the total upfront cost with a 20% deposit on a $50,000 ute?",
     ],
     "expect": "T3 must use the corrected $700 (not $649): $10,000 deposit + $700 establishment fee. "
               "NOTE: $700 is a fabricated test value, restored away after the run."},

    # ---------------- GROUP C -- special position ----------------
    {"id": "C1", "group": "C. Special position", "title": "Credit score exactly on the tier boundary",
     "turns": ["A BFS commercial applicant has an Experian CCR score of exactly 600. Another has 599. What changes between them?"],
     "expect": "600 = Tier 2 (meets the minimum, no mandatory deposit). 599 = Tier 3 (550+), which carries a "
               "mandatory 20% deposit on EVERY application, not conditional on contract type."},

    {"id": "C2", "group": "C. Special position", "title": "Threshold met exactly -- no auto-decline",
     "turns": ["A BFS consumer applicant has net monthly income of exactly $2,318. Is that an automatic decline?"],
     "expect": "No -- the trigger is income BELOW $2,318. At exactly $2,318 it does not fire. Other auto-decline "
               "triggers still apply independently."},

    {"id": "C3", "group": "C. Special position", "title": "Allied health vs medical specialist limits",
     "turns": ["A physiotherapist with 5 years' experience wants $200,000 of new medical equipment under Westpac Medical. Does it fit?"],
     "expect": "No. Physio = Allied Health = single combined <$150k cap across MV/office/medical equipment; "
               "cumulative <$250k. The <$350k medical-equipment figure is Specialist/GP/Dental/Vet only. "
               "The 5 years' experience is a red herring (>3yr requirement is satisfied)."},

    {"id": "C4", "group": "C. Special position", "title": "Loan size vs total exposure",
     "turns": ["A Metro customer with 12 months of good repayment history wants a single $400,000 truck. Their maximum exposure is $500,000 — so this fits, right?"],
     "expect": "No -- false premise. Max LOAN SIZE with 12 months history is $300k (dealer); exposure $500k is a "
               "separate aggregate ceiling. Both must be cleared. Prime movers excluded; private sale caps $250k."},

    {"id": "C5", "group": "C. Special position", "title": "Remote area -- which lender actually has the rule",
     "turns": ["My client is in a Remote area and is non-asset-backed. What deposit will BFS want, and what about CFAL?"],
     "expect": "BFS PRIME: 20% deposit for non-asset-backed in remote areas. CFAL: no such rule exists -- it was "
               "traced to Resimac's/BFS's guides and removed. Do not apply a geography rule to CFAL."},

    {"id": "C6", "group": "C. Special position", "title": "Hard exclusion vs soft condition",
     "turns": ["My client wants flexicommercial to fund a passenger car for their business. They can put down a 50% deposit and they've been trading 10 years. Does that get it over the line?"],
     "expect": "No. Passenger cars/SUVs are a hard asset exclusion at flexicommercial -- deposit and trading "
               "history cannot satisfy it. Commercial vehicles (utes/vans/4WDs) ARE fundable as primary assets."},

    {"id": "C7", "group": "C. Special position", "title": "A product tier that does not exist",
     "turns": ["What are CFAL's Low Doc requirements for a $150,000 transaction?"],
     "expect": "CFAL has NO Low Doc option -- reject the premise. Documentation scales with transaction size; "
               "financial statements must be no more than 18 months old, for all related companies and trusts."},

    {"id": "C8", "group": "C. Special position", "title": "The corpus contradicts itself",
     "turns": ["What's the maximum vehicle price for Metro's MetroEco electric vehicle discount?"],
     "expect": "Flag the conflict: rate sheet says $91,661, MetroEco booklet says $91,387. Surface BOTH and say "
               "to confirm with Metro. Silently picking one (or averaging) is the failure."},
]


def _post(path, body, timeout=180):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(API_BASE + path, data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _snapshot(path):
    return Path(path).read_text(encoding="utf-8") if os.path.exists(path) else None


def _restore(path, snap):
    if snap is None:
        if os.path.exists(path):
            os.remove(path)
        return
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(snap)
    os.replace(tmp, path)


def run_case(case):
    print(f"\n{case['id']} ({case['group']}): {case['title']}")
    history, turns_out = [], []
    for i, question in enumerate(case["turns"], start=1):
        try:
            data = _post("/query", {"question": question,
                                    "history": [{"question": h["question"], "answer": h["answer"]} for h in history[-3:]]})
        except Exception as e:
            print(f"  T{i}: ERROR {type(e).__name__}: {e}")
            turns_out.append({"turn": i, "question": question, "answer": f"ERROR: {e}",
                              "answer_source": "error", "sources": [], "seconds": 0})
            continue
        history.append({"question": question, "answer": data["answer"]})
        turns_out.append({
            "turn": i, "question": question, "answer": data["answer"],
            "answer_source": data.get("answer_source"),
            "sources": [s["chunk_id"] for s in data.get("sources", [])],
            "seconds": round(data.get("response_time", 0), 1),
        })
        print(f"  T{i}: {data.get('answer_source')} | {len(data.get('sources', []))} src | {data.get('response_time', 0):.1f}s")
    return {**{k: case[k] for k in ("id", "group", "title", "expect")}, "turns": turns_out}


def write_transcript(results, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("#" * 92 + "\n# FINALS PRACTICE CASES -- grade against docs/Finals_Practice_Cases.md\n" + "#" * 92 + "\n\n")
        for r in results:
            f.write("=" * 92 + "\n")
            f.write(f"{r['id']} | {r['group']} | {r['title']}\n")
            f.write("=" * 92 + "\n\n")
            f.write(f"EXPECTED (verified against chunks):\n{r['expect']}\n\n")
            for t in r["turns"]:
                label = f"TURN {t['turn']}" if len(r["turns"]) > 1 else "QUESTION"
                f.write(f"{label}: {t['question']}\n\n")
                f.write(f"{t['answer']}\n\n")
                f.write(f"[{t['answer_source']} | {len(t['sources'])} sources | {t['seconds']}s]\n")
                if len(r["turns"]) > 1:
                    f.write(f"sources: {', '.join(t['sources'][:14]) or 'none'}\n")
                f.write("\n")
            f.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ids", help="Comma-separated case IDs to run instead of all")
    parser.add_argument("--no-restore", action="store_true",
                        help="Leave data files as the run left them (debug only -- B3 saves a fabricated fee)")
    args = parser.parse_args()

    try:
        urllib.request.urlopen(f"{API_BASE}/health", timeout=5)
    except Exception:
        print(f"Backend isn't responding at {API_BASE} -- start it first:\n  uvicorn src.api:app --port 8000")
        sys.exit(1)

    cases = CASES
    if args.ids:
        wanted = [i.strip() for i in args.ids.split(",")]
        by_id = {c["id"]: c for c in CASES}
        missing = [i for i in wanted if i not in by_id]
        if missing:
            print(f"Unknown case ID(s): {', '.join(missing)}")
            sys.exit(1)
        cases = [by_id[i] for i in wanted]

    print(f"Running {len(cases)} practice case(s).")
    cache_snap = _snapshot(QUERY_CACHE_PATH)
    lib_snap = _snapshot(ANSWER_LIBRARY_PATH)

    results = []
    try:
        for c in cases:
            results.append(run_case(c))
    finally:
        if not args.no_restore:
            # Only the library is rolled back: B3's fabricated correction must
            # not survive. The query cache is deliberately KEPT -- these are
            # real questions and the cache was just cleared for a fresh
            # pre-competition warm-up, so letting them land is useful.
            _restore(ANSWER_LIBRARY_PATH, lib_snap)
            print("\nRestored answer_library.json (B3's fabricated $700 correction removed). "
                  "Query cache intentionally kept -- these are real questions worth caching.")

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    write_transcript(results, TRANSCRIPT_PATH)
    print(f"\nRaw results: {RESULTS_PATH}\nTranscript:  {TRANSCRIPT_PATH}")
    print("\nNo auto-scoring -- grade each answer against its EXPECTED block in the transcript.")


if __name__ == "__main__":
    main()
