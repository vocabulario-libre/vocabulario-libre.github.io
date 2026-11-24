#!/usr/bin/env python3
"""anon.py — the check that no file of a folder points to a person or a machine.

    python anon.py            # the folder this file is in
    python anon.py FOLDER     # another folder, or several

Four parts, each a line of the result:

  1. Fields. In every file, each field that can hold a person, a machine or a
     clock is read. It must be empty or a value of the lists below: the authors
     corpus.json names, the project's name, the tools that write the file, a
     day without an hour.
  2. Patterns. The text of every file — a PDF's pages and an EPUB's chapters
     included — is searched for an address, a path with a user's name, an IP
     address, an hour with its zone, a handle, an account of a service, a key,
     a record of who uploaded a file, a credit line. What is kept is written in
     EXCEPTIONS, each row with its reason.
  3. This machine. What the machine that runs the check says of itself — the
     user's name, the home directory, the host's name, the zone, git's user —
     is read at the run and sought in every file. Nothing of it is stored, and
     nothing of it is printed: a line names the kind of value and the file.
  4. Types. A file of a type the check does not read, or a file of such a type
     inside another, fails.

The last line is ANONYMITY CHECK PASS, or ANONYMITY CHECK FAIL. Exit status 0
on PASS. Nothing is written.

Standard library only. A PDF is read from its bytes as build_pdf.py writes it.
A .woff2 file is opened where the module `brotli` is installed; elsewhere its
table of contents is held to the .otf beside it, and the line says so. A PNG
is read part by part: what it says of itself is a field and is searched as
text; the hour of its last change, or a part the check does not know, fails.
"""
from __future__ import annotations
import base64, getpass, io, json, os, re, socket, struct, subprocess, sys, time, unicodedata, zipfile, zlib
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

# ================================================================== the lists (part 1)
PROJECT = ("Vocabulario Libre",)                               # the name a feed gives as its author
PDF_CREATOR = ("build_pdf.py",)
PDF_PRODUCER = ("ReportLab PDF Library - (opensource)", "ReportLab PDF Library - www.reportlab.com")   # reportlab 4 and 5; reportlab 3
PDF_DATE = ("D:20000101000000+00'00'",)                        # the fixed date of an invariant build: no clock
PDF_INFO_KEYS = {"Author", "CreationDate", "Creator", "Keywords", "ModDate", "Producer", "Subject", "Title", "Trapped"}
PDF_CATALOG_KEYS = {"Type", "Pages", "Outlines", "PageMode"}
NAMED_SYSTEM = ("Claude", "Anthropic")                         # the system the policy names (4.14)
DAY = r"\d{4}-\d\d-\d\dT00:00:00Z"                             # a day at midnight UTC: a date and no hour
OPF_DC = {"identifier", "title", "creator", "language", "rights", "description"}
OPF_META = {"dcterms:modified"}
NCX_META = {"dtb:uid"}
EPUB_INSIDE = {".xml", ".opf", ".ncx", ".xhtml", ".css", ".otf"}       # and the entry `mimetype`
ZIP_SYSTEMS = {0, 3}                                           # the entry's «made on»: 0 where Windows packed it, 3 where Unix did
HTML_META = {"viewport"}
HTML_LINK = {"stylesheet"}
SLOT = r"<!-- slot:[a-z]+ -->"                                 # the one comment a page carries: a slot's bare mark
FONT_TABLES = {"CFF ", "GPOS", "GSUB", "OS/2", "cmap", "head", "hhea", "hmtx", "maxp", "name", "post"}
FONT_NAME_IDS = {0, 1, 2, 4, 5, 6, 10, 13, 14}                 # no 8 (maker), 9 (designer), 11, 12 (their addresses), 7 (trademark)
FONT_VENDOR = ("????", "    ")
PNG_IMAGE = {"IHDR", "PLTE", "IDAT", "IEND", "tRNS"}           # the image and nothing said of it: no text, no time, no profile
PNG_TEXT = {"tEXt", "zTXt", "iTXt"}                            # what an image says of itself, each text under a keyword
PNG_SAID = {"Copyright": ("CC0 1.0 Universal",)}               # the keywords an image may carry, and the values of each: its dedication, by the licence's name
# A key of a data file that is of the kind below must be in JSON_KEYS, and its value of the shape given there.
META_KEY = re.compile(r"(?i)^(author|creator|generator|producer|user(name)?|host(name)?|path|file|e-?mail|created|"
                      r"modified|updated|date|time(stamp)?|built|version|machine|cwd|home)$")
JSON_KEYS = {
    "author": "AUTHORS",
    "date": r"(?s)(?!.*\d{1,2}:\d{2}).*",                    # a day in figures or in words, a place with it: no hour
    "version": r"\d+(\.\d+)*",
    "file": r"(?![/\\~]|[A-Za-z]:)[^\n]*",                     # a file named from the folder: no path from a drive or a home
}
PLAIN = {".md", ".py", ".tsv", ".txt", ".sha256", ".css", ".js"}       # read as text; no fields but an .md's
BARE = {"LICENSE"}                                             # files without a suffix that are read as text

# ================================================================== the patterns (part 2)
AT_RULE = (r"(?:media|font-face|import|page|supports|keyframes|charset|namespace|staticmethod|classmethod|property|"
           r"dataclass|functools|contextmanager|type|id|context|graph|value|language|vocab)")
ACCOUNTS = ("twitter.com", "x.com/", "mastodon", "facebook.com", "instagram", "linkedin", "youtube.com", "youtu.be", "reddit.com",
            "substack", "buttondown", "gmail", "protonmail", "proton.me", "outlook.com", "hotmail", "icloud", "google-analytics",
            "googletagmanager", "gtag(", "adsbygoogle", "doubleclick", "hotjar", "plausible.io", "cloudflareinsights",
            "google-site-verification")
# The zones' short names, after an hour: those of every continent, in the order of the alphabet.
ZONES = ("ACDT ACST ADT AEDT AEST AKDT AKST ART AST AWST BRT BST CAT CDT CEST CET CLT CST EAT EDT EEST EET EST GMT HKT HST IST JST "
         "KST MDT MSK MST NZDT NZST PDT PKT PST SAST SGT UTC WAT WEST WET")
