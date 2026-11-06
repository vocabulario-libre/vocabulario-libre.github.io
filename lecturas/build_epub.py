#!/usr/bin/env python3
"""
build_epub.py — Produce a reflowable EPUB from the Markdown edition.

Companion to build_pdf.py. Same source file, same content; the EPUB reflows for
phones and e-readers, where the fixed-page PDF reads poorly.

    python build_epub.py                       # governing document + every built lectura
    python build_epub.py 02                    # one lectura
    python build_epub.py --input FILE.md --output FILE.epub

Title and author are read from the edition's front matter (see corpus.py).

No dependencies beyond the standard library: an EPUB is a ZIP archive of XHTML,
and zipfile ships with Python. Nothing is downloaded and nothing is installed.

Structure produced:
    - one chapter per level-1 heading, so the reading text, the apparatus,
      the source notes, the glossary and the reference key are separate
      chapters a reader can jump between
    - a navigation document (EPUB 3) plus an NCX (EPUB 2 readers)
    - paragraph numbers rendered as small grey markers, as in the PDF
    - footnotes rendered inline beneath the paragraph that calls them
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus  # noqa: E402

# Filled per edition from its front matter by set_metadata(); never edit here.
TITLE = ""
AUTHOR = ""
LANG = "es"


def set_metadata(md: str) -> None:
    global TITLE, AUTHOR
    fm = corpus.front_matter(md)
    TITLE, AUTHOR = fm["title"] or "Edición de lectura", fm["author"] or ""

CSS = """\
body { font-family: Georgia, 'Times New Roman', serif; line-height: 1.55;
       margin: 0 0.6em; text-align: justify; hyphens: auto; }
h1 { font-size: 1.45em; text-align: center; margin: 1.4em 0 0.8em; line-height: 1.25; }
h2 { font-size: 1.15em; text-align: center; margin: 1.3em 0 0.6em; }
h3 { font-size: 1em; font-style: italic; text-align: center; margin: 1em 0 0.5em;
     font-weight: normal; }
