# Plan: Lauf S (B-142)

**Gefahren am 03.11.2026, Ergebnis in `data/research/auge_plan/lauf_s_20261103/Ergebnis_Lauf_S.md`. Abweichungen vom Plan: Lastprobe mit 1.150 gegen 1.150 Pikenieren ohne Schützen; Reichweite über eine Leiter statt Anlauf; Haltung in zwei Szenen; Lauf-K-Stand nicht gefahren. Widerlegt: laufendes Ziel verfehlt, Streitkolbenkämpfer im Gefecht schneller, Katapult 20 und Trebuchet 60 je Stein. Die sieben Sonderfälle sind bis 23:17 nachgefahren, alle erreicht, Löschen und Durchgang durchs Tor nicht.**

Erstellt 03.11.2026 von SRE, neu gefasst nach Daniels Einwand ("niemand will 102 minuten", "schlau testen", "viele dinge extrapolieren") und dem Rat. Der lange Vorgänger mit 1.158 Einzelversuchen steht in Commit `6a78841`. **Noch nichts gebaut, nichts gestartet.** Belege und Befehle: `data/research/auge_plan/lauf_s_plan/`.

## Der Gedanke

**Geprüft werden Regeln, nicht Zeilen.** Die 1.158 Zeilen der Liste sind Art mal Art. Das Spiel rechnet aber mit wenigen Regeln: Nahkampf ist ein Griff in eine Tabelle, Prüfrunde eine Bitmaske, Gebäudeschaden ein fester Wert je Stein. **Das Auge sieht jede Einheit in jedem Takt,** also liefert eine Szene alle Paare auf einmal. Abstand braucht es nur, wo sich etwas wirklich stören kann.

**Was das schon gebracht hat, ohne Spielstart** (`regeln_aus_lauf_k.txt`, 10.009 Takte Lauf K):

| Regel | Fälle | Ergebnis |
|---|---|---|
| Nahkampf: Verlust gleich Tabelle Schläger gegen Opfer | 4.556 | 4.319 gleich, 228 mit Angstfaktor (Stufe 1: 162 statt 150, also 8 statt 5 Prozent), 9 traf im selben Takt zusätzlich ein Geschoss. **Keiner ungeklärt** |
| Prüfrunde: `(totalGameTicksUnk + 1) & Maske` gleich `fixedRng & Maske` | 54.497 | 54.452 passen, 45 mit Versatz 0 (Lesung an der Taktgrenze). **Keiner ungeklärt** |

Gesehen sind dabei nur 12 von 361 Paaren. Darum muss jede Art einmal wirklich zuschlagen, aber nicht jede 500 Takte lang in eigener Zelle.

## Die Szenen

Jede Szene: Spiel anhalten, alles setzen, weiter, das Auge zeichnet auf, fertig oder Grenze, abräumen. Die Grenze ist in Takten, die Sekunden sind daraus gerechnet (`rechnung_szenen.txt`). **Setzen und Laden sind noch nicht gemessen.**

