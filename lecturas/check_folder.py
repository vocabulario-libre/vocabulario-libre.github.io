#!/usr/bin/env python3
"""check_folder.py — the check of this folder, run in the folder alone.

    python check_folder.py            # the folder this file is in
    python check_folder.py FOLDER     # another copy of the release

Four things, in order:

  1. Against the release. Every file named in MANIFEST.sha256 is hashed and
     compared; what has changed since the release, what is gone and what is
     new is named. A change is not a failure: the folder may be changed.
  2. Built files against their sources. The folder is copied to a temporary
     directory and the builders are run there: the PDFs and EPUBs they build, the
     trainer, the index and the pages. Each file a builder writes is compared with the
     folder's. A file whose content differs from what the folder's sources
     build is out of date and is named.
  3. The texts. verify.py (word and paragraph counts) and ortografia.py
     (criterion 1 on every reading text), run on the same copy.
  4. Persons and machines. anon.py, on the folder as it stands. It names any
     file that carries a person's name or address, or a trace of the machine
     it was made on, and any file of a type it does not read. What it names
     is a failure.

The last line is FOLDER CHECK PASS, or FOLDER CHECK FAIL with what failed.
Exit status 0 on PASS. Nothing is written in the folder.

How built files are compared. First by bytes. The bytes of a built file depend
on the system that builds it: its compression library for a PDF or an EPUB,
the system field of each zip entry for an EPUB, its line endings for a page.
Where the bytes differ, the content is compared: a PDF with every stream
decompressed, an EPUB entry by entry (name, order, date, data), a page with
its line endings set aside. «Same content, other bytes» is not a failure. Where the
content differs and no file has changed since the release, the folder is the
release itself, shown by its hashes, and the difference lies in the tools of
this system (reportlab, pyphen); it is said and is not a failure.

Standard library only. The builders need what they need: build_pdf.py needs
reportlab, and pyphen for the hyphenation the released PDFs carry.
"""
from __future__ import annotations
import base64, hashlib, json, os, re, shutil, subprocess, sys, tempfile, zipfile, zlib
from pathlib import Path

NOT_LISTED = {"MANIFEST.sha256", "PROVENANCE.md"}      # written with the release, not named in its manifest
BY_PRODUCTS = {"vocab/vocab.json"}                     # extract_vocab.py's intermediate: build_app.py reads it
CACHE = "__pycache__"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def files_of(folder: Path) -> list[str]:
    out = []
    for p in folder.rglob("*"):
        if p.is_file() and CACHE not in p.parts:
            out.append(p.relative_to(folder).as_posix())
    return sorted(out)


# ---- 1. against the release -----------------------------------------------------------------------------------
def against_release(folder: Path) -> tuple[list[str], list[str], list[str], int]:
    listed = {}
    for line in (folder / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(None, 1)
            listed[name.strip()] = digest
    changed = [f for f, d in sorted(listed.items()) if (folder / f).is_file() and sha256(folder / f) != d]
    gone = [f for f in sorted(listed) if not (folder / f).is_file()]
    new = [f for f in files_of(folder) if f not in listed and f not in NOT_LISTED and f not in BY_PRODUCTS]
    return changed, gone, new, len(listed)


# ---- 2. the content of a built file, apart from how the system packed it --------------------------------------
PDF_OBJECT = re.compile(rb"(\d+ \d+) obj\n(.*?)\nendobj\n", re.S)


def pdf_content(data: bytes) -> list[bytes] | None:
    """A PDF as build_pdf.py writes it, every stream decoded; None if it is not read whole."""
    try:
        out, pos = [], 0
        for m in PDF_OBJECT.finditer(data):
            out.append(data[pos:m.start()])
            body = m.group(2)
            at = body.find(b"stream\n")
            if at != -1:
                if not body.endswith(b"endstream"):
                    return None
                head, raw = body[:at], body[at + 7:-len(b"endstream")]
                for name in re.findall(rb"/(\w+Decode)", head):
                    if name == b"ASCII85Decode":
                        raw = raw.strip()
                        raw = base64.a85decode(raw[:-2] if raw.endswith(b"~>") else raw)
                    elif name == b"FlateDecode":
                        raw = zlib.decompress(raw)
                    else:
                        return None
                out.append(m.group(1) + b" " + re.sub(rb"/Length \d+", b"/Length", head) + raw)
            else:
                out.append(m.group(1) + b" " + body)
            pos = m.end()
        tail = data[pos:]                          # the cross-reference table, the trailer, the offset of the table
        a, b = tail.find(b"trailer"), tail.find(b"startxref")
        if not out or a == -1 or b == -1 or not tail.startswith(b"xref"):
            return None
        out.append(tail[a:b])                      # the table and its offset follow from the lengths: left out
        return out
    except Exception:
        return None


def epub_content(path: Path) -> list[tuple] | None:
    try:
        with zipfile.ZipFile(path) as z:
            return [(i.filename, i.date_time, i.compress_type, z.read(i)) for i in z.infolist()] + [("", z.comment)]
    except Exception:
        return None


def same_content(a: Path, b: Path) -> bool:
    if a.suffix == ".pdf":
        x, y = pdf_content(a.read_bytes()), pdf_content(b.read_bytes())
    elif a.suffix == ".epub":
        x, y = epub_content(a), epub_content(b)
    else:                                               # a page: the line endings are the system's
        return a.read_bytes().replace(b"\r\n", b"\n") == b.read_bytes().replace(b"\r\n", b"\n")
    return x is not None and x == y


def builders(folder: Path) -> list[tuple[list[str], str]]:
    """The commands of the README's «Change and rebuild», for every file: (arguments, directory)."""
    m = json.loads((folder / "corpus.json").read_text(encoding="utf-8"))
    cmds = [(["build_pdf.py"], "."), (["build_epub.py"], ".")]
    for key in ("policy", "method"):
        if m.get(key):
            cmds.append((["build_pdf.py", "-i", m[key], "-o", str(Path(m[key]).with_suffix(".pdf"))], "."))
    cmds += [(["extract_vocab.py"], "vocab"), (["build_app.py"], "vocab"), (["build_index.py"], "."), (["build_pages.py"], ".")]
    return cmds


def run(args: list[str], cwd: Path) -> tuple[int, str]:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable] + args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def tail(text: str, n: int = 12) -> str:
    return "\n".join("      " + line for line in text.rstrip().splitlines()[-n:])


