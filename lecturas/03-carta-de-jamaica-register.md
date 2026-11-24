# Register of guards — Carta de Jamaica

Lectura 03 · `03-carta-de-jamaica-lectura.md`

Every device implemented in this edition, with the location where a reader can find it and the standard in `POLICY-scholarship-and-compliance.md` that it serves. This file is checked by `drift.py`: every specific location below must resolve in the edition, and every standard cited must exist in the policy.

Until policy v1.3 this register lived inside the policy as § 5. It was moved here so that each lectura carries the register that describes it, and the policy describes none in particular.

Edition published (v2.5, 2026-11-03). First published as v2.4 on 2026-11-02. First published as v2.3 on 2026-11-01. First published as v2.2 on 2026-11-01.

## 1. Declaratory guards

| # | Guard | Location | Standard |
|---|---|---|---|
| 1 | Purpose statement: personal study only, not a critical edition, not to be cited as an established text | *Advertencia*, front matter | 4.6 |
| 2 | Rights statement: text public domain, compiler's layer released CC0 | *Advertencia*; *Derechos y propósito* | 4.5 |
| 3 | Affirmative declaration that no third-party matter is incorporated undeclared | *Advertencia* | 4.4 |
| 4 | Errata clause directing corrections to the originals | *Derechos y propósito* | 4.7 |
| 5 | Licence and positive terms of use stated; support never a condition of access | *Derechos y propósito* | 4.6 |

## 2. Methodological guards

| # | Guard | Location | Standard |
|---|---|---|---|
| 6 | Sigla table naming all three witnesses (**M**, **Y**, **V**) | *Nota sobre el texto* | 3.1 |
| 7 | Five numbered editorial criteria stated before the text | *Nota sobre el texto* | 3.2 |
| 8 | Transmission history explaining how the witnesses relate | *Nota sobre el texto* | 3.1 |
| 9 | Explicit statement that nothing has been omitted or abridged | Criterion 5 | 2.8 |
| 10 | Declaration that the collation rests on the 2015 transcription, not the manuscript | *Nota sobre el texto*; Notes § 1 | 3.7 |

## 3. Textual guards

| # | Guard | Location | Standard |
|---|---|---|---|
| 11 | Apparatus § I: eight restitutions, each with source sigla | *Aparato crítico* | 3.3 |
| 12 | Apparatus § II: 25-row table of corrections, adopted reading against rejected reading with sigla | *Aparato crítico* | 3.3 |
| 13 | Apparatus § III: all nineteen divergences from the best witness, grouped in five classes by editorial risk, each reversible | *Aparato crítico* | 3.4 |
| 13a | The single true emendation on grounds of sense isolated in its own subsection as the document's highest-risk decision | Apparatus § III.a | 3.4 |
| 13b | Seven readings marked *duda de digitalización* where mediation makes the source of the anomaly undeterminable, naming what would resolve it | Apparatus § III | 3.4.1, 3.7 |
| 13c | Dropped editorial mark from the source transcription recorded so it cannot read as oversight | Apparatus § III.e | 2.8 |
| 13d | *Nota metodológica* recording that a previous version misdescribed its own method | Apparatus § III | 2.9 |
| 14 | Italic marking of the closing sentences, which the manuscript does not authorize | Reading text; Apparatus § IV | 3.5 |
| 15 | Refusal to print the signature "Bolívar" that modern versions add without warrant | Apparatus § IV | 3.6 |
| 16 | Date left in its manuscript position, with the divergence from common practice noted | Apparatus § IV | 3.3 |
| 17 | Restored paragraph quoted in full in the apparatus, not merely referenced | Apparatus § I.1 | 3.3 |

## 4. Epistemic guards

| # | Guard | Location | Standard |
|---|---|---|---|
| 18 | Master register of eight source notes, each with a stated confidence grade | *Notas sobre las fuentes* | 3.8 |
| 19 | Mediation chain disclosed with named OCR failure modes, separating reliable content differences from unverified orthographic detail | Notes § 1 | 3.7 |
| 20 | Volume number omitted from the bibliography because sources disagree; discrepancy recorded instead of resolved | Notes § 2; Apparatus § V | 2.2 |
| 21 | Printer's name declared a conjecture, with both variant spellings given | Notes § 3 | 2.3 |
| 22 | Secondary-source provenance flagged for the English printings | Notes § 4 | 2.3 |
| 23 | Transcribed-from-image reservation on ISBN and depósito legal | Notes § 5 | 2.3 |
| 24 | Unverifiable death date removed, removal noted, argument shown not to depend on it | Notes § 6 | 3.9 |
| 25 | "Censored paragraph" claim attributed to its official source and expressly not adopted; innocent explanation offered | Notes § 7; Apparatus § I.1 | 2.6 |
| 26 | High-confidence items graded too, so grading is not a euphemism for doubt | Notes § 8 | 2.3 |
| 27 | Errata clause: unverified data flagged one by one in the Notas and the reference key; corrections directed to the originals; errata found in use corrected in later versions and recorded in the Historial | *Advertencia* | 4.7 |

## 5. Redundancy guards

