# The method — an assistant working backwards into a language, for a reader who cannot check it

*A document of the project (decision 86, 2026-11-07): it explains the source of the grammar layer's cards and ships with the
release that carries them, beside the policy. Living and versioned; English, as the policy is (decision 72).*

Version 0.15, 2026-11-08 (twenty-third session, turn 2; registered with the fifth distribution). A living document: each version adds what the work taught and marks
what it overturned. The compiler asked for it after 8.1a: «document the method we are discovering; it may evolve into something
interesting — an LLM doing work backwards unto language for a human». Evidence for every claim is in
`2026-11-07-8.0-pilot/` (P0, P1 and their reads) and the design `2026-11-07-8.1-concept-model-design.md`.

## 0. The situation

A reader is learning Spanish from fifteen historical texts. The assistant has built them a trainer: every word form, a one-word
English equivalent in the sense the text uses, the sentence it sits in. That layer the reader can check against the text, and
English readers can check against themselves. Now the reader wants the grammar too — what *a* does in *redimir a esta de la que
padece*, and what it becomes in Japanese, Sanskrit, Avestan — and wants it for the whole corpus, efficiently. The reader states
plainly that **they cannot judge the output**: they are learning the language the cards teach. There is no expert in the loop and,
by the project's own policy (decision 58), no dictionary, parser or corpus of anyone else's as a dependency.

So the question is not «how does the assistant annotate grammar» but **how is an annotation made trustworthy when the only reader
is the person it is for, and they cannot verify it** — and done at a scale (122,616 tokens, 62,197 of them function words) where
authoring token by token is not an option.

## 1. The objects (decision 85)

- **words** — a form and its concept (the lexical layer, already built);
- **atoms** — a function word *in one locus*, with its sense there and, per target language, its realisation: a word, a particle,
  an ending, a feature on another word, an order, or ∅ with a stated reason;
- **stretches** — the shortest run of tokens that a given target language can translate whole, computed from the atoms by a head
  rule, per (locus, language set). A card side is a stretch whenever any language on the other side needs one.

Three worked cases (design §§ 1, 8) established that atom-level one-to-one is not universal and that one rule — extend from the
atom to its head — closes every failing instance. The schema's *shape* has not been contradicted since; everything below is
about making its *content* right.

## 2. The three kinds of answer

Every locus gets a sense from the rules in one of three ways, and the kind is kept with the sense:

| kind | what it is | share on 03 (P1) | accuracy found (P1 read) |
|---|---|---|---|
| **pattern** | a declared condition on the neighbours fired (or a table row: locution, governed preposition) | 48 % | 85 % on the chunk-bearing classes, 100 % on the rest |
| **default** | no pattern fired; the form's declared default sense | 22 % | **80 %** |
| **record** | the rules decline (*se* with no pronominal verb; *a* after a verb before a determiner); a human-or-assistant decision per locus | 4 % | — |
| invariant | the form has one sense everywhere (*y, no, muy* …) | 26 % | 100 % |

The kind is not bookkeeping: it is the **grade the reader will see on the card** (as tiers show on every non-English form), and it is
where the errors live. The first uniform sample spent a quarter of its reads on invariants that cannot fail.

## 3. The two kinds of error (the finding of 8.1a)

Reading P1's risk-weighted hundred, the fourteen wrong loci split without remainder:

- **Logic** — a rule reasons wrongly about a context: a comma taken for a clause boundary; a noun in *-emos* taken for a verb; a
  participle before its noun taken for a verb; *de* + adverb of place not seen as origin; an accent-stripper that silently
  turned *más* into *mas* so that no comparative pattern had ever fired. **Logic errors converge under sampling**: each hundred
  names classes, each class is fixed once and does not return (none of read 1's eight recurred in read 2).
- **Coverage** — a table lacks a row: a locution (*en vano, he aquí, por parte de*), a governed word (*despojar de, adicto a*), an
  archaic sense (*tres siglos ha*). **Coverage errors do not converge under sampling**: a table is as complete as the rows someone
  wrote, and every sample finds the next gap. They converge under **enumeration**, because the corpus is finite: harvest every
  run of two to four consecutive function words and every (verb-or-adjective, preposition) pair, with counts, and decide each
  once from the most frequent down. After that the table is complete *for this corpus* by construction.

So the method has two engines, and knowing which error is which tells you which engine to run.

## 4. The instruments

1. **Rules as declared, printed code and data.** Patterns on neighbouring forms; one default per form; tables for locutions and
   governed prepositions; a pronominal-verb list; nothing learned from outside the corpus and the project's own glosses (which
   are allowed as evidence: a gloss beginning «to» marks an infinitive). Every run is byte-stable at rebuild and guarded as the
   trainer is.
2. **Sampling stratified by risk, not by population.** Weighted to defaults and the chunk-bearing classes; invariants barely.
   Accuracy per stratum; the corpus estimate by weighting back. (P0's uniform hundred: 11 wrong, 7 among 26 defaults. P1's
   weighted hundred: 14 wrong, found ten new classes that a uniform sample would have met one at a time.)
3. **Two reads of different kinds, never two of the same.** Read 1 is the rule's. Read 2 is **triangulation**: render the
   stretch in two typologically distant languages (Japanese and a Sanskrit shape) *without looking at the label*, and confirm the
   sense only if both realisations agree with it — object marker ⇒ を and the accusative; direction ⇒ に and a dative. This is
   not a second opinion; it is a different test, and it is the test the cards will put the sense to. Disagreements get a third,
   **contrastive** read: argue for the rule's sense; if no coherent clause comes out, it is wrong.