# (the pattern's name, the pattern, what the text — in lower case — must hold for the pattern to be tried: one of these, or anything)
PATTERNS = [
    ("e-mail address", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), ("@",)),
    ("mailto", re.compile(r"(?i)mailto:"), ("mailto:",)),
    ("path with a user's name", re.compile(r"(?i)/Users/[^/\s\"'`]+|/home/[^/\s\"'`]+|[A-Z]:\\+Users\\+[^\\\s\"'`]+|/mnt/user-data|~/[\w.]"),
     ("/users/", "/home/", "\\users\\", "/mnt/user-data", "~/")),
    ("IP address", re.compile(r"(?<!\d)(?<!\d\.)(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?!\d|\.\d)"), ()),
    ("hour with a zone or an offset", re.compile(
        r"\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s?(?:[+-]\d{2}:?\d{2}\b|Z\b|(?:" + ZONES.replace(" ", "|") + r")\b)"
        r"|D:\d{8,14}[+-]\d\d'\d\d'?|(?i:time ?zone|huso horario|zona horaria|タイムゾーン|標準時|夏時間"
        r"|\b(?:standard|daylight|summer) time\b|\b(?:atlantic|central|eastern|european|greenwich|mountain|pacific) time\b"
        r"|\bhora (?:del atlántico|del centro|del este|de la montaña|del pacífico|central europea|peninsular)\b)"), ()),
    ("handle", re.compile(r"(?<![\w/.@-])@(?!" + AT_RULE + r"\b)[A-Za-z][\w-]{2,}"), ("@",)),
    ("account of a service", re.compile("(?i)" + "|".join((r"\b" if a == "x.com/" else "") + re.escape(a) for a in ACCOUNTS)), ACCOUNTS),
    ("key or token", re.compile(r"ghp_\w{20,}|github_pat_\w+|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|"
                                r"(?i:api[_-]?key\s*[:=]|password\s*[:=]|passwd|secret\s*[:=]|bearer\s+[a-z0-9._-]{20,})"),
     ("ghp_", "github_pat_", "sk-", "akia", "-----begin", "apikey", "api_key", "api-key", "password", "passwd", "secret", "bearer")),
    ("record of who uploaded a file", re.compile(r"(?i)uploaded by:? [^.;·]{2,40}|subido por [^.;·]{2,40}|[\w-]+ \(private account\)"),
     ("uploaded by", "subido por", "(private account)")),
    ("credit line", re.compile(r"(?i)__author__|__maintainer__|@author|maintained by|compiled by|compilado por|"
                               r"\bcontact(?:o)?\s*:|©|\(c\)\s*\d{4}|copyright\s+(?:\(c\)|©|\d{4})"),
     ("__author__", "__maintainer__", "@author", "maintained by", "compiled by", "compilado por", "contact", "©", "(c)", "copyright")),
]
# What is kept: (the file, the pattern — «*» for every pattern —, what the hit must be, the reason). A hit that no row covers fails.
# A file is named from the folder that holds corpus.json.
EXCEPTIONS = [
    (r"^anon\.py$", "*", r"(?s).*", "this program's own lists of what it looks for"),
    (r"^(README\.md|build_pages\.py|copiar-y-cambiar(\.en|\.ja)?\.html)$", "hour with a zone or an offset", r"(?i)time zone|huso horario|タイムゾーン",
     "the sentence that says what anon.py looks for"),
    (r"\.epub$", "hour with a zone or an offset", r"00:00:00Z",
     "the day an EPUB's package gives as its date: midnight UTC, as build_epub.py writes it"),
    (r"^releases\.xml$", "hour with a zone or an offset", r"00:00:00Z",
     "the days of the feed's entries: midnight UTC"),
    (r"^build_epub\.py$", "hour with a zone or an offset", r"00:00:00Z|timezone",
     "the program that writes that midnight, and the name `timezone` of Python's library"),
    (r"\.pdf$", "hour with a zone or an offset", r"D:20000101000000\+00'00'",
     "the fixed date build_pdf.py gives every PDF: the same for all, and no clock"),
]
SECRET = "key or token"


# ================================================================== reading: a PDF, from its bytes
PDFDOC = {0x18: "\u02d8", 0x19: "\u02c7", 0x1a: "\u02c6", 0x1b: "\u02d9", 0x1c: "\u02dd", 0x1d: "\u02db", 0x1e: "\u02da", 0x1f: "\u02dc",
          0x80: "\u2022", 0x81: "\u2020", 0x82: "\u2021", 0x83: "\u2026", 0x84: "\u2014", 0x85: "\u2013", 0x86: "\u0192", 0x87: "\u2044",
          0x88: "\u2039", 0x89: "\u203a", 0x8a: "\u2212", 0x8b: "\u2030", 0x8c: "\u201e", 0x8d: "\u201c", 0x8e: "\u201d", 0x8f: "\u2018",
          0x90: "\u2019", 0x91: "\u201a", 0x92: "\u2122", 0x93: "\ufb01", 0x94: "\ufb02", 0x95: "\u0141", 0x96: "\u0152", 0x97: "\u0160",
          0x98: "\u0178", 0x99: "\u017d", 0x9a: "\u0131", 0x9b: "\u0142", 0x9c: "\u0153", 0x9d: "\u0161", 0x9e: "\u017e", 0xa0: "\u20ac"}
ESC = {ord("n"): 10, ord("r"): 13, ord("t"): 9, ord("b"): 8, ord("f"): 12, ord("("): 40, ord(")"): 41, ord("\\"): 92}


def pdf_string(b: bytes, i: int) -> tuple[bytes, int]:
    """The literal string that opens at b[i] == «(»: its bytes, and the place after its «)»."""
    out, depth, i = bytearray(), 1, i + 1
    while i < len(b):
        c = b[i]
        if c == 92 and i + 1 < len(b):                         # a backslash
            d = b[i + 1]
            if d in ESC:
                out.append(ESC[d]); i += 2
            elif 48 <= d <= 55:
                j = i + 1
                while j < min(i + 4, len(b)) and 48 <= b[j] <= 55:
                    j += 1
                out.append(int(b[i + 1:j], 8) & 255); i = j
            elif d in (10, 13):
                i += 3 if b[i + 1:i + 3] == b"\r\n" else 2
            else:
                out.append(d); i += 2
            continue
        if c == 40:
            depth += 1
        elif c == 41:
            depth -= 1
            if not depth:
                return bytes(out), i + 1
        out.append(c); i += 1
    return bytes(out), i


def pdf_text_string(raw: bytes) -> str:
    if raw[:2] == b"\xfe\xff":
        return raw[2:].decode("utf-16-be", "replace")
    if raw[:3] == b"\xef\xbb\xbf":
        return raw[3:].decode("utf-8", "replace")
    return "".join(PDFDOC.get(c, chr(c)) for c in raw)