def tools() -> str:
    found = [f"Python {sys.version.split()[0]}"]
    for name in ("reportlab", "pyphen"):
        try:
            mod = __import__(name)
            found.append(f"{name} {getattr(mod, 'Version', None) or getattr(mod, '__version__', '')}".strip())
        except Exception:
            found.append(f"{name} not installed")
    found.append(f"zlib {getattr(zlib, 'ZLIB_RUNTIME_VERSION', zlib.ZLIB_VERSION)}")
    return ", ".join(found)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")       # a console that lacks a letter prints a mark, not an error
    folder = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
    failed: list[str] = []
    print(f"Folder: {folder.name}")                    # its name, not its path: what is printed may be passed on
    print(f"Tools:  {tools()}")
    if not (folder / "MANIFEST.sha256").is_file() or not (folder / "corpus.json").is_file():
        print("  FAIL  MANIFEST.sha256 or corpus.json is not here: this is not a folder of the release")
        print("FOLDER CHECK FAIL: not a folder of the release")
        return 1

    # 1
    print("\n1. Against the release (MANIFEST.sha256)")
    changed, gone, new, n = against_release(folder)
    for label, names in (("changed", changed), ("gone", gone), ("new", new)):
        for f in names:
            print(f"  {label:8}{f}")
    intact = not changed and not gone
    print(f"  {n} files named: {n - len(changed) - len(gone)} as released, {len(changed)} changed, {len(gone)} gone; "
          f"{len(new)} new")

    # 2
    print("\n2. Built files against their sources")
    with tempfile.TemporaryDirectory(prefix="check_folder-") as tmp:
        copy = Path(tmp) / "folder"
        shutil.copytree(folder, copy, ignore=shutil.ignore_patterns(CACHE))
        before = {f: (copy / f).stat().st_mtime_ns for f in files_of(copy)}
        for args, where in builders(copy):
            code, text = run(args, copy / where)
            if code:
                print(f"  FAIL  python {' '.join(args)}  (in {where}) — exit {code}\n{tail(text)}")
                failed.append(f"a builder did not run ({args[0]})")
        built = [f for f in files_of(copy) if f not in BY_PRODUCTS and before.get(f) != (copy / f).stat().st_mtime_ns]
        same, packed, stale = [], [], []
        for f in built:
            here, there = folder / f, copy / f
            if here.is_file() and here.read_bytes() == there.read_bytes():
                same.append(f)
            elif here.is_file() and same_content(here, there):
                packed.append(f)
            else:
                stale.append(f)
        print(f"  {len(built)} files built: {len(same)} byte for byte the folder's; {len(packed)} the same content, other bytes; "
              f"{len(stale)} other content")
        if packed:
            kinds = sorted({Path(f).suffix for f in packed})
            print("  same content, other bytes (" + ", ".join(f"{sum(1 for f in packed if Path(f).suffix == k)} {k}" for k in kinds)
                  + "): the compression or the line endings of this system are not those of the system the folder's "
                  "files were built on")
        if stale and intact:
            print("  other content, and no file has changed since the release: the folder is the release; the tools of "
                  "this system build otherwise (reportlab, pyphen)")
            for f in stale:
                print(f"    builds otherwise here: {f}")
        elif stale:
            for f in stale:
                print(f"  FAIL  out of date — rebuild: {f}")
            failed.append(f"{len(stale)} built file(s) out of date")

        # 3
        print("\n3. The texts")
        for script in ("verify.py", "ortografia.py"):
            code, text = run([script], copy)
            last = [line for line in text.rstrip().splitlines() if line.strip()][-1:] or [""]
            if code:
                print(f"  FAIL  python {script} — exit {code}\n{tail(text)}")
                failed.append(script)
            else:
                print(f"  PASS  python {script} — {last[0].strip()[:110]}")

    # 4
    print("\n4. Persons and machines")
    program = Path(__file__).resolve().parent / "anon.py"
    if not program.is_file():
        print("  FAIL  anon.py is not beside check_folder.py: not run")
        failed.append("anon.py did not run")
    else:
        import importlib.util
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location("anon", program)
        anon = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(anon)
        report = anon.check(folder)
        count = 0
        for _, title, faults, detail in report["parts"]:
            print(f"  {'FAIL' if faults else 'PASS'}  {title}{detail}")
            for x in faults[:20]:
                print(f"          {x}")
            if len(faults) > 20:
                print(f"          … and {len(faults) - 20} more")
            count += len(faults)
        for note in report["notes"]:
            print(f"  NOTE  {note}")
        if count:
            failed.append(f"anon.py names {count}")

    print()
    if failed:
        print("FOLDER CHECK FAIL: " + "; ".join(dict.fromkeys(failed)))
        return 1
    print("FOLDER CHECK PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
