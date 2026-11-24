#!/usr/bin/env python3
"""build_index.py — the folder's main page, in three languages: index.html, index.en.html, index.ja.html, from corpus.json.

One page a language (Spanish, English, Japanese), each whole: the trainer first, then every published lectura with its files,
the documents, how the folder is copied and changed, how it is replicated. One file a page: its style, its cards and their one script inside it, no
external reference, relative links only (decision 61): it works in a folder opened from a disk, in a mirror, or under a path of a site.
Deterministic.

At the page's head, the cards of the day: a day's cards, their colours and the font for their letters are taken from the trainer
as built, `vocab/flashcards.html` — build the trainer first. The mark beside the name is `icon-192.png`, written into the page.

    python build_index.py        writes the three pages beside this file

A host's own page is this page written above the folder, with what belongs to a host: `page(folder, lang, at, host)`.
Standard library only. CC0.
"""
from __future__ import annotations
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = "corpus.json"
FOLDER = "lecturas"              # the folder's name on a host and in the mirror's repository: the two sentences that name it say this
TRAINER = "vocab/flashcards.html"
DAYS_FIRST = "12"                # the lectura whose cards were made first: it comes first in the turn, and its longest sentence is the measure of one that fits the card
RELEASED = ("PROVENANCE.md", "MANIFEST.sha256")   # written when the folder is released: listed wherever the page is built, so that the page is one
SITE_TITLE = "Vocabulario Libre" # the tab's title and the page's heading; each corpus keeps its own title (corpus.json)
MASTHEAD = "Vocabulario Libre"
LANGS = ["es", "en", "ja"]       # index.html is Spanish; index.<lang>.html for the others; each links to the other two
LANG_NAMES = {"es": "Español", "en": "English", "ja": "日本語"}   # the language line, in each language's own name
GUIDE_NAME = {"es": "como-usar.html", "en": "como-usar.en.html", "ja": "como-usar.ja.html"}      # build_pages.py builds them
GUIDE_LABEL = {"es": "Cómo usar", "en": "How to use", "ja": "使い方"}
COPY_PAGE = {"es": "copiar-y-cambiar.html", "en": "copiar-y-cambiar.en.html", "ja": "copiar-y-cambiar.ja.html"}
NEXT_PAGE = {"es": "proximos-cambios.html", "en": "proximos-cambios.en.html", "ja": "proximos-cambios.ja.html"}      # «Próximos cambios»: build_pages.py builds them
PRIMER_DOCS = (("PRIMER-sanskrit", "d_psa"), ("PRIMER-avestan", "d_pav"))  # the primers among the documents: the file's stem, its entry
# The line of every page: the main page, the trainer, the guide. By language: what a screen reader calls the line, and the main page's name.
NAV = {"es": ("Navegación", "Página principal"), "en": ("Navigation", "Main page"), "ja": ("ナビゲーション", "トップページ")}
NAV_CSS = (".nav { font-size: .9em; margin: 0 0 1em; } .nav a, .nav span { display: inline-block; padding: .35em 0; } .nav [aria-current] { font-weight: bold; }\n"
           ".nav-foot { margin: 1.5em 0 0; } footer .nav-foot { margin: 0; }\n"
           ".top { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 0 1em; margin: 0 0 1em; } .top .nav { margin: 0; }\n")

# ----------------------------------------------------------------------------- the page's style
CSS = """
:root { color-scheme: light dark; --fg: #1a1a1a; --bg: #fdfcf9; --mute: #5a5a5a; --rule: #d9d6cf; --link: #1f4d7a; --code: #efede8; }
@media (prefers-color-scheme: dark) { :root { --fg: #e8e6e1; --bg: #15171a; --mute: #a4a39e; --rule: #33363b; --link: #8ab4e0; --code: #22252a; } }
html { font-family: Georgia, "Times New Roman", "Noto Serif", serif; font-size: 18px; line-height: 1.5; }
body { margin: 0 auto; max-width: 44rem; padding: 2rem 1.25rem 4rem; color: var(--fg); background: var(--bg); }
.masthead { font-size: .95rem; letter-spacing: .08em; text-transform: uppercase; margin: 0 0 1.2rem; }
h1 { font-size: 1.9rem; font-weight: normal; margin: 0 0 .25rem; }
h2 { font-size: 1.05rem; font-weight: normal; letter-spacing: .05em; text-transform: uppercase; color: var(--mute);
     margin: 2.4rem 0 .6rem; border-bottom: 1px solid var(--rule); padding-bottom: .2rem; }
p { margin: .6rem 0; }
a { color: var(--link); text-decoration: none; } a:hover, a:focus { text-decoration: underline; }
code { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .85em; background: var(--code); padding: 0 .25em; }
table { border-collapse: collapse; width: 100%; font-size: .95rem; }
td { padding: .4rem .4rem .4rem 0; vertical-align: top; border-bottom: 1px solid var(--rule); }
td.n { color: var(--mute); width: 2.2rem; } td.l { white-space: nowrap; text-align: right; }
td.l a { margin-left: .7rem; }
ul { margin: .4rem 0 .4rem 1.2rem; padding: 0; } li { margin: .25rem 0; }
dl { margin: .4rem 0; } dt { margin-top: .5rem; } dd { margin: 0 0 0 1.2rem; color: var(--mute); font-size: .92rem; }
.mute { color: var(--mute); font-size: .9rem; }
h3.corpus { font-size: 1.3rem; font-weight: normal; margin: 1rem 0 .2rem; }   /* B3: a corpus entry under «Los textos» */
.lang { text-align: right; font-size: .9rem; margin: 0; }
footer { margin-top: 3rem; border-top: 1px solid var(--rule); padding-top: 1rem; font-size: .9rem; color: var(--mute); }
footer a { margin-right: .8rem; }
/* a narrow screen (U.2, D19): a row of the table is a block — the number, the title and its line, then the links, which wrap — so that no table holds the page wider
   than the screen. The number stands in the row's margin, as wide as its column was, and everything else of the row begins at one edge */
@media (max-width: 40rem) { table, tbody, tr, td { display: block; } tr { padding: .5rem 0 .5rem 2.2rem; border-bottom: 1px solid var(--rule); }
  td { border: 0; padding: 0; } td.n { float: left; width: 2.2rem; margin-left: -2.2rem; }
  td.l { display: flex; flex-wrap: wrap; gap: .1rem 1rem; padding-top: .2rem; white-space: normal; text-align: left; }
  td.l a { margin: 0; padding: .35rem 0; } td.l a:first-child { font-weight: bold; } }
"""


