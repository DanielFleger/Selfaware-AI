# Streuung: Wohin Geschosse und Feuer gehen

B-142, 04.11.2026. Auftrag Daniel: „Das spiel wirkt teilweise zufällig wo projektile bzw. feuer geht … wäre das eine goldgrube“, dann „Ja, entziffern“.

**Ergebnis:** Der Zufall ist eine feste Tabelle aus 20.000 Zahlen, die das Spiel der Reihe nach verbraucht. Zielpunkt, Flug, Einschlag und Opfer folgen aus ihr und aus dem Spielstand. Der Nachbau sagt 2.724 geprüfte Schussenden ohne Abweichung voraus, auf Takt, Mikrofeld und Opfer.

8 Mikro sind 1 Feld. Alle Zahlen gelten für Instanz 2 mit aktiver Liga (`liga_ai.json`, SHA-256 beginnt 205bf2841888).

## Wie das belegt ist

| Prüfung | Umfang | Ergebnis | Beleg |
|---|---|---|---|
| Zielfunktionen direkt im Spiel gerufen, Zufallszahl vorgegeben | 83.840 Aufrufe, 11 Schützenarten, 8 Blickrichtungen | 0 Abweichungen | `streuung_rufen.txt` |
| Gegenprobe dazu: Modell bekommt die falsche Zufallszahl | 8.384 Aufrufe | 4.311 weichen ab, der Test schlägt also an | `streuung_gegenprobe.txt` |
| Trefferfenster und Teamregel direkt gerufen | 150 Aufrufe, 10 Zielarten | 0 Abweichungen | `fenster_rufen.txt` |
| Tempo und Winkel beim Abschuss | 3.784 Schüsse aus Lauf S | alle gleich | `flug_pruefung.txt` |
| Flug Takt für Takt, Ort und Höhe, auch nach dem Abprall | 80.770 Takte | 80.768 gleich. Die 2 Reste und 9 weitere Stellen hängen an Rahmen, die noch den Takt davor zeigen, vor allem 7809319 der Szene streuung: ein Fehler der Aufnahme, nicht des Spiels | `flug_pruefung.txt` |
| Ende des Flugs: Takt, Mikrofeld, Opfer verliert Leben | 2.724 Flüge | 0 falsch | `flug_pruefung.txt` |
| Zielpunkt gegen die Zufallszahlen des Takts | 3.170 Schüsse | alle passen, 2 davon sind Brandpfeile auf Pech ohne Streuung | `ziel_pruefung.txt` |
| Feuerschaden je Takt | 10.232 und 1.017 Einheit-Takte auf Feuerfeldern | 1 Takt ohne Verlust, nicht weiter untersucht | `feuer_pruefung.txt`, `feuer_pruefung_streuung.txt` |
| Tests mit 19 eingebauten Fehlern | 91 Tests gegen echte Spielwerte | 19 von 19 rot | `tests/test_streuung.py`, `lauf_negativ.py St:` |

**Nicht geprüft:** 739 Flüge aus Aufnahmen ohne jeden Takt, 321 Flüge, die bei Aufnahmeende noch flogen. Die Szenen liegen auf einer fast ebenen Karte, Hügel kommen nur als Einzelfälle vor.

Eigene Szenen mit jedem Takt schlossen die Lücken (Aufnahmen bleiben lokal): `streuung` (497 Schüsse: Geräte, Boden), `streuung2` (569: Freunde, große Ziele, Mauerecke, Bäume), `streuung3` (145: Schützen auf Mauer und Turm, Korb, Schuss nach oben), `streuung4_g` (9, im Gefecht: Pech).

## 1. Worauf gezielt wird

**Schuss auf eine Einheit** (Bogenschütze E_ARCHER 22, Armbrustschütze E_XBOW 23, arabischer Bogenschütze A_ARCHER 70, Schleuderer A_SLINGER 72, Berittener Bogenschütze A_HARCHER 74, Feuerwerfer A_FIRETHROWER 76, Feuerballiste S_FBALLISTA 77):

- Zielpunkt ist die **Feldmitte** des Ziels, nicht die Einheit selbst.
- Läuft das Ziel, kommt ein **Vorhalt** in seiner Blickrichtung dazu: Sichtlänge × 133 / 100, geteilt durch 16 × Lauftempo.
- Zielhöhe: Boden des Ziels plus 30, beim Feuerwerfer plus 0.
- **Streuung nur nach oben:** Steht das Ziel höher als der Boden unter dem Schützen, streut der Schuss mit der Chance Höhenunterschied / 300 (ab 75 Höhe das 1,5-fache, Deckel 280). Auf gleicher Höhe oder nach unten fliegt er genau.

