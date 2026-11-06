#!/usr/bin/env python3
"""
corpus.py — The one place the project's files are named.

Every other script (build_pdf, build_epub, compliance, drift, verify,
vocab/extract_vocab) imports this module instead of hard-coding a filename.
Add a lectura to corpus.json and every tool sees it; nothing else to edit.

    python corpus.py            # print the manifest as a table

The manifest, corpus.json, lists each lectura in chronological order with a
two-digit number that prefixes all its files, so that any directory listing —
a USB stick, a Drive folder, an e-reader shelf — sorts the corpus in time.

A lectura whose status is "pendiente" has no files yet and is skipped by every
tool; one whose status is anything else must name its edition file.

Front matter convention, read by the builders and checks (nothing else is
assumed about the file):

    # Title                         first level-1 heading
    ## Subtitle                     first level-2 heading before the text (optional)
    ### Author                      first level-3 heading before the text
    **Place, date**                 first bold line before the text
    **Versión N.N**                 version line, anywhere in the front matter

The reading text begins after the last horizontal rule before the first
numbered paragraph [§1] and ends at "# Aparato crítico". Everything a tool
needs to find in an edition goes through the helpers below.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "corpus.json"
BODY_END = "# Aparato crítico"


# --------------------------------------------------------------------------
# Manifest
# --------------------------------------------------------------------------

def load_manifest(path: Path | None = None) -> dict:
    p = path or MANIFEST
    if not p.exists():
        sys.exit(f"Manifest not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def lecturas(manifest: dict | None = None, built_only: bool = True) -> list[dict]:
    """Lecturas in chronological order; by default only those with an edition."""
    m = manifest or load_manifest()
    out = []
    for rec in m["lecturas"]:
        if built_only and (rec.get("status") == "pendiente" or not rec.get("edition")):
            continue
        out.append(rec)
    return out


def find(key: str, manifest: dict | None = None) -> dict | None:
    """Look a lectura up by number ("02"), slug, or edition filename."""
    for rec in (manifest or load_manifest())["lecturas"]:
        if key in (rec.get("n"), rec.get("slug"), rec.get("edition")):
            return rec
        if rec.get("edition") and Path(key).name == rec["edition"]:
            return rec
    return None


def edition_path(rec: dict) -> Path:
    return ROOT / rec["edition"]


def read_edition(rec: dict) -> str:
    p = edition_path(rec)
    if not p.exists():
        sys.exit(f"Edition not found: {p}")
    return p.read_text(encoding="utf-8")


def stem(rec: dict) -> str:
    """'03-carta-de-jamaica-lectura' — the shared stem of a lectura's outputs."""
    return Path(rec["edition"]).stem


# --------------------------------------------------------------------------
# Front matter and body
# --------------------------------------------------------------------------

def front_matter(md: str) -> dict:
    """Title, subtitle, author, date, version — read from the file itself."""
    if "[§1]" in md:
        head = md[: body_start(md)]
    else:                       # a document without a numbered text: front matter ends at the first rule
        cut = md.find("\n---\n")
        head = md[:cut] if cut > 0 else md
    def first(pat: str) -> str:
        m = re.search(pat, head, re.M)
        return re.sub(r"[*`]", "", m.group(1)).strip() if m else ""
    return {
        "title": first(r"^# (.+)$"),
        "subtitle": first(r"^## (.+)$"),
        "author": first(r"^### (.+)$"),
        "date": first(r"^\*\*([^*\n]+)\*\*\s*$"),
        "version": first(r"^\*\*Versión ([\d.]+)\*\*"),
    }


def body_start(md: str) -> int:
    """Offset of the reading text: after the last '---' before [§1]."""
    i = md.find("[§1]")
    if i < 0:
        return 0
    j = md.rfind("\n---\n", 0, i)
    return j + len("\n---\n") if j >= 0 else i


def body_end(md: str) -> int:
    i = md.find(BODY_END)
    return i if i >= 0 else len(md)


def body(md: str) -> str:
    return md[body_start(md) : body_end(md)]


def paragraphs(md: str) -> dict[int, str]:
    """Numbered paragraphs of the reading text, markdown emphasis stripped."""
    out = {}
    for num, text in re.findall(r"\[§(\d+)\]\s+(.*?)(?=\n\n|\Z)", body(md), re.S):
        out[int(num)] = re.sub(r"\s+", " ", re.sub(r"[*]", "", text)).strip()
    return out


def declared_paragraph_count(md: str) -> int | None:
    """The count the edition itself declares in its criteria ('del 1 al 60')."""
    m = re.search(r"numerados del 1 al (\d+)", md)
    return int(m.group(1)) if m else None


def section(md: str, start: str, level: str = "# ") -> str:
    """Text of a section from its heading to the next heading of the same level."""
    if start not in md:
        return ""
    s = md[md.index(start) :]
    nxt = s.find("\n" + level, len(start))
    return s[:nxt] if nxt > 0 else s


