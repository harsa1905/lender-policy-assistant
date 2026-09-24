"""Generate the shareable results page from finals_practice_results.json.

Generated rather than hand-written so every answer is verbatim from the run
-- transcribing 15 cases by hand is how a report quietly stops matching what
the system actually said.
"""
import html
import json
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import PROJECT_ROOT

SRC = str(PROJECT_ROOT / "tests" / "finals_practice_results.json")
OUT = str(PROJECT_ROOT / "finals_practice_report.html")

# Grading verdicts (mine, against the verified references in
# docs/Finals_Practice_Cases.md). "watch" = correct but with a caveat.
VERDICT = {
    "A1": ("pass", "All seven lenders right. Applied the EV discounts that exist and invented none where they don't."),
    "A2": ("pass", "Both loadings stacked, cap recognised explicitly as a ceiling that was reached, not exceeded."),
    "A3": ("pass", "The premium-tier trap. Gave 7.85%, not 7.15%, and named the 4-year requirement as the reason."),
    "A4": ("pass", "All three add-ons. Volunteered two eligibility conditions the question didn't ask for."),
    "B1": ("pass", "Turn 3 named nothing. Carried four attributes across two hops and knew the loading stacks."),
    "B2": ("pass", "Held figures from two separate turns and compared both against a number introduced only in turn 3."),
    "B3": ("pass", "The corrected fee propagated into later arithmetic, not just into a repeat of the same question."),
    "C1": ("pass", "Treated 600 as the qualifying minimum. Also caught that the used-vehicle limit is Tier 4, not Tier 3."),
    "C2": ("pass", "Read it as a threshold, not a memorised association. Exactly at the floor is not a decline."),
    "C3": ("pass", "Avoided the $350k figure sitting in the same table, and named the experience detail as satisfied."),
    "C4": ("pass", "Rejected the premise and separated the per-deal cap from the aggregate exposure ceiling."),
    "C5": ("pass", "Surfaced two carve-outs the reference answer had missed. Both verified correct against policy."),
    "C6": ("pass", "Held the line that a hard asset exclusion is not a credit condition a deposit can satisfy."),
    "C7": ("pass", "Rejected the false premise, then gave the correct document band in full."),
    "watch_note": None,
}
VERDICT["C8"] = ("watch", "Flagged both conflicting figures and said to confirm — then added a working range. "
                          "Defensible for a broker, but it softens the 'don't quote until confirmed' line.")

GROUP_BLURB = {
    "A. Rate": ("Rate accuracy",
                "The mock calls Case 1 \u201cmainly test rate related\u201d, so these press hardest on rate-table "
                "selection: picking the right band, applying discounts only where they exist, stacking loadings, "
                "and respecting caps."),
    "B. Memory": ("Memory across a conversation",
                  "Run as real multi-turn conversations. The final turn in each names neither the lender nor the "
                  "asset \u2014 the context has to survive from earlier turns or the answer is meaningless."),
    "C. Special position": ("Policy edge cases",
                            "Threshold boundaries, exclusions that can\u2019t be bought out, a product tier that "
                            "doesn\u2019t exist, and one question the source documents answer two different ways."),
}


def md(text):
    """Minimal markdown -> HTML for the answer bodies (bold, bullets, breaks)."""
    out, buf, lines = [], [], text.split("\n")
    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            buf.append(stripped[2:])
            continue
        if buf:
            out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in buf) + "</ul>")
            buf = []
        if stripped:
            out.append(f"<p>{inline(stripped)}</p>")
    if buf:
        out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in buf) + "</ul>")
    return "".join(out)


def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    # percentages, dollar figures and month counts read as data, not prose
    s = re.sub(r"(?<![\w>])(\$[\d,]+(?:\.\d+)?k?|\d+\.\d+%|\d+%)", r'<span class="fig">\1</span>', s)
    return s


with open(SRC, encoding="utf-8") as f:
    cases = json.load(f)

n_pass = sum(1 for c in cases if VERDICT[c["id"]][0] == "pass")
n_watch = sum(1 for c in cases if VERDICT[c["id"]][0] == "watch")
total_turns = sum(len(c["turns"]) for c in cases)

