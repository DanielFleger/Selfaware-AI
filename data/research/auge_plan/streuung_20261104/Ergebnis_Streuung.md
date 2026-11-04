# Streuung: Wohin Geschosse und Feuer gehen

B-142, 04.11.2026. Auftrag Daniel: „Das spiel wirkt teilweise zufällig wo projektile bzw. feuer geht … wäre das eine goldgrube“, dann „Ja, entziffern“.

**Ergebnis:** Der Zufall ist eine feste Tabelle aus 20.000 Zahlen, die das Spiel der Reihe nach verbraucht. Zielpunkt, Flug, Einschlag und Opfer folgen aus ihr und aus dem Spielstand. Der Nachbau sagt 1.977 geprüfte Schussenden ohne Abweichung voraus, auf Takt, Mikrofeld und Opfer.

8 Mikro sind 1 Feld. Alle Zahlen gelten für Instanz 2 mit aktiver Liga (`liga_ai.json`, SHA-256 beginnt 205bf2841888).

## Wie das belegt ist

| Prüfung | Umfang | Ergebnis | Beleg |
|---|---|---|---|
| Zielfunktionen direkt im Spiel gerufen, Zufallszahl vorgegeben | 83.840 Aufrufe, 11 Schützenarten, 8 Blickrichtungen | 0 Abweichungen | `streuung_rufen.txt` |
| Gegenprobe dazu: Modell bekommt die falsche Zufallszahl | 8.384 Aufrufe | 4.311 weichen ab, der Test schlägt also an | `streuung_gegenprobe.txt` |
| Tempo und Winkel beim Abschuss | 3.050 Schüsse aus Lauf S | alle gleich | `flug_pruefung.txt` |
| Flug Takt für Takt, Ort und Höhe | 47.859 Takte | 47.858 gleich. Der eine Rest und 5 weitere Flüge hängen an Rahmen 7809319 der Szene streuung, der noch den Takt davor zeigt: ein Fehler der Aufnahme, nicht des Spiels | `flug_pruefung.txt` |
| Ende des Flugs: Takt, Mikrofeld, Opfer verliert Leben | 1.977 Flüge | 0 falsch | `flug_pruefung.txt` |
| Zielpunkt gegen die Zufallszahlen des Takts | 2.434 Schüsse | 2.433 passen. Der eine Rest ist ein Brandpfeil auf Pech (Zielart 34), der ohne Streuung fliegt (Code) | `ziel_pruefung.txt` |
| Feuerschaden je Takt | 10.232 und 1.017 Einheit-Takte auf Feuerfeldern | 1 Takt ohne Verlust, nicht weiter untersucht | `feuer_pruefung.txt`, `feuer_pruefung_streuung.txt` |
| Tests mit 13 eingebauten Fehlern | 57 Tests gegen echte Spielwerte | 13 von 13 rot | `tests/test_streuung.py`, `lauf_negativ.py St:` |

**Nicht geprüft:** 734 Flüge aus Aufnahmen ohne jeden Takt, 315 Flüge, die bei Aufnahmeende noch flogen, 24 Flüge mit Abpraller (Richtung nicht nachgebaut, siehe unten). Die Szenen liegen auf einer fast ebenen Karte, Hügel und Bäume kommen nur als Einzelfälle vor.

Eine eigene Szene `streuung` (jeder Takt, 497 Schüsse, `lauf_s_20261104_215808_streuung.auge`, bleibt lokal) schloss die Lücke bei den Belagerungsgeräten und den Schüssen auf den Boden.

## 1. Worauf gezielt wird

**Schuss auf eine Einheit** (Bogenschütze E_ARCHER 22, Armbrustschütze E_XBOW 23, arabischer Bogenschütze A_ARCHER 70, Schleuderer A_SLINGER 72, Berittener Bogenschütze A_HARCHER 74, Feuerwerfer A_FIRETHROWER 76, Feuerballiste S_FBALLISTA 77):

- Zielpunkt ist die **Feldmitte** des Ziels, nicht die Einheit selbst.
- Läuft das Ziel, kommt ein **Vorhalt** in seiner Blickrichtung dazu: Sichtlänge × 133 / 100, geteilt durch 16 × Lauftempo.
- Zielhöhe: Boden des Ziels plus 30, beim Feuerwerfer plus 0.
- **Streuung nur nach oben:** Steht das Ziel höher als der Boden unter dem Schützen, streut der Schuss mit der Chance Höhenunterschied / 300 (ab 75 Höhe das 1,5-fache, Deckel 280). Auf gleicher Höhe oder nach unten fliegt er genau.

