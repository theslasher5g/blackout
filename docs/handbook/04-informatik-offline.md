# 04 – Informatik & IT offline

## Grundregel: Strom ist knapp
Typischer Verbrauch: Smartphone 3–6 W (Laden 10–15 Wh pro Vollladung), Raspberry Pi 3–6 W, Laptop 15–60 W, Desktop-PC 100–300 W, **lokale KI auf CPU 30–100 W**.
→ **Bibliothek (Kiwix) lesen** statt KI fragen, wenn Strom knapp ist. KI nur für gezielte Fragen starten. Bildschirm dunkel, Flugmodus, Netzwerkdienste aus.

## Wissensbibliothek für andere bereitstellen
- Auf dem Laptop: `UI_LAN=1 sh start.sh` startet Chat (Port 8000) und Kiwix (8080) für andere Geräte im selben WLAN.
- Kein Router? **Handy-Hotspot** (ohne SIM-Daten) oder Laptop-Hotspot aufmachen; Gäste verbinden sich und öffnen `http://<IP-des-Laptops>:8080`.
- IP herausfinden: Linux/Mac `ip a` bzw. `ifconfig`, Windows `ipconfig`.
- Kiwix-App (Android/iOS) kann ZIM-Dateien direkt lesen – ZIMs auf Handys kopieren.

## Netzwerk-Grundwissen
- **IPv4-Privatbereiche:** 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16. `/24` = 255.255.255.0 = 254 Hosts.
- Tools: `ping`, `ip a`/`ipconfig`, `ss -tulpn`/`netstat -ano`, `traceroute`.
- Lokale Datei-Server: `python3 -m http.server 9000` im gewünschten Ordner.
- Ad-hoc-Netz: Zwei Rechner per **Ethernet-Kabel** direkt verbinden, feste IPs 192.168.50.1/24 und 192.168.50.2/24.
- Kabel-Fehler: Link-LED prüfen, anderer Port, Kabel tauschen.

## Linux-Spickzettel
```
ls -la          Dateien       cd, pwd         Ordner
cp -r a b       kopieren      mv a b          verschieben
rm -r ordner    löschen       mkdir -p a/b    anlegen
cat, less       lesen         grep -ri text . suchen
df -h           Speicher      du -sh *        Größen
lsblk           Datenträger   mount           einhängen
ps aux          Prozesse      kill PID        beenden
chmod +x f      ausführbar    sudo            Adminrechte
tar xzf a.tgz   entpacken     sha256sum f     Prüfsumme
rsync -a --progress quelle/ ziel/             Backup
```
- Hilfe zu jedem Befehl: `man befehl`, `befehl --help`.
- Datenträger prüfen/reparieren: `lsblk`, `fsck` (nur ausgehängt!), Daten retten mit `ddrescue`.
- Windows: `dir`, `cd`, `copy`, `robocopy quelle ziel /E`, `ipconfig`, `tasklist`.

## Backups (3-2-1)
**3 Kopien, 2 Medien, 1 an anderem Ort.** Wichtige Dokumente (Ausweise, Verträge, Fotos, Schlüssel/Passwörter) verschlüsselt auf SSD/USB + Papier-Kopie. Prüfsummen mit `sha256sum` speichern, um Korruption zu erkennen. SSD/USB-Sticks halten Daten ohne Strom Jahre, aber **nicht ewig – alle 1–2 Jahre auffrischen/kopieren**.

## Verschlüsselung & Passwörter
- Datenträger: **VeraCrypt** (plattformübergreifend), Linux `cryptsetup`/LUKS.
- Passwortmanager offline: **KeePassXC** (Datei mit auf SSD).
- Notfall-Passwortliste auf Papier im Safe/Versteck. Nicht alles im Kopf behalten.

## Programmieren offline
- Python 3 (Standardbibliothek reicht für viel): Dokumentation `python3 -m pydoc -b` öffnet Hilfe im Browser **lokal**. Alternativ ZIM „python docs“/Stack-Overflow-ZIMs.
- Mini-Beispiel (Messwerte loggen):
```python
import time, csv
with open("log.csv", "a", newline="") as f:
    w = csv.writer(f)
    for _ in range(10):
        w.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), 12.6])  # z.B. Batteriespannung
        f.flush(); time.sleep(60)
```
- Shell: Schleifen, Variablen, Pipes (`cmd1 | cmd2`) lösen viele Probleme ohne Zusatzsoftware.
- **Git** funktioniert komplett offline (`git init`, `git commit`, `git bundle` zum Austauschen per USB).
- Sprachen/Referenzen (vorher laden!): Dokumentation von Python, C, JavaScript, Bash, SQL, Arduino.

## Raspberry Pi / Arduino / ESP32
- **Raspberry Pi** (3–6 W) ist ideal als Dauer-Wissensserver/Hotspot (Kiwix läuft, Chat ohne KI), per Solar/Powerbank betreibbar.
- **Arduino/ESP32** für Sensoren, Funk (LoRa), Steuerungen. IDE/Bibliotheken **vorher** offline spiegeln (arduino-cli, PlatformIO-Cache).
- SD-Karten sichern (Image mit `dd`/Imager), Ersatzkarte bereithalten.

## Zahlensysteme, ASCII, Codes
- Binär ↔ Hex: 0000=0 … 1001=9, 1010=A, 1011=B, 1100=C, 1101=D, 1110=E, 1111=F.
- ASCII: `A`=65 (0x41), `a`=97 (0x61), `0`=48 (0x30), Leerzeichen=32, Zeilenumbruch=10.
- UTF-8 für Umlaute; Dateinamen ohne Sonderzeichen, wenn plattformübergreifend.
- Prüfsummen: CRC (Übertragung), SHA-256 (Integrität). Einfaches Papier-Codeschema: Caesar/Vigenère nur zum Spaß, **nicht sicher**.

## Offline-Hilfen sinnvoll sammeln
Karten (OsmAnd/Organic Maps), Kiwix-ZIMs, Datenblätter, Treiber/Firmware, Linux-ISO (Live-USB), KeePassXC/VeraCrypt-Installer, Android-APKs wichtiger Apps (F-Droid: Briar, Meshtastic, Kiwix, OsmAnd), Wörterbuch.
