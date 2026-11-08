# Léxico — the vocabulary trainer

One self-contained page, `flashcards.html`, covering every built lectura in the
corpus: the text of each edition beside its cards. Every word form each author
wrote, with the sentence it appears in, its paragraph locator, an English
equivalent, and a Spanish definition where the project has one — and, since the
fifth distribution, the **grammar layer**: every grammatical word in its place,
with its function, wherever that function has been certified.

## Use it

Open **`flashcards.html`**. One file, no server, no install, no network. It
works from your desktop, from an editor's preview, from a USB stick.

**The text pane** (right by default; `⇄ lado` swaps sides) shows one edition
paragraph by paragraph. Click a paragraph to study it, shift-click for a run of
paragraphs, «Todo el texto» for the whole edition; a selection may span several
texts («Todos los textos» selects all fifteen). Hover a word for its gloss;
click it again for its card. Unlearned forms are dotted; «marcar lo asentado»
greys the known ones. Save a selection under a name, or copy a link to it.

**Índice** lists the forms of the checked editions by frequency in the
selection or by dispersion over the corpus (texts · authors), in units of a
hundred — «Unidad n de N», ‹ › to move, a number to jump — with «Estudiar esta
unidad» forming the deck; when a deck runs dry the next unit is offered. The
author's text and the edition's apparatus are separate sources; one is always on.

**Three card sets**, chosen in the deck bar:

- **palabras** — one card per form in the selection, with its first sentence
  there and how often it recurs in the corpus. «gramaticales» adds the function
  words as word cards.
- **átomos** — one card per grammatical concept in the selection (*a* +
  infinitive, *de* of possession, *se* reflexive…): the sentence with the word
  lit, the function in a line, the realisation in each chosen language (word,
  particle, ending, feature, order, or ∅ with its reason), and the stretch it
  belongs to.
- **tramos** — one card per stretch: the smallest run of words with an
  equivalent of its own (*a contestar*, *de 29 del mes*), lit in its sentence,
  with its atoms beneath.

Atom and stretch cards exist **only for certified loci** — a sense decided from
facts enumerated once and confirmed by a read that was never wrong. Every other
grammatical word says *en revisión* in its hover and gets no atom card. The
trainer never shows a guess. `METHOD-grammar-layer.md` explains how; the counts
are in `schema-summary.json`.

**Sides.** Two rows of chips, *anverso* and *reverso*, one per language
(ES · EN · JA · SA · AE · EL): any language with forms may face either way, and
a language without a form for a concept shows «—». The choice is kept; a link
can carry it (`#en/es~en+ja/03/§5` — front Spanish, back English and
Japanese, text 03, paragraph 5).

**Modes** — *Reconocer* (front → back) and *Producir* (the sentence with the
word, atom or stretch blanked). **Keyboard** — `space` reveals, `1`–`4` grade.

**Entrances** — `#NN` a text, `#NN/§P` a paragraph, `#índice` the index,
`#índice/n` a unit, `#01/1,2;03/5` a selection; `#en/…` or `#ja/…` opens the
interface in that language.

Scheduling is SM-2 (*Por repasar* orders the deck: unseen, due, rest). Progress
is one record per form, per grammatical concept and per stretch, kept in the
browser; export it with **Guardar progreso** and load it on another device.
Progress from earlier versions of the trainer is read and migrated.

## Rebuild it

    python extract_vocab.py    # every built lectura in ../corpus.json -> vocab.json
    python build_app.py        # vocab.json + the grammar layer + app_template.html -> flashcards.html

Standard library only. `build_app.py` reads `concepts.json` and `NN/senses.json`
beside it and embeds them compactly (under 1 MB of the 10 MB budget): certified
loci with the span of their stretch; loci under review as offsets only.

## Files per lectura

    NN/glosses.json       one English equivalent per form
    NN/definitions.json   fuller Spanish explanations for the hard words
    NN/senses.json        every grammatical-word locus of the text: concept, how it was
                          decided, head and stretch, status (certified | review) and reason

And for the corpus: `concepts.json` (lexical concepts by English pivot;
grammatical concepts with their realisations per language), `stretches.json`
(the stretches, derived from the loci), `schema-summary.json` (the counts).
The schema is data: it is exported from the workshop's ledger of validation
reads and cannot be regenerated from this distribution alone; each distribution
carries the ledger's state on its date.

Glosses and definitions are written for this project and taken from no
dictionary; that is what lets them sit under CC0. Glosses are tuned to how the
word is used *in that text*. Cards are **word forms, not lemmas**: you meet
*conservamos* on the page, so that is what the card shows.

## Rights

The authors' texts are public domain (dates in `../corpus.json`). Glosses,
definitions, senses, concepts, data and code: CC0 1.0.
