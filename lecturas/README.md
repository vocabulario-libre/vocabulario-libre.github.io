# Lecturas de los libertadores

Reading editions of texts by Bolívar, San Martín and O'Higgins, prepared for
personal study of Spanish, each with a critical apparatus, graded source notes
and a vocabulary trainer built from it. One standard governs all of them:
`POLICY-scholarship-and-compliance.md`.

The authors' texts are public domain. Everything added here — apparatus,
notes, glosses, definitions, code — is released under CC0 1.0.

This folder is the release: the editions, the documents that govern them, the
trainer, and the programs that build and check them.

---

## Files

Lecturas are numbered in chronological order; the two-digit number prefixes
every file of a lectura, so any folder — a USB stick, a Drive folder, an
e-reader — sorts the corpus in time.

| File | |
|---|---|
| `00-lecturas-de-los-libertadores.md` / `.pdf` / `.epub` | **Governing document**, bilingual (Spanish then English): the corpus in order with signatory, drafting, witnesses, status; rights derivation per author; the shared conventions. Start here. |
| `NN-slug-lectura.md` | **Source** of a lectura. The PDF and the EPUB are built from it. |
| `NN-slug-lectura.pdf` / `.epub` | Print and e-reader editions, built. |
| `NN-slug-register.md` | The register of the lectura's guards. |
| `POLICY-scholarship-and-compliance.md` / `.pdf` | The standard. |
| `METHOD-grammar-layer.md` / `.pdf` | How the sense of each grammatical word in its place is decided and certified. |
| `PROVENANCE.md` | The rights record of the release: every witness, the rights line read on its provider's page, the evidence files verbatim. |
| `LICENSE` | CC0 1.0. |
| `MANIFEST.sha256` | One SHA-256 for each file of the release. |
| `index.html`, `index.en.html`, `index.ja.html` | The main page of the folder, in Spanish, English and Japanese: the cards of the day, the trainer, every lectura with its files, the documents. Built by `build_index.py` from `corpus.json` and the trainer. Each page is one file: the style and the one script, which runs the cards, are inside it, and nothing is fetched. |
| `icon-192.png` | The project's mark. `build_index.py` writes it into the main pages, beside the name. |
| `PRIMER-sanskrit.md` / `.html` / `.epub`, `PRIMER-avestan.md` / `.html` / `.epub` | The primers: the tables the project writes Sanskrit and Avestan forms with, in Spanish and English, each as Markdown, a page and an EPUB. They are made from the project's tables, which are not in this folder; the folder holds them as made. |
| `VocabularioAvestan.otf`, `VocabularioAvestan.woff2` | The font of the Avestan script in the Avestan primer. `PROVENANCE.md` gives its account. |
| `como-usar.html`, `como-usar.en.html`, `como-usar.ja.html` | «How to use», in Spanish, English and Japanese: what is here, how it is read, how the trainer is used, how it is checked. Built by `build_pages.py`. |
| `copiar-y-cambiar.html`, `copiar-y-cambiar.en.html`, `copiar-y-cambiar.ja.html` | «Copy and change», in Spanish, English and Japanese: how the folder is had, how it is changed, what its check checks. Built by `build_pages.py`. |
| `proximos-cambios.html`, `proximos-cambios.en.html`, `proximos-cambios.ja.html` | «Upcoming changes», in Spanish, English and Japanese: what is being made now and what comes after, as a list. Built by `build_pages.py`. |
| `vocab/` | The trainer, `vocab/flashcards.html`, with its data and its builders. `vocab/README.md` describes it. |
| `corpus.json` | **The manifest.** Every lectura, its number, status and files. Every program reads it. |
| `corpus.py` | Shared helpers: manifest, front matter, body boundaries. `python corpus.py` prints the table. |
| `build_pdf.py`, `build_epub.py`, `build_index.py`, `build_pages.py` | The builders. |
| `check_folder.py` | The check of this folder. |
| `anon.py` | Names any file that carries a person's name or address, or a trace of the machine it was made on. |
| `verify.py`, `ortografia.py` | The checks of the texts: counts, and spelling by the rules in `ortografia-reglas.tsv` and `ortografia-conservadas.tsv`. |
| `compliance.py`, `drift.py`, `release.py`, `dist.py` | The gate of the workshop and the programs that write a release (see «Check»). |