| # | Guard | Location | Standard |
|---|---|---|---|
| 28 | Eight point-of-use footnotes, each with a one-line gloss and a pointer to its section in the master register | Throughout | 2.4 |
| 29 | Every material uncertainty disclosed in at least two places; the volume-number problem in three | Front matter, apparatus, bibliography | 2.4 |
| 30 | Footnotes kept on the page with the text that calls them | Build script (`CondPageBreak`) | 2.4 |

## 6. Verification and reproducibility guards

| # | Guard | Location | Standard |
|---|---|---|---|
| 31 | `verify.py`: shingle-based content check reporting any passage in a source absent from the edition (extended by guard 45) | Distributed with the document | 2.7, 3.10 |
| 32 | Verification method documented, including its known false-positive behaviour on legitimate variants | `verify.py` docstring | 3.10 |
| 33 | Word and paragraph counts reported for the body alone, excluding apparatus | `verify.py` | 2.7 |
| 34 | `build_pdf.py`: deterministic render from the plain-text source, no network, single dependency | Distributed with the document | 3.11 |
| 35 | Markdown retained as canonical, human-readable and diffable | Source file | 3.11 |

## 7. Guards added after policy v1.1

| # | Guard | Location | Standard |
|---|---|---|---|
| 36 | Folio concordance: all 31 manuscript breaks located mechanically, each unambiguous | Apparatus § VI | 3.5, 3.7 |
| 37 | Damage point declared: the supplied word is marked as a restitution over a lacuna, and the extent of the loss stated as unknown | Apparatus § VII | 3.5, 2.2 |
| 38 | Normalization table closing criterion 3, including three deliberate non-normalizations with reasons | Apparatus § VIII | 3.2 |
| 39 | Paragraph numbering 1–60, declared as the edition's own and not the sources' | Criterion 6 | 3.3 |
| 40 | Every apparatus reference located by script rather than from memory, after 17 of 19 hand-estimated references proved wrong | Apparatus § II, § III | 2.7 |
| 41 | No-interpretation rule stated before any content | *Advertencia* | 2.10, 3.12 |
| 42 | Glossary confined to word meanings; definitions independently written, taken from no dictionary | *Glosario* | 3.12, 4.4 |
| 43 | Reference key confined to identifying persons, places and events | *Referencias del texto* | 2.10, 3.12 |
| 44 | `compliance.py`: 31 automated checks covering declarations, structure, references, footnotes, grading and rights hygiene | Distributed with the document | 2.7, 3.10 |
| 45 | Evaluative language blocked mechanically, so interpretation cannot re-enter through later edits | `compliance.py` | 3.12 |
| 46 | `verify.py` reconciles every difference against the apparatus automatically, reporting explained, orthographic and unexplained separately | `verify.py` | 2.7 |
| 47 | EPUB built from the same source, standard library only | `build_epub.py` | 3.11 |
| 48 | `drift.py`: verifies that every location cited in this register still resolves in the edition | `drift.py` | 2.5 |
| 49 | Public-domain status derived from the author's death and the printing date, stated rather than assumed | *Derechos y propósito* | 4.1 |
| 50 | Underlying text, transcription, third-party apparatus and this edition assessed as four separate layers | *Derechos y propósito* | 4.2 |
| 51 | Divergence between jurisdictions on rights in transcriptions and in first publication of unpublished works acknowledged rather than glossed | *Derechos y propósito* | 4.3 |
| 52 | Errata clause frames unverified data as defects to be corrected against the sources, not as misrepresentation | *Derechos y propósito*; *Historial de revisiones* | 4.7, 4.8 |
| 53 | Sources named before the text and every reading traced to one, so that presentation never substitutes for attribution | *Nota sobre el texto*; *Aparato crítico* | 2.1 |
| 54 | Stated counts reconciled against content mechanically, after two prose counts were found not to match | `compliance.py` | 2.7 |
| 55 | Accentuation conforms to the academic norm of 2010 and criterion 1 says so, after the text was found to follow an older convention | Criterion 1 | 3.2 |

---

## 8. Guards added with policy v1.3

| # | Guard | Location | Standard |
|---|---|---|---|
| 56 | Edition file carries its chronological number in the corpus; the renaming is recorded, not silent | *Historial de revisiones* | 2.9 |
| 57 | Register of guards relocated from the policy to this file, so each lectura is described by its own register | `drift.py` | 2.5 |
| 58 | Manifest `corpus.json` is the only place the edition is named; every tool reads it | `corpus.py` | 3.11 |

## 9. Guards added with policy v1.4

| # | Guard | Location | Standard |
|---|---|---|---|
| 59 | First publication recorded and graded; publication right excluded | *Derechos y propósito* | 4.9 |
| 60 | Text, not provider files; Wikisource notice scoped to contributors' additions | *Derechos y propósito* | 4.10 |
| 61 | Moral rights: attribution, no altered reading as the author's, interventions reversible | *Derechos y propósito* | 4.11 |
| 62 | Dependencies listed with licences; nothing third-party embedded; trainer offline | *Derechos y propósito* | 4.12 |
| 63 | Method disclosed, including AI assistance | *Derechos y propósito* | 4.14 |
| 64 | Rewrite of the rights section recorded, with the reason | *Historial de revisiones* | 2.9 |
