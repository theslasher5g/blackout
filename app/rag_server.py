#!/usr/bin/env python3
"""BLACKOUT Chat-Server: lokale KI (llama-server) + Offline-Wissen (Kiwix-ZIMs + eigene Dokumente).
Nur Standardbibliothek. Oeffnet eine Chat-Oberflaeche auf http://localhost:8000
"""
import html, json, mimetypes, os, re, sqlite3, sys, threading, time
import urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("BLACKOUT_ROOT", HERE.parent))
LLM = os.environ.get("LLM_URL", "http://127.0.0.1:8081").rstrip("/")
KIWIX = os.environ.get("KIWIX_URL", "http://127.0.0.1:8080").rstrip("/")
PORT = int(os.environ.get("UI_PORT", "8000"))
DB, DOCS = ROOT / "index" / "docs.sqlite", ROOT / "docs"
MAX_PAGES, PAGE_CHARS, DOC_HITS = 5, 1500, 6

SYSTEM = (
    "Du bist BLACKOUT, ein Offline-Notfallassistent ohne Internetzugang. "
    "Du bekommst nummerierte Quellen [1], [2], ... aus einer lokalen Wissensbasis. "
    "Stuetze dich vorrangig auf diese Quellen und nenne die Quellennummern. "
    "Reichen die Quellen nicht aus, sag das offen und gib nur gesicherte Allgemeinhinweise - erfinde nichts, "
    "besonders nicht bei Medizin, Strom, Gas, Chemie und Statik. Warne bei Lebensgefahr deutlich. "
    "Wenn moeglich und noetig: Notruf 112. Antworte knapp, als Schritt-fuer-Schritt-Anleitung, "
    "in der Sprache der Frage."
)


def http_get(url, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def strip_html(s):
    s = re.sub(r"(?is)<(script|style|nav|head).*?</\1>", " ", s)
    s = re.sub(r"(?i)</(p|div|li|h\d|tr|br)>|<br\s*/?>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\n\s*\n+", "\n", re.sub(r"[ \t\r\f]+", " ", s)).strip()


def terms(q):
    return [t.lower() for t in re.findall(r"\w{3,}", q)]


def best_window(text, qterms, size=PAGE_CHARS):
    paras = [p.strip() for p in text.split("\n") if len(p.strip()) > 40]
    if not paras:
        return text[:size]
    scored = sorted(range(len(paras)), key=lambda i: (-sum(paras[i].lower().count(t) for t in qterms), i))
    keep, used = [], 0
    for i in scored:
        if used + len(paras[i]) > size and keep:
            continue
        keep.append(i)
        used += len(paras[i])
        if used >= size:
            break
    return "\n".join(paras[i] for i in sorted(keep))[: size + 300]


# ------------------------------------------------------------------- Kiwix
_books = {"t": 0, "v": []}


def kiwix_books():
    if time.time() - _books["t"] < 60 and _books["v"]:
        return _books["v"]
    try:
        root = ET.fromstring(http_get(f"{KIWIX}/catalog/v2/entries?count=200", 5))
    except Exception:
        return _books["v"]
    out = []
    for e in root.iter():
        if e.tag.endswith("}entry") or e.tag == "entry":
            d = {c.tag.split("}")[-1]: (c.text or "") for c in e if c.tag.split("}")[-1] in ("name", "title", "language")}
            if d.get("name"):
                out.append(d)
    _books.update(t=time.time(), v=out)
    return out


def kiwix_search(book, q, n=2):
    base = f"{KIWIX}/search?content={urllib.parse.quote(book)}&pattern={urllib.parse.quote(q)}&pageLength={n}"
    res = []
    try:
        root = ET.fromstring(http_get(base + "&format=xml", 8))
        for it in root.iter("item"):
            link = urllib.parse.urlparse(it.findtext("link") or "").path
            if link:
                res.append((it.findtext("title") or link, link))
    except Exception:
        try:
            page = http_get(base, 8)
            for href, title in re.findall(r'<a href="(/content/[^"]+)"[^>]*>(.*?)</a>', page, re.S)[:n]:
                res.append((strip_html(title), html.unescape(href)))
        except Exception:
            pass
    return res[:n]


def kiwix_context(queries, qterms):
    books = kiwix_books()
    jobs = [(b, q) for q in queries for b in books]
    hits, seen = [], set()
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda j: (j[0], kiwix_search(j[0]["name"], j[1])), jobs))
    # Runde 1: je Buch/Anfrage erster Treffer, danach zweiter ...
    for rank in (0, 1):
        for b, res in results:
            if rank < len(res) and res[rank][1] not in seen:
                seen.add(res[rank][1])
                hits.append((b, *res[rank]))
    out = []
    for b, title, path in hits[: MAX_PAGES + 3]:
        try:
            text = strip_html(http_get(KIWIX + path, 8))
        except Exception:
            continue
        if len(text) < 80:
            continue
        out.append({"title": title, "source": b.get("title") or b["name"], "url": path,
                    "text": best_window(text, qterms), "kind": "kiwix"})
        if len(out) >= MAX_PAGES:
            break
    return out


