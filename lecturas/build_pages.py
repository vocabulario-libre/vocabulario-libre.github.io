#!/usr/bin/env python3
"""build_pages.py — the folder's pages beside its index, in Spanish, English and Japanese: «Cómo usar», «Copiar y cambiar» and
«Próximos cambios».

    python build_pages.py

«Cómo usar»: what is here, how it is read, how the trainer is used, how it is checked. «Copiar y cambiar»: how the
folder is had, how it is changed, what its check checks. «Próximos cambios»: what is being made now and what comes after, as
a list. Plain HTML, no script, no external reference, relative links
only, as index.html: each page works in a folder opened from a disk, in a mirror, or under a path of a site. An
address outside the folder is text, not a link. Deterministic; line endings are written as they stand here on every
system.
"""
from __future__ import annotations
import html, json, sys
from pathlib import Path

sys.dont_write_bytecode = True      # another program of the folder is imported: no compiled Python is left in the folder
from build_index import NAV_CSS, NEXT_PAGE, nav, trainer_data

ROOT = Path(__file__).resolve().parent
m = json.loads((ROOT / "corpus.json").read_text(encoding="utf-8"))
N = sum(1 for r in m["lecturas"] if r.get("status") == "publicada" and r.get("release") != "excluded")
POLICY = m["policy"][:-3] + ".pdf"
EXAMPLE = min((r for r in m["lecturas"] if r.get("status") == "publicada" and r.get("release") != "excluded"),
              key=lambda r: int(r.get("words_est") or 0))        # the shortest edition: the example the pages name
REPO = "https://github.com/vocabulario-libre/vocabulario-libre.github.io"
ARCHIVE = REPO + "/archive/refs/heads/main.zip"
CLONE = "git clone -c core.autocrlf=false " + REPO
NAME = {"es": "copiar-y-cambiar.html", "en": "copiar-y-cambiar.en.html", "ja": "copiar-y-cambiar.ja.html"}
GUIDE_NAME = {"es": "como-usar.html", "en": "como-usar.en.html", "ja": "como-usar.ja.html"}
NEXT_NAME = NEXT_PAGE
LANG_NAMES = {"es": "Español", "en": "English", "ja": "日本語"}

CSS = """
:root { color-scheme: light dark; --fg: #222; --bg: #fdfcf8; --mute: #666; --line: #ddd; --link: #1a4d8f; --code: #efede8; }
@media (prefers-color-scheme: dark) { :root { --fg: #e8e6e0; --bg: #1c1b19; --mute: #9a978f; --line: #3a3835; --link: #8ab4f8; --code: #2a2926; } }
body { font-family: Georgia, 'Times New Roman', serif; color: var(--fg); background: var(--bg); max-width: 44em; margin: 2em auto; padding: 0 1em; line-height: 1.5; }
h1 { font-weight: normal; margin-bottom: .2em; }
h2 { font-size: 1.05em; font-weight: normal; letter-spacing: .05em; text-transform: uppercase; color: var(--mute); margin: 2.2em 0 .5em; border-bottom: 1px solid var(--line); padding-bottom: .2em; }
a { color: var(--link); } li { margin: .3em 0; }
code, pre { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .85em; background: var(--code); }
code { padding: 0 .25em; } pre { padding: .5em .7em; white-space: pre-wrap; overflow-wrap: anywhere; }
dl { margin: .4em 0; } dt { margin-top: .5em; } dd { margin: 0 0 0 1.2em; color: var(--mute); }
.lang { text-align: right; font-size: .9em; margin: 0; } .lang a { margin-left: .8em; }
footer { color: var(--mute); font-size: .9em; margin-top: 2.5em; border-top: 1px solid var(--line); padding-top: .8em; }
"""

