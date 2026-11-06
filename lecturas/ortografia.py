#!/usr/bin/env python3
"""ortografia.py — fourth check: the reading text against criterion 1.

Every lectura declares the same criterion 1: spelling, accents and punctuation
by the Ortografía of 2010, lexical forms of the witness kept. compliance.py
tests declarations and structure, drift.py pointers, verify.py the text against
its witnesses — and a witness carries the old spelling, so an unmodernised form
passes verify. Nothing tested criterion 1 itself until this script.

Data (project root, plain TSV):
  ortografia-reglas.tsv       antigua, moderna, clase — corpus-wide word rules
  ortografia-conservadas.tsv  lectura, forma, motivo — forms an edition keeps
                              by its criterion 2 (never flagged for it)

Checks, per built edition, on the reading text only (corpus.body):
  FAIL  a rule's old form present (whole word, case kept)
  FAIL  productive classes by pattern: -cion/-sion/-xion/-gion, grave accents,
        old -rémos preterites, á/ó/é/ú as words, capitalised gentilicios
        inside a sentence
  FAIL  digitisation residues: space before : ; ? ! , — doubled punctuation —
        · glyph — lowercase after a sentence-ending stop — unbalanced ¿/? ¡/!
        in a paragraph — a numbered paragraph that ends without a stop while
        the next begins lowercase — « » or " " left open
  WARN  candidates: -ia/-ian/-ias endings not in the rules (an imperfect
        without its tilde, or a noun: the editor decides, then adds a rule or
        a conserved form)

Usage:   python ortografia.py            every built edition
         python ortografia.py 04 01      selected
Exit status 1 if any edition fails.

Builders import it:  text, hits = ortografia.modernizar(text, "04")
"""
from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import corpus  # noqa: E402

RULES = HERE / "ortografia-reglas.tsv"
KEPT = HERE / "ortografia-conservadas.tsv"

GENTILICIOS = ("Americanos", "Americano", "Americanas", "Españoles", "Español", "Española",
               "Peninsulares", "Peninsular", "Indios", "Araucanos", "Ingleses", "Chilenos",
               "Chileno", "Franceses", "Europeos", "Granadinos", "Venezolanos", "Caraqueños",
               "Mexicanos", "Peruanos", "Argentinos", "Portugueses")
# nouns and adjectives in -ia that are not imperfects: never reported as candidates
NOT_IMPERFECT = {"sabia", "media", "india", "arabia", "envidia", "custodia", "concordia", "discordia",
                 "misericordia", "comedia", "tragedia", "insidia", "perfidia", "efigie",
                 "sabias", "medias", "hacia", "gracia", "gracias", "francia", "prusia",
                 "rusia", "persia", "asia", "italia", "turquia", "bolivia", "colombia",
                 "esencia", "estudia", "odia", "guardia", "guardias", "copia", "copias",
                 "lidia", "fabia", "bahia", "secretaria", "andalucia", "colonia", "colonias",
                 "ceremonia", "ceremonias", "incendia", "remedia", "odia", "patria", "patrias"}


PATTERNS = [
    (r"\b(\w+)(cion|sion|xion|gion)\b", r"\1\2́", "terminación -ción"),  # placeholder, replaced below
]
PATTERNS = [
    (r"\b(\w+)cion\b", r"\1ción", "tilde en sílaba final (-n, -s, vocal)"),
    (r"\b(\w+)sion\b", r"\1sión", "tilde en sílaba final (-n, -s, vocal)"),
    (r"\b(\w+)xion\b", r"\1xión", "tilde en sílaba final (-n, -s, vocal)"),
    (r"\b(\w+)gion\b", r"\1gión", "tilde en sílaba final (-n, -s, vocal)"),
    (r"(?<![\w'])à(?![\w'])", "a", "acento grave"),
    (r"\b(\w+)rémos\b", r"\1remos", "tilde antigua en pretérito"),
]


def rules() -> list[tuple[str, str, str]]:
    with RULES.open(encoding="utf-8") as f:
        return [(r["antigua"], r["moderna"], r["clase"]) for r in csv.DictReader(f, delimiter="\t")]