def pdf_dict(body: bytes) -> dict[str, str]:
    """The first dictionary of an object, one level: each key with its value as text (a string decoded, a name with its «/»)."""
    out, i = {}, body.find(b"<<") + 2
    if i < 2:
        return out
    while i < len(body):
        m = re.compile(rb"\s*").match(body, i); i = m.end()
        if body[i:i + 2] == b">>":
            break
        if body[i:i + 1] != b"/":
            i += 1; continue
        m = re.compile(rb"/([^\s/<>\[\]()]+)\s*").match(body, i)
        key, i = m.group(1).decode("latin-1"), m.end()
        if body[i:i + 1] == b"(":
            raw, i = pdf_string(body, i); out[key] = pdf_text_string(raw)
        elif body[i:i + 2] == b"<<":                           # a dictionary inside: stepped over
            depth, j = 0, i
            while j < len(body):
                if body[j:j + 2] == b"<<": depth += 1; j += 2
                elif body[j:j + 2] == b">>":
                    depth -= 1; j += 2
                    if not depth: break
                else: j += 1
            out[key] = "<<…>>"; i = j
        elif body[i:i + 1] == b"<":
            j = body.find(b">", i)
            try: out[key] = pdf_text_string(bytes.fromhex(body[i + 1:j].decode("ascii")))
            except ValueError: out[key] = body[i:j + 1].decode("latin-1")
            i = j + 1
        elif body[i:i + 1] == b"[":
            j = body.find(b"]", i); out[key] = body[i:j + 1].decode("latin-1"); i = j + 1
        else:
            m = re.compile(rb"(?:\d+ \d+ R|/?[^\s/<>\[\]()]+)").match(body, i)
            out[key] = m.group(0).decode("latin-1") if m else ""; i = m.end() if m else i + 1
    return out


PDF_SHOWN = re.compile(rb"\((?:[^()\\]|\\.|\((?:[^()\\]|\\.)*\))*\)|<[0-9A-Fa-f\s]+>|/([^\s/<>\[\]()]+)\s+[\d.]+\s+Tf\b"
                       rb"|(?<![^\s\])>])(?:T\*|ET|Td|TD|'|\")(?![^\s\[(<])", re.S)


def pdf_page_text(stream: bytes, signs: set[bytes] = frozenset()) -> str:
    """The strings a content stream shows, in its order; a move to another line is a line break. A string set in a font
    of signs (`signs`: Symbol, ZapfDingbats — a mark, not a letter) is given as U+FFFD, one for each sign."""
    out, sign = [], False
    for m in PDF_SHOWN.finditer(stream):
        tok = m.group(0)
        if tok[:1] == b"(":
            t = pdf_string(tok, 0)[0].decode("cp1252", "replace")
            out.append("\ufffd" * len(t) if sign else t)
        elif tok[:1] == b"<":
            try: t = bytes.fromhex(re.sub(rb"\s", b"", tok[1:-1]).decode("ascii")).decode("cp1252", "replace")
            except ValueError: continue
            out.append("\ufffd" * len(t) if sign else t)
        elif tok[:1] == b"/":
            sign = m.group(1) in signs
        else:
            out.append("\n")
    return "".join(out)


def read_pdf(data: bytes) -> dict:
    """{'info': the Info dictionary, 'catalog': the catalog's keys, 'text': the pages' text, 'streams': every stream decoded,
    'unread': [what could not be read]}"""
    r = {"info": {}, "catalog": set(), "text": "", "streams": [], "unread": [], "xmp": False, "annot_t": 0}
    if not data.startswith(b"%PDF-"):
        r["unread"].append("not a PDF"); return r
    if re.search(rb"/Type\s*/(ObjStm|XRef)\b", data) or b"/Encrypt" in data:
        r["unread"].append("a PDF with object streams or encryption: not as build_pdf.py writes it"); return r
    objs = {}
    for m in re.finditer(rb"(\d+) (\d+) obj\b(.*?)\bendobj", data, re.S):
        objs[int(m.group(1))] = m.group(3)
    pages = []
    signs = {m.group(1) for body in objs.values() if re.search(rb"/BaseFont\s*/(Symbol|ZapfDingbats)\b", body)
             for m in [re.search(rb"/Name\s*/([^\s/<>\[\]()]+)", body)] if m}
    for num, body in objs.items():
        at = re.search(rb"\bstream\r?\n", body)
        head = body[:at.start()] if at else body
        if re.search(rb"/Type\s*/Metadata\b|/Subtype\s*/XML\b", head):
            r["xmp"] = True
        if re.search(rb"/Type\s*/Catalog\b", head):
            r["catalog"] = set(pdf_dict(head))
            if b"/Metadata" in head: r["xmp"] = True
        if re.search(rb"/Subtype\s*/(Text|FreeText|Popup|Highlight|Underline|Ink|Stamp|FileAttachment)\b", head) or \
                (b"/Annot" in head and re.search(rb"/T\s*[(<]", head)):
            r["annot_t"] += 1
        if not at:
            continue
        raw = body[at.end():]
        end = raw.rfind(b"endstream")
        raw = raw[:end] if end >= 0 else raw
        try:
            for name in re.findall(rb"/(\w+Decode)\b", head):
                if name == b"ASCII85Decode":
                    raw = raw.strip()
                    raw = base64.a85decode(raw[:-2] if raw.endswith(b"~>") else raw)
                elif name == b"FlateDecode":
                    raw = zlib.decompress(raw.strip(b"\r\n") if not raw[:1].isalnum() else raw)
                else:
                    raise ValueError(name.decode())
        except Exception as e:
            r["unread"].append(f"a stream that was not opened ({e})"); continue
        r["streams"].append(raw)
        pages.append(pdf_page_text(raw, signs))
    r["text"] = "\n".join(pages)
    tail = data[data.rfind(b"trailer"):] if b"trailer" in data else b""
    m = re.search(rb"/Info\s+(\d+)\s+\d+\s+R", tail)
    if m and int(m.group(1)) in objs:
        r["info"] = pdf_dict(objs[int(m.group(1))])
    elif not tail:
        r["unread"].append("a PDF without a trailer: not as build_pdf.py writes it")
    return r