PAGES = {
 "es": dict(title="Copiar y cambiar", body="""
<h1>Copiar y cambiar</h1>

<h2>La carpeta</h2>
<p>La obra entera es esta carpeta: {n} ediciones de lectura con sus fuentes, el entrenador de vocabulario con sus datos, los
documentos que las rigen y los programas que las construyen y las comprueban. <a href="README.md"><code>README.md</code></a>
lista los archivos (en inglés). El texto de los autores es de dominio público; todo lo añadido es CC0
(<a href="LICENSE"><code>LICENSE</code></a>): la carpeta se copia, se aloja y se cambia sin condición.</p>
<p>Lo que se está haciendo ahora y lo que viene después: <a href="{next}">Próximos cambios</a>.</p>

<h2>Cómo se obtiene</h2>
<p>Del sitio, archivo por archivo: la carpeta <code>lecturas/</code>. Entera, del repositorio de la réplica,
<code>{repo}</code>: como un solo archivo comprimido,</p>
<pre>{archive}</pre>
<p>o por clonación,</p>
<pre>{clone}</pre>
<p>La carpeta es <code>lecturas/</code> dentro de uno u otra. <code>-c core.autocrlf=false</code> conserva los archivos como se
publicaron; sin ella, git en Windows reescribe por defecto los finales de línea, y la comprobación da los archivos por
cambiados. Para verificar la carpeta: <code>sha256sum -c MANIFEST.sha256</code> dentro de ella, o
<code>python check_folder.py</code>.</p>

<h2>Cómo se cambia</h2>
<p>El archivo <code>.md</code> de una edición es su fuente; de él se generan su PDF y su EPUB. El entrenador se genera de las
ediciones y de los archivos de equivalencias y definiciones de cada una, <code>vocab/NN/</code>. <code>README.md</code> da las
órdenes; piden Python 3.9 o posterior, <code>reportlab</code> y <code>pyphen</code>. Tras un cambio: reconstruir y comprobar.</p>
<p>Para corregir una palabra en una edición —aquí, la lectura {ex}—:</p>
<ol>
<li>Editar su fuente, <code>{ed}</code>.</li>
<li>Reconstruir sus archivos: <code>python build_pdf.py {ex}</code> y después <code>python build_epub.py {ex}</code>.</li>
<li>Ejecutar <code>python check_folder.py</code>. Termina en <code>FOLDER CHECK PASS</code>.</li>
</ol>
<p>Para cambiar la equivalencia en inglés de una palabra:</p>
<ol>
<li>Editar el archivo de equivalencias de la edición, <code>vocab/{ex}/glosses.json</code>.</li>
<li>Reconstruir el entrenador: en <code>vocab/</code>, <code>python extract_vocab.py</code> y después
<code>python build_app.py</code>.</li>
<li>Reconstruir las páginas principales, que llevan fichas del entrenador: de vuelta en la carpeta, <code>python build_index.py</code>.</li>
<li>Ejecutar <code>python check_folder.py</code>, como arriba.</li>
</ol>
<p>La carpeta puede darse entera a un modelo de lenguaje: el archivo descomprimido, o el clon, y una instrucción que termine
en la comprobación. Tres instrucciones:</p>
<ul>
<li>«En la lectura {ex}, en las notas sobre las fuentes, sustituye esta palabra por esta otra. Reconstruye el PDF y el EPUB de
la edición. Ejecuta check_folder.py y da su última línea.»</li>
<li>«En vocab/{ex}/glosses.json, cambia la equivalencia de esta palabra por esta. Reconstruye el entrenador y después las páginas principales. Ejecuta
check_folder.py y da su última línea.»</li>
<li>«Ejecuta check_folder.py. Lista lo que ha cambiado en esta carpeta respecto de la distribución y lo que está
atrasado.»</li>
</ul>

<h2>Qué se comprueba</h2>
<p><code>check_folder.py</code> compara cada archivo con <a href="MANIFEST.sha256"><code>MANIFEST.sha256</code></a> y nombra lo
que ha cambiado respecto de la distribución. Genera de nuevo cada archivo que los programas de la carpeta construyen —los PDF
y los EPUB de las ediciones y de los documentos, el entrenador, las páginas principales y estas páginas— y nombra lo que está atrasado
respecto de su fuente. Las cartillas y la fuente tipográfica se comprueban sólo contra el manifiesto. Ejecuta las comprobaciones de cómputo y de
ortografía. Ejecuta <code>anon.py</code>, que nombra todo archivo que lleve el nombre o la dirección de una persona, o un rastro de la máquina en que se hizo: una ruta, un nombre de usuario, un huso horario. Su última línea es <code>FOLDER CHECK PASS</code>, o <code>FOLDER CHECK FAIL</code> y lo que falló.</p>
<p>No comprueba el resto de la norma. <code>compliance.py</code>, <code>drift.py</code> y <code>release.py</code> comprueban
las ediciones contra la <a href="{policy}">política</a>; necesitan los archivos de trabajo con que se hicieron las ediciones,
que no están en esta carpeta. Una edición nueva, o un cambio en un aparato, no se comprueba aquí contra la política.
<code>MANIFEST.sha256</code> y <a href="PROVENANCE.md"><code>PROVENANCE.md</code></a> describen la distribución, no una copia
cambiada.</p>
"""),
 "en": dict(title="Copy and change", body="""
<h1>Copy and change</h1>

<h2>The folder</h2>
<p>The whole work is this folder: {n} reading editions with their sources, the vocabulary trainer with its data, the
documents that govern them, and the programs that build and check them. <a href="README.md"><code>README.md</code></a> lists
the files. The authors’ texts are public domain; everything added is CC0 (<a href="LICENSE"><code>LICENSE</code></a>): the
folder is copied, hosted and changed without condition.</p>
<p>What is being made now and what comes after: <a href="{next}">Upcoming changes</a>.</p>

<h2>How it is had</h2>
<p>From the site, file by file: the folder <code>lecturas/</code>. Whole, from the repository of the mirror,
<code>{repo}</code>: as one archive,</p>
<pre>{archive}</pre>
<p>or by a clone,</p>
<pre>{clone}</pre>
<p>The folder is <code>lecturas/</code> inside either. <code>-c core.autocrlf=false</code> keeps the files as published;
without it, git on Windows rewrites line endings by default, and the check reports the files as changed. To verify the
folder: <code>sha256sum -c MANIFEST.sha256</code> inside it, or <code>python check_folder.py</code>.</p>

<h2>How it is changed</h2>
<p>The <code>.md</code> file of an edition is its source; its PDF and its EPUB are built from it. The trainer is built from the
editions and from the files of glosses and definitions of each, <code>vocab/NN/</code>. <code>README.md</code> gives the
commands; they need Python 3.9 or later, <code>reportlab</code> and <code>pyphen</code>. After a change: rebuild, then check.</p>
<p>To correct a word in an edition — here, edition {ex}:</p>
<ol>
<li>Edit its source, <code>{ed}</code>.</li>
<li>Rebuild its files: <code>python build_pdf.py {ex}</code>, then <code>python build_epub.py {ex}</code>.</li>
<li>Run <code>python check_folder.py</code>. It ends on <code>FOLDER CHECK PASS</code>.</li>
</ol>
<p>To change the English equivalent of a word:</p>
<ol>
<li>Edit the edition’s file of equivalents, <code>vocab/{ex}/glosses.json</code>.</li>
<li>Rebuild the trainer: in <code>vocab/</code>, <code>python extract_vocab.py</code>, then
<code>python build_app.py</code>.</li>
<li>Rebuild the main pages, which carry cards from the trainer: back in the folder, <code>python build_index.py</code>.</li>
<li>Run <code>python check_folder.py</code>, as above.</li>
</ol>
<p>The folder can be given whole to a language model: the archive unpacked, or the clone, and an instruction that ends at the
check. Three instructions:</p>
<ul>
<li>«In edition {ex}, in the notes on the sources, replace this word with this one. Rebuild the edition’s PDF and EPUB. Run
check_folder.py and give its last line.»</li>
<li>«In vocab/{ex}/glosses.json, change the gloss of this word to this. Rebuild the trainer, then the main pages. Run check_folder.py and give its
last line.»</li>
<li>«Run check_folder.py. List what has changed in this folder since the release and what is out of date.»</li>
</ul>

<h2>What is checked</h2>
<p><code>check_folder.py</code> compares every file with <a href="MANIFEST.sha256"><code>MANIFEST.sha256</code></a> and names
what has changed since the release. It rebuilds every file the folder’s programs build — the PDFs and EPUBs of the editions
and the documents, the trainer, the main pages and these pages — and names each that is out of date with its source. The primers
and the font are held to the manifest alone. It runs the checks of counts and of spelling. It runs <code>anon.py</code>, which names any file that carries a person’s name or address, or a trace of the machine it was made on: a path, a user’s name, a time zone. Its last line is <code>FOLDER CHECK PASS</code>, or <code>FOLDER CHECK FAIL</code> and what failed.</p>
<p>It does not check the rest of the standard. <code>compliance.py</code>, <code>drift.py</code> and <code>release.py</code>
check the editions against the <a href="{policy}">policy</a>; they need the working files the editions were made from, which
are not in this folder. A new edition, or a change to an apparatus, is not checked here against the policy. <code>MANIFEST.sha256</code> and <a href="PROVENANCE.md"><code>PROVENANCE.md</code></a> describe
the release, not a changed copy.</p>
"""),
 "ja": dict(title="複製と改変", body="""
<h1>複製と改変</h1>

<h2>フォルダ</h2>
<p>作品の全体がこのフォルダである：{n} の読解用校訂版とそのソース、語彙トレーナーとそのデータ、それらを規定する文書、
それらを生成し検査するプログラム。<a href="README.md"><code>README.md</code></a> がファイルを列挙する（英語）。著者の本文は
パブリックドメイン、加えたものはすべて CC0（<a href="LICENSE"><code>LICENSE</code></a>）：フォルダは無条件で複製し、
ホスティングし、改変できる。</p>
<p>現在作成中のものと、今後予定しているもの：<a href="{next}">今後の予定</a>。</p>

<h2>入手の仕方</h2>
<p>サイトからは、ファイルごとに：フォルダ <code>lecturas/</code>。丸ごとなら、ミラーのリポジトリ
<code>{repo}</code> から：一つのアーカイブとして、</p>
<pre>{archive}</pre>
<p>またはクローンで、</p>
<pre>{clone}</pre>
<p>どちらの場合も、フォルダはその中の <code>lecturas/</code> である。<code>-c core.autocrlf=false</code> はファイルを公開された
ままに保つ。これがないと、Windows の git は既定で改行を書き換え、検査はファイルを変更されたものとして示す。フォルダを
検証するには：その中で <code>sha256sum -c MANIFEST.sha256</code>、または <code>python check_folder.py</code>。</p>

<h2>変え方</h2>
<p>校訂版の <code>.md</code> ファイルがそのソースであり、PDF と EPUB はそこから生成する。トレーナーは、校訂版と、各校訂版の
訳語と定義のファイル <code>vocab/NN/</code> から生成する。コマンドは <code>README.md</code> にある。Python 3.9 以降、
<code>reportlab</code>、<code>pyphen</code> が要る。変更のあとは：再構築し、検査する。</p>
<p>校訂版の一語を直すには（ここでは校訂版 {ex}）：</p>
<ol>
<li>そのソース <code>{ed}</code> を編集する。</li>
<li>そのファイルを再構築する：<code>python build_pdf.py {ex}</code>、続いて <code>python build_epub.py {ex}</code>。</li>
<li><code>python check_folder.py</code> を実行する。<code>FOLDER CHECK PASS</code> で終わる。</li>
</ol>
<p>ある語の英語の訳語を変えるには：</p>
<ol>
<li>その校訂版の訳語ファイル <code>vocab/{ex}/glosses.json</code> を編集する。</li>
<li>トレーナーを再構築する：<code>vocab/</code> の中で <code>python extract_vocab.py</code>、続いて
<code>python build_app.py</code>。</li>
<li>トレーナーのカードを載せるトップページを再構築する：フォルダに戻って <code>python build_index.py</code>。</li>
<li>上と同じく <code>python check_folder.py</code> を実行する。</li>
</ol>
<p>フォルダは丸ごと言語モデルに渡せる：展開したアーカイブ、またはクローンと、検査で終わる指示を一つ。指示の例を三つ：</p>
<ul>
<li>「校訂版 {ex} の出典についての注記で、この語をこの語に置き換えてください。その校訂版の PDF と EPUB を再構築してください。
check_folder.py を実行し、最後の行を示してください。」</li>
<li>「vocab/{ex}/glosses.json で、この語の訳語をこれに変えてください。トレーナーを再構築し、続いてトップページを再構築してください。check_folder.py を
実行し、最後の行を示してください。」</li>
<li>「check_folder.py を実行してください。配布時からこのフォルダで変わったものと、再構築が要るものを列挙してください。」</li>
</ul>

<h2>検査されること</h2>
<p><code>check_folder.py</code> は各ファイルを <a href="MANIFEST.sha256"><code>MANIFEST.sha256</code></a> と照合し、配布時から
変わったものを示す。フォルダ内のプログラムが生成するすべてのファイル ― 校訂版と文書の PDF と EPUB、トレーナー、トップページ、
これらのページ ― を生成し直し、ソースに対して古くなったものを示す。手引きとフォントは目録との照合だけで検査する。語数と正書法の検査を実行する。<code>anon.py</code> を実行する。これは、人の名前やアドレス、あるいはファイルを作った機械の痕跡 ― パス、ユーザー名、タイムゾーン ― を含むファイルを示す。最後の行は <code>FOLDER CHECK PASS</code>、または
<code>FOLDER CHECK FAIL</code> と失敗した項目である。</p>
<p>基準の残りは検査しない。<code>compliance.py</code>、<code>drift.py</code>、<code>release.py</code> は校訂版を
<a href="{policy}">方針</a>に照らして検査する。校訂版を作るのに使った作業ファイルが要り、それはこのフォルダにない。
新しい校訂版や校訂注の変更は、ここでは方針に照らして検査されない。<code>MANIFEST.sha256</code> と
<a href="PROVENANCE.md"><code>PROVENANCE.md</code></a> は配布物を記述するものであり、変更した複製を記述するものではない。</p>
"""),
}


