#!/usr/bin/env python3
"""
build_app.py — Assemble the standalone flashcard app.

Injects vocab.json into app_template.html and writes flashcards.html: one file,
no server, no network, no dependencies. Open it from disk, from VS Code's Live
Preview, from a USB stick, or from Google Drive.

    python extract_vocab.py && python build_app.py

Since 8.3 (2026-11-08) it also injects the grammar layer (decision 87): the
grammatical concepts and, per sentence, the function-word loci — a certified
locus with its concept and the character span of its stretch; a locus under
review as an offset only, so the hover can say «under review» without ever
showing the guess. Only certified loci become atom or stretch cards. The schema
is read beside this script since 8.4: `concepts.json` and `NN/senses.json` (exported from the workshop's ledger by
`work/research/2026-11-07-8.0-pilot/S3-export.py`; `--schema DIR` reads another folder in either layout).
Compact arrays keep the whole layer under 1 MB of the 10 MB budget.

Standard library only.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

MARKER = "/*__VOCAB_DATA__*/null"
GMARKER = "/*__GRAMMAR_DATA__*/null"
DEFAULT_SCHEMA = "."
WORD = re.compile(r"[^\W\d_][\w'’-]*", re.U)   # the trainer's WORD_RE: letters, no digits
FUSED = {("de", "el"): "del", ("a", "el"): "al"}


def words(s: str):
    return [(m.group(0).lower(), m.start(), m.end()) for m in WORD.finditer(s)]


def locate_run(toks, run: str, o: int):
    """Find the stretch `run` (space-separated tokens, fused forms split, enclitics stripped) in the sentence's
    word tokens and return the (start_char, end_char) of the occurrence that contains the locus offset `o`,
    or None (the latest-starting match that holds `o`, so the second of two *de* is not given the first's run). A sentence token matches when it equals a run token or the concatenation of two or three (vencerla ~
    vencer la), when it begins with that concatenation (aceptarla ~ aceptar), when it ends with the first run token
    (dirigirme ~ me …: the atom is an enclitic), when a `de el` / `a el` pair is its fused form, or when it is that
    fused form and the run token is its tail (del ~ … el). Numerals are not word tokens and are stepped over."""
    rt = [t.lower() for t in run.split()]
    if not rt:
        return None
    n = len(toks)
    best = None
    for i in range(n):
        j, k = i, 0
        while k < len(rt) and j < n:
            w = toks[j][0]
            if k + 1 < len(rt) and FUSED.get((rt[k], rt[k + 1])) == w:
                k += 2; j += 1; continue
            if w in FUSED.values() and rt[k] == "el":
                k += 1; j += 1; continue
            took = 0
            for m in (3, 2, 1):
                cat = "".join(rt[k:k + m])
                if k + m <= len(rt) and (w == cat or (w.startswith(cat) and len(w) > len(cat))):
                    took = m; break
            if took:
                k += took; j += 1; continue
            if k == 0 and w.endswith(rt[0]) and len(w) > len(rt[0]):
                k += 1; j += 1; continue
            break
        if k == len(rt) and toks[i][1] <= o < toks[j - 1][2]:
            best = (toks[i][1], toks[j - 1][2])   # the tightest match: the latest start that still holds the locus
    return best


def grammar_data(schema_dir: str, data: dict) -> dict:
    """Build the compact grammar layer from the schema folder.
    G: [[id, sense, class, en_form|null, en_kind|null], …]   grammatical concepts; index = reference
    L: { "<sentence index>": [[o, g, a, b], …] }            certified loci: offset, concept index, stretch span (a=b=-1: none)
    R: { "<sentence index>": [o, …] }                         loci under review: offsets only, never the guess
    """
    ledger = os.path.exists(os.path.join(schema_dir, "S-concepts.json"))   # the workshop's S/ layout, or vocab/'s
    cpath = os.path.join(schema_dir, "S-concepts.json" if ledger else "concepts.json")
    senses = sorted(glob.glob(os.path.join(schema_dir, "S-senses-*.json" if ledger else os.path.join("[0-9][0-9]", "senses.json"))))
    concepts = json.load(open(cpath, encoding="utf-8"))
    gl, gidx = [], {}
    for c in concepts["grammatical"]:
        en = (c.get("forms") or {}).get("en") or []
        gidx[c["id"]] = len(gl)
        gl.append([c["id"], c["sense"], c.get("class"), (en[0].get("form") if en else None), (en[0].get("realisation") if en else None)])
    sentences = data["sentences"]
    L, R = {}, {}
    unlocated = certified = 0
    tokcache = {}
    for f in senses:
        for l in json.load(open(f, encoding="utf-8"))["loci"]:
            s = l["s"]
            if l["status"] != "certified":
                R.setdefault(str(s), []).append(l["o"])
                continue
            certified += 1
            a = b = -1
            run = l.get("stretch")
            if run:
                toks = tokcache.get(s)
                if toks is None: toks = tokcache[s] = words(sentences[s])
                span = locate_run(toks, run, l["o"])
                if span:
                    a, b = span
                else:
                    unlocated += 1
            if l["c"] not in gidx:
                sys.exit(f"locus cites an unknown concept {l['c']!r} at sentence {s}")
            L.setdefault(str(s), []).append([l["o"], gidx[l["c"]], a, b])
    for k in L: L[k].sort()
    for k in R: R[k].sort()
    return {"schema": concepts.get("schema"), "G": gl, "L": L, "R": R,
            "counts": {"certified": certified, "review": sum(len(v) for v in R.values()),
                       "grammatical": len(gl), "unlocated_stretches": unlocated}}


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the standalone flashcard app.")
    ap.add_argument("--data", "-d", default="vocab.json")
    ap.add_argument("--template", "-t", default="app_template.html")
    ap.add_argument("--out", "-o", default="flashcards.html")
    ap.add_argument("--schema", "-s", default=DEFAULT_SCHEMA, help="folder with S-concepts.json and S-senses-NN.json")
    ap.add_argument("--grammar-out", default=None, help="also write the compact grammar layer as JSON (for inspection)")
    args = ap.parse_args()

    for f in (args.data, args.template):
        if not Path(f).exists():
            sys.exit(f"Not found: {f}. Run extract_vocab.py first.")
    if not (Path(args.schema, "concepts.json").exists() or Path(args.schema, "S-concepts.json").exists()):
        sys.exit(f"Schema not found at {args.schema}: no concepts.json. Export it (S3-export.py) or pass --schema.")

    data = Path(args.data).read_text(encoding="utf-8")
    tpl = Path(args.template).read_text(encoding="utf-8")
    for m in (MARKER, GMARKER):
        if m not in tpl:
            sys.exit(f"Template is missing the data marker {m!r}")

    parsed = json.loads(data)
    grammar = grammar_data(args.schema, parsed)
    gtext = json.dumps(grammar, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if args.grammar_out:
        Path(args.grammar_out).write_text(gtext, encoding="utf-8")

    # Guard against breaking out of the <script> element.
    safe = data.replace("</", "<\\/")
    gsafe = gtext.replace("</", "<\\/")
    html = tpl.replace(MARKER, safe).replace(GMARKER, gsafe)
    Path(args.out).write_text(html, encoding="utf-8")

    s = parsed["stats"]; gc = grammar["counts"]
    kb = Path(args.out).stat().st_size / 1024
    print(f"Wrote {args.out} ({kb:,.0f} KB, self-contained)")
    print(f"  {s['forms']:,} word forms · {s['defined']} with a definition · {len(parsed['sentences'])} sentences")
    print(f"  grammar layer: {gc['grammatical']} grammatical concepts · {gc['certified']:,} certified loci "
          f"· {gc['review']:,} under review · {len(gtext)/1024:,.0f} KB · stretches not located: {gc['unlocated_stretches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