# ----------------------------------------------------------------------------- the page's words
STR = {
 "es": dict(
    status_label="",
    tagline="Quince textos de tres libertadores: Bolívar, San Martín, O’Higgins. Unas cuarenta mil palabras de cada "
            "uno, 1812–1843: manifiestos, discursos, proclamas, partes y oficios, cartas públicas y privadas, "
            "máximas. Orden cronológico. Texto de dominio público; todo lo demás —ediciones, aparato, glosas, "
            "programas— CC0: se copia, se aloja, se adapta, sin condición.",
    study="Estudiar",
    study_lead="Léxico — entrenador de vocabulario y asistente de lectura para los textos de la colección; hoy, las quince "
               "lecturas de los libertadores.",
    project="Ediciones de lectura y un entrenador de vocabulario para el estudio personal de las lenguas en que se escribieron "
            "los textos de la colección; hoy, el español.",
    study_items=[
        "Todas las formas que escribieron los autores, cerca de treinta mil, cada una con la frase en que aparece y "
        "una equivalencia en inglés; más de mil definiciones en español para las voces difíciles. La equivalencia "
        "sigue el sentido de la palabra en ese texto, no el del diccionario. Formas, no lemas: la forma es la que el "
        "lector encuentra en la página.",
        "El texto junto a sus fichas: se eligen párrafos (o los quince textos, por el índice) y se forman las fichas. "
        "El texto del autor y el aparato de la edición, por separado.",
        "Tres conjuntos de fichas: palabras; átomos — cada palabra gramatical en su lugar, con su función —; tramos — el "
        "trozo mínimo con equivalente propio —. Átomos y tramos sólo donde el sentido está certificado; lo demás dice «en revisión».",
        "Reconocer o producir; el idioma de cada cara se elige; índice por frecuencia o dispersión, en unidades de cien.",
        "Repaso espaciado. El progreso se guarda en el navegador y se exporta a un archivo.",
        "Un solo archivo. Sin red, sin instalación.",
    ],
    read="Los textos",
    texts_intro="Las piezas sueltas se eligieron por dos criterios del compilador: peso histórico y prosa. Las "
                "correspondencias y los impresos, por unidades —la serie entera a un corresponsal, el registro entero "
                "de un testimonio, un tramo de fechas fijado antes de leer las páginas—; dentro de la unidad nada se "
                "omite. A cada autor, prosa pública de los años de campaña y cartas privadas de sus últimas décadas; "
                "el cómputo de palabras se declara, no se ajusta. Entra solo lo que tiene testimonio impreso de "
                "dominio público, leído sobre la imagen de la página. Lo considerado y no adoptado consta en el "
                "manifiesto, con su razón. Dos textos de O’Higgins no son de su mano —el manifiesto de 1818, "
                "redactado por otro bajo su nombre; el discurso de 1823, transmitido por relato posterior—; se "
                "consigna y no se corrige. Las ediciones registran: declaran sus testimonios, anotan cada "
                "intervención, no juzgan.",
    words="palabras",
    version="versión",
    read_note="Cada edición: el texto, leído sobre la imagen de la página contra un testimonio impreso y fechado; "
              "la nota sobre el texto; el aparato —restituciones, correcciones de lectura, divergencias, "
              "normalización— con cada intervención, una por una; notas sobre las fuentes; clave de referencias; "
              "glosario; historial de revisiones; párrafos numerados. «Fuente» es ese texto en Markdown, del que se "
              "generan el PDF y el EPUB. «Registro» es la lista de comprobaciones que la edición superó —declaratorias, "
              "metodológicas, textuales, epistémicas, de reproducibilidad— y la prueba de cada una. Son ediciones de "
              "lectura para el estudio personal del español; no son ediciones críticas ni deben citarse como texto "
              "establecido.",
    links=("PDF", "EPUB", "fuente", "registro", "estudiar"),
    docs="Documentos",
    source_md="Fuente en Markdown",
    d_gov=("Documento rector", "Identifica y ordena las quince lecturas: quién firmó y quién redactó cada texto, "
           "cuándo, de qué testimonios procede y en qué estado se halla su edición."),
    d_pol=("Política de rigor y cumplimiento", "<i>Standards of Scholarship and Legal Compliance</i>: cada archivo "
           "de proveedor con su línea de derechos leída y archivada; cada persona de cada capa de cada testimonio, "
           "datada; la condición de publicación comprobada por programa antes de cada distribución."),
    d_prov=("Procedencia", "Cada archivo de proveedor consultado, con la línea de derechos leída en su página."),
    d_met=("El método de la capa gramatical", "<i>The method</i>: cómo se decide el sentido de cada palabra gramatical en su lugar, "
           "cómo se certifica o se aparta — nada dudoso llega a una ficha — y qué parte del corpus está certificada. Inglés."),
    d_psa=("Cartilla de sánscrito", "La escritura devanāgarī con su transliteración y sus sonidos, cómo se escribe una sílaba, "
           "las ligaduras y cómo se comprueba una forma. En español y en inglés. No es una gramática. Sin certificar: ninguna "
           "persona la ha comparado aún con sus fuentes."),
    d_pav=("Cartilla de avéstico", "La escritura avéstica con la transliteración de Hoffmann y sus sonidos, lo que imprime la "
           "edición de Geldner, las correspondencias con el sánscrito y las terminaciones. En español y en inglés. La escritura "
           "va en la fuente tipográfica del proyecto, trazada del tipo de Geldner; la procedencia da su relación. Sin certificar: "
           "ninguna persona la ha comparado aún con sus fuentes."),
    d_readme=("README", "Cómo está hecha la distribución y cómo reproducirla."),
    d_man=("Manifiesto de sumas", "Una suma SHA-256 por archivo publicado; véase «Réplica»."),
    d_lic=("Licencia", "CC0 1.0 Universal para el icono y para todo lo que no es texto histórico."),
    mirror="Réplica",
    mirror_text="Esta carpeta se replica copiándola entera. Para verificarla: <code>sha256sum -c MANIFEST.sha256</code> "
                "dentro de <code>{cid}/</code>. Para reconstruirla: los programas de la carpeta, con Python, reportlab y "
                "pyphen; el README da las órdenes.",
    copy="Copiar y cambiar",
    copy_text="La obra entera es una carpeta, <code>{cid}/</code>: las ediciones con sus fuentes, el entrenador con sus "
              "datos, los documentos, los programas que las construyen y las comprueban. Se obtiene entera del repositorio "
              "de la réplica, <code>github.com/vocabulario-libre/vocabulario-libre.github.io</code>, como un solo archivo "
              "comprimido o por clonación. Se cambia a mano o con un modelo de lenguaje; <code>check_folder.py</code>, en la "
              "carpeta, nombra lo que cambió.",
    copy_more="Cómo se hace",
    next_line='Próximos cambios: más lenguas en las fichas, griego, un panel de lógica, más obras en la biblioteca. La lista: «{a}Próximos cambios{z}».',      # {a}, {z}: the link to the page
    f_policy="Política",
 ),
 "en": dict(
    status_label="Status, from the governing document (Spanish): ",
    tagline="Fifteen texts by three liberators: Bolívar, San Martín, O’Higgins. About forty thousand words from "
            "each, 1812–1843: manifestos, speeches, proclamations, dispatches and official letters, public and "
            "private letters, maxims. Chronological order. The text is public domain; everything else — editions, "
            "apparatus, glosses, programs — is CC0: copy it, host it, adapt it, no condition.",
    study="Study",
    study_lead="Léxico — vocabulary trainer and reading assistant for the texts of the collection; today, the fifteen readings "
               "of the libertadores.",
    project="Reading editions and a vocabulary trainer for personal study of the languages the texts of the collection were "
            "written in; today, Spanish.",
    study_items=[
        "Every word form the authors wrote, close to thirty thousand, each with the sentence it appears in and an "
        "English equivalent; over a thousand Spanish definitions for the hard words. The equivalent follows the "
        "word’s sense in that text, not the dictionary’s. Forms, not lemmas: the form is what the reader meets on "
        "the page.",
        "The text beside its cards: choose paragraphs (or all fifteen texts, through the index) and the cards form. "
        "The author’s text and the edition’s apparatus, kept apart.",
        "Three card sets: words; atoms — each grammatical word in its place, with its function —; stretches — the smallest "
        "run with an equivalent of its own. Atoms and stretches only where the sense is certified; the rest says «under review».",
        "Recognise or produce; the language of each side is yours to choose; an index by frequency or spread, in units of a "
        "hundred. The interface is in Spanish, English or Japanese.",
        "Spaced repetition. Progress is saved in the browser and exported to a file.",
        "One file. No network, no install.",
    ],
    read="The texts",
    texts_intro="The standalone pieces were chosen on two criteria of the compiler’s: historical weight and prose. The "
                "correspondences and the printed papers, by unit — the whole series to one correspondent, the whole "
                "register of one witness, a date window fixed before the pages were read; nothing is omitted inside a "
                "unit. Each author has public prose from the campaign years and private letters from his last decades; "
                "the word count is reported, not engineered. Only what has a public-domain printed witness, read on "
                "the page image, enters. What was considered and not adopted is in the manifest, with its reason. Two "
                "of O’Higgins’s texts are not his hand — the 1818 manifesto, drafted by another under his name; the "
                "1823 speech, transmitted by later account; recorded, not corrected. The editions record: they declare "
                "their witnesses, note every intervention, pass no judgement.",
    words="words",
    version="version",
    read_note="Each edition: the text, read on the page image against a dated printed witness; the note on the "
              "text; the apparatus — restitutions, corrections of reading, divergences, normalisation — with every "
              "intervention listed one by one; notes on the sources; a reference key; a glossary; a revision "
              "history; numbered paragraphs. “Source” is that text in Markdown, from which the PDF and EPUB are "
              "generated. “Register” is the list of checks the edition passed — declaratory, methodological, "
              "textual, epistemic, reproducibility — with the proof of each. The editions, the trainer’s interface "
              "and the governing document are in Spanish; the glosses, the policy and the README are in English. "
              "These are reading editions for private study, not critical editions, and should not be cited as "
              "established text.",
    links=("PDF", "EPUB", "source", "register", "study"),
    docs="Documents",
    source_md="Source in Markdown",
    d_gov=("Governing document", "Identifies and orders the fifteen readings: who signed and who drafted each text, "
           "when, from which witnesses it comes and the state of its edition. Spanish, with an English part."),
    d_pol=("Scholarship and compliance policy", "<i>Standards of Scholarship and Legal Compliance</i>: every "
           "provider file with its rights line read and filed; every person in every layer of every witness, dated; "
           "the condition for publication checked by program before each distribution. English."),
    d_prov=("Provenance", "Every provider file consulted, with the rights line read on its page."),
    d_met=("The method of the grammar layer", "<i>The method</i>: how the sense of every grammatical word in its place is decided, "
           "how it is certified or quarantined — nothing doubtful reaches a card — and what share of the corpus is certified. English."),
    d_psa=("Sanskrit primer", "The Devanāgarī script with its transliteration and sounds, how a syllable is written, the "
           "ligatures, and how a form is checked. In Spanish and English. Not a grammar. Not certified: no person has yet "
           "compared it with its sources."),
    d_pav=("Avestan primer", "The Avestan script with Hoffmann’s transliteration and its sounds, what Geldner’s edition prints, "
           "the correspondences with Sanskrit, and the endings. In Spanish and English. The script is set in the project’s font, "
           "traced from Geldner’s type; the provenance record gives its account. Not certified: no person has yet compared it "
           "with its sources."),
    d_readme=("README", "How the distribution is made and how to reproduce it."),
    d_man=("Manifest of checksums", "One SHA-256 per published file; see “Mirror”."),
    d_lic=("Licence", "CC0 1.0 Universal for the icon and for everything that is not historical text."),
    mirror="Mirror",
    mirror_text="This folder is mirrored by copying it whole. To verify it: <code>sha256sum -c MANIFEST.sha256</code> "
                "inside <code>{cid}/</code>. To rebuild it: the programs in the folder, with Python, reportlab and "
                "pyphen; the README gives the commands.",
    copy="Copy and change",
    copy_text="The whole work is one folder, <code>{cid}/</code>: the editions with their sources, the trainer with its "
              "data, the documents, the programs that build and check them. It is had whole from the mirror’s repository, "
              "<code>github.com/vocabulario-libre/vocabulario-libre.github.io</code>, as one archive or by a clone. It is "
              "changed by hand or by a language model; <code>check_folder.py</code>, in the folder, names what changed.",
    copy_more="How it is done",
    next_line='Upcoming changes: more languages on the cards, Greek, a logic pane, more works in the library. The list: «{a}Upcoming changes{z}».',
    f_policy="Policy",
 ),
 "ja": dict(
    status_label="現況（統括文書より、スペイン語）：",
    tagline="三人の解放者 — ボリーバル、サン・マルティン、オイギンス — の十五のテキスト。各人およそ四万語、1812–1843年："
            "宣言、演説、布告、戦況報告と公文書、公開の書簡と私信、箴言。年代順。本文はパブリックドメイン。それ以外のすべて "
            "— 校訂版、校訂注、訳語、プログラム — は CC0：複製も、ホスティングも、改変も、無条件。",
    study="学習",
    study_lead="Léxico — 収録文書のための語彙トレーナー・読解補助。現在は解放者たちの十五の文書。",
    project="収録文書が書かれた言語を個人で学ぶための読解用校訂版と語彙トレーナー。現在はスペイン語。",
    study_items=[
        "著者たちが書いたすべての語形、およそ三万。それぞれに出現する文と英語の訳語を付し、難しい語には千を超えるスペイン語の定義を"
        "添える。訳語は辞書の語義ではなく、そのテキストでの意味に従う。見出し語ではなく語形：読者が紙面で出会うのは語形である。",
        "本文の横にカード：段落を選ぶと（索引からは十五のテキスト全体も）カードができる。著者の本文と校訂版の校訂注は分けて扱う。",
        "三種のカード：語；要素 ― 各機能語をその位置で、その機能とともに ―；区間 ― 固有の対応をもつ最小の連なり。要素と区間は意味が"
        "検証済みの箇所だけ。残りは「審査中」と示す。",
        "認識と穴埋め。カードの表裏の言語は選べる。索引は頻度順か分布順、百語ずつ。インターフェースはスペイン語、英語、日本語。",
        "間隔反復。進捗はブラウザに保存され、ファイルに書き出せる。",
        "ファイル一つ。ネットワーク不要、インストール不要。",
    ],
    read="テキスト",
    texts_intro="単独の作品は編者の二つの基準 — 歴史的な重みと文章 — で選んだ。書簡集と刊行文書は単位ごとに — 一人の相手への"
                "全書簡、一つの証本の全記録、ページを読む前に定めた日付の範囲 —、単位の内側では何も省かない。各著者について、"
                "戦役期の公的な散文と晩年の私信。語数は報告するものであって、調整するものではない。パブリックドメインの印刷証本が"
                "あり、ページ画像の上で読んだものだけが入る。検討して採らなかったものは、理由とともに統括文書に記す。オイギンスの"
                "二つのテキストは本人の筆ではない — 1818年の宣言は他者が彼の名で起草し、1823年の演説は後の記録によって伝わる —。"
                "記録し、訂正しない。校訂版は記録する：証本を明示し、すべての介入を注記し、判断を下さない。",
    words="語",
    version="版",
    read_note="各校訂版：日付のある印刷証本に対し、ページ画像の上で読んだ本文；本文についての注記；校訂注 — 復元、読みの訂正、"
              "異同、正書法の統一 — をすべての介入について一つずつ；出典についての注記；参照記号の凡例；用語集；改訂履歴；"
              "番号付きの段落。「ソース」は Markdown の本文で、PDF と EPUB はそこから生成する。「記録」は校訂版が通過した検査の"
              "一覧 — 宣言、方法、本文、認識、再現性 — と、それぞれの証拠。校訂版と統括文書はスペイン語；トレーナーの"
              "インターフェースはスペイン語、英語、日本語；訳語、方針、README は英語。これらは個人の学習のための読書用校訂版で"
              "あり、批判的校訂版ではない。確定した本文として引用してはならない。",
    links=("PDF", "EPUB", "ソース", "記録", "学習"),
    docs="文書",
    source_md="Markdown のソース",
    d_gov=("統括文書", "十五の読み物を特定し、順序づける：各テキストに誰が署名し、誰が起草したか、いつ、どの証本に由来し、"
           "校訂版はどの段階にあるか。スペイン語、英語の部分あり。"),
    d_pol=("学術的厳密さと法令遵守の方針", "<i>Standards of Scholarship and Legal Compliance</i>：提供元の各ファイルについて"
           "権利表示を読んで記録；各証本の各層の各人物に日付；公開の条件は配布のたびにプログラムで検査。英語。"),
    d_prov=("来歴", "参照した提供元の各ファイルと、そのページで読んだ権利表示。"),
    d_met=("文法レイヤーの方法", "<i>The method</i>：各機能語の意味をその位置でどう決めるか、どう検証し、または保留するか"
           "（疑わしいものはカードにならない）、コーパスのどの部分が検証済みか。英語。"),
    d_psa=("サンスクリットの手引き", "デーヴァナーガリー文字とその翻字と音、音節の書き方、合字、語形の検査の仕方。スペイン語と英語。"
           "文法書ではない。未検証：出典との照合を人がまだ行っていない。"),
    d_pav=("アヴェスター語の手引き", "アヴェスター文字とホフマン式の翻字と音、ゲルトナー版の印刷、サンスクリットとの対応、語尾。"
           "スペイン語と英語。文字はプロジェクトのフォントで組む。ゲルトナー版の活字から輪郭を取ったもので、その記録は来歴にある。"
           "未検証：出典との照合を人がまだ行っていない。"),
    d_readme=("README", "配布物の作り方と再現の仕方。"),
    d_man=("チェックサム目録", "公開ファイルごとに SHA-256 を一つ。「ミラー」を参照。"),
    d_lic=("ライセンス", "アイコンと、歴史的本文以外のすべてに CC0 1.0 Universal。"),
    mirror="ミラー",
    mirror_text="このフォルダは丸ごと複製してミラーする。検証するには：<code>{cid}/</code> の中で "
                "<code>sha256sum -c MANIFEST.sha256</code>。再構築するには：フォルダ内のプログラムと、Python、reportlab、"
                "pyphen。コマンドは README にある。",
    copy="複製と改変",
    copy_text="作品の全体が一つのフォルダ <code>{cid}/</code> である：校訂版とそのソース、トレーナーとそのデータ、文書、"
              "それらを生成し検査するプログラム。ミラーのリポジトリ "
              "<code>github.com/vocabulario-libre/vocabulario-libre.github.io</code> から、一つのアーカイブとして、または"
              "クローンで、丸ごと入手できる。手でも、言語モデルでも変えられる。フォルダ内の <code>check_folder.py</code> が、"
              "変わったものを示す。",
    copy_more="その方法",
    next_line='今後の予定：カードの言語の追加、ギリシア語、論理パネル、ライブラリの作品の追加。一覧：「{a}今後の予定{z}」。',
    f_policy="方針",
 ),
}


