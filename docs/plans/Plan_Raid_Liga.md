# Plan: Raid-Module gegen verschiedene Gegner auf Team-Liga-Karten (B-182)

Auftrag Daniel 10.11.2026 09:25: selbstständig an den Raid-Modulen weiterarbeiten, gegen verschiedene Gegner auf verschiedenen Team-Liga-Karten, Fokus auf die 2 bis 3 wichtigsten Module. Daniel ist 10 Stunden nicht erreichbar.

## Fokus: drei Module

1. **Kauf nach Wirkung** (`baukasten/wirkung.py`, `RaidBestellungNachWirkung`): Erwartung gegen Ergebnis eichen. Jede Zeile `WIRKUNG-KAUF` nennt, was eine Art bringen soll. Nach jeder Partie wird verglichen, was sie wirklich gebracht hat. Ersatzwerte (Gebäuderate anderer Nahkämpfer, Leben auf Instanz 2) werden durch Messwerte aus den Partien ersetzt.
2. **Nahkampf-Raid** (`micro/tasks/nahkampf.py`): erste echte Einsätze. Zu prüfen: Zielwahl, sicherer Weg, Verluste, und ob die Einheiten am Ziel wirklich Schaden machen.
3. **Brandtrupp** (Sklaven, `micro/tasks/raids.py`): bisher das stärkste Mittel. Zu klären: warum der Kern 86-mal „wirkt nicht“ meldet, obwohl Gebäude brennen, und welche Gebäudearten Sklaven überhaupt anzünden können.

## Ablauf je Schritt

1. Ansage in diesem Plan (Abschnitt Stand): was, erhofft, widerlegt wenn, Grenze.
2. Eine Änderung, dann eine Partienreihe auf Instanz 2 mit Wache (Abbruch bei Angriffs- oder Verteidigungswerbung, ohne Raid-Werbung bis Takt 10.000, ohne Fortschritt).
3. Auswertung mit `aufstellung_vergleich` und Mitschrift, Eintrag im Register, Commit, Push.

## Gegner und Karten

- Karten: zuerst The Killing Plains (alle bisherigen Zahlen), dann Team-Liga-Karten. Welche es auf Instanz 2 gibt, wird zuerst nachgesehen, nicht geraten.
- Gegner: KI-Nummer 7 (bisher), dazu 8 und eine dritte. Ihre Namen kommen aus der Liga-Datei, nicht aus dem Gedächtnis.
- Je Karte und Gegner dieselben zwei Aufstellungen: `raid_ohne_angriff` (feste Kasse) gegen `raid_wirkung` (Kauf nach Wirkung).

## Grenzen

- Nur Instanz 2. Instanz 4 (SAI) und 5 (Daniel) bleiben unberührt.
- Fairness (`docs/FAIRNESS.md`): nur Sichtbares, nichts am Spiel verändern.
- Keine Umbauten an Angriff, Verteidigung oder Wirtschaft.
- Je Partie bis Takt 40.000, Tempo 200.

## Stand

| Zeit | Schritt | Ergebnis |
|---|---|---|
| 10.11. 09:23 | Reihe 1: The Killing Plains, KI 7: `raid_frueh`, `raid_ohne_angriff`, `raid_wirkung` | läuft |
