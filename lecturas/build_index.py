#!/usr/bin/env python3
"""build_index.py — the release's front door: index.html, generated from corpus.json.

Plain HTML, no script, no external reference, relative links only (decision 61): it works as a folder opened from a
stick, as a mirror, or mounted at a path of a site. Lists every published lectura with its PDF, EPUB and source,
the trainer, the governing document, the policy, the provenance record and the manifest. Deterministic.
"""
from __future__ import annotations
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
m = json.loads((ROOT / "corpus.json").read_text(encoding="utf-8"))
e = html.escape
recs = [r for r in m["lecturas"] if r.get("status") == "publicada" and r.get("release") != "excluded"]
gov = m["governing"]; pol = m["policy"]; gov_stem = gov[:-3]; pol_stem = pol[:-3]
rows = []
for r in recs:
    stem = r["edition"][:-3]
    rows.append(f"<tr><td>{e(r['n'])}</td><td>{e(r['title'])}</td><td>{e(r['author'])}</td><td>{e(r['date'])}</td>"
                f"<td>v{e(str(r.get('version','')))}</td>"
                f"<td><a href=\"{e(stem)}.pdf\">PDF</a> · <a href=\"{e(stem)}.epub\">EPUB</a> · <a href=\"{e(r['edition'])}\">fuente</a> · <a href=\"{e(r['register'])}\">registro</a></td></tr>")
page = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(m['project'])}</title>
<style>
:root {{ color-scheme: light dark; --fg: #222; --bg: #fdfcf8; --mute: #666; --line: #ddd; --link: #1a4d8f; }}
@media (prefers-color-scheme: dark) {{ :root {{ --fg: #e8e6e0; --bg: #1c1b19; --mute: #9a978f; --line: #3a3835; --link: #8ab4f8; }} }}
body {{ font-family: Georgia, 'Times New Roman', serif; color: var(--fg); background: var(--bg); max-width: 60em; margin: 2em auto; padding: 0 1em; line-height: 1.5; }}
h1 {{ font-weight: normal; margin-bottom: .2em; }} .sub {{ color: var(--mute); margin-top: 0; }}
a {{ color: var(--link); }} table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th, td {{ text-align: left; vertical-align: top; padding: .35em .5em; border-bottom: 1px solid var(--line); }}
th {{ font-weight: normal; color: var(--mute); }} td:first-child {{ white-space: nowrap; }}
.tools a {{ margin-right: 1em; }} footer {{ color: var(--mute); font-size: .9em; margin-top: 2em; }}
</style>
</head>
<body>
<h1>{e(m['project'])}</h1>
<p class="sub">Ediciones de lectura de Bolívar, San Martín y O'Higgins para el estudio del español, con aparato crítico, notas graduadas y un entrenador de vocabulario. Los textos son de dominio público; todo lo añadido es CC0.</p>
<p class="tools"><a href="vocab/flashcards.html">Entrenador de vocabulario</a> <a href="{e(gov_stem)}.pdf">Documento rector (PDF)</a> <a href="{e(gov_stem)}.epub">(EPUB)</a> <a href="{e(pol_stem)}.pdf">Política</a> <a href="PROVENANCE.md">Procedencia</a> <a href="README.md">README</a></p>
<table>
<thead><tr><th>N.º</th><th>Lectura</th><th>Firmante</th><th>Fecha</th><th>Versión</th><th>Archivos</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>
<p>El entrenador es un solo archivo: funciona sin servidor ni conexión, desde una carpeta copiada, una memoria USB o el visor de Google Drive. El progreso se guarda en el navegador y puede exportarse e importarse.</p>
<footer>
<p>Para reproducir este sitio basta copiar la carpeta; para comprobarla, <code>sha256sum -c MANIFEST.sha256</code>; para modificarla, editar los archivos <code>.md</code> y ejecutar los programas incluidos (Python). Ningún archivo aquí carga nada de fuera. Véase <a href="README.md">README</a>.</p>
</footer>
</body>
</html>
"""
(ROOT / "index.html").write_text(page, encoding="utf-8")
print(f"Wrote index.html ({len(page):,} bytes; {len(recs)} lecturas)")