# --------------------------------------------------------------- eigene Docs
def docs_search(queries, qterms):
    if not DB.exists():
        return []
    toks = sorted({t for q in queries for t in terms(q)})[:12]
    if not toks:
        return []
    match = " OR ".join(f'"{t}"*' if len(t) >= 4 else f'"{t}"' for t in toks)
    try:
        db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        rows = db.execute("SELECT path, ord, text FROM chunks WHERE chunks MATCH ? ORDER BY bm25(chunks) LIMIT ?",
                          (match, DOC_HITS)).fetchall()
    except sqlite3.Error:
        return []
    return [{"title": Path(p).name, "source": "Eigene Dokumente", "url": ("/view/" if p.lower().endswith((".md", ".txt")) else "/files/") + urllib.parse.quote(p),
             "text": t[:PAGE_CHARS], "kind": "doc"} for p, _, t in rows]


# --------------------------------------------------------------------- LLM
def llm_post(payload, timeout=300, stream=False):
    r = urllib.request.Request(f"{LLM}/v1/chat/completions", json.dumps(payload).encode(),
                               {"Content-Type": "application/json"})
    return urllib.request.urlopen(r, timeout=timeout)


def make_queries(question):
    prompt = ("Erzeuge 3 kurze Stichwort-Suchanfragen fuer eine Offline-Enzyklopaedie zu dieser Frage: "
              "eine auf Deutsch, zwei auf Englisch. Nur die 3 Zeilen, ohne Nummerierung.\n\nFrage: " + question)
    try:
        with llm_post({"messages": [{"role": "user", "content": prompt}], "max_tokens": 60,
                       "temperature": 0}, timeout=60) as r:
            txt = json.load(r)["choices"][0]["message"]["content"]
        qs = [re.sub(r"^[\s\-\*\d\.\)\"]+|[\"\s]+$", "", l) for l in txt.splitlines()]
        qs = [q for q in qs if 2 < len(q) < 120][:3]
    except Exception:
        qs = []
    return [question] + qs


def build_context(question):
    queries = make_queries(question)
    qterms = sorted({t for q in queries for t in terms(q)})
    with ThreadPoolExecutor(2) as ex:
        f1 = ex.submit(docs_search, queries, qterms)
        f2 = ex.submit(kiwix_context, queries, qterms)
        return f1.result() + f2.result()


# --------------------------------------------------------- Handbuch (ohne KI)
def md_inline(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", t)


def md_to_html(md):
    out, lst, code, tbl = [], None, False, False
    def close():
        nonlocal lst, tbl
        if lst: out.append(f"</{lst}>"); lst = None
        if tbl: out.append("</table>"); tbl = False
    for line in md.splitlines():
        if line.startswith("```"):
            close(); out.append("</pre>" if code else "<pre>"); code = not code; continue
        if code: out.append(html.escape(line)); continue
        m = re.match(r"(#{1,4})\s+(.*)", line)
        if m: close(); n = len(m.group(1)); out.append(f"<h{n}>{md_inline(m.group(2))}</h{n}>"); continue
        if line.startswith(">"): close(); out.append(f"<blockquote>{md_inline(line[1:].strip())}</blockquote>"); continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells): continue
            if not tbl: close(); out.append("<table>"); tbl = True; tag = "th"
            else: tag = "td"
            out.append("<tr>" + "".join(f"<{tag}>{md_inline(c)}</{tag}>" for c in cells) + "</tr>"); continue
        m = re.match(r"\s*([-*]|\d+\.)\s+(.*)", line)
        if m:
            kind = "ol" if m.group(1)[0].isdigit() else "ul"
            if lst != kind: close(); out.append(f"<{kind}>"); lst = kind
            out.append(f"<li>{md_inline(m.group(2))}</li>"); continue
        if not line.strip(): close(); continue
        close(); out.append(f"<p>{md_inline(line)}</p>")
    close()
    return "\n".join(out)


