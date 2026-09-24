"""
Pilot: draft policy chunks directly from source PDFs using a vision-capable
LLM, instead of a human retyping tables by hand.

Why this is the "easier version" of the automation attempt that was tried
and scrapped earlier in this project: that attempt treated an LLM reading a
PDF as the risky fallback (only for scanned/checkmark-grid pages), because
the original chunking bug came from naive text-extraction scrambling a
table's column order before anyone — human or model — ever looked at it
(PyMuPDF's raw get_text() reading angle_interest_rates' multi-column layout
out of order). Rendering the page to an image and having a vision model
read it the way a human would never hits that failure mode at all — it's
reading the visual layout, not a scrambled text stream. This session's own
manual chunk audit (reading ~15 source PDFs directly and cross-checking
every number against the chunks) validated this: zero transcription errors
made that way, only pre-existing chunk errors caught.

This script does NOT touch data/chunks/ — it only ever writes to
data/chunks_draft/, and every draft must be manually reviewed against the
current chunk file before anything gets promoted. Nothing here is wired
into the live pipeline.

Usage:
    python scripts/draft_chunks.py ANGLE
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz
from openai import OpenAI

from src.config import OPENAI_API_KEY, PROJECT_ROOT
from src.ingest import VALID_LENDERS, VALID_INTENTS, parse_chunk_file
from scripts.table_geometry import describe_tables_on_page

CHUNKS_DRAFT_DIR = str(PROJECT_ROOT / "data" / "chunks_draft")
DOCUMENTS_DIR = str(PROJECT_ROOT / "data" / "documents")

# Vision-capable model for reading source PDFs. Kept as its own constant
# (distinct from LLM_MODEL in config.py, which answers broker questions)
# since this is a completely different job — document transcription, not
# policy Q&A — and may warrant a different model choice later.
VISION_MODEL = "gpt-5"

# Which source PDFs belong to which lender. Matches this session's manual
# audit — not derived automatically, since a lender's PDFs aren't named
# consistently enough to infer this reliably.
LENDER_SOURCE_PDFS = {
    "ANGLE": [
        "angle-finance-rate-card.pdf",
        "angle-start-up-flyer-jan.pdf",
        "full-doc-checklist_angle-finance.pdf",
        "prime-movers.pdf",
    ],
    "BFS": [
        "BFS Product Guide_260701_Broker.pdf",
    ],
}

_openai_client = OpenAI(api_key=OPENAI_API_KEY)

# A real, human-authored chunk (already verified word-for-word accurate
# against its own source PDF this session) given to the model as the one
# concrete example of the exact schema and style to reproduce — field
# names, the chunk-separator convention, and how a table becomes a
# markdown table plus a short prose note about how to read it.
FORMAT_EXAMPLE = """## chunk_id: angle_interest_rates
**source:** angle
**topic:** interest_rates
**intent:** PRICING
**lenders:** ANGLE
**borrower_profile:** COMMERCIAL, PROPERTY_BACKED, NON_PROPERTY_BACKED
**asset_class:** PRIMARY, SECONDARY, TERTIARY, PRIME_MOVER
**doc_type:** ALL
**loan_size_band:** ALL
**answerable_questions:** What rate does Angle charge for primary / secondary / tertiary assets by end-of-term age? What is the prime mover rate? What loadings apply? What has no rate loading?
**confidence:** high
**last_verified:** 2026-07-28
**trigger_words:** Angle rate, Angle interest rate, Angle pricing, Angle primary asset rate, Angle secondary rate, Angle tertiary rate, Angle prime mover rate, Angle rate loading, Angle property backed rate

**Content:**

Angle Finance Rate Card, April 2026 (Version 02.04.26). All rates per annum.

**Standard rate card -- for 2+ year ABN & 1+ year GST registration, by asset class, property status, and end-of-term (EOT) age:**

| Asset class | Owner status | 10 years (EOT) | 15 years (EOT) |
|------------|-------------|---------------|---------------|
| Primary assets | Property Owner | 8.39% | 9.65% |
| Primary assets | Non-Property Owner | 10.95% | 11.45% |

Read the row for the correct asset class AND the correct property-owner status -- these are two independent rows per asset class, not sub-bands of one row.
---
"""

SYSTEM_PROMPT = f"""You are transcribing a lender's policy PDF into a structured markdown chunk format for a RAG knowledge base. You will be shown page images from the actual PDF.

Rules, in order of importance:
1. Transcribe numbers, percentages, dollar amounts, ages, and thresholds EXACTLY as shown in the image. Never round, average, infer, or "clean up" a number. If a table cell says "Not available" or is blank, write exactly that -- never fill in a plausible-looking number.
1b. Pages that are visually dense with several similar-looking numbers near each other (e.g. multiple "500+" / "550+" / "600+" credit-score thresholds in different sections of the same page) are exactly where transcription mistakes happen -- before writing any such number down, re-locate it in the image and re-read the specific section/heading it sits under, rather than trusting your first impression of "a number near there."
2. Every table in the source becomes a markdown table with the same rows and columns -- do not collapse, merge, or reorder rows/columns.
3. If a value is directly under one column header in the image, it belongs to that column and no other -- double-check which row/column each number came from before writing it. This is the single most important rule: a number placed under the wrong column is the exact failure mode this process exists to avoid.
4. Split the document into one chunk per distinct topic (e.g. one chunk for rates, one for eligibility criteria, one for exclusions) rather than one giant chunk -- mirror how a human would naturally divide it.
5. Each chunk must have this exact field structure, separated by a line containing only "---":

