# Standards of Scholarship and Legal Compliance

**A policy for personal-study editions of public-domain texts**

Version 1.7 · Derived from the *Carta de Jamaica* reading edition

*1.1 — Broadened standard 3.4 after it was found to have licensed undeclared divergences; added 2.9, 3.4.1 and guards 13a–13d.*

*1.2 — Added 2.10 and 3.12 after evaluative commentary was found in the edition's ancillary matter and removed; registered guards 35–47.*

*1.7 — Evidence is text, and the release carries it (decisions 55 and 54 of the roadmap, 2026-11-01). 8.7: the title page or colophon is transcribed into the evidence file and no provider image is kept; the compiler's read covers every entry of a witness table, not only base and collation witnesses. 8.4: `PROVENANCE.md` reproduces every evidence file verbatim, with the date and person of each read, every person's death date and source, each edition's own derivation and first-publication statement, and every excluded text and source with its reason, so that whoever holds the release holds the whole evidence. 8.8: modern text layers are never kept in the workshop (decision 56). Decided 2026-11-02.*

*1.6 — § 8 added: the release condition. Nothing is distributed until every edition in the release rests only on dates and on the compiler's own waiver — no pending item, no declared exception, no unread rights line, no modern text layer, no open rights question — and `release.py` proves it mechanically and writes the provenance record into the distribution. Advertising on the hosting page named as an acceptable support form, never inside a distributed file. Claims procedure. 8.7 re-verification of every rights fact with recorded evidence before release; 8.8 pruning of the workshop to the record. Decided 2026-10-14.*

*1.5 — Four checks named (ortografia.py added 2026-10-12). § 6 steps 1 and 2 require the provider's rights line before download and a witness-layer entry in the manifest, which compliance.py tests against a cutoff year; modern transcriptions and editions are never filed as witnesses. Prompted by the rights audit of 2026-10-13.*

*1.3 — Generalised from one edition to a corpus. The register of guards (former § 5) moved out of the policy into a per-edition file; § 5 now says where registers live. Added 3.13 on authorship, needed by texts issued under one name and drafted by another. Added 3.14 on the corpus manifest.*

*1.4 — Made the compliance standards sufficient for public distribution with support mechanisms. Rewrote 4.6 to declare the licence and positive terms of use instead of a non-commercial purpose that a lawful later use would contradict. Added 4.9 (first publication and the publication right), 4.10 (text, not provider files; provider terms recorded), 4.11 (moral rights), 4.12 (dependency and asset audit), 4.13 (workshop separated from distribution), 4.14 (method disclosed, including AI assistance).*

---

## 1. Purpose and scope

This policy governs documents made for private study that reproduce or reconstruct texts belonging to other people. It exists to answer two questions before anyone thinks to ask them: *where did this come from* and *by what right do you have it*.

It applies to any document that assembles a reading text from multiple witnesses — printed editions, manuscripts, online transcriptions — where the compiler is not the author and does not claim to be.

It does not govern original writing, quotation from in-copyright works, or anything intended for publication or sale. Those raise different questions and need different rules.

The governing insight is that a study document has no defence except its own transparency. It is not peer-reviewed, not published by an institution, not vouched for by anyone. Its credibility rests entirely on whether it declares its sources, its choices, and its uncertainties clearly enough that a sceptical reader can check every one. A document that does this cannot be accused of concealment, because there is nothing concealed.

---

## 2. Principles

**2.1 Provenance precedes polish.** A beautiful text of unknown origin is worth less than an ugly one whose every reading can be traced. Presentation serves attribution, never substitutes for it.

**2.2 Declare rather than decide.** Where evidence is insufficient to settle a question, the question is recorded as open. Choosing arbitrarily and stating the choice confidently is the failure mode this policy exists to prevent. An unresolved discrepancy honestly labelled is a stronger document than a resolved one silently guessed.

