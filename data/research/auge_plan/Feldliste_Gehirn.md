# Feldliste fürs Gehirn (B-168)

Erzeugt von `feldliste_gehirn.py`, ohne Spielstart. Ganze Liste: `feldliste_gehirn.csv`.

**1219 Felder**, davon 971 fürs Gehirn nutzbar, mindestens für die eigene Seite.

| Bezug | takt | selten | einmal | entbehrlich | ki | zufall | unklar | zusammen |
|---|---|---|---|---|---|---|---|---|
| einheit | 45 | 63 | 11 | 64 | 3 | 0 | 26 | 212 |
| gebaeude | 4 | 75 | 57 | 35 | 1 | 1 | 22 | 195 |
| trupp | 5 | 25 | 8 | 5 | 10 | 0 | 9 | 62 |
| geschoss | 14 | 0 | 10 | 30 | 0 | 0 | 3 | 57 |
| spieler | 1 | 188 | 21 | 30 | 83 | 0 | 57 | 380 |
| kartenfeld | 0 | 14 | 1 | 1 | 0 | 0 | 0 | 16 |
| landschaft | 0 | 10 | 26 | 42 | 0 | 0 | 5 | 83 |
| allgemein | 1 | 57 | 48 | 90 | 0 | 0 | 18 | 214 |
| **alle** | 70 | 432 | 182 | 297 | 97 | 1 | 140 | 1219 |

- **takt:** jeden Takt nötig. **selten:** bei Änderung oder alle paar Takte. **einmal:** beim Entstehen oder zum Partiestart.
- **entbehrlich:** nur Bild, Hilfswert der Engine oder ableitbar. **ki, zufall:** fürs Gehirn gesperrt. **unklar:** ungenutzt, bis geklärt.

## Was jeden Takt ankommt (Kern 21, Aufbau 5, B-169; im Spiel bei Tempo 200 geprueft, siehe kern_felder_1108c_200.json)

| Bezug | takt-Felder | liest der Kern | kommt bei Python an | steckt drin | fehlt |
|---|---|---|---|---|---|
| einheit | 45 | 41 | 39 | 6 | 0 |
| gebaeude | 4 | 4 | 3 | 1 | 0 |
| trupp | 5 | 5 | 5 | 0 | 0 |
| geschoss | 14 | 14 | 14 | 0 | 0 |
| spieler | 1 | 1 | 1 | 0 | 0 |
| allgemein | 1 | 0 | 0 | 1 | 0 |
| **alle** | 70 | 65 | 62 | 8 | 0 |

Von den 614 Feldern für selten und einmal liest der Kern 18, bei Python kommen 7 an.

### Fehlende takt-Felder

Keine.

Ob ein Feld auch für fremde Einheiten gelesen werden darf, steht in der Spalte `fremd`. Die neuen Felder schwärzt der Kern für Fremde. Noch ungefiltert an Python gehen die sieben alten Felder Laufziel x und y, Gruppe, Zielart, Zieleinheit, Zielgebäude und Nahziel; die Sperre dafür kommt mit dem Gehirn (B-152).

## Sichtschranke

Die Spalten `eigen` und `fremd` kommen aus `sichtschranke.csv`. Was nach dieser Liste dort korrigiert wurde, steht Feld für Feld in `sichtschranke_zweifel.md`.

## Gegenprobe

Zweiter Weg, unabhängig von der Namensliste: Messung aus Lauf F und K (nie geändert) und die schreibenden Funktionen.

- takt, aber nie geändert: **0**. takt, aber nur beim Anlegen geschrieben: **0**.
- einmal, aber auch im Lauf geschrieben: 35, einzeln durchgesehen: Besitzerwechsel beim Tod eines Spielers, Werte je Schuss und Werte beim Bau.
- selten, aber nur beim Anlegen geschrieben: 44, fast alle Eingänge von Gebäuden: Sie entstehen, wenn gebaut wird.
- ki, aber auch im Lauf geschrieben: 39. Schreiber ist meist `updateUnits` oder eine andere Sammelfunktion. 17 der Spieler-Felder liest auch Code außerhalb der KI, zum Beispiel `enemies` und `totalEnemyTroopValue`; sie lassen sich aus sichtbaren Einheiten und Teams selbst rechnen.

## Grenzen

- **Belegt** ist, welche Felder sich in Lauf F und K nie änderten und welche Funktionen schreiben.
- **Einschätzung** ist die Trennung von takt und selten: Wie oft sich jedes Feld ändert, ist nicht gemessen, die Rohaufzeichnungen liegen auf dem anderen PC.
- **Einschätzung** ist auch entbehrlich. Es heißt nicht unsichtbar, sondern nur: nicht jeden Takt liefern.
- **Offen:** 140 unklare Felder hier und die reinen Platzhalter, die gar nicht in dieser Liste stehen.
