#!/usr/bin/env python3
"""
extract_vocab.py — Build the vocabulary dataset for the whole corpus.

Reads every built lectura listed in ../corpus.json and emits vocab.json: for
each text, every distinct word form the author used, with the sentences it
appears in, its paragraph locators, its frequency, and a definition where the
edition has one. Each text is its own corpus: the same form may be glossed
differently in two texts, because glosses follow the sense in that text.

    python extract_vocab.py                 # all built lecturas
    python extract_vocab.py --only 02       # one, for a quick rebuild

Per-lectura meaning files live in NN/ (e.g. 02/glosses.json, 02/definitions.json).
A lectura with no such directory is included with contexts but no meanings;
the app shows those cards as "sin equivalencia".

Standard library only. The output is embedded into flashcards.html by
build_app.py, so the app needs no server and no network.

WHAT IS AND IS NOT INCLUDED
  - Word forms as they actually occur. No lemmatization: a reader meets
    *conservamos*, not *conservar*, and the card should show what the page
    shows. Forms are grouped into families by a crude shared-stem heuristic,
    used for browsing only and labelled as such.
  - Two kinds of meaning, both written for this project and copied from no
    dictionary: a short English equivalent for every form (glosses.json), and
    a fuller Spanish definition for the words that need one (definitions.json).
  - Sentences are Bolívar's, public domain.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import corpus  # noqa: E402

BODY_END = corpus.BODY_END

# The editorial half of the edition: apparatus, source notes, chronology,
# reference key and glossary. Its Spanish is modern descriptive prose, a
# different register from Bolívar's, so it forms a separate corpus rather
# than being mixed into his vocabulary.
EDITORIAL_SECTIONS = [
    ("# Aparato crítico", "# Notas sobre las fuentes"),
    ("# Notas sobre las fuentes", "# Bibliografía"),
    ("## Cronología", "## Personas"),
    ("# Referencias del texto", "# Glosario"),
    ("# Glosario", "# Historial de revisiones"),
]

# Very common function words: kept in the data (they appear in contexts) but
# flagged so the app can exclude them from study by default.
FUNCTION = set("""
el la los las un una unos unas lo al del de a en y e o u que se su sus me te
le les nos os por para con sin sobre entre hasta desde según tras durante
no ni ya más mas muy tan como cuando donde quien quienes cual cuales cuyo
cuya cuyos cuyas es son era eran fue fueron ser sido siendo está están
estaba estaban ha han había habían he hemos hay haber si sí pero aunque
porque pues aun también tanto tal tales este esta estos estas ese esa esos
esas aquel aquella aquellos aquellas mi mis tu tus nuestro nuestra nuestros
nuestras yo él ella ellos ellas usted vd nosotros se lo la
""".split())


def fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def load_paragraphs(md: str) -> dict[int, str]:
    return corpus.paragraphs(md)


def load_glossary(md: str) -> dict[str, str]:
    """Definitions written for this edition. Nothing here is copied."""
    if "# Glosario" not in md:
        return {}
    gl = md[md.index("# Glosario") :]
    gl = gl[: gl.index("\n# ")] if "\n# " in gl[5:] else gl
    defs = {}
    for entry, rest in re.findall(r"^\*\*(.+?)\*\*(.*?)$", gl, re.M):
        body_txt = rest.split("·", 1)[-1].strip() if "·" in rest else ""
        if not body_txt:
            continue
        for form in re.sub(r"[*]", "", entry).split("/"):
            form = form.replace("pl.", "").strip().lower()
            if form and " " not in form:
                defs[form] = body_txt
    return defs


def load_names(md: str) -> dict[str, str]:
    """Proper nouns identified in the reference key, for the 'nombres' deck."""
    if "# Referencias del texto" not in md:
        return {}
    sec = md[md.index("# Referencias del texto") :]
    sec = sec[: sec.index("\n# ")] if "\n# " in sec[5:] else sec
    out = {}
    for head, rest in re.findall(r"^\*\*(.+?)\*\*(?:[^—]*?)—\s*(.+?)$", sec, re.M):
        head = re.sub(r"[*†]|\(.*?\)", "", head).strip()
        if head and len(head.split()) <= 4:
            out[head.lower()] = re.sub(r"\s+", " ", rest).strip()
    return out


def load_editorial(md: str) -> list[str]:
    """Paragraphs of the edition's own prose, for the editorial corpus."""
    out = []
    for start, end in EDITORIAL_SECTIONS:
        if start not in md or end not in md:
            continue
        block = md[md.index(start) : md.index(end)]
        for para in block.split("\n\n"):
            t = para.strip()
            if (not t or t.startswith(("#", "|", ">", "^", "---", "**§"))
                    or t.startswith("- ") or len(t) < 60):
                continue
            t = re.sub(r"[*`]|\[\^?\d+\]|§ ?\d+", "", t)
            t = re.sub(r"\s+", " ", t).strip()
            if len(t) > 60:
                out.append(t)
    return out


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[¿¡«A-ZÁÉÍÓÚÑ])", text)
    return [p.strip() for p in parts if p.strip()]