| # | Szene | Warum es so geht | Tempo | Grenze | s |
|---|---|---|---|---|---|
| 1 | **Laufen:** 24 Arten nebeneinander, 10 Felder schräg, 10 gerade | Alle gehören einem Spieler, also stört sich nichts. Tempo ändert sich nach dem Anlauf nicht | 200 | 2.880 | 14 |
| 2 | **Nahkampf:** alle 190 Paare dicht, je Paar Abstand 1 | Der nächste Feind ist der Partner. Ausgewertet wird bis zum ersten Tod je Paar. Füllt 361 Zeilen | 40 | 507 | 13 |
| 3a | **Beschuss:** alle 171 Paare, Abstand 8, 3 Treffer | Wie 2. Täter steht im Geschoss | 40 | 867 | 23 |
| 3b | **Reichweite:** jeder Schütze auf eine unbemannte Ramme, von außerhalb | Die Ramme hält 400.000 Leben aus und wehrt sich nicht. Jeder läuft, bis er schießt | 200 | 4.608 | 23 |
| 3c | **Laufendes Ziel,** 5 Schuss | Noch nie gemessen, wichtig fürs Ausweichen | 200 | 1.323 | 7 |
| 4 | **Haltung:** 3 Arten (eine je Prüfrunde), 5 Fälle, Abstand 60 | Nur hier stört der Nachbar wirklich. Der Grenzwert steht einmal im Code, ohne Sonderfall je Art | 200 | 1.024 | 5 |
| 5a | **Fußtruppen gegen Gebäude:** 80 Paare | Wie 2 | 40 | 507 | 13 |
| 5b | **Belagerung:** 82 Ziele mit je einem Katapult, die 5 anderen Geräte gegen 6 Klassen (Hütte, Burgbau ohne Leben, Tor, Turm, Steinmauer, Holzmauer) | Schaden je Stein ist fest, Leben steht in der Tabelle. Bricht die Regel, kommt ein Durchgang mit allen Zielen für dieses Gerät dazu | 1000 | 4.920 | 6 |
| 6a | **Angriff auf einen Punkt:** alle 8 zugleich | Ein Besitzer, kein Feind außer dem leeren Tor und Turm, also kein Beschuss | 200 | 5.000 | 25 |
| 6b | **Sonderfälle:** alle 11 zugleich, weit auseinander | Feuer, Pech, Öl, Mordloch, Hunde, Kuhwurf, Graben, Leiter, Tunnel, Schild, Tor | 40 | 3.000 | 78 |
| 7a | **Schlachten:** 20 gegen 20, 1.000 gegen 1.000, 500 Schützen, 500 Araber | Eine große Schlacht läuft selbst durch alle kleineren Größen. Die Reihen mit 100 werden daraus abgelesen | 1000 | 40.000 | 52 |
| 7b | **Lesen unter Last:** 2.400 Einheiten, Wechselprobe | Siehe unten | 1000 bis 40 | 16.040 | 39 |
| 8a | **Gegenprobe Gefecht:** Szenen 1, 2, 3a, 5b noch einmal, Spieler 2 ohne KI | Dieselben Szenen, dieselbe Auswertung, Vergleich Zeile für Zeile. Weicht etwas ab, gilt der Editor-Wert dort nicht | wie oben | | 57 |
| 8b | **Lauf-K-Stand:** was nur eine laufende KI zeigt | Bis nach dem übernächsten Lord-Fall in Lauf K | 1000 | 30.000 | 39 |

**Zusammen 6,6 Minuten, ohne Setzen und Laden.** Das ist eine Obergrenze.

Die erste Szene ist zugleich die Probe. Scheitert eine Szene, wird erklärt und nur sie neu gefahren. Es gibt keinen Lauf am Stück, den man abwarten muss.

Karte: `Liga_Grumpy Neighbors` im Karteneditor, so wie Daniel es wollte. Instanz 2, Instanz 5 bleibt unberührt.

## Warum Gefecht trotzdem

Im Schadenscode fragt das Spiel die Spielart nur für Töne ab. Beim Gehen nicht: Der Streitkolbenkämpfer (E_MACE 26) geht im Einzelspiel und rennt im Gefecht (`UpdateMaceman` Zeile 405), und UCP hat genau diese Stelle umgebaut. SamurAI spielt im Gefecht. In 8a ist Spieler 2 ein Mensch-Platz ohne KI (L119), abgeräumt wird ohne die Lords (B-149).

## Lesen unter Last

Der alte Vergleich ohne, mit, ohne Lesen zählt jede Laständerung als Rauschen. In Lauf K (827, 812,7, 800,1) hätte er erst ab rund 5 Prozent angeschlagen. Neu: abwechselnd mit und ohne Lesen, jede Phase gegen ihre Nachbarn, und das Ergebnis nennt, ab welchem Abzug es angeschlagen hätte. 2.400 Einheiten kämpfen dabei, der Schaden Pikenier gegen Pikenier steht in der Tabelle auf 1, damit die Last gleich bleibt. Danach wird der alte Wert zurückgeschrieben.

**Ohne eigene Messung, begründet:** Stufen 1 und 10 (das Lesen ist fertig, bevor der nächste Takt kommt) und die leere Karte (leichter als das volle Dorf aus Lauf F).

## Was gerechnet und was gemessen ist