**2.3 Confidence is part of the datum.** A fact and the compiler's warrant for believing it travel together. "Page 207–229, attested by two independent sources" and "printer's name, conjectural spelling" are different kinds of claim and must not be typeset identically.

**2.4 Disclose redundantly.** A caveat that appears only in a back-matter appendix will be missed by a reader who encounters the claim on page three. Every material uncertainty is disclosed at each point of use *and* in a master register. Redundancy is not clutter here; it is the mechanism.

**2.5 The sources prevail.** The compiled document is a convenience, never an authority. Where it conflicts with a source, the source is right and the document is wrong. This is stated inside the document itself.

**2.6 Attribute without endorsing.** Contested characterizations from third parties may be reported, but reporting is not adoption. Where a claim is politically or institutionally motivated, the document says who made it and declines to ratify it.

**2.7 Verify mechanically where possible.** Human proofreading misses dropped clauses. Anything checkable by script is checked by script, and the script ships with the document.

**2.8 Nothing is silently omitted.** Abridgement, however sensible, breaks the compact with the reader. If material is left out, the omission is declared.

**2.9 Correct the record visibly.** When a document is found to have made a false claim about itself, the correction is recorded alongside the fix. Silent repair leaves a reader who saw the earlier version with no way to know which of the two to trust, and converts an honest error into something that resembles concealment. The note states what was wrong, how it was found, and what the true position is.

**2.10 Record, do not read.** The document's business is the text: what it says, where each reading comes from, what each word means. It is not the compiler's business to tell the reader what the text is worth, whether its predictions held, or how others have judged it. Identification is in scope — who a named person was, what a named event was. Evaluation is not. The distinction is easy to state and easy to lose: a definition that illustrates a word by characterizing the author's tone has already crossed it.

---

## 3. Standards of scholarship

**3.1 Name every witness.** Each source consulted is assigned a sigla and listed in a table before the text. No reading enters the document from an unnamed source.

**3.2 State the criteria before the text, not after.** The rules governing orthography, choice between conflicting witnesses, treatment of proper names, and marking of unauthorized passages are set out in advance, so the reader judges the text against a declared standard rather than reverse-engineering one.

**3.3 Record every intervention.** No change to the base text goes unregistered. The critical apparatus lists restitutions, corrections, and emendations separately, each with the reading adopted, the reading rejected, and the sigla of the witnesses involved.

**3.4 Declare every departure from the best witness, graded by risk.** All divergences from the most authoritative source are collected in one section — not only those made on grounds of sense — and grouped by the class of decision they represent: emendation on grounds of sense, correction of manifest corruption, substitution of an anomalous form, grammatical regularization, omission of editorial marks. Each carries instructions for reversal.

An earlier form of this standard covered only overrides on grounds of sense. That narrowness produced a defect in the reference edition: one divergence was declared and eighteen were not, because the compiler only looked for the class the standard named. The lesson is general. A standard that enumerates one kind of intervention licenses silence about the rest.

**3.4.1 Flag mediated readings at item level.** Where the disclosed chain of mediation (3.7) makes it impossible to tell whether an anomalous reading originates with the source or with an intervening process, that specific reading is marked as such — not merely covered by a general caveat elsewhere. The mark names what would resolve it.

**3.5 Mark unauthorized text typographically.** Passages not supported by the primary witness — because of damage, loss, or absence — are visually distinguished in the reading text itself, not merely footnoted.

**3.6 Add nothing the witnesses do not support.** Where a common modern version supplies material no source authorizes, the material is excluded and the exclusion explained.

**3.7 Disclose the chain of mediation.** If the compiler worked from a transcription rather than the original, or from a digitization rather than the print, every intervening step is named, along with the class of error each step introduces.

**3.8 Grade confidence explicitly.** Each item of unverified information receives a stated grade — high, medium, low, mixed, unresolved — with the reason.

**3.9 Remove what cannot be verified.** A claim the compiler cannot support is deleted, not softened. Where its removal leaves a gap, the gap is noted and the surrounding argument shown not to depend on it.