| Höhenunterschied | gleich | 10 | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|---|
| Chance auf Streuung | 0 % | 3 % | 10 % | 20 % | 50 % | 75 % |

Streut er, gilt: 2 von 8 Fällen seitlich und längs bis Stufe / 8 Mikro, 4 von 8 Höhe um 20 und mehr daneben, 2 von 8 Höhe um 40 und mehr zu hoch. Im echten Flug gemessen: Pikeniere oben auf einer Mauer, 94 Höhe über dem Schützen: Modell 47 %, gemessen 41 % von 70 Schüssen (`oben_pruefung.txt`).

**Nach oben macht ein Schuss nur ein Drittel Schaden:** Pfeil gegen den Pikenier 333 statt 1.000, Stein 250. Das gilt, wenn das Ziel mehr als 30 über dem Abschuss liegt (Code: Ballista die Hälfte, Ingenieur mit Öl ein Zwanzigstel).

**Oben stehen:** Auf der Mauer zählt die Höhe als Gelände (`terrainOrClimbHeight` 98, `buildingHeight` 4, Abschuss auf 132), auf dem Turm als Gebäude (8 und 180, Abschuss auf 218). Die Streu-Stufe vergleicht nur die Geländehöhe: Ein Schütze auf dem Turm zählt dort wie am Boden. Vom Turm und von der Mauer auf den Boden flog jeder Schuss genau (22 und 30 Schüsse).

**Sicht verdeckt:** Hat der Schütze keine freie Linie, nimmt `acquireShootTarget` die Stelle des Gegners als Ziel (Zielnummer -2) und schießt mit Bodenweg und hoher Bahn. Er trifft also nur noch zufällig. **Mangonel und Ballista zielen immer so**, sie treffen, wo der Gegner beim Zielen stand.

**Bodenweg** (Bodenbefehl, verdeckte Sicht, und jedes Katapult, Trebuchet, Mangonel, Ballista): erst die Streuung der Tabelle, dann dieselbe zweite Stufe wie oben. Der Schuss zieht dabei zwei Zufallszahlen, wenn die zweite Stufe greift.

| Waffe | längs in Mikro (minus = zu weit) | quer | Höhe | Besonderheit |
|---|---|---|---|---|
| Bogen, Armbrust, Schleuder, Feuerwerfer, Feuerballiste am Boden | -48 bis 47 | -40 bis 39 | -40 bis 39 | |
| Katapult S_CATAPULT 39 | -96 bis 31 | -48 bis 47 | -48 bis 15 | im Mittel 4 Felder **zu weit** |
| Trebuchet S_TREBUCHET 40 | 3 von 4 Schüssen 0, sonst -48 bis 47 | -48 bis 47 | -16 bis 15 | genau in der Länge |
| Mangonel S_MANGONEL 41 | -112 bis 111 | -64 bis 63 | -64 bis 63 | **7 Steine, jeder startet am Punkt des vorigen** |
| Ballista S_BALLISTA 61 am Boden | -24 bis 7 | -20 bis 19 | -20 bis 19 | auf einen Gegner: in dieser Stufe 0 |

Die zweite Stufe greift bei gleicher Höhe beim Katapult und der Ballista zu 13 %, beim Trebuchet zu 20 %, beim Mangonel zu 23 %. Bei den Schützen hängt sie an der Höhe, die die erste Stufe ausgewürfelt hat. Liegt der Punkt näher als die halbe Länge, halbieren sich längs und quer. Vor jedem Schuss steht der Ausgangspunkt wieder auf dem befohlenen Feld, Streuung summiert sich also nur innerhalb einer Mangonel-Salve.

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

- nicht der Schütze ist und nicht stirbt (Tiere zählen als Gegner),
- und die Geschosshöhe zwischen ihrem Boden und Boden + 42 liegt. Als Ziel haben Trebuchet und Belagerungsturm 80, Schild 90, Katapult 50, Ramme 40, Mangonel 70 (direkt gerufen, alle bestätigt).