# ================================================================== reading: a font, from its bytes
WOFF2_TAGS = ("cmap head hhea hmtx maxp name OS/2 post cvt  fpgm glyf loca prep CFF  VORG EBDT EBLC gasp hdmx kern LTSH PCLT VDMX "
              "vhea vmtx BASE GDEF GPOS GSUB EBSC JSTF MATH CBDT CBLC COLR CPAL SVG  sbix acnt avar bdat bloc bsln cvar fdsc feat "
              "fmtx fvar gvar hsty just lcar mort morx opbd prop trak Zapf Silf Glat Gloc Feat Sill")
WOFF2_TAGS = [WOFF2_TAGS[i:i + 4] for i in range(0, len(WOFF2_TAGS), 5)]


def sfnt_tables(data: bytes) -> dict[str, bytes] | None:
    if data[:4] not in (b"OTTO", b"\x00\x01\x00\x00", b"true"):
        return None
    out = {}
    for i in range(struct.unpack(">H", data[4:6])[0]):
        tag, _, off, ln = struct.unpack(">4sIII", data[12 + 16 * i:28 + 16 * i])
        out[tag.decode("latin-1")] = data[off:off + ln]
    return out


def woff2_directory(data: bytes) -> tuple[list[tuple[str, int, int]], dict, int] | None:
    """A WOFF2 file's table of contents — (tag, the table's length, its length in the stream) — its header, and where the stream begins."""
    if data[:4] != b"wOF2" or len(data) < 48:
        return None
    keys = ("flavor", "length", "numTables", "reserved", "totalSfntSize", "totalCompressedSize", "major", "minor",
            "metaOffset", "metaLength", "metaOrigLength", "privOffset", "privLength")
    head = dict(zip(keys, struct.unpack(">IIHHIIHHIIIII", data[4:48])))
    i, tables = 48, []

    def base128(i):
        v = 0
        for _ in range(5):
            b = data[i]; i += 1
            v = (v << 7) | (b & 0x7f)
            if not b & 0x80:
                return v, i
        raise ValueError("a length that does not end")
    try:
        for _ in range(head["numTables"]):
            flags = data[i]; i += 1
            if flags & 0x3f == 63:
                tag = data[i:i + 4].decode("latin-1"); i += 4
            else:
                tag = WOFF2_TAGS[flags & 0x3f]
            version = flags >> 6
            orig, i = base128(i)
            packed = orig
            if (tag in ("glyf", "loca")) == (version == 0):
                packed, i = base128(i)
            tables.append((tag, orig, packed))
    except (IndexError, ValueError):
        return None
    return tables, head, i


def woff2_tables(data: bytes) -> tuple[dict[str, bytes] | None, list[tuple[str, int, int]] | None, dict]:
    """(the tables, where `brotli` is installed and the stream opens; the table of contents; the header)."""
    d = woff2_directory(data)
    if d is None:
        return None, None, {}
    tables, head, at = d
    try:
        import brotli
        stream = brotli.decompress(data[at:at + head["totalCompressedSize"]])
    except Exception:
        return None, tables, head
    out, i = {}, 0
    for tag, orig, packed in tables:
        out[tag] = stream[i:i + packed]; i += packed
    return out, tables, head


def cff_index(b: bytes, i: int) -> tuple[list[bytes], int]:
    count = struct.unpack(">H", b[i:i + 2])[0]
    if not count:
        return [], i + 2
    size = b[i + 2]
    offs = [int.from_bytes(b[i + 3 + k * size:i + 3 + (k + 1) * size], "big") for k in range(count + 1)]
    base = i + 3 + (count + 1) * size - 1
    return [b[base + offs[k]:base + offs[k + 1]] for k in range(count)], base + offs[-1]


def cff_operators(d: bytes) -> set[tuple]:
    ops, i = set(), 0
    while i < len(d):
        b0 = d[i]
        if b0 <= 21:
            if b0 == 12: ops.add((12, d[i + 1])); i += 2
            else: ops.add((b0,)); i += 1
        elif b0 == 28: i += 3
        elif b0 == 29: i += 5
        elif b0 == 30:
            i += 1
            while i < len(d) and (d[i] & 0x0f) != 0x0f and (d[i] >> 4) != 0x0f: i += 1
            i += 1
        elif b0 <= 246: i += 1
        else: i += 2
    return ops


def read_font(tables: dict[str, bytes]) -> tuple[list[str], list[str]]:
    """(what is wrong in the font's own fields, the strings it holds)."""
    faults, strings = [], []
    other = sorted(set(tables) - FONT_TABLES)
    if other:
        faults.append("a table the check does not read: " + ", ".join(repr(t) for t in other))
    try:
        nm = tables.get("name", b"")
        if nm:
            _, count, at = struct.unpack(">HHH", nm[:6])
            ids = set()
            for k in range(count):
                plat, enc, lang, nid, ln, off = struct.unpack(">HHHHHH", nm[6 + 12 * k:18 + 12 * k])
                raw = nm[at + off:at + off + ln]
                strings.append(raw.decode("mac_roman" if plat == 1 else "utf-16-be", "replace"))
                ids.add(nid)
            if ids - FONT_NAME_IDS:
                faults.append("a name record outside the list: " + ", ".join(str(n) for n in sorted(ids - FONT_NAME_IDS)))
        os2 = tables.get("OS/2", b"")
        if os2 and os2[58:62].decode("latin-1") not in FONT_VENDOR:
            faults.append("a vendor's mark in OS/2")
        hd = tables.get("head", b"")
        if hd:
            created, modified = struct.unpack(">qq", hd[20:36])
            if created % 86400 or modified % 86400:
                faults.append("an hour in the dates of `head`")
        cff = tables.get("CFF ", b"")
        if cff:
            names, i = cff_index(cff, cff[2])
            tops, i = cff_index(cff, i)
            strs, i = cff_index(cff, i)
            strings += [s.decode("latin-1") for s in names + strs]
            for top in tops:
                ops = cff_operators(top)
                if (1,) in ops or (12, 0) in ops:
                    faults.append("a notice or a copyright in the CFF table")
    except (struct.error, IndexError):
        faults.append("a table that could not be read")
    return faults, strings


# ================================================================== the files of a folder
def fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()


def alnum(s: str) -> str:
    return "".join(c for c in fold(s) if c.isalnum())