## Read

Open the `.pdf` (bookmarked) or the `.epub` (reflowable, for phones) of any
lectura. Each contains the text in numbered paragraphs, the critical apparatus,
source notes graded for confidence, bibliography, chronology, reference key,
glossary, revision history and rights statement.

## Study vocabulary

Open `vocab/flashcards.html` in a browser: the text of each edition beside its
cards. `vocab/README.md` describes the panes, the card sets and the keys.

## Change and rebuild

The `.md` file of a lectura is its source. The trainer is built from the
editions and from the meaning files of each lectura, `vocab/NN/`. The main
pages are built from `corpus.json` and from the trainer, so `build_index.py`
runs after the trainer is built. A lectura is
named by number, slug or filename; without a name a builder builds every one.

    python build_pdf.py 12
    python build_epub.py 12
    python build_pdf.py
    python build_epub.py
    python build_pdf.py -i POLICY-scholarship-and-compliance.md -o POLICY-scholarship-and-compliance.pdf
    python build_pdf.py -i METHOD-grammar-layer.md -o METHOD-grammar-layer.pdf
    python build_pages.py
    cd vocab
    python extract_vocab.py
    python build_app.py
    cd ..
    python build_index.py

`vocab/extract_vocab.py` writes `vocab/vocab.json`, which `vocab/build_app.py`
reads; it is an intermediate and no part of the release.

`build_pdf.py` needs `reportlab`, and `pyphen` for the hyphenation the released
PDFs carry. Everything else is Python's standard library. The programs run
on Python 3.9 or later.

## Check

    python check_folder.py

It compares every file with `MANIFEST.sha256` and names what has changed since
the release. It copies the folder to a temporary directory, runs the builders
there and names each PDF, EPUB or page, and the trainer, where it is out of date
with its source. It runs `verify.py` (word and paragraph counts) and `ortografia.py`
(the reading texts against the orthography of 2010). It runs `anon.py`, which
names any file that carries a person's name or address, or a trace of the
machine it was made on: a path, a user's name, a time zone. It writes nothing
in the folder. Its last line is `FOLDER CHECK PASS`, or `FOLDER CHECK FAIL` and what
failed.

After a change: rebuild, then check. A changed file is named and is not a
failure; a built file left behind its source is, and so is a file `anon.py`
names.

The bytes of a PDF or an EPUB depend on the system that builds it. Where the
bytes differ the check compares the content and says which it found.

`compliance.py`, `drift.py` and `release.py` are the gate of the workshop in
which the editions were made. They read that workshop's `work/` folder — the
scripts, logs and evidence files behind each edition — and do not pass in this
folder alone. The evidence is here, in `PROVENANCE.md`.

## Use, distribution and support

Everything here may be read, copied, redistributed and adapted by anyone, for
any purpose: the texts are public domain and everything added is CC0. Hosting
it, mirroring it, or offering it with a donation or patronage link is within
those terms, provided nothing released under the policy is ever gated behind
payment. Policy § 4 and § 8 set out the standards — first-publication checks,
text-not-files, moral rights, a dependency audit, and the separation of the
workshop from the distributed set.

**Release condition (policy § 8).** Nothing is released until every edition in
the release rests only on dates — public domain by age in every layer — and
on the compiler's CC0 waiver, with the evidence inside the release
(`PROVENANCE.md`). A pending item, a declared exception, an unread rights
line, a modern text layer or an open rights question holds that edition back.
Donations, patronage, subscriptions and advertising on the hosting page are
welcome and never a condition of access; no advertisement, tracker, script or
asset of a third party ever goes inside a distributed file. This release
carries no support or hosting link of its own; if the hosting page offers one,
it lives on that page and nowhere in these files, and this paragraph is where a
later release would name it.

## What this is not

Not a critical edition, and not to be cited as an established text. Each
lectura records decisions about its text, defines words and identifies names;
it does not interpret what the text says. Where it conflicts with a source,
the source is right and this is wrong.