# «Cómo usar»: `back` names the link to the folder's index, which lists the texts.
GUIDE = {
 "es": dict(title="Cómo usar",
  body="""
<h1>Cómo usar</h1>

<h2>Qué hay</h2>
<p>Quince textos de Bolívar, San Martín y O’Higgins, 1812–1843, cada uno en una edición de lectura: el texto establecido y
su aparato. Un entrenador de vocabulario, Léxico, que lleva los quince textos dentro. Los documentos que permiten
comprobarlo todo: procedencia, política, método, manifiesto. El texto es de dominio público; lo demás, CC0. La colección
crece por corpus; hoy, uno, en español.</p>

<h2>Leer</h2>
<p>La página principal lista los quince textos en orden cronológico, con autor y fecha. Cada entrada abre el texto en su
edición. El aparato registra, caso por caso, lo que la edición cambió respecto del testimonio. El registro de procedencia
(<a href="PROVENANCE.md"><code>PROVENANCE.md</code></a>) nombra el testimonio de cada texto y sus derechos.</p>

<h2>Estudiar</h2>
<p><a href="vocab/flashcards.html">Léxico</a> abre en la vista «Texto». Clic en un párrafo: sus palabras forman las
fichas. Mayúsculas-clic: un tramo de párrafos. «Todo el texto»: el texto entero. Clic en una palabra: su equivalencia en
inglés, escrita para ese pasaje. La vista «Índice» ordena todas las formas por frecuencia, en unidades de cien;
«Estudiar esta unidad» forma el mazo.</p>
<p>Tres juegos de fichas: «palabras» (cada forma con la frase en que aparece y su equivalencia), «átomos» (las palabras
gramaticales: partícula, desinencia, rasgo, orden, ∅) y «tramos» (el átomo en el trecho de frase donde actúa). Sólo lo
certificado forma fichas; lo demás dice «en revisión».</p>
<p>Dos modos: «Reconocer» (se ve la palabra; se recuerda el sentido) y «Producir» (la frase con un hueco; se completa).
En pantalla ancha, «⇄ panel» pasa el texto al otro lado de las fichas; junto a la ficha se eligen los idiomas de cada cara, «anverso» y «reverso». Tres órdenes: «Orden del texto», «Barajadas», «Por repasar». La barra espaciadora
gira la ficha, y también un clic o un toque sobre ella; al repetirlo vuelve el anverso. Otra vez · Difícil · Bien · Fácil fija el próximo repaso.</p>
<p>Las fichas de una lectura cuyas formas están hechas —la lista de lecturas la marca con sus lenguas— llevan además la
palabra en japonés, ruso, alemán, sánscrito y avéstico: la forma, su lectura debajo y la forma de diccionario. El signo ◇
marca una forma escrita para este proyecto que todavía no ha revisado ninguna persona que lea la lengua: puede contener
errores. En las demás lecturas esas lenguas muestran «—».</p>
<p>El progreso queda en este navegador y en ningún otro sitio. «Guardar progreso» lo escribe en un archivo; «Cargar
progreso» lo lee; «Empezar de nuevo» lo borra. «Guardar selección» conserva un grupo de párrafos; «Enlace a esta
selección» produce una dirección que lo abre en cualquier aparato.</p>

<h2>Comprobar</h2>
<p><a href="MANIFEST.sha256"><code>MANIFEST.sha256</code></a> lista cada archivo con su huella;
<code>sha256sum -c MANIFEST.sha256</code> comprueba la distribución entera. <code>PROVENANCE.md</code> nombra testimonios y
derechos. La <a href="{policy}">política</a> fija las reglas; el método, cómo se aplicaron.
<a href="{page}">Copiar y cambiar</a> dice cómo se cambia la carpeta y cómo se comprueba el cambio.</p>

<h2>Términos</h2>
<dl>
<dt>edición</dt><dd>el texto establecido a partir de un testimonio, con su aparato</dd>
<dt>aparato</dt><dd>la lista de lo que la edición cambió respecto del testimonio, caso por caso</dd>
<dt>testimonio</dt><dd>la impresión o el manuscrito del que procede el texto</dd>
<dt>átomo</dt><dd>una palabra gramatical o una marca gramatical: partícula, desinencia, rasgo, orden, ∅</dd>
<dt>tramo</dt><dd>el trecho de frase en que un átomo actúa</dd>
<dt>certificado</dt><dd>un lugar cuyo sentido quedó comprobado; sólo éstos forman fichas</dd>
</dl>
"""),
 "en": dict(title="How to use",
  body="""
<h1>How to use</h1>

<h2>What is here</h2>
<p>Fifteen texts by Bolívar, San Martín and O’Higgins, 1812–1843, each in a reading edition: the established text and its
apparatus. A vocabulary trainer, Léxico, with the fifteen texts inside it. The documents that let all of it be checked:
provenance, policy, method, manifest. The text is public domain; everything else is CC0. The collection grows by corpus;
today, one, in Spanish.</p>

<h2>Read</h2>
<p>The main page lists the fifteen texts in chronological order, with author and date. Each entry opens the text in its
edition. The apparatus records, case by case, what the edition changed against the witness. The provenance record
(<a href="PROVENANCE.md"><code>PROVENANCE.md</code></a>) names each text’s witness and its rights.</p>

<h2>Study</h2>
<p><a href="vocab/flashcards.html#en">Léxico</a> opens in the “Text” view. Click a paragraph: its words form the cards.
Shift-click: a stretch of paragraphs. “Whole text”: the entire text. Click a word: its English gloss, written for that
passage. The “Index” view orders every form by frequency, in units of a hundred; “Study this unit” forms the deck.</p>
<p>Three card sets: “words” (each form with the sentence it occurs in and its gloss), “atoms” (the grammatical words:
particle, ending, feature, order, ∅) and “stretches” (the atom in the span of sentence where it acts). Only what is
certified forms cards; the rest says “under review”.</p>
<p>Two modes: “Recognise” (the word is shown; the sense is recalled) and “Produce” (the sentence with a gap; it is
supplied). On a wide screen, “⇄ pane” moves the text to the other side of the cards; beside the card the languages of each face are chosen, “front” and “back”. Three orders: “Text order”, “Shuffled”, “To review”. The space
bar turns the card, and so does a click or a tap on it; done again, it brings the front back. Again · Hard · Good · Easy sets the next review.</p>
<p>The cards of a lectura whose forms are made — the list of lecturas marks it with its languages — also carry the word in
Japanese, Russian, German, Sanskrit and Avestan: the form, its reading beneath, and the dictionary form. The mark ◇ stands
on a form written for this project that no person who reads the language has checked yet: it may be wrong. In the other
lecturas those languages show “—”.</p>
<p>Progress stays in this browser and nowhere else. “Save progress” writes it to a file; “Load progress” reads it; “Start
over” erases it. “Save selection” keeps a group of paragraphs; “Link to this selection” produces an address that opens it
on any device.</p>

<h2>Check</h2>
<p><a href="MANIFEST.sha256"><code>MANIFEST.sha256</code></a> lists every file with its digest;
<code>sha256sum -c MANIFEST.sha256</code> verifies the whole distribution. <code>PROVENANCE.md</code> names witnesses and
rights. The <a href="{policy}">policy</a> sets the rules; the method, how they were applied.
<a href="{page}">Copy and change</a> says how the folder is changed and how a change is checked.</p>

<h2>Terms</h2>
<dl>
<dt>edition</dt><dd>the text established from a witness, with its apparatus</dd>
<dt>apparatus</dt><dd>the list of what the edition changed against the witness, case by case</dd>
<dt>witness</dt><dd>the printing or manuscript the text comes from</dd>
<dt>atom</dt><dd>a grammatical word or a grammatical mark: particle, ending, feature, order, ∅</dd>
<dt>stretch</dt><dd>the span of sentence in which an atom acts</dd>
<dt>certified</dt><dd>a locus whose sense was verified; only these form cards</dd>
</dl>
"""),
 "ja": dict(title="使い方",
  body="""
<h1>使い方</h1>

<h2>何があるか</h2>
<p>ボリバル、サン・マルティン、オイギンスの十五の文書、1812–1843年。各文書は読むための校訂版：確定した本文とその校異。
語彙トレーナー Léxico は十五の文書を内蔵する。すべてを検証するための文書：出所、方針、方法、マニフェスト。本文はパブリックドメイン、
それ以外は CC0。収録は文書群ごとに増える。現在は一つ、スペイン語。</p>

<h2>読む</h2>
<p>トップページは十五の文書を年代順に、著者と年とともに並べる。各項目は校訂版の本文を開く。校異は、底本に対して校訂版が変えた箇所を
一つずつ記録する。出所記録（<a href="PROVENANCE.md"><code>PROVENANCE.md</code></a>）は各文書の底本と権利を示す。</p>

<h2>学ぶ</h2>
<p><a href="vocab/flashcards.html#ja">Léxico</a> は「本文」表示で開く。段落をクリック：その語がカードになる。Shift＋クリック：段落の範囲。
「全文を選択」：文書全体。語をクリック：その箇所のための英語の対応語。「索引」表示は全語形を頻度順に百語ずつ並べる。
「このユニットを学習」がデッキを作る。</p>
<p>三つのカード集：「語」（各語形と、その文と対応語）、「要素」（文法語：助詞、語尾、素性、語順、∅）、「区間」（要素が働く文の範囲）。
検証済みのものだけがカードになる。それ以外は「審査中」と表示する。</p>
<p>二つのモード：「認識」（語を見て、意味を思い出す）と「穴埋め」（空所のある文を補う）。広い画面では、「⇄ 左右」が本文をカードの反対側へ移す。カードのそばで、「表」と「裏」それぞれの言語を選ぶ。
三つの順序：「本文順」「シャッフル」「復習待ち」。スペースキー、またはカードのクリックやタップでカードを裏返す。同じ操作で表に戻る。もう一度・難しい・できた・簡単 が次の復習を決める。</p>
<p>語形が作成済みの講読（講読の一覧に言語名が付きます）のカードには、日本語・ロシア語・ドイツ語・サンスクリット語・
アヴェスター語の語形も載ります。語形、その下に読み、そして見出し語です。◇ は、このプロジェクトのために書かれ、
その言語を読める人による確認がまだ済んでいない語形に付きます。誤りを含むことがあります。それ以外の講読では、
これらの言語は「—」と表示されます。</p>
<p>進捗はこのブラウザにのみ残る。「進捗を保存」はファイルに書き出す。「進捗を読み込む」はそれを読む。「最初からやり直す」は消去する。
「選択を保存」は段落の組を保持する。「この選択へのリンク」はどの端末でもそれを開くアドレスを作る。</p>

<h2>確かめる</h2>
<p><a href="MANIFEST.sha256"><code>MANIFEST.sha256</code></a> は各ファイルとそのハッシュを列挙する。
<code>sha256sum -c MANIFEST.sha256</code> で配布物全体を検証できる。<code>PROVENANCE.md</code> は底本と権利を示す。
<a href="{policy}">方針</a>が規則を定め、方法がその適用を記す。
<a href="{page}">複製と改変</a>は、フォルダの変え方と変更の検査の仕方を記す。</p>

<h2>用語</h2>
<dl>
<dt>校訂版</dt><dd>底本から確定した本文と、その校異</dd>
<dt>校異</dt><dd>底本に対して校訂版が変えた箇所の一覧、一件ずつ</dd>
<dt>底本</dt><dd>本文の出所となる印刷物または写本</dd>
<dt>要素</dt><dd>文法語または文法標識：助詞、語尾、素性、語順、∅</dd>
<dt>区間</dt><dd>要素が働く文の範囲</dd>
<dt>検証済み</dt><dd>意味が確認された箇所。カードになるのはこれだけ</dd>
</dl>
"""),
}


