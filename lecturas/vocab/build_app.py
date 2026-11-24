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
FMARKER = "/*__FONT_FACE__*/"
FONT_FAMILY = "av"                           # the name the trainer's own style gives the font it carries for the Avestan letters
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


FORMS_SCHEMA = "vocabulario-forms/2"          # 2: a realisation said in words stands in `said`, not in `form`
CARD_LANGS = ("ja", "ru", "de", "sa", "ae")   # the languages a lectura's forms.json writes


def fold_forms(concepts: dict, stretches: dict, vocab_dir) -> list:
    """Write the forms of every NN/forms.json under `vocab_dir` into the schema, in place. Returns what does not fit,
    one line each; an empty list when everything does.

    NN/forms.json is the source of a lectura's forms in the languages of the cards. Each unit of it goes where the
    schema keeps its kind:
      a word     its lexical concept — a unit {es, gloss, t, lemma[, note]} in `units`, and in forms[language] the
                 word's form as the file has it, with the same `es` and `t`;
      an atom    its grammatical concept — a unit {t[, where][, note]} in `units`, and in forms[language] its
                 realisation as the file has it, with that `t`;
      a stretch  its record among the stretches — `forms`, by language, English among them.
    `t` is the lectura that wrote the unit. A word with its gloss is written once, at the first lectura that has it.
    Whatever stood in these places is cleared first, so a second fold changes nothing."""
    bad: list = []
    lex: dict = {}
    twice = set()
    for c in concepts["lexical"]:
        if c["id"] in lex:
            twice.add(c["id"])
        lex.setdefault(c["id"], c)
        c.pop("units", None)
        for L in CARD_LANGS:
            c["forms"][L] = []
    gram = {c["id"]: c for c in concepts["grammatical"]}
    for c in concepts["grammatical"]:
        c.pop("units", None)
        for L in CARD_LANGS:
            c["forms"][L] = None
    runs = {(s["t"], s["s"], s["run"]): s for s in stretches["stretches"]}
    for s in stretches["stretches"]:
        s.pop("forms", None)
    written: dict = {}
    for path in sorted(Path(vocab_dir).glob("[0-9][0-9]/forms.json")):
        t = path.parent.name
        d = json.loads(path.read_text(encoding="utf-8"))
        if d.get("schema") != FORMS_SCHEMA or d.get("lectura") != t:
            bad.append(f"{t}/forms.json: not the forms of lectura {t} in {FORMS_SCHEMA}")
            continue
        langs = [L for L in CARD_LANGS if L in d.get("languages", [])]
        for w, x in d.get("words", {}).items():
            where = f"{t}/forms.json, «{w}»"
            c = lex.get(x.get("concept"))
            if c is None:
                bad.append(f"{where}: no lexical concept {x.get('concept')!r}"); continue
            if c["id"] in twice:
                bad.append(f"{where}: the id {c['id']} names two concepts"); continue
            if not any(f["form"] == w and t in f["source"] for f in c["forms"]["es"]):
                bad.append(f"{where}: {c['id']} does not hold this word from lectura {t}"); continue
            if x.get("gloss") not in c.get("senses_seen", []):
                bad.append(f"{where}: its gloss is not one of {c['id']}"); continue
            if not x.get("lemma") or any(not isinstance(x.get(L), dict) for L in langs):
                bad.append(f"{where}: no dictionary form, or a language without a form or a declared absence"); continue
            key = (c["id"], w, x["gloss"])
            if key in written:
                bad.append(f"{where}: this word with this gloss is written at lectura {written[key]} already"); continue
            written[key] = t
            unit = {"es": w, "gloss": x["gloss"], "t": t, "lemma": x["lemma"]}
            if x.get("note"):
                unit["note"] = x["note"]
            c.setdefault("units", []).append(unit)
            for L in langs:
                c["forms"][L].append({"es": w, "t": t, **x[L]})
        for cid, x in d.get("atoms", {}).items():
            where = f"{t}/forms.json, {cid}"
            c = gram.get(cid)
            if c is None:
                bad.append(f"{where}: no grammatical concept of this id"); continue
            if x.get("sense") != c["sense"]:
                bad.append(f"{where}: its sense is not the concept's"); continue
            if any(not isinstance(x.get(L), dict) for L in langs):
                bad.append(f"{where}: a language without a realisation or a declared absence"); continue
            unit = {"t": t}
            for k in ("where", "note"):
                if x.get(k):
                    unit[k] = x[k]
            c.setdefault("units", []).append(unit)
            for L in langs:
                c["forms"][L] = (c["forms"][L] or []) + [{"t": t, **x[L]}]
        for s in d.get("stretches", []):
            where = f"{t}/forms.json, stretch «{s.get('run')}» (sentence {s.get('s')})"
            r = runs.get((t, s.get("s"), s.get("run")))
            if r is None:
                bad.append(f"{where}: not a stretch of lectura {t}"); continue
            if "forms" in r:
                bad.append(f"{where}: translated twice"); continue
            if any(not isinstance(s.get(L), dict) for L in ["en"] + langs):
                bad.append(f"{where}: a language without a translation or a declared absence"); continue
            r["forms"] = {L: s[L] for L in ["en"] + langs}
    for c in concepts["lexical"] + concepts["grammatical"]:
        if "units" in c:
            c["units"].sort(key=lambda u: (u["t"], u.get("es", "")))
            for L in CARD_LANGS:
                if c["forms"][L]:
                    c["forms"][L].sort(key=lambda f: (f["t"], f.get("es", "")))
    return bad