**Eigene Leute:** Pfeil, Bolzen, Stein und Ballista fliegen durch. Katapult und Trebuchet treffen sie, außer Schild, Belagerungsturm und Ramme. Das Mangonel trifft sie nur beim menschlichen Spieler. Gemessen: 7 Treffer an eigenen Leuten, 140 Flüge durch einen Freund, dazu 70 Direktaufrufe.

**Große Geräte werden schon vom diagonalen Nachbarfeld getroffen:** Katapult, Trebuchet (dort Fenster 40), Mangonel, Belagerungsturm, Ramme, Schild, Ballista. Die Feuerballiste nicht (Tabelle im Speicher). 17 solche Treffer im Flug, an Ramme und Schild, die anderen Arten nur als Tabelle und im Direktaufruf.

Gemessen: 1.691 Treffer am anvisierten Ziel, 68 an einem anderen Feind, 7 an eigenen Leuten, 4 an Tieren. Die Einheit bewegt sich im Takt vor dem Geschoss; wer im selben Takt schon von einem anderen Geschoss getötet wurde, fängt nichts mehr.

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
- Trifft er ein Mauerfeld, prallt er ab: Tempo durch 8, Winkel wie die Flugrichtung im Moment (höchstens 80 nach unten). Gespiegelt wird die Achse, die im Feld näher am Rand liegt, in der Ecke entscheiden die Nachbarfelder. Danach zählt er keine Einheiten mehr, weil unter Tempo 80 keine geprüft werden, und fällt an der Mauer herunter. 68 solche Flüge aus 7 Richtungen, 7.560 Takte danach gleich.
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
- **Bäume:** Ein Feuer auf einem Baumfeld zündet den Baum an. Kleine Bäume (Art 6, 9, 17) verschwinden einfach. Ein großer Baum (Art 1 bis 4, ab Wachstumsstufe 3) brennt: Im selben Takt entstehen bis zu 8 neue Feuer rundum, Stufe 2 und voller Schaden (gemessen 6), und von dort geht es ein Feld weiter. So wandert ein Waldbrand. Gemessen an 2 großen und 5 kleinen Bäumen (`reste_pruefung.txt`).
- **Feuerkorb und Brandpfeile:** Befehl 69 setzt den Korb auf die hohe Mauer. Ein Schütze auf der Mauer unter 4 Feldern davon schießt Brandpfeile. Sie machen denselben Schaden wie normale (1.000 und 1.500, 29 Treffer) und zündeten die Hütte nicht an (2 Treffer, kein Brand).
- **Pech:** Mit Korb daneben zündet Anweisung 34 den Graben im Gefecht an. Der Brandpfeil fliegt ohne Streuung genau aufs Feld, ein Schuss reicht. Es entstehen Feuer der Stufe 3 mit vollem Schaden, 31 Feuer in dieser Probe. Eine Einheit auf dem Graben verlor 75 je Takt, 610 Takte lang, bis die Aufnahme endete (`pech_pruefung.txt`). Ohne Korb fliegen nur normale Pfeile (Lauf S, 03.11.). Im Editor hat der Graben keinen Besitzer, dort ging es nicht.

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
- Nach oben schießen lohnt kaum: ein Drittel Schaden und Streuung. Wer oben steht, trifft genau und mit vollem Schaden.
- Eigene Leute nicht ins Ziel von Katapult und Trebuchet stellen. Schild, Turm und Ramme dürfen dort stehen.
- Brandpfeile bringen keinen Schaden mehr. Der Korb lohnt nur für Pech.
- Ein Feuer zwischen großen Bäumen breitet sich viel weiter aus als auf freiem Feld.

**Daniels Schalter, nicht von mir entschieden:** Den Stand des Zufallszeigers auslesen und damit den nächsten Einschlag vorhersagen wäre verborgenes Wissen. Das Wissen steht hier im Register, der faire Spielweg nutzt es nicht, bis Daniel anders entscheidet.

## Feuerkorb: Wo er steht und was er kostet (P312)

Szene `korb_g`, jedes Feld einzeln, jeder Takt aufgezeichnet. Ausgabe: `korb_pruefung.txt`, Neuzählung: `korb_zaehlung.txt`.