## chunk_id: <lowercase_lender>_<topic>
**source:** <lowercase lender code>
**topic:** <short topic slug>
**intent:** <one of: {', '.join(sorted(VALID_INTENTS))}>
**lenders:** <one of: {', '.join(sorted(VALID_LENDERS))}>
**borrower_profile:** <comma-separated tags, your best judgment>
**asset_class:** <comma-separated tags, your best judgment>
**doc_type:** <comma-separated tags, your best judgment>
**loan_size_band:** <comma-separated tags, your best judgment>
**answerable_questions:** <2-4 example questions this chunk answers>
**confidence:** high
**last_verified:** 2026-07-28
**trigger_words:** <comma-separated search terms a broker might use>

**Content:**

<the actual transcribed policy content, as markdown tables and prose>

6. Do not invent an "intent" or "lenders" value outside the allowed lists above -- pick the closest correct one.
7. If a fact in the source is genuinely ambiguous or contradicts another part of the same document, transcribe both readings and flag the ambiguity explicitly in prose rather than silently picking one.
8. EVERY table and section in the source must produce a chunk, with no exceptions -- including tables with unusual merged/spanning cells, tables that look hard to parse, or a table you're genuinely unsure how to read. If a table's layout is confusing (e.g. a value appears to span multiple rows or columns, or a cell's meaning is unclear), still transcribe your best reading of every cell AND add a one-line note flagging exactly which cell you're uncertain about and why. Silently omitting a table because it's difficult is the single worst failure mode here -- worse than a flagged uncertain guess, because it deletes real information instead of just risking one wrong detail. Before finishing, re-check that every distinct table/section visible across all the page images has a corresponding chunk.
9. Whenever a "DETERMINISTIC TABLE STRUCTURE" block appears after a page image, it is a ground-truth extraction from that PDF page's actual vector line data (real divider lines, or their genuine absence) -- not a guess. It tells you exactly which cells are merged and what text is in each. Use it as the authoritative source for that table's structure and values, overriding your own visual impression of the image wherever the two disagree -- your own visual read of a merge/no-merge from pixels alone is exactly the failure mode this exists to correct. A row marked "MERGED" there means that one value applies to every row listed; write it into each of those rows in your markdown table, don't collapse it into just one.

Here is one real, verified-accurate example chunk showing the exact format to produce:

{FORMAT_EXAMPLE}

Now transcribe ALL the page images you are shown into this same format. Output ONLY the chunk markdown (starting with the first "## chunk_id:" line) -- no preamble, no explanation, no markdown code fences around the whole output."""


def _build_content_parts(lender_code: str, pdf_files: list[tuple[str, bytes]]) -> list[dict]:
    """pdf_files is a list of (filename, raw_pdf_bytes) -- decoupled from
    DOCUMENTS_DIR/LENDER_SOURCE_PDFS so callers (e.g. the /chunks/draft API
    endpoint) can pass in an arbitrary uploaded file, not just the
    pre-registered per-lender PDF set."""
    import base64

    content_parts = [{"type": "text", "text": f"Lender: {lender_code}. Source PDFs follow, in order."}]

    for filename, pdf_bytes in pdf_files:
        content_parts.append({"type": "text", "text": f"--- Document: {filename} ---"})
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))
            b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
            content_parts.append({"type": "text", "text": f"Page {i} of {filename}:"})
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"},
            })
            # Deterministic ground truth from the PDF's actual vector line
            # geometry -- which cells are genuinely merged, and what text
            # falls in each. See scripts/table_geometry.py's docstring for
            # why this exists: no vision model tested reliably told "merged
            # across 2 rows" apart from "merged across 3 rows" from pixels
            # alone, but PDF table borders are real line objects, so this
            # is checked with code instead of asked of the model.
            geometry = describe_tables_on_page(page, page_label=f"page {i} of {filename}")
            if geometry:
                content_parts.append({
                    "type": "text",
                    "text": (
                        "DETERMINISTIC TABLE STRUCTURE for the page above, extracted "
                        "directly from the PDF's own vector line data (not a guess -- "
                        "trust this over your own visual read of merges/dividers):\n"
                        + geometry
                    ),
                })

            # Exact digital text layer for this page. These PDFs have real
            # embedded text (not scans), so this is character-for-character
            # ground truth -- not an OCR guess and not subject to the visual
            # confusion that mixed up "500+" and "550+" on a dense Angle page
            # (two similar-looking figures near each other on the rendered
            # image). Reading order CAN scramble a genuinely tabular layout
            # (the original angle_interest_rates bug), so for tables prefer
            # the DETERMINISTIC TABLE STRUCTURE block above -- but for plain
            # prose/bullet text, this raw text is the more reliable source.
            raw_text = page.get_text().strip()
            if raw_text:
                content_parts.append({
                    "type": "text",
                    "text": (
                        f"EXACT DIGITAL TEXT of page {i} of {filename} (character-for-"
                        "character from the PDF itself, not OCR -- use this to verify "
                        "any specific number, threshold, or label before writing it "
                        "down, especially on a page with several similar-looking "
                        "figures near each other. Reading order may not reflect "
                        "column layout for genuine tables -- defer to the "
                        "DETERMINISTIC TABLE STRUCTURE block for those instead):\n"
                        + raw_text
                    ),
                })
        doc.close()

    return content_parts


def draft_chunks_from_pdfs(
    lender_code: str,
    pdf_files: list[tuple[str, bytes]],
    model: str = VISION_MODEL,
    reasoning_effort: str = None,
) -> str:
    """Core entry point, decoupled from disk paths. Takes raw PDF bytes
    directly so it can draft chunks from an arbitrary uploaded file (the
    /chunks/draft API endpoint) as well as the CLI's pre-registered,
    on-disk PDF sets (draft_chunks_for_lender below)."""
    content_parts = _build_content_parts(lender_code, pdf_files)

    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content_parts},
        ],
    }
    if model.startswith(("gpt-5", "o1", "o3", "o4")):
        kwargs["max_completion_tokens"] = 24000
        kwargs["reasoning_effort"] = reasoning_effort or "low"
    else:
        # gpt-4o family: no reasoning_effort param, uses max_tokens + temperature.
        kwargs["max_tokens"] = 8000
        kwargs["temperature"] = 0

    response = _openai_client.chat.completions.create(**kwargs)
    choice = response.choices[0]
    print(f"model={model} finish_reason={choice.finish_reason}, usage={response.usage}")

    # Refuse a truncated draft rather than returning it. finish_reason
    # "length" means the output hit the token cap mid-write, so the tail of
    # the draft is cut off -- but the VALID PREFIX still parses, and the
    # partial final chunk can look structurally complete (all schema fields
    # present, a Content section that simply stops early). That is the worst
    # shape this failure could take: a chunk that passes validation and gets
    # promoted with policy content silently missing from the end of it.
    # Better to fail loudly and have the operator split the PDF -- a missing
    # draft is recoverable, a quietly incomplete rate table is not.
    if choice.finish_reason == "length":
        raise ValueError(
            f"the model hit its {kwargs.get('max_completion_tokens') or kwargs.get('max_tokens')}-token "
            "output limit and the draft was cut off part-way through. Nothing was drafted, because a "
            "truncated draft can still look complete and would be unsafe to promote. Try splitting the "
            "PDF into smaller files (for example one section or rate card at a time) and uploading them "
            "separately."
        )
    # No second-pass merged-cell recheck needed anymore -- that was a
    # workaround for the model guessing at merges from pixels. Now that
    # scripts/table_geometry.py hands it the actual answer as deterministic
    # ground truth in the first pass, testing showed it gets every cell
    # right without a follow-up call (see BFS pilot, 2026-07-29).
    return choice.message.content or ""


def draft_chunks_for_lender(lender_code: str, model: str, reasoning_effort: str = None) -> str:
    pdf_files = []
    for filename in LENDER_SOURCE_PDFS[lender_code]:
        pdf_path = os.path.join(DOCUMENTS_DIR, filename)
        with open(pdf_path, "rb") as f:
            pdf_files.append((filename, f.read()))
    return draft_chunks_from_pdfs(lender_code, pdf_files, model, reasoning_effort)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in LENDER_SOURCE_PDFS:
        print(f"Usage: python scripts/draft_chunks.py <LENDER> [model] [reasoning_effort]")
        print(f"Available lenders: {', '.join(LENDER_SOURCE_PDFS)}")
        print(f"Example: python scripts/draft_chunks.py BFS gpt-5 minimal")
        print(f"Example: python scripts/draft_chunks.py BFS gpt-4o")
        sys.exit(1)

    lender_code = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else VISION_MODEL
    reasoning_effort = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Rendering and drafting chunks for {lender_code} from {len(LENDER_SOURCE_PDFS[lender_code])} PDF(s) using {model}"
          f"{' (' + reasoning_effort + ' effort)' if reasoning_effort else ''}...")
    draft_text = draft_chunks_for_lender(lender_code, model, reasoning_effort)

    os.makedirs(CHUNKS_DRAFT_DIR, exist_ok=True)
    suffix = f"_{model.replace('-', '')}" + (f"_{reasoning_effort}" if reasoning_effort else "")
    out_path = os.path.join(CHUNKS_DRAFT_DIR, f"{lender_code.lower()}_chunks_draft{suffix}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(draft_text)
    print(f"Draft written to {out_path}")

    warnings = []
    docs = parse_chunk_file(out_path, warnings)
    print(f"\nSchema validation: {len(docs)} chunk(s) parsed successfully.")
    if warnings:
        print(f"{len(warnings)} WARNING(S):")
        for w in warnings:
            print(f"  ! {w}")
    else:
        print("No validation warnings.")


if __name__ == "__main__":
    main()