def card_form(f: dict) -> dict:
    """A form, a realisation or a declared absence as the trainer carries it: short keys, and no key that says nothing.
    x absence, with its reason · k kind of realisation · rule · f form · sd what realises it, said in words, where it is no form
    of the language · r reading · d dictionary form · dr its reading ·
    t tier, where it is not 1 · g grade · s the form in its own script · u 1: not yet cited · c where it is cited ·
    src the word a loan or a derivation comes from; for a derived form, w = [[source word, every outcome, the rows that
    changed a letter], …], ds the source of the dictionary form, do its outcomes where there are two."""
    if "absent" in f:
        return {"x": f["absent"]}
    o = {}
    if f.get("realisation"):
        o["k"] = f["realisation"]
    if f.get("rule"):
        o["rule"] = f["rule"]
    if f.get("form"):
        o["f"] = f["form"]
    if f.get("said"):
        o["sd"] = f["said"]
    if f.get("reading") and f["reading"] != f.get("form"):
        o["r"] = f["reading"]
    if f.get("dict"):
        o["d"] = f["dict"]
        if f.get("dict_reading") and f["dict_reading"] != f["dict"]:
            o["dr"] = f["dict_reading"]
    if f.get("tier", 1) != 1:
        o["t"] = f["tier"]
    if f.get("grade"):
        o["g"] = f["grade"]
    if f.get("script"):
        o["s"] = f["script"]
    if "words" in f:
        o["src"] = f["source"]
        o["w"] = [[w["source"], w["outcomes"], [r for r in w["rows"] if r[0] != "="]] for w in f["words"]]
        if f.get("dict_source"):
            o["ds"] = f["dict_source"]
        if len(f.get("dict_outcomes") or []) > 1:
            o["do"] = f["dict_outcomes"]
    elif f.get("source"):
        o["src"] = f["source"]
    if f.get("cited"):
        o["c"] = f["cited"]
    elif f.get("uncited"):
        o["u"] = 1
    return o