4. **Enumeration for coverage** (§ 3): the finite corpus's runs and pairs, decided top-down in batches, as the tables.
5. **A held-out text.** Rules written and fixed on one text (03, Bolívar 1815) are measured on a text they never saw before the
   schema is committed — ideally another author (11, O'Higgins and San Martín), to catch fitting to one hand.
6. **The grade on the card** (§ 2) and **errata from use** (Phase 6): what the reader meets is labelled as a pattern, a default or a
   record, and what they find wrong is corrected against the text, by the same path the editions already use.

## 5. The criterion, revised twice

- Design (§ 2.7): rule coverage ≥ 90 % on 03, ≤ 3 wrong in a hundred. Met on coverage (96.7 % / 96.0 %), **not met** on accuracy
  (P0: 11 wrong; P1: 14 on a harder sample).
- Now: ≤ 3 wrong in a **risk-weighted** hundred on the **held-out** text, after the logic fixes **and the enumerations**. The number
  must hold where the errors live, on a text the rules did not see, with the tables complete.

## 6. What this is, seen from outside

The usual direction is: a language, a corpus, a human expert, a model trained to imitate the expert. Here the direction is
reversed. There is a model and a reader; the reader is the only consumer and the only judge, and the reader *cannot* judge. What
replaces the expert is **structure that makes the model's own errors visible and separable**: answers graded by how they were
reached; samples aimed at the weak grade; a second read that uses other languages as instruments rather than another opinion;
a split between the errors that sampling cures and the errors that only enumeration cures; a text the rules never saw; and a
promise on every card about what kind of answer it is. None of it requires the reader to know Spanish. All of it is printed.

Whether this generalises is an open question worth keeping: the same shape — graded answers, risk-stratified sampling,
triangulation through independent realisations, enumeration of a finite domain, a held-out set, labelled outputs — would
apply to any task where a model works alone for a non-expert on a closed body of material. The corpus here happens to be
language, which is why the triangulation can use other languages; elsewhere the independent realisations would have to be
something else.

## 6b. What 8.1a′ added (v0.2)

The two enumerations are real: 5,398 runs and 7,742 pairs for 122,616 tokens — a few thousand decisions, not sixty thousand,
and the first 544 of them (everything seen ≥ 10–12 times) took one sitting. A third risk-weighted hundred: 12 wrong, ≈ 91 %,
and once again **none of the previous round's classes recurred**. The largest class left is structural: a heuristic cannot tell
*parece* from *parte* by its ending. The cure is the same engine as for the tables — **enumerate the corpus's verb forms** in
their diagnostic positions and decide each once — which suggests a general rule of the method: *whenever a heuristic has a
floor, replace it with an enumeration over the finite corpus.* Heuristics are for the first pass; enumerations are for the
number that has to hold.

## 6c. The fourth round (v0.3)

The third enumeration — **the corpus's verb forms** — was 4,231 candidates in diagnostic positions, 1,086 above the cut, decided in
one sitting (273 verbs, 826 not). With it, the class that a heuristic could never close (*parece*, *llama*) closed, and the fourth
risk-weighted hundred came back with 8 wrong, ≈ 93 %. The curve so far: 86 → 89 → 91 → 93, each round on a harder sample, each
round's classes gone the next time. Three things worth keeping:

1. **Three enumerations were enough to name every kind of coverage gap this layer has**: locutions (runs of function words),
   governed words (content word + preposition), verb forms (diagnostic positions). Nothing in four rounds has needed a fourth.
2. **Mechanism bugs are a third kind of error**, beside logic and coverage: the table had the row and the code did not look it up
   (*gozaríamos también de*). They are found exactly as logic errors are, by the read, and they are the cheapest to fix.
3. **The method is now worth less than the held-out text.** Four rounds on one text have reduced the classes to one locus each;
   the next number that matters is the one on a text the rules never saw. Rounds on the training text have reached the point of
   diminishing returns, which is what a held-out text is for.

## 6d. The held-out text (v0.4)

With the rules frozen, the O'Higgins · San Martín correspondence (text 11: 9,994 loci, 2.4 × the pilot text, two other hands,
another decade) returned **≈ 93 %** — the same number as the text the rules were built on. The fixes made on one text were fixes
to the language, not to the text; the engines produce rules, not memories. A fourth enumeration was needed on the way (locutions
with a content word inside, which the all-function-word harvest had not seen), which corrects § 6c's «three were enough»: the
count of enumerations is not the point; the point is that each gap, once named, is finite and can be listed.

The last seven per cent is a long tail of one-locus classes. The method's answer to a tail is not more rounds but the grade on
the card and errata from use (§ 4.5–4.6): the reader is told which kind of answer they hold, and what they find wrong is fixed
against the text. Whether to stop at the floor or run one more round is the compiler's call, recorded at 8.1b.

## 8. Precision, not accuracy — certify or quarantine (v0.5; decision 87)

The compiler, at ≈ 93 % on the held-out text: *is that the best we can do? I would not include any wrong content in the work, ever.
Where it comes out wrong, that should be an extraction point — take it, add it to a list to be studied and fixed manually, but don't
keep it in the cards. A reader does better learning what is complete and true around the problem than learning a faulty card.*

He was right, and the mistake was in the target, not in the rules. §§ 2–6 measured **accuracy** — how often the rules are right.
A card needs **precision** — that nothing wrong reaches the reader — and precision does not come from more accuracy; it comes from
**abstaining wherever the answer is not grounded**. The two are different problems, and the second is solvable at once.

### 8.1 Grounded versus guessed

Read the strata of every read again: invariants 0/12 wrong, locutions 1/8, patterns 3/40, defaults 6/40. A *default* is by definition
«no rule fired» — a guess with a label. And most pattern errors trace to a heuristic underneath: an ending taken for a verb, an ending
taken for a participle. So the line that matters is not 93 % against 97 %; it is **grounded against guessed**. A sense is *grounded*
when every fact it rests on was decided once by enumeration — this form is a verb (it is in the list); this run is a locution (it is
in the table); this word governs this preposition (it is in the sheet); this form is not a verb (decided «not») — and the rule that
joins those facts is exact. A sense is *guessed* when any link in that chain is an ending regex or a default. **Grounded ships.
Guessed never does.**

