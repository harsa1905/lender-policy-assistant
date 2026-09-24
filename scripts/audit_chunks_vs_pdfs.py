"""
Audit every chunk's figures against the lender's actual source PDFs.

For each lender: pull all text out of its source PDFs (the embedded digital
text layer, plus the deterministic table-cell text from
scripts/table_geometry.py where the page has ruled tables), then pull every
rate and dollar figure out of that lender's chunks, and report any chunk
figure that does not appear anywhere in the sources.

This is a REVIEW REPORT, not an auto-fixer. A flagged figure is not
automatically wrong -- chunks legitimately contain derived values (a rate
build-up's total), values quoted from a superseded card alongside a change
note, and figures written in a different format from the PDF. The point is
to produce a short, checkable list rather than to re-read 25 PDFs by hand.

KNOWN FALSE POSITIVE -- READ BEFORE "CORRECTING" A CHUNK. This audit reads
the PDF text layer, so any figure that lives inside an EMBEDDED IMAGE is
invisible to it and will be flagged as missing even when it is plainly
there. This is not hypothetical: it flagged metro_interest_rates' $91,661
MetroEco EV cap as unsourced, and that figure turned out to be printed in a
green graphic box on page 1 of the rate sheet -- the chunk was right and the
audit was wrong. The per-lender table below reports how many images each
lender's PDFs contain precisely so a flag against an image-heavy source is
treated as "go and look at the page" rather than as evidence of an error.
Render the page (fitz get_pixmap) and read it before changing any chunk.

Usage:
    python scripts/audit_chunks_vs_pdfs.py            # summary
    python scripts/audit_chunks_vs_pdfs.py --full     # every flagged figure
"""
import argparse
import os
import re
import sys
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz
from src.config import PROJECT_ROOT
from src.ingest import split_chunk_blocks
from scripts.table_geometry import describe_tables_on_page

DOCS = str(PROJECT_ROOT / "data" / "documents")
CHUNKS = str(PROJECT_ROOT / "data" / "chunks")

# Which source PDFs belong to which lender. Taken from each chunk file's own
# header block, which names its source documents -- not guessed from
# filenames. Two documents are deliberately listed under two lenders:
# CFAL and Westpac genuinely share the Key Financial Policies and the
# Settlement Requirements update.
LENDER_PDFS = {
    "angle": ["angle-finance-rate-card.pdf", "angle-start-up-flyer-jan.pdf",
              "full-doc-checklist_angle-finance.pdf", "prime-movers.pdf"],
    "bfs": ["BFS Product Guide_260701_Broker.pdf"],
    "cfal": ["CreditMinimumCreditDocumentsChecklist.pdf",
             "Key Financial Policies_Q1FY26_25022026.pdf",
             "UPDATEDEquipmentFinanceSettlementRequirements.pdf"],
    "flexi": ["FCAU_flexicommercial Rate Card_13 July 2026.pdf",
              "FCAU_flexicommercial Credit Matrix_8 December 2025.pdf",
              "FC_AU_flexireplacementPolicy_August20241.pdf",
              "Flexi Premium Low Start Loans Fact Sheet.pdf",
              "Mid Term Refinancing Fact Sheet.pdf",
              "Old Finance Meets New Fact Sheet.pdf"],
    "metro": ["Commercial_Rate_Sheet_20072026.pdf", "MetroEco_Booklet_1905.pdf",
              "Metro_Finance_Agri_Streamlined_Product_R1_copy.pdf",
              "Metro_Finance_Balloon_Residual_Refinance_Streamlined_Product_R1.pdf",
              "Metro_Finance_Other_Equipment_Streamlined_Product_R1.pdf",
              "Metro_Finance_Passenger_Vehicle_Streamlined_Product_R1_copy.pdf",
              "Metro_Finance_Replacement_Policy_Streamlined_Product_R1.pdf",
              "Metro_Finance_Trucks_Trailers_amp_Wheeled_Equipment_Streamlined_Product_R1.pdf"],
    "resimac": ["Resimac-Commercial Asset Finance Rates and Product Guide.pdf"],
    "westpac": ["Key Financial Policies_Q1FY26_25022026.pdf",
                "Westpac Rate Chart 13072026.pdf",
                "Westpac Rate Chart 13072026 Xpress Only.pdf",
                "UPDATEDEquipmentFinanceSettlementRequirements.pdf"],
}