def forms_data(concepts: dict, stretches: dict, gidx: dict, span_of: dict, data: dict, atoms_of: dict) -> dict:
    """The forms of the languages of the cards, from the schema as folded.
    langs: the languages, in the order of every list `f` below
    W: { "<word>\t<gloss>": {t, f: [form, …][, n: note]} }                    a word with its gloss, wherever it stands
    A: { "<concept index>": [{t, f: [realisation, …][, w: where][, n]}, …] }   a grammatical concept, by the lectura that wrote it
    S: { "<sentence index>": { "<a>:<b>": {en: form, f: [form, …]} } }         a stretch, by its span in the sentence
    T: { "<lectura>": [language, …] }   the lecturas whose forms are made, each with the languages in which every unit of it — every
       glossed word that is not a function word, every grammatical concept certified in it, every stretch — has its form or a declared absence"""
    W, A, S, lost = {}, {}, {}, []
    carried = lambda f: card_form(f) if f else None        # None: a language the lectura's file does not write
    for c in concepts["lexical"]:
        for u in c.get("units", []):
            e = {"t": u["t"], "f": [carried(next((f for f in c["forms"][L] if f["es"] == u["es"] and f["t"] == u["t"]), None)) for L in CARD_LANGS]}
            if u.get("note"):
                e["n"] = u["note"]
            W[u["es"] + "\t" + u["gloss"]] = e
    for c in concepts["grammatical"]:
        for u in c.get("units", []):
            e = {"t": u["t"], "f": [carried(next((f for f in (c["forms"][L] or []) if f["t"] == u["t"]), None)) for L in CARD_LANGS]}
            if u.get("where"):
                e["w"] = u["where"]
            if u.get("note"):
                e["n"] = u["note"]
            A.setdefault(str(gidx[c["id"]]), []).append(e)
    for s in stretches["stretches"]:
        if "forms" not in s:
            continue
        span = span_of.get((s["s"], s["run"]))
        if not span:
            lost.append(f"lectura {s['t']}, sentence {s['s']}, «{s['run']}»")
            continue
        S.setdefault(str(s["s"]), {})[f"{span[0]}:{span[1]}"] = {"en": card_form(s["forms"]["en"]), "f": [carried(s["forms"].get(L)) for L in CARD_LANGS]}
    if lost:
        sys.exit("a translated stretch is not found in its sentence, so no card would show it: " + "; ".join(lost))
    # the lecturas that are made: every unit of the lectura is asked for, as a card would ask
    units: dict = {}
    excluded = {(x[0], x[1]) for x in concepts.get("excluded", [])}
    for e in data["entries"]:
        if (e.get("en") or "").strip() and not e["fn"] and (e["t"], e["w"]) not in excluded:
            units.setdefault(e["t"], []).append(W.get(e["w"] + "\t" + e["en"]))
    for t, gs in atoms_of.items():
        for g in sorted(gs):
            us = A.get(str(g), [])
            units.setdefault(t, []).append(next((u for u in us if u["t"] == t), None) or next((u for u in us if not u.get("w")), None))
    for s in stretches["stretches"]:
        span = span_of.get((s["s"], s["run"]))
        units.setdefault(s["t"], []).append(S.get(str(s["s"]), {}).get(f"{span[0]}:{span[1]}") if span else None)
    T = {}
    for t, us in sorted(units.items()):
        langs = [L for i, L in enumerate(CARD_LANGS) if us and all(u is not None and u["f"][i] is not None for u in us)]
        if langs:
            T[t] = langs
    return {"langs": list(CARD_LANGS), "W": W, "A": A, "S": S, "T": T}