# «Próximos cambios»: what is being made now and what comes after. By language: the title, the line under it, the two headings, and
# under each its items, an item with its sub-points. `{n}`: the lecturas whose cards are whole, by their own files; `{m}`: the
# lecturas published. An item that is made is taken off the list.
NEXT = {'es': {'title': 'Próximos cambios',
        'lead': 'Lo que se está haciendo ahora y lo que viene después. La obra es de dominio público: quien la copia puede continuarla.',
        'heads': ('Ahora', 'Después'),
        'now': [('Las fichas en cinco lenguas más, en las quince lecturas. Hechas: {n} de {m}.',
                 ['japonés', 'ruso', 'alemán', 'sánscrito', 'avéstico'])],
        'after': [('Índice de formas: se busca una palabra y se ve su forma de diccionario y cada lugar en que aparece.', []),
                  ('Cursos de estudio, del primer nivel al avanzado:', ['español', 'inglés', 'japonés']),
                  ('Griego:', ['una cartilla de griego', 'griego en las fichas']),
                  ('Hindi y chino en las fichas.', []),
                  ('Un panel de lógica en el entrenador:',
                   ['un curso de lógica, con problemas y soluciones',
                    'las frases de los textos en lógica formal, en cada una de sus lecturas; cuáles concuerdan con la ciencia moderna y entre sí; '
                    'qué se sigue de ellas',
                    'un problema de lógica cada día']),
                  ('Más obras en la biblioteca:',
                   ['Epicteto, «Golden Sayings» (griego e inglés)',
                    'Franklin, «Autobiography» (inglés)',
                    '«El arte de la guerra», las «Analectas» y el «Dao De Jing» (chino)',
                    'Platón (griego): «Apología», «Critón», «Fedón», «Fedro», «Protágoras», «Gorgias», «Teeteto»',
                    'el Avesta entero (avéstico)',
                    'piezas védicas del mismo periodo que cada parte del Avesta, puestas junto a ella (sánscrito y avéstico)',
                    'una obra budista. La primera elección es el «Abhidharmakośa». Su texto sánscrito se imprimió por primera vez en el siglo XX, '
                    'demasiado tarde para las reglas del proyecto; lo antiguo son sus traducciones china y tibetana. Qué obra incluir está por '
                    'decidir.'])]},
 'en': {'title': 'Upcoming changes',
        'lead': 'What is being made now and what comes after. The work is in the public domain: whoever copies it can carry it on.',
        'heads': ('Now', 'After that'),
        'now': [('The cards in five more languages, for all fifteen lecturas. Done: {n} of {m}.',
                 ['Japanese', 'Russian', 'German', 'Sanskrit', 'Avestan'])],
        'after': [('An index of forms: look up a word and see its dictionary form and every place it appears.', []),
                  ('Study courses, from the first level to advanced:', ['Spanish', 'English', 'Japanese']),
                  ('Greek:', ['a Greek primer', 'Greek on the cards']),
                  ('Hindi and Chinese on the cards.', []),
                  ('A logic pane in the trainer:',
                   ['a course in logic, with problems and solutions',
                    'the sentences of the texts in formal logic, in each of their readings; which readings agree with modern science and with one '
                    'another; what follows from them',
                    'a logic problem each day']),
                  ('More works in the library:',
                   ['Epictetus, «Golden Sayings» (Greek and English)',
                    'Franklin, «Autobiography» (English)',
                    'the «Art of War», the «Analects» and the «Dao De Jing» (Chinese)',
                    'Plato (Greek): the «Apology», «Crito», «Phaedo», «Phaedrus», «Protagoras», «Gorgias», «Theaetetus»',
                    'the whole Avesta (Avestan)',
                    'Vedic pieces from the same period as each part of the Avesta, set beside it (Sanskrit and Avestan)',
                    'a Buddhist work. The first choice is the «Abhidharmakośa». Its Sanskrit text was first printed in the twentieth century, too '
                    "recently for the project's rules; what is old are its Chinese and Tibetan translations. Which work to include is still to be "
                    'decided.'])]},
 'ja': {'title': '今後の予定',
        'lead': '現在作成中のものと、今後予定しているもの。本作品はパブリックドメインにあり、複製した人が続きを作ることができる。',
        'heads': ('現在', '今後'),
        'now': [('十五の講読すべてで、カードにさらに五言語。完成：{m} のうち {n}。', ['日本語', 'ロシア語', 'ドイツ語', 'サンスクリット', 'アヴェスター語'])],
        'after': [('語形索引：語を引くと、その辞書形と、すべての出現箇所がわかる。', []),
                  ('初級から上級までの学習課程：', ['スペイン語', '英語', '日本語']),
                  ('ギリシア語：', ['ギリシア語の手引き', 'カードのギリシア語']),
                  ('カードにヒンディー語と中国語。', []),
                  ('トレーナーに論理パネル：', ['問題と解答つきの論理学の課程', '本文の各文を、その解釈ごとに形式論理で表す。どの解釈が現代科学と、また互いに整合するか。そこから何が導かれるか', '毎日一問の論理の問題']),
                  ('ライブラリに作品を追加：',
                   ['エピクテトス「Golden Sayings」（ギリシア語と英語）',
                    'フランクリン「Autobiography」（英語）',
                    '『孫子』『論語』『老子道徳経』（中国語）',
                    'プラトン（ギリシア語）：『ソクラテスの弁明』『クリトン』『パイドン』『パイドロス』『プロタゴラス』『ゴルギアス』『テアイテトス』',
                    'アヴェスター全巻（アヴェスター語）',
                    'アヴェスターの各部分と同時代のヴェーダの諸篇を選び、その部分と並べる（サンスクリットとアヴェスター語）',
                    '仏教の一作品。第一候補は『阿毘達磨倶舎論』である。そのサンスクリット本文が初めて刊行されたのは二十世紀で、本プロジェクトの規則には新しすぎる。古くから伝わるのは漢訳とチベット語訳である。どの作品を収めるかは検討中。'])]}}


