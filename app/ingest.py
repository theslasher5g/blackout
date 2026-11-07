#!/usr/bin/env python3
"""Indexiert eigene Dokumente (docs/) in eine SQLite-Volltextsuche (FTS5).
Unterstuetzt: .txt .md .html .htm .epub .pdf (PDF: pdftotext oder 'pypdf', sonst uebersprungen).
Nur Standardbibliothek. Aufruf:  python3 app/ingest.py [--rebuild]
"""
import html, os, re, shutil, sqlite3, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(os.environ.get("BLACKOUT_ROOT", Path(__file__).resolve().parent.parent))
DOCS, DB = ROOT / "docs", ROOT / "index" / "docs.sqlite"
CHUNK, OVERLAP = 1100, 150


def strip_html(s):
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"[ \t\r\f]+", " ", html.unescape(s))


def read_pdf(p):
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True)
        return r.stdout.decode("utf-8", "replace")
    try:
        from pypdf import PdfReader
        return "\n\f".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
    except ImportError:
        return None


def read_epub(p):
    out = []
    with zipfile.ZipFile(p) as z:
        for n in sorted(z.namelist()):
            if n.lower().endswith((".xhtml", ".html", ".htm")):
                out.append(strip_html(z.read(n).decode("utf-8", "replace")))
    return "\n\n".join(out)


def read_any(p):
    ext = p.suffix.lower()
    if ext in (".txt", ".md", ".rst", ".csv"):
        return p.read_text("utf-8", "replace")
    if ext in (".html", ".htm"):
        return strip_html(p.read_text("utf-8", "replace"))
    if ext == ".epub":
        return read_epub(p)
    if ext == ".pdf":
        return read_pdf(p)
    return None


def chunks(text):
    paras = [re.sub(r"\s+", " ", x).strip() for x in re.split(r"\n\s*\n|\f", text)]
    buf = ""
    for para in filter(None, paras):
        while len(para) > CHUNK * 1.5:  # sehr lange Absaetze zerlegen
            cut = para.rfind(" ", 0, CHUNK)
            cut = cut if cut > 0 else CHUNK
            yield (buf + " " + para[:cut]).strip()
            buf, para = "", para[max(cut - OVERLAP, 0):]
        if len(buf) + len(para) > CHUNK and buf:
            yield buf
            buf = buf[-OVERLAP:] + " "
        buf = (buf + " " + para).strip()
    if buf:
        yield buf


def main():
    rebuild = "--rebuild" in sys.argv
    DB.parent.mkdir(parents=True, exist_ok=True)
    if rebuild and DB.exists():
        DB.unlink()
    db = sqlite3.connect(DB)
    try:
        db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(path UNINDEXED, ord UNINDEXED, text, "
                   "tokenize='unicode61 remove_diacritics 2')")
    except sqlite3.OperationalError as e:
        sys.exit(f"Dieses Python hat kein SQLite-FTS5 ({e}).")
    db.execute("CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, sig TEXT)")
    seen, added, skipped = set(), 0, []
    for p in sorted(DOCS.rglob("*")):
        if not p.is_file() or p.name.startswith(".") or p.name.lower().startswith("readme."):
            continue
        rel = p.relative_to(DOCS).as_posix()
        seen.add(rel)
        sig = f"{p.stat().st_size}:{int(p.stat().st_mtime)}"
        row = db.execute("SELECT sig FROM files WHERE path=?", (rel,)).fetchone()
        if row and row[0] == sig:
            continue
        try:
            text = read_any(p)
        except Exception as e:
            skipped.append(f"{rel} ({e})")
            continue
        if text is None:
            skipped.append(f"{rel} (Format/Tool fehlt)")
            continue
        db.execute("DELETE FROM chunks WHERE path=?", (rel,))
        n = 0
        for i, c in enumerate(chunks(text)):
            db.execute("INSERT INTO chunks(path, ord, text) VALUES (?,?,?)", (rel, i, c))
            n += 1
        db.execute("INSERT OR REPLACE INTO files VALUES (?,?)", (rel, sig))
        db.commit()
        added += 1
        print(f"  {rel}: {n} Abschnitte")
    for (gone,) in db.execute("SELECT path FROM files").fetchall():
        if gone not in seen:
            db.execute("DELETE FROM chunks WHERE path=?", (gone,))
            db.execute("DELETE FROM files WHERE path=?", (gone,))
    db.commit()
    total = db.execute("SELECT count(*) FROM chunks").fetchone()[0]
    print(f"Fertig: {added} neue/geaenderte Dateien, {total} Abschnitte im Index.")
    for s in skipped:
        print("  uebersprungen:", s)
    if any("pdf" in s.lower() for s in skipped):
        print("  Tipp: PDFs brauchen 'pdftotext' (poppler) oder 'pip install pypdf'.")


if __name__ == "__main__":
    main()