**3.10 Publish the verification method.** Any mechanical check performed is distributed as runnable code, so a reader can repeat it rather than trust the result.

**3.11 Keep a plain-text source of truth.** The canonical file is human-readable and diffable. Rendered formats are generated from it by a script that requires no network access and no proprietary tooling.

**3.12 Separate identification from evaluation.** Ancillary matter — glossaries, reference keys, historical notes — states what a word means and who a person was. It does not say what a passage implies, whether an argument succeeded, or how the work has been received. Each such section carries a header declaring which side of the line it sits on, and the constraint is enforced mechanically where possible so it cannot erode through later edits.

**3.13 Declare authorship separately from signature.** A text issued under one person's name and drafted by another is attributed to both, with the roles stated and the attribution graded like any other unverified datum (3.8). The signatory's name is not a finding about who wrote the words; where the drafting is disputed, that is recorded as open (2.2). Proclamations, manifestos and official addresses of the period routinely pass through secretaries, so this is the normal case rather than the exception, and silence about it is a concealment.

**3.14 Name every document of a corpus in one manifest.** When several editions share tooling, one machine-readable manifest lists them in a declared order with their status, and every script reads the manifest rather than a filename. A tool that silently assumes one document will silently ignore the others.

---

## 4. Standards of legal compliance

**4.1 Establish public-domain status affirmatively.** Status is derived from the author's death and the date of publication, stated in the document, not assumed from the age of the work.

**4.2 Analyse each layer separately.** An underlying text, a transcription of it, an editor's notes, and a publisher's design are four distinct objects with four distinct statuses. They are assessed individually and the assessment is written down.

**4.3 Note jurisdictional variation.** Where the law differs materially between jurisdictions — on transcription originality, on rights in first publication of unpublished works, on term length — the divergence is acknowledged rather than glossed with the compiler's preferred rule.

**4.4 Do not appropriate third-party editorial matter.** Notes, prefaces, and apparatus written by others carry their own licences. They are not absorbed into the document. Where their factual content is needed, the facts are restated independently and the source cited.

**4.5 Waive rather than assert.** The compiler's own contribution is released under CC0. This removes any question about the document's status and forecloses the argument that a private compilation is being used to encumber a public-domain work.

**4.6 State the licence and the terms of use positively.** The document declares that it was prepared for study and reading practice; that, by virtue of the public-domain status of the text and the CC0 waiver of 4.5, it may be read, copied, redistributed and adapted by anyone, for any purpose; that support for the compiler's work — donations, patronage, or subscriptions toward future work — is welcome and is never a condition of access to anything released under this policy; and that it is not a substitute for the cited sources. A document never declares a purpose that a later lawful use of it would contradict: the licence is the commitment, the purpose is a description.

**4.7 Include an errata clause.** The document states that it may contain unverified bibliographic data, points to the register of such data, and directs that corrections be made against the originals.

**4.8 Distinguish error from misconduct.** The document's own framing makes clear that a mistaken citation is a defect to be corrected, not a misrepresentation. Nothing in it claims work that is not the compiler's, which is the only conduct that would warrant a charge of plagiarism.

**4.9 Record first publication.** For every text the date and place of first publication are recorded and graded. In some jurisdictions (the European Union, the United Kingdom) the first publisher of a work never before published, whose copyright has expired, holds a limited right of about twenty-five years. A text, or a substantial portion of one, first published within the last twenty-five years is treated as encumbered until the contrary is established and written down.

**4.10 Incorporate text, not files.** An edition incorporates text established by the compiler against named witnesses. It never incorporates a provider's page images, scan files or raw OCR output, and its distribution never depends on them. For each digitisation consulted, the edition names the provider and that provider's stated terms (a library's public-domain designation; a "public domain, US only" notice; a provider's request for non-commercial use), so that a reader can see the text owes nothing to those terms.

