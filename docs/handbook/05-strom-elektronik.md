# 05 – Strom & Elektronik

> **Lebensgefahr:** 230 V tötet. Arbeiten an Hausinstallation nur Elektrofachkräfte. Hier geht es um **Kleinspannung (12 V, USB, Akkus)** und sicheren Umgang.

## Formeln
- **Ohmsches Gesetz:** U = R · I (Volt = Ohm · Ampere)
- **Leistung:** P = U · I (Watt)
- **Energie:** Wh = V · Ah; kWh = 1000 Wh
- Reihenschaltung: Spannungen addieren, Strom gleich. Parallel: Ströme addieren, Spannung gleich.
- LED-Vorwiderstand: R = (U_Quelle − U_LED) / I_LED, z. B. (5 V − 2 V) / 0,015 A = 200 Ω (nächster Wert 220 Ω).
- Leitungsverlust: dicke Kabel bei niedriger Spannung! 1000 W bei 12 V = 83 A → mind. 16–25 mm² und Sicherung dicht an der Batterie.

## Widerstands-Farbcode
Schwarz 0, Braun 1, Rot 2, Orange 3, Gelb 4, Grün 5, Blau 6, Violett 7, Grau 8, Weiß 9. Ringe: 1. Ziffer, 2. Ziffer, Multiplikator (10^n), dann Toleranz (Gold 5 %, Silber 10 %). Beispiel Gelb-Violett-Rot = 4 7 ·100 = 4,7 kΩ.

## Akkus & Batterien
| Typ | Nennspannung | nutzbar | Hinweis |
|---|---|---|---|
| Blei (Auto/AGM) | 12 V | ~50 % der Ah | nicht tief entladen, gasen beim Laden → lüften |
| LiFePO4 | 12,8 V | 80–90 % | sicher, langlebig, BMS beachten |
| Li-Ion (18650) | 3,6–3,7 V | 80–90 % | Brandgefahr bei Kurzschluss/Beschädigung |
| NiMH (AA/AAA) | 1,2 V | gut | wiederaufladbar, selbstentladungsarme „Eneloop“ |
| Alkaline | 1,5 V | – | lange lagerbar, nicht wiederaufladen |
- **Beispiel:** 12 V · 100 Ah = 1200 Wh. Bei Blei nutzbar ~600 Wh = z. B. 60 W Verbraucher 10 h.
- Powerbank-Kapazität ist in **Zellspannung (3,7 V)** angegeben, real nutzbar ca. 60–70 %: 20 000 mAh ≈ 74 Wh Zelle ≈ 45–50 Wh nutzbar ≈ 4 Handy-Vollladungen (je ~12 Wh).
- Kurzschluss vermeiden, Pole abkleben, keine beschädigten Li-Ion laden, nicht im Auto bei Hitze lagern.

## Solar
- Panelleistung in Wp; **Ertrag/Tag ≈ Wp × Sonnenstunden-Äquivalent**: Sommer ≈ 4–5 h, Winter ≈ 0,5–1 h (Deutschland).
- Beispiel 100 Wp im Sommer ≈ 400–500 Wh/Tag, im Winter ≈ 50–100 Wh.
- **Laderegler** (MPPT) zwischen Panel und Akku; Sicherungen auf beiden Seiten.
- Panels ausrichten nach Süden, Neigung ~30–45°, nicht verschatten (ein Schatten kann das ganze Modul bremsen).
- Faltbare 20–60-W-Panels laden Powerbanks/Handys direkt per USB-C.

## Aggregate & Wechselrichter
- **Aggregat nur im Freien**, mind. mehrere Meter von Fenstern/Türen/Lüftungen, **nie** in Garage/Keller (CO!), gegen Regen schützen, nicht heiß nachtanken, Brennstoff sicher lagern.
- **Niemals in die Steckdose einspeisen („Hausrückspeisung“)**: lebensgefährlich für Netzarbeiter, zerstört Geräte. Nur über zugelassene Umschalteinrichtung (Elektriker!) oder direkte Verbraucher-Steckdosen am Aggregat.
- Wechselrichter (12 V → 230 V): Reine Sinus für empfindliche Geräte, Leistungsreserve +30 %, dicke Kabel.
- Autobatterie als Notquelle: Motor ab und zu laufen lassen (nur im Freien), nicht komplett leerziehen.

## Sicherheit & Messen
- Multimeter: Gleichspannung (V⎓), Durchgang (Piepser), Widerstand (Ω). Strommessung nur in Reihe, Messbereich beachten.
- Sicherungen immer in den **Pluspol**-Zweig nahe der Quelle.
- Flüssigkeit/Feuchtigkeit und Strom: Abstand. Kinder fernhalten.
- Brandbekämpfung: Elektro-/Lithiumbrand: nur kleine Brände mit CO₂/Pulver; große Li-Ion-Brände nicht löschen, Abstand halten, Raum verlassen.

## Reparieren / Löten (Grundlagen)
- Lötkolben 300–350 °C, bleifreies Lot, Flussmittel; kurz erhitzen, Lot an Bauteil+Pad, **nicht** am Kolben.
- Typische Fehler: kalte Lötstelle (matt/rau), Brücken, falsche Polarität bei Elkos/LEDs/Dioden.
- Ersatzteile aus Altgeräten: Netzteile, Motoren, Schalter, Kabel, Akkus.
- Anleitungen: iFixit-ZIM, Elektronik-StackExchange-ZIM.

## Typische Verbrauchswerte (Orientierung)
LED-Lampe 3–10 W · Router 8–12 W · Kühlschrank ~100 W (im Betrieb) · Gefriertruhe ~100 W · Laptop 30–60 W · Heizlüfter 1000–2000 W (nicht für Notstrom!) · Kaffeemaschine ~1000 W.
