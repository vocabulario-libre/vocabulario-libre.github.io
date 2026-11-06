#!/usr/bin/env python3
"""
drift.py — Verify that each lectura's register of guards still describes it.

Every edition in corpus.json names a register file (NN-slug-register.md): a
table of every guard the edition implements, where to find it, and the policy
standard it serves. Those pointers rot: a section gets renumbered, a file is
renamed, a claim like "the single emendation" stops being true. A register
that misdescribes its document is worse than no register, because it invites a
reader to conclude the whole thing is decorative.

This script resolves each cited location against the edition it belongs to,
and each cited standard against the policy.

    python drift.py           # every built lectura with a register
    python drift.py 02        # one lectura

Resolvable location kinds:
    *Section name*              italicised Spanish section, matched as a heading
    Apparatus § N / § N.x       apparatus section, matched by roman numeral
    Notes § N                   numbered entry in the source-notes register
    Criterion N                 numbered item in the editorial criteria
    `file.py`                   a distributed script (project root or vocab/)
Generic pointers ("Throughout", "Source file") are counted and skipped, since
there is nothing specific to resolve.

Exit status 0 if every specific pointer in every register resolves, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus  # noqa: E402

POLICY = "POLICY-scholarship-and-compliance.md"

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII"}

GENERIC = {
    "throughout",
    "source file",
    "distributed with the document",
    "front matter, apparatus, bibliography",
    "reading text; apparatus § iv",
}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


class Resolver:
    def __init__(self, edition: str) -> None:
        self.ed = edition
        self.ed_folded = fold(edition)
        self.headings = [
            fold(h) for h in re.findall(r"^#{1,3}\s+(.*)$", edition, re.M)
        ]
        self.notes = set(re.findall(r"\*\*§ (\d+)\.", edition))
        crit = re.search(r"\*\*Criterios\*\*(.*?)\n---", edition, re.S)
        self.criteria = (
            len(re.findall(r"^\d+\.", crit.group(1), re.M)) if crit else 0
        )
        self.apparatus = set(
            re.findall(r"^## ([IVX]+)\.", edition, re.M)
        )

    def resolve(self, loc: str) -> tuple[bool, str]:
        raw = loc.strip()
        key = fold(re.sub(r"[*`]", "", raw)).strip()

        if key in GENERIC:
            return True, "generic"

        results = []
        # split compound locations on ';'
        for part in re.split(r";", raw):
            part = part.strip()
            if not part:
                continue
            ok, why = self._resolve_one(part)
            results.append((ok, why))
        if not results:
            return False, "empty"
        if all(ok for ok, _ in results):
            return True, ", ".join(w for _, w in results)
        return False, ", ".join(
            w if ok else f"UNRESOLVED({w})" for ok, w in results
        )

    def _resolve_one(self, part: str) -> tuple[bool, str]:
        p = part.strip()
        clean = re.sub(r"[*`]", "", p).strip()

        if fold(clean) in GENERIC:
            return True, "generic"

        m = re.match(r"^`?([\w_/\-]+\.py)`?$", clean)
        if m:
            f = m.group(1)
            return (Path(f).exists() or Path("vocab", f).exists()), f"file {f}"

        m = re.match(r"^`?([\w_]+\.py)`?\s+docstring$", clean, re.I)
        if m:
            fp = Path(m.group(1))
            return (fp.exists() and '"""' in fp.read_text(encoding="utf-8")), "docstring"

        m = re.search(r"apparatus\s*§\s*(\d+|[IVX]+)(?:\.(\w+))?", clean, re.I)
        if m:
            tok = m.group(1)
            roman = tok if tok.isalpha() else ROMAN.get(int(tok), tok)
            if roman not in self.apparatus:
                return False, f"apparatus § {roman}"
            if m.group(2):
                sub = m.group(2)
                # Subsections appear either as their own heading (### III.a)
                # or as a bold numbered item inside the section (**1. ...**).
                if f"### {roman}.{sub}" in self.ed:
                    return True, f"apparatus § {roman}.{sub}"
                block = self.ed[self.ed.index(f"## {roman}."):]
                nxt = block.find("\n## ", 4)
                block = block[:nxt] if nxt > 0 else block
                if re.search(rf"^\*\*{re.escape(sub)}\.\s", block, re.M):
                    return True, f"apparatus § {roman}.{sub}"
                return False, f"apparatus § {roman}.{sub}"
            return True, f"apparatus § {roman}"

        m = re.search(r"notes\s*§\s*(\d+)", clean, re.I)
        if m:
            return (m.group(1) in self.notes), f"notes § {m.group(1)}"

        m = re.search(r"criterion\s+(\d+)", clean, re.I)
        if m:
            return (int(m.group(1)) <= self.criteria), f"criterion {m.group(1)}"

        m = re.search(r"build script \(`?(\w+)`?\)", clean, re.I)
        if m:
            src = Path("build_pdf.py")
            return (src.exists() and m.group(1) in src.read_text(encoding="utf-8")), (
                f"build script/{m.group(1)}"
            )

        # Otherwise: an italicised Spanish section name
        name = fold(clean)
        if any(name in h or h in name for h in self.headings):
            return True, f"section “{clean}”"
        if name in self.ed_folded:
            return True, f"text “{clean}”"
        return False, f"section “{clean}”"