class Folder:
    def __init__(self, root: Path):
        self.root = root
        self.names = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() or p.is_symlink())
        self.authors: set[str] = set()
        self.has_manifest = False
        self.base = ""                   # where corpus.json stands, from the folder checked: «» or a folder's name with its «/»
        for n in self.names:
            if n.rsplit("/", 1)[-1] == "corpus.json":
                if not self.has_manifest or len(n) < len(self.base) + len("corpus.json"):
                    self.base = n[:-len("corpus.json")]
                try:
                    d = json.loads((root / n).read_text(encoding="utf-8"))
                    self.authors |= set(d.get("authors", {})) | {r.get("author", "") for r in d.get("lecturas", [])}
                    self.has_manifest = True
                except Exception:
                    pass
        self.authors.discard("")
        self.fields: list[str] = []      # part 1
        self.unread: list[str] = []      # part 4
        self.notes: list[str] = []
        self.pieces: list[tuple[str, str, str, bool]] = []    # (file, where in it, text, is text and not raw bytes)
        self.kinds: Counter = Counter()

    def is_author(self, v: str) -> bool:
        """An author corpus.json names, or several of them joined as the editions join them."""
        if v in self.authors:
            return True
        parts = [p for p in re.split(r" · | y ", v) if p]
        return bool(parts) and bool(self.authors) and all(
            any(re.search(r"(?<![^\W_])" + re.escape(p) + r"(?![^\W_])", a) for a in self.authors) for p in parts)

    def rel(self, name: str) -> str:
        """A file's name from the folder that holds corpus.json; a file outside that folder keeps its name."""
        return name[len(self.base):] if self.base and name.startswith(self.base) else name

    def bad(self, name: str, what: str) -> None:
        self.fields.append(f"{name}: {what}")

    def text(self, name: str, where: str, t: str) -> None:
        self.pieces.append((name, where, t, True))

    def raw(self, name: str, data: bytes) -> None:
        self.pieces.append((name, "", data.decode("latin-1"), False))

    # ---- each type's reader
    def read(self) -> None:
        for name in self.names:
            p = self.root / name
            base = name.rsplit("/", 1)[-1]
            suf = p.suffix.lower()
            self.text(name, "its name", name)
            if p.is_symlink():
                self.unread.append(f"{name}: a symbolic link"); continue
            if "__pycache__" in name.split("/") or suf in (".pyc", ".pyo"):
                self.unread.append(f"{name}: compiled Python, which holds the path it was compiled at: delete the folder `__pycache__`"); continue
            data = p.read_bytes()
            if suf == ".pdf": self.pdf(name, data)
            elif suf == ".epub": self.epub(name, data)
            elif suf == ".html": self.page(name, "", data.decode("utf-8", "replace"))
            elif suf == ".json": self.data_file(name, data.decode("utf-8", "replace"))
            elif suf == ".xml": self.xml(name, data.decode("utf-8", "replace"))
            elif suf in (".otf", ".woff2"): self.font(name, "", data)
            elif suf == ".png": self.png(name, "", data)
            elif suf in PLAIN or (not suf and base in BARE): self.plain(name, data.decode("utf-8", "replace"))
            else:
                self.unread.append(f"{name}: a type the check does not read"); continue
            self.kinds[suf or base] += 1

    def plain(self, name: str, t: str) -> None:
        self.text(name, "", t)
        if name.endswith(".md"):
            lines = t.split("\n")
            if lines and lines[0].strip() == "---" and any(l.strip() == "---" for l in lines[1:40]):
                self.bad(name, "front matter")
            if re.search(r"<!--.*?-->", t, re.S):
                self.bad(name, "a comment")

    def page(self, name: str, inner: str, t: str, in_epub: bool = False) -> None:
        self.text(name, inner, t)
        lab = name + (" › " + inner if inner else "")
        for m in re.finditer(r"<meta\b[^>]*>", t):
            tag = m.group(0)
            if re.search(r"\bcharset=", tag):
                continue
            nm = re.search(r"\b(?:name|property|http-equiv)=[\"']([^\"']*)", tag)
            if not nm or nm.group(1) not in HTML_META:
                self.bad(lab, f"a <meta> outside the list ({nm.group(1) if nm else 'unnamed'})")
        for m in re.finditer(r"<link\b[^>]*>", t):
            rel = re.search(r"\brel=[\"']([^\"']*)", m.group(0))
            if not rel or rel.group(1) not in HTML_LINK:
                self.bad(lab, f"a <link> outside the list ({rel.group(1) if rel else 'no rel'})")
        for m in re.finditer(r"<!--.*?-->", t, re.S):
            if in_epub or not re.fullmatch(SLOT, m.group(0)):
                self.bad(lab, "a comment that is not a slot's bare mark")
        if re.search(r"application/ld\+json|\bitemscope\b|\bitemprop=|rel=[\"']?(?:author|me)\b", t):
            self.bad(lab, "structured data, or a link that names an author")
        for m in re.finditer(r"data:([\w/+.-]*)((?:;[\w=-]+)*),([A-Za-z0-9+/=%._~-]*)", t):
            if ";base64" not in m.group(2):
                self.unread.append(f"{lab}: a file set inline ({m.group(1) or 'no type'}) that the check does not read"); continue
            try:
                payload = base64.b64decode(m.group(3))
            except Exception:
                payload = b""
            if payload[:4] in (b"wOF2", b"OTTO"):
                self.font(name, (inner + " › " if inner else "") + "the font set inline", payload)
            elif payload[:8] == b"\x89PNG\r\n\x1a\n":
                self.png(name, (inner + " › " if inner else "") + "the image set inline", payload)
            else:
                self.unread.append(f"{lab}: a file set inline ({m.group(1) or 'no type'}) that the check does not read")

    def data_file(self, name: str, t: str) -> None:
        self.text(name, "", t)
        try:
            d = json.loads(t)
        except Exception:
            self.unread.append(f"{name}: does not parse as JSON"); return
        seen = set()

        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if isinstance(k, str) and META_KEY.match(k) and not isinstance(v, (dict, list)):
                        rule = JSON_KEYS.get(k)
                        val = "" if v is None else str(v)
                        good = rule is not None and (not val or (self.is_author(val) if rule == "AUTHORS" else bool(re.fullmatch(rule, val))))
                        if not good and k not in seen:
                            seen.add(k)
                            self.bad(name, f"the key «{k}» " + ("outside the list" if rule is None else "with a value outside its list"))
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(d)

    def xml(self, name: str, t: str) -> None:
        self.text(name, "", t)
        if "<!--" in t:
            self.bad(name, "a comment")
        try:
            root = ET.fromstring(t)
        except ET.ParseError:
            self.unread.append(f"{name}: does not parse as XML"); return
        for el in root.iter():
            tag = el.tag.split("}")[-1]
            if tag in ("author", "contributor"):
                for ch in el:
                    ctag = ch.tag.split("}")[-1]
                    if ctag != "name" or (ch.text or "").strip() not in PROJECT:
                        self.bad(name, f"<{tag}> holds what is not the project's name (<{ctag}>)")
                if tag == "contributor" or (not len(el) and (el.text or "").strip() not in PROJECT + ("",)):
                    self.bad(name, f"a <{tag}> outside the list")
            elif tag in ("generator", "managingEditor", "webMaster"):
                self.bad(name, f"a <{tag}>")
            elif tag in ("updated", "published", "pubDate", "lastBuildDate"):
                if not re.fullmatch(DAY, (el.text or "").strip()):
                    self.bad(name, f"<{tag}> is not a day at midnight UTC")

    def pdf(self, name: str, data: bytes) -> None:
        self.raw(name, data)
        r = read_pdf(data)
        self.unread += [f"{name}: {u}" for u in r["unread"]]
        info = r["info"]
        self.text(name, "its fields", "\n".join(f"{k}: {v}" for k, v in sorted(info.items())))
        self.text(name, "its pages", r["text"])
        for s in r["streams"]:
            self.raw(name, s)
        for k in sorted(set(info) - PDF_INFO_KEYS):
            self.bad(name, f"the field «{k}» outside the list")
        if info.get("Author") and not self.is_author(info["Author"]):
            self.bad(name, "the author is no author corpus.json names")
        for k, allowed in (("Creator", PDF_CREATOR), ("Producer", PDF_PRODUCER), ("CreationDate", PDF_DATE), ("ModDate", PDF_DATE)):
            if info.get(k) and info[k] not in allowed:
                self.bad(name, f"«{k}» is outside its list")
        if info.get("Keywords"):
            self.bad(name, "keywords")
        src = (self.root / name).with_suffix(".md")
        words = alnum(src.read_text(encoding="utf-8", errors="replace")) if src.is_file() else None
        for k in ("Title", "Subject"):
            for part in (info.get(k) or "").split(" \u2014 "):
                if part.strip() and (words is None or alnum(part) not in words):
                    self.bad(name, f"«{k}» is not drawn from the Markdown beside it"); break
        if r["xmp"]:
            self.bad(name, "an XMP packet")
        if r["annot_t"]:
            self.bad(name, "an annotation that can carry a name")
        if r["catalog"] - PDF_CATALOG_KEYS:
            self.bad(name, "the catalog holds " + ", ".join(sorted(r["catalog"] - PDF_CATALOG_KEYS)))

    def epub(self, name: str, data: bytes) -> None:
        self.raw(name, data)
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile:
            self.unread.append(f"{name}: not a readable EPUB"); return
        with z:
            infos = z.infolist()
            if z.comment or any(i.comment for i in infos):
                self.bad(name, "a comment in the archive")
            if any(i.extra for i in infos):
                self.bad(name, "an extra field on an entry")
            if any(i.date_time[3:] != (0, 0, 0) for i in infos):
                self.bad(name, "an hour on an entry")
            if {i.create_system for i in infos} - ZIP_SYSTEMS:
                self.bad(name, "an entry packed on a system outside the list")
            for i in infos:
                inner, isuf = i.filename, Path(i.filename).suffix.lower()
                self.text(name, "the name of an entry", inner)
                if inner.endswith("/"):
                    continue
                body = z.read(i)
                if inner != "mimetype" and isuf not in EPUB_INSIDE:
                    self.unread.append(f"{name} › {inner}: a type the check does not read"); continue
                if isuf == ".otf":
                    self.font(name, inner, body); continue
                t = body.decode("utf-8", "replace")
                if isuf == ".xhtml":
                    self.page(name, inner, t, in_epub=True); continue
                self.text(name, inner, t)
                if re.search(r"<!--.*?-->|/\*.*?\*/", t, re.S):
                    self.bad(f"{name} › {inner}", "a comment")
                if isuf == ".opf":
                    self.opf(f"{name} › {inner}", t)
                elif isuf == ".ncx":
                    for m in re.finditer(r"<meta\b[^>]*\bname=[\"']([^\"']*)", t):
                        if m.group(1) not in NCX_META:
                            self.bad(f"{name} › {inner}", f"a <meta> outside the list ({m.group(1)})")
                    for m in re.finditer(r"<docAuthor>\s*<text>(.*?)</text>", t, re.S):
                        if not self.is_author(m.group(1).strip()):
                            self.bad(f"{name} › {inner}", "a <docAuthor> that is no author corpus.json names")

    def opf(self, lab: str, t: str) -> None:
        try:
            root = ET.fromstring(t)
        except ET.ParseError:
            self.unread.append(f"{lab}: does not parse as XML"); return
        for el in root.iter():
            ns, _, tag = el.tag.rpartition("}")
            val = (el.text or "").strip()
            if "purl.org/dc/elements" in ns:
                if tag not in OPF_DC:
                    self.bad(lab, f"<dc:{tag}> outside the list")
                elif tag == "creator" and not self.is_author(val):
                    self.bad(lab, "<dc:creator> is no author corpus.json names")
                elif tag == "identifier" and not re.fullmatch(r"urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", val):
                    self.bad(lab, "<dc:identifier> is not an identifier made from a name (a UUID of version 5)")
            elif tag == "meta":
                prop = el.attrib.get("property") or el.attrib.get("name") or ""
                if prop not in OPF_META:
                    self.bad(lab, f"a <meta> outside the list ({prop or 'unnamed'})")
                elif not re.fullmatch(DAY, val):
                    self.bad(lab, f"«{prop}» is not a day at midnight UTC")

    def png(self, name: str, inner: str, data: bytes) -> None:
        """A PNG, part by part. The image and how it is drawn hold no one. A text is a field: its keyword and its value must be of
        PNG_SAID, and the value is searched as any text is. The hour of the last change is a clock. Any other part is not read."""
        lab = name + (" › " + inner if inner else "")
        if not inner:
            self.raw(name, data)
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            self.unread.append(f"{lab}: not a readable PNG"); return
        i, kinds = 8, []
        while i + 12 <= len(data):
            n = struct.unpack(">I", data[i:i + 4])[0]
            kind, body = data[i + 4:i + 8].decode("latin-1"), data[i + 8:i + 8 + n]
            i += 12 + n
            kinds.append(kind)
            if kind in PNG_IMAGE:
                continue
            if kind == "tIME":
                self.bad(lab, "the hour of the image's last change"); continue
            if kind not in PNG_TEXT:
                self.unread.append(f"{lab}: a part of the image ({kind}) that the check does not read"); continue
            key, _, rest = body.partition(b"\x00")
            try:
                if kind == "zTXt":
                    value = zlib.decompress(rest[1:]).decode("latin-1")
                elif kind == "iTXt":
                    packed, rest = rest[:1] == b"\x01", rest[2:]
                    _, _, rest = rest.partition(b"\x00")          # the language's tag
                    _, _, rest = rest.partition(b"\x00")          # the keyword, translated
                    value = (zlib.decompress(rest) if packed else rest).decode("utf-8")
                else:
                    value = rest.decode("latin-1")
            except Exception:
                self.unread.append(f"{lab}: a text of the image that does not open"); continue
            word = key.decode("latin-1")
            self.text(name, (inner + " › " if inner else "") + f"the image's text «{word}»", value)
            if value not in PNG_SAID.get(word, ()):
                self.bad(lab, f"a text of the image outside the list ({word})")
        if i != len(data) or kinds[:1] != ["IHDR"] or kinds[-1:] != ["IEND"]:
            self.unread.append(f"{lab}: a PNG whose parts do not run from its head to its end")

    def font(self, name: str, inner: str, data: bytes) -> None:
        lab = name + (" › " + inner if inner else "")
        if not inner:
            self.raw(name, data)
        if data[:4] == b"wOF2":
            tables, toc, head = woff2_tables(data)
            if toc is None:
                self.unread.append(f"{lab}: not a readable WOFF2 file"); return
            if head.get("metaLength") or head.get("privLength") or head.get("metaOffset") or head.get("privOffset"):
                self.bad(lab, "a block of metadata or of private data")
            if tables is None:                                # no brotli here: the table of contents, held to an .otf of the folder
                twin = None
                for n in self.names:
                    if n.endswith(".otf"):
                        t = sfnt_tables((self.root / n).read_bytes())
                        if t and sorted((k, len(v)) for k, v in t.items()) == sorted((k, o) for k, o, _ in toc):
                            twin = n; break
                if twin:
                    self.notes.append(f"{lab}: not opened (the module `brotli` is not installed); its tables are those of {twin}, by name and length")
                else:
                    self.unread.append(f"{lab}: not opened (the module `brotli` is not installed), and no .otf of the folder has its tables")
                return
        else:
            tables = sfnt_tables(data)
            if tables is None:
                self.unread.append(f"{lab}: not a readable font"); return
        faults, strings = read_font(tables)
        for f in faults:
            self.bad(lab, f)
        self.text(name, (inner + " › " if inner else "") + "the font's strings", "\n".join(strings))
        if inner or data[:4] == b"wOF2":
            for v in tables.values():
                self.raw(name, v)