# ---------- summary rows ----------
rows = []
for c in cases:
    v, note = VERDICT[c["id"]]
    secs = sum(t["seconds"] for t in c["turns"])
    turns = len(c["turns"])
    rows.append(f"""<tr>
      <td class="mono id-cell"><a href="#{c['id']}">{c['id']}</a></td>
      <td>{html.escape(c['title'])}</td>
      <td class="mono num">{turns}</td>
      <td class="mono num">{secs:.1f}s</td>
      <td><span class="chip chip-{v}">{'Correct' if v == 'pass' else 'Correct, with a caveat'}</span></td>
    </tr>""")

# ---------- case detail ----------
blocks, current_group = [], None
for c in cases:
    if c["group"] != current_group:
        current_group = c["group"]
        label, blurb = GROUP_BLURB[current_group]
        blocks.append(f"""<section class="group-intro">
      <p class="eyebrow">{html.escape(current_group.split('. ')[0])} &middot; {html.escape(label)}</p>
      <p class="group-blurb">{blurb}</p>
    </section>""")

    v, note = VERDICT[c["id"]]
    turn_html = []
    multi = len(c["turns"]) > 1
    for t in c["turns"]:
        label = f"Turn {t['turn']}" if multi else "Question"
        src = t.get("answer_source") or ""
        badge = ' <span class="src-tag">correction saved</span>' if src == "correction_saved" else ""
        turn_html.append(f"""<div class="turn">
        <p class="turn-label">{label}{badge}</p>
        <p class="question">{html.escape(t['question'])}</p>
        <div class="answer">{md(t['answer'])}</div>
        <p class="meta mono">{len(t['sources'])} sources &middot; {t['seconds']}s</p>
      </div>""")

    blocks.append(f"""<article class="case" id="{c['id']}">
      <header class="case-head">
        <span class="mono case-id">{c['id']}</span>
        <h3>{html.escape(c['title'])}</h3>
        <span class="chip chip-{v}">{'Correct' if v == 'pass' else 'Caveat'}</span>
      </header>
      <div class="expected">
        <p class="expected-label">Expected &mdash; verified against the policy chunk files</p>
        <p>{inline(c['expect'])}</p>
      </div>
      <div class="turns">{''.join(turn_html)}</div>
      <p class="assessment"><span class="assessment-label">Assessment</span> {html.escape(note)}</p>
    </article>""")

