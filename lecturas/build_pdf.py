#!/usr/bin/env python3
"""
build_pdf.py — Typeset a reading edition of the corpus as a PDF.

Converts the Markdown source into a printable PDF with a serif book face,
justified body text, running headers and page numbers.

    pip install reportlab
    python build_pdf.py                     # governing document + every built lectura
    python build_pdf.py 02                  # one lectura
    python build_pdf.py --input FILE.md --output FILE.pdf   # any file (e.g. the policy)
    python build_pdf.py --paper a4          # default: letter

Title, author and subtitle are read from the edition's front matter (corpus.py).

No network access and no external binaries required: reportlab is the only
dependency, and it ships the Type 1 base fonts used here. Those fonts cover
the full Latin-1 range, so Spanish accents, inverted punctuation and angle
quotes all render correctly.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        BaseDocTemplate,
        CondPageBreak,
        Frame,
        HRFlowable,
        PageBreak,
        PageTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
except ImportError:
    sys.exit(
        "reportlab is required.\n"
        "  pip install reportlab\n"
        "  (on Debian/Ubuntu system Python: pip install --break-system-packages reportlab)"
    )


# Spanish hyphenation is optional: ReportLab uses pyphen when it is installed.
# Without it the build still succeeds, with looser justified lines.
try:
    import pyphen  # noqa: F401
    HYPHENATION = "es_ES"
except ImportError:
    HYPHENATION = None

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus  # noqa: E402

# Filled per edition from its front matter by set_metadata(); never edit here.
TITLE = ""
AUTHOR = ""
SUBJECT = ""


def set_metadata(md: str) -> None:
    global TITLE, AUTHOR, SUBJECT
    fm = corpus.front_matter(md)
    TITLE = fm["title"] or "Edición de lectura"
    AUTHOR = fm["author"]
    SUBJECT = fm["subtitle"]


# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------

def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    s: dict[str, ParagraphStyle] = {}

    body_kw = {}
    if HYPHENATION:
        body_kw["hyphenationLang"] = HYPHENATION
        body_kw["embeddedHyphenation"] = 1
    s["body"] = ParagraphStyle(
        "body",
        parent=base["BodyText"],
        fontName="Times-Roman",
        fontSize=10.5,
        leading=15.5,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=7,
        firstLineIndent=0,
        **body_kw,
    )
    s["h1"] = ParagraphStyle(
        "h1",
        parent=s["body"],
        fontName="Times-Bold",
        fontSize=17,
        leading=21,
        alignment=TA_CENTER,
        spaceBefore=20,
        spaceAfter=12,
    )
    s["h2"] = ParagraphStyle(
        "h2",
        parent=s["body"],
        fontName="Times-Bold",
        fontSize=12.5,
        leading=16,
        alignment=TA_CENTER,
        spaceBefore=16,
        spaceAfter=9,
    )
    s["h3"] = ParagraphStyle(
        "h3",
        parent=s["body"],
        fontName="Times-Italic",
        fontSize=11.5,
        leading=15,
        alignment=TA_CENTER,
        spaceBefore=10,
        spaceAfter=8,
    )
    s["quote"] = ParagraphStyle(
        "quote",
        parent=s["body"],
        leftIndent=22,
        rightIndent=22,
        fontName="Times-Italic",
        spaceBefore=6,
        spaceAfter=8,
    )
    s["bullet"] = ParagraphStyle(
        "bullet",
        parent=s["body"],
        leftIndent=18,
        bulletIndent=6,
        spaceAfter=4,
    )
    s["cell"] = ParagraphStyle(
        "cell",
        parent=s["body"],
        fontSize=9,
        leading=12,
        alignment=0,
        spaceAfter=0,
    )
    s["cellhead"] = ParagraphStyle(
        "cellhead",
        parent=s["cell"],
        fontName="Times-Bold",
    )
    s["footnote"] = ParagraphStyle(
        "footnote",
        parent=s["body"],
        fontSize=8.2,
        leading=10.6,
        leftIndent=14,
        firstLineIndent=-9,
        textColor=colors.HexColor("#333333"),
        spaceBefore=1,
        spaceAfter=2,
    )
    return s


# --------------------------------------------------------------------------
# Inline markup: **bold**, *italic*, `code`
# --------------------------------------------------------------------------

def inline(text: str) -> str:
    """Translate a subset of Markdown inline markup into reportlab's mini-HTML."""
    # Escape XML metacharacters first so the source can contain < > &.
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.S)
    text = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+?)`", r'<font face="Courier">\1</font>', text)
    # Footnote reference: [^3] -> superscript 3
    text = re.sub(r"\[\^(\d+)\]", r"<super><font size=7>\1</font></super>", text)
    # Paragraph number: [§12] -> small grey marker at paragraph head
    text = re.sub(
        r"^\[§(\d+)\]\s*",
        r'<font size=7.5 color="#8a8a8a"><b>\1</b></font>&nbsp;&nbsp;',
        text,
    )
    return text


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_divider(line: str) -> bool:
    return bool(re.fullmatch(r"\|?[\s:|-]+\|?", line.strip())) and "-" in line


# --------------------------------------------------------------------------
# Markdown -> flowables
# --------------------------------------------------------------------------

def convert(md: str, styles: dict[str, ParagraphStyle], width: float) -> list:
    story: list = []
    lines = md.split("\n")
    i = 0
    first_heading = True

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            story.append(Spacer(1, 6))
            story.append(
                HRFlowable(width="60%", thickness=0.6, color=colors.HexColor("#999999"))
            )
            story.append(Spacer(1, 10))
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            text = inline(m.group(2))
            if level == 1:
                if not first_heading:
                    story.append(PageBreak())
                story.append(Paragraph(text, styles["h1"]))
                first_heading = False
            elif level == 2:
                story.append(Paragraph(text, styles["h2"]))
            else:
                story.append(Paragraph(text, styles["h3"]))
            i += 1
            continue

        # Table
        if stripped.startswith("|") and i + 1 < len(lines) and is_divider(lines[i + 1]):
            header = split_row(stripped)
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i].strip()))
                i += 1
            story.append(make_table(header, rows, styles, width))
            continue

        # Footnote definition: "^3: text"
        m = re.match(r"^\^(\d+):\s+(.*)$", stripped)
        if m:
            notes = []
            while i < len(lines):
                mm = re.match(r"^\^(\d+):\s+(.*)$", lines[i].strip())
                if not mm:
                    if not lines[i].strip():
                        i += 1
                        continue
                    break
                notes.append(
                    Paragraph(
                        f"<super><font size=6.5>{mm.group(1)}</font></super>&nbsp;"
                        + inline(mm.group(2)),
                        styles["footnote"],
                    )
                )
                i += 1
            block = [
                Spacer(1, 3),
                HRFlowable(
                    width="32%", thickness=0.5, color=colors.HexColor("#999999"),
                    hAlign="LEFT", spaceAfter=3,
                ),
                *notes,
                Spacer(1, 6),
            ]
            # Keep the notes on the same page as the paragraph that calls them.
            if story and isinstance(story[-1], Paragraph):
                story.append(CondPageBreak(2.2 * cm))
            story.extend(block)
            continue

        # Blockquote
        if stripped.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            story.append(Paragraph(inline(" ".join(buf)), styles["quote"]))
            continue

        # Bullet list
        if re.match(r"^[-*+]\s+", stripped):
            while i < len(lines) and re.match(r"^[-*+]\s+", lines[i].strip()):
                item = re.sub(r"^[-*+]\s+", "", lines[i].strip())
                story.append(
                    Paragraph(inline(item), styles["bullet"], bulletText="\u2022")
                )
                i += 1
            story.append(Spacer(1, 4))
            continue

        # Paragraph: gather until blank line or a new block starts
        buf = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or nxt.startswith(("#", ">", "|")) or re.match(r"^[-*+]\s+", nxt):
                break
            if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", nxt):
                break
            buf.append(nxt)
            i += 1
        story.append(Paragraph(inline(" ".join(buf)), styles["body"]))

    return story


def make_table(header, rows, styles, width) -> Table:
    ncols = max(len(header), max((len(r) for r in rows), default=1))

    def pad(row):
        return list(row) + [""] * (ncols - len(row))

    data = [[Paragraph(inline(c), styles["cellhead"]) for c in pad(header)]]
    for r in rows:
        data.append([Paragraph(inline(c), styles["cell"]) for c in pad(r)])

    col_width = width / ncols
    table = Table(data, colWidths=[col_width] * ncols, hAlign="CENTER", repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.HexColor("#444444")),
                ("LINEBELOW", (0, 1), (-1, -2), 0.25, colors.HexColor("#cccccc")),
                ("LINEBELOW", (0, -1), (-1, -1), 0.7, colors.HexColor("#444444")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
            ]
        )
    )
    return table


# --------------------------------------------------------------------------
# Page furniture
# --------------------------------------------------------------------------

class OutlineDoc(BaseDocTemplate):
    """BaseDocTemplate that turns headings into PDF bookmarks."""

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        name = flowable.style.name
        if name not in ("h1", "h2"):
            return
        text = re.sub(r"<[^>]+>", "", flowable.getPlainText()).strip()
        if not text:
            return
        key = f"sec-{self._bmseq}"
        self._bmseq += 1
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=0 if name == "h1" else 1, closed=0)
        self.notify("TOCEntry", (0 if name == "h1" else 1, text, self.page))


def decorate(canvas, doc):
    canvas.saveState()
    w, h = doc.pagesize
    n = canvas.getPageNumber()
    if n > 1:
        canvas.setFont("Times-Italic", 8.5)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawCentredString(w / 2.0, h - 1.5 * cm, f"{AUTHOR} \u2014 {TITLE}")
        canvas.setFont("Times-Roman", 9)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(w / 2.0, 1.4 * cm, str(n))
    canvas.restoreState()



def learner_text(md: str) -> str:
    """Rule 15: learner products carry no critical apparatus. The section from
    '# Aparato crítico' to the next top-level heading is replaced by a pointer."""
    import re as _re
    m = _re.search(r"^# Aparato crítico.*?(?=^# )", md, _re.M | _re.S)
    if not m:
        return md
    note = ("# Aparato crítico\n\nEsta versión para el estudio de la lengua no incluye el aparato crítico. "
            "El aparato completo —testimonios, enmiendas, divergencias y tabla de normalización— está en la "
            "edición en Markdown de la que este archivo se genera.\n\n")
    return md[:m.start()] + note + md[m.end():]

def build_file(src: Path, out: Path, paper: str) -> None:
    md = learner_text(src.read_text(encoding="utf-8"))
    set_metadata(md)
    pagesize = A4 if paper == "a4" else letter
    styles = build_styles()

    margins = dict(
        leftMargin=2.7 * cm,
        rightMargin=2.7 * cm,
        topMargin=2.4 * cm,
        bottomMargin=2.2 * cm,
    )
    doc = OutlineDoc(
        str(out),
        pagesize=pagesize,
        title=f"{TITLE} \u2014 {SUBJECT}" if SUBJECT else TITLE,
        author=AUTHOR,
        subject=SUBJECT,
        creator="build_pdf.py",
        invariant=1,   # fixed creation date and document ID: the same source gives the same bytes (release, MANIFEST.sha256)
        **margins,
    )
    doc._bmseq = 0
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="text",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=decorate)])

    story = convert(md, styles, doc.width)
    doc.build(story)
    doc.canv = None

    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Typeset Markdown editions as PDF.")
    ap.add_argument("lectura", nargs="*", help="number, slug or filename from corpus.json")
    ap.add_argument("--input", "-i", help="any Markdown file, if not in the manifest")
    ap.add_argument("--output", "-o")
    ap.add_argument("--paper", choices=["letter", "a4"], default="letter")
    args = ap.parse_args()

    if args.input:
        src = Path(args.input)
        if not src.exists():
            sys.exit(f"Input not found: {src}")
        build_file(src, Path(args.output or src.with_suffix(".pdf")), args.paper)
        return 0

    recs = corpus.lecturas()
    gov = corpus.ROOT / corpus.load_manifest().get("governing", "")
    if args.lectura:
        keys = [k for k in args.lectura if k != "00"]
        recs = [corpus.find(k) for k in keys]
        if any(r is None or not r.get("edition") for r in recs):
            sys.exit(f"Not a built lectura: {keys}")
        if "00" not in args.lectura:
            gov = None
    if gov and gov.exists():
        build_file(gov, gov.with_suffix(".pdf"), args.paper)
    for rec in recs:
        src = corpus.edition_path(rec)
        build_file(src, src.with_suffix(".pdf"), args.paper)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
