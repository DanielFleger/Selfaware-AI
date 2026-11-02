# Ergebnis Lauf F

Erstellt 02.11.2026 von SRE (B-142). Lauf 21:42:40 bis 21:51:17, Instanz 2, Burgenbau "A Mighty Oasis", Liga-Balance aktiv. Auswertung bis 21:58:46.

## Frage und Antwort

**Sieht das Auge alles, was im friedlichen Spiel passiert, ohne das Spiel zu bremsen?**

- **Bremsen: nein.** Auf keiner Stufe von 1 bis 1000 zieht das Lesen Tempo ab, gemessen im vollen Dorf.
- **Jeden Takt sehen: bis Tempo 40 ja.** Ein ganzes Jahr, 9.605 Lesungen, 0 fehlend, 0 gemischt. Darüber geht das Tempo vor, siehe Tabelle.
- **Alles sehen: noch nicht.** Die Feldliste hatte Lücken: 624 Spielfelder änderten sich außerhalb der Liste, sie stehen jetzt drin. Kampf und KI zeigt erst Lauf K und S.

| Stufe | ohne Lesen | mit Lesen | ohne Lesen | gelesene Takte |
|---|---|---|---|---|
| 1 | 1,0 | 1,0 | 1,0 | alle (20) |
| 10 | 9,98 | 9,98 | 9,98 | alle (100) |
| 40 | 39,94 | 39,92 | 39,93 | alle (1.000) |
| 100 | 99,82 | 99,82 | 99,84 | 988 von 1.001 |
| 200 | 199,78 | 199,46 | 200,19 | 732 von 1.002 |
| 500 | 499,17 | 499,50 | 500,57 | 361 von 1.000 |
| 1000 | 824,23 | 825,23 | 825,49 | 242 von 1.001 |

## Erfolgsbedingungen

| Bedingung | Ergebnis |
|---|---|
| 62 von 63 Arten stehen | ja, nur die Pechgrube fehlt (kein Boden auf der Karte) |
| Alle Arbeitsplätze besetzt | ja, 36 (34 plus Zusatzbauten) |
| Mindestens 1 Jahreswechsel | 6 |
| Tempo-40-Jahr ohne fehlenden Takt | ja |
| Kein Tempoabzug, jede Stufe gemessen | ja |
| Frist 10 Minuten | 8 Minuten 37 Sekunden |

## Gesamtproben

| Probe | Ergebnis | Aussage |
|---|---|---|
| A1 | widerlegt | 1.483 Felder außerhalb der Liste: 859 Technik (Uhr, Ansicht), 624 Spielfelder. Liste: `feldluecken_lauf_f.csv` |
| A2 | gemessen | 1.482 von 2.694 Feldern nie geändert. Restliste für K und S: `nie_gesehen_lauf_f.csv` |
| A3 | bestätigt | Tempo 40: 107.234 Rahmen rein. Grenze: "rein" heißt, der Taktzähler ist vor und nach dem Lesen gleich |
| A4 | bestätigt | Tabelle oben, im vollen Dorf. Das leere Spiel und die Massenschlacht fehlen noch |
| A7 | bestätigt | 19.208 Zufallszahlen passen zur Tabelle |
| A8 | bestätigt im Umfang | 273 von 273 Änderungen fallen mit einer möglichen Ursache zusammen, zeitlich zugeordnet. Das Werkzeug im Lauf meldete 6 ohne Ursache: alle Mehl, im selben Takt bekam jedes Mal der Müller oder Bäcker einen neuen Weg |
| A9 | bestätigt | 173 gesendete Befehle laut Log, 173 neue Plätze im Ring, je Art gleich |
| A10 | bestätigt | 7.565 Platzwechsel ohne Verstoß, Einheiten-Platz 0 zählt nicht |
| A12 | gemessen | `DAT_CurrentUnitSlotID` wechselte 5 Mal am Taktende |
| A13 | gemessen | `currentGameMode` 0, `gameMode_2` 2 |

## Einzelpunkte (241)

| Urteil | Punkte |
|---|---|
| bestätigt | 74 |
| widerlegt | 7 |
| gemessen | 67 |
| gesehen, nicht nachgerechnet | 27 |
| Lage fehlte, geht an Lauf K oder S | 58 |
| offen | 8 |

Einzeln mit Beleg: `Punkte_Lauf_F.md`. Bestätigtes und Widerlegtes steht als `live_ergebnis` im Funktionswissen.

## Funde

- **Zuzugsuhr:** `vclock` ist nicht die Beliebtheit. Sie läuft von 2000 bis 4000, je Takt um `gathering_rate`/4. Über 4000 kommt ein Bewohner und sie fällt um 2000. Also 1 Bewohner je 8000/`gathering_rate` Takte: 250 bei Beliebtheit 85 bis 89, 222 bei 90 bis 94, 200 ab 95. Das passt zu allen drei Messungen.
- **Handel:** Kauf aller Waren -3.420 Gold, Verkauf +1.610 Gold, beides auf das Gold genau wie die Tabelle. Verkaufsmenge: unter 50 Stück 5, unter 100 Stück 10, unter 200 Stück 20, sonst 50.
- **Anwerben:** 18 Einheiten kosteten -850 Gold, genau die Summe der Liga-Tabelle.
- **Steuer:** je Woche Leute x Gold-Tabelle x 2,5 aufs Sammelfeld, je Monat ein Zehntel aufs Gold. In 3 von 3 Monaten stimmte es genau.
- **Abreißen:** Mit Param1 50 kommt genau die Hälfte zurück.
- **Falsche Erwartungen aus dem Funktionswissen:** 4 Pechgräben kosten 2 Pech statt 1. `commandDelay` ist im Einzelspiel 0 statt 35. Bier füllt 120 Humpen statt 160 (Liga). `countSlingers2` zählt keine Schleuderer, sondern seit Takt 16.541 je Takt +1. Hopfenbauer tragen bis 6 statt 1. `storageMarketFailState` bleibt bei Befehl 38 auf 0.
- **Tor:** Zustand 10 und 11 werden nach dem Umschalten zu 12. Die beiden gemeldeten "Schaltungen ohne Wirkung" waren meine falsche Erwartung, das Werkzeug ist berichtigt.

## Grenzen

- **Warenketten:** Das gemessene Ende wurde nicht erreicht. Neue Felder kamen noch bei Takt 34.946, der Abschnitt endete an der Obergrenze von 2 Jahren.
- **A4:** nur im vollen Dorf gemessen. Das leere Spiel und die Massenschlacht fehlen.
- **A8:** zeitlich zugeordnet, nicht Stück für Stück.
- **27 Punkte** sind gesehen, aber nicht nachgerechnet, **8** von hier aus nicht zu beantworten.

## Dateien

Hier: Protokoll, Bericht des Werkzeugs, Belege, Rechnungen. Die Aufzeichnungen (rund 1 GB) bleiben lokal in `laeufe/`, `reihen.pkl` auch.
