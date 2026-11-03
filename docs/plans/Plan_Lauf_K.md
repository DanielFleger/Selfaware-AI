# Plan: Lauf K (B-142)

Erstellt 02.11.2026 von SRE nach Daniels "Ja, Lauf K", berichtigt nach drei gescheiterten Proben. Grundlage: `data/research/auge_plan/Checkliste_Auge.md`, Teil B, und die Lehren aus Lauf F.

## Frage des Laufs

Sieht das Auge auch, was KI und Kampf tun? Und ist der Stand nach dem Laden gleich dem gespeicherten, läuft er danach gleich weiter?

## Karte

**`Green Haven`, im Spiel „Der grüne Punkt“** (Daniel 02.11.). Kartenkopf: 8 Spieler, 8 Startplätze. Gemessen: 8 Lords, je Spieler einer, spätestens bei Takt 100, wie auf allen 24 Karten mit 8 Spielern (`karten_acht_lords.json`). Vor dem Start prüft das Programm den Kartenkopf.

## Abschnitte

| # | Abschnitt | Prüfung | Grenze | Grund |
|---|---|---|---|---|
| 0 | Start: 8 KI, kein Mensch, jeder gegen jeden. Das Spiel hält bei Takt 0, die Aufzeichnung läuft an, dann weiter | Takt steht | | Die ersten Takte sollen in der Aufzeichnung sein |
| 1 | Lords stehen | je Spieler genau 1 Lord, Friedenszeit läuft | 200 Takte | Das Doppelte der Messung (Takt 100) |
| 2 | Friedenszeit auf Tempo 1000 | `totalNoRushTicks` läuft auf 0 | 12.000 + 22 Takte | Stufe 1 = 12.000 Takte = 5 Minuten bei Tempo 40, am Start gemessen |
| 3 | Bremsprobe am Ende der Friedenszeit | Abzug ist ein Fund | 3 x 1.000 Takte | Die KI ist jetzt voll im Spiel |
| 4 | Anhalten, speichern, 2.000 Takte auf Tempo 40 (t1) | jeder Takt streng gelesen | 2.000 Takte, 50 Sekunden | Checkliste; Tempo 40 ist die höchste Stufe mit jedem Takt (Lauf F) |
| 5 | Weiter auf Tempo 1000 bis zum letzten Lord | Bremsprobe alle 150.000 Takte | bis 12 Minuten Laufzeit | Kommt kein Ende, ist das ein Ergebnis, kein Scheitern |
| 6 | Hauptmenü, Stand laden, 2.000 Takte (t2). Noch einmal (t3) | jeder Takt streng gelesen, geladen auf den Takt des Speicherns | je 50 Sekunden plus rund 20 Sekunden Laden (Probe) | t1 gegen t2: was ändert das Laden. t2 gegen t3: läuft das Spiel ab dem Laden gleich |

**Warum erst nach dem Kampf geladen wird (Probe 23:19, Spielcode):** `prepareMap` 0x00512450 ruft beim Laden einmal `processGameTick` mit `gamePausedLogical = -1` auf: Einheiten und Gebäude rechnen einen Schritt, Takt und Zufall stehen. Und `upgradeMapFormatForUnits` 0x0053E390 setzt bei jedem Laden über alle Einheiten Tempo und, bei vollem Leben, das Leben auf den Tabellenwert. KI-Lords verlieren so ihren Faktor (gemessen: 75.000 bis 180.000 werden 150.000). Der Kampf soll das nicht abbekommen.

## Die 8 KI-Lords

14, 15, 1, 9, 2, 5, 7, 4. Gerechnet, nicht gewählt: Aus den 16 KI-Sätzen im Speicher (Lauf F) die 8, die sich im Abstand aller Kennwerte am stärksten unterscheiden. Die übrigen 8 sind nur über ihre Tabellen erfasst, wie in der Checkliste.

## Abbruch