def family_key(word: str) -> str:
    """Crude shared-stem grouping. Browsing aid only — not linguistics."""
    w = fold(word)
    for suf in ("ísimos", "ísimas", "ísimo", "ísima", "aciones", "ación",
                "amiento", "imiento", "mente", "ábamos", "aremos", "eremos",
                "iremos", "aban", "ando", "iendo", "ados", "adas", "idos",
                "idas", "aron", "eron", "aba", "ían", "ado", "ida", "ido",
                "ada", "oso", "osa", "ces", "es", "as", "os", "a", "o", "e"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: len(w) - len(suf)]
    return w


# 2026-11-01 (step 12/3 c): letters with any accent (Liège), and a form may carry an internal apostrophe or hyphen
# (O'Higgins, qu'il, moro-guineas, Bío-Bío); a hyphen the print uses for a dash («vino-he») joins two words into one
# form, which the gloss guard then lists — a text residue to fix, not a gloss to write.
_L = r"A-Za-zÁÉÍÓÚÜÑáéíóúüñÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÇç"
WORD_RE = re.compile(rf"[{_L}]+(?:['’\-][{_L}]+)*")


def harvest(paras_or_blocks, sentences, sent_para, sent_text, tid, para_numbers=True):
    """Tokenise blocks into the shared sentence list; return (freq, occurrences)."""
    freq: Counter[str] = Counter()
    occ: dict[str, list[list[int]]] = defaultdict(list)
    items = sorted(paras_or_blocks.items()) if para_numbers else [(0, b) for b in paras_or_blocks]
    for pnum, block in items:
        for sent in split_sentences(block):
            si = len(sentences)
            sentences.append(sent)
            sent_para.append(pnum)
            sent_text.append(tid)
            if len(sent) <= 12:
                continue   # a fragment (a dateline, «Vale.», «¡Peruanos!») is shown in the pane but not harvested (7.2, 2026-11-06)
            seen_here = set()
            for m in WORD_RE.finditer(sent):
                w = m.group(0).lower()
                freq[w] += 1
                if w in seen_here:
                    continue
                seen_here.add(w)
                if len(occ[w]) < 3:
                    occ[w].append([si, m.start(), m.end()])   # [sentence, start, end]
    return freq, occ