CHUNK_FILE = {
    "angle": "angle_chunks.md", "bfs": "bfs_chunks_v2.md", "cfal": "cfal_chunks_v2.md",
    "flexi": "flexi_chunks.md", "metro": "metro_chunks.md",
    "resimac": "resimac_chunks_v2.md", "westpac": "westpac_chunks_v2.md",
}

PCT = re.compile(r"\b(\d{1,2}\.\d{1,2})\s*%")
DOLLAR = re.compile(r"\$\s?([\d,]{3,})")


def source_text(lender):
    """Digital text layer plus deterministic table-cell text, per PDF.

    Also returns how many embedded images the lender's PDFs contain -- see
    the module docstring: figures printed inside an image are invisible here
    and produce false 'missing from source' flags.
    """
    parts = []
    n_images = 0
    for name in LENDER_PDFS[lender]:
        path = os.path.join(DOCS, name)
        if not os.path.exists(path):
            parts.append(f"[MISSING PDF: {name}]")
            continue
        doc = fitz.open(path)
        for i, page in enumerate(doc, 1):
            n_images += len(page.get_images())
            parts.append(page.get_text())
            geo = describe_tables_on_page(page, f"{name} p{i}")
            if geo:
                parts.append(geo)
        doc.close()
    return "\n".join(parts), n_images


def figures(text):
    """Normalised rate and dollar figures. Percentages keep 2dp so 7.15 and
    7.150 compare equal; dollars drop separators so $91,387 == 91387."""
    pcts = {f"{float(m):.2f}%" for m in PCT.findall(text)}
    dollars = {m.replace(",", "") for m in DOLLAR.findall(text)}
    return pcts, dollars


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="list every flagged figure, not just counts")
    args = ap.parse_args()

    grand = defaultdict(list)
    print(f"{'lender':<9} {'chunks':>6} {'src %':>6} {'src $':>6} {'flag %':>7} {'flag $':>7} {'imgs':>5}")
    for lender in sorted(LENDER_PDFS):
        src, n_images = source_text(lender)
        src_p, src_d = figures(src)

        path = os.path.join(CHUNKS, CHUNK_FILE[lender])
        _, blocks, order = split_chunk_blocks(open(path, encoding="utf-8").read())

        flag_p = flag_d = 0
        for cid in order:
            body = blocks[cid]
            cp, cd = figures(body)
            miss_p = sorted(cp - src_p)
            miss_d = sorted(cd - src_d, key=lambda x: -int(x))
            flag_p += len(miss_p); flag_d += len(miss_d)
            if miss_p or miss_d:
                grand[lender].append((cid, miss_p, miss_d))
        warn = "  <- image-heavy: flags may be false" if n_images and (flag_p or flag_d) else ""
        print(f"{lender:<9} {len(order):>6} {len(src_p):>6} {len(src_d):>6} {flag_p:>7} {flag_d:>7} {n_images:>5}{warn}")

    print("\n" + "=" * 78)
    print("FIGURES PRESENT IN A CHUNK BUT NOT FOUND IN THAT LENDER'S SOURCE PDFs")
    print("=" * 78)
    print("Not automatically errors -- derived totals, deliberately-recorded superseded")
    print("values, and format differences all land here. Check before changing anything.\n")
    for lender, rows in grand.items():
        print(f"--- {lender} ---")
        for cid, mp, md in rows:
            if not args.full and not mp:
                continue  # summary mode: rates matter most
            bits = []
            if mp: bits.append("rates " + ", ".join(mp))
            if md: bits.append("$ " + ", ".join(md[:6]) + (" ..." if len(md) > 6 else ""))
            print(f"  {cid:<42} {' | '.join(bits)}")
        print()


if __name__ == "__main__":
    main()