def _dump(x) -> str:
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def grammar_data(schema_dir: str, data: dict) -> dict:
    """Build the compact grammar layer from the schema folder.
    G: [[id, sense, class, en_form|null, en_kind|null], …]   grammatical concepts; index = reference
    L: { "<sentence index>": [[o, g, a, b], …] }            certified loci: offset, concept index, stretch span (a=b=-1: none)
    R: { "<sentence index>": [o, …] }                         loci under review: offsets only, never the guess
    F: the forms of the languages of the cards (forms_data)
    In vocab/'s layout the forms of every NN/forms.json are folded into the schema first (fold_forms), and concepts.json
    and stretches.json are written again where that changed them: change a lectura's forms.json, build, and the trainer
    and the schema both have it.
    """
    ledger = os.path.exists(os.path.join(schema_dir, "S-concepts.json"))   # the workshop's S/ layout, or vocab/'s
    cpath = os.path.join(schema_dir, "S-concepts.json" if ledger else "concepts.json")
    spath = os.path.join(schema_dir, "S-stretches.json" if ledger else "stretches.json")
    senses = sorted(glob.glob(os.path.join(schema_dir, "S-senses-*.json" if ledger else os.path.join("[0-9][0-9]", "senses.json"))))
    ctext, stext = Path(cpath).read_text(encoding="utf-8"), Path(spath).read_text(encoding="utf-8")
    concepts, stretches = json.loads(ctext), json.loads(stext)
    if not ledger:
        unfit = fold_forms(concepts, stretches, schema_dir)
        if unfit:
            sys.exit("the forms do not fit the schema — nothing is built:\n  " + "\n  ".join(unfit))
        for path, old, new in ((cpath, ctext, _dump(concepts)), (spath, stext, _dump(stretches))):
            if new != old:
                Path(path).write_text(new, encoding="utf-8")
                print(f"  {os.path.basename(path)}: written again from the lecturas' forms")
    gl, gidx = [], {}
    for c in concepts["grammatical"]:
        en = (c.get("forms") or {}).get("en") or []
        gidx[c["id"]] = len(gl)
        gl.append([c["id"], c["sense"], c.get("class"), (en[0].get("form") if en else None), (en[0].get("realisation") if en else None)])
    sentences = data["sentences"]
    L, R = {}, {}
    span_of, atoms_of = {}, {}
    unlocated = certified = 0
    tokcache = {}
    for f in senses:
        doc = json.load(open(f, encoding="utf-8"))
        for l in doc["loci"]:
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
                    span_of[(s, run)] = span
                else:
                    unlocated += 1
            if l["c"] not in gidx:
                sys.exit(f"locus cites an unknown concept {l['c']!r} at sentence {s}")
            L.setdefault(str(s), []).append([l["o"], gidx[l["c"]], a, b])
            atoms_of.setdefault(doc["text"], set()).add(gidx[l["c"]])
    for k in L: L[k].sort()
    for k in R: R[k].sort()
    F = forms_data(concepts, stretches, gidx, span_of, data, atoms_of)
    return {"schema": concepts.get("schema"), "G": gl, "L": L, "R": R, "F": F,
            "counts": {"certified": certified, "review": sum(len(v) for v in R.values()),
                       "grammatical": len(gl), "unlocated_stretches": unlocated,
                       "forms": {"words": len(F["W"]), "atoms": sum(len(v) for v in F["A"].values()), "stretches": sum(len(v) for v in F["S"].values())}}}


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the standalone flashcard app.")
    ap.add_argument("--data", "-d", default="vocab.json")
    ap.add_argument("--template", "-t", default="app_template.html")
    ap.add_argument("--out", "-o", default="flashcards.html")
    ap.add_argument("--schema", "-s", default=DEFAULT_SCHEMA, help="folder with S-concepts.json and S-senses-NN.json")
    ap.add_argument("--grammar-out", default=None, help="also write the compact grammar layer as JSON (for inspection)")
    ap.add_argument("--font", default=None,
                    help="a .woff2 for the Avestan letters (default: the one .woff2 in the folder above, where there is one); "
                         "without a font the trainer shows transliteration alone")
    args = ap.parse_args()

    for f in (args.data, args.template):
        if not Path(f).exists():
            sys.exit(f"Not found: {f}. Run extract_vocab.py first.")
    if not ((Path(args.schema, "concepts.json").exists() and Path(args.schema, "stretches.json").exists())
            or (Path(args.schema, "S-concepts.json").exists() and Path(args.schema, "S-stretches.json").exists())):
        sys.exit(f"Schema not found at {args.schema}: no concepts.json with its stretches.json. Export it (S3-export.py) or pass --schema.")

    data = Path(args.data).read_text(encoding="utf-8")
    tpl = Path(args.template).read_text(encoding="utf-8")
    for m in (MARKER, GMARKER, FMARKER):
        if m not in tpl:
            sys.exit(f"Template is missing the data marker {m!r}")

    parsed = json.loads(data)
    grammar = grammar_data(args.schema, parsed)
    face = ""
    beside = sorted(Path("..").glob("*.woff2"))
    font = args.font or (str(beside[0]) if len(beside) == 1 else "")
    if font and Path(font).exists():   # one font, inline: the file's own bytes, for the Avestan block alone
        import base64
        face = ('@font-face{font-family:"' + FONT_FAMILY + '";src:url(data:font/woff2;base64,' + base64.b64encode(Path(font).read_bytes()).decode("ascii")
                + ') format("woff2");unicode-range:U+10B00-10B3F}\n.av{font-family:"' + FONT_FAMILY + '",serif;font-size:calc(1em*var(--av,1))}')
    grammar["F"]["font"] = bool(face)
    gtext = json.dumps(grammar, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if args.grammar_out:
        Path(args.grammar_out).write_text(gtext, encoding="utf-8")

    # Guard against breaking out of the <script> element.
    safe = data.replace("</", "<\\/")
    gsafe = gtext.replace("</", "<\\/")
    html = tpl.replace(MARKER, safe).replace(GMARKER, gsafe).replace(FMARKER, face)
    Path(args.out).write_text(html, encoding="utf-8")

    s = parsed["stats"]; gc = grammar["counts"]
    kb = Path(args.out).stat().st_size / 1024
    print(f"Wrote {args.out} ({kb:,.0f} KB, self-contained)")
    print(f"  {s['forms']:,} word forms · {s['defined']} with a definition · {len(parsed['sentences'])} sentences")
    print(f"  grammar layer: {gc['grammatical']} grammatical concepts · {gc['certified']:,} certified loci "
          f"· {gc['review']:,} under review · {len(gtext)/1024:,.0f} KB · stretches not located: {gc['unlocated_stretches']}")
    fc = gc["forms"]
    print(f"  forms in {' '.join(CARD_LANGS)}: {fc['words']} words · {fc['atoms']} grammatical concepts · {fc['stretches']} stretches"
          f" · the Avestan font: {'inline' if face else 'not in the folder — transliteration alone'}"
          f" · lecturas made: {', '.join(t + ' (' + ' '.join(v) + ')' for t, v in grammar['F']['T'].items()) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