| Höhenunterschied | gleich | 10 | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|---|
| Chance auf Streuung | 0 % | 3 % | 10 % | 20 % | 50 % | 75 % |

Streut er, gilt: 2 von 8 Fällen seitlich und längs bis Stufe / 8 Mikro, 4 von 8 Höhe um 20 und mehr daneben, 2 von 8 Höhe um 40 und mehr zu hoch.

**Sicht verdeckt:** Hat der Schütze keine freie Linie, nimmt `acquireShootTarget` die Stelle des Gegners als Ziel (Zielnummer -2) und schießt mit Bodenweg und hoher Bahn. Er trifft also nur noch zufällig. **Mangonel und Ballista zielen immer so**, sie treffen, wo der Gegner beim Zielen stand.

**Bodenweg** (Bodenbefehl, verdeckte Sicht, und jedes Katapult, Trebuchet, Mangonel, Ballista): erst die Streuung der Tabelle, dann dieselbe zweite Stufe wie oben. Der Schuss zieht dabei zwei Zufallszahlen, wenn die zweite Stufe greift.

| Waffe | längs in Mikro (minus = zu weit) | quer | Höhe | Besonderheit |
|---|---|---|---|---|
| Bogen, Armbrust, Schleuder, Feuerwerfer, Feuerballiste am Boden | -48 bis 47 | -40 bis 39 | -40 bis 39 | |
| Katapult S_CATAPULT 39 | -96 bis 31 | -48 bis 47 | -48 bis 15 | im Mittel 4 Felder **zu weit** |
| Trebuchet S_TREBUCHET 40 | 3 von 4 Schüssen 0, sonst -48 bis 47 | -48 bis 47 | -16 bis 15 | genau in der Länge |
| Mangonel S_MANGONEL 41 | -112 bis 111 | -64 bis 63 | -64 bis 63 | **7 Steine, jeder startet am Punkt des vorigen** |
| Ballista S_BALLISTA 61 am Boden | -24 bis 7 | -20 bis 19 | -20 bis 19 | auf eine Stelle mit Gegner: 0, genau |

Liegt der Punkt näher als die halbe Länge, halbieren sich längs und quer. Vor jedem Schuss steht der Ausgangspunkt wieder auf dem befohlenen Feld, Streuung summiert sich also nur innerhalb einer Mangonel-Salve.

**Wo es wirklich landet** (gerechnet mit dem geprüften Nachbau, ebener Boden, jede 10. Tabellenzahl, `verteilung.txt`):

| Waffe, 20 Felder Abstand | im befohlenen Feld | bis 1 Feld | bis 2 | bis 4 | bis 8 | Mittel längs | Mittel quer |
|---|---|---|---|---|---|---|---|
| Bogenschütze | 0 % | 3 % | 14 % | 49 % | 99 % | +2,1 | 2,6 |
| Armbrustschütze | 1 % | 6 % | 20 % | 60 % | 100 % | +0,7 | 2,4 |
| Katapult | 0 % | 3 % | 8 % | 35 % | 75 % | +5,0 | 3,4 |
| Trebuchet | 1 % | 14 % | 26 % | 67 % | 100 % | 0 | 3,2 |
| Mangonel, je Stein | 0 % | 1 % | 3 % | 10 % | 34 % | +6,0 | 8,3 |
| Ballista | 0 % | 15 % | 72 % | 85 % | 100 % | +2,1 | 1,4 |

## 2. Der Flug

Geschosse fliegen eine echte Wurfbahn, ohne Zufall:

- Strecke nach t: `Tempo × cos(Winkel) × t / 4` Schritte auf der Linie zum Ziel, Höhe `2 × (Tempo × sin(Winkel) × t - 4,906 × t²)`. Je Takt wächst t um den Zeitschritt der Art.
- Winkel oder Tempo rechnet das Spiel so, dass die Bahn genau den Zielpunkt trifft. Pfeil, Bolzen, Stein, Feuer und Ballista haben festes Tempo und rechnen den Winkel; Katapult, Trebuchet, Mangonel haben festen Winkel und rechnen das Tempo.

| Geschoss | Tempo | Zeitschritt | Schritte je Takt längs |
|---|---|---|---|
| Pfeil | 125 | 0,18 | 5,6 |
| Bolzen | 125 | 0,20 | 6,25 |
| Stein der Schleuder | 100 | 0,20 | 5 |
| Feuer | 80 | 0,20 | 4 |
| Bolzen der Ballista | 170 | 0,18 | 7,65 |
| Bolzen der Feuerballiste | 125 | 0,18 | 5,6 |
| Bodenschuss Pfeil, Bolzen, Stein, Feuer | 81, 81, 70, 60 (ab 150 Mikro 125) | 0,14 bis 0,16 | |