**4.11 Respect moral rights.** In several jurisdictions the rights of attribution and integrity are perpetual. The edition always names the author; it never presents an altered reading as the author's words; every intervention is declared and reversible (3.3, 3.4). Modernisation is a declared editorial criterion applied to a named text, not a change to the work, and the edition says so.

**4.12 Audit the distribution.** Every software dependency used to build or run the documents is listed with its licence, and the list states which, if any, of its code or assets ends up in a distributed file. Nothing under a copyleft or non-commercial licence, and no third-party font, script or image, is embedded in a distributed file. The trainer makes no network request.

**4.13 Separate the workshop from the distribution.** Fetched witnesses, research reports, working notes and intermediate files live under `work/` and form no part of the distribution. The distributable set is: the governing document, the lecturas with their PDF and EPUB, their registers, this policy, the manifest, the scripts and the trainer.

**4.14 Disclose the method.** The rights section states in one sentence how the edition was prepared, including that it was prepared with the assistance of an AI system (Claude, by Anthropic) working under this policy, with the compiler responsible for the result.

---

## 5. Register of guards

Every edition built to this policy carries a register of guards: a table of every device it implements, where in the edition a reader finds it, and the standard here that it serves. The register lives beside the edition, in a file named for it (`NN-slug-register.md`), and is listed in `corpus.json`. `drift.py` resolves every location in every register against its edition and every cited standard against this policy.

Until version 1.3 the register of the *Carta de Jamaica* edition stood here as § 5. It was moved out so that the policy describes no edition in particular and each lectura is described by its own register. The reference register remains the Carta's: `02-carta-de-jamaica-register.md`.

The corpus's governing document (`00-…`) carries no register of its own: it implements no textual guards, only declarations and tables, and every one of those is checked directly by `compliance.py` against the manifest. A register would describe a check that already runs.

---

## 6. Procedure for a new document

0. Add the document to `corpus.json` with its chronological number and the status *pendiente*. Create nothing else until the manifest names it: the number fixes the filenames, and the tools only see what the manifest lists.
1. Identify every witness. Assign sigla. Record what each one is and how it descends from the others. Before any witness file is downloaded, copy the provider's own rights line into `work/NN/README.md`; a digitisation whose provider states no public-domain designation for its own layer is read for facts only and not filed. Where the text was issued under one name and drafted by another, record both and grade the attribution (3.13).
2. Determine copyright status for each layer separately. Write the determination down — in the edition's rights section and in the manifest's `witnesses` block (sigla, role, text-layer year, provider, rights line), which `compliance.py` tests: no text layer later than the manifest's cutoff year is filed as base or collation witness, and a declared exception (a modern layer that corroborates an older base, or supplies a passage no older witness carries) is recorded in the manifest with its closing condition and shown at every run; modern transcriptions and editions are otherwise read for facts and cited (4.4), never filed.
3. Choose a base text and state the criteria for departing from it — before doing any collation.
4. Collate. Record every intervention as it is made, not afterwards from memory.
5. Collect every departure from the best witness into one section, grouped by class of decision. Do not assume the only departures are the interesting ones.
6. List every fact not verified at first hand. Grade each. Delete what cannot be supported.
7. Place a point-of-use note at every location where a graded item appears.
8. Write the purpose, rights, and errata statements.
9. Run the mechanical check against each source. Reconcile every flagged passage to an apparatus entry or investigate it.
10. Write the register of guards (`NN-slug-register.md`) and list it in the manifest. Run `drift.py` until every location resolves.
11. Ship the source file, the register, the manifest and the scripts together. Set the status in the manifest to *publicada* only when all four checks pass (`compliance.py`, `drift.py`, `verify.py`, `ortografia.py`).

---

## 7. What this policy does not claim

It does not make a document authoritative. The reference edition states plainly that it is not a critical edition and should not be cited as an established text; this policy does not quietly retract that.

It does not make the compiler a philologist. Editorial judgement exercised without training in the discipline remains editorial judgement exercised without training in the discipline. The guards make that judgement visible and reversible; they do not make it expert.