**Es gibt zwei Regeln, nicht eine.** Befehl 69 setzt den Korb ohne Prüfung, danach prüft das Spiel ihn beim Erzeugen und in jedem Takt (`processEntityHitBuildingOrUnit`). Ein Mensch kommt nur über das Menü dorthin, und das Menü fragt vorher `getHeightAtTileIncludingOwnersBuildings`, für Vorschau und Klick (`MenuItemActionHandler_InGameMenu_TriggerPlaceBuildingCommand`).

| Ziel | Korb bleibt mit Befehl 69 | Prüfung des Menüs sagt ja | Höhe des Korbs |
|---|---|---|---|
| Bergfried (BT_STONEKEEP 41) | 49 von 49 | 25, die inneren | 100 |
| Wachturm (BT_TOWER1 74) | 9 von 9 | 1 | 304 |
| Verteidigungsturm (BT_TOWER2 75) | 16 von 16 | 4 | 156 |
| Geschützturm (BT_TOWER3 76) | 25 von 25 | 9 | 188 |
| Eckiger Turm (BT_TOWER4 77) | 36 von 36 | 16 | 200 |
| Runder Turm (BT_TOWER5 78) | 36 von 36 | 16 | 200 |
| Kleines Torhaus (BT_GATEHOUSESMALL 46) | 25 von 25 | 25 | 136 |
| Hohe Mauer (M_MAPPER_WALL 25) | 8 von 8 | 8 | 98 |
| Treppe (M_MAPPER_STAIR 27) | 1 von 1 | 1 | 82 |
| Zinne an der Mauer (M_MAPPER_CRENAL 26) | 7 von 7 | 3 | 106 |
| Bergfried von Spieler 2, gesetzt von Spieler 1 | 3 von 3 | 0 | 100 |
| Hütte (BT_HOVEL 1) | 0 von 16 | 0 | |
| Boden | 0 von 3 | 0 | |
| Außerhalb der Karte | 0 von 7 | | |

Die Regel aus dem Code stimmt auf allen 241 geprüften Feldern. Der Prüfer schlägt an: Hütte als erlaubt gerechnet 16 Abweichungen, Bergfried als verboten 52, ohne gelesene Körbe 215. Die Prüfung des Menüs ist direkt gerufen, solange noch kein Korb dort stand. Das Menü selbst ist nicht angeklickt.

**Warum die alte Kurzprobe nichts fand:** Sie zielte außerhalb der Karte. Sie ging x und y von 0 bis 399 durch, das Spielfeld ist aber eine Raute. Außerhalb der Raute liefert die Zeilentabelle die Nummer eines anderen, echten Feldes: 40.002 der 80.400 Feldnummern wurden so doppelt oder dreifach getroffen (gerechnet aus `zeilen.npy`), und die Probe merkte sich dabei auch falsche Koordinaten. Alle 4 Ziele ohne Korb lagen außerhalb der Karte, die 2 mit Korb auf ihr. Das Spiel setzt dort Zustand 3, der Korb erscheint in keinem Takt.

Doppelprobe auf 3 Feldern des fremden Bergfrieds, je dieselbe Feldnummer: mit den Koordinaten außerhalb kein Korb und leerer Listenkopf wie damals, mit den echten steht er. Die 4 alten Ziele brachten wieder keinen Korb. `s.kachel` bricht jetzt bei Feldern außerhalb ab. Die Kartenmaske ist die Raute ohne 1.596 Felder, kein Feld der Maske liegt außerhalb der Raute.

Mein erster Verdacht, die zweite Feldliste `EntityLayerLT25`, war falsch: 217 Körbe, keiner mit Nummer unter 25. Der Listenkopf täuscht trotzdem: Auf einem Feld stand die Flagge (ET_FLAG_4, Art 11) vorn, der Korb dahinter.

**Zinnen:** Zinnenfelder tragen auf x + y ungerade das Bit 0x400000 (`placeWalls`, 7 von 7 Feldern). Mit Bit sagt die Prüfung des Menüs nein, ohne Bit ja. 8 KI-Burgen, letzter Stand von Lauf K, jede Feldnummer einmal: 230 mit Bit alle nein, 88 ohne Bit alle ja. Mauer 951 ja, 166 nein. Treppe 198 ja, 1 nein. Die Rechnung ist vorher an 16 direkten Aufrufen bestätigt. Die alten Zahlen (Mauer 3.089 zu 488, Zinne 169 zu 683) zählten Felder mehrfach.

