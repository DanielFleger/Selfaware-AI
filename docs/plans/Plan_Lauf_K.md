# Plan: Lauf K (B-142)

Erstellt 02.11.2026 von SRE nach Daniels "Ja, Lauf K". Grundlage: `data/research/auge_plan/Checkliste_Auge.md`, Teil B, und die Lehren aus Lauf F.

## Frage des Laufs

Sieht das Auge auch, was KI und Kampf tun? Und ist der Stand nach dem Laden gleich dem gespeicherten, läuft er danach gleich weiter?

## Abschnitte

| # | Abschnitt | Prüfung | Grenze | Grund |
|---|---|---|---|---|
| 1 | Gefecht: 8 KI, kein Mensch, jeder gegen jeden | 8 Lords stehen | 200 Takte | Eine Karte mit zu wenig Plätzen zeigt sich sofort |
| 2 | Friedenszeit auf Tempo 1000 | `totalNoRushTicks` läuft auf 0 | 12.000 + 22 Takte | Stufe 1 der Spieltabelle = 12.000 Takte = 5 Minuten bei Tempo 40 (gelesen in Lauf F) |
| 3 | Bremsprobe am Ende der Friedenszeit | Abzug ist ein Fund | 3 x 1.000 Takte | Die KI ist jetzt voll im Spiel |
| 4 | Anhalten, speichern, 2.000 Takte auf Tempo 40 | jeder Takt streng gelesen | 2.000 Takte, 50 Sekunden | Checkliste; Tempo 40 ist die höchste Stufe mit jedem Takt (Lauf F) |
| 5 | Laden, Vergleich A5, dieselben 2.000 Takte, Vergleich A6 | Abbruch, wenn Kernfelder nach dem Laden abweichen | wie 4 | Checkliste: Weicht A5 stark ab, wird nicht weitergespielt |
| 6 | Weiter auf Tempo 1000 bis zum letzten Lord | Bremsprobe alle 150.000 Takte | bis 14 Minuten Laufzeit | Rund 620.000 Takte. Kommt kein Ende, ist das ein Ergebnis, kein Scheitern |

## Die 8 KI-Lords

14, 15, 1, 9, 2, 5, 7, 4. Gerechnet, nicht gewählt: Aus den 16 KI-Sätzen im Speicher (Lauf F) die 8, die sich im Abstand aller Kennwerte am stärksten unterscheiden. Die übrigen 8 sind nur über ihre Tabellen erfasst, wie in der Checkliste.

## Abbruch

Frist 15 Minuten, von Hand gestoppt, Spiel weg, Aufzeichnung weg, 5 s kein Takt (Massenschlachten sind nicht gemessen, Lauf F hatte 1 s), weniger als 8 Lords am Start, Friedenszeit endet nicht, Takt steht nach dem Anhalten nicht, Speichern oder Laden scheitert, Takt fehlt oder ist gemischt in einem der beiden Fenster, Kernfelder weichen nach dem Laden ab (Einheiten-Ort und -Typ, Gebäudetyp, Waren, Monat).

**Kein Abbruch, sondern Fund:** Abzug in der Bremsprobe (die Massenschlacht misst Lauf S), einzelne andere Felder bei A5 und A6.

**Nach jedem Ende:** Das Ende wird sofort gemeldet. Spiel anhalten, nachlesen, dass der Takt steht, Aufzeichnung beenden, Sperre frei. Kein zweiter Lauf von selbst.

## Erfolg

8 Lords am Start, Friedenszeit zu Ende, beide Fenster ohne fehlenden Takt, A5 und A6 haben ein Ergebnis. Der letzte Lord muss nicht erreicht sein.

## Auswertung

A1, A2, A3, A5, A6, A7, A9, A10, A11, A12, A13 und die 55 Punkte "Lauf K", dazu die Gegenprobe der Punkte mit Marke [Spielart]. Die Auswertung läuft nach der Meldung, sie kann bei großen Aufzeichnungen lange dauern.

## Trockenlauf

1. Das ganze Programm gegen ein künstliches Spiel, jeder Abbruchgrund, mit Sabotage.
2. Kleine Probe am echten Spiel: Karte finden, Friedenszeit-Stufe 6 (500 Takte), Fenster 200 Takte, Ende nach 2.000 Takten. Prüft Start, Speichern, Laden und A5/A6 in echt.

Der echte Lauf startet erst nach Ansage und Daniels Ja.
