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

## Gefunden (10.11. 09:35)

- **Team-Liga-Karten auf Instanz 2** (`ucp/plugins/Mod-KI-Team-Liga-2.0.2/resources/maps`): Battle Brother's Strife, Branching Fortunes, Dwarven Dream, Green Trench, Grumpy Neighbors, Paradise Plains. Grumpy Neighbors ist die Hauskarte des Lenkers (Plan M19), jede andere vermisst der Lenker beim ersten Lauf einmal selbst.
- **KI-Nummern** laut `config.yml` der Liga: 1 Rotkäppchen, 2 Rattenfänger, 3 Kult (Franz von Festenberg), 4 BierKönig (Karl von Festenberg), 5 Bauer, 6 König, 7 Gardist, 8 Kriegsfürst. Die bisherigen Partien liefen also gegen zwei Gardisten.
- Die Platzliste `0,1,7` gilt nur für The Killing Plains. Darum nimmt eine Aufstellung einen Schalter der Basis mit `null` heraus (`raid_*_gn`).

## Reihenfolge der Reihen

1. The Killing Plains, Gardist: `raid_frueh`, `raid_ohne_angriff`, `raid_wirkung` (läuft).
2. Grumpy Neighbors, Gardist: `raid_ohne_angriff_gn` gegen `raid_wirkung_gn`.
3. Grumpy Neighbors, Kriegsfürst: dieselben zwei.
4. Green Trench und Paradise Plains, je ein Gegner: erst vermessen, dann dieselben zwei.

## Grenzen

- Nur Instanz 2. Instanz 4 (SAI) und 5 (Daniel) bleiben unberührt.
- Fairness (`docs/FAIRNESS.md`): nur Sichtbares, nichts am Spiel verändern.
- Keine Umbauten an Angriff, Verteidigung oder Wirtschaft.
- Je Partie bis Takt 40.000, Tempo 200.

## Stand

| Zeit | Schritt | Ergebnis |
|---|---|---|
| 10.11. 09:23 | Reihe 1: The Killing Plains, Gardist (KI 7): `raid_frueh`, `raid_ohne_angriff`, `raid_wirkung` | Je Aufstellung: angezündet 20 / 20 / 42, Gold am Ende 5.054 / 6.392 / 2.698, tote Assassinen 29 / 27 / 12, Arbeiter von Reitern getötet 18 / 48 / 0. Der Kauf nach Wirkung kaufte nur Sklaven (363 angekommen) und Assassinen (27): Die Rechnung traute Sklaven auch Arbeiter zu, die der Brandtrupp nie jagt. Behoben: Jede Art bekommt nur die Ziele ihres Moduls (`raid.ZIELARTEN`). Je eine Partie, nur eine erste Richtung. |
| 10.11. 09:50 | Reihe 2: Grumpy Neighbors, Gardist: `raid_ohne_angriff_gn` gegen `raid_wirkung_gn`. Erhofft: Der Kauf nach Wirkung kauft jetzt auch Reiter, und auf der neuen Karte laufen beide ohne Fehler. Widerlegt, wenn wieder nur eine Art gekauft wird oder eine Partie hängt. | läuft |