VIEW = ("<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
        "<title>{t}</title><style>body{{font:17px/1.6 system-ui,sans-serif;max-width:800px;margin:0 auto;padding:16px;"
        "background:#101214;color:#e8e6e1}}a{{color:#f0a030}}table{{border-collapse:collapse;width:100%;font-size:14px}}"
        "td,th{{border:1px solid #444;padding:4px 8px;text-align:left}}code,pre{{background:#1a1d21;padding:2px 5px;"
        "border-radius:4px}}pre{{padding:10px;overflow:auto}}blockquote{{border-left:3px solid #f0a030;margin:0;"
        "padding:4px 12px;background:#1a1d21}}@media(prefers-color-scheme:light){{body{{background:#f6f4ef;color:#1c1c1c}}"
        "code,pre,blockquote{{background:#eee}}}}</style><a href='/'>&larr; zurück</a>{b}")


def doc_list():
    if not DOCS.exists():
        return []
    return [p.relative_to(DOCS).as_posix() for p in sorted(DOCS.rglob("*"))
            if p.is_file() and not p.name.lower().startswith("readme.") and not p.name.startswith(".")]


# -------------------------------------------------------------------- HTTP
class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            return self.send(200, (HERE / "ui.html").read_bytes())
        if path == "/api/status":
            def ok(u):
                try:
                    http_get(u, 2)
                    return True
                except Exception:
                    return False
            n = 0
            if DB.exists():
                try:
                    n = sqlite3.connect(DB).execute("SELECT count(*) FROM chunks").fetchone()[0]
                except sqlite3.Error:
                    pass
            return self.send(200, json.dumps({"llm": ok(LLM + "/health"), "kiwix": ok(KIWIX),
                                              "books": [b.get("title") or b["name"] for b in kiwix_books()],
                                              "doc_chunks": n}), "application/json")
        if path == "/api/docs":
            return self.send(200, json.dumps(doc_list()), "application/json")
        if path == "/api/search":
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("q", [""])[0]
            hits = docs_search([q], terms(q))
            return self.send(200, json.dumps(hits), "application/json")
        if path.startswith("/view/"):
            p = (DOCS / urllib.parse.unquote(path[6:])).resolve()
            if DOCS.resolve() in p.parents and p.suffix.lower() in (".md", ".txt") and p.is_file():
                txt = p.read_text("utf-8", "replace")
                body = md_to_html(txt) if p.suffix.lower() == ".md" else "<pre>" + html.escape(txt) + "</pre>"
                return self.send(200, VIEW.format(t=html.escape(p.name), b=body))
        if path.startswith("/files/"):
            p = (DOCS / urllib.parse.unquote(path[7:])).resolve()
            if DOCS.resolve() in p.parents and p.is_file():
                return self.send(200, p.read_bytes(), mimetypes.guess_type(p.name)[0] or "application/octet-stream")
        self.send(404, "nicht gefunden", "text/plain; charset=utf-8")

    def emit(self, obj):
        self.wfile.write(b"data: " + json.dumps(obj).encode() + b"\n\n")
        self.wfile.flush()

    def do_POST(self):
        if self.path != "/api/chat":
            return self.send(404, "nicht gefunden", "text/plain")
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        msgs = [m for m in data.get("messages", []) if m.get("role") in ("user", "assistant")][-10:]
        if not msgs or msgs[-1]["role"] != "user":
            return self.send(400, "keine Frage", "text/plain")
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            question = msgs[-1]["content"]
            sources = build_context(question) if data.get("use_rag", True) else []
            self.emit({"sources": [{k: s[k] for k in ("title", "source", "url", "kind")} for s in sources]})
            if sources:
                ctx = "\n\n".join(f"[{i}] ({s['source']}: {s['title']})\n{s['text']}" for i, s in enumerate(sources, 1))
                msgs[-1] = {"role": "user", "content": f"QUELLEN:\n{ctx}\n\nFRAGE: {question}"}
            payload = {"messages": [{"role": "system", "content": SYSTEM}] + msgs, "stream": True, "temperature": 0.3}
            with llm_post(payload) as r:
                for line in r:
                    line = line.decode("utf-8", "replace").strip()
                    if not line.startswith("data:") or line.endswith("[DONE]"):
                        continue
                    try:
                        delta = json.loads(line[5:])["choices"][0]["delta"].get("content")
                    except (ValueError, KeyError, IndexError):
                        continue
                    if delta:
                        self.emit({"delta": delta})
            self.emit({"done": True})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            try:
                self.emit({"error": f"LLM nicht erreichbar oder Fehler: {e}"})
            except Exception:
                pass


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("0.0.0.0" if os.environ.get("UI_LAN") else "127.0.0.1", PORT), H)
    print(f"BLACKOUT Chat: http://localhost:{PORT}  (LLM {LLM}, Kiwix {KIWIX})")
    srv.serve_forever()
