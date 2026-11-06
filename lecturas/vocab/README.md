# Léxico — the vocabulary trainer

One self-contained page, `flashcards.html`, covering every built lectura in the
corpus. Every word form each author wrote, with the sentence it appears in,
its paragraph locator, an English equivalent, and a Spanish definition where
the project has one.

## Use it

Open **`flashcards.html`**. That's all — one file, no server, no install, no
network. It works from your desktop, from VS Code's preview, from a USB stick,
and from Google Drive's viewer.

**Text** — pick one lectura, or *Todos los textos*. Each text is its own
corpus: the same form may carry a different gloss in two texts, because
glosses follow the sense in that text.

**Corpus** — two checkboxes. *Texto*: the author's own words. *Aparato*: the
edition's editorial prose (apparatus, notes, chronology, reference key,
glossary) — modern descriptive Spanish, a different register, kept separate
on purpose. The two never overlap within a text. One is always on.

**Decks** — the whole lexicon, the glossary words, by frequency band, or by
paragraph range (single text only) so you can study §16–30 the night before
you read it.

**Modes** — *Reconocer* (word → meaning and context), *Hueco* (sentence with
the word blanked), *Producir* (meaning → word), *Índice* (browse and search).

**Keyboard** — `space` reveals, `1`–`4` grade (Otra vez / Difícil / Bien / Fácil).

Scheduling is SM-2. Progress is saved in the browser, keyed by text and word,
so the same form in two texts is learned separately. If the browser blocks
storage — Google Drive's viewer sometimes does — the app says so and you can
use **Guardar progreso** to keep a JSON file. Progress files from the
single-text version of the app are read and migrated.

## Rebuild it

    python extract_vocab.py    # every built lectura in ../corpus.json -> vocab.json
    python extract_vocab.py --only 02
    python build_app.py        # vocab.json + app_template.html -> flashcards.html

Standard library only.

## Per-lectura meaning files

    NN/glosses.json       one English equivalent per form
    NN/definitions.json   fuller Spanish explanations for the hard words

Both are written for this project and taken from no dictionary; that is what
lets them sit under CC0. Glosses are tuned to how the word is used *in that
text*: where a word means something different today, the gloss gives the
author's sense and says so (in the Carta, *coartada* is "restricted", not an
alibi).

Cards are **word forms, not lemmas**. You meet *conservamos* on the page, so
that is what the card shows; the family line groups obvious relatives by a
crude shared-stem rule that is a browsing aid and not linguistics.

## Rights

The authors' texts are public domain (dates in `../corpus.json`). Glosses,
definitions, data and code: CC0 1.0.