# ================================================================== part 2
def line_of(t: str, at: int) -> int:
    return t.count("\n", 0, at) + 1


_HITS: dict[str, list[tuple[str, int, str]]] = {}              # a text's hits, found once: the same file stands in more than one folder


def hits_of(t: str) -> list[tuple[str, int, str]]:
    got = _HITS.get(t)
    if got is None:
        low, got = t.lower(), []
        for label, rx, needs in PATTERNS:
            if needs and not any(n in low for n in needs):
                continue
            got += [(label, m.start(), m.group(0)) for m in rx.finditer(t)]
        _HITS[t] = got
    return got


def patterns(f: Folder) -> tuple[list[str], Counter]:
    faults, used = [], Counter()
    for name, where, t, is_text in f.pieces:
        if not is_text:
            continue
        rows = [(i, lab, re.compile(rx)) for i, (frx, lab, rx, _) in enumerate(EXCEPTIONS) if re.search(frx, f.rel(name))]
        hits, first = Counter(), {}
        for label, at, found in hits_of(t):
            row = next((i for i, lab, mrx in rows if lab in (label, "*") and mrx.fullmatch(found)), None)
            if row is not None:
                used[row] += 1; continue
            hits[label] += 1
            first.setdefault(label, (line_of(t, at), "" if label == SECRET else re.sub(r"\s+", " ", found)[:40]))
        for label, n in hits.items():
            ln, shown = first[label]
            faults.append(name + (f" › {where}" if where else f", line {ln}") + f": {label}" + (f" ×{n}" if n > 1 else "") + (f" «{shown}»" if shown else ""))
    return faults, used


