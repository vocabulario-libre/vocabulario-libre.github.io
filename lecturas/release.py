#!/usr/bin/env python3
"""release.py — the release gate (policy § 8).

    python release.py --check     # apply § 8.2 to the manifest and editions; exit 1 on the first blocker
    python release.py             # check, then build dist/ via dist.py and write dist/PROVENANCE.md
    python release.py --provenance PATH   # check, then write the provenance record alone (for review; builds nothing)

A release is the output of this program and nothing else. Blockers are listed
in full so that the roadmap can carry them; nothing is built while any remains.
"""
from __future__ import annotations
import json, re, subprocess, sys
from datetime import date
from pathlib import Path
import corpus, dist

ROOT = Path(__file__).resolve().parent
OK_ROLES = {"base", "collation", "derived"}

# ---- rule 15: quotation ceiling at release (same test as compliance.py) ----
def quotation_ceiling_ok(md: str, witnesses: list) -> list:
    import re as _re
    problems = []
    words_total = len(_re.findall(r"\w+", "\n".join(_re.findall(r"^\[§\d+\] (.*)$", md, _re.M)))) or 1
    for w in witnesses:
        layer = w.get("text_layer")
        if not isinstance(layer, int) or layer <= 1929: continue
        sig = w["sigla"]; quoted = 0
        for line in md.splitlines():
            if not line.startswith("| "): continue
            for cell in line.strip().strip("|").split("|"):
                if f"(**{sig}**)" in cell:
                    q = _re.sub(r"\*+|«|»|—.*$", "", cell.split(f"(**{sig}**)")[0]).strip()
                    n = len(_re.findall(r"\w+", q)); quoted += n
                    if n > 15: problems.append(f"{sig}: quotation over 15 words")
        if 100.0 * quoted / words_total > 10.0: problems.append(f"{sig}: quotations exceed 10 % of the edition")
    return problems


THIRD_PARTY_NOTICE = re.compile(r"google-front-matter", re.I)   # files that are a provider's notice, not a record
CORPUS_PARAS = {"Esta edición", "Programas y dependencias", "Propósito y uso", "Método", "Errores"}   # corpus texts, said once (convention 11)

def evidence_files(rec: dict, w: dict) -> list[Path]:
    """Every evidence file a witness entry names (rights_evidence, rights_evidence_also). A bare file name
    resolves to the last `work/NN/evidence/` folder named before it in the same field (a shared witness points
    to the folder of the edition that filed it), else to this edition's folder."""
    out: list[Path] = []
    own = ROOT / "work" / rec["n"] / "evidence"
    for field in ("rights_evidence", "rights_evidence_also"):
        folder = own
        for tok in re.findall(r"work/\d\d/evidence/|[\w\-./]+?\.(?:txt|md)", w.get(field) or ""):
            if tok.endswith("/"):
                folder = ROOT / tok; continue
            q = ROOT / tok if tok.startswith("work/") else folder / tok
            if q not in out: out.append(q)
    return out

def blockers(m: dict, subset: list[str] | None = None) -> list[str]:
    b: list[str] = []
    cutoff = m.get("witness_layer_cutoff", 1929)
    excluded_ok = {e.get("n") for e in m.get("excluded", []) if isinstance(e, dict)}
    for rec in m["lecturas"]:
        n = rec["n"]
        if subset is not None and n not in subset:
            continue
        if rec.get("status") != "publicada":
            if rec.get("release") == "excluded" and rec.get("release_reason"):
                continue
            b.append(f"{n}: status {rec.get('status')} — not publicada and not formally excluded (release='excluded' + release_reason)")
            continue
        if rec.get("release") == "excluded":
            continue
        ws = rec.get("witnesses") or []
        if not ws:
            b.append(f"{n}: no witnesses block"); continue
        if not any(w.get("role") == "base" for w in ws):
            b.append(f"{n}: no base witness")
        for w in ws:
            s = w.get("sigla")
            if w.get("pending"):
                b.append(f"{n} {s}: pending — {w['pending']}")
            if w.get("exception"):
                b.append(f"{n} {s}: declared exception — {w['exception']}")
            if w.get("role") in OK_ROLES:
                if int(w.get("text_layer", 0)) > cutoff:
                    b.append(f"{n} {s}: text layer {w.get('text_layer')} later than {cutoff}")
                if not w.get("rights"):
                    b.append(f"{n} {s}: provider rights line not recorded")
                if w.get("role") != "derived" and ("por leer" in w.get("rights", "") or "unread" in w.get("rights", "").lower()):
                    b.append(f"{n} {s}: rights line marked unread")
        for w in ws:
            # decision 54 (2026-11-01): every entry of the witness table — base, collation, control, discarded,
            # identification — carries the compiler's read of its rights line and an evidence file; only «derived»
            # (this edition's own OCR of another witness) has no provider to read.
            if w.get("role") != "derived":
                ro = w.get("rights_read_on") or ""
                if not w.get("rights_evidence") or not ro:
                    b.append(f"{n} {w.get('sigla')}: rights evidence not recorded (rights_evidence + rights_read_on; policy 8.7, decision 54)")
                elif "compiler" not in ro or "to confirm" in ro:
                    b.append(f"{n} {w.get('sigla')}: rights line read provisionally ({ro}); the compiler's read is needed (8.7, decision 54)")
                for q in evidence_files(rec, w):   # decision 55: the release reproduces the evidence, so it must be on disk
                    if not q.is_file():
                        b.append(f"{n} {w.get('sigla')}: evidence file not on disk — {q.relative_to(ROOT)}")
        try:   # rule 15: quotation ceiling for modern layers (same test as compliance.py)
            for prob in quotation_ceiling_ok(corpus.read_edition(rec), ws):
                b.append(f"{n} {prob} (rule 15)")
        except Exception as exc:
            b.append(f"{n}: could not test the quotation ceiling ({exc})")
        for prob in corpus.persons_problems(rec):   # every layer of every base/collation witness closed by a dated person (policy 8.1/8.7)
            b.append(prob)
        if rec.get("open_rights_questions"):
            b.append(f"{n}: open rights questions — {rec['open_rights_questions']}")
    return b

