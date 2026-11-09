# Partie nur mit Raids, 09.11.2026 (B-177, B-178)

Aufstellung `raid_frueh` Version 1 auf Instanz 2: The Killing Plains, KI-Nummer 7 als zwei Gegner, Tempo 200, bis Takt 40.071. `logik.lua` sha256 533d78d156642eec, Kern 24 (DLL sha256 223c45b3ee2cea7a), Code 34cea1c.

Mitschrift `data/research/aufstellung_20261109_223741_raid_frueh_i2_konsole.txt`, Lagebild `data/research/lage_20261109_223747_i2.jsonl.gz`. Die Zahlen rechnet `auswertung.py`, Ausgabe `ergebnis.txt`.

**Eine Partie je Einstellung ist nur eine erste Richtung.**

## Vorher angesagt

Erhofft: Es kommen nur Raid-Einheiten dazu, Ausweichen läuft nur unter Beschuss. Widerlegt: eine andere Soldatenart kommt neu dazu. Abbruch: bis Takt 10.000 keine Raid-Werbung (selbst gesetzte Grenze, in der Partie davor kam die erste bei Takt 6.712).

## Ergebnis

| Prüfung | Gemessen | Wie |
|---|---|---|
| Nur Raids | Neu: 50 Sklaven (A_SLAVE 71), 43 Assassinen (A_ASSASSIN 73), 3 Berittene Bogenschützen (A_HARCHER 74). Andere Soldaten neu: 0 | Lagebild, erstes Bild (Takt 698) als Starttruppen |
| Abbruchgrenze | Erste Raid-Werbung Takt 6.568 | Mitschrift |
| Ausweichen seltener | 535 Wegpunkte, an 12 von 63 Messstellen Trupps aktiv. Partie davor (immer an): 8.826 Wegpunkte, 74 von 81 | Kern-Protokoll, eine Zeile je 500 Takte |
| Ausweichen wirklich nur unter Beschuss | **In der Partie nicht einzeln gemessen.** Nur die Regel ist ohne Spiel getestet | `tests/test_baukasten.py` |

## Warum das Gold erst fehlt und dann liegen bleibt

- **Bis etwa Takt 22.500 ist Gold der Engpass:** meist unter 100 Gold, dabei 18 bis 23 freie Leute am Feuer. Bis Takt 2.506 ist das Feuer leer, bei Takt 5.117 stehen 10 Leute dort. Bei Takt 5.221 meldet die Mitschrift 8 Gold und „Planer braucht Gold“.
- **Ab Takt 30.000 läuft das Gold auf, 5.578 am Ende.** Sklaven (Soll 5) und Berittene (Soll 3) sind voll. Assassinen werden kaum noch geworben, weil laut Mitschrift bis zu 9 von ihnen kein ungefährliches Ziel finden („alle gefährlich“) und die Werbung ab 2 ohne Ziel stoppt (`A_OHNE_ZIEL_MAX`).
- **Reiter:** 13 bestellt, 3 angekommen. In 8 von 12 Bestellrunden kam kein Reiter, in allen 12 aber eine Assassine, und das Gold fiel oft um genau 70, den Preis der Assassine. Beide Stellen rechnen mit dem Gold vom Rundenanfang, die Assassine wird zuerst gekauft. Die Mitschrift zählt die Bestellung trotzdem.

## Vergleich (je eine Partie, gleiche Karte und Gegner)

| | raid_frueh | Zickzack an | Zickzack aus |
|---|---|---|---|
| Rekrutiert | nur Raids | alles | alles |
| Angezündet | 22 | 19 | 13 |
| Zerstört | 56 | 45 | 37 |
| Eigene Verluste | 33 | 31 | 24 |
| Arbeiter von Reitern getötet | 17 | 10 | 21 |

## Nicht geklärt

- Der Kern meldet 227 doppelte Gebäude-Befehle, in der Partie davor 2. Vermutung: Ohne ständiges Ausweichen wiederholt der Brandtrupp denselben Befehl. Nicht untersucht.
- Der Kern meldet 86-mal „wirkt nicht“ bei Gebäuden, obwohl Gebäude brennen (schon in der Partie davor offen).