# ================================================================== part 3
GENERIC = {"root", "/root", "localhost", "localhost.localdomain", "utc", "gmt", "etc/utc", "etc/gmt", "universal", "zulu", "z"}


def machine(folder: Path | None = None) -> list[tuple[str, str]]:
    """What this machine says of itself: (the kind of value, the value). Read here; stored nowhere."""
    out: list[tuple[str, str]] = []

    def add(kind: str, v) -> None:
        v = (v or "").strip() if isinstance(v, str) else ""
        if v:
            out.append((kind, v))
    try: add("the user's name", getpass.getuser())
    except Exception: pass
    home = os.path.expanduser("~")
    if home != "~":
        add("the home directory", home)
    for h in {socket.gethostname(), os.uname().nodename if hasattr(os, "uname") else ""}:
        add("the host's name", h)
        if "." in h: add("the host's name", h.split(".")[0])
    for k in ("USER", "LOGNAME", "USERNAME", "HOSTNAME", "COMPUTERNAME", "EMAIL"):
        add(f"the environment's {k}", os.environ.get(k))
    for k in ("user.name", "user.email"):
        try:
            r = subprocess.run(["git", "config", "--get", k], capture_output=True, text=True, timeout=20,
                               cwd=str(folder) if folder and folder.is_dir() else None)
            add(f"git's {k}", r.stdout)
        except Exception:
            pass
    for z in set(time.tzname) | {os.environ.get("TZ") or ""}:
        if not re.fullmatch(r"[+-]\d\d(?::?\d\d)?", z):       # a zone named by its offset alone is sought as an offset, below
            add("the zone's name", z.lstrip(":"))
    try: add("the zone's name", Path("/etc/timezone").read_text(encoding="utf-8"))
    except Exception: pass
    try:
        link = os.path.realpath("/etc/localtime")
        if "zoneinfo/" in link: add("the zone's name", link.split("zoneinfo/", 1)[1])
    except Exception:
        pass
    for secs in {-time.timezone} | ({-time.altzone} if time.daylight else set()):
        if not secs:
            continue
        sign, a = ("+" if secs > 0 else "-"), abs(secs)
        h, m = a // 3600, a % 3600 // 60
        forms = {f"UTC{sign}{h}", f"UTC{sign}{h:02d}", f"GMT{sign}{h}", f"GMT{sign}{h:02d}", f"UTC{sign}{h:02d}:{m:02d}", f"GMT{sign}{h:02d}:{m:02d}",
                 f"{sign}{h:02d}'{m:02d}"}
        for v in sorted(forms):
            add("the zone's offset", v)
    if folder is not None:
        parent = str(folder.resolve().parent)
        if len(Path(parent).parts) > 2:
            add("the path of the folder", parent)
    return out


