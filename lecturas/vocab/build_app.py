#!/usr/bin/env python3
"""
build_app.py — Assemble the standalone flashcard app.

Injects vocab.json into app_template.html and writes flashcards.html: one file,
no server, no network, no dependencies. Open it from disk, from VS Code's Live
Preview, from a USB stick, or from Google Drive.

    python extract_vocab.py && python build_app.py

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MARKER = "/*__VOCAB_DATA__*/null"


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the standalone flashcard app.")
    ap.add_argument("--data", "-d", default="vocab.json")
    ap.add_argument("--template", "-t", default="app_template.html")
    ap.add_argument("--out", "-o", default="flashcards.html")
    args = ap.parse_args()

    for f in (args.data, args.template):
        if not Path(f).exists():
            sys.exit(f"Not found: {f}. Run extract_vocab.py first.")

    data = Path(args.data).read_text(encoding="utf-8")
    tpl = Path(args.template).read_text(encoding="utf-8")

    if MARKER not in tpl:
        sys.exit(f"Template is missing the data marker {MARKER!r}")

    # Guard against breaking out of the <script> element.
    safe = data.replace("</", "<\\/")
    html = tpl.replace(MARKER, safe)

    Path(args.out).write_text(html, encoding="utf-8")

    parsed = json.loads(data)
    s = parsed["stats"]
    kb = Path(args.out).stat().st_size / 1024
    print(f"Wrote {args.out} ({kb:,.0f} KB, self-contained)")
    print(f"  {s['forms']:,} word forms · {s['defined']} with a definition "
          f"· {len(parsed['sentences'])} sentences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