### 8.2 The seven moves

1. **Certify or quarantine.** Every locus is either *certified* (a grounded chain, and its context signature has never failed a
   read) or *queued*. Only certified loci become atom or stretch cards. Queued loci are extracted — form, sentence, candidate sense,
   the reason — into a work list sorted by frequency: finite, prioritised, and every item resolved becomes a rule or a record that
   certifies every locus like it. Coverage grows; precision never falls.
2. **Decide at the signature, not the token.** 62,197 loci, but the distinct contexts (the form with its decided neighbours) are a
   few thousand, and the frequent ones are few. *de* between a noun and an article is one signature covering thousands of loci.
   This is the same engine as the three enumerations: contexts are finite; decide them from the top. The one-locus tail that
   stopped the rules at 93 % is exactly what remains when the signatures are decided — and it goes to the queue, not the cards.
3. **Ship at the granularity of certainty.** When an atom is uncertain, its stretch may still be certain: *a esta de la que padece*
   can carry a verified whole translation while the atom cards for *a* and *la* are withheld. The reader learns the true thing at
   the level that can be vouched for — «complete and true around the problem», made exact.
4. **Every wrong locus ever read is a test.** The verdicts of all the reads are a regression suite the pipeline must pass before any
   cut; a new failure decertifies its whole signature class. Reads stop being measurements and become permanent guards.
5. **The acceptance test matches the promise.** Not «≤ 3 wrong in a hundred» but: a risk-weighted hundred drawn *from certified loci
   only*, on the held-out text, shows **zero** wrong, repeatedly. The metric watched is the **certified share**; precision is 100 %
   by construction and coverage is what the work buys.
6. **Triangulation certifies signatures, not tokens.** A signature is certified when the rule's sense and the blind Japanese and
   Sanskrit realisations agree on all its sampled instances; one disagreement quarantines the signature whole.
7. **The hard classes get a table or wait.** *se*, the personal *a*, the causal *como*: a decided signature table, or no atom card —
   the lexical card still ships, and the hover says *under review* instead of guessing.

### 8.3 The first measurement (turn 10)

Built the same turn: provenance on every decision, the queue by signature, a hundred drawn from grounded loci only. The grounded
share was 48–50 % on both texts — and the grounded hundred still held **nine wrong**, every one a *rule* wrong on grounded inputs
(preposition + *que* after a noun; *y que*; *como* after a comma; two table rows too broad). The lesson, immediately: **grounded is
necessary, not sufficient — a signature must also be validated by a read**. The strict share (grounded, read right, never wrong) was
**28 % of the pilot text and 30 % of the held-out text**: the part of the corpus that can carry a card today with the promise kept,
zero wrong by construction. The way up is reading by signature — one instance validates thousands — and the frequent signatures
are few.

### 8.4 The loop running (turn 11)

With context-exact signatures the strict share began at 14–17 %. Two validation reads later — one instance each of the two hundred
most frequent unvalidated signatures on the held-out text, 199 of 200 right — it was 24 % and 27 %. The frequent signatures are the
simple ones, so a read that used to measure now certifies, and cheaply: the first hundred signatures carried 928 loci. The one wrong
(*lo* before an adjective after a verb) failed its signature and named its fix, as every wrong does now. The loop is the method's
answer to the compiler's demand: zero wrong by construction, coverage bought one read at a time, every read permanent.

Three reads later (turn 13: 98, 98 and 100 of a hundred), the strict share stood at 32 % and 33 %, and the four wrong loci of
three hundred were all row conditions — a governed row that depends on what follows, a locution that must not fire after an
article, a two-letter verb under a length floor, a longer locution row. The logic of the rules has not been wrong since the first
certified hundred; what the reads find now is the edge of a table. That is the expected shape of a converging loop.

