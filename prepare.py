#!/usr/bin/env python3
"""BLACKOUT - bereitet die Notfall-SSD vor (einmalig, MIT Internet ausfuehren).

Beispiele:
  python3 prepare.py --target /mnt/ssd/BLACKOUT --profile small
  python3 prepare.py --target E:\\BLACKOUT --profile standard --platforms win-x64,linux-x64
  python3 prepare.py list-zim wikipedia          # verfuegbare ZIM-Dateien ansehen
  python3 prepare.py --target ... --only zim     # nur einen Teil (bin,models,zim,files,app)

Nur Python-Standardbibliothek. Abgebrochene Downloads werden fortgesetzt.
"""
import argparse, json, os, re, shutil, sys, tarfile, tempfile, time, zipfile
import urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "blackout-prepare/1.0"}
KIWIX = "https://download.kiwix.org"
RANK = {"small": 0, "standard": 1, "full": 2}
PLATFORMS = ["linux-x64", "linux-arm64", "win-x64", "mac-arm64", "mac-x64"]
PY_EMBED = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip"


# ---------------------------------------------------------------- http helpers
def req(url, headers=None, method="GET"):
    return urllib.request.Request(url, headers={**UA, **(headers or {})}, method=method)


def get_text(url, timeout=60):
    with urllib.request.urlopen(req(url), timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def head_size(url):
    try:
        with urllib.request.urlopen(req(url, method="HEAD"), timeout=30) as r:
            return int(r.headers.get("Content-Length") or 0)
    except Exception:
        return 0


def human(n):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or u == "TB":
            return f"{n:.1f} {u}" if u != "B" else f"{n} B"
        n /= 1024


def download(url, dest, expected=0, tries=8):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and (not expected or dest.stat().st_size == expected):
        print(f"  ok (vorhanden): {dest.name}")
        return True
    part = dest.with_name(dest.name + ".part")
    for attempt in range(1, tries + 1):
        have = part.stat().st_size if part.exists() else 0
        try:
            hdr = {"Range": f"bytes={have}-"} if have else {}
            with urllib.request.urlopen(req(url, hdr), timeout=60) as r:
                if have and r.status != 206:
                    have = 0  # Server ignoriert Range -> von vorn
                total = have + int(r.headers.get("Content-Length") or 0)
                mode = "ab" if have else "wb"
                t0, last = time.time(), 0
                with open(part, mode) as f:
                    while True:
                        chunk = r.read(1 << 20)
                        if not chunk:
                            break
                        f.write(chunk)
                        have += len(chunk)
                        if time.time() - last > 1:
                            last = time.time()
                            pct = f"{100 * have / total:5.1f}%" if total else ""
                            print(f"\r  {dest.name}: {human(have)} {pct}", end="", flush=True)
            print(f"\r  fertig: {dest.name} ({human(have)})        ")
            os.replace(part, dest)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 416 and part.exists():  # schon komplett
                os.replace(part, dest)
                return True
            print(f"\n  HTTP {e.code} bei {url}")
            if e.code in (401, 403, 404):
                return False
        except Exception as e:
            print(f"\n  Fehler ({e}), Versuch {attempt}/{tries}")
        time.sleep(min(5 * attempt, 30))
    return False


# ------------------------------------------------------------------- resolvers
def list_dir(url):
    return re.findall(r'href="([^"?/#][^"]*)"', get_text(url))


def resolve_zim(item):
    pat = re.compile(re.escape(item["prefix"]) + r"_(\d{4}-\d{2})\.zim")
    for d in item["dirs"]:
        try:
            names = [n for n in list_dir(f"{KIWIX}/zim/{d}/") if pat.fullmatch(n)]
        except Exception as e:
            print(f"  Verzeichnis {d} nicht lesbar: {e}")
            continue
        if names:
            return f"{KIWIX}/zim/{d}/{max(names)}", max(names)
    return None, None


def kiwix_plat(token):
    return {"linux-x86_64": "linux-x64", "linux-aarch64": "linux-arm64", "win-x86_64": "win-x64",
            "win-i686": "win-x64", "macos-arm64": "mac-arm64", "macos-x86_64": "mac-x64"}.get(token)


def resolve_kiwix_tools(plats):
    base = f"{KIWIX}/release/kiwix-tools/"
    best = {}
    for n in list_dir(base):
        m = re.fullmatch(r"kiwix-tools_([a-z0-9_-]+?)-(\d+(?:\.\d+)+)\.(?:tar\.gz|zip)", n)
        if not m:
            continue
        p = kiwix_plat(m.group(1))
        if p == "win-x64" and "win-i686" not in n and "win-x86_64" not in n:
            continue
        ver = tuple(map(int, m.group(2).split(".")))
        if p and (p not in best or ver > best[p][0]):
            best[p] = (ver, n)
    out = {}
    for p in plats:
        q = p if p in best else ("mac-x64" if p == "mac-arm64" and "mac-x64" in best else None)
        if q:
            out[p] = base + best[q][1]
    return out


def resolve_llama(plats):
    rel = json.loads(get_text("https://api.github.com/repos/ggml-org/llama.cpp/releases/latest"))
    assets = {a["name"]: a["browser_download_url"] for a in rel["assets"]}
    pats = {
        "linux-x64": [r"bin-ubuntu-x64\.(zip|tar\.gz)$"],
        "linux-arm64": [r"bin-ubuntu-arm64\.(zip|tar\.gz)$"],
        "win-x64": [r"bin-win-cpu-x64\.zip$", r"bin-win-avx2-x64\.zip$"],
        "mac-arm64": [r"bin-macos-arm64\.(zip|tar\.gz)$"],
        "mac-x64": [r"bin-macos-x64\.(zip|tar\.gz)$"],
    }
    out = {}
    for p in plats:
        for pat in pats[p]:
            hit = [n for n in assets if re.search(pat, n)]
            if hit:
                out[p] = assets[hit[0]]
                break
    return out


# ------------------------------------------------------------------ extraction
def extract(archive, outdir):
    if str(archive).endswith(".zip"):
        with zipfile.ZipFile(archive) as z:
            z.extractall(outdir)
    else:
        with tarfile.open(archive) as t:
            t.extractall(outdir)


def install_bin_archive(url, plat, target, must_contain, tmp):
    arc = Path(tmp) / url.rsplit("/", 1)[-1]
    if not download(url, arc):
        return False
    ex = Path(tmp) / (arc.name + ".x")
    extract(arc, ex)
    exe = [must_contain + ".exe", must_contain]
    hits = [p for p in ex.rglob("*") if p.name in exe]
    if not hits:
        print(f"  {must_contain} nicht im Archiv gefunden")
        return False
    dest = Path(target) / "bin" / plat
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(hits[0].parent, dest, dirs_exist_ok=True, symlinks=False)
    for p in dest.iterdir():
        if p.is_file() and not p.suffix.lower() in (".dll", ".txt", ".md"):
            p.chmod(p.stat().st_mode | 0o111)
    print(f"  installiert: bin/{plat}/{must_contain}")
    return True


# ------------------------------------------------------------------------ main
def select(items, profile):
    return [i for i in items if RANK[i["profile"]] <= RANK[profile]]


def copy_app(target):
    t = Path(target)
    for d in ("app", "bin", "models", "zim", "maps", "docs", "index"):
        (t / d).mkdir(parents=True, exist_ok=True)
    for f in (HERE / "app").iterdir():
        shutil.copy2(f, t / "app" / f.name)
    for f in ("start.sh", "start.bat", "ingest.sh", "ingest.bat", "README.md"):
        if (HERE / f).exists():
            shutil.copy2(HERE / f, t / f)
    (t / "start.sh").chmod(0o755)
    (t / "ingest.sh").chmod(0o755)
    docs_readme = HERE / "docs" / "README.txt"
    if docs_readme.exists():
        shutil.copy2(docs_readme, t / "docs" / "README.txt")
    print(f"App-Dateien kopiert nach {t}")


def write_tiers(target, models):
    ms = sorted(models, key=lambda m: -m["min_ram_gb"])
    (Path(target) / "models" / "tiers.txt").write_text(
        "".join(f"{m['min_ram_gb']} {m['file']}\n" for m in ms), encoding="utf-8")
    mid = [m for m in ms if m["min_ram_gb"] <= 10]
    default = (mid[0] if mid else ms[-1])["file"]
    (Path(target) / "models" / "default.txt").write_text(default + "\n", encoding="utf-8")


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "list-zim":
        d = sys.argv[2] if len(sys.argv) > 2 else "wikipedia"
        for n in list_dir(f"{KIWIX}/zim/{d}/"):
            if n.endswith(".zim"):
                print(n)
        return
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", required=True, help="Zielordner auf der SSD, z.B. /mnt/ssd/BLACKOUT")
    ap.add_argument("--profile", choices=list(RANK), default="small")
    ap.add_argument("--platforms", default="linux-x64,win-x64,mac-arm64",
                    help="Komma-Liste aus: " + ",".join(PLATFORMS))
    ap.add_argument("--only", default="app,bin,models,zim,files", help="Teilmenge")
    ap.add_argument("--catalog", default=str(HERE / "catalog.json"))
    ap.add_argument("--yes", action="store_true", help="ohne Rueckfrage starten")
    ap.add_argument("--no-python", action="store_true", help="kein portables Python fuer Windows laden")
    a = ap.parse_args()

    only = set(a.only.split(","))
    plats = [p for p in a.platforms.split(",") if p]
    bad = [p for p in plats if p not in PLATFORMS]
    if bad:
        sys.exit(f"Unbekannte Plattform(en): {bad}")
    cat = json.load(open(a.catalog, encoding="utf-8"))
    target = Path(a.target)
    target.mkdir(parents=True, exist_ok=True)

    plan = []  # (label, url, dest, size)
    print("Suche aktuelle Versionen ...")
    models = select(cat["models"], a.profile)
    if "models" in only:
        for m in models:
            url = f"https://huggingface.co/{m['repo']}/resolve/main/{m['file']}"
            plan.append((f"Modell {m['id']}", url, target / "models" / m["file"], head_size(url)))
    if "zim" in only:
        for z in select(cat["zim"], a.profile):
            url, name = resolve_zim(z)
            if not url:
                print(f"  ! nicht gefunden: {z['prefix']}" + (" (optional)" if z.get("optional") else ""))
                continue
            plan.append((f"ZIM {z['desc']}", url, target / "zim" / name, head_size(url)))
    if "files" in only:
        for f in select(cat.get("files", []), a.profile):
            plan.append((f["desc"], f["url"], target / f["dest"], head_size(f["url"])))
    tools = []  # (kind, plat, url)
    if "bin" in only:
        try:
            for p, u in resolve_kiwix_tools(plats).items():
                tools.append(("kiwix-serve", p, u))
        except Exception as e:
            print(f"  ! kiwix-tools: {e}")
        try:
            for p, u in resolve_llama(plats).items():
                tools.append(("llama-server", p, u))
        except Exception as e:
            print(f"  ! llama.cpp: {e}")
        if "win-x64" in plats and not a.no_python:
            tools.append(("python", "win-x64", PY_EMBED))
        for kind, p, u in tools:
            plan.append((f"{kind} ({p})", u, None, head_size(u)))

    total = sum(p[3] for p in plan)
    print(f"\n{'Was':58} {'Groesse':>10}")
    for label, url, dest, size in plan:
        print(f"{label[:58]:58} {human(size):>10}")
    free = shutil.disk_usage(target).free
    done = sum(p[3] for p in plan if p[2] and p[2].exists())
    print(f"\nGesamt: {human(total)} (davon schon vorhanden ~{human(done)}), frei auf Ziel: {human(free)}")
    if total - done > free:
        print("ACHTUNG: Speicherplatz reicht nicht - kleineres --profile waehlen oder catalog.json anpassen.")
    if not a.yes and input("Starten? [j/N] ").lower() not in ("j", "y", "ja", "yes"):
        return

    if "app" in only:
        copy_app(target)
        if models:
            write_tiers(target, models)
    failed = []
    for label, url, dest, size in plan:
        if dest is None:
            continue
        print(f"\n{label}")
        if not download(url, dest, size):
            failed.append(label)
    with tempfile.TemporaryDirectory() as tmp:
        for kind, p, u in tools:
            print(f"\n{kind} ({p})")
            if kind == "python":
                arc = Path(tmp) / "py.zip"
                if download(u, arc):
                    out = target / "bin" / p / "python"
                    out.mkdir(parents=True, exist_ok=True)
                    extract(arc, out)
                else:
                    failed.append("python")
            elif not install_bin_archive(u, p, target, kind, tmp):
                failed.append(f"{kind} {p}")
    print("\n=== Fertig ===" if not failed else "\n=== Fertig, aber mit Fehlern ===")
    for f in failed:
        print("  fehlgeschlagen:", f, "(Skript erneut ausfuehren setzt fort)")
    print(f"\nNaechste Schritte:\n  1. Eigene PDFs/Dokumente nach {target / 'docs'} legen\n"
          f"  2. Index bauen:  {target / 'ingest.sh'}   (Windows: ingest.bat)\n"
          f"  3. Starten:      {target / 'start.sh'}    (Windows: start.bat)")


if __name__ == "__main__":
    main()
