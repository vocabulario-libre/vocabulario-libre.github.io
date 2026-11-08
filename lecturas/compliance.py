#!/usr/bin/env python3
"""
compliance.py — Audit every edition in the corpus against the policy.

Mechanical checks only. It cannot judge whether prose is accurate or whether a
definition was written independently; it checks the things a script can check:
that required declarations are present, that every internal reference resolves,
that counts the edition states about itself match its content, and that no
obvious rights problem has crept in.

    python compliance.py              # governing document + every built lectura
    python compliance.py 02           # one lectura, by number, slug or filename
    python compliance.py 00           # the governing document alone

Two layers of checks:

  GENERIC    applied to every edition identically: declarations, structure,
             paragraph numbering, § references, footnotes, grading, rights.
  PER-EDITION read from the lectura's "compliance" block in corpus.json:
             which apparatus sections it must have, the counts it states about
             itself, the sources its notes cite, markers that must be present,
             third-party prose that must be absent, evaluative words to block.

Add a lectura to the manifest and the generic layer runs on it at once; fill
its compliance block as the edition takes shape. Exit status 0 if every check
on every edition passes, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus  # noqa: E402

POLICY = "POLICY-scholarship-and-compliance.md"

# Evaluative vocabulary blocked in every edition (policy 2.10, 3.12). Each
# lectura may add its own list in the manifest.
EVALUATIVE_COMMON = (
    "acertó", "falló", "profético", "profética", "genial", "visionario",
    "visionaria", "equivocado", "equivocada", "poco glorioso", "pasaje incómodo",
)


def policy_version() -> str:
    """The version the policy file declares («Version X.Y» in its head); the governing document must cite it."""
    pol = corpus.ROOT / corpus.load_manifest().get("policy", "POLICY-scholarship-and-compliance.md")
    m = re.search(r"^Version (\d+\.\d+)", pol.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "?"

def fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


class Audit:
    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: list[str] = []

    def check(self, ok: bool, label: str, detail: str = "") -> None:
        (self.passed if ok else self.failed).append(
            label + (f" — {detail}" if detail and not ok else "")
        )

    def report(self) -> int:
        for p in self.passed:
            print(f"  PASS  {p}")
        for f in self.failed:
            print(f"  FAIL  {f}")
        print(f"\n{len(self.passed)} passed, {len(self.failed)} failed")
        return 1 if self.failed else 0


def roman_section(md: str, roman: str) -> str:
    """Apparatus section '## II. …' up to the next '## '."""
    m = re.search(rf"^## {roman}\. .*$", md, re.M)
    if not m:
        return ""
    s = md[m.start():]
    nxt = s.find("\n## ", 4)
    return s[:nxt] if nxt > 0 else s


def audit_edition(rec: dict) -> int:
    md = corpus.read_edition(rec)
    cfg = rec.get("compliance", {})
    a = Audit()
    fm = corpus.front_matter(md)
    print(f"\n==== {rec['n']} · {fm['title'] or rec['title']} ({rec['edition']})")

    # ---- Front matter the tools depend on -------------------------------
    print("FRONT MATTER")
    a.check(bool(fm["title"]), "title heading present")
    a.check(bool(fm["author"]), "author heading present")
    a.check(bool(fm["date"]), "date line present")
    a.check(bool(fm["version"]), "edition carries a version number")


    # ---- Rule 15 / policy § 9: quotations from modern text layers ------------
    print("QUOTATIONS FROM MODERN LAYERS (rule 15)")
    words_total = len(re.findall(r"\w+", "\n".join(re.findall(r"^\[§\d+\] (.*)$", md, re.M)))) or 1
    for w in rec.get("witnesses", []):
        layer = w.get("text_layer")
        if not isinstance(layer, int) or layer <= 1929:
            continue
        sig = w["sigla"]
        quoted, long_rows = 0, []
        for line in md.splitlines():
            if not line.startswith("| "):
                continue
            for cell in line.strip().strip("|").split("|"):
                if f"(**{sig}**)" not in cell:
                    continue
                q = cell.split(f"(**{sig}**)")[0]
                q = re.sub(r"\*+|«|»|—.*$", "", q).strip()
                n = len(re.findall(r"\w+", q))
                quoted += n
                if n > 15:
                    long_rows.append((n, q[:50]))
        share = 100.0 * quoted / words_total
        # non-substantiality report (policy § 9.4): sentences, longest row, concentration, dispersion
        per_par, longest, sentences, nrows = {}, 0, 0, 0
        for line in md.splitlines():
            m_par = re.match(r"^\|\s*(\d+)\s*\|", line)
            if not m_par: continue
            for cell in line.strip().strip("|").split("|"):
                if f"(**{sig}**)" not in cell: continue
                q = re.sub(r"\*+|«|»|—.*$", "", cell.split(f"(**{sig}**)")[0]).strip()
                n = len(re.findall(r"\w+", q)); nrows += 1
                longest = max(longest, n)
                if n >= 6 and re.search(r"[.!?]$", q) and q[:1].isupper(): sentences += 1
                per_par[int(m_par.group(1))] = per_par.get(int(m_par.group(1)), 0) + n
        par_words = {int(n): len(re.findall(r"\w+", p)) for n, p in re.findall(r"^\[§(\d+)\] (.*)$", md, re.M)}
        conc = max((100.0 * v / par_words[k] for k, v in per_par.items() if k in par_words and par_words[k]), default=0.0)
        print(f"  INFO  {sig}: {quoted} words in {nrows} quotations ({share:.1f} % of the text); longest {longest} words; "
              f"complete sentences {sentences}; most-quoted paragraph {conc:.0f} % reconstructable; spread over {len(per_par)} paragraphs")
        a.check(sentences == 0, f"{sig}: no complete sentence quoted")
        a.check(conc <= 50.0, f"{sig}: no paragraph more than half reconstructable from quotations ({conc:.0f} %)")
        a.check(not long_rows, f"{sig}: no quotation over 15 words", f"{long_rows}")
        a.check(share <= 10.0, f"{sig}: quotations within 10 % of the edition ({quoted} words, {share:.1f} %)", f"{quoted} words")
        if quoted:
            a.check("derecho de cita" in md, f"{sig}: rights section states the right of quotation as the basis")

    # ---- Declaratory requirements (policy 4.5, 4.6, 4.7) -------------------
    print("DECLARATIONS")
    required = {
        "purpose / study only": "estudio personal",
        "not a critical edition": "No constituye edición crítica",
        "CC0 waiver": "CC0",
        "errata clause": "prevalecen siempre sobre esta edición",
        "terms of use: support never a condition of access": "nunca condición de acceso",
        "first publication recorded (4.9)": "**Primera publicación.**",
        "text not provider files (4.10)": "no incorpora imágenes de página",
        "moral rights (4.11)": "**Derechos morales.**",
        "dependencies audited (4.12)": "reportlab",
        "method disclosed (4.14)": "Claude, de Anthropic",
        "public-domain basis": "Dominio público",
        "sources-prevail statement": "debe acudir",
        "no-interpretation rule": "no interpreta",
        "no undeclared third-party text": "No se ha incorporado texto ajeno sin declararlo",
    }
    for label, probe in required.items():
        a.check(probe in md, label, f"missing marker {probe!r}")

    # ---- Witness apparatus (policy 3.1, 3.2) ------------------------------
    print("APPARATUS STRUCTURE")
    sigla = cfg.get("sigla") or re.findall(r"^\| \*\*([A-Z])\*\* \|", md, re.M)
    a.check(bool(sigla), "sigla table present", "no '| **X** |' rows")
    for sg in sigla:
        a.check(f"| **{sg}** |" in md, f"sigla {sg} declared in table")
    a.check("**Criterios**" in md, "editorial criteria stated before the text")
    a.check(corpus.BODY_END in md, "critical apparatus present")
    for probe in ["## II. Correcciones", "## III. Divergencias",
                  "# Notas sobre las fuentes", "# Bibliografía",
                  "# Referencias del texto", "# Glosario",
                  "# Historial de revisiones", "# Derechos y propósito"]:
        a.check(probe in md, f"section: {probe}", "missing")
    for probe in cfg.get("required_sections", []):
        a.check(probe in md, f"edition-specific section: {probe}", "missing")

    # ---- Witness layers (policy 4.2, 4.10; roadmap rule 13) ---------------
    print("WITNESS LAYERS")
    wl = rec.get("witnesses")
    a.check(bool(wl), "witnesses block present in manifest", "add sigla/role/text_layer/provider/rights")
    if wl:
        cutoff = corpus.load_manifest().get("witness_layer_cutoff", 1929)
        table = set(re.findall(r"^\| \*\*([A-Z]\d?′?)\*\* \|", md, re.M))  # A′ (05, decision 50) carries a prime
        listed = {w["sigla"] for w in wl}
        a.check(table <= listed, "every sigla in the table is in the manifest", f"missing {sorted(table - listed)}")
        a.check(listed <= table, "every manifest witness is in the sigla table", f"extra {sorted(listed - table)}")
        probs = corpus.persons_problems(rec)
        a.check(not probs, "persons[]: every base/collation witness has a dated compiler and printer row (policy 8.1/8.7)", "; ".join(probs)[:300])
        a.check(any(w.get("role") == "base" for w in wl), "a base witness is named")
        pend = 0
        for w in wl:
            filed = w.get("role") in ("base", "collation")
            late = filed and int(w.get("text_layer", 0)) > cutoff
            norights = filed and not w.get("rights")
            if (late or norights) and w.get("exception"):
                print(f"  NOTE  {w['sigla']}: declared exception — {w['exception']}")
                continue
            if (late or norights) and w.get("pending"):
                pend += 1
                print(f"  WARN  {w['sigla']}: {'text layer ' + str(w['text_layer']) + ' > ' + str(cutoff) if late else 'no rights line'} — pending: {w['pending']}")
                continue
            a.check(not late, f"{w['sigla']}: filed text layer no later than {cutoff}", f"{w.get('text_layer')}")
            a.check(not norights, f"{w['sigla']}: provider rights line recorded", "empty")
        if pend:
            print(f"  ({pend} witness(es) pending audit — warnings, not failures, until the audit item is closed)")

    # ---- Every paragraph reference must resolve (policy 3.3) --------------
    print("INTERNAL REFERENCES")
    def words_only(t): return " ".join(re.findall(r"[a-z0-9ñ]+", fold(t)))
    paras = {k: words_only(v) for k, v in corpus.paragraphs(md).items()}
    declared = corpus.declared_paragraph_count(md)
    n_par = max(paras) if paras else 0
    a.check(declared is not None, "criteria declare the paragraph count", "no 'numerados del 1 al N'")
    a.check(declared == n_par and sorted(paras) == list(range(1, n_par + 1)),
            f"paragraph numbering 1–{declared} contiguous", f"found {len(paras)} up to {n_par}")

    # References to source notes («Notas, § 3», «**§ 3.** …», and any «§ N»
    # inside the notes section itself) are not paragraph references.
    def strip_note_refs(t):
        notes = corpus.section(t, "# Notas sobre las fuentes") or ""
        t = t.replace(notes, " ")
        t = re.sub(r"Notas[^\n]{0,40}?§ ?\d+(?:[ ,y]+§ ?\d+)*", " ", t)
        return re.sub(r"\*\*§ \d+\.", " ", t)
    # «§ 0» is accepted when the criteria declare it for the lines outside the
    # numbering (data, salutation, closing, signature); it resolves against them.
    zero_declared = "§ 0 designa" in md
    if zero_declared:
        head = md[: corpus.body_end(md)]
        tail_lines = head.split("numerados del 1 al", 1)[-1].split("\n")
        paras[0] = words_only(" ".join(l for l in tail_lines if l.strip() and not l.startswith("[§")))

    after = strip_note_refs(md[corpus.body_end(md):])
    refs = [int(n) for n in re.findall(r"§ ?(\d+)", after)]
    dangling = sorted({n for n in refs if n not in paras and n > n_par})
    a.check(not dangling, "no dangling § references", f"{dangling}")

    bad = []
    for roman in ("II", "III"):
        s = roman_section(md, roman)
        # a table may carry a «Carta» column between § and the reading (editions of letter series)
        pat = r"^\| (\d+) \| [^|]+ \| (.+?) \|" if re.search(r"^\| § \| Carta \|", s, re.M) else r"^\| (\d+) \| (.+?) \|"
        for num, adopted in re.findall(pat, s, re.M):
            # a reading that spans a paragraph break (marked ¶) resolves if each side
            # is found in the cited paragraph, the one before or after it, or § 0
            near = " ".join(paras.get(int(num) + k, "") for k in (-1, 0, 1)) + " " + paras.get(0, "")
            parts = [words_only(re.sub(r"[*`]|\[\?OCR\]|duda de digitalización", "", a)) for a in adopted.split("¶")]
            if len(parts) == 1:
                if parts[0] not in paras.get(int(num), ""): bad.append((roman, num, adopted[:40]))
            elif not all(pt in near for pt in parts if pt):
                bad.append((roman, num, adopted[:40]))
    a.check(not bad, "apparatus rows resolve to cited paragraphs", f"{bad}")

    all_refs = [int(n) for n in re.findall(r"§ ?(\d+)", strip_note_refs(md)) if int(n) <= n_par]
    dangling_any = sorted({n for n in all_refs if n not in paras})
    a.check(not dangling_any, "every § reference document-wide resolves", f"{dangling_any}")
    a.check(len(all_refs) >= n_par, "reference density plausible", f"{len(all_refs)} refs")

    # ---- Footnote integrity (policy 2.4) ---------------------------------
    print("REDUNDANT DISCLOSURE")
    calls = set(re.findall(r"\[\^(\d+)\]", md))
    defs = set(re.findall(r"^\^(\d+):", md, re.M))
    a.check(calls <= defs, "every footnote call is defined", f"{sorted(calls - defs)}")
    a.check(defs <= calls, "every footnote definition is called", f"{sorted(defs - calls)}")
    notes = re.findall(r"\*\*§ (\d+)\.", md)
    a.check(len(notes) >= 1, "source-notes register populated", f"{len(notes)} entries")

    # ---- Confidence grading (policy 2.3, 3.8) ----------------------------
    print("CONFIDENCE GRADING")
    graded = re.findall(r"\*\*§ \d+\. .+? — (.+?)\.\*\*", md)
    a.check(len(graded) == len(notes), "each source note carries a grade",
            f"{len(graded)} graded of {len(notes)}")
    for probe in cfg.get("require_markers", []):
        a.check(probe in md, f"required marker present: {probe!r}")
    audit_declaratory(a, rec, md, corpus.load_manifest())

    # ---- Self-describing counts (policy 2.7) -----------------------------
    print("SELF-DESCRIBING COUNTS")
    counts = cfg.get("counts", {})
    if "apparatus_sections" in counts:
        a.check(len(re.findall(r"^## [IVX]+\.", md, re.M)) == counts["apparatus_sections"],
                f"apparatus: {counts['apparatus_sections']} sections", "stated count does not match content")
    if "source_notes" in counts:
        a.check(len(notes) == counts["source_notes"],
                f"source notes: {counts['source_notes']} entries", f"found {len(notes)}")
    if "restitutions" in counts:
        sec_i = roman_section(md, "I")
        a.check(len(re.findall(r"^\*\*\d+\.", sec_i, re.M)) == counts["restitutions"],
                f"§ I: {counts['restitutions']} restitutions", "stated count does not match content")
    for roman, n in counts.get("rows", {}).items():
        sec = roman_section(md, roman)
        a.check(len(re.findall(r"^\| \d+ \|", sec, re.M)) == n,
                f"§ {roman}: {n} rows", "stated count does not match content")
    for roman, phrase in cfg.get("count_phrases", {}).items():
        a.check(phrase in roman_section(md, roman), f"§ {roman} states its count: {phrase!r}")

    # ---- Cited sources must reach the bibliography (policy 3.1) ----------
    print("CITATION INTEGRITY")
    notes_sec = corpus.section(md, "# Notas sobre las fuentes")
    bib_sec = corpus.section(md, "# Bibliografía")
    for name in cfg.get("cited_sources", []):
        if name in notes_sec:
            a.check(name in bib_sec, f"source cited in notes appears in bibliography: {name}")

    # ---- Rights hygiene (policy 4.4, 2.10, 3.12) --------------------------
    print("RIGHTS HYGIENE")
    a.check("definiciones son de esta edición" in md, "glossary declares independent authorship")
    a.check("Son datos, no interpretación" in md, "reference key declares itself factual, not interpretive")
    # Attributed quotations in « » are reporting, not adoption (policy 2.6),
    # so they are removed before the scan.
    # The reading text itself is the author's and is not scanned (policy 2.10 governs the compiler's commentary);
    # the apparatus, notes, key and glossary are.
    outside = md[:corpus.body_start(md)] + md[corpus.body_end(md):]
    unquoted = re.sub(r"«[^»]*»", "«»", outside)
    words = list(EVALUATIVE_COMMON) + list(cfg.get("evaluative", []))
    hits = sorted({w for w in words if re.search(rf"\b{re.escape(w)}\b", unquoted)})
    a.check(not hits, "no evaluative commentary on the text", f"{hits}")
    leaks = [f for f in cfg.get("forbidden", []) if f in md]
    a.check(not leaks, "no third-party editorial prose reproduced", f"{leaks}")

    # ---- Glosses must gloss, never diagnose (policy 2.7; audit of 2026-10-27) --------------
    # A gloss that declares its form a misread, a fragment or a residue is an uncorrected
    # error in the reading text, recorded where no reader of the text will see it (15 carried
    # 34 of them at v1.3). Such a form is returned to the text, read on the image and fixed.
    print("GLOSSES")
    gpath = Path(rec["vocab"]) / "glosses.json" if rec.get("vocab") else None
    if gpath and gpath.exists():
        glosses = json.loads(gpath.read_text(encoding="utf-8"))
        bad = sorted(w for w, g in glosses.items()
                     if re.search(r"[\(\[]\s*(misread|fragment|residue|garbled|OCR (error|fragment|residue|misread))", str(g), re.I))
        a.check(not bad, "no gloss declares its form a misread, fragment or residue", f"{bad[:12]}")

    return a.report()



# ============================================================================
# Declaratory text (decisions 50–52, 2026-11-01; Phase 4b, step 12/2)
# ============================================================================
# (i) the six corpus texts of the governing document, slots filled from the manifest, verbatim in
#     every published edition, and the Estado line of the standard form with the title page's version;
# (ii) no pre-publication prose in the declaratory sections of a published edition: no future tense of
#     the work verbs, no turn vocabulary, no pending marker (an exception list is not needed: the
#     reader's «podrá», «hallará» are not work verbs);
# (iii) every `work/…` path an edition cites exists (the allowlist half lands with prune.py, step 14).

WORK_VERBS = ["comprobar", "resolver", "marcar", "fijar", "enumerar", "registrar", "constar", "identificar",
              "cargar", "seguir", "llevar", "hacer", "completar", "graduar", "reproducir"]
_FUT = [v + "á" for v in WORK_VERBS] + [v + "án" for v in WORK_VERBS]
RESIDUE_RE = re.compile(r"\b(" + "|".join(_FUT) + r")\b|\bturnos? [A-Z]\d?\b|\bturnos? siguientes?\b|\ben esta etapa\b"
                        r"|\b[Nn]o debe citarse hasta\b|\b[Pp]endiente|\b[Pp]revist|\bpor (determinar|confirmar|consignar|comprobar)\b")
# («hasta la versión 1.2 lo fue L» is history, not a residue; «No debe citarse hasta la versión 1.0» is.)
DECL_LABELS = ["Advertencia", "Transcripciones", "Esta edición", "Programas y dependencias", "Propósito y uso", "Método"]


def corpus_texts(gov_md: str) -> tuple[dict, dict]:
    """The six texts and the slot-value sentences, parsed from the governing document (Part I, item 11)."""
    es = gov_md[gov_md.index("# Parte I · Español"):gov_md.index("# Part II · English")]
    texts, values = {}, {}
    for m in re.finditer(r"^\s*- \*\*(" + "|".join(DECL_LABELS) + r")\.\*\* «(.*)»\s*$", es, re.M):
        texts[m.group(1)] = m.group(2)
    for m in re.finditer(r"^\s*- `\{(\w+)\}` `([\w+]+)`: «(.*)»\s*$", es, re.M):
        values[(m.group(1), m.group(2))] = m.group(3)
    return texts, values


def instantiate(label: str, texts: dict, values: dict, d: dict) -> str:
    t = texts[label]
    case = d.get("capas", "own")
    sub = lambda s: s.replace("{imagen}", d.get("imagen", "")).replace("{proveedor}", d.get("proveedor", "")).replace("{lectura}", d.get("lectura", ""))
    t = (t.replace("{testimonio}", d.get("testimonio", ""))
          .replace("{capas}", sub(values.get(("capas", case), "")))
          .replace("{ocr_prog}", sub(values.get(("ocr_prog", case), "")))
          .replace("{texto}", d.get("texto", ""))
          .replace("{secciones}", d.get("secciones", ""))
          .replace("{cronologia}", d.get("cronologia", ""))
          .replace("{extras}", d.get("extras", ""))
          .replace("{ocr_esta}", "" if case == "provider" else ", y el reconocimiento óptico que ella hizo")
          .replace("{procedencia}", d.get("procedencia", "")))
    return t


def declaratory_ranges(md: str) -> list[tuple[str, str]]:
    """(section name, text) for the declaratory sections of an edition."""
    out = []
    m = re.search(r"^## Advertencia\s*$", md, re.M)
    if m:
        e = re.search(r"^## ", md[m.end():], re.M)
        out.append(("Advertencia", md[m.end(): m.end() + e.start()] if e else md[m.end():]))
    m = re.search(r"^## Nota sobre el texto\s*$", md, re.M)
    if m:
        s = md[m.end():]
        e = min([x for x in (s.find("\n[§1]"), s.find("\n# Texto de lectura"), s.find("\n# Aparato")) if x > 0] or [len(s)])
        out.append(("Nota", s[:e]))
    sec = roman_section(md, "V")
    if sec:
        out.append(("Aparato § V", "\n".join(l for l in sec.split("\n") if not l.startswith("|"))))
    m = re.search(r"^# Derechos y propósito\s*$", md, re.M)
    if m:
        e = re.search(r"^# ", md[m.end():], re.M)
        out.append(("Derechos", md[m.end(): m.end() + e.start()] if e else md[m.end():]))
    return out


def audit_declaratory(a: "Audit", rec: dict, md: str, manifest: dict) -> None:
    print("DECLARATORY TEXT (decisions 50–52)")
    published = rec.get("status") == "publicada"
    gov = Path(manifest.get("governing", "00-lecturas-de-los-libertadores.md")).read_text(encoding="utf-8")
    texts, values = corpus_texts(gov)
    a.check(len(texts) == 6, "governing document carries the six corpus texts", f"found {sorted(texts)}")
    d = rec.get("declaratory", {})
    a.check(bool(d), "manifest carries the edition's declaratory slots", "no `declaratory` block")
    # (i) corpus texts verbatim
    if texts and d:
        adv = None
        for name, text in declaratory_ranges(md):
            if name == "Advertencia":
                paras = [p for p in text.split("\n") if p.strip() and not p.startswith("**Estado")]
                adv = paras[0] if paras else ""
        a.check(adv == instantiate("Advertencia", texts, values, d), "Advertencia is the corpus text (slots filled)",
                f"differs: {adv[:90]!r}…" if adv is not None else "no Advertencia")
        der = dict(x for x in declaratory_ranges(md) if x[0] == "Derechos").get("Derechos", "")
        for label in DECL_LABELS[1:]:
            want = f"**{label}.** " + instantiate(label, texts, values, d)
            have = re.search(r"^\*\*" + re.escape(label) + r"\.\*\* (.*)$", der, re.M)
            a.check(have is not None and have.group(0) == want, f"Derechos · {label} is the corpus text",
                    "missing" if have is None else f"differs: {have.group(1)[:90]!r}…")
    # Estado line
    fm = corpus.front_matter(md)
    est = re.search(r"^\*\*Estado: publicada \(versión (\d+\.\d+), \d{4}-\d{2}-\d{2}\)\.\*\*", md, re.M)
    if published:
        a.check(est is not None, "Estado line of the standard form", "missing or malformed")
        if est:
            a.check(est.group(1) == fm["version"], "Estado line version = title page", f"{est.group(1)} vs {fm['version']}")
    # version sync (decision 52 C2, step 12/3 a): the title page is the one source of an edition's version;
    # the Estado line, the head of the Historial (list form «- **N.N (date).**» or narrative «**Versión N.N**»:
    # the highest version in either), the manifest's `version` (generated by `python corpus.py --sync`), every
    # status cell of the governing document's tables («publicada · vN.N» / «published · vN.N») and the register's
    # «Edition published (vN.N, date).» line must all say what the title page says.
    if published:
        for where, got in version_sources(rec, md, gov).items():
            a.check(got == fm["version"], f"version sync · {where} = title page",
                    f"{got!r} vs v{fm['version']}")
    # corpus-level markers
    for probe in manifest.get("declaratory_markers", []):
        a.check(probe in md, f"corpus marker present: {probe!r}")
    # (ii) residues
    if published:
        hits = []
        for name, text in declaratory_ranges(md):
            for m in RESIDUE_RE.finditer(text):
                hits.append(f"{name}: «{m.group(0)}»")
        a.check(not hits, "no pre-publication prose in the declaratory sections (future tense, turn vocabulary, pending markers)",
                f"{len(hits)} hit(s): " + "; ".join(hits[:8]) + (" …" if len(hits) > 8 else ""))
    # names (decision 53, step 12/3 b): every proper-name token in the reading text carries the accentuation of its
    # Personas/Lugares key; the twin test is accent-only (n/ñ and other spellings are not caught here); «St. Martin» skipped
    if published:
        lags = name_lags(md)
        a.check(not lags, "every name token in the text has its key's accentuation (decision 53)",
                "; ".join(f"{k}→{t}×{c}" for k, t, c in lags[:8]) + (" …" if len(lags) > 8 else ""))
    # paragraph markers (12/4): every [§N] starts after a blank line, or the builders fuse it with the line above
    bl = corpus.body(md).split("\n")
    fused = [l[:8] for i, l in enumerate(bl) if l.startswith("[§") and i > 0 and bl[i - 1].strip()]
    a.check(not fused, "a blank line before every [§N]", f"{len(fused)}: {fused[:6]}")
    # text boundary (nineteenth session, 2026-11-03): the level-1 heading «Texto de lectura» stands before § 1 in every
    # edition, so the PDF breaks the page and the EPUB opens a chapter where the text begins
    n1 = md.find("\n[§1]"); tl = md.find("\n# Texto de lectura\n")
    a.check(0 < tl < n1, "the heading «# Texto de lectura» stands before [§1]",
            "missing" if tl < 0 else ("after §1" if tl > n1 else ""))
    # glosses (12/4): every form of the reading text has a gloss in the trainer (vocab/vocab.json, text deck);
    # the trainer's own form set is the authority, not a second tokeniser
    vj = Path("vocab/vocab.json")
    if published and vj.exists():
        try:
            ents = json.loads(vj.read_text(encoding="utf-8")).get("entries", [])
            ung = sorted(x["w"] for x in ents if x.get("t") == rec["n"] and x.get("src_deck") == "text" and not x.get("en"))
            a.check(not ung, "every text form glossed in the trainer", f"{len(ung)}: {ung[:10]}" + (" …" if len(ung) > 10 else ""))
        except Exception as ex:  # a broken vocab.json is its own failure
            a.check(False, "every text form glossed in the trainer", f"vocab.json unreadable: {ex}")
    # (iii) cited paths exist — and the prune would keep them (policy 8.8; prune.py's classes vs the citations)
    cited = sorted({p for p in re.findall(r"`(work/[^`\s]+)`", md)})
    missing = [p for p in cited if not Path(p).exists()]
    a.check(not missing, "every `work/…` path cited exists", f"{missing}")
    try:
        import prune
        doomed = [p for p in cited if prune.would_delete(p) and prune.cited_by(corpus.ROOT / p, {p: [rec["edition"]]})]
        a.check(not doomed, "no cited `work/…` path is in a prune class (8.8)", f"{doomed}")
    except ImportError:   # prune.py lives in the workshop; a distribution copy has neither it nor work/
        a.check(not (corpus.ROOT / "work").is_dir(), "no cited `work/…` path is in a prune class (8.8)", "prune.py missing from the workshop")


def version_sources(rec: dict, md: str, gov: str) -> dict:
    """Every place that states the edition's version, keyed by name, with the version it states (None if absent).
    The title page is the source; `audit_declaratory` holds each of these to it."""
    out = {}
    hist = md.split("# Historial de revisiones", 1)[1] if "# Historial de revisiones" in md else ""
    vs = re.findall(r"^- \*\*(\d+\.\d+) \(\d{4}-\d{2}-\d{2}\)\.\*\*", hist, re.M) + \
         re.findall(r"^\*\*Versión (\d+\.\d+)\*\*", hist, re.M)
    out["Historial head"] = max(vs, key=lambda v: tuple(int(x) for x in v.split("."))) if vs else None
    out["manifest `version`"] = str(rec["version"]) if rec.get("version") is not None else None
    n = rec["n"]
    cells = []
    for line in gov.split("\n"):
        if re.match(rf"^\| *{n} *\|", line):
            cells += re.findall(r"(?:publicada|published) [·—] v(\d+\.\d+)", line)
    seps = re.findall(rf"^\| *{n} *\|.*?(?:publicada|published) (—) v", gov, re.M)
    out["governing table cells"] = (cells[0] if cells and len(set(cells)) == 1 and not seps
                                    else ("—" if seps else (None if not cells else "/".join(cells))))
    reg = Path(rec["register"]).read_text(encoding="utf-8") if rec.get("register") and Path(rec["register"]).exists() else ""
    m = re.search(r"^Edition published \(v(\d+\.\d+), \d{4}-\d{2}-\d{2}\)\.", reg, re.M)
    out["register «Edition published» line"] = m.group(1) if m else None
    return out


def name_lags(md: str) -> list[tuple[str, str, int]]:
    """Tokens of the reading text that are an accent-only variant of a Personas/Lugares key token.
    Returns (key form, text form, count). Common homographs that happen to be capitalised are not names."""
    import unicodedata
    def strip(s): return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    WORD = re.compile(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñü']+")
    SKIP = {"Esta", "Este", "Como", "Cuando", "Cuanto", "Cuantos", "Mas", "Para", "Sobre", "Entre", "Hasta", "Solo",
            "Aun", "Rio", "Rios", "Que", "Si", "Se", "De", "El", "Pena"}
    keys = []
    for head in ("## Personas", "## Lugares e instituciones"):
        if head in md:
            sec = md.split(head, 1)[1].split("\n# ", 1)[0].split("\n## ", 1)[0]
            keys += re.findall(r"^- \*\*([^*]+?)\*\*", sec, re.M)
    forms: dict[str, set[str]] = {}
    for k in keys:
        for w in WORD.findall(k):
            if len(w) > 3: forms.setdefault(strip(w), set()).add(w)
    body = corpus.body(md)
    out: dict[tuple[str, str], int] = {}
    for mm in WORD.finditer(body):
        tok = mm.group(0); s = strip(tok)
        if s in SKIP or s not in forms or tok in forms[s]: continue
        if body[max(0, mm.start() - 4):mm.start()].endswith("St. "): continue
        key = "/".join(sorted(forms[s]))
        out[(key, tok)] = out.get((key, tok), 0) + 1
    return [(k, t, c) for (k, t), c in sorted(out.items())]


def audit_governing(manifest: dict) -> int:
    """The governing document: bilingual, tables mirror the manifest, no evaluation."""
    path = Path(manifest.get("governing", ""))
    a = Audit()
    print(f"\n==== 00 · governing document ({path})")
    if not path.exists():
        a.check(False, "governing document present", f"missing {path}")
        return a.report()
    md = path.read_text(encoding="utf-8")
    fm = corpus.front_matter(md)
    a.check(bool(fm["title"]) and bool(fm["version"]), "front matter: title and version")
    a.check("# Parte I · Español" in md and "# Part II · English" in md, "two parts, Spanish and English")
    es = md[md.index("# Parte I · Español"):md.index("# Part II · English")]
    en = md[md.index("# Part II · English"):]
    for label, probe_es, probe_en in [
        ("identification not evaluation", "identifica y ordena", "identifies and orders"),
        ("not a critical edition", "no son ediciones críticas", "are not critical editions"),
        ("sources prevail", "la fuente tiene razón", "the source is right"),
        ("selection criterion stated once", "Se consigna el criterio una vez", "The criterion is stated once"),
        ("exclusions pointed to manifest", "no adoptados", "not adopted"),
        ("CC0 waiver", "CC0 1.0 Universal", "CC0 1.0 Universal"),
        ("terms of use: support never a condition of access", "nunca condición de acceso", "never a condition of access"),
        ("first publication (4.9)", "**Primera publicación.**", "**First publication.**"),
        ("text not provider files (4.10)", "nunca imágenes de página", "never a provider's page images"),
        ("moral rights (4.11)", "**Derechos morales.**", "**Moral rights.**"),
        ("distribution audited (4.12, 4.13)", "`work/`", "`work/`"),
        ("method disclosed (4.14)", "Claude, de Anthropic", "Claude, by Anthropic"),
        ("policy version named", f"versión {policy_version()}", f"version {policy_version()}"),
        ("errata clause", "prevalecen siempre", "always prevail"),
    ]:
        a.check(probe_es in es, f"ES: {label}", f"missing {probe_es!r}")
        a.check(probe_en in en, f"EN: {label}", f"missing {probe_en!r}")

    # tables mirror the manifest: number, order, status, in both parts
    lect = manifest["lecturas"]
    status_map = {"pendiente": ("pendiente", "pending"), "en curso": ("en curso", "in progress"),
                  "publicada": ("publicada", "published")}
    for part, text, idx in (("ES", es, 0), ("EN", en, 1)):
        ident = [r for r in re.findall(r"^\| (\d\d) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", text, re.M)]
        prov = re.findall(r"^\| (\d\d) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", text, re.M)
        a.check([r[0] for r in ident] == [l["n"] for l in lect],
                f"{part}: identification rows match manifest numbers and order",
                f"{[r[0] for r in ident]}")
        a.check([r[0] for r in prov] == [l["n"] for l in lect],
                f"{part}: provenance rows match manifest numbers and order", f"{[r[0] for r in prov]}")
        bad = [(r[0], r[5].strip()) for r, l in zip(ident, lect)
               if not r[5].strip().startswith(status_map[l["status"]][idx])]
        a.check(not bad, f"{part}: statuses match manifest", f"{bad}")
        bad_t = [(r[0], r[3].strip()) for r, l in zip(ident, lect) if r[3].strip() != l["title"]]
        a.check(not bad_t, f"{part}: titles match manifest", f"{bad_t}")
        bad_a = [(r[0], r[2].strip()) for r, l in zip(ident, lect) if r[2].strip() != l["author"]]
        a.check(not bad_a, f"{part}: signatories match manifest", f"{bad_a}")
        for author in manifest.get("authors", {}):
            a.check(re.search(rf"^\| {re.escape(author)} \| \d{{4}} \|", text, re.M) is not None,
                    f"{part}: rights table names {author}")
        unquoted = re.sub(r"«[^»]*»", "«»", text)
        hits = sorted({w for w in EVALUATIVE_COMMON if re.search(rf"\b{re.escape(w)}\b", unquoted)})
        a.check(not hits, f"{part}: no evaluative vocabulary", f"{hits}")

    # built outputs
    stem = path.with_suffix("")
    a.check(Path(f"{stem}.pdf").exists() and Path(f"{stem}.epub").exists(), "PDF and EPUB built")
    return a.report()


def audit_schema() -> int:
    """8.2 (2026-11-08; decisions 85, 87; design §§ 2, 9): the grammar layer's data as distributed — vocab/concepts.json, vocab/NN/senses.json,
    vocab/schema-summary.json. Portable: reads only files of the distribution.
    (1) every glossed text form of every published lectura (function words apart) attaches to exactly one lexical concept, with that text as source;
    (2) no concept without an English form: every lexical concept has an English pivot form, every grammatical concept an English realisation;
    (3) every function-word locus resolves — a concept that exists, a status certified or review, and a reason wherever it is under review;
    (4) every grammatical concept's realisations are explicit in every language that has forms at all (∅ written, never absent), with a kind from the
        declared set; (5) the summary's counts equal the data's; a concept with no locus is named."""
    import json, glob
    a = Audit()
    vocab = corpus.ROOT / "vocab"
    cpath, spath = vocab / "concepts.json", vocab / "schema-summary.json"
    a.check(cpath.exists() and spath.exists(), "schema present (vocab/concepts.json, vocab/schema-summary.json)")
    if not (cpath.exists() and spath.exists()):
        return a.report()
    C = json.loads(cpath.read_text(encoding="utf-8")); S = json.loads(spath.read_text(encoding="utf-8"))
    V = json.loads((vocab / "vocab.json").read_text(encoding="utf-8")) if (vocab / "vocab.json").exists() else None
    sys.path.insert(0, str(vocab)); from extract_vocab import FUNCTION  # noqa
    kinds = {"word", "particle", "ending", "feature", "order", "∅"}
    # (2)
    no_en = [c["id"] for c in C["lexical"] if not any((f.get("form") or "").strip() for f in (c["forms"].get("en") or []))]
    a.check(not no_en, f"every lexical concept has an English form ({len(C['lexical']):,} concepts)", f"{len(no_en)}: {no_en[:5]}")
    # (4)
    langs_with_forms = {L for g in C["grammatical"] for L, fs in (g.get("forms") or {}).items() if fs}
    bad_real = [(g["id"], L) for g in C["grammatical"] for L in langs_with_forms
                if not (g.get("forms") or {}).get(L) or not all((f.get("form") or "").strip() and f.get("realisation") in kinds for f in g["forms"][L])]
    a.check(not bad_real, f"every grammatical concept's realisation explicit in every language with forms ({len(C['grammatical'])} concepts; {', '.join(sorted(langs_with_forms)) or 'none'}; ∅ written, never absent)", f"{len(bad_real)}: {bad_real[:4]}")
    # (1) — needs vocab.json (the workshop; a scratch rebuild in a distribution has it after extract_vocab.py)
    if V is not None:
        att: dict = {}
        for c in C["lexical"]:
            for f in c["forms"].get("es") or []:
                for t in f.get("source") or []:
                    att[(t, f["form"])] = att.get((t, f["form"]), 0) + 1
        lex_entries = [e for e in V["entries"] if (e.get("en") or "").strip() and e["w"].lower() not in FUNCTION and e["w"].lower() not in ("al", "del")]
        excluded = {(x[0], x[1]) for x in C.get("excluded", [])}   # [text, form, gloss] triples
        unattached = [(e["t"], e["w"]) for e in lex_entries if att.get((e["t"], e["w"]), 0) == 0 and (e["t"], e["w"]) not in excluded]
        multi = [(e["t"], e["w"]) for e in lex_entries if att.get((e["t"], e["w"]), 0) > 1]
        a.check(not unattached and not multi, f"every glossed form attaches to exactly one lexical concept ({len(lex_entries):,} forms; {len(excluded)} excluded as note-only glosses, listed)",
                f"unattached {len(unattached)}: {unattached[:4]}; multiple {len(multi)}: {multi[:4]}")
    else:
        a.check(False, "every glossed form attaches to one lexical concept", "vocab/vocab.json not built — run vocab/extract_vocab.py")
    # (3) and (5)
    ids = {g["id"] for g in C["grammatical"]}
    n = cert = bad = 0; used = set(); per_text = {}
    for f in sorted(glob.glob(str(vocab / "[0-9][0-9]" / "senses.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        tc = 0
        for l in d["loci"]:
            n += 1; used.add(l.get("c"))
            ok = l.get("c") in ids and l.get("status") in ("certified", "review") and (l["status"] == "certified" or bool(l.get("reason")))
            bad += 0 if ok else 1
            if l.get("status") == "certified": cert += 1; tc += 1
        per_text[d["text"]] = (len(d["loci"]), tc)
    a.check(bad == 0, f"every function-word locus resolves: a concept that exists, certified or under review with a reason ({n:,} loci in {len(per_text)} texts)", f"{bad} do not")
    sum_ok = S.get("loci") == n and S.get("certified") == cert and S.get("grammatical") == len(C["grammatical"]) and S.get("lexical") == len(C["lexical"]) \
             and all(S["texts"].get(t, {}).get("loci") == a_ and S["texts"].get(t, {}).get("certified") == c_ for t, (a_, c_) in per_text.items())
    a.check(sum_ok, f"schema-summary.json equals the data ({cert:,} of {n:,} loci certified; {len(C['lexical']):,} lexical, {len(C['grammatical'])} grammatical concepts)")
    orphan = sorted(ids - used)
    a.check(not orphan, "every grammatical concept has a locus", f"{len(orphan)}: {orphan[:4]}")
    return a.report()


def main() -> int:
    if not Path(POLICY).exists():
        sys.exit(f"Policy not found: {POLICY}")
    recs = corpus.lecturas()
    if len(sys.argv) > 1:
        keys = [k for k in sys.argv[1:] if k != "00"]
        picked = [corpus.find(k) for k in keys]
        if any(r is None for r in picked):
            sys.exit(f"Not in manifest: {keys}")
        recs = picked
    want_gov = len(sys.argv) == 1 or "00" in sys.argv[1:]
    if not recs and not want_gov:
        print("No built lecturas in corpus.json.")
        return 0
    rc = 0
    # ---- Manifest consistency (policy 3.14) ------------------------------
    print("MANIFEST")
    m = Audit()
    nums = [r["n"] for r in corpus.load_manifest()["lecturas"]]
    m.check(nums == sorted(nums) and len(set(nums)) == len(nums), "lectura numbers unique and ascending")
    dates = [r["date"] for r in corpus.load_manifest()["lecturas"]]
    m.check(dates == sorted(dates), "lecturas in chronological order", f"{dates}")
    for rec in recs:
        st = corpus.stem(rec)
        m.check(Path(rec["edition"]).exists(), f"{rec['n']}: edition file present")
        m.check(Path(rec["edition"]).name.startswith(rec["n"] + "-"), f"{rec['n']}: edition carries its number")
        if rec.get("status") == "publicada":
            m.check(bool(rec.get("register")) and Path(rec["register"]).exists(), f"{rec['n']}: register present")
            m.check(Path(st + ".pdf").exists() and Path(st + ".epub").exists(), f"{rec['n']}: PDF and EPUB built")
            m.check(bool(rec.get("vocab")) and (Path(rec["vocab"]) / "glosses.json").exists(),
                    f"{rec['n']}: vocabulary glosses present")
    rc |= m.report()
    # ---- Distribution (policy 4.13) --------------------------------------
    if len(sys.argv) == 1:
        print("DISTRIBUTION")
        import dist
        rc |= dist.check()
    # ---- Schema: the grammar layer's data (8.2; decisions 85, 87) -------------
    if len(sys.argv) == 1:
        print("SCHEMA (8.2)")
        rc |= audit_schema()
    # ---- Release gate (policy § 8) — reported, not enforced here ------------
    if len(sys.argv) == 1:
        print("RELEASE GATE (policy § 8.2; informational — release.py enforces it)")
        import release
        bl = release.blockers(corpus.load_manifest(), corpus.load_manifest().get("release_subset"))
        for x in bl:
            print(f"  BLOCK  {x}")
        print(f"  ({len(bl)} blocker(s); nothing is released while any remains)")
    if want_gov:
        rc |= audit_governing(corpus.load_manifest())
    for rec in recs:
        r = audit_edition(rec)
        if rec.get("status") == "en curso":
            print(f"  (status en curso: {rec['n']} audited for information; failures do not fail the run)")
        else:
            rc |= r
    print(f"\n{'ALL PASS' if rc == 0 else 'FAILURES'} across {len(recs)} edition(s)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