Jede Zeile der Liste bekommt einen Status: **gemessen** oder **gerechnet aus Regel, geprüft an N Fällen**. Gerechnet sind vor allem 380 der 492 Zeilen V4 und die Reihen mit 100 Einheiten in V5. Bricht die Regel irgendwo, wird dort gemessen.

## Vorher festgelegt, was widerlegt

| Regel | Widerlegt, wenn |
|---|---|
| Nahkampf gleich Tabelle mal Angstfaktor. Leiterträger und Ingenieur schlagen nicht (`DAT_UNIT_CAN_MELEE` 0) | Ein Fall bleibt ungeklärt |
| Pfeil und Bolzen gleich Tabelle je Ziel. Schleuderer: nur gemessen, sein Code ist von UCP ersetzt | Ein Fall bleibt ungeklärt |
| Stehendes Ziel wird immer getroffen, laufendes verfehlt | Lücke, oder 100 Prozent |
| Haltung: aggressiv reagiert in 24 Feldern, in 26 nicht; defensiv in 4, in 6 nicht | Anderer Rand |
| Katapult 20, Trebuchet 60, Mangonel 5 je Stein. Kein Schaden an Lager, Bergfried, Zugbrücke, Mordgrube, Pechgraben, Teich | Andere Stufen, Leben fällt |
| Besatzung: Trebuchet 3, Katapult, Mangonel, Ballista, Feuerballiste 2, Ramme und Turm 4, Schild 1 | Schießt oder fährt mit weniger |
| Schaden im Gefecht gleich Editor. Gehtempo Streitkolbenkämpfer verschieden | Schaden weicht ab, Tempo gleich |
| Auf Tempo 40 fehlt kein Takt. Mit Lesen kein Abzug | Takt fehlt, Abzug über der genannten Grenze |
| Die Kontrolleinheit je Szene verliert kein Leben und läuft nicht los | Sie tut es: Szene gilt als gestört |

## Abbruch

Grenzen in Takten. Die Uhr zählt nur gegen Hängen: 5 s kein Takt im laufenden Spiel. Abbruch der Szene: Spiel oder Aufzeichnung weg, von Hand gestoppt, falsche Spielart, Takt fehlt auf Tempo 40, kein einziger Treffer in der ganzen Szene. Widerlegte Regeln sind Funde, kein Abbruch. Danach: Tabellenwert zurück, Takt steht, Sperre frei, Ende sofort melden, kein zweiter Lauf von selbst.

## Auswertung

Ein Regel-Prüfer für alle Szenen: Er gibt nur die Zahl der Fälle und die **Abweichungen** aus, von Hand wird nur angesehen, was abweicht. Dazu A1, A2, A3, A4, A9, A10, A12, A13 und die 89 Punkte (`punkte_zuteilung.csv`) mit dem vorhandenen Werkzeug. Ergebnis in `Ergebnis_Lauf_S.md`, Status in `versuche_szenario.csv`, dann Handbuch, Register, Wissensstand, Backlog, Ton.

## Bauen

Ein Szenen-Programm `auge_lauf_s.py` auf den Bausteinen von Lauf F und K, ein Regel-Prüfer `auge_regeln.py`, aufbauend auf `regeln_aus_lauf_k.py`, `a4_wechselprobe`, `toeteAlle` "ohneLord" im Modul. Tests gegen ein künstliches Spiel mit Sabotage, auch: 1 Prozent Abzug bei fallender Last muss gefunden werden. Keine Prüfer-Helfer.

## Was die erste Szene gleich mit klärt

Steht die Karte in der Editor-Liste (sie liegt nur im Plugin-Ordner, sonst Kopie nach `Instanz2\maps`)? `currentGameMode` im Editor? Wie lange dauern Setzen und Abräumen? Wirken Befehle an Spieler 2? Bemannen und Haltung setzen zeigen die Szenen 3b und 4, 2.400 Einheiten die Szene 7b.

## Was dieser Lauf nicht beantwortet

Bündnis, `GM_SIEGE_THAT`, Wellen-System, Außenposten, die 8 offenen und 27 gesehenen Punkte aus Lauf F. Was nebenbei vorkommt, wird mitgelesen.