def whole(langs: list, asked: int, forms: dict) -> bool:
    """A lectura's cards are whole when its file of forms names every language of the cards and holds every stretch the lectura has."""
    return bool(langs) and set(forms.get("languages") or []) >= set(langs) and len(forms.get("stretches") or []) == asked


def made(folder: Path = ROOT) -> int:
    """The lecturas published whose cards are whole, read from the lecturas' own files: the languages are those of the trainer as
    built, the stretches a lectura has are those of `vocab/stretches.json`. A meaning changed does not change the count."""
    read = lambda p: json.loads(p.read_text(encoding="utf-8"))
    langs = list(trainer_data(folder)[1].get("langs") or [])
    asked: dict = {}
    for s in read(folder / "vocab" / "stretches.json")["stretches"]:
        asked[s["t"]] = asked.get(s["t"], 0) + 1
    files = [(r["n"], folder / r["vocab"] / "forms.json") for r in read(folder / "corpus.json")["lecturas"] if r.get("status") == "publicada" and r.get("release") != "excluded"]
    return sum(1 for t, f in files if f.is_file() and whole(langs, asked.get(t, 0), read(f)))


def next_body(lang: str) -> str:
    P, e = NEXT[lang], (lambda s: html.escape(s, quote=False))
    said = lambda s: e(s.replace("{n}", str(made())).replace("{m}", str(N)))
    out, k = [f"\n<h1>{e(P['title'])}</h1>\n<p>{e(P['lead'])}</p>\n"], 1
    for head, items in zip(P["heads"], (P["now"], P["after"])):
        out.append(f'\n<h2>{e(head)}</h2>\n<ol start="{k}">\n')
        for text, subs in items:
            under = "\n<ul>\n" + "".join(f"<li>{said(s)}</li>\n" for s in subs) + "</ul>\n" if subs else ""
            out.append(f"<li>{said(text)}{under}</li>\n")
        out.append("</ol>\n")
        k += len(items)
    return "".join(out)