# --------------------------------------------------------------------------

def main() -> int:
    m = load_manifest()
    print(f"{m['project']}\n")
    print(f"{'#':<3} {'date':<11} {'author':<18} {'title':<36} {'status':<12} edition")
    for r in m["lecturas"]:
        print(f"{r['n']:<3} {r['date']:<11} {r['author']:<18} {r['title'][:36]:<36} "
              f"{r['status']:<12} {r.get('edition', '—')}")
    return 0


def sync_versions(write: bool = True) -> list[str]:
    """Decision 52 C2 (2026-11-01): the manifest's `version` is generated from each edition's title page
    («**Versión N.N**»), never hand-edited. `python corpus.py --sync` writes it; returns the lines changed."""
    import json
    path = Path(__file__).with_name("corpus.json")
    m = json.loads(path.read_text(encoding="utf-8"))
    changed = []
    for r in m["lecturas"]:
        if not r.get("edition") or not Path(r["edition"]).exists():
            continue
        v = front_matter(Path(r["edition"]).read_text(encoding="utf-8"))["version"]
        if v and str(r.get("version")) != v:
            changed.append(f"{r['n']}: version {r.get('version')} -> {v}")
            r["version"] = v
    if write and changed:
        path.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return changed


if __name__ == "__main__":
    import sys
    if "--sync" in sys.argv:
        for line in sync_versions(write="--dry" not in sys.argv):
            print(line)
        raise SystemExit(0)
    raise SystemExit(main())


# ---- persons guard (added 2026-10-20, ROADMAP Phase 5 first box) ----------------------------------------------
PERSON_KINDS = ("author", "compiler", "printer", "none")

def persons_problems(rec: dict) -> list[str]:
    """Policy 8.1/8.7: every layer of every base or collation witness must be closed by a dated, sourced person.
    Each person row carries `kind` (author | compiler | printer | none) and `layers` (the siglas whose layer it is;
    `text` for the author's own layer). Each base/collation witness needs a `compiler` row and a `printer` row that
    list its sigla, unless the witness declares `layers_needed` (e.g. ["printer"] for a contemporary printing with
    no editor). A row of kind `none` closes nothing (a discarded witness's people, a publisher, a lead)."""
    out = []
    persons = rec.get("persons") or []
    if not persons:
        return [f"{rec['n']}: persons[] empty (policy 8.7)"]
    for p in persons:
        k = p.get("kind")
        if k not in PERSON_KINDS: out.append(f"{rec['n']}: {p.get('name')} — kind missing or unknown ({k})")
        if k != "none" and (not p.get("death_date") or not p.get("death_source")):
            out.append(f"{rec['n']}: {p.get('name')} — death date or its source not recorded (policy 8.7)")
        elif k != "none" and "por consignar" in str(p.get("death_date")) and "13" not in str(p.get("death_source")):
            out.append(f"{rec['n']}: {p.get('name')} — death date pending and not closed by decision 13 (policy 8.7)")
    for p in persons:   # 2026-11-01 (step 13): a pending row is pending, even if its source names decision 13
        if p.get("kind") in ("compiler", "printer") and (str(p.get("grade")).lower().startswith("pend") or "por consignar" in str(p.get("death_date"))):
            out.append(f"{rec['n']}: {p.get('name')} — printer/compiler row still pending (grade or date); 8.7 not met")
    for p in persons:   # 2026-11-02 (audit): a declared-not-closed row, and a layered person whose term may subsist
        dd = str(p.get("death_date", "")); gr = str(p.get("grade", "")).lower()
        if (p.get("layers") or []) and ("no buscada" in dd or "not searched" in dd or gr.startswith("declar")):
            out.append(f"{rec['n']}: {p.get('name')} — row declared, not closed (8.2: a date, a decision-52 rule, or no layer)")
        m = re.search(r"(1[6-9]\d\d|20\d\d)", dd)
        if m and int(m.group(1)) > 1925 and (p.get("layers") or []):
            out.append(f"{rec['n']}: {p.get('name')} — died {m.group(1)} and carries a layer {p.get('layers')}: the hundred-year term may subsist; classify (no layer, decision 40) or hold the edition (8.1)")
    if not any(p.get("kind") == "author" and "text" in (p.get("layers") or []) for p in persons):
        out.append(f"{rec['n']}: no dated author row for the text layer")
    for w in rec.get("witnesses", []):
        if w.get("role") not in ("base", "collation"): continue
        s = w.get("sigla"); need = w.get("layers_needed", ["compiler", "printer"])
        for kind in need:
            if not any(p.get("kind") == kind and s in (p.get("layers") or []) for p in persons):
                out.append(f"{rec['n']} {s}: no {kind} row in persons[] closes this witness's layer (policy 8.1)")
    return out