def check_register(rec: dict, policy: str) -> tuple[int, int, int]:
    """Returns (resolved, generic, drifted) for one lectura."""
    reg_path = Path(rec["register"])
    if not reg_path.exists():
        print(f"  DRIFT  {rec['n']}: register file missing: {reg_path}")
        return 0, 0, 1
    register = reg_path.read_text(encoding="utf-8")
    edition = corpus.read_edition(rec)
    r = Resolver(edition)

    rows = re.findall(
        r"^\|\s*(\d+[a-z]?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$", register, re.M
    )
    rows = [x for x in rows if x[0][0].isdigit()]
    print(f"\n==== {rec['n']} · {rec['title']} — {len(rows)} guards in {reg_path}")

    failures = []
    generic = 0
    for num, guard, loc, std in rows:
        ok, why = r.resolve(loc)
        if why == "generic":
            generic += 1
            continue
        if not ok:
            failures.append((num, loc, why))
            print(f"  DRIFT  guard {num:>4}  → {loc}")
            print(f"                     {why}")

    std_cited = {s.strip() for _, _, _, std in rows for s in std.split(",")}
    std_defined = set(re.findall(r"\*\*(\d+\.\d+(?:\.\d+)?) ", policy))
    missing_std = sorted(s for s in std_cited if s and s not in std_defined)
    if missing_std:
        print(f"  DRIFT  guards cite undefined standards: {missing_std}")
        failures.append(("standards", ",".join(missing_std), "undefined"))

    resolved = len(rows) - len(failures) - generic
    print(f"  {resolved} resolved, {generic} generic (skipped), {len(failures)} drifted")
    return resolved, generic, len(failures)


def main() -> int:
    if not Path(POLICY).exists():
        sys.exit(f"Not found: {POLICY}")
    policy = Path(POLICY).read_text(encoding="utf-8")

    recs = [r for r in corpus.lecturas() if r.get("register")]
    if len(sys.argv) > 1:
        recs = [corpus.find(k) for k in sys.argv[1:]]
        if any(r is None or not r.get("register") for r in recs):
            sys.exit(f"Not in manifest, or no register: {sys.argv[1:]}")

    print("REGISTER DRIFT CHECK")
    tot_ok = tot_gen = tot_bad = 0
    for rec in recs:
        ok, gen, bad = check_register(rec, policy)
        tot_ok += ok; tot_gen += gen; tot_bad += bad

    print(f"\n{tot_ok} resolved, {tot_gen} generic (skipped), {tot_bad} drifted "
          f"across {len(recs)} register(s)")
    if tot_bad:
        print("\nA register no longer describes its edition. Fix the register, "
              "or the edition, before relying on either.")
        return 1
    print("\nPASS: every specific pointer in every register resolves.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