def page(lang: str, guide: bool = False, coming: bool = False) -> str:
    P = NEXT[lang] if coming else (GUIDE if guide else PAGES)[lang]
    names = NEXT_NAME if coming else GUIDE_NAME if guide else NAME
    here = "guide" if guide else ""                  # the guide is one of the line's three; «Copiar y cambiar» is none
    e = html.escape
    if coming:
        body = next_body(lang)
    elif guide:
        body = P["body"].replace("{page}", e(NAME[lang])).replace("{policy}", e(POLICY))
    else:
        body = (P["body"].replace("{n}", str(N)).replace("{ex}", e(EXAMPLE["n"])).replace("{ed}", e(EXAMPLE["edition"]))
                .replace("{repo}", e(REPO)).replace("{archive}", e(ARCHIVE))
                .replace("{clone}", e(CLONE)).replace("{policy}", e(POLICY)).replace("{next}", e(NEXT_NAME[lang])))
    others = "".join(f'<a href="{names[l]}" lang="{l}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in names if l != lang)
    return (f'<!DOCTYPE html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{e(P['title'])} · {e(m['project'])}</title>\n<style>{CSS}{NAV_CSS}</style>\n</head>\n<body>\n"
            f'<div class="top">{nav(lang, here)}<p class="lang">{others}</p></div>\n{body}'
            f'<footer>\n{nav(lang, here, foot=True)}\n</footer>\n</body>\n</html>\n')


def main() -> None:
    for guide, coming, names in ((True, False, GUIDE_NAME), (False, False, NAME), (False, True, NEXT_NAME)):
        for lang, name in names.items():
            text = page(lang, guide, coming)
            with open(ROOT / name, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print(f"Wrote {name} ({len(text.encode('utf-8')):,} bytes)")


if __name__ == "__main__":
    main()