Frist 15 Minuten, von Hand gestoppt, Spiel weg, Aufzeichnung weg, 5 s kein Takt (Massenschlachten sind nicht gemessen, Lauf F hatte 1 s), Karte ohne 8 Spieler, nicht je Spieler ein Lord, Friedenszeit greift nicht oder endet nicht, Takt steht nach dem Anhalten nicht, Speichern oder Laden scheitert, geladen auf einen anderen Takt, Takt fehlt oder ist gemischt in einem der drei Fenster.

**Kein Abbruch, sondern Fund:** Abzug in der Bremsprobe (die Massenschlacht misst Lauf S). Abweichungen nach dem Laden sind das Ergebnis, sie stehen in der Auswertung.

**Nach jedem Ende:** Das Ende wird sofort gemeldet. Spiel anhalten, nachlesen, dass der Takt steht, Aufzeichnung beenden, Sperre frei. Kein zweiter Lauf von selbst.

## Erfolg

8 Lords am Start, Friedenszeit zu Ende, alle drei Fenster ohne fehlenden Takt, zweimal geladen. Der letzte Lord muss nicht erreicht sein.

## Auswertung

A1, A2, A3, A5, A6, A7, A9, A10, A11, A12, A13 und die 55 Punkte "Lauf K", dazu die Gegenprobe der Punkte mit Marke [Spielart]. A5 vergleicht t1 einen Takt später mit t2, wegen des Schritts beim Laden. Die Auswertung läuft nach der Meldung, sie kann bei großen Aufzeichnungen lange dauern.

## Trockenlauf

1. Das ganze Programm gegen ein künstliches Spiel, jeder Abbruchgrund, mit Sabotage (`lauf_negativ.py "K:"`, 20 von 20 bemerkt).
2. Kleine Probe am echten Spiel: Fenster 200 Takte, Kampf 2.000 Takte. Gültig seit 23:30.

Gestartet nach Daniels "fange dann an" (02.11. 23:10).

## Was die Proben gefunden haben

| Probe | Abbruch | Ursache | Behoben |
|---|---|---|---|
| Kartensuche | höchstens 7 Lords | Die Startliste trägt Spieler minus 1 ein (`GetPlayerPosition` 0x0042AC60), ich hatte Spieler 1 ausgelassen | Liste 0 bis 7, Test |
| Probe 1, 23:10 | erster strenger Takt gemischt | Erst weiter, dann Tempo: 0,3 s lief das Spiel auf Tempo 1000 | Tempo im Stand setzen, Test |
| Probe 2, 23:19 | Kernfelder nach dem Laden | Das Laden rechnet einen Schritt ohne Takt | Vergleich einen Takt versetzt, Laden erst nach dem Kampf |
| Probe 2 | keine Friedenszeit | Stufe 6 ergibt 0 Takte, die „500“ waren falsch gelesen | Stufe 1 auch in der Probe, Prüfung am Start |
| Lauf K, 1. Durchgang | „letzter Lord“ bei 3 Lebenden (Fehlalarm) | `updateUnits` setzt `maxUnitCount` in jedem Takt auf 0 und zählt hoch, der Zähler las nur bis dorthin | Lord-Zähler über alle 2.500 Plätze, Test |
| Lauf K, 1. Durchgang | Laden hing im Hauptmenü | Das Ladefenster läuft dort nicht weiter (Modal 14, Aktion 31), erst eine laufende Partie lässt es fertig werden | Vor dem Laden ein Gefecht starten, Test |
| Lauf K, 1. Durchgang | halbe Takte im Vergleich | Der Takt steigt vor der Rechnung | In den strengen Fenstern 5 ms warten, Test |

## Ergebnis

Durchgang 2, 02.11. 23:49 bis 23:55, gültig. Bericht: `data/research/auge_plan/lauf_k_20261102/Ergebnis_Lauf_K.md`, Punkte: `Punkte_Lauf_K.md`.