The grounded share has a ceiling the reads cannot touch; it moved only when the enumerations' cuts came down. Lowering the verb
sheet's cut for the 1,823 words that stand before a preposition (1,363 decided in one pass, most by morphology) took grounded
from 50 % to 58 % on the pilot text and from 53 % to 61 % on the held-out one in a single turn — more than six reads had.
The order of work the loop teaches: **enumerate first, validate second, read where the signatures are thick.**

Two cuts and two signature batches later the grounded share is 69 % and 71 % and the strict share 50 % on both texts, from 14–17 %
when the loop opened — 1,417 loci read right against 72 wrong, and every wrong one a named class with a fix. The reads now run
95–100 of a hundred, and what they find is where a rule tested a word with an ending instead of with the sheet, or a verb of
saying standing a phrase away from its *que*. The layer is approaching the point where the queue is three things: *se*, *por*, and
the personal *a* — the records, which are the one class that was never meant to be guessed.

The records got their tables at turn 17 — *se* by the verb's root and by what follows the verb, the personal *a* by a declared list
of the verbs that take a personal object or a dative — and the grounded share reached 72.8 % / 73.9 %, the strict share
55.6 % / 54.1 %, with 1,610 loci read right against 79 wrong. Two of the day's last wrong loci were a hand decision
that was right in one position and wrong in another (*goce*: a verb after *que*, a noun after *el*) — the reminder that a form's class is
positional, and that the sheet's decision is a default the position can overrule.

Turn 18 closed the day's rounds at grounded 77.4 % / 77.5 %, strict 60.4 % / 57.8 %, 1,795 loci read right against
94 wrong. The *se* table's first read found six of its edges in a hundred loci — which is the pattern every table has shown: a
table's edges are found by its first read and closed by its second. And the last cut taught a rule about enumeration itself: a
morphological decision made without a stem test (*-ndo* for a gerund, *-imos* for a first plural) is a heuristic wearing a sheet's clothes;
the honest test is whether the stem plus *-ar/-er/-ir* exists in the corpus — a fact, not an ending.