def tipo(s: str) -> str:
    """Typographic apostrophe in displayed text (the manifest writes O'Higgins with a straight one)."""
    return html.escape(s).replace("&#x27;", "’")


def estado(governing: Path) -> str:
    """The governing document's Estado line: its first sentence."""
    text = governing.read_text(encoding="utf-8")
    m = re.search(r"^## Estado\s*\n+(.+?)\n", text, re.M | re.S)
    line = m.group(1).strip() if m else ""
    line = line.replace("**", "")
    return re.split(r"(?<=[.!?])\s+", line)[0]


def page_name(lang: str) -> str:
    return "index.html" if lang == "es" else f"index.{lang}.html"


def nav(lang: str, here: str = "", at: str = "", foot: bool = False) -> str:
    """The line that stands at the head and at the foot of every page: the main page, the trainer, the guide — in the page's
    language, each link leading to that page in the same language. `here`: which of the three the page itself is — «main»,
    «trainer», «guide» —, written as plain text and not as a link; nothing where the page is none of them. `at`: where the
    folder stands from the page. `foot`: the line as it stands at the foot."""
    words = {"main": NAV[lang][1], "trainer": "Léxico", "guide": GUIDE_LABEL[lang]}
    to = {"main": at + page_name(lang), "trainer": at + TRAINER + ("" if lang == "es" else "#" + lang), "guide": at + GUIDE_NAME[lang]}
    items = [f'<span aria-current="page">{tipo(words[k])}</span>' if k == here else f'<a href="{to[k]}">{tipo(words[k])}</a>' for k in ("main", "trainer", "guide")]
    return f'<nav class="nav{" nav-foot" if foot else ""}" aria-label="{NAV[lang][0]}">' + " · ".join(items) + "</nav>"