def kept(lectura: str) -> set[str]:
    out = set()
    if KEPT.exists():
        with KEPT.open(encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                if r["lectura"] in (lectura, "*"):
                    out.add(r["forma"])
    return out


def _variants(old: str, new: str):
    """The rule as written, and its capitalised form if the rule is lowercase."""
    yield old, new
    if old[0].islower():
        yield old[0].upper() + old[1:], new[0].upper() + new[1:]


def modernizar(text: str, lectura: str) -> tuple[str, Counter]:
    """Apply the corpus rules to text (minus the lectura's conserved forms).
    Returns the new text and a Counter of (old, new, clase) → occurrences."""
    hits: Counter = Counter()
    keep = kept(lectura)
    for old, new, cls in rules():
        for o, n in _variants(old, new):
            if o in keep:
                continue
            pat = re.compile(rf"(?<![\w'])({re.escape(o)})(?![\w'])")
            text, k = pat.subn(n, text)
            if k:
                hits[(o, n, cls)] += k
    for pat, rep, cls in PATTERNS:
        def _f(m, rep=rep, cls=cls):
            new = m.expand(rep)
            hits[(m.group(0), new, cls)] += 1
            return new
        text = re.sub(pat, _f, text)
    return text, hits


def _reading(md: str) -> str:
    body = corpus.body(md)
    body = re.sub(r"\s?\[\^?\d+\]", "", body)        # note calls (and the space before them)
    body = re.sub(r"^\^\d+:.*$", "", body, flags=re.M)  # note definitions (checked separately)
    return body


def _notes(md: str) -> str:
    return "\n".join(re.findall(r"^\^\d+:.*$", corpus.body(md), flags=re.M))


def _paragraphs(body: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(r"^\[§(\d+)\]\s*(.*?)(?=^\[§\d+\]|\Z)", body, flags=re.M | re.S):
        out.append((m.group(1), m.group(2).strip()))
    return out


def audit(rec: dict, verbose: bool = True) -> tuple[int, int]:
    lectura = str(rec.get("n") or rec.get("number") or rec.get("id", "??"))
    md = corpus.read_edition(rec)
    body = _reading(md)
    notes = _notes(md)
    keep = kept(lectura)
    fails: list[str] = []
    warns: list[str] = []

    def find(pat: str, where: str = body) -> list[str]:
        return re.findall(pat, where)

    # 1. word rules
    for old, new, cls in rules():
        for o, n in _variants(old, new):
            if o in keep:
                continue
            k = len(find(rf"(?<![\w'])({re.escape(o)})(?![\w'])"))
            if k:
                fails.append(f"forma antigua «{o}» ×{k} → «{n}» ({cls})")
            k2 = len(find(rf"(?<![\w'])({re.escape(o)})(?![\w'])", notes))
            if k2:
                fails.append(f"forma antigua «{o}» ×{k2} en las notas → «{n}» ({cls})")

    # 2. productive classes
    for w in find(r"\b\w+(?:cion|sion|xion|gion)\b"):
        if w.lower() not in keep:
            fails.append(f"terminación sin tilde «{w}»")
    for w in find(r"\b\w*[àèìòù]\w*\b"):
        if w in keep or w.lower() in keep: continue   # a conserved form (a foreign place name as the print gives it: «Liège»)
        fails.append(f"acento grave «{w}»")
    for w in find(r"\b\w+rémos\b"):
        fails.append(f"pretérito con tilde antigua «{w}»")
    for w in find(r"(?<![\w'])[áóéú](?![\w'])"):
        fails.append(f"monosílabo con tilde «{w}»")
    for m in re.finditer(r"(?<![.!?¿¡«\"»\n]\s)(?<!^)(?<![.!?¿¡«\"»])\b(" + "|".join(GENTILICIOS) + r")\b", body, flags=re.M):
        start = body.rfind("\n", 0, m.start()) + 1
        before = body[start:m.start()].rstrip()
        if before and not re.search(r"[.!?¿¡«\":]$|^\[§\d+\]$|\bEl$|\*$", before):
            fails.append(f"gentilicio con mayúscula «{m.group(1)}»")

    # 3. digitisation residues
    for m in re.finditer(r"\w ([:;?!,])", body):
        fails.append(f"espacio ante signo «…{body[max(0, m.start()-12):m.end()]}»")
    for m in re.finditer(r"[,;:.]\s?[,;:]|\.\s?\.(?!\.)", body):
        ctx = body[max(0, m.start()-15):m.end()+5].replace("\n", " ")
        abbrev = re.search(r"(?:\b[A-Z]|\bVdes|\bVd|\bUd|\bSr|\bSra|\bExmo|\bDr|\baffmo|\bq\. b\. s\. m)\.$", body[:m.start()+1])
        if "..." not in ctx and "…" not in ctx and "etc." not in ctx and not abbrev:
            fails.append(f"puntuación doble «{ctx}»")
    for m in re.finditer(r"·", body):
        fails.append(f"glifo · «{body[max(0, m.start()-15):m.end()+10]}»")
    for m in re.finditer(r"(?<!\betc)(?<!\b[A-Z])(?<!\b[A-Z][a-z])[a-záéíóúñ]{3,}(?<!affmo)\. ([a-záéíóúñ]\w*)", body):
        fails.append(f"minúscula tras punto «{body[max(0, m.start()-10):m.end()]}»")
    for m in re.finditer(r"\(\s|\s\)|,-\s", body):
        fails.append(f"signo suelto «{body[max(0, m.start()-12):m.end()+8]}»")
    paras = _paragraphs(body)
    for i, (n, p) in enumerate(paras):
        if f"§{n}" in keep:   # paragraph declared in ortografia-conservadas.tsv: the print's own repeated marks, kept and declared in § V
            continue
        if p.count("¿") != p.count("?"):
            fails.append(f"§{n}: ¿ {p.count('¿')} / ? {p.count('?')}")
        if p.count("¡") != p.count("!"):
            fails.append(f"§{n}: ¡ {p.count('¡')} / ! {p.count('!')}")
        if p.count("«") != p.count("»"):
            fails.append(f"§{n}: « {p.count('«')} / » {p.count('»')}")
        if p.count('"') % 2:
            fails.append(f"§{n}: comillas rectas impares ({p.count(chr(34))})")
        if i + 1 < len(paras):
            nxt = paras[i + 1][1]
            if p and not re.search(r"[.!?»\"…:;]\s*\**$", p) and nxt and nxt[0].islower():
                fails.append(f"§{n}→§{paras[i+1][0]}: párrafo partido («…{p[-20:]}» / «{nxt[:20]}…»)")
        if p and p[0].islower() and not (i and re.search(r"[:;]\s*\**$", paras[i-1][1])):
            fails.append(f"§{n}: empieza en minúscula")

    # 4. candidates (warnings)
    known_old = {o for o, _, _ in rules()}
    for w in sorted(set(find(r"\b[a-záéíóúñ]{4,}(?:bia|dia|nia|tia|ria|lia|via|gia|mia|pia|sia|zia|ñia)(?:n|s)?\b"))):
        if w in NOT_IMPERFECT or w in keep or w in known_old or re.search(r"[áéíóú]", w):
            continue
        if re.search(r"(?:cia|ncia|rcia|gia|ria|lia|sia|pia|mia|via|zia)(?:n|s)?$", w):
            continue  # -cia, -ria, -lia … are nouns and adjectives
        warns.append(w)

    if verbose:
        print(f"==== {lectura} · {rec.get('title', '')}")
        for f_ in fails:
            print(f"  FAIL  {f_}")
        if warns:
            print(f"  WARN  candidatos -ia sin tilde (decidir: regla o forma conservada): {', '.join(warns)}")
        print(f"  {'PASS' if not fails else 'FAIL'}: {len(fails)} fallo(s), {len(warns)} candidato(s)\n")
    return len(fails), len(warns)


def main() -> int:
    manifest = corpus.load_manifest()
    recs = corpus.lecturas(manifest, built_only=True)
    sel = [a for a in sys.argv[1:] if not a.startswith("-")]
    if sel:
        recs = [r for r in recs if any(str(r.get("n", r.get("number", ""))).startswith(x) for x in sel)]
    recs = [r for r in recs if str(r.get("n", r.get("number", ""))) != "00"]
    total_f = total_w = 0
    for rec in recs:
        f_, w_ = audit(rec)
        if str(rec.get("status", "")).startswith("en curso"):
            print(f"  (status en curso: {rec.get('n')} audited for information; failures do not fail the run)\n")
            total_w += w_
            continue
        total_f += f_; total_w += w_
    print(f"{'PASS' if not total_f else 'FAIL'}: {total_f} fallo(s), {total_w} candidato(s) en {len(recs)} edición(es)")
    return 1 if total_f else 0


if __name__ == "__main__":
    sys.exit(main())