def stands_in(v: str, low: str) -> int:
    """Where `v` stands in `low` outside a longer run of letters and digits, or -1. Both in lower case."""
    at = low.find(v)
    while at >= 0:
        before, after = low[at - 1:at] if at else "", low[at + len(v):at + len(v) + 1]
        if not (v[:1].isalnum() and before.isalnum()) and not (v[-1:].isalnum() and after.isalnum()):
            return at
        at = low.find(v, at + 1)
    return -1


def forms(v: str) -> set[str]:
    """A path is sought with either mark between its parts, and with the mark doubled as a data file writes it."""
    return {v, v.replace("\\", "/"), v.replace("/", "\\"), v.replace("\\", "\\\\"), v.replace("/", "\\\\")}


def this_machine(f: Folder, values: list[tuple[str, str]]) -> tuple[list[str], list[str], list[str]]:
    """(the faults, the kinds sought, the kinds set aside with the reason).

    A value is set aside — not sought — in four cases, and the line says which:
      - every system bears it (GENERIC);
      - a text of this size and with these letters holds it by chance: the number of places, times the frequency of each
        of its letters, is one or more;
      - it is a value of the lists above (an author, the project's name, a tool, the system the policy names);
      - the authors' texts hold it, as a word."""
    freq, n = Counter(), 0
    for _, _, t, is_text in f.pieces:
        if is_text:
            low = t.lower(); freq.update(low); n += len(low)
    reading = []
    for name in f.names:
        if re.search(r"(^|/)\d\d-[^/]*-lectura\.md$", name):
            t = (f.root / name).read_text(encoding="utf-8", errors="replace")
            m = re.search(r"^# Texto de lectura\s*$(.*?)(?=^# |\Z)", t, re.M | re.S)
            if m: reading.append(m.group(1))
    reading = fold("\n".join(reading))
    lists = fold("\n".join(sorted(f.authors) + list(PROJECT + PDF_CREATOR + PDF_PRODUCER + NAMED_SYSTEM)))
    merged: dict[str, list[str]] = {}
    for kind, v in values:
        kinds = merged.setdefault(v.lower(), [])
        if kind not in kinds:
            kinds.append(kind)
    sought, aside = {}, []
    for v, kinds in merged.items():
        kind = " and ".join(kinds)
        expected = float(n)
        for c in v:
            expected *= freq.get(c, 0) / n if n else 0
        if v in GENERIC:
            why = "a value every system bears"
        elif expected >= 1:
            why = "so short that a text of this size holds it by chance"
        elif stands_in(fold(v), lists) >= 0:
            why = "a value of the lists"
        elif stands_in(fold(v), reading) >= 0:
            why = "a word of the authors' texts"
        else:
            sought[v] = kind; continue
        if f"{kind} ({why})" not in aside:
            aside.append(f"{kind} ({why})")
    found = {}
    if sought:
        for name, where, t, is_text in f.pieces:
            low = t.lower()
            for v, kind in sought.items():
                at = max(stands_in(x, low) for x in forms(v))
                if at >= 0:
                    found.setdefault((name, kind), where or (f"line {line_of(t, at)}" if is_text else "its bytes"))
    faults = [f"{name} ({where}): holds {kind} of this machine" for (name, kind), where in sorted(found.items())]
    return faults, sorted(set(sought.values())), aside


# ================================================================== the check
TITLES = {
    1: "fields — each field that can hold a person, a machine or a clock is empty or a value of the lists",
    2: "patterns — no address, path, hour with its zone, handle, account, key, uploader or credit line but the written exceptions",
    3: "this machine — nothing it says of itself stands in a file",
    4: "types — every file, and every file inside a file, is of a type the check reads",
}


def check(folder: Path, values: list[tuple[str, str]] | None = None) -> dict:
    """The four parts on one folder. `values`, where given, stands in for what the machine says of itself."""
    f = Folder(Path(folder))
    f.read()
    p2, used = patterns(f)
    p3, sought, aside = this_machine(f, machine(f.root) if values is None else values)
    if not f.has_manifest:
        f.notes.append("no corpus.json here: no author is on the list, and an author's field that is not empty fails")
    idle = [EXCEPTIONS[i][0] for i in range(len(EXCEPTIONS)) if not used[i] and any(re.search(EXCEPTIONS[i][0], f.rel(n)) for n in f.names)]
    if idle:
        f.notes.append("an exception that covers nothing any more: " + "; ".join(idle))
    kinds = ", ".join(f"{n} {k}" for k, n in sorted(f.kinds.items()))
    detail = {
        1: f" ({len(f.names)} files: {kinds})",
        2: f" ({sum(used.values())} hits kept by {sum(1 for i in used if used[i])} of the {len(EXCEPTIONS)} exceptions)",
        3: f" (sought: {', '.join(sought) or 'nothing'}; set aside: {'; '.join(aside) or 'nothing'})",
        4: "",
    }
    parts = [(1, TITLES[1], f.fields, detail[1]), (2, TITLES[2], p2, detail[2]), (3, TITLES[3], p3, detail[3]), (4, TITLES[4], f.unread, detail[4])]
    return {"parts": parts, "notes": f.notes, "files": len(f.names)}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    folders = [Path(a).resolve() for a in sys.argv[1:]] or [Path(__file__).resolve().parent]
    failed = 0
    for folder in folders:
        print(f"Folder: {folder.name}")                        # its name, not its path: what is printed may be passed on
        if not folder.is_dir():
            print("  FAIL  not a folder"); failed += 1; continue
        rep = check(folder)
        for n, title, faults, detail in rep["parts"]:
            print(f"  {'FAIL' if faults else 'PASS'}  {n}. {title}{detail}")
            for x in faults[:40]:
                print(f"          {x}")
            if len(faults) > 40:
                print(f"          … and {len(faults) - 40} more")
            failed += bool(faults)
        for note in rep["notes"]:
            print(f"  NOTE  {note}")
    print("ANONYMITY CHECK " + ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