def extract_text(rec: dict, manifest: dict, sentences, sent_para, sent_text):
    """Entries for one lectura. Returns (text_record, entries)."""
    tid = rec["n"]
    md = corpus.read_edition(rec)
    fm = corpus.front_matter(md)
    here = Path(__file__).resolve().parent / tid

    paras = load_paragraphs(md)
    glossary = load_glossary(md)
    names = load_names(md)
    extra = json.loads((here / "definitions.json").read_text(encoding="utf-8")) \
        if (here / "definitions.json").exists() else {}
    glosses = json.loads((here / "glosses.json").read_text(encoding="utf-8")) \
        if (here / "glosses.json").exists() else {}

    freq, occurrences = harvest(paras, sentences, sent_para, sent_text, tid)
    ed_freq, ed_occ = harvest(load_editorial(md), sentences, sent_para, sent_text, tid,
                              para_numbers=False)

    families: dict[str, list[str]] = defaultdict(list)
    for w in set(freq) | set(ed_freq):
        families[family_key(w)].append(w)

    # A glossary headword may be a lemma that never occurs literally
    # (*hollar* for *huella*). Attach it to forms sharing its family.
    fam_of = {w: family_key(w) for w in freq}
    lemma_defs: dict[str, tuple[str, str]] = {}
    for head, definition in glossary.items():
        if head in freq:
            continue
        hk = family_key(head)
        for w in freq:
            if fam_of[w] == hk:
                lemma_defs[w] = (definition, head)

    entries = []
    for w, n in freq.most_common():
        lemma = None
        d = glossary.get(w) or extra.get(w)
        if not d and w in lemma_defs:
            d, lemma = lemma_defs[w]
        fam = sorted(families[family_key(w)])
        entries.append({
            "t": tid, "w": w, "n": n, "d": d,
            "src": ("glosario" if w in glossary else "edición") if d else None,
            "fn": w in FUNCTION,
            "name": w in names or any(w == k.split()[0] for k in names),
            "fam": fam if len(fam) > 1 else [],
            "en": glosses.get(w), "lem": lemma,
            "src_deck": "text", "ctx": occurrences[w],
        })
    for w, n in ed_freq.most_common():
        if w in freq:
            continue
        fam = sorted(families[family_key(w)])
        entries.append({
            "t": tid, "w": w, "n": n,
            "d": glossary.get(w) or extra.get(w),
            "src": "glosario" if w in glossary else ("edición" if w in extra else None),
            "fn": w in FUNCTION, "name": False,
            "fam": fam if len(fam) > 1 else [],
            "en": glosses.get(w), "lem": None,
            "src_deck": "editorial", "ctx": ed_occ[w],
        })

    author = fm["author"] or rec["author"]
    # A lectura may carry two authors ("A y B"); dates are joined in the same order.
    dates = " y ".join(
        d for d in (manifest.get("authors", {}).get(a.strip(), {}).get("dates", "")
                    for a in author.split(" y ")) if d)
    text = {
        "id": tid, "title": fm["title"] or rec["title"], "author": author,
        "authorDates": dates, "date": fm["date"], "year": rec["date"][:4],
        "paragraphs": len(paras), "running": sum(freq.values()),
        "textForms": len(freq),
        "editorialForms": sum(1 for e in entries if e["src_deck"] == "editorial"),
        "glossed": sum(1 for e in entries if e["en"]),
        "defined": sum(1 for e in entries if e["d"]),
        "glossaryHeads": len(glossary), "extraDefs": len(extra),
    }
    return text, entries


def main() -> int:
    ap = argparse.ArgumentParser(description="Build vocab.json for the corpus.")
    ap.add_argument("--out", "-o", default="vocab.json")
    ap.add_argument("--only", action="append", default=[],
                    help="lectura number/slug; repeatable. Default: every built lectura")
    args = ap.parse_args()

    manifest = corpus.load_manifest()
    recs = corpus.lecturas(manifest)
    if args.only:
        recs = [corpus.find(k, manifest) for k in args.only]
        if any(r is None or not r.get("edition") for r in recs):
            sys.exit(f"Not a built lectura: {args.only}")
    if not recs:
        sys.exit("No built lecturas in corpus.json.")

    sentences: list[str] = []
    sent_para: list[int] = []
    sent_text: list[str] = []
    texts, entries = [], []
    for rec in recs:
        t, es = extract_text(rec, manifest, sentences, sent_para, sent_text)
        texts.append(t)
        entries.extend(es)
        print(f"  {t['id']} {t['title']}: {t['running']:,} running words, "
              f"{t['textForms']:,} forms (+{t['editorialForms']} editorial), "
              f"{t['glossed']:,} glossed, {t['defined']} defined, {t['paragraphs']} §")

    data = {
        "project": manifest["project"],
        "texts": texts,
        "sentences": sentences,
        "sentPara": sent_para,
        "sentText": sent_text,
        "entries": entries,
        "stats": {
            "texts": len(texts),
            "running": sum(t["running"] for t in texts),
            "forms": sum(t["textForms"] for t in texts),
            "editorialForms": sum(t["editorialForms"] for t in texts),
            "glossed": sum(1 for e in entries if e["en"]),
            "defined": sum(1 for e in entries if e["d"]),
        },
        "rights": (
            "Textos de los autores: dominio público. "
            "Equivalencias, definiciones, agrupaciones y programa: CC0 1.0. "
            "Ninguna definición procede de un diccionario."
        ),
    }
    Path(args.out).write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    s = data["stats"]
    print(f"Wrote {args.out}: {s['texts']} text(s), {s['running']:,} running words, "
          f"{s['forms']:,} forms, {len(sentences):,} sentences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
