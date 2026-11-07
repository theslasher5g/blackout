# 03 – Funk: Kommunikation ohne Netz

> Rechtlich: In echter Lebensgefahr darf **jeder** einen Notruf auf jeder Frequenz absetzen. Ansonsten gelten Lizenz- und Frequenzregeln (Deutschland, Stand 2024 – aktuelle Vorschriften der Bundesnetzagentur prüfen).

## Welche Funkarten gibt es?
| Dienst | Frequenz | Lizenz (DE) | Leistung | Reichweite typ. |
|---|---|---|---|---|
| **PMR446** | 446,0–446,2 MHz, 16 Kanäle | keine | 0,5 W ERP, feste Antenne | 0,5–3 km (Stadt), bis 5+ km freies Feld |
| **Freenet** | 149,025–149,1125 MHz, 6 Kanäle | keine (Anmeldung nicht nötig) | 0,5 W ERP | 1–4 km |
| **CB-Funk** | ca. 26,565–27,405 MHz, 80 FM-Kanäle (AM/FM) | keine, Geräte zugelassen | FM 4 W, AM 1 W | 3–10 km; Kanal 9 gilt als Notrufkanal |
| **Amateurfunk 2 m** | 144–146 MHz | **Zeugnis nötig** | bis 750 W (Klasse A), N/E weniger | 5–50 km, über Relais viel mehr |
| **Amateurfunk 70 cm** | 430–440 MHz | Zeugnis | s. o. | 5–30 km |
| **Amateurfunk Kurzwelle** | 80 m (3,5–3,8), 40 m (7,0–7,2), 20 m (14,0–14,35) MHz | Zeugnis | s. o. | 100–10 000 km |
| **Marinefunk Kanal 16** | 156,800 MHz | Zeugnis auf See | | Notruf Schiffe |
| **Flugnotfrequenz** | 121,500 MHz | | | Flug-Notruf |

Faustregel: **UKW/UHF = Sichtverbindung**, Reichweite steigt mit Höhe (Hügel, Dach, Turm). Kurzwelle reflektiert an der Ionosphäre – für große Entfernungen, braucht Erfahrung.

## Schnellstart ohne Lizenz
1. PMR446-Geräte (Set ~40 €), **Akkus/Batterien auf Vorrat**.
2. Vorher mit Nachbarn/Familie **Kanal und Zeitplan vereinbaren** (z. B. täglich 18:00 und 08:00 je 10 Minuten zuhören auf Kanal 5).
3. Höher stehen, Gerät aufrecht halten, nicht in Metallgebäuden sprechen.
4. Weniger ist mehr: kurz sprechen, Akku sparen.

## Sprechfunk-Regeln
- **Hören vor Senden.** Wenn Kanal belegt: warten.
- Erst Gegenstelle, dann sich selbst: „**Anton, hier Berta, kommen.**“
- „**Kommen**“ = Ende der Durchsage, Antwort erwartet. „**Ende**“ = Gespräch beendet. „**Verstanden**“ = bestätigt.
- Zahlen einzeln: „eins vier fünf Komma fünf null null“. Wichtiges buchstabieren und wiederholen lassen.
- **Notruf-Ablauf (MAYDAY):** „MAYDAY, MAYDAY, MAYDAY – hier ist [Name/Standort] – MAYDAY. Position [Ort/Koordinaten] – Art des Notfalls – Zahl der Personen – benötigte Hilfe – kommen.“ Für dringende, nicht lebensbedrohliche Lage: „PAN-PAN“ (3×).
- Feste **Hörzeiten** vereinbaren (z. B. täglich 08:00 und 18:00, je 10 Minuten), damit Akkus geschont werden.

## Buchstabieralphabet Deutsch (DIN 5009)
Anton, Berta, Cäsar, Dora, Emil, Friedrich, Gustav, Heinrich, Ida, Julius, Kaufmann, Ludwig, Martha, Nordpol, Otto, Paula, Quelle, Richard, Samuel, Theodor, Ulrich, Viktor, Wilhelm, Xanthippe, Ypsilon, Zacharias.