# ----------------------------------------------------------------------------- the cards of the day
# One sentence of the collection a day, with the cards of its words: the same for every reader on the same date. The days are
# made from the trainer as built — its sentences, its words and their forms — so that a card here is the trainer's card.
_TRAINER: dict = {}


def trainer_data(folder: Path) -> tuple[dict, dict]:
    """What the built trainer carries: its texts with their sentences and words, and the forms of the words in the other
    languages. Read once for a file as it stands."""
    f = folder / TRAINER
    key = (str(f), f.stat().st_mtime_ns, f.stat().st_size)
    if key not in _TRAINER:
        text, read = f.read_text(encoding="utf-8"), json.JSONDecoder().raw_decode
        data = read(text, text.index("const DATA = ") + len("const DATA = "))[0]
        grammar = read(text, text.index("GRAMMAR = ") + len("GRAMMAR = "))[0]
        _TRAINER.clear(); _TRAINER[key] = (data, grammar.get("F") or {})
    return _TRAINER[key]


def fits(sentence: str, longest: int) -> bool:
    """A sentence is a day's if it is no longer than the longest whose card fits the page."""
    return len(sentence) <= longest


def share(counts: list[int], room: int) -> int:
    """The number of days each lectura gives: the largest with which the days of all — each lectura giving that many, or all it
    has — are no more than the page has room for."""
    k = 0
    while k < max(counts, default=0) and sum(min(k + 1, c) for c in counts) <= room: k += 1
    return k