page = f"""<title>LifeX Policy Assistant &mdash; Finals Practice Results</title>
<style>
:root {{
  --ground:#FCFCFD; --surface:#FFFFFF; --surface-2:#F4F6F8;
  --ink:#16202B; --ink-2:#3D4A59; --muted:#5F6C7B;
  --rule:#E1E6EC; --rule-strong:#CBD3DC;
  --accent:#1F4E79; --accent-soft:#EAF1F8;
  --pass:#1B6B47; --pass-soft:#E6F2EC;
  --watch:#8A5A00; --watch-soft:#FBF1DD;
  --display:Georgia,"Iowan Old Style","Times New Roman",serif;
  --body:-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
  --mono:ui-monospace,"SF Mono","Cascadia Mono",Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#12161B; --surface:#171D24; --surface-2:#1D242C;
    --ink:#E7ECF1; --ink-2:#C3CCD6; --muted:#94A1B0;
    --rule:#28313A; --rule-strong:#3A4550;
    --accent:#84B6E2; --accent-soft:#17242F;
    --pass:#63C295; --pass-soft:#152620;
    --watch:#DCA84A; --watch-soft:#2A2213;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#12161B; --surface:#171D24; --surface-2:#1D242C;
  --ink:#E7ECF1; --ink-2:#C3CCD6; --muted:#94A1B0;
  --rule:#28313A; --rule-strong:#3A4550;
  --accent:#84B6E2; --accent-soft:#17242F;
  --pass:#63C295; --pass-soft:#152620;
  --watch:#DCA84A; --watch-soft:#2A2213;
}}
* {{ box-sizing:border-box; }}
body {{
  background:var(--ground); color:var(--ink);
  font-family:var(--body); font-size:16px; line-height:1.6;
  margin:0; padding:0 20px 96px;
  -webkit-font-smoothing:antialiased;
}}
.wrap {{ max-width:860px; margin:0 auto; }}
.masthead {{ padding:64px 0 32px; border-bottom:2px solid var(--ink); margin-bottom:40px; }}
.eyebrow {{
  font-family:var(--mono); font-size:11px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--muted); margin:0 0 14px;
}}
h1 {{
  font-family:var(--display); font-weight:400; font-size:clamp(30px,5vw,44px);
  line-height:1.14; letter-spacing:-.01em; margin:0 0 16px; text-wrap:balance;
}}
.standfirst {{ font-size:17px; color:var(--ink-2); margin:0; max-width:64ch; }}
.scoreline {{ display:flex; flex-wrap:wrap; gap:28px; margin:32px 0 0; padding:0; list-style:none; }}
.scoreline div {{ display:flex; flex-direction:column; gap:2px; }}
.score-n {{ font-family:var(--display); font-size:30px; line-height:1; }}
.score-l {{
  font-family:var(--mono); font-size:10.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--muted);
}}
h2 {{
  font-family:var(--display); font-weight:400; font-size:25px;
  margin:56px 0 8px; padding-bottom:9px; border-bottom:1px solid var(--rule-strong);
  text-wrap:balance;
}}
.section-note {{ color:var(--muted); font-size:14.5px; margin:0 0 22px; max-width:66ch; }}
.table-scroll {{ overflow-x:auto; border:1px solid var(--rule); border-radius:3px; background:var(--surface); }}
table {{ width:100%; border-collapse:collapse; font-size:14.5px; min-width:520px; }}
th {{
  text-align:left; font-family:var(--mono); font-weight:600; font-size:10.5px;
  letter-spacing:.09em; text-transform:uppercase; color:var(--muted);
  padding:11px 14px; border-bottom:1px solid var(--rule-strong); white-space:nowrap;
}}
td {{ padding:11px 14px; border-bottom:1px solid var(--rule); vertical-align:middle; }}
tr:last-child td {{ border-bottom:none; }}
.num {{ text-align:right; font-variant-numeric:tabular-nums; color:var(--muted); }}
.id-cell a {{ color:var(--accent); text-decoration:none; font-weight:600; }}
.id-cell a:hover, .id-cell a:focus-visible {{ text-decoration:underline; }}
.mono {{ font-family:var(--mono); }}
.chip {{
  display:inline-block; font-family:var(--mono); font-size:10.5px;
  letter-spacing:.05em; padding:3px 9px; border-radius:2px; white-space:nowrap;
}}
.chip-pass {{ background:var(--pass-soft); color:var(--pass); }}
.chip-watch {{ background:var(--watch-soft); color:var(--watch); }}
.group-intro {{ margin:52px 0 26px; padding-left:16px; border-left:3px solid var(--accent); }}
.group-intro .eyebrow {{ margin-bottom:7px; color:var(--accent); }}
.group-blurb {{ margin:0; color:var(--ink-2); font-size:15px; max-width:66ch; }}
.case {{
  background:var(--surface); border:1px solid var(--rule);
  border-radius:4px; padding:24px; margin:0 0 20px;
}}
.case-head {{ display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; margin-bottom:16px; }}
.case-id {{
  font-size:12px; font-weight:600; color:var(--accent);
  background:var(--accent-soft); padding:3px 8px; border-radius:2px;
}}
.case-head h3 {{
  font-family:var(--display); font-weight:400; font-size:19px;
  margin:0; flex:1 1 260px; line-height:1.3;
}}
.expected {{
  background:var(--surface-2); border-radius:3px;
  padding:14px 16px; margin-bottom:20px; font-size:14.5px; color:var(--ink-2);
}}
.expected p:last-child {{ margin:0; }}
.expected-label {{
  font-family:var(--mono); font-size:10px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--muted); margin:0 0 6px;
}}
.turns {{ display:flex; flex-direction:column; gap:22px; }}
.turn {{ border-left:2px solid var(--rule-strong); padding-left:16px; }}
.turn-label {{
  font-family:var(--mono); font-size:10px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--muted); margin:0 0 6px;
}}
.src-tag {{
  color:var(--accent); background:var(--accent-soft);
  padding:2px 6px; border-radius:2px; letter-spacing:.04em;
}}
.question {{
  font-family:var(--display); font-size:17px; line-height:1.42;
  margin:0 0 12px; color:var(--ink);
}}
.answer {{ font-size:15px; }}
.answer p {{ margin:0 0 10px; }}
.answer p:last-child {{ margin-bottom:0; }}
.answer ul {{ margin:0 0 10px; padding-left:20px; }}
.answer li {{ margin-bottom:5px; }}
.answer strong {{ color:var(--ink); font-weight:600; }}
.fig {{ font-family:var(--mono); font-size:.93em; font-variant-numeric:tabular-nums; }}
.meta {{ font-size:11px; color:var(--muted); margin:10px 0 0; letter-spacing:.03em; }}
.assessment {{
  margin:20px 0 0; padding-top:14px; border-top:1px solid var(--rule);
  font-size:14px; color:var(--ink-2);
}}
.assessment-label {{
  font-family:var(--mono); font-size:10px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--muted); margin-right:8px;
}}
.callout {{
  border:1px solid var(--rule-strong); border-left:3px solid var(--watch);
  background:var(--surface); border-radius:3px; padding:18px 20px; margin:26px 0;
}}
.callout h3 {{ font-family:var(--display); font-weight:400; font-size:17px; margin:0 0 8px; }}
.callout p {{ margin:0 0 10px; font-size:14.5px; color:var(--ink-2); }}
.callout p:last-child {{ margin:0; }}
footer {{
  margin-top:64px; padding-top:22px; border-top:1px solid var(--rule);
  font-size:13px; color:var(--muted);
}}
a {{ color:var(--accent); }}
:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
@media (max-width:600px) {{
  .masthead {{ padding-top:44px; }}
  .case {{ padding:18px; }}
}}
</style>

<div class="wrap">
  <header class="masthead">
    <p class="eyebrow">LifeX Policy Assistant &middot; Evaluation</p>
    <h1>Finals practice results</h1>
    <p class="standfirst">
      Fifteen practice cases built in the same shape as the supplied finals mock, run against
      the live assistant. Each expected answer was verified directly against the lender policy
      files before the run &mdash; not written from memory &mdash; so a disagreement points at
      the system or at the source documents, never at a guess.
    </p>
    <div class="scoreline">
      <div><span class="score-n">{n_pass}/{len(cases)}</span><span class="score-l">Correct</span></div>
      <div><span class="score-n">{n_watch}</span><span class="score-l">With a caveat</span></div>
      <div><span class="score-n">{total_turns}</span><span class="score-l">Questions asked</span></div>
      <div><span class="score-n">7</span><span class="score-l">Lenders covered</span></div>
    </div>
  </header>

  <h2>At a glance</h2>
  <p class="section-note">
    Cases are grouped by the three capabilities the mock tests. Select a case ID to jump to the
    full question and answer.
  </p>
  <div class="table-scroll">
    <table>
      <thead><tr><th>Case</th><th>What it tests</th><th>Turns</th><th>Time</th><th>Result</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>

  <div class="callout">
    <h3>One thing to flag about the mock&rsquo;s own answer key</h3>
    <p>
      For Case 3 the supplied key gives BFS a flat &ldquo;20% deposit&rdquo;. The underlying policy file
      states the New Business Ventures deposit is <strong>20% for Tier 3 and Tier 4</strong> &mdash; tier-dependent,
      not universal. Our assistant answers the tier-dependent version, which is more precise than the key.
    </p>
    <p>
      Worth agreeing as a team whether to answer precisely or to match the key, in case a judge marks
      against the flat figure.
    </p>
  </div>

  <h2>Case by case</h2>
  <p class="section-note">
    Answers below are reproduced exactly as the assistant returned them.
  </p>
  {''.join(blocks)}

  <footer>
    <p>
      Generated from <span class="mono">tests/finals_practice_results.json</span>. Cases and verified
      reference answers live in <span class="mono">docs/Finals_Practice_Cases.md</span>; rerun any time
      with <span class="mono">python tests/run_finals_practice.py</span>.
    </p>
  </footer>
</div>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(page)
print("wrote", OUT, len(page), "bytes")