Eine Zinne allein entsteht nicht: 9 Versuche mit Stein, `validateWallBuildPath` verlangt für M_MAPPER_CRENAL Mauer daneben (Grund 0x13). Auf einer fertigen Mauer auch nicht (`validateWallPlacementAtTile`).

**Gold:** Befehl 69 kostet nur in Siege That, und zwar 5 Gold aus `startResources[15]`, der Bestand `currentResources` bleibt. Gemessen: 0 auf -5 auf der Mauer, ein Korb auf Boden danach lässt es bei -5, das Gold kommt im selben Befehl zurück. Im Gefecht 0. Der Befehl fragt nicht, ob das Gold reicht, darum -5. Das Menü fragt es laut Code. Siege That ist hier nur durch Setzen von `gameMode_2` im laufenden Gefecht hergestellt.

**Holzwand (M_MAPPER_WOODWALL 46):** Im echten Spiel nicht baubar, weder im Spiel noch im eigenen Szenario, Stufe Daniel. Der Code ist noch da: Befehl 25 baute sie in einem abgebrochenen Start (Höhe 8 auf 68, `placeWalls` +60, keine Aufzeichnung), und ein KI-Bauplan könnte sie laut Code anfordern (`AIVBT_LOW_WALL`). Darum nicht weiter geprüft. Das Feld, das in P312 „niedrige Mauer (Höhe 8)“ hieß, war mein eigener Name.

**Falle beim Aufbau im Gefecht:** Eine Befehlsliste baut nicht alle Mauerlinien, obwohl jeder Befehl „abgesetzt“ meldet. Im ersten Versuch entstanden 1 von 5, 2 von 5 und 2 von 4 Linien, danach mit neuem Stein je höchstens 1, ohne neuen Stein keine (`korb_mauerlinien.txt`). Gesetzter Stein fällt auf den echten Lagerbestand zurück, beim nächsten Versuch 40 Takte später stand er wieder auf 0. Wann genau das passiert, ist nicht gemessen. `szene_sonder` gibt jetzt je Versuch neuen Stein, fährt je Linie einen Versuch mehr und nennt Fehlendes im Ergebnis, nicht nur im Plan. 6 eingebaute Fehler zu diesen Änderungen, 6 rot.

## Noch offen

- Feuerkorb im Menü: nicht geklickt, Tests laufen nie über die Maus. „Prüfung des Menüs sagt ja“ heißt, die Funktion antwortet ja. Bei den Feldern ohne Bit widerspricht das Daniels Angabe „keine Zinnen“, das klärt nur ein Blick ins Spiel.
- Feuerkorb auf großem Torhaus und den Bergfried-Arten 42 bis 44: nur Code.
- Abprall an Turm und Burg: nur 1 Flug (Ballista am Bergfried), alle anderen an der Mauer.
- Nachbarfeld bei den Arten 9, 50 und 51: Sie tragen dasselbe Merkmal, kamen nicht vor.
- Schütze auf dem Turm gegen ein Ziel auf der Mauer: gerechnet, nicht geflogen.
- Aufschlaghöhe plus 20 auf Türmen bei der Hälfte der Geschosse: Code, kein eigener Fall.
- Brandpfeil gegen eine Hütte: nur 2 Treffer, das ist wenig.
- Instanz 2 lief nach dem zweiten Direkttest der Trefferfenster im Gefecht nicht mehr. Der Ton „Wir werden angegriffen“ aus fremdem Faden ist eine Vermutung, nicht belegt. Der erste Durchgang im Editor lief sauber, beide Ergebnisse sind gleich.

## Dateien

Alle unter `data/research/auge_plan/streuung_20261104/`: `korb_lauf.py`, `korb_pruefen.py`, `korb_zaehlen.py` (Feuerkorb), `flug_modell.py`, `streuung_modell.py` (die Regeln als Rechnung), `flug_pruefen.py`, `ziel_pruefen.py`, `feuer_pruefen.py`, `brand_pruefen.py`, `streuung_rufen.py`, `fenster_rufen.py`, `reste_pruefen.py`, `oben_pruefen.py`, `pech_pruefen.py`, `verteilung.py`, `gefahr_tabelle.py`, je mit Ausgabe `.txt`. Festwerte für die Tests: `streuung_beispiele.json`, `flug_beispiele.json`, `fenster_beispiele.json`. Szenen: `streuung`, `streuung2`, `streuung3`, `streuung4_g` in `auge_lauf_s.py`.
