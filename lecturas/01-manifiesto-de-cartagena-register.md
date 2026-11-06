# Register of guards — Manifiesto de Cartagena

Lectura 01 · `01-manifiesto-de-cartagena-lectura.md`

Every device implemented in this edition, with the location where a reader can find it and the standard in `POLICY-scholarship-and-compliance.md` that it serves. Checked by `drift.py`: every specific location below must resolve in the edition, and every standard cited must exist in the policy.

Edition published (v2.4, 2026-11-03). First published as v2.3 on 2026-11-02. First published as v2.2 on 2026-11-01.

## 1. Witnesses and sources

| # | Guard | Location | Standard |
|---|---|---|---|
| 1 | Every witness named with a sigla, its provider and its chain of mediation | *Nota sobre el texto* | 3.1, 3.7 |
| 2 | Base text chosen and the choice stated: Y (1826) base since v1.3, L collated at every place, J and W controls; the former §1 restitution closed | *Nota sobre el texto* | 3.2 |
| 3 | First printing and manuscript: facts from L restated with citation, loss reported at low grade | Notes § 1 | 2.3, 2.6 |
| 4 | Loss of MS and first edition recorded as an unverified claim of secondary sources | Notes § 2 | 2.2, 3.8 |
| 5 | Authorship declared separately from custody (Tejera); attribution graded | Notes § 3 | 3.13 |
| 6 | Dateline attested by all three witnesses | Notes § 4 | 2.3 |
| 7 | L identified by catalogue record; pages supplied by the compiler; OCR mediation stated | Notes § 5 | 3.7 |
| 8 | J's self-declared source (Jackson 1945) reported, not verified; J's OCR errors noted | Notes § 6 | 2.6 |
| 9 | W's licence notice scoped; its departures counted; its added signature not adopted | Notes § 7 | 4.2, 4.10 |
| 10 | Unconsulted witnesses named as a declared lacuna | Notes § 8 | 2.8, 3.9 |
| 11 | Received title vs printed title distinguished | Notes § 9 | 2.6 |
| 12 | Chronology and key checked against named general reference works; grade medium; one entry withdrawn | Notes § 10 | 2.3, 3.9 |

## 2. Text and apparatus

| # | Guard | Location | Standard |
|---|---|---|---|
| 13 | Six editorial criteria stated before the text, including modernisation classes and OCR repair rule | Criterion 1 | 3.2 |
| 14 | Lexical and syntactic forms of L kept; every departure recorded with the rejected reading | Criterion 2 | 3.3, 3.4 |
| 15 | OCR damage repaired from J, marked [?OCR], verified against W | Criterion 3 | 3.7 |
| 16 | Punctuation policy declared by class | Criterion 4 | 3.2 |
| 17 | Paragraph numbering is the edition's; dateline outside it; W's signature not adopted | Criterion 6 | 3.2 |
| 18 | Restitution of §1 with grade | Apparatus § I | 3.3 |
| 19 | Every OCR repair with adopted reading, rejected reading, witness tag and [?OCR] | Apparatus § II | 3.3, 3.4, 3.7 |
| 20 | Every L/J divergence with L kept, J and W readings recorded; J's own OCR damage noted | Apparatus § III | 3.3, 3.4 |
| 21 | Modernisation counted by class, by program | Apparatus § IV | 2.7, 3.2 |
| 22 | W's departures recorded, none adopted | Apparatus § V | 3.4 |
| 23 | Proper names normalised in a table | Apparatus § VI | 3.2 |
| 24 | Apparatus generated from a logged, reproducible procedure; the logs shipped in the workshop | Apparatus § II | 3.11 |

## 3. Reference matter

| # | Guard | Location | Standard |
|---|---|---|---|
| 25 | Reference key identifies, does not evaluate; says so | *Referencias del texto* | 2.10, 3.12 |
| 26 | † convention: verified entries marked; the rest declared as compiler's general knowledge | *Referencias del texto* | 2.3, 3.8 |
| 27 | Chronology states what and when, not why | *Cronología* | 2.10 |
| 28 | Glossary definitions written for the edition from the sentence, from no dictionary | *Glosario* | 4.4, 4.5 |
| 29 | Bibliography lists only works consulted; unconsulted ones referred to the notes | *Bibliografía* | 3.1 |

## 4. Rights and history

| # | Guard | Location | Standard |
|---|---|---|---|
| 30 | Public domain derived from the author's death | *Derechos y propósito* | 4.1 |
| 31 | First publication recorded; publication right excluded | *Derechos y propósito* | 4.9 |
| 32 | Text, not provider files; each provider's terms stated; Larrazábal's prose excluded though public domain | *Derechos y propósito* | 4.4, 4.10 |
| 33 | Moral rights respected and said how | *Derechos y propósito* | 4.11 |
| 34 | CC0 waiver over everything that is not the author's text, workshop scripts included | *Derechos y propósito* | 4.5 |
| 35 | Dependencies listed with licences; nothing third-party embedded; trainer offline | *Derechos y propósito* | 4.12 |
| 36 | Licence and positive terms of use; support never a condition of access | *Derechos y propósito* | 4.6 |
| 37 | Method disclosed, including AI assistance | *Derechos y propósito* | 4.14 |
| 38 | Errata clause; sources prevail | *Derechos y propósito* | 4.7 |
| 39 | Every version's substantive changes and the procedure's own errors recorded in the open | *Historial de revisiones* | 2.9 |
| 40 | Status *en curso* stated in the front matter until publication | *Advertencia* | 2.3 |
| 41 | Errata clause: unverified data flagged one by one in the Notas and the reference key; corrections directed to the originals; errata found in use corrected in later versions and recorded in the Historial | *Advertencia* | 4.7 |

## 5. Mechanical checks

| # | Guard | Location | Standard |
|---|---|---|---|
| 42 | Declarations, structure, references, counts, rights audited | `compliance.py` | 2.5 |
| 43 | This register resolved against the edition and the policy | `drift.py` | 2.5 |
| 44 | Edition reconciled with all three witnesses; whole-word matching, segmentation and class fallbacks | `verify.py` | 2.5, 3.7 |
| 45 | Base text laid down by a reproducible script with a decision log | `work/01/B-build.py` | 3.11 |
| 46 | Three-way collation by script | `work/01/C-collate.py` | 3.11 |
| 47 | Apparatus generated from the logs, paragraph numbers located not typed | `work/01/C-apparatus.py` | 3.11 |
| 48 | Manifest names the edition; tools read the manifest | `corpus.py` | 3.14 |
