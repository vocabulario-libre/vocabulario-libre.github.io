#!/usr/bin/env python3
"""dist.py — build or check the distributable set (policy 4.13).

The distributable set is derived from the manifest by allowlist: the
governing document, every lectura with status *publicada* (source, PDF,
EPUB, register, vocabulary meaning files), the policy (source and PDF), the
manifest, the scripts that regenerate everything, and the trainer. Nothing
under work/ is ever included; ROADMAP.md, research reports, provider files,
generated intermediates (vocab/vocab.json) and a user's own progress file
(vocab/lexico-progreso.json) stay in the workshop.

    python dist.py            # write dist/ from scratch and dist/MANIFEST.sha256
    python dist.py --list     # print the allowlist
    python dist.py --check    # verify the allowlist and, if dist/ exists, its contents

The check is also run by compliance.py. Exit status 0 when sound.
"""
from __future__ import annotations
import hashlib, shutil, sys
from pathlib import Path
import corpus

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
SCRIPTS = ["index.html", "build_index.py", "corpus.py", "build_pdf.py", "build_epub.py", "compliance.py", "drift.py",
           "verify.py", "ortografia.py", "dist.py", "release.py", "LICENSE", "ortografia-reglas.tsv",
           "ortografia-conservadas.tsv", "vocab/extract_vocab.py", "vocab/build_app.py",
           "vocab/app_template.html", "vocab/README.md"]
ALLOWED_SUFFIXES = {".md", ".pdf", ".epub", ".json", ".py", ".tsv", ".html", ""}


def allowlist() -> list[str]:
    m = corpus.load_manifest()
    files = ["README.md", m["policy"], Path(m["policy"]).with_suffix(".pdf").name,
             "corpus.json", m["governing"], Path(m["governing"]).with_suffix(".pdf").name,
             Path(m["governing"]).with_suffix(".epub").name, "vocab/flashcards.html"] + SCRIPTS
    for rec in m["lecturas"]:
        if rec.get("status") != "publicada":
            continue
        st = corpus.stem(rec)
        files += [rec["edition"], st + ".pdf", st + ".epub", rec["register"],
                  f"{rec['vocab']}/glosses.json", f"{rec['vocab']}/definitions.json"]
    return sorted(dict.fromkeys(files))


def provider_files() -> set[str]:
    p = ROOT / "work" / "PROVIDER-FILES.tsv"
    if not p.exists():
        return set()
    rows = [l.split("\t")[0].strip() for l in p.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return set(rows)


def check(verbose: bool = True) -> int:
    bad: list[str] = []
    files = allowlist()
    prov = provider_files()
    for f in files:
        p = Path(f)
        if p.parts and p.parts[0] == "work":
            bad.append(f"under work/: {f}")
        if p.suffix not in ALLOWED_SUFFIXES:
            bad.append(f"file type not allowed: {f}")
        if not (ROOT / f).exists():
            bad.append(f"missing: {f}")
        if f in prov:
            bad.append(f"listed in work/PROVIDER-FILES.tsv: {f}")
        if f == "ROADMAP.md" or "/research/" in f or f.startswith("work"):
            bad.append(f"workshop file: {f}")
    if DIST.exists():
        have = sorted(str(p.relative_to(DIST)) for p in DIST.rglob("*")
                      if p.is_file() and p.name not in ("MANIFEST.sha256", "PROVENANCE.md"))
        extra = sorted(set(have) - set(files))
        missing = sorted(set(files) - set(have))
        for e in extra:
            bad.append(f"dist/ holds a file not in the allowlist: {e}")
        for mfile in missing:
            bad.append(f"dist/ lacks: {mfile}")
        for f in set(have) & set(files):
            if (DIST / f).read_bytes() != (ROOT / f).read_bytes():
                bad.append(f"dist/ copy differs from source: {f}")
    if verbose:
        for b in bad:
            print(f"  FAIL  {b}")
        state = "present and identical" if DIST.exists() else "not built"
        print(f"  {'FAIL' if bad else 'PASS'}  distribution: {len(files)} allowlisted files, nothing from work/, dist/ {state}")
    return 1 if bad else 0


def build() -> int:
    if check(verbose=False) and not DIST.exists():
        pass
    if DIST.exists():
        shutil.rmtree(DIST)
    files = allowlist()
    lines = []
    for f in files:
        src, dst = ROOT / f, DIST / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        lines.append(f"{hashlib.sha256(src.read_bytes()).hexdigest()}  {f}")
    (DIST / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote dist/ — {len(files)} files, {sum((ROOT / f).stat().st_size for f in files):,} bytes; MANIFEST.sha256")
    return check()


if __name__ == "__main__":
    if "--list" in sys.argv:
        print("\n".join(allowlist()))
    elif "--check" in sys.argv:
        sys.exit(check())
    else:
        sys.exit(build())