## ICAO/NATO international
Alfa, Bravo, Charlie, Delta, Echo, Foxtrot, Golf, Hotel, India, Juliett, Kilo, Lima, Mike, November, Oscar, Papa, Quebec, Romeo, Sierra, Tango, Uniform, Victor, Whiskey, X-ray, Yankee, Zulu.

## Amateurfunk einsteigen (vor der Krise!)
- Prüfung bei der Bundesnetzagentur (Klassen N, E, A), Lernmaterial z. B. von **DARC** (Online-Lehrgang, Ortsverbände helfen kostenlos).
- Anrufkanal 2 m FM: **145,500 MHz**; 70 cm FM: **433,500 MHz**. Notfunk wird über Ortsverbände/Relaisfunkstellen organisiert.
- Handfunkgeräte (Baofeng, Yaesu, Kenwood) 40–150 €; Ersatzakku, **Außenantenne** (J-Pole, Magnetfuß) vergrößert Reichweite stark.
- Relais (Repeater) erweitern die Reichweite; Frequenz-Listen vorher ausdrucken/speichern.
- Kurzwelle mit Dipolantenne und einem 10–100-W-Transceiver für Fernverbindungen; Stromversorgung per 12-V-Akku/Solar.

## Antennen-Faustformeln
- **Halbwellen-Dipol:** Gesamtlänge ≈ **143 / f(MHz)** Meter (z. B. 7,1 MHz ≈ 20,1 m, je 10,05 m pro Seite). Leicht kürzer wenn Draht isoliert.
- **Viertelwellen-Strahler:** ≈ **71 / f(MHz)** Meter (145 MHz ≈ 49 cm).
- Höhe und freie Umgebung schlagen Leistung. Koax kurz halten, SWR prüfen (< 2:1), Antenne nie bei Gewitter betreiben.
- Notantenne: Dipol aus Litze/Klingeldraht, in Bäumen aufgehängt, Mittelisolator aus Plastik.

## Nur empfangen (immer erlaubt)
- **UKW-Rundfunk** (87,5–108 MHz): Katastrophen-Durchsagen. Kurbelradio besitzen.
- **Kurzwelle**: Weltempfänger (BBC, Deutsche Welle, Zeitzeichen).
- **Langwelle DCF77 (77,5 kHz)**: Zeitzeichensender (Funkuhren).
- **Wetter/Seefunk**: Sturmwarnungen über UKW-Seefunk.
- Handy: **Cell Broadcast** (Warnungen) kommt auch bei überlasteten Netzen oft durch, solange Mobilfunk-Masten Strom haben (meist wenige Stunden bis Tage).

## LoRa/Meshtastic (digitale Textnachrichten ohne Netz)
- **Meshtastic**-Geräte (868 MHz EU, lizenzfrei) bauen ein Mesh-Netz für **Kurznachrichten und GPS-Position**. Reichweite pro Hop 1–10 km (Sichtverbindung, Höhe!), mehr über mehrere Knoten.
- Hardware: Heltec V3, LilyGO T-Beam, RAK WisBlock (~25–60 €), Handy-App per Bluetooth. **Vorher** konfigurieren, gleiche Region (EU_868), gleiche Kanalschlüssel verteilen.
- Sehr stromsparend (Wochen an einer Powerbank). Ideal für Gruppen/Nachbarschaft.
- Alternative **Briar** (Android): Chat per Bluetooth/WLAN direkt zwischen Handys, ohne Internet.

## Morsecode (Rettung, Lichtsignal, Klopfen)
A ·–   B –···   C –·–·   D –··   E ·   F ··–·   G ––·   H ····   I ··   J ·–––   K –·–   L ·–··   M ––
N –·   O –––   P ·––·   Q ––·–   R ·–·   S ···   T –   U ··–   V ···–   W ·––   X –··–   Y –·––   Z ––··
1 ·––––  2 ··–––  3 ···––  4 ····–  5 ·····  6 –····  7 ––···  8 –––··  9 ––––·  0 –––––
**SOS = ··· ––– ···** (Taschenlampe, Pfeife, Klopfen, Spiegel). Internationale Not-Pfeifsignale: 6× pro Minute, 1 Min Pause, wiederholen.
