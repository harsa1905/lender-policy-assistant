"""Render docs/Technical_Documentation.md as a readable HTML manual.

Generated from the markdown rather than hand-authored so the two can't drift
-- edit the .md, re-run this, and the HTML follows.

The converter handles exactly the constructs used in that document (headings,
pipe tables, fenced code, blockquotes, lists, bold/italic/inline-code, links,
rules). It is not a general markdown parser and doesn't need to be.
"""
import html
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import PROJECT_ROOT

SRC = str(PROJECT_ROOT / "docs" / "Technical_Documentation.md")
OUT = str(PROJECT_ROOT / "LifeX_Technical_Documentation_v2.html")


def inline(s, escape=True):
    if escape:
        s = html.escape(s)
    # inline code first so its contents aren't re-processed
    holds = []

    def hold(m):
        holds.append(m.group(1))
        return f"\x00{len(holds) - 1}\x00"

    s = re.sub(r"`([^`]+)`", hold, s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", s)
    for i, code in enumerate(holds):
        s = s.replace(f"\x00{i}\x00", f"<code>{code}</code>")
    return s


def slug(text):
    t = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s]+", "-", t).strip("-")


with open(SRC, encoding="utf-8") as f:
    lines = f.read().split("\n")

body, toc = [], []
i, n = 0, len(lines)

while i < n:
    line = lines[i]
    stripped = line.strip()

    # fenced code
    if stripped.startswith("```"):
        i += 1
        buf = []
        while i < n and not lines[i].strip().startswith("```"):
            buf.append(html.escape(lines[i]))
            i += 1
        i += 1
        body.append('<pre><code>' + "\n".join(buf) + "</code></pre>")
        continue

    # pipe table
    if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
        header = [c.strip() for c in stripped.strip("|").split("|")]
        i += 2
        rows = []
        while i < n and lines[i].strip().startswith("|"):
            rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
            i += 1
        thead = "".join(f"<th>{inline(c)}</th>" for c in header)
        tbody = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
        body.append(f'<div class="table-scroll"><table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>')
        continue

    # blockquote (may span lines)
    if stripped.startswith(">"):
        buf = []
        while i < n and lines[i].strip().startswith(">"):
            buf.append(lines[i].strip().lstrip(">").strip())
            i += 1
        text = " ".join(x for x in buf if x)
        body.append(f'<aside class="callout">{inline(text)}</aside>')
        continue

    # list
    if stripped.startswith("- "):
        items = []
        while i < n and (lines[i].strip().startswith("- ") or (lines[i].startswith("  ") and lines[i].strip() and items)):
            s = lines[i].strip()
            if s.startswith("- "):
                items.append(s[2:])
            else:
                items[-1] += " " + s
            i += 1
        body.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
        continue

    # headings
    if stripped.startswith("### "):
        t = stripped[4:]
        body.append(f'<h3 id="{slug(t)}">{inline(t)}</h3>')
        i += 1
        continue
    if stripped.startswith("## "):
        t = stripped[3:]
        sid = slug(t)
        num, _, rest = t.partition(". ")
        toc.append((sid, num if num.isdigit() else "", rest or t))
        body.append(f'<h2 id="{sid}"><span class="h2-num">{html.escape(num) if num.isdigit() else ""}</span>{inline(rest or t)}</h2>')
        i += 1
        continue
    if stripped.startswith("# "):
        i += 1
        continue  # page title handled by the masthead

    if stripped in ("---", "***"):
        body.append('<hr />')
        i += 1
        continue

    if not stripped:
        i += 1
        continue

    # paragraph (gather until blank / block start)
    buf = []
    while i < n and lines[i].strip() and not re.match(r"^(#|\||```|>|- |---$)", lines[i].strip()):
        buf.append(lines[i].strip())
        i += 1
    para = " ".join(buf)

    # Section 11 pattern: a bolded question followed directly by its answer.
    # In the source they sit on consecutive lines with no blank between, so
    # they arrive here as one paragraph -- split them back apart and render
    # the pair distinctly.
    m = re.match(r'^\*\*["“](.+?)["”]\*\*\s*(.*)$', para, re.S)
    if m:
        question, answer = m.group(1), m.group(2).strip()
        body.append(f'<p class="qa-q">{inline(question)}</p>')
        if answer:
            body.append(f"<p>{inline(answer)}</p>")
        continue
    body.append(f"<p>{inline(para)}</p>")