def checks_pass() -> list[str]:
    out = []
    for cmd in (["compliance.py"], ["drift.py"], ["verify.py"], ["ortografia.py"], ["dist.py", "--check"]):
        r = subprocess.run([sys.executable] + cmd, capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0:
            out.append(f"{' '.join(cmd)} failed")
        if cmd == ["compliance.py"] and "audited for information" in r.stdout:
            out.append("compliance.py: an edition is audited informationally (status en curso)")
    return out

def derivation_paragraphs(rec: dict) -> list[str]:
    """The edition's own rights derivation: every paragraph of *Derechos y propósito* that is this edition's
    (text, printings, persons, first publication, transcriptions, providers, moral rights), without the corpus
    texts the governing document owns (convention 11)."""
    md = corpus.read_edition(rec)
    i = md.find("# Derechos y propósito")
    if i < 0: return []
    j = md.find("\n# ", i + 5)
    sec = md[i:j if j > 0 else None]
    out = []
    for para in sec.split("\n\n"):
        para = para.strip()
        if not para or para.startswith("#"): continue
        mlabel = re.match(r"\*\*([^*]+?)\.?\*\*", para)
        label = (mlabel.group(1) if mlabel else "").strip()
        if label.split(" (")[0] in CORPUS_PARAS: continue
        out.append(para)
    return out

def provenance(m: dict) -> str:
    """PROVENANCE.md — policy 8.4 and 8.7, decision 55: for every released edition, every witness with its
    text-layer date, provider, rights line as read, the date and person of the read and the evidence file
    reproduced verbatim; every person the derivation rests on with death date and source; the edition's own
    derivation and first-publication statement; every excluded text and source with its reason."""
    cutoff = m.get("witness_layer_cutoff", 1929)
    recs = [r for r in m["lecturas"] if r.get("status") == "publicada" and r.get("release") != "excluded"]
    L = [f"# Provenance — {m['project']}", "",
         f"Generated by `release.py` on {date.today().isoformat()} from `corpus.json`, the editions and the evidence files "
         f"of the workshop. Policy § 8: every layer of every distributed file is public domain by **date** (author, drafter, "
         f"compiler and printer dead; printing before {cutoff + 1}) or CC0 by the compiler's waiver, and the evidence for each "
         f"fact is in this file. Rights lines are quoted as read on the provider's record; the evidence files below are the "
         f"compiler's reads, reproduced verbatim (decision 55: the evidence is text a reader can re-check on the provider's page; "
         f"no provider image is kept or distributed). The editions' own *Derechos y propósito* sections carry the same derivation "
         f"in Spanish; where this file and an edition differ, the edition's current version is the record.", "",
         "## Editions in this release", "", "| No. | Title | Signatory | Date | Edition | Witnesses (text layer) |", "|---|---|---|---|---|---|"]
    for r in recs:
        ws = ", ".join(f"**{w['sigla']}** {w.get('role')} {w.get('text_layer')}" for w in r.get("witnesses", []))
        L.append(f"| {r['n']} | {r['title']} | {r['author']} | {r['date']} | `{r['edition']}` v{r.get('version','?')} | {ws} |")
    L.append("")
    seen: dict[str, str] = {}   # evidence file -> the edition under which it is reproduced
    for r in recs:
        n = r["n"]
        L += [f"## {n} · {r['title']} ({r['author']}, {r['date']}) — `{r['edition']}`, v{r.get('version','?')}", "",
              "### Witnesses", "", "| Sigla | Role | Text layer | What | Provider | Rights line as read | Read on | Evidence files |", "|---|---|---|---|---|---|---|---|"]
        files: list[Path] = []
        for w in r.get("witnesses", []):
            ev = evidence_files(r, w)
            for q in ev:
                if q not in files: files.append(q)
            cell = lambda x: str(x or "").replace("|", "\\|").replace("\n", " ")
            L.append(f"| **{w['sigla']}** | {cell(w.get('role'))} | {cell(w.get('text_layer'))} | {cell(w.get('what'))} | {cell(w.get('provider'))} | "
                     f"{cell(w.get('rights'))} | {cell(w.get('rights_read_on'))} | {', '.join('`' + str(q.relative_to(ROOT)) + '`' for q in ev) or '— (derived: this edition\'s own read of another witness)'} |")
        L.append("")
        urls = [(w["sigla"], k, v) for w in r.get("witnesses", []) for k, v in (w.get("urls") or {}).items()]
        if urls:
            L += ["Provider records and pages read:", ""]
            L += [f"- **{s}** — {k}: <{v}>" for s, k, v in urls]
            L.append("")
        L += ["### Persons on whom the derivation rests", "", "| Role | Name | Death | Source | Grade | Layers |", "|---|---|---|---|---|---|"]
        for p in r.get("persons", []):
            cell = lambda x: str(x or "").replace("|", "\\|")
            L.append(f"| {cell(p.get('role'))} | {cell(p.get('name'))} | {cell(p.get('death_date'))} | {cell(p.get('death_source'))} | {cell(p.get('grade'))} | {', '.join(p.get('layers') or [])} |")
        L.append("")
        paras = derivation_paragraphs(r)
        if paras:
            L += [f"### Derivation as the edition states it (*Derechos y propósito*, v{r.get('version','?')})", ""]
            for para in paras: L += [para, ""]
        ex = r.get("excluded") or []
        if ex:
            L += [f"### Texts and sources considered and not adopted ({len(ex)})", ""]
            for e in ex:
                if isinstance(e, dict):
                    L.append(f"- {e.get('date','')} · {e.get('what','')} — {e.get('reason','')}".replace("\n", " "))
                else:
                    L.append(f"- {e}")
            L.append("")
        # every other text file filed under this edition's evidence folder (title pages and colophons transcribed
        # under decision 55, persons' dates, provider records) is evidence too (policy 8.7) and is reproduced
        folder = ROOT / "work" / n / "evidence"
        others = [q for q in sorted(folder.glob("*")) if q.is_file() and q.suffix in (".txt", ".md") and q not in files] if folder.is_dir() else []
        if files or others:
            L += ["### Evidence files, verbatim", ""]
            for q in files + others:
                tag = "" if q in files else " (filed for this edition; not named by a witness entry)"
                rel = str(q.relative_to(ROOT))
                if rel in seen:
                    L += [f"#### `{rel}` — reproduced above under {seen[rel]} (shared witness)", ""]; continue
                seen[rel] = n
                if THIRD_PARTY_NOTICE.search(q.name):   # a provider's own boilerplate (Google's «Acerca de este libro»): not evidence of a rights fact, and not ours to reproduce
                    L += [f"#### `{rel}`{tag} — a provider's standard notice, kept in the workshop and not reproduced here", "",
                          "Google's front matter («Acerca de este libro», pp. 2–4 of its PDF): its usage request attaches to Google's files, which never enter a release; the rights line that governs is HathiTrust's, quoted above.", ""]
                    continue
                L += [f"#### `{rel}`{tag}", "", "~~~~text", q.read_text(encoding="utf-8", errors="replace").rstrip("\n"), "~~~~", ""]
    L += ["## Sources considered at corpus level and not adopted", "", m.get("excluded", {}).get("note", ""), ""]
    for e in m.get("excluded", {}).get("items", []):
        L.append(f"- {e.get('what','')} — {e.get('why','')}".replace("\n", " ") if isinstance(e, dict) else f"- {e}")
    L += ["", "## Licence", "",
          "The authors' texts are public domain. Scripts, apparatus, notes, glossaries, definitions, registers and this file: "
          "CC0 1.0 Universal (the compiler's waiver, policy 4.5). Provider terms attach to providers' scan files, which never enter "
          "a release (policy 4.10, 8.5)."]
    return "\n".join(L) + "\n"

def main() -> int:
    m = corpus.load_manifest()
    subset = m.get("release_subset")  # list of lectura numbers, set only by a written decision in the roadmap
    b = blockers(m, subset) + checks_pass()
    if b:
        print("RELEASE BLOCKED — policy § 8.2:")
        for x in b: print("  ", x)
        return 1
    print("RELEASE GATE PASS: every edition rests on dates and the compiler's waiver; all checks pass.")
    if "--check" in sys.argv:
        return 0
    if "--provenance" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--provenance") + 1])
        out.write_text(provenance(m), encoding="utf-8")
        print(f"Wrote {out} ({out.stat().st_size:,} bytes); nothing built")
        return 0
    rc = dist.build()
    (ROOT / "dist" / "PROVENANCE.md").write_text(provenance(m), encoding="utf-8")
    print("Wrote dist/PROVENANCE.md")
    return rc

if __name__ == "__main__":
    sys.exit(main())