p { margin: 0 0 0.65em; text-indent: 0; }
hr { border: 0; border-top: 1px solid #bbb; width: 50%; margin: 1.4em auto; }
blockquote { margin: 0.8em 1.4em; font-style: italic; }
.pnum { font-size: 0.72em; color: #8a8a8a; font-weight: bold;
        vertical-align: baseline; padding-right: 0.45em; }
.fnref { font-size: 0.7em; vertical-align: super; }
.fnotes { font-size: 0.82em; color: #333; margin: 0.5em 0 1em;
          border-top: 1px solid #ccc; padding-top: 0.4em; }
.fnotes p { margin: 0 0 0.3em 1.1em; text-indent: -1.1em; text-align: left; }
table { border-collapse: collapse; width: 100%; font-size: 0.8em; margin: 0.9em 0; }
th { text-align: left; border-bottom: 1.2px solid #444; padding: 0.3em 0.4em;
     background: #f2f2f2; }
td { border-bottom: 1px solid #ddd; padding: 0.3em 0.4em; vertical-align: top; }
ul { margin: 0.5em 0 0.8em 1.2em; padding: 0; }
li { margin-bottom: 0.3em; }
"""


# ---------------------------------------------------------------------------
# Markdown -> XHTML (same subset build_pdf.py handles)
# ---------------------------------------------------------------------------

def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text, flags=re.S)
    text = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[\^(\d+)\]", r'<span class="fnref">\1</span>', text)
    text = re.sub(r"^\[§(\d+)\]\s*", r'<span class="pnum">\1</span>', text)
    return text


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_divider(line: str) -> bool:
    return bool(re.fullmatch(r"\|?[\s:|-]+\|?", line.strip())) and "-" in line


def convert(lines: list[str]) -> str:
    out: list[str] = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue

        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", s):
            out.append("<hr/>")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            lvl = min(len(m.group(1)), 3)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        m = re.match(r"^\^(\d+):\s+(.*)$", s)
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
                    f'<p><span class="fnref">{mm.group(1)}</span> '
                    f"{inline(mm.group(2))}</p>"
                )
                i += 1
            out.append('<div class="fnotes">' + "".join(notes) + "</div>")
            continue

        if s.startswith("|") and i + 1 < len(lines) and is_divider(lines[i + 1]):
            head = split_row(s)
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i].strip()))
                i += 1
            t = ["<table><tr>"]
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr>")
            for r in rows:
                r = r + [""] * (len(head) - len(r))
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</table>")
            out.append("".join(t))
            continue

        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(buf))}</p></blockquote>")
            continue

        if re.match(r"^[-*+]\s+", s):
            items = []
            while i < len(lines) and re.match(r"^[-*+]\s+", lines[i].strip()):
                items.append(
                    "<li>" + inline(re.sub(r"^[-*+]\s+", "", lines[i].strip())) + "</li>"
                )
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue

        buf = [s]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (
                not nxt
                or nxt.startswith(("#", ">", "|", "^"))
                or re.match(r"^[-*+]\s+", nxt)
                or re.fullmatch(r"-{3,}|\*{3,}|_{3,}", nxt)
            ):
                break
            buf.append(nxt)
            i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")

    return "\n".join(out)


def chapterize(md: str) -> list[tuple[str, str]]:
    """Split on level-1 headings; return [(title, xhtml_body), ...]."""
    lines = md.split("\n")
    marks = [n for n, l in enumerate(lines) if re.match(r"^# [^#]", l)]
    if not marks or marks[0] > 0:
        marks = [0] + marks
    chapters = []
    for idx, start in enumerate(marks):
        end = marks[idx + 1] if idx + 1 < len(marks) else len(lines)
        block = lines[start:end]
        title = next(
            (re.sub(r"^#+\s*", "", l) for l in block if re.match(r"^#{1,3} ", l)),
            TITLE,
        )
        title = re.sub(r"[*`]", "", title).strip()
        chapters.append((title, convert(block)))
    return chapters


# ---------------------------------------------------------------------------
# EPUB container
# ---------------------------------------------------------------------------

def xhtml(title: str, body: str) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        f'xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="{LANG}">\n'
        f"<head><title>{html.escape(title)}</title>"
        '<meta charset="utf-8"/>'
        '<link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
        f"<body>\n{body}\n</body>\n</html>\n"
    )


def build(md: str, out_path: str) -> int:
    chapters = chapterize(md)
    # Deterministic: the identifier is derived from the source text and the stamp is the latest date the source
    # states (its Historial / Estado line), so the same source gives the same bytes (release, MANIFEST.sha256).
    uid = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, md)}"
    dates = re.findall(r"\b(20\d\d-\d\d-\d\d)\b", md)
    stamp = (max(dates) if dates else "2026-01-01") + "T00:00:00Z"
    zdate = tuple(int(x) for x in stamp[:10].split("-")) + (0, 0, 0)
    files = [(f"ch{n:02d}.xhtml", t, b) for n, (t, b) in enumerate(chapters, 1)]

    manifest = "\n".join(
        f'    <item id="ch{n:02d}" href="{f}" media-type="application/xhtml+xml"/>'
        for n, (f, _, _) in enumerate(files, 1)
    )
    spine = "\n".join(f'    <itemref idref="ch{n:02d}"/>' for n in range(1, len(files) + 1))

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{uid}</dc:identifier>
    <dc:title>{TITLE}</dc:title>
    <dc:creator>{AUTHOR}</dc:creator>
    <dc:language>{LANG}</dc:language>
    <dc:rights>Texto en dominio público. Aparato y notas bajo CC0 1.0.</dc:rights>
    <dc:description>Edición de lectura para estudio personal. No es edición crítica.</dc:description>
    <meta property="dcterms:modified">{stamp}</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="css" href="style.css" media-type="text/css"/>
{manifest}
  </manifest>
  <spine toc="ncx">
{spine}
  </spine>
</package>
"""

    nav_items = "\n".join(
        f'      <li><a href="{f}">{html.escape(t)}</a></li>' for f, t, _ in files
    )
    nav = xhtml(
        "Índice",
        f'<nav epub:type="toc" id="toc"><h1>Índice</h1>\n<ol>\n{nav_items}\n</ol></nav>',
    )

    ncx_points = "\n".join(
        f'    <navPoint id="n{n}" playOrder="{n}">'
        f"<navLabel><text>{html.escape(t)}</text></navLabel>"
        f'<content src="{f}"/></navPoint>'
        for n, (f, t, _) in enumerate(files, 1)
    )
    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="{uid}"/></head>
  <docTitle><text>{TITLE}</text></docTitle>
  <navMap>
{ncx_points}
  </navMap>
</ncx>
"""

    with zipfile.ZipFile(out_path, "w") as z:
        _writestr = z.writestr
        def writestr(name, data, compress_type=zipfile.ZIP_DEFLATED):   # fixed entry dates, same reason
            zi = zipfile.ZipInfo(name, date_time=zdate); zi.compress_type = compress_type
            _writestr(zi, data)
        z.writestr = writestr
        # mimetype must be first and stored uncompressed
        z.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr(
            "META-INF/container.xml",
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<container version="1.0" '
            'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
            '  <rootfiles><rootfile full-path="OEBPS/content.opf" '
            'media-type="application/oebps-package+xml"/></rootfiles>\n'
            "</container>\n",
            zipfile.ZIP_DEFLATED,
        )
        z.writestr("OEBPS/content.opf", opf, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/toc.ncx", ncx, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, zipfile.ZIP_DEFLATED)
        for fname, title, body in files:
            z.writestr(f"OEBPS/{fname}", xhtml(title, body), zipfile.ZIP_DEFLATED)

    return len(files)



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

def build_file(src: Path, out: Path) -> None:
    md = learner_text(src.read_text(encoding="utf-8"))
    set_metadata(md)
    n = build(md, str(out))
    print(f"Wrote {out} ({out.stat().st_size:,} bytes, {n} chapters)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build EPUBs from the Markdown editions.")
    ap.add_argument("lectura", nargs="*", help="number, slug or filename from corpus.json")
    ap.add_argument("--input", "-i", help="edition file, if not in the manifest")
    ap.add_argument("--output", "-o")
    args = ap.parse_args()

    if args.input:
        src = Path(args.input)
        if not src.exists():
            sys.exit(f"Input not found: {src}")
        build_file(src, Path(args.output or src.with_suffix(".epub")))
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
        build_file(gov, gov.with_suffix(".epub"))
    for rec in recs:
        src = corpus.edition_path(rec)
        build_file(src, src.with_suffix(".epub"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