## 3. Wen es trifft

**Ein Schuss hat kein festes Opfer.** Bei jedem Mikroschritt prüft das Spiel alle Einheiten auf dem Feld, auf dem das Geschoss gerade ist. Getroffen wird die erste in der Liste des Felds, wenn sie:

- nicht der Schütze ist, nicht stirbt und nicht zum eigenen Team gehört (Tiere zählen als Gegner),
- und die Geschosshöhe zwischen ihrem Boden und Boden + 42 liegt. Als Ziel haben Trebuchet und Belagerungsturm 80, Schild 90, Katapult 50, Ramme 40, Mangonel 70 (Code, in den Aufnahmen trafen nur die 42 zu).

Gemessen: 1.321 Treffer am anvisierten Ziel, 47 an einem anderen Feind, 4 an Tieren. Die Einheit bewegt sich im Takt vor dem Geschoss; wer im selben Takt schon von einem anderen Geschoss getötet wurde, fängt nichts mehr.

**Darum wirkt es zufällig:** Pfeile treffen, was im Weg steht, und fliegen über alles andere hinweg. Wo das ist, steht fest (`gefahr_tabelle.txt`, ebener Boden):

| Abstand | Pfeil höchster Punkt | Über diesen Feldern fliegt er zu hoch zum Treffen |
|---|---|---|
| bis 8 Felder | bis 42 | keine: Er trifft jeden im Weg |
| 10 | 47 | Feld 2 bis 8 |
| 15 | 68 | Feld 1 bis 13 |
| 20 | 98 | Feld 1 bis 19 |
| 30 | 182 | Feld 0 bis 28 |

Feuer der Feuerwerfer trifft niemanden direkt, es zündet beim Aufkommen.

## 4. Mauern und Gebäude

- In der ersten Hälfte des Flugs kommt ein Pfeil weder am Boden noch an einer Mauer auf (Code; Einheiten trifft er auch dort).
- Trifft er ein Mauerfeld, prallt er ab: Tempo durch 8, neue Richtung. 24 solche Flüge, alle ohne Treffer danach (`flug_pruefung.txt`). Unter Tempo 80 zählen Einheiten für ein Geschoss nicht mehr (Code).
- An einem Gebäude endet der Flug dort, gemessen auf Takt und Ort bei 15 Flügen.
- Auf Türmen steigt die Aufschlaghöhe bei der Hälfte der Geschosse um 20 (Code, nicht gemessen).

## 5. Feuer

- **Aufkommen:** Eine Flamme des Feuerwerfers landet nach dem Flug oben genau und legt **ein** Feuer an Landepunkt plus Versatz aus einer Tabelle mit 64 Einträgen. Sie liegt auf vier Linien (längs, quer, zwei Diagonalen), höchstens 8 Mikro weit. Von der Feldmitte aus bleiben 31 von 64 auf dem Feld, der Rest geht auf ein Nachbarfeld. Brennt es dort schon, entsteht kein neues Feuer, das alte fängt von vorn an.
- **Ausbreitung ohne Zufall in der Richtung:** Ein Feuer der Stufe 2 oder mehr zündet nacheinander die 4 Nachbarn an (x-1, x+1, y+1, y-1), die meisten 6 bis 15 Takte nach seinem Entstehen, weitere nach einem Neuanfang. Das neue Feuer hat Stufe minus 1, und auch dort kommt der Tabellen-Versatz dazu. Stufe 1 breitet sich nicht weiter aus. Einen Nachbarn mit über 24 Höhenunterschied lässt es aus (Code). 370 neue Feuer der Stufe 1 geprüft, alle haben ein passendes Elternfeuer.
- **Schaden, ohne Zufall:** Jede Einheit auf dem Feuerfeld verliert **jeden Takt** Leben.

| Einheit | Flamme des Feuerwerfers | Brand eines Gebäudes |
|---|---|---|
| alle anderen | 37 | 75 |
| Lord UT_LORD 55 | 12 | 25 |
| Feuerwerfer A_FIRETHROWER 76 | 5 | 10 |
| Feuerwehr UT_FIREFIGHTER 53 | 0 | 1 |

Gemessen sind 37, 5 und 75, die übrigen stehen in der Tabelle im Speicher (`tabellen.txt`).