The rounds closed at turn 19: grounded 76.4 % / 76.5 %, strict 62.4 % / 58.7 %, 1,988 loci read right against 101
wrong, sixteen validation reads at 1,556 of 1,600. The last turn's lesson was small and exact: a heuristic that stops counting as ground
(W2's list reduced) costs a point of the grounded share and buys an honest one — the number goes down because a guess stopped being
called knowledge. The method's thermometer is built to do that.

### 8.5 The schema as data (turn 20)

The schema was written at turn 20 against the layer as it stood, and the method's promise became a file format: every locus carries its
status — *certified*, with the signature a read confirmed, or *review*, with the reason — and a guard proves that the cards are exactly the
certified set, that every certified signature is in the ledger and never failed, and that a scratch rebuild is byte-identical. The ledger
built on two texts certified fifteen, because a signature is a fact about the language, not about the text: 34,010 of 65,567 loci on the
first day. Two of the guard's own faults were found by the guard's first run — which is the right order of things.

### 8.6 What is new, if anything

A model working alone for a reader who cannot check it does not become trustworthy by being more accurate. It becomes
trustworthy by **refusing to answer wherever its answer is not grounded in a fact it decided explicitly**, and by making the
refusals a finite, visible, shrinking list. Accuracy was the wrong thermometer. The right one is how much of the corpus has been
certified, with the rest on a desk and not on a card.

### 8.7 The card shows the text, not the rendering (v0.14; 8.3)

Three things the trainer taught when the certified loci became cards. (1) A derived string is not the text: the stretch's run omits
numerals and splits fused forms (*de de el mes* for *de 29 del mes*), and does not always begin at the atom — a relative's run begins at
its antecedent, an enclitic's atom sits inside another word. So the card lights the sentence by character span, found by matching the
run's tokens against the sentence's (exact, prefix, enclitic suffix, fused pair), keeping the tightest match that still holds the locus;
what cannot be located is shown as «sin tramo», never guessed. (2) One offset may carry two atoms (*del*, *al*, *haberlo*), and their
statuses are independent: the hover lists each, and a guard that forbids «certified and under review at one offset» must except exactly
these. (3) «Under review» is a status the reader sees, not a sense: the layer ships the offsets of the queued loci and nothing else about
them, so the hover can abstain in public without the guess ever leaving the workshop. The reader learns that the word is being worked on —
which is true — and nothing that might be false.

## 7. Open questions (v0.1)

- How large are the two enumerations for this corpus, and how many turns to decide them? (8.1a′ harvests them with counts.)
- Does the held-out text (another author, another decade) hold the number, or does each author need a round of logic fixes?
- *se*: 107 records on 03 alone (~1,600 on the corpus). Is a two-sense inventory (reflexive vs passive/impersonal) decidable
  by a rule after all — plural subject after the verb ⇒ passive — or is *se* the one class that stays authored?
- The head rule's «head» is the first noun-ish token: an adjective before its noun makes the stretch one word short. Fix, or
  accept and let the card show the noun phrase whole?
- Can the project's own glosses do more than mark infinitives — e.g. mark the finite verbs the heuristic misses?

## History

- 0.1 (2026-11-07) — written after 8.0 and 8.1a; the two kinds of error; the six instruments; the criterion revised.
- 0.2 (2026-11-07) — § 6b after 8.1a′: the enumerations sized; «replace a heuristic's floor with an enumeration».
- 0.3 (2026-11-07) — § 6c after 8.1a″: the verb enumeration; mechanism bugs as a third kind; diminishing returns on the training text.
- 0.4 (2026-11-07) — promoted to a document of the project (decision 86); § 6d after 8.1b: the held-out text transfers at ≈ 93 %; a fourth enumeration; the tail.
- 0.5 (2026-11-07) — § 8, precision not accuracy: certify or quarantine (decision 87); § 8.3 the first measurement — grounded 48–50 %, strict 28–30 %, grounded is not sufficient.
- 0.6 (2026-11-07) — § 8.4 the validation loop: context-exact signatures, two reads, 199/200, strict 24 % / 27 %.
- 0.7 (2026-11-07) — § 8.4 continued: five reads, 497/500, strict 32 % / 33 %; the wrong are table edges, not logic.
- 0.8 (2026-11-07) — § 8.4: the cut lowered moves grounded more than reads do; enumerate first, validate second.
- 0.9 (2026-11-07) — § 8.4: after the second cut, grounded 69 % / 71 %, strict 50 % / 50 %; the queue converging on the records.
- 0.10 (2026-11-07) — § 8.4: the records' tables; grounded 72.8 % / 73.9 %, strict 55.6 % / 54.1 %; a form's class is positional.
- 0.11 (2026-11-07) — § 8.4: the last cut; a sheet decision needs a stem test; grounded 77.4 % / 77.5 %, strict 60.4 % / 57.8 %.
- 0.12 (2026-11-07) — § 8.4: the rounds close; grounded 76.4 % / 76.5 %, strict 62.4 % / 58.7 %; a guess that stops counting as ground lowers the number honestly.
- 0.13 (2026-11-07) — § 8.5 the schema as data: the status on every locus; the guard; the ledger of two texts certifies fifteen (34,010 of 65,567 loci).
- 0.14 (2026-11-08) — § 8.7 the card shows the text, not the rendering: a stretch is located by its tokens in the sentence; two atoms at one offset; «under review» is a status, never a guess.
- 0.15 (2026-11-08) — registered as a document of the project with the fifth distribution (decision 86): manifest `method` beside `policy`; source and PDF in the allowlist; a row on the hub. The schema ships beside it (`vocab/concepts.json`, `NN/senses.json`, `schema-summary.json`): 34,010 of 65,567 loci certified on the day it shipped.
