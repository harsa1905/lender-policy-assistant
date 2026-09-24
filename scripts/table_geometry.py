"""
Deterministic table-structure extraction from a PDF page's actual vector
line data -- built after finding that an LLM (across 6 different model/
config combinations) could not reliably tell "this cell is merged across
2 rows" apart from "merged across 3 rows" from pixels alone on a real
BFS rate table. PDF table borders are usually drawn as literal thin
filled rectangles (line segments), not just visual style -- so whether a
divider exists between two rows in a specific column is something code
can check exactly, instead of something a vision model has to guess.

This does NOT try to fully replace the LLM drafting step. It produces a
structured, human-readable report of every detected table's row/column
boundaries and merged cells, which gets fed to the LLM alongside the page
images as ground truth to read from -- turning "guess whether this is
merged" into "here's what's actually merged, transcribe accordingly."

KNOWN LIMITATION -- tables drawn as filled blocks are not detected.
This finds tables whose borders are STROKED (thin filled rects acting as
line segments). Some rate cards draw no strokes at all: every cell is a
filled rectangle and the "border" is just where two fills meet. Measured
2026-08-19: the Angle rate card has 98 drawings, all filled, yielding 0
horizontal and 1 vertical line; the Westpac rate chart, 26 drawings and
likewise nothing. Both return "" here -- and they are two of the most
rate-critical documents in the corpus.

Deriving grid lines from those blocks' EDGES was tried and REVERTED, not
left undone. It does find grids, but the wrong ones: gated only on size it
produced a 31x40 "table" of almost entirely empty cells on the Angle card;
gated additionally on cells containing text it still produced 19x22 with
negative coordinates, and on the Westpac chart it collapsed a rate table
into one column reading "Term 48 Months Term 60 Months Term 24-36 Months
9.97% 9.97% 10.17%" -- term-to-rate association destroyed, which is the
exact failure this module exists to prevent. Since the drafting prompt
tells the model to trust this output OVER its own reading of the page,
plausible-but-wrong structure is worse than no output: with none, the model
reads the rendered image, which it does correctly on these cards today.

If revisiting: the bar is recovering true column structure, not merely
detecting that a grid exists. Text-column clustering (x-positions of text
spans) is likely a better signal than block edges.

Usage as a library: `describe_tables_on_page(page) -> str`
"""
import fitz


def _is_thin_rect(rect, max_thickness=2.0, min_length=15.0):
    """A vector-drawn line segment is rendered as a very thin filled rect.
    Returns ('h', length) for a horizontal line, ('v', length) for
    vertical, or None if this rect isn't line-like."""
    w, h = rect.x1 - rect.x0, rect.y1 - rect.y0
    if h <= max_thickness and w >= min_length:
        return ("h", w)
    if w <= max_thickness and h >= min_length:
        return ("v", h)
    return None


def _cluster(values, tol=2.5):
    """Group nearby numbers together (e.g. y-coordinates that are all
    "the same" row boundary but off by sub-pixel rendering differences)."""
    values = sorted(values)
    clusters = []
    for v in values:
        if clusters and v - clusters[-1][-1] <= tol:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    return [sum(c) / len(c) for c in clusters]


def _extract_grid_lines(page):
    h_lines = []  # (y_center, x0, x1)
    v_lines = []  # (x_center, y0, y1)
    for d in page.get_drawings():
        kind = _is_thin_rect(d["rect"])
        if kind is None:
            continue
        r = d["rect"]
        if kind[0] == "h":
            h_lines.append(((r.y0 + r.y1) / 2, r.x0, r.x1))
        else:
            v_lines.append(((r.x0 + r.x1) / 2, r.y0, r.y1))
    return h_lines, v_lines