It does not constitute legal advice. The copyright analysis in the reference edition is reasoning about publicly stated rules, offered by a non-lawyer, in a matter where jurisdictions differ. It is disclosed as such.

It does not eliminate error. It ensures that error, when found, is locatable, attributable to a declared source, and correctable — and that it will be read as error rather than as concealment.

Nor does compliance with it guarantee that the document is sound. The reference edition satisfied an earlier form of this policy while misdescribing its own method in a section devoted to method. The guards caught it eventually, on re-collation, which is the most that can be claimed for them: they shorten the interval between an error being made and being found. They do not close it.

## 8. Release condition

**8.1 The standard.** The corpus is prepared for public distribution with voluntary support (4.6). It is released only when the exposure of every distributed file is *zero in the only sense a compiler can secure*: every layer of every distributed file is either public domain by **date** (author, drafter, compiler and printer dead and the work printed before the manifest's cutoff year, so that no term can subsist anywhere) or the compiler's own contribution waived under **CC0**; and the evidence for each of those facts is on record in the release itself. Nothing in a release may rest on an *argument* — a reading of the law, a plausible inference, a good-faith belief — where a date or a waiver could have been obtained instead. "Perfect" means: no item in the release that a future reader, claimant or compiler would need to argue about.

**8.2 What blocks a release.** A release is not made while any edition it would contain has:
- a base or collation witness whose text layer is later than the cutoff year, or a reading text that rests on such a layer (a modern transcription or edition);
- a witness entry in the manifest marked *pending* or carrying a declared *exception*, whatever its closing condition says;
- a digitisation whose provider's rights line has not been read on the record and recorded verbatim;
- an open question in its rights section — a first-publication right, a scientific-edition right, a death date needed for the derivation — that is "declared" rather than closed by a date;
- any provider file, image, OCR layer, font, script or third-party asset inside a distributed file (4.10, 4.12);
- a failing or informational result on any of the four checks, the register check or the distribution check.
Declaring such an item in the edition (2.2, rule 4 of the roadmap) is the right way to *work*; it is not a way to *release*. An edition that cannot close its items is held back from the release, with the reason recorded; it is not released with a caveat.

**8.3 Scope of a release.** The unit of release is the corpus as the governing document describes it. A release is made once Phase 5 of the roadmap closes — every lectura published or formally excluded in the manifest with its reason — unless the compiler decides, in writing in the roadmap, to release a named subset; a subset release still applies 8.2 to every edition in it and excludes the rest by the manifest's release switch, never by hand.

**8.4 Mechanical gate.** `release.py --check` applies 8.2 to the manifest and the editions and fails on the first blocker; `release.py` builds the distribution only when the check passes, through `dist.py`, and writes into it `PROVENANCE.md` — for every edition, every witness with its text-layer date, provider, rights line as read, the date and person of the read and the evidence file reproduced verbatim; every person on whom the derivation rests with death date and source; the edition's own derivation and first-publication statement; and every excluded text and source with the reason — together with `MANIFEST.sha256`. A release therefore carries the whole evidence it rests on, and an evidence file named in the manifest but missing from the workshop blocks the release. A release is the output of that program and nothing else; the project zip (the workshop, `work/` included) is never published.

**8.5 Support and advertising.** Donations, patronage, subscriptions toward future work, and advertising on the page that hosts the distribution are acceptable forms of support. None of them is ever a condition of access to anything released. No advertisement, tracker, script, font or asset of a third party is ever placed inside a distributed file (4.12); advertising lives on the hosting page only, and the release's README says so. The provider terms that restrict "non-commercial use" attach to providers' scan files, which never enter a release; the released text is public domain and the compiler's layer is CC0, and HathiTrust's own statement that transcribed text carries no restriction is quoted in the rights section wherever its scans were read.
**8.6 Claims.** If anyone asserts a right over anything in a release, the compiler answers from the record: the provenance file, the edition's rights section and the register. Nothing is removed before the claim has been read against the record; if the record shows a date or a waiver, the claim is answered and recorded in the edition's *Historial*; if the record shows an argument where a date should have been, 8.2 was not met and the edition is withdrawn from the release until it is. Every claim and its answer are recorded in the roadmap's history. No claim is ever answered by asserting fair use or by a legal opinion of the compiler, who is not a lawyer (§ 7).


**8.7 Re-verification before release.** Before a release, every rights fact the release relies on is read again and its evidence recorded, so that no claim can stand against the record. For every entry of every witness table — base, collation, control, discarded or identification witness; an edition's own read of another witness excepted — and every source read for text: the provider's rights line, copied verbatim from the record on a stated date by a stated person, with the record's identifier and, where the record can be saved, a copy of it under `work/NN/evidence/`; the printing's date, place and printer as read on its title page or colophon, transcribed into the evidence file (no provider image is kept: the evidence of a rights fact is text a reader can re-check on the provider's record, and the release reproduces it); the text-layer date. For every person on whom the public-domain derivation depends — author, drafter, amanuensis, compiler, printer — the death date with its source, primary where one is reachable, graded otherwise. For every text: the date and place of first publication with its source. The manifest carries these as `rights_evidence` (a pointer to the evidence file) and `rights_read_on` (the date) on each witness and `death_date` / `death_source` on each person; `release.py --check` fails on any witness or person without them. Re-verification is a stage of its own in the roadmap, done after every lectura is published and before the release, and recorded in each edition's *Historial*.

**8.8 Pruning the workshop.** After re-verification, the workshop is pruned to the record: kept are the witness files with their rights lines (or, for provider files whose terms restrict redistribution, the identification that allows re-fetching), the evidence files, the decision tables and logs, the scripts that regenerate each edition from its witness, the provider-file inventory, and the research reports' findings and exclusions; deleted are debug copies, superseded scripts, partial or intermediate files, crops, and anything a kept script regenerates. A text layer later than the cutoff year — a modern edition, a modern transcription, a provider's layer of a post-cutoff printing — is never kept in the workshop once the readings taken from it stand in the decision tables; the identification that allows it to be read again replaces the file, as for restricted provider files. `work/KEEP.md` states the rule and `prune.py` applies it from an allowlist, listing every deletion in the roadmap. The workshop is never published either before or after pruning.

---

## 9. Amendment of 2026-10-14: the right of quotation

**9.1** Sections 4 and 8 speak of text layers later than 1929 as layers the text must not rest on. They do not say what may be *quoted* from such a layer. This amendment says it, and the roadmap's rule 15 enforces it.

**9.2** Words from a text layer later than 1929 enter a distributed file only as quotations within the right of quotation — the exception that the Berne Convention (art. 10) obliges every member state to provide and that national laws state in their own terms (for example Spain, TRLPI art. 32; the Andean Community's Decision 351, art. 22; the United States' fair use). Its conditions, which every such quotation in this corpus meets and which the compiler checks by program: the source is a lawfully published work, named with its author; the quotation is short and proportionate to its purpose; the purpose is the comparison of witnesses, criticism or teaching; and the quotations together could not stand in for the work.

**9.3** The rights section of an edition that quotes a modern layer states this basis and cites the source. It does not argue that no right subsists in the layer; that question is left open, because the quotation is lawful either way.

**9.4** Ceilings: no quotation longer than 15 words; no witness quoted, in all, beyond 10 % of the edition's word count. `compliance.py` reports the counts and fails on a breach; `release.py` applies the same ceiling at release.

**9.5** Learner products (PDF, EPUB, the trainer) are built without the critical apparatus and therefore carry no such quotation.

**9.6** What the right of quotation does not allow — reproducing a modern layer's text at length, or as a base — the compiler does not do and does not seek permission to do.

---

*This policy is released under CC0 1.0 Universal. Apply, adapt, or discard it freely.*
