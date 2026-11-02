# Plan: Lauf F neu (B-142)

Erstellt 02.11.2026 19:57 von SRE, nach Daniels "Ja, so bauen". Grundlage: `data/research/auge_plan/ursachen_lauf_f/Ursachen_Lauf_F.md`. Gebaut wird neu, nicht geflickt.

## Frage des Laufs

Sieht das Auge alles, was im friedlichen Spiel passiert, ohne das Spiel zu bremsen?

## Abschnitte

| # | Abschnitt | Wirkung, die geprüft wird | Grenze in Takten | Grund |
|---|---|---|---|---|
| 1 | Gold, Burg, Kornspeicher, 6 Hütten, 3 Lager, Waffenlager, Startwaren | Anzeige 20 aus, Woche zählt, Startwaren eingebucht, Deckel mindestens 58 | 200 + Ablesefehler; 4 je Stück + 20 | 1 Woche = 200 (gemessen); `UpdateStockpile` bucht 1 Stück je 4 Takte |
| 2 | Alle übrigen Arten plus wenige Zusatzbauten, Waren nachfüllen | Eintrag im Speicher mit richtigem Bildwert, je Art bis 3 Stellen | 20 je Bau | gemessen 2 bis 6 |
| 3 | Bauern kommen | `currentlyNeededEmployeeCount` überall 0 | Arbeitsplätze × 250 | gemessen 1 Bewohner je 250 Takte |
| 4 | Handel, Steuern, Rationen, Mauer, Graben, Tore, Schlafen, Abreißen, Anwerben, zweite Kaserne | je Schritt Soll gegen Ist | je Einstellung 200 | die Beliebtheit rechnet wöchentlich |
| 5 | Warenketten | neue Felder der Feldliste | mindestens 1 Jahr ohne neues Feld, höchstens 19.200 | 1 Jahr = 9.600 ist der längste Kalenderkreis |
| 6 | Ein Jahr auf Tempo 40 | Kein Takt fehlt, kein jeden Takt gelesener Bereich gemischt | 9.600 | 40 ist die höchste Stufe mit jedem Takt (201 von 201) |
| 7 | Tempotreppe im vollen Spiel | Kein Abzug, zu wenige Takte heißt "nicht gemessen" | 20 auf Stufe 1, 100 auf Stufe 10, sonst 1.000; je Stufe ohne, mit, ohne | Ablesefehler 4 Takte, also bei 1.000 Takten 0,4 % |

Dazu zweimal eine kurze Bremsprobe (Stufe 1000, ohne, mit, ohne), einmal nach den Bauern und einmal nach den Warenketten.

## Änderungen gegenüber der Erklärung an Daniel, mit Grund

1. **Keine Pause für den Bauplan.** Je Art wird vor dem Bau ein kleines Fenster geprüft (bis 25 × 25 Felder), das kostet Millisekunden. Das Spiel muss dafür nicht anhalten. Vorteil: Daniels Vorgabe "Bauen darf das Tempo nicht herausnehmen" gilt ohne Ausnahme.
2. **Gemischte Schnappschüsse:** Abbruch nur bei Bereichen, die jeden Takt gelesen werden. Gemessen im letzten Lauf: Der einzige gemischte Rahmen auf Tempo 40 war der Datenblock (8,2 ms Lesezeit), der nur alle 250 Takte für den Änderungsmelder gelesen wird.
3. **Warteschlange voll:** Abbruch nur auf Tempo 40. Auf Stufe 1000 ist sie der normale Grund, warum nur rund 27 % der Takte gelesen werden, das hat Daniel freigegeben.
4. **Einzelne Schaltung ohne Wirkung** (Abschnitt 4) ist ein Fund und beendet den Lauf nicht. Abbruch nur, wenn die Grundlage kaputt ist.
5. **Bremsprobe:** Zeigt sie einen Abzug, wird sie einmal wiederholt, erst der zweite Abzug bricht ab. Ein einzelner Ruckler des Rechners ist kein Bremsen durch das Lesen (Daniel 22.10.: Auslöser nicht streng gegen laufende Arbeit).
6. **Kein neuer Bewohner:** Abbruch nur, solange Arbeitsplätze offen sind, und nur bis zum Ende des Abschnitts Bauern. Die Rate 1 je 250 Takte ist nur bei Beliebtheit 87,75 gemessen, und danach braucht der Lauf keine neuen Leute mehr. Ob am Ende alle Plätze besetzt sind, sagt die Schlussprüfung. Die alte Fassung hätte auch mit besetzten Plätzen abgebrochen, obwohl die Bevölkerung bei 21 bis 23 Wartenden am Feuer gemessen nur in 306 von 2.144 Schritten stieg (Wissensstand 13v).
7. **Einzelpunkte:** Das Werkzeug sagt "Zahl passt" oder "Zahl weicht ab", nicht bestätigt oder widerlegt. Es sieht Feldwerte, nicht die Lage des Punkts: In der Probe nannte es "Goldzuwachs je Takt 80" widerlegt, weil es die 80 im Goldbestand suchte.
8. **A10:** Einheiten-Platz 0 zählt nicht mit. `setDestinationForUnit` und `computeLadderClimbPath` kopieren die Einheit vor der Wegsuche dorthin.