Im ersten Takt eines neuen Feuers kommt der volle Wert dazu: 75 oder 112 (75 + 37) statt 37, weil die erste Runde vor dem Setzen der Stärke läuft (Code). **Das berichtigt meine Aussage vom 03.11.**, „mehrere Flammen addieren sich (37, 75, 112)“: Alle 8 Fälle mit 75 und die 11 mit 112 liegen im ersten Takt eines Feuers.

- **Die offenen Feuerschüsse sind erklärt** (82 Schüsse, Szene Beschuss): 56 Felder brannten schon, darum kam der Verlust vor der Landung. 22 neu entzündet, Verlust im selben Takt. Bei 2 war das Ziel schon tot. Bei 2 landete das Feuer durch den Versatz auf dem Nachbarfeld, das Zielfeld brannte 60 Takte nicht.
- **Gebäude:** Ein Feuer auf einem brennbaren Bau zündet ihn an. Hütten: 200 Leben, alle 20 Takte minus 4, also rund 1.000 Takte Brand (gemessen an 3 Hütten: 968, 983, 1.001). Nachbarhütten fingen 7 und 285 Takte später Feuer. Ein neuer Bau brennt nicht, solange sein Abkühlzähler läuft (Code; in der Szene 279 Takte Rest).
- **Bäume:** Ein Feuer auf einem Baum entzündet Felder im Umkreis (Code, in der Szene nicht vorgekommen).

## 6. Der Zufall

Das Spiel hat zwei Zeiger auf **dieselbe** Tabelle. Der Spielstrom (`nextRandomNumber2`) entscheidet Streuung, Feuer-Versatz, Ausbreitung; er läuft festgelegt mit, Lauf K hat das bestätigt. Der erste Strom (`nextRandomNumber1`) hängt an der echten Zeit und bestimmt nur Ton und Bild. Ein Schuss auf den Boden verbraucht 1 oder 2 Zahlen, dazu 1 beim Erzeugen des Geschosses. In der Szene streuung flossen je Takt 2 bis 49 Zahlen, im Mittel 3,8, auch aus anderen Quellen. Der Zeiger sagt den nächsten Schuss darum nur, wenn man auch alles andere im Takt mitrechnet.

## 7. Was das für SamurAI heißt

**Fair nutzbar, ohne verborgenes Wissen:**

- Fläche planen statt Punkt: Die Tabellen oben sagen je Waffe, wie weit es streut.
- Bogenschützen schießen auf gleicher Höhe genau. Wer nicht das Ziel ist, wird nur getroffen, wenn er im Weg steht und die Bahn dort niedrig genug ist.
- Unter der Bahn laufen: Ab 10 Feldern Abstand trifft ein Pfeil auf dem Weg fast niemanden. Die Gefahr liegt beim Schützen und beim Ziel.
- Vorne stehen schützt: Auf kurzem Abstand fängt die erste Reihe die Pfeile ab.
- Feuer weicht man aus, indem man das Feld wechselt: Der Verlust hängt am Feld, nicht an der Flamme.
- Katapulte zielen im Mittel 4 Felder zu weit, also davor anlegen.
- Mangonel: Sieben Steine wandern, die Salve streut stark.

**Daniels Schalter, nicht von mir entschieden:** Den Stand des Zufallszeigers auslesen und damit den nächsten Einschlag vorhersagen wäre verborgenes Wissen. Das Wissen steht hier im Register, der faire Spielweg nutzt es nicht, bis Daniel anders entscheidet.

## Noch offen

- Richtung beim Abprall ist nicht nachgebaut. Das Spiel zeigt: danach kein Treffer.
- Treffer auf Nachbarfeldern bei großen Geräten: im Code gelesen (Feld 0x90 der Einheit), nicht nachgebaut, in den Aufnahmen nicht aufgefallen.
- Katapult und Trebuchet treffen laut Code auch Freunde, außer Schild, Turm, Ramme. Die Szene stellte Freunde daneben, es kam kein Fall.
- Schütze auf einem Turm: Verglichen wird mit dem Boden unter ihm (Feld `terrainOrClimbHeight`). Was dort beim Turm drinsteht, ist nicht gemessen.
- Brandpfeile vom Feuerkorb: nur im Code gelesen.

## Dateien

Alle unter `data/research/auge_plan/streuung_20261104/`: `flug_modell.py`, `streuung_modell.py` (die Regeln als Rechnung), `flug_pruefen.py`, `ziel_pruefen.py`, `feuer_pruefen.py`, `brand_pruefen.py`, `streuung_rufen.py`, `verteilung.py`, `gefahr_tabelle.py`, je mit Ausgabe `.txt`. Festwerte für die Tests: `streuung_beispiele.json`, `flug_beispiele.json`. Szene: `streuung` in `auge_lauf_s.py`.