def spread(items: list, k: int) -> list:
    """k of a lectura's sentences, at even steps through its text, the first among them; all of them where it has no more."""
    n = len(items)
    return list(items) if k >= n else [items[(i * n) // k] for i in range(k)]


def cycle(lists: list[list]) -> list:
    """The days in their order: the lecturas take turns, each giving its next; one that has given all it has is passed over."""
    out, i = [], 0
    while any(i < len(x) for x in lists):
        out += [x[i] for x in lists if i < len(x)]; i += 1
    return out


def word_sentences(data: dict, forms: dict, lectura: str) -> dict[int, list]:
    """The sentences of a lectura's own text that hold a word's card: for each, its words that have forms, where they stand."""
    words, found = forms.get("W") or {}, {}
    for e in data["entries"]:
        if e["t"] != lectura or e.get("src_deck") != "text" or f"{e['w']}\t{e['en']}" not in words: continue
        for s, a, b in e["ctx"]: found.setdefault(s, []).append((a, b, e))
    return {s: sorted(found[s], key=lambda x: x[0]) for s in sorted(found)}


def day(data: dict, forms: dict, lectura: str, s: int, items: list) -> dict:
    """One day: the lectura, the paragraph, the sentence, and a card for each of its words — the word as it stands, its place, its
    equivalent, its definition where it has one, and in each language its form with its reading, its letters and its tier."""
    sent, langs, cards = data["sentences"][s], forms.get("langs") or [], []
    for a, b, e in items:
        card = {"w": sent[a:b], "a": a, "b": b, "en": e["en"]}
        if e.get("d"): card["d"] = e["d"]
        for lang, f in zip(langs, forms["W"][f"{e['w']}\t{e['en']}"]["f"]):
            if not f or not f.get("f"): continue
            card[lang] = {k: (str(f[k]) if k == "t" else f[k]) for k in ("f", "r", "s", "t") if f.get(k)}
        cards.append(card)
    return {"t": lectura, "p": data["sentPara"][s], "sent": sent, "cards": cards}


def days(folder: Path, room: int | None = None, each: int | None = None) -> list[dict]:
    """The days, in their order. A day is a sentence of a lectura's own text that holds a word's card and is no longer than the
    longest of the first lectura's; the lecturas whose words have their forms take turns, the first lectura first; and where
    the page has room for fewer days than there are (`room`), each lectura gives the same number — the largest the room
    allows —, at even steps through its text, a lectura with fewer giving all it has. `each`: that number, given outright."""
    data, forms = trainer_data(folder)
    made = sorted(forms.get("T") or {}, key=lambda t: (t != DAYS_FIRST, t))
    by = {t: word_sentences(data, forms, t) for t in made}
    longest = max((len(data["sentences"][s]) for s in by.get(DAYS_FIRST, {})), default=0)
    fit = {t: [s for s in by[t] if fits(data["sentences"][s], longest)] for t in made}
    if room is not None or each is not None:
        k = each if each is not None else share([len(fit[t]) for t in made], room)
        fit = {t: spread(fit[t], k) for t in made}
    return cycle([[day(data, forms, t, s, by[t][s]) for s in fit[t]] for t in made])


# ----------------------------------------------------------------------------- the card of the day, on the page
PAGE_BUDGET = 200_000            # bytes: a main page is one plain page, there at once
CARD_WORDS = {"es": ("Fichas del día", "Ficha anterior", "Ficha siguiente"), "en": ("Cards of the day", "Previous card", "Next card"),
              "ja": ("今日のカード", "前のカード", "次のカード")}      # the caption over the card; what a screen reader calls ‹ and ›
FRONT = {"es": ("es", "ja"), "ja": ("es", "ja"), "en": ("es",)}      # the languages a card opens with on its front, by the page's language; the others stand on its back
TIERS = ("2", "3", "3r", "4")    # the tiers of a form that the trainer says in words
_LOOK: dict = {}


def trainer_look(folder: Path) -> dict:
    """What the page takes from the trainer as built, so that its card is the trainer's: the colours, light and dark; the width
    under which a screen is narrow; and the trainer's own words, in each language, for the card's faces, how a card is asked,
    the shuffled order, the tiers of a form, and the mark of a form that no person has checked."""
    f = folder / TRAINER
    key = (str(f), f.stat().st_mtime_ns, f.stat().st_size)
    if key not in _LOOK:
        t = f.read_text(encoding="utf-8")
        def need(pattern: str, where: str, what: str):
            m = re.search(pattern, where, re.S)
            if not m: raise SystemExit(f"build_index: the trainer's {what} is not where it was")
            return m.group(1)
        look = {"light": " ".join(need(r":root\{(.*?)\}", t, "colours").split()),
                "dark": " ".join(need(r"@media \(prefers-color-scheme:dark\)\{\s*:root\{(.*?)\}", t, "dark colours").split()),
                "rule": need(r"@media (\(max-width:(\d+)px\)(?:,\(max-height:\2px\) and \(pointer:coarse\))?)\{\s*\.panes", t, "narrow rule"), "words": {}}
        look["narrow"] = int(re.search(r"\d+", look["rule"]).group(0))
        faces = re.findall(r"@font-face\s*\{[^}]*\}", t)       # the trainer carries the project's font where the row of the font is open, and none where it is closed
        if len(faces) > 1: raise SystemExit("build_index: the trainer carries more than one font")
        look["face"] = faces[0] if faces else ""
        at = t.index("const STRINGS")
        for n, lang in enumerate(LANGS):
            a = t.index(f"\n  {lang}: {{", at)
            b = t.index(f"\n  {LANGS[n + 1]}: {{", a) if n + 1 < len(LANGS) else len(t)
            word = lambda k: json.loads('"' + need(r'\b%s: "((?:[^"\\]|\\.)*)"' % k, t[a:b], f"word «{k}» in {lang}") + '"')
            look["words"][lang] = {"front": word("front"), "back": word("back"), "recog": word("d_recog"), "cloze": word("d_cloze"), "shuffle": word("o_shuffle"),
                                   "unchecked": word("unchecked"), "tiers": {k: word("tier_" + k) for k in TIERS}}
        _LOOK.clear(); _LOOK[key] = look
    return _LOOK[key]


def sides(lang: str, langs: list[str]) -> tuple[list[str], list[str], list[str]]:
    """The languages of a card in the trainer's order, and those of its front and of its back as the page opens."""
    every = ["es", "en"] + [l for l in langs if l not in ("es", "en")]
    front = [l for l in every if l in FRONT[lang]]
    return every, front, [l for l in every if l not in front]


def sides_segment(front: list[str], back: list[str]) -> str:
    """The sides as the trainer's address takes them; nothing for the trainer's own, Spanish to English."""
    return "" if (front, back) == (["es"], ["en"]) else "+".join(front) + "~" + "+".join(back) + "/"


def trainer_address(at: str, lang: str, front: list[str], back: list[str], lectura: str, para: int) -> str:
    """Where «study» leads: the trainer in the page's language, on the day's paragraph, with the sides as they are set."""
    return f"{at}{TRAINER}#{'' if lang == 'es' else lang + '/'}{sides_segment(front, back)}{lectura}/{para}"


def card_row(L: str, c: dict, look: dict, lang: str) -> str:
    """One language's row of a card's face; nothing for a language the card has no form in."""
    e = html.escape
    if L == "es": return f'<h3 class="headword" lang="es">{e(c["w"])}</h3>'
    if L == "en": return f'<div class="side"><span class="lg">EN</span><span class="fm" lang="en">{e(c["en"])}</span></div>'
    f = c.get(L)
    if not f: return ""
    W = look["words"][lang]
    form = f'<span class="av">{e(f["s"])}</span>' if f.get("s") else e(f["f"])
    under = f["f"] if f.get("s") else f.get("r")
    tier = W["tiers"].get(f.get("t", ""))
    return (f'<div class="side"><span class="lg">{L.upper()}</span><span class="fm" lang="{L}">{form}</span><span class="mk" title="{e(W["unchecked"])}">◇</span>'
            + (f'<span class="k">{e(tier)}</span>' if tier else "") + (f'<div class="sub">{e(under)}</div>' if under else "") + "</div>")


def card_html(d: dict, i: int, look: dict, lang: str, every: list[str], front: list[str], back: list[str]) -> str:
    """One card laid open, as plain text: its front, its sentence, its back. What stands where no script runs, and what the script draws over."""
    e, c, s = html.escape, d["cards"][i], d["sent"]
    faces = ["".join(card_row(L, c, look, lang) for L in every if L in side) for side in (front, back)]
    ctx = f'{e(s[:c["a"]])}<b>{e(s[c["a"]:c["b"]])}</b>{e(s[c["b"]:])}'
    said = re.sub(r"[*]([^*]+)[*]", r"<i>\1</i>", e(c["d"])) if c.get("d") else ""       # made outside the f-string: a backslash inside one's braces is read only from Python 3.12
    note = f'<p class="def">{said}</p>' if said else ""
    return f'{faces[0]}<p class="ctx" lang="es">{ctx}</p><div class="back">{faces[1]}{note}</div>'


# The card's script: one text, the same on every page and in every language. It reads the day from the reader's own clock and
# works the card. It asks nothing of the network, stores nothing, and reads nothing of the reader but the date.
CARD_SCRIPT = r"""(function(){
var D=JSON.parse(document.getElementById("dias").textContent),N=D.days.length,LANG=document.documentElement.lang,i=0,back=false,mode="recog",mixed=false,order=[];
var S={front:D.front.slice(),back:D.back.slice()},box=document.getElementById("ficha"),$=function(id){return document.getElementById(id)};
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function today(){var n=new Date();return Math.floor(Date.UTC(n.getFullYear(),n.getMonth(),n.getDate())/864e5)}
function set(){return D.days[((today()%N)+N)%N]}
function deal(){var m=set().cards.length,k,r,x;order=[];for(k=0;k<m;k++)order.push(k);if(mixed)for(k=m-1;k>0;k--){r=Math.floor(Math.random()*(k+1));x=order[k];order[k]=order[r];order[r]=x}i=0;back=false}
function row(L,c){if(L==="es")return'<h3 class="headword" lang="es">'+esc(c.w)+'</h3>';
 if(L==="en")return'<div class="side"><span class="lg">EN</span><span class="fm" lang="en">'+esc(c.en)+'</span></div>';
 var f=c[L],u,t;if(!f)return"";u=f.s?f.f:f.r;t=f.t?D.tiers[f.t]:"";
 return'<div class="side"><span class="lg">'+L.toUpperCase()+'</span><span class="fm" lang="'+L+'">'+(f.s?'<span class="av">'+esc(f.s)+'</span>':esc(f.f))+'</span><span class="mk" title="'+esc(D.note)+'">◇</span>'+(t?'<span class="k">'+esc(t)+'</span>':'')+(u?'<div class="sub">'+esc(u)+'</div>':'')+'</div>'}
function face(side,c,hide){var h="";D.all.forEach(function(L){if(S[side].indexOf(L)<0||L===hide)return;h+=row(L,c)});return h}
function ctx(d,c,gap){var s=d.sent;return'<p class="ctx" lang="es">'+esc(s.slice(0,c.a))+(gap?'<b class="gap">'+new Array(c.w.length+1).join(" ")+'</b>':'<b>'+esc(s.slice(c.a,c.b))+'</b>')+esc(s.slice(c.b))+'</p>'}
function seg(){var f=D.all.filter(function(L){return S.front.indexOf(L)>=0}).join("+"),b=D.all.filter(function(L){return S.back.indexOf(L)>=0}).join("+");return f==="es"&&b==="en"?"":f+"~"+b+"/"}
function each(q,fn){Array.prototype.forEach.call(document.querySelectorAll(q),fn)}
function draw(){var d=set(),c=d.cards[order[i]],cloze=mode==="cloze",h="",f,up=back?"back":"front";
 if(!back){f=face("front",c,cloze?"es":"");if(cloze&&!f)f=row("en",c);h+=f;if(cloze)h+=ctx(d,c,true);else if(S.front.indexOf("es")>=0)h+=ctx(d,c,false)}
 else{h+=(cloze&&S.back.indexOf("es")<0?row("es",c):"")+face("back",c,"");if(c.d)h+='<p class="def">'+esc(c.d).replace(/\*([^*]+)\*/g,"<i>$1</i>")+'</p>';h+=ctx(d,c,false)}
 box.innerHTML=h;$("donde").textContent=d.t+" · § "+d.p;$("obra").textContent=D.titles[d.t]||"";
 $("fecha").textContent=new Date().toLocaleDateString(LANG==="en"?"en-GB":LANG,{day:"numeric",month:"long"});$("cuenta").textContent=(i+1)+" / "+d.cards.length;
 $("ir").setAttribute("href",D.trainer+"#"+(LANG==="es"?"":LANG+"/")+seg()+d.t+"/"+d.p);
 each("#cara button",function(b){b.setAttribute("aria-pressed",b.getAttribute("data-c")===up?"true":"false")});
 each("#lados button",function(b){b.setAttribute("aria-pressed",S[up].indexOf(b.getAttribute("data-l"))>=0?"true":"false")});
 each("#modo button",function(b){b.setAttribute("aria-pressed",b.getAttribute("data-m")===mode?"true":"false")});
 $("mix").setAttribute("aria-pressed",mixed?"true":"false")}
function turn(){back=!back;draw()}function go(k){var m=order.length;i=((i+k)%m+m)%m;back=false;draw()}
box.addEventListener("click",turn);box.tabIndex=0;
box.addEventListener("keydown",function(e){if(e.key===" "||e.key==="Enter"){e.preventDefault();turn()}else if(e.key==="ArrowRight")go(1);else if(e.key==="ArrowLeft")go(-1)});
$("antes").addEventListener("click",function(){go(-1)});$("luego").addEventListener("click",function(){go(1)});
each("#cara button",function(b){b.addEventListener("click",function(){back=b.getAttribute("data-c")==="back";draw()})});
each("#lados button",function(b){b.addEventListener("click",function(){var side=back?"back":"front",L=b.getAttribute("data-l"),k=S[side].indexOf(L);
 if(k>=0){if(S[side].length>1)S[side].splice(k,1)}else S[side].push(L);draw()})});
each("#modo button",function(b){b.addEventListener("click",function(){mode=b.getAttribute("data-m");back=false;draw()})});
$("mix").addEventListener("click",function(){mixed=!mixed;deal();draw()});
document.documentElement.className+=" js";deal();draw()})()"""

CARD_CSS = """
/* the cards of the day: the card is one object — its head (where it is from; which face is up, and that face's languages), the face, its foot (the day's cards, how they are asked, and the one action) */
.day { @@LIGHT@@ margin: 1.2rem 0 0; }
@media (prefers-color-scheme: dark) { .day { @@DARK@@ } }
.day .cap { display: flex; flex-wrap: wrap; gap: .2rem .8rem; align-items: baseline; font-family: var(--mono); font-size: .62rem; letter-spacing: .09em; text-transform: uppercase; color: var(--ink-3); margin: 0 0 .4rem; }
.day .cap b { color: var(--ink-2); font-weight: 600; }
.card { background: var(--leaf); color: var(--ink); border: 1px solid var(--rule); border-radius: 4px; box-shadow: var(--shadow); padding: .8rem 1.1rem 0; font-family: var(--serif);
        display: grid; grid-template-columns: auto 1fr auto; grid-template-areas: "head head head" "face face face" "steps opts go"; column-gap: .6rem; align-items: center; }
.card .chead { grid-area: head; display: flex; flex-wrap: wrap; align-items: center; gap: .4rem .6rem; border-bottom: 1px solid var(--rule); padding-bottom: .6rem; }
.card .where { font-family: var(--mono); font-size: .6rem; letter-spacing: .09em; text-transform: uppercase; color: var(--verdigris); margin-right: auto; }
.card #ficha { grid-area: face; cursor: pointer; padding: .8rem 0 .7rem; min-height: 6.5rem; border-bottom: 1px dashed var(--rule); } .card #ficha:focus-visible { outline: 2px solid var(--verdigris); outline-offset: 2px; }
.card .bar { display: contents; } .card .steps { grid-area: steps; display: flex; align-items: center; } .card .opts { grid-area: opts; display: flex; gap: .5rem; justify-self: start; } .card .go { grid-area: go; }
.card .steps, .card .opts, .card .go { margin: .6rem 0 .7rem; }
.card button { font: inherit; font-family: var(--sans); font-size: .68rem; height: 1.8rem; min-width: 1.8rem; padding: 0 .55rem; border: 1px solid var(--rule); border-radius: 3px; background: transparent; color: var(--ink-2); cursor: pointer; position: relative; }
.card button[aria-pressed="true"] { border-color: var(--verdigris); color: var(--verdigris); background: var(--verdigris-soft); z-index: 1; }
.card .seg { display: inline-flex; } .card .seg button { border-radius: 0; margin-left: -1px; } .card .seg button:first-child { border-radius: 3px 0 0 3px; margin-left: 0; } .card .seg button:last-child { border-radius: 0 3px 3px 0; }
.card .chips { display: inline-flex; gap: .2rem; } .card .chips button { font-family: var(--mono); font-size: .58rem; letter-spacing: .05em; padding: 0; width: 1.9rem; }
.card #cuenta { font-family: var(--mono); font-size: .62rem; color: var(--ink-3); min-width: 2.6rem; text-align: center; }
.card .go { display: inline-block; height: 2.1rem; line-height: 2.1rem; padding: 0 1.3rem; border-radius: 3px; background: var(--verdigris); color: var(--on-verdigris); font-family: var(--sans); font-size: .85rem; font-weight: 600; text-decoration: none; text-align: center; }
.card .headword { font-size: 1.9rem; line-height: 1.15; font-weight: 500; margin: 0 0 .3rem; }
.card .ctx { font-size: .85rem; line-height: 1.6; color: var(--ink-3); margin: .6rem 0 0; }
.card .ctx b { color: var(--ink); font-weight: 600; background: var(--verdigris-soft); padding: 0 2px; border-radius: 2px; }
.card .gap { background: var(--verdigris-soft); border-bottom: 1px solid var(--verdigris); white-space: pre; }
.card .side { margin: 0 0 .3rem; } .card .lg { font-family: var(--mono); font-size: .55rem; letter-spacing: .09em; color: var(--ink-3); margin-right: .5rem; }
.card .fm { font-size: 1.1rem; line-height: 1.4; } .card .mk { color: var(--ochre); margin-left: .5rem; font-size: .8rem; } .card .k { font-family: var(--mono); font-size: .55rem; color: var(--ink-3); margin-left: .4rem; }
.card .sub { font-family: var(--sans); font-size: .7rem; color: var(--ink-2); margin-left: 1.5rem; } .card .def { font-size: .85rem; color: var(--ink-2); margin: .5rem 0 0; }
.day .legend { font-size: .72rem; color: var(--mute); margin: .5rem 0 0; } .day .legend .mk { color: var(--ochre); margin-right: .3rem; }
html:not(.js) .needs-js { display: none; }
/* a narrow screen: the card's parts one under another; the languages a row of their own, as wide as the card; the row of the one action at the screen's foot
   while the card is in view — under the thumb, and on the first screen whatever the card's height. Narrow by its width alone: on a phone held sideways
   that row would cover the card's word, and the card is laid there as on a wide screen */
@media @@WIDTH@@ { html.js .day .cap #obra { display: none; } .day { margin-top: .8rem; }
  .card { display: flex; flex-direction: column; align-items: stretch; padding: .7rem .9rem 0; }
  .card .chips { flex: 1 0 100%; display: flex; } .card .chips button { flex: 1 1 0; width: auto; }
  .card #ficha { border-bottom: 0; padding-bottom: .5rem; } .card .opts { order: 3; margin: 0 0 .6rem; }
  .card .bar { order: 4; display: flex; align-items: center; gap: .6rem; position: sticky; bottom: 0; z-index: 3; background: var(--leaf); border-top: 1px dashed var(--rule); margin: 0 -.9rem; padding: .5rem .9rem; border-radius: 0 0 4px 4px; }
  .card .steps, .card .go { margin: 0; } .card .go { flex: 1 1 auto; } }
"""


def font_css(folder: Path) -> str:
    """The font a page carries for the letters a reader's system may lack: the trainer's own, as the trainer carries it — its one rule,
    byte for byte —, with the class that asks for it by the name that rule gives it. Nothing where the trainer carries none: the
    page has the letters where the trainer has them, and not otherwise."""
    face = trainer_look(folder)["face"]
    if not face: return ""
    family = re.search(r'font-family:\s*("[^"]+"|[\w-]+)', face)
    if not family: raise SystemExit("build_index: the trainer's font gives no name to ask for it by")
    return f"{face}\n.av {{ font-family: {family.group(1)}, serif; }}\n"


MARK = "icon-192.png"            # the project's mark: the picture an installed copy shows, beside the name at the page's head
PAGES_NARROW = re.search(r"@media (\([^)]*\)) \{ table, tbody", CSS).group(1)      # the pages' own rule for a narrow screen, where no trainer gives the card's

# The head of a main page: the mark and the name, the page's one sentence; on a host's page the square code and the address beside
# them — behind one word where the screen is narrow, so that the card stands on the first screen.
HEAD_CSS = """
.head { display: flex; gap: 1.5rem; align-items: flex-start; } .head .say { flex: 1 1 auto; min-width: 0; }
.name { display: flex; align-items: center; gap: .8rem; margin: 0 0 .4rem; } .name h1 { margin: 0; }
.name .mark { flex: none; width: 3rem; height: 3rem; border-radius: 22%; background: center / contain no-repeat; }
.top { position: relative; }
.code-wide { flex: none; text-align: center; font-size: .7rem; color: var(--mute); } .code-wide svg { display: block; margin: 0 auto .2rem; }
.share { display: none; font-size: .9rem; } .share summary { cursor: pointer; color: var(--link); list-style: none; padding: .35em 0; } .share summary::-webkit-details-marker { display: none; }
.share .pop { position: absolute; right: 0; top: 100%; z-index: 5; background: var(--bg); border: 1px solid var(--rule); padding: .8rem; text-align: center; box-shadow: 0 6px 22px -14px #000; }
.share .pop svg { display: block; margin: 0 auto; } .share .pop code { display: block; margin-top: .4rem; font-size: .75rem; }
@media @@RULE@@ { .share { display: block; } .code-wide { display: none; } body { padding-top: 1rem; } h1 { font-size: 1.6rem; }
  .top { margin-bottom: .5rem; } .name { margin-bottom: .2rem; } .name .mark { width: 2.4rem; height: 2.4rem; } }
"""


def narrow_rule(folder: Path) -> str:
    """The screens a main page lays its head out for as narrow: the trainer's own rule where the folder has a trainer — the card is
    the trainer's, and the head makes room for it —, else the pages' own."""
    return trainer_look(folder)["rule"] if (folder / TRAINER).is_file() else PAGES_NARROW


def head_css(folder: Path) -> str:
    """The style of the page's head, with the mark written into it as data where the mark's file stands in the folder."""
    mark = folder / MARK
    image = ""
    if mark.is_file():
        import base64
        image = f".name .mark {{ background-image: url(data:image/png;base64,{base64.b64encode(mark.read_bytes()).decode('ascii')}); }}\n"
    return HEAD_CSS.replace("@@RULE@@", narrow_rule(folder)) + image


def card_parts(folder: Path, made: list[dict], lang: str, at: str) -> tuple[str, str, str]:
    """The card of the day for one page: its style; its section — the caption, the card laid open as it stands where no script runs,
    the mark's sentence —; and, for the page's end, the days as data and the script. Nothing where there is no day."""
    if not made: return "", "", ""
    font = font_css(folder)
    if not font:                                            # no font in the page: a form in the letters of a script the page cannot draw is given in Latin letters alone
        made = [dict(d, cards=[{k: ({x: y for x, y in v.items() if x != "s"} if isinstance(v, dict) else v) for k, v in c.items()} for c in d["cards"]]) for d in made]
    e, look = html.escape, trainer_look(folder)
    data, forms = trainer_data(folder)
    W, (caption, before, after) = look["words"][lang], CARD_WORDS[lang]
    every, front, back = sides(lang, forms.get("langs") or [])
    titles = {t["id"]: t["title"] for t in data["texts"]}
    first = made[0]
    css = font + CARD_CSS.replace("@@LIGHT@@", look["light"]).replace("@@DARK@@", look["dark"]).replace("@@WIDTH@@", f"(max-width:{look['narrow']}px)")
    chips = "".join(f'<button type="button" data-l="{L}" aria-pressed="{"true" if L in front else "false"}">{L.upper()}</button>' for L in every)
    section = (f'<section class="day" aria-label="{e(caption)}">\n'
               f'<p class="cap"><b class="needs-js">{e(caption)}</b><span class="needs-js" id="fecha"></span><span id="obra">{tipo(titles.get(first["t"], ""))}</span></p>\n'
               '<div class="card">\n'
               f'<div class="chead"><span class="where" id="donde">{e(first["t"])} · § {first["p"]}</span><span class="seg needs-js" id="cara"><button type="button" data-c="front" aria-pressed="true">{e(W["front"])}</button>'
               f'<button type="button" data-c="back" aria-pressed="false">{e(W["back"])}</button></span><span class="chips needs-js" id="lados">{chips}</span></div>\n'
               f'<div id="ficha">{card_html(first, 0, look, lang, every, front, back)}</div>\n'
               f'<div class="opts needs-js"><span class="seg" id="modo"><button type="button" data-m="recog" aria-pressed="true">{e(W["recog"])}</button><button type="button" data-m="cloze" aria-pressed="false">{e(W["cloze"])}</button></span>'
               f'<button type="button" id="mix" aria-pressed="false">{e(W["shuffle"])}</button></div>\n'
               f'<div class="bar"><span class="steps needs-js"><button type="button" id="antes" aria-label="{e(before)}">‹</button><span id="cuenta"></span><button type="button" id="luego" aria-label="{e(after)}">›</button></span>'
               f'<a class="go" id="ir" href="{e(trainer_address(at, lang, front, back, first["t"], first["p"]))}">{e(STR[lang]["study"])}</a></div>\n'
               '</div>\n'
               f'<p class="legend"><span class="mk">◇</span>{e(W["unchecked"])}</p>\n</section>\n')
    block = {"days": made, "all": every, "front": front, "back": back, "note": W["unchecked"], "tiers": W["tiers"], "titles": {t: titles.get(t, "") for t in sorted({d["t"] for d in made})},
             "trainer": at + TRAINER}
    text = json.dumps(block, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return css, section, f'<script type="application/json" id="dias">{text}</script>\n<script>{CARD_SCRIPT}</script>\n'


_SETTLED: dict = {}


def settled(folder: Path) -> list[dict]:
    """The days as every page of the folder carries them, and a page set above it: all of them where the folder's largest main page
    stands within its budget with them; else the largest equal share of each lectura with which it does. No day where the
    folder has no trainer."""
    f = folder / TRAINER
    if not f.is_file(): return []
    key = (str(f), f.stat().st_mtime_ns, f.stat().st_size)
    if key not in _SETTLED:
        heavy = lambda made: max(len(page(folder, l, made=made).encode("utf-8")) for l in LANGS)
        made = days(folder); k = max((sum(1 for d in made if d["t"] == t) for t in {d["t"] for d in made}), default=0)
        while made and heavy(made) > PAGE_BUDGET and k > 0:
            k -= 1; made = days(folder, each=k)
        _SETTLED.clear(); _SETTLED[key] = made
    return _SETTLED[key]


def page(folder: Path, lang: str = "es", at: str = "", host: dict | None = None, made: list | None = None) -> str:
    """The main page in one language. `folder`: the folder it is written from. `at`: where the folder stands from the page —
    nothing for the folder's own page, the folder's name and a slash for a page above it. `host`: what a host adds to its own
    page — `head` (lines of the head, before the style), `script` (after the style), `addresses` (under how the folder is
    replicated), `after` (after the folder's sections), `links` (more links at the foot, each an address and its words), `share` (at
    the head's line, after the languages) and `beside` (beside the name and the sentence). `made`: the
    days of the cards of the day, where they are not those settled for the folder."""
    T, h = STR[lang], host or {}
    card_css, card, card_end = card_parts(folder, settled(folder) if made is None else made, lang, at)
    man = json.loads((folder / MANIFEST).read_text(encoding="utf-8"))
    gov = folder / man["governing"]
    lecturas = [l for l in man["lecturas"] if l.get("status") == "publicada"]
    P = []
    P.append(f"<!DOCTYPE html>\n<html lang=\"{lang}\">\n<head>\n<meta charset=\"utf-8\">\n"
             "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
             f"<title>{tipo(SITE_TITLE)}</title>\n{h.get('head', '')}<style>{CSS}{NAV_CSS}{head_css(folder)}{card_css}</style>\n{h.get('script', '')}</head>\n<body>\n")
    others = [(page_name(l), LANG_NAMES[l], l) for l in LANGS if l != lang]
    # at the head, the line and, at its other end, the page's other languages; the project is the one <h1>
    P.append(f"<div class=\"top\">{nav(lang, 'main', at)}<p class=\"lang\">"
             + " · ".join(f"<a href=\"{n}\" lang=\"{l}\" hreflang=\"{l}\">{w}</a>" for n, w, l in others) + "</p>" + h.get("share", "") + "</div>\n")
    mark = '<span class="mark" aria-hidden="true"></span>' if (folder / MARK).is_file() else ""
    P.append(f'<div class="head"><div class="say"><div class="name">{mark}<h1>{tipo(MASTHEAD)}</h1></div>\n<p>{T["project"]}</p></div>{h.get("beside", "")}</div>\n')
    P.append(card)                                         # the cards of the day: what the collection is, shown before it is listed

    # The trainer first: it is the tool; the texts are its corpus.
    P.append(f"<h2>{T['study']}</h2>\n")
    P.append(f"<p>{T['study_lead']}</p>\n"
             f"<p><a href=\"{at}{TRAINER}{'' if lang == 'es' else '#' + lang}\"><b>Léxico · {tipo(man['project'])}</b></a></p>\n<ul>\n"
             + "".join(f"<li>{item}</li>\n" for item in T["study_items"]) + "</ul>\n")

    P.append(f"<h2>{T['read']}</h2>\n")
    P.append(f"<h3 class=\"corpus\">{tipo(man['project'])}</h3>\n<p>{T['tagline']}</p>\n"
             f"<p class=\"mute\">{T['status_label']}{tipo(estado(gov))}</p>\n")
    P.append(f"<p>{T['texts_intro']}</p>\n<table>\n")
    L = T["links"]
    for l in lecturas:
        base = f"{at}{l['n']}-{l['slug']}-lectura"
        reg = f"{at}{l['register']}"
        words = int(l.get("words_est") or 0)
        meta = f"{tipo(l['author'])} · {l['date'][:4]}"
        if words:
            meta += f" · ≈ {words:,} {T['words']}".replace(",", "\u202f")
        meta += f" · {T['version']} {l['version']}"
        P.append(f"<tr><td class=\"n\">{l['n']}</td><td>{tipo(l['title'])}<br><span class=\"mute\">{meta}</span></td>"
                 f"<td class=\"l\"><a href=\"{at}{TRAINER}#{'' if lang == 'es' else lang + '/'}{l['n']}\">{L[4]}</a>"   # into the trainer on that lectura: the first of the row's links at every width
                 f"<a href=\"{base}.pdf\">{L[0]}</a><a href=\"{base}.epub\">{L[1]}</a>"
                 f"<a href=\"{base}.md\">{L[2]}</a><a href=\"{reg}\">{L[3]}</a></td></tr>\n")
    P.append("</table>\n")
    P.append(f"<p class=\"mute\">{T['read_note']}</p>\n")

    P.append(f"<h2>{T['docs']}</h2>\n<dl>\n")
    src_link = lambda md: f" <a href=\"{at}{md}\">{T['source_md']}</a>."
    epub_link = lambda stem: f" <a href=\"{at}{stem}.epub\">{T['links'][1]}</a>." if (folder / f"{stem}.epub").exists() else ""
    gov_stem = man["governing"][:-3]
    docs = [
        (gov_stem + ".pdf", T["d_gov"][0], T["d_gov"][1] + epub_link(gov_stem) + src_link(man["governing"])),
        (man["policy"].replace(".md", ".pdf"), T["d_pol"][0], T["d_pol"][1] + src_link(man["policy"])),
        *([(man["method"].replace(".md", ".pdf"), T["d_met"][0], T["d_met"][1] + src_link(man["method"]))] if man.get("method") else []),
        *[(f"{stem}.html", T[key][0], T[key][1] + f" <a href=\"{at}{stem}.epub\">{T['links'][1]}</a>." + src_link(f"{stem}.md"))
          for stem, key in PRIMER_DOCS],      # the primers: a page, an EPUB and the Markdown; no PDF of either
        ("PROVENANCE.md", *T["d_prov"]), ("README.md", *T["d_readme"]),
        ("MANIFEST.sha256", *T["d_man"]), ("LICENSE", *T["d_lic"]),
    ]
    for path, label, desc in docs:
        if path in RELEASED or (folder / path).exists():
            P.append(f"<dt><a href=\"{at}{path}\">{label}</a></dt><dd>{desc}</dd>\n")
    P.append("</dl>\n")

    # what is being made and what comes after, in a line; a page of the folder has the list
    P.append("<p>" + T["next_line"].format(a=f'<a href="{at}{NEXT_PAGE[lang]}">', z="</a>") + "</p>\n")

    # the folder is had whole and changed; a page of the folder says how
    P.append(f"<h2>{T['copy']}</h2>\n<p>{T['copy_text'].format(cid=FOLDER)} "
             f"<a href=\"{at}{COPY_PAGE[lang]}\">{T['copy_more']}</a>.</p>\n")
    P.append(f"<h2>{T['mirror']}</h2>\n<p>{T['mirror_text'].format(cid=FOLDER)}</p>\n")
    P.append(h.get("addresses", ""))
    P.append(h.get("after", ""))

    P.append(f"<footer>\n{nav(lang, 'main', at, foot=True)}\n<p>")      # the line again: the guide is in it
    links = [(f"{at}{man['policy'].replace('.md', '.pdf')}", T["f_policy"]),
             (f"{at}LICENSE", "CC0")] + list(h.get("links", []))
    P.append(" ".join(f"<a href=\"{p}\">{t}</a>" for p, t in links))
    P.append("</p>\n</footer>\n" + card_end + "</body>\n</html>\n")
    return "".join(P)


def main() -> int:
    for lang in LANGS:
        text = page(ROOT, lang)
        (ROOT / page_name(lang)).write_text(text, encoding="utf-8")
        print(f"Wrote {page_name(lang)} ({len(text):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
