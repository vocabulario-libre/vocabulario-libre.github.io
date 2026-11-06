#!/usr/bin/env python3
"""
verify.py — Check the edition against its sources, and reconcile the results
against the critical apparatus.

Word counts catch gross truncation but not a dropped clause. So this script
looks for every run of N consecutive words in a source and reports the ones
absent from the edition — then does the part that used to be manual: it reads
the apparatus tables and works out which of those absences are already
recorded editorial decisions.

    python verify.py                                   # counts for every lectura
    python verify.py 05 --source correo.txt --source ayacucho.txt
    python verify.py --edition FILE.md --source copia1.txt

The lectura is named by number, slug or filename as listed in corpus.json;
with none given and no sources, every built lectura is counted. Sources are
plain-text files of a witness, kept outside the corpus (they are working
material, not deliverables).

Output separates three cases:

  EXPLAINED    the passage differs because of a reading recorded in the
               apparatus (§ II, § III or § VIII). Expected; no action.
  ORTHOGRAPHIC the passage matches once period spelling is normalized, using
               a short heuristic rule list (see PROVENANCE below). Usually
               needs no action, but is not a guarantee.
  UNEXPLAINED  content in a source that is neither in the edition nor
               accounted for anywhere. THESE ARE THE ONES TO INVESTIGATE.

Save each source as plain UTF-8, letter text only — strip headers, prologues
and footnotes or they will register as unexplained.

Matching is case-insensitive and accent-folded throughout, so that
modernization of spelling cannot masquerade as a difference in substance.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus  # noqa: E402

BODY_END = corpus.BODY_END
DEFAULT_N = 6

# Period spellings normalized under criterion 1, used only to decide whether an
# otherwise-unexplained difference is merely orthographic.
#
# PROVENANCE AND LIMITS. These rules were written from the manuscript
# transcription while collating; they are not a systematic description of
# period orthography and have not been validated against a reference grammar.
# A rule that is wrong in the permissive direction is the dangerous kind: it
# could file a real textual difference under ORTHOGRAPHIC and hide it. The list
# is therefore kept deliberately short, and rules the compiler could not vouch
# for were removed rather than guessed — a missing rule merely sends a passage
# to UNEXPLAINED, where it gets read. Treat ORTHOGRAPHIC as "probably spelling,
# still worth a glance", not as a clean bill.
ORTHO = [
    (r"\bmejic", "mexic"), (r"\bgoatemala\b", "guatemala"), (r"\bymper", "imper"),
    (r"\bynd", "ind"), (r"\byns", "ins"), (r"\bysla", "isla"), (r"\byst", "ist"),
    (r"\byntere", "intere"),
    (r"\breyno", "reino"), (r"\bvirreynato\b", "virreinato"), (r"\bayres\b", "aires"),
    (r"\bsetiembre\b", "septiembre"), (r"\bconcerv", "conserv"),
    (r"\bconceg", "conseg"), (r"\bconcec", "consec"), 
    (r"\bespres", "expres"), (r"\besten", "exten"), (r"\besclus", "exclus"),
    (r"\besact", "exact"), (r"\besces", "exces"), (r"\bespus", "expus"),
    (r"\bespon", "expon"), (r"\bestran", "extran"), (r"\bestraord", "extraord"),
    (r"\besterm", "exterm"), (r"\bespuls", "expuls"), 
    (r"\besepto\b", "excepto"), (r"\bimpocible\b", "imposible"),
    (r"\bpocible\b", "posible"), (r"\blejitim", "legitim"), (r"\bjeneral", "general"),
    (r"\bmagestuosa\b", "majestuosa"), (r"\bdies y seis\b", "dieciseis"),
    (r"\bdies y siete\b", "diecisiete"), (r"\bhavia\b", "habia"),
    (r"\bovedienc", "obedienc"), (r"\bdevo\b", "debo"), (r"\bbiolenta\b", "violenta"),
    (r"\besclavis", "esclaviz"), (r"\bhizieron\b", "hicieron"),
    (r"\bpadese\b", "padece"), (r"\bparese\b", "parece"), (r"\bdeside\b", "decide"),
    (r"\bamenasa\b", "amenaza"), (r"\briquesas\b", "riquezas"), (r"\bcapas\b", "capaz"),
    (r"\batros\b", "atroz"), (r"\bfelis\b", "feliz"), (r"\bquisa\b", "quiza"),
    (r"\bpaices\b", "paises"), (r"\bpricioner", "prisioner"), (r"\bpacion", "pasion"),
    (r"\bdivicion", "division"), (r"\bpocecion", "posesion"), (r"\bposecion", "posesion"),
    (r"\bmicion\b", "mision"), (r"\baucili", "auxili"), (r"\bacequible\b", "asequible"),
    (r"\baccequible\b", "asequible"), (r"\bcerbidumbre\b", "servidumbre"),
    (r"\beccist", "exist"), (r"\bnomades\b", "nomadas"),
    # generic orthographic classes (applied to both sides, so they only erase class differences)
    (r"g(?=[ei])", "j"),            # gefes/jefes, dirijía/dirigía, jeneral/general
    (r"y(?=[^aeiou\s]|\s|$)", "i"),  # Maracaybo/Maracaibo, muy/mui, rey/rei
    (r"\bfue\b", "fue"),
]


def fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9ñ\s]", " ", s)
    return " ".join(s.split())


def words(s: str) -> list[str]:
    return fold(s).split()


def orthonorm(s: str) -> str:
    for pat, rep in ORTHO:
        s = re.sub(pat, rep, s)
    return s


class Apparatus:
    """Readings recorded in the apparatus, loaded for reconciliation."""

    def __init__(self, md: str) -> None:
        self.variants: list[tuple[str, str]] = []
        if BODY_END not in md:
            return
        tail = md[md.index(BODY_END):]

        secs = [(m.group(0), f"§ {m.group(1)}") for m in
                re.finditer(r"^## ([IVX]+)\. (?:Correcciones|Divergencias)[^\n]*$", tail, re.M)]
        for sec, label in secs:
            block = tail[tail.index(sec):]
            nxt = block.find("\n## ", 4)
            block = block[:nxt] if nxt > 0 else block
            for num, rest in re.findall(r"^\|\s*(\d+)\s*\|(.+)$", block, re.M):
                for cell in rest.split("|"):
                    c = re.sub(r"\*+|`+|\[\?OCR\]|duda de digitalizacion|duda de digitalización", "", cell)
                    c = re.sub(r"\((?:\*\*)?[MYV].*?\)|\(.*?\)", "", c)
                    # A rejected-reading cell may hold several alternatives,
                    # e.g. "bey (Y); rey (V)" — each must be matchable alone.
                    for alt in re.split(r"[;/]", c):
                        f = fold(alt.strip(" ·"))
                        if f:
                            self.variants.append((f, f"{label} § {num}"))

        mnorm = re.search(r"^## [IVX]+\. Tabla de normalización.*$", tail, re.M)
        if mnorm:
            block = tail[mnorm.start():]
            nxt = block.find("\n## ", 4)
            block = block[:nxt] if nxt > 0 else block
            # Two shapes (2026-11-01, step 12/4): by place «| § | adoptado | impreso |…» and by form
            # «| antigua | moderna | clase | lugares |» (05, 13); in both the two forms are the first two text cells.
            pairs = []
            for line in block.split("\n"):
                if not line.startswith("|") or re.match(r"^\|\s*-", line): continue
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) < 3 or cells[0].lower() in ("§", "antigua", "impreso", "forma adoptada"): continue
                pairs.append((cells[1], cells[2]) if re.match(r"^[\d,\s]+$", cells[0]) else (cells[0], cells[1]))
            for adopted, ms in pairs:
                for form in (adopted, ms):
                    form = re.sub(r"\*+|\(.*?\)", "", form).strip()
                    for part in form.split("/"):
                        if fold(part):
                            self.variants.append((fold(part), "§ VIII"))

    MIN_LEN = 4   # a recorded reading shorter than this cannot by itself explain a passage

    def explains(self, passage: str) -> str | None:
        """A passage is explained only by a recorded reading matched as whole words,
        at least MIN_LEN characters long. Short readings (la/lo, de/a) must be
        recorded with a neighbouring word in the apparatus to be matchable."""
        p = " " + fold(passage) + " "
        best = None
        for reading, where in self.variants:
            if len(reading) < self.MIN_LEN:
                continue
            if (" " + reading + " ") in p:
                if best is None or len(reading) > best[0]:
                    best = (len(reading), where)
        return best[1] if best else None


def extract_body(md: str) -> str:
    body = corpus.body(md)
    body = re.sub(r"^#.*$|^-{3,}$|^\^\d+:.*$", "", body, flags=re.M)
    body = re.sub(r"\[§\d+\]|\[\^\d+\]", "", body)
    return body


def shingles(ws: list[str], n: int):
    return ((i, tuple(ws[i : i + n])) for i in range(len(ws) - n + 1))


def check(ed_words, source_text, name, n, app):
    ed_set = {s for _, s in shingles(ed_words, n)}
    ed_ortho = {tuple(orthonorm(" ".join(s)).split()) for s in ed_set}
    src = words(source_text)

    missing = [i for i, sh in shingles(src, n) if sh not in ed_set]
    if not missing:
        print(f"\n  {name}: complete. Every {n}-word run appears in the edition.")
        return 0, 0, 0

    runs: list[list[int]] = [[missing[0]]]
    for i in missing[1:]:
        runs[-1].append(i) if i - runs[-1][-1] <= n else runs.append([i])

    # OCR splits a word across a line ("sis tema") or joins two ("decíanlos"); a
    # passage whose letters, with spaces removed, occur in the edition's letters is
    # a segmentation difference, declared by class, not a textual one.
    ed_joined = orthonorm(" ".join(ed_words)).replace(" ", "")

    buckets = {"EXPLAINED": [], "ORTHOGRAPHIC": [], "SEGMENTATION": [], "UNEXPLAINED": []}
    for run in runs:
        lo, hi = run[0], run[-1] + n
        snippet = " ".join(src[lo:hi])
        where = app.explains(snippet)
        norm = orthonorm(snippet).split()
        ortho_ok = any(
            tuple(norm[k : k + n]) in ed_ortho for k in range(max(1, len(norm) - n + 1))
        )
        seg_ok = (not where and not ortho_ok and len(norm) >= n
                  and orthonorm(snippet).replace(" ", "") in ed_joined)
        if where:
            buckets["EXPLAINED"].append(f"[{lo:>5}] {where:<14} {snippet[:88]}")
        elif seg_ok:
            buckets["SEGMENTATION"].append(f"[{lo:>5}] {snippet[:88]}")
        elif ortho_ok:
            buckets["ORTHOGRAPHIC"].append(f"[{lo:>5}] {snippet[:88]}")
        else:
            buckets["UNEXPLAINED"].append(f"[{lo:>5}] {snippet[:110]}")

    print(f"\n  {name}: {len(runs)} passage(s) differ from the edition.")
    for label in ("UNEXPLAINED", "EXPLAINED", "SEGMENTATION", "ORTHOGRAPHIC"):
        rows = buckets[label]
        if not rows:
            continue
        print(f"\n    {label} ({len(rows)})")
        show = rows if label == "UNEXPLAINED" else rows[:8]
        for r in show:
            print(f"      {r}")
        if len(rows) > len(show):
            print(f"      … and {len(rows) - len(show)} more")

    return len(buckets["EXPLAINED"]), len(buckets["ORTHOGRAPHIC"]), len(buckets["UNEXPLAINED"])


def source_text(raw: str) -> str:
    """A span file is witness text plus the pipeline's own markers (added 2026-11-01, step 12/3 d, for 05's
    `work/05/A-span.md`): item headings «## Item N · pieza N · A pp. …», HTML comments with the item's metadata,
    page marks «[p. NN]» and the file's title line. They are not the witness's words and are dropped before the
    comparison; everything else is kept as it stands."""
    return "\n".join(t for _, t in source_items("", raw))


def source_items(name: str, raw: str) -> list[tuple[str, str]]:
    """Split a span file at its item headings, one source per item, so that a shingle running from the end of one
    piece into the head of the next is not reported as a passage the edition lacks (the edition separates the pieces
    with their own headings). A plain witness file has no headings and comes back whole."""
    items: list[tuple[str, list[str]]] = [(name, [])]
    for line in raw.split("\n"):
        t = line.strip()
        if re.match(r"^## Item \d", t) or (t.startswith("<!--") and t.endswith("-->")) or re.match(r"^\[p\. ?\d+[a-z]?\]$", t) \
                or re.match(r"^# \d\d — span", t):
            if t.startswith("## Item"):
                items.append((f"{name} · {t[3:].split(' · A')[0].strip()}", []))
            continue
        items[-1][1].append(re.sub(r"^\[§\d+\]\s*", "", line))  # a built text's paragraph markers are not words
    return [(n, "\n".join(ls)) for n, ls in items if "".join(ls).strip()]


def report(md: str, label: str, sources: list[tuple[str, str]], window: int) -> int:
    ed_words = words(extract_body(md))
    app = Apparatus(md)
    print(f"\n==== {label}")
    print("COUNTS")
    paras = len(re.findall(r"\[§\d+\]", md))
    print(f"  {'edition (text only)':<28} {len(ed_words):>6,} words   {paras:>3} paragraphs")
    print(f"  {'apparatus readings loaded':<28} {len(app.variants):>6}")
    for name, t in sources:
        print(f"  {name:<28} {len(words(t)):>6,} words")
    if not sources:
        return 0
    print("\nCONTENT CHECK")
    unexplained = 0
    for name, text in sources:
        _, _, u = check(ed_words, text, name, window, app)
        unexplained += u
    print()
    if unexplained == 0:
        print("PASS: every difference is accounted for by the apparatus or by "
              "declared orthographic modernization.")
        return 0
    print(f"REVIEW: {unexplained} unexplained passage(s). Each is either content "
          "missing from the edition or a decision that was never recorded.")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify an edition against its sources.")
    ap.add_argument("lectura", nargs="?", help="number, slug or filename from corpus.json")
    ap.add_argument("--edition", "-e", help="edition file, if not in the manifest")
    ap.add_argument("--source", "-s", action="append", default=[])
    ap.add_argument("--window", "-n", type=int, default=DEFAULT_N)
    args = ap.parse_args()

    sources = []
    for s in args.source:
        p = Path(s)
        if not p.exists():
            print(f"  ! not found, skipping: {p}")
            continue
        sources.extend(source_items(p.name, p.read_text(encoding="utf-8")))

    if args.edition:
        path = Path(args.edition)
        if not path.exists():
            sys.exit(f"Edition not found: {path}")
        return report(path.read_text(encoding="utf-8"), path.name, sources, args.window)

    if args.lectura:
        rec = corpus.find(args.lectura)
        if not rec or not rec.get("edition"):
            sys.exit(f"Not a built lectura in corpus.json: {args.lectura}")
        return report(corpus.read_edition(rec), f"{rec['n']} · {rec['title']}", sources, args.window)

    if sources:
        sys.exit("Name the lectura the sources belong to: verify.py 02 --source FILE")
    rc = 0
    for rec in corpus.lecturas():
        rc |= report(corpus.read_edition(rec), f"{rec['n']} · {rec['title']}", [], args.window)
    print("\nNo sources supplied; counts only. Add --source FILE.txt with a lectura "
          "to run the content check.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
