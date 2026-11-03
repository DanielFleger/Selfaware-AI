# Punkte Lauf S

75 Punkte der Checkliste (Abschnitt Lauf S) gegen alle 30 Aufzeichnungen, mit dem Werkzeug `auge_punkte`. Befehl oben in `punkte_lauf_s.py`, Zahlen in `punkte_lauf_s.txt`.

**„Gesehen“ heißt nur: Das Feld ändert sich.** Ob das zur Erwartung im Punkt passt, muss noch jemand lesen, das ist für diese 50 nicht geschehen. In Lauf K wurde das je Punkt von Hand nachgerechnet, hier noch nicht.

| Urteil | Punkte |
|---|---|
| gesehen | 50 |
| nicht gesehen | 6 |
| nicht zuordenbar | 15 |
| zahl passt | 4 |

**Nicht gesehen:** P302 UpdateTower4, P306 processUnitLossStatistic, P317 UpdateLadderManState01, P320 resetCountdownInHeatMap, P331 shouldUnitsEngageInMelee, P370 updateUnits. P317 passt dazu, dass die Leiter nicht erreicht wurde.

**Nicht zuordenbar** (das Werkzeug findet im Punkt kein Feld): P305, P307, P310, P311, P334, P335, P338, P353, P354, P355, P356, P361, P366, P367, P368.

## Gesamtproben an drei Szenen

| Probe | Punkt | Einzel Gefecht | 1.000 gegen 1.000 |
|---|---|---|---|
| A1 Felder außerhalb der Liste | 241 | 10 | 3 |
| A3 Takte | Tempo 200, nicht streng | Tempo 100: 848 fehlen, 782 gemischt. Das Werkzeug schreibt „widerlegt“, weil es Tempo 100 als streng behandelt; die Szene war absichtlich nicht streng | Tempo 1000, nicht streng |
| A4 Lesen je Takt, Median und Höchstwert | 1,2 und 15,3 ms | 2,6 und 14,6 ms | 0,6 und 15,3 ms |
| A7 Zufallsfolge passt zur Tabelle | 2.315 von 2.315 | 5.120 von 5.120 | **2.173 von 2.174** |
| A10 Platzwechsel ohne Verstoß | 7.776 | 17.912 | 9.745 |

A1: Die ersten 14 der 241 Felder gehören zum Befehlsring `DAT_GameCommand...`, weil hier viele Befehle liefen. Alle 241 sind nicht einzeln angesehen. A7: Der eine Fall auf Tempo 1000 ist nicht geklärt, vermutlich ein Rahmen über die Taktgrenze.