def _find_tables(h_lines, v_lines, min_rows=3, min_cols=2):
    """Group grid lines into distinct tables by spatial proximity, then
    derive row/column boundaries for each. Deliberately simple (bounding
    box clustering, not a general layout engine) -- good enough to find
    the kind of ruled tables these policy PDFs actually use.
    """
    all_segments = [("h", y, x0, x1) for y, x0, x1 in h_lines] + \
                   [("v", x, y0, y1) for x, y0, y1 in v_lines]
    if not all_segments:
        return []

    def bbox(seg):
        kind = seg[0]
        if kind == "h":
            _, y, x0, x1 = seg
            return fitz.Rect(x0, y - 1, x1, y + 1)
        _, x, y0, y1 = seg
        return fitz.Rect(x - 1, y0, x + 1, y1)

    boxes = [bbox(s) for s in all_segments]
    n = len(boxes)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        pi, pj = find(i), find(j)
        if pi != pj:
            parent[pi] = pj

    expanded = [fitz.Rect(b) + (-3, -3, 3, 3) for b in boxes]
    for i in range(n):
        for j in range(i + 1, n):
            if expanded[i].intersects(expanded[j]):
                union(i, j)

    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(all_segments[i])

    tables = []
    for segs in groups.values():
        h_segs = [(y, x0, x1) for kind, y, x0, x1 in segs if kind == "h"]
        v_segs = [(x, y0, y1) for kind, x, y0, y1 in segs if kind == "v"]
        row_ys = _cluster([y for y, _, _ in h_segs])
        col_xs = _cluster([x for x, _, _ in v_segs])
        if len(row_ys) < min_rows or len(col_xs) < min_cols:
            continue
        tables.append({
            "row_ys": sorted(row_ys),
            "col_xs": sorted(col_xs),
            "h_segs": h_segs,
            "v_segs": v_segs,
        })
    return tables


def _divider_present_for_column(h_segs, row_y, col_x0, col_x1, y_tol=3.0, coverage=0.6):
    """Does a horizontal divider actually span this specific column's
    x-range at this row boundary? Requires the line to cover most of the
    column width, not just clip its edge."""
    needed = (col_x1 - col_x0) * coverage
    covered = 0.0
    for y, x0, x1 in h_segs:
        if abs(y - row_y) > y_tol:
            continue
        overlap = min(x1, col_x1) - max(x0, col_x0)
        if overlap > 0:
            covered += overlap
    return covered >= needed


def _cell_text(page, rect):
    text = page.get_textbox(rect).strip()
    return " ".join(text.split())


def describe_tables_on_page(page: fitz.Page, page_label: str = "") -> str:
    """Return a plain-text, deterministic description of every ruled
    table on this page: row/column boundaries, per-column merge
    detection, and the extracted text for each resulting cell (already
    combined across any merged rows). Empty string if no ruled tables
    are found (most pages in these PDFs are checklists/prose, not grids).
    """
    h_lines, v_lines = _extract_grid_lines(page)
    tables = _find_tables(h_lines, v_lines)
    if not tables:
        return ""

    out = []
    for t_idx, table in enumerate(tables, 1):
        row_ys, col_xs = table["row_ys"], table["col_xs"]
        n_rows, n_cols = len(row_ys) - 1, len(col_xs) - 1
        if n_rows < 2 or n_cols < 1:
            continue

        # For each column, walk down the row boundaries and merge any
        # consecutive rows where THIS column's divider is missing (even
        # though the table overall has a row boundary there, evidenced by
        # other columns having a divider at that y).
        merge_report = [f"Table {t_idx} on {page_label}: {n_rows} data rows x {n_cols} columns."]
        col_cells = []  # per column: list of (row_start_idx, row_end_idx, text)
        for c in range(n_cols):
            col_x0, col_x1 = col_xs[c], col_xs[c + 1]
            row_start = 0
            spans = []
            for boundary_idx in range(1, n_rows):
                boundary_y = row_ys[boundary_idx]
                has_divider = _divider_present_for_column(
                    table["h_segs"], boundary_y, col_x0, col_x1
                )
                if has_divider:
                    spans.append((row_start, boundary_idx - 1))
                    row_start = boundary_idx
            spans.append((row_start, n_rows - 1))
            col_cells.append(spans)

        for c, spans in enumerate(col_cells):
            col_x0, col_x1 = col_xs[c], col_xs[c + 1]
            for (r0, r1) in spans:
                y0, y1 = row_ys[r0], row_ys[r1 + 1]
                rect = fitz.Rect(col_x0, y0, col_x1, y1)
                text = _cell_text(page, rect)
                row_label = f"row {r0+1}" if r0 == r1 else f"rows {r0+1}-{r1+1} (MERGED -- one value spanning all these rows, not separate per-row values)"
                merge_report.append(f"  Column {c+1} ({col_x0:.0f}-{col_x1:.0f}pt), {row_label}: \"{text}\"")

        out.append("\n".join(merge_report))

    return "\n\n".join(out)


if __name__ == "__main__":
    import sys
    doc = fitz.open(sys.argv[1])
    page_num = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    print(describe_tables_on_page(doc[page_num], page_label=f"page {page_num + 1}"))