# The title goes in its own span: the anchor is a flex row, so any inline
# markup inside the title (an <em>, say) would otherwise become a sibling
# flex item and get spaced out as its own column.
toc_html = "".join(
    f'<li><a href="#{sid}"><span class="toc-num">{num}</span><span>{inline(title)}</span></a></li>'
    for sid, num, title in toc
)

page = f"""<title>LifeX Policy Assistant — Technical Documentation</title>
<style>
:root {{
  --ground:#FCFCFD; --surface:#FFFFFF; --surface-2:#F4F6F8; --code-bg:#F1F4F7;
  --ink:#16202B; --ink-2:#3D4A59; --muted:#5F6C7B;
  --rule:#E1E6EC; --rule-strong:#CBD3DC;
  --accent:#1F4E79; --accent-soft:#EAF1F8;
  --warn:#8A5A00; --warn-soft:#FBF1DD;
  --display:Georgia,"Iowan Old Style","Times New Roman",serif;
  --body:-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
  --mono:ui-monospace,"SF Mono","Cascadia Mono",Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#12161B; --surface:#171D24; --surface-2:#1D242C; --code-bg:#1B222A;
    --ink:#E7ECF1; --ink-2:#C3CCD6; --muted:#94A1B0;
    --rule:#28313A; --rule-strong:#3A4550;
    --accent:#84B6E2; --accent-soft:#17242F;
    --warn:#DCA84A; --warn-soft:#2A2213;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#12161B; --surface:#171D24; --surface-2:#1D242C; --code-bg:#1B222A;
  --ink:#E7ECF1; --ink-2:#C3CCD6; --muted:#94A1B0;
  --rule:#28313A; --rule-strong:#3A4550;
  --accent:#84B6E2; --accent-soft:#17242F;
  --warn:#DCA84A; --warn-soft:#2A2213;
}}
* {{ box-sizing:border-box; }}
body {{
  background:var(--ground); color:var(--ink);
  font-family:var(--body); font-size:16px; line-height:1.65;
  margin:0; padding:0 20px 100px; -webkit-font-smoothing:antialiased;
}}
.shell {{ max-width:1140px; margin:0 auto; }}
.masthead {{ padding:60px 0 28px; border-bottom:2px solid var(--ink); }}
.eyebrow {{
  font-family:var(--mono); font-size:11px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--muted); margin:0 0 14px;
}}
.masthead h1 {{
  font-family:var(--display); font-weight:400; font-size:clamp(30px,5vw,44px);
  line-height:1.14; margin:0 0 14px; text-wrap:balance;
}}
.masthead .standfirst {{ font-size:17px; color:var(--ink-2); margin:0; max-width:62ch; }}
.layout {{ display:grid; grid-template-columns:230px minmax(0,1fr); gap:52px; margin-top:40px; }}
nav {{ position:sticky; top:24px; align-self:start; max-height:calc(100vh - 48px); overflow-y:auto; }}
nav p {{
  font-family:var(--mono); font-size:10px; letter-spacing:.12em; text-transform:uppercase;
  color:var(--muted); margin:0 0 12px;
}}
nav ol {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:1px; }}
nav a {{
  display:flex; gap:9px; padding:5px 8px; border-radius:3px;
  color:var(--ink-2); text-decoration:none; font-size:13.5px; line-height:1.35;
}}
nav a:hover, nav a:focus-visible {{ background:var(--surface-2); color:var(--ink); }}
.toc-num {{ font-family:var(--mono); font-size:11px; color:var(--muted); min-width:14px; padding-top:2px; }}
main {{ min-width:0; }}
h2 {{
  font-family:var(--display); font-weight:400; font-size:27px; line-height:1.2;
  margin:56px 0 16px; padding-bottom:10px; border-bottom:1px solid var(--rule-strong);
  display:flex; gap:14px; align-items:baseline; scroll-margin-top:20px; text-wrap:balance;
}}
main > h2:first-child {{ margin-top:0; }}
.h2-num {{
  font-family:var(--mono); font-size:13px; color:var(--accent);
  background:var(--accent-soft); padding:3px 8px; border-radius:2px; flex:none;
}}
h3 {{
  font-family:var(--body); font-weight:650; font-size:16.5px; letter-spacing:-.005em;
  margin:34px 0 10px; color:var(--ink); scroll-margin-top:20px;
}}
p {{ margin:0 0 15px; max-width:70ch; }}
main ul {{ margin:0 0 16px; padding-left:22px; max-width:70ch; }}
main li {{ margin-bottom:7px; }}
strong {{ font-weight:650; color:var(--ink); }}
code {{
  font-family:var(--mono); font-size:.875em; background:var(--code-bg);
  padding:1.5px 5px; border-radius:3px; color:var(--ink);
}}
pre {{
  background:var(--surface-2); border:1px solid var(--rule);
  border-radius:4px; padding:16px 18px; overflow-x:auto; margin:0 0 20px;
}}
pre code {{ background:none; padding:0; font-size:12.8px; line-height:1.6; }}
.table-scroll {{
  overflow-x:auto; border:1px solid var(--rule); border-radius:4px;
  background:var(--surface); margin:0 0 22px;
}}
table {{ width:100%; border-collapse:collapse; font-size:14.5px; min-width:480px; }}
th {{
  text-align:left; font-family:var(--mono); font-weight:600; font-size:10.5px;
  letter-spacing:.08em; text-transform:uppercase; color:var(--muted);
  padding:11px 14px; border-bottom:1px solid var(--rule-strong); white-space:nowrap;
}}
td {{ padding:11px 14px; border-bottom:1px solid var(--rule); vertical-align:top; }}
tr:last-child td {{ border-bottom:none; }}
.callout {{
  background:var(--warn-soft); border-left:3px solid var(--warn);
  border-radius:0 3px 3px 0; padding:15px 18px; margin:0 0 22px;
  font-size:14.5px; color:var(--ink-2); max-width:70ch;
}}
.qa-q {{
  font-family:var(--display); font-size:18px; line-height:1.35; color:var(--ink);
  margin:32px 0 8px; padding-left:15px; border-left:3px solid var(--accent);
  max-width:66ch;
}}
.qa-q + p {{ margin-left:18px; color:var(--ink-2); }}
hr {{ border:none; border-top:1px solid var(--rule); margin:40px 0; }}
a {{ color:var(--accent); }}
:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
footer {{
  margin-top:64px; padding-top:20px; border-top:1px solid var(--rule);
  font-size:13px; color:var(--muted);
}}
@media (max-width:900px) {{
  .layout {{ grid-template-columns:1fr; gap:32px; }}
  nav {{
    position:static; max-height:none; background:var(--surface);
    border:1px solid var(--rule); border-radius:4px; padding:16px 18px;
  }}
  nav ol {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:2px; }}
}}
</style>

<div class="shell">
  <header class="masthead">
    <p class="eyebrow">LifeX Policy Assistant</p>
    <h1>Technical Documentation</h1>
    <p class="standfirst">
      How the system works, and why each decision was made that way. Current as at
      18 August 2026. Section 11 is a prepared answer bank for likely questions.
    </p>
  </header>

  <div class="layout">
    <nav aria-label="Contents">
      <p>Contents</p>
      <ol>{toc_html}</ol>
    </nav>
    <main>
      {''.join(body)}
      <footer>
        <p>Generated from <code>docs/Technical_Documentation.md</code> &mdash; edit that file and
        re-run <code>python scripts/build_technical_doc_html.py</code> to refresh this page.</p>
      </footer>
    </main>
  </div>
</div>
"""

# Escape every non-ASCII character to a numeric entity. The page carries no
# <meta charset> of its own (the artifact host supplies the document head),
# so opened as a local file a browser is free to guess the encoding and turn
# em-dashes and curly quotes into mojibake. Entities render identically
# whatever the browser decides the charset is.
page = page.encode("ascii", "xmlcharrefreplace").decode("ascii")

with open(OUT, "w", encoding="ascii") as f:
    f.write(page)
print("wrote", OUT, len(page), "bytes;", len(toc), "sections")
