# BLACKOUT – Offline-Notfall-SSD mit lokaler KI

Eine SSD, die **ohne Strom-Netz, Internet und Cloud** funktioniert: Offline-Wikipedia & Fachwissen,
eigene PDFs (Baupläne, Handbücher), Kartendaten – und eine lokale KI, die dieses Wissen durchsucht
und mit Quellenangaben antwortet.

```
BLACKOUT/
├─ start.sh / start.bat     Alles starten (Chat unter http://localhost:8000)
├─ ingest.sh / ingest.bat   Eigene Dokumente für die KI indexieren
├─ bin/<plattform>/         llama-server (KI), kiwix-serve (Bibliothek), Python (Windows)
├─ models/                  KI-Modelle (.gguf)
├─ zim/                     Offline-Wissen (Wikipedia, iFixit, StackExchange, ...)
├─ maps/                    Kartendaten
├─ docs/                    DEINE PDFs/Handbücher/Baupläne
└─ index/                   Suchindex der eigenen Dokumente
```

## 1. Vorbereiten (einmalig, mit Internet)

SSD als **exFAT** formatieren (Windows + macOS + Linux, Dateien > 4 GB). Dann auf einem normalen Rechner:

```bash
python3 prepare.py --target /pfad/zur/ssd/BLACKOUT --profile small
```

| Profil | Inhalt | Platz (grob) |
|---|---|---|
| `small` | KI 3B + 7B, dt. Wikipedia, Medizin, Elektronik, DIY, Outdoor, iFixit, Wasser/Erste Hilfe | ~60–80 GB |
| `standard` | + KI 14B, engl. Wikipedia, WikEM, Appropedia, Kfz, Funk, Garten, OSM Deutschland | ~200–250 GB |
| `full` | + Wikipedia mit Bildern (de/en), Kochen, Physik, OSM Europa/AT/CH | ~400–500 GB, passt auf 1 TB |

- Das Skript zeigt vorher alle Dateien mit **echter Größe** und fragt nach.
- Abbruch/Neustart ist unkritisch (Downloads werden fortgesetzt).
- Plattformen wählen: `--platforms linux-x64,win-x64,mac-arm64` (Standard).
- Alles Weitere steht in `catalog.json` (Wikipedia-Varianten, Modelle, Regionen) – frei editierbar.
- ZIM-Dateien ansehen: `python3 prepare.py list-zim wikipedia`

## 2. Eigenes Wissen hinzufügen

PDFs, EPUBs, TXT, MD, HTML nach `docs/` kopieren (Baupläne, Datenblätter, Handbücher deiner Geräte,
BBK-Notfallratgeber, Survival-Handbücher …), dann `ingest.sh` bzw. `ingest.bat`.
PDF-Text braucht `pdftotext` (poppler) oder `pip install pypdf` – **beim Vorbereiten, nicht im Notfall**.
Gescannte PDFs (nur Bilder) enthalten keinen Text und werden nicht gefunden (OCR nötig).

## 3. Benutzen (offline)

SSD anstecken, `sh start.sh` (Linux/macOS) oder `start.bat` (Windows). Die Modellwahl richtet sich nach
dem RAM (unter 10 GB: 3B, ab 10: 7B, ab 20: 14B); überschreiben mit `MODEL=datei.gguf sh start.sh`.
Browser: **http://localhost:8000** (KI-Chat mit Quellen) · **http://localhost:8080** (Bibliothek direkt durchblättern).
Mit `UI_LAN=1` kann ein Handy im selben WLAN/Hotspot mitnutzen (Port 8000 + 8080).

Wie es funktioniert: Die KI formuliert aus deiner Frage deutsche + englische Suchbegriffe, durchsucht
Kiwix-Bibliotheken und deine Dokumente (SQLite-FTS5), und beantwortet die Frage anhand der Treffer.
Ohne Python startet nur KI (`:8081`) + Bibliothek (`:8080`) – unter Windows bringt prepare.py ein portables Python mit.

## Grenzen – bitte ehrlich einplanen

- **Kleine lokale KI kann Fehler machen.** Bei Medizin, Strom, Gas, Chemie, Statik immer die verlinkte Quelle lesen.
- Die KI braucht einen **Rechner mit Strom** (Laptop + Akku/Powerbank/Solar, ≥ 8 GB RAM, besser 16 GB). Die Bibliothek (`:8080`) läuft auch ohne KI auf jedem Gerät, sogar einem Handy mit Kiwix-App.
- **Karten:** `maps/` enthält Rohdaten (OSM-PBF). Für Navigation **zusätzlich auf dem Handy** *Organic Maps* oder *OsmAnd* installieren und deine Regionen vorher laden – ein Handy kann nicht von der SSD navigieren. Fertige Kartendateien (`.mwm`/`.obf`) kannst du zusätzlich in `maps/` sichern.
- Die Download-Quellen (Kiwix, Hugging Face, GitHub) ändern Namen/Versionen; `prepare.py` sucht die jeweils neueste ZIM/Release automatisch und meldet, was nicht gefunden wurde (dann `catalog.json` anpassen).
- Dieses Repo wurde ohne Internetzugriff entwickelt: die Logik ist getestet (Index, Suche, Chat-Streaming gegen Test-Server), **die Downloads selbst musst du einmal real durchlaufen lassen.**
- Alle 6–12 Monate `prepare.py` erneut ausführen, Modelle und Wikipedia veralten.
- Zusätzlich analog sichern: gedruckte Karte, Notfallnummern, Erste-Hilfe-Karte.