## Abbruch

Frist 10 Minuten, von Hand gestoppt, Spiel weg, Aufzeichnung weg, 1 s kein Takt (auf langsamen Stufen 10 Takt-Abstände), Gold kommt nicht an, Anzeige 20 bleibt, Woche zählt nicht, erlaubte Stelle ohne Gebäude an 3 Stellen, Art ohne Stelle (außer Pechgrube), Startwaren hängen, Deckel zu klein, 1.000 Takte kein neuer Bewohner trotz Platz und offener Arbeit (nur bis zum Ende der Bauern), Beliebtheit unter 50 (außer im Steuertest), zweimal Abzug in der Bremsprobe, auf Tempo 40 Takt fehlt oder gemischt.

**Nach jedem Ende:** Spiel anhalten, zweimal lesen, dass der Takt steht, dann Aufzeichnung beenden, erst dann die Sperre frei. Die Reihenfolge hat einen Grund: Das Beenden der Aufzeichnung kann dauern oder scheitern, das Spiel darf dabei nicht weiterlaufen. Kein zweiter Lauf von selbst.

## Erfolg

62 von 63 Arten stehen (ohne Pechgrube), alle Arbeitsplätze besetzt, mindestens 1 Jahreswechsel, Tempo-40-Jahr ohne fehlenden Takt, Tempotreppe ohne Abzug und jede Stufe gemessen.

## Waren: was, wie viel, warum

- **Lagerwaren:** je ein volles Lagerfeld laut `StorageLimitResourceTypeArray`: Hopfen 16, Stein 48, Eisen 48, Pech 16, Weizen 32, Bier 16, Mehl 32. Holz 96, weil die Karte nur 50 mitbringt und die Bauten Holz kosten.
- **Essen:** Der Kornspeicher fasst 250. Die Karte bringt 20 Äpfel. Dazu Brot, Käse, Fleisch je 60, Äpfel 40. Fällt das Essen unter 100, kommen 100 Äpfel nach, weil Essen hier nicht die Prüffrage ist. Jede Nachlieferung steht im Protokoll und zählt in A8 als Eingang.
- **Waffen:** je 20, für das Anwerben.
- **Weg:** `startResources` (+0x46C), nie `currentResources`. Gold direkt (das Spiel lässt es beim Nachzählen stehen).

## Werkzeuge

- `auge_aufzeichnung.py`: alles in Takten, Modus `--streng`, Aussetzen für die Bremsprobe, Feld-Wache für das gemessene Ende.
- `auge_lauf_f.py`: neu, liest den Zustand direkt aus dem Speicher statt über den Kanal.
- `auge_auswertung.py`: Stufe mit zu wenig Takten ist "nicht gemessen", A3 streng nur für jeden Takt gelesene Bereiche, A8 neu.
- `auge_punkte.py`: neu, Beleg je Einzelpunkt aus der Aufzeichnung, Urteil wo es sich rechnen lässt.
- `auge_ergebnis.py`: neu, alles zusammen nach dem Lauf.

## Trockenlauf

1. Das ganze Programm gegen ein künstliches Spiel, Erfolg und jeder Abbruchgrund, mit Negativlauf.
2. `pruefen` und `trocken` am echten Spiel: Module, Felder, Bauplan für alle Arten am aktuellen Spielstand, ohne zu bauen.
3. Auswertung an der Aufzeichnung des letzten Laufs.
4. Kurze Messprobe auf Tempo 40 im strengen Modus.

Der echte Lauf startet erst nach Ansage und Daniels Ja.
