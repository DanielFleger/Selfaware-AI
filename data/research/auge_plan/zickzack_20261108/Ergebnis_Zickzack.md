# Zickzack für ganze Gruppen, im Kern gebaut und im Gefecht geprüft (B-174)

Stand 09.11.2026. Läufe auf Instanz 2 im Gefecht (zwei Menschen-Plätze, keine KI, Tempo 20, freies Feld), Kern Version 22 und ab dem letzten Brandtrupp-Lauf 23, jeder Takt aufgezeichnet.

## Ergebnis

**Zickzack wirkt auch für Gruppen, aber nur, wenn sie breit läuft.** Dicht aufgestellt fängt der Nachbar den Pfeil, der sein Ziel verfehlt. Mit 5 Feldern Abstand und einem eigenen Befehl je Einheit bleiben ab 12 Feldern 4,5 % Treffer übrig, gegen 87 % beim geraden Lauf. Die Strecke bleibt gleich.

Je 8 Sklaven (A_SLAVE, 71) pendeln zwischen 22 und 8 Feldern vor 8 Bogenschützen (E_ARCHER, 22), jeder Schütze zielt auf einen eigenen Läufer.

| Bahn | Lauf | Felder je 1.000 Takte | Schritte mit neuer Richtung | Treffer ab 12 Feldern, jeder Takt | Treffer ab 12 Feldern, wirkliche Pfeile |
|---|---|---|---|---|---|
| gerade | 1 | 80,8 | 10 % | 86,7 % | 93 % von 86 |
| gerade | 2 | 79,4 | 10 % | 87,3 % | 100 % von 74 |
| Zickzack dicht, ein Befehl je Feld | 1 | 80,4 | 94 % | 38,1 % | 46 % von 87 |
| Zickzack dicht, daneben die breite Bahn | 2 | 80,7 | 62 % | 61,2 % | 42 % von 60 |
| Zickzack breit, je Einheit ein Befehl je Feld | 2 | 83,0 | 100 % | 4,5 % | 6 % von 86 |

„Jeder Takt“ heißt: für jeden Takt und jeden Schützen gerechnet, als wäre in diesem Takt ein Pfeil auf sein Ziel geflogen, mit der echten Spur aller 8 Läufer. Die Rechnung traf bei den wirklich abgefeuerten Pfeilen in beiden Läufen jedes Mal Zielpunkt und Ergebnis (175 von 175, 264 von 264).

Die 10 % Richtungswechsel der geraden Gruppe sind ihre Wenden: 12 Wenden auf rund 114 Schritte je Einheit.

Gerechnet nach Abstand, Lauf 2 (`zickzack2_g_ergebnis.txt`):

| Abstand | gerade | Zickzack dicht | Zickzack breit |
|---|---|---|---|
| 8 bis 10 Felder | 94,9 % | 78,3 % | 7,0 % |
| 11 bis 13 | 98,8 % | 73,0 % | 2,1 % |
| 14 bis 16 | 99,9 % | 68,7 % | 1,2 % |
| 17 bis 19 | 76,1 % | 51,2 % | 0,2 % |
| 20 bis 24 | 47,4 % | 33,0 % | 12,9 % |

Vor den Läufen gesetzt, von mir und ohne Vorgabe: widerlegt, wenn weniger als die Hälfte der Schritte die Richtung wechselt oder der Zickzack ab 12 Feldern nicht seltener getroffen wird. Beides trat nicht ein. Ob die Wirkung reicht, entscheidet Daniel.

## Warum die dichte Gruppe trotzdem getroffen wird

Jeder Läufer einzeln weicht aus. Auf derselben Spur, nur ohne Nachbarn, wäre er in Lauf 1 ab 12 Feldern zu 5,4 % getroffen worden, in der Gruppe sind es 38,1 % (`zickzack_abstand.txt`). In der breiten Bahn liegen beide Werte bei 0,2 % für das Ziel selbst.

Das Spiel stellt eine Gruppe auf jedes zweite Feld (gelesen in `giveTribeMoveInstruction`). Der Pfeil zielt auf Feldmitte plus Vorhalt, beim Zickzack landet er also 2 bis 3 Felder neben dem Ziel. Genau dort steht der Nachbar. Die Gefahrenkarte aus Lauf 1 sagt, wie oft ein gedachter Nachbar mit festem Versatz getroffen würde (ab 12 Feldern):

- quer zur Schussrichtung, 2 und 3 Felder: bis 23 %
- quer, 5 Felder: 2 %
- quer, ab 6 Felder: 0 %
- in Schussrichtung, 1 bis 3 Felder dahinter: höchstens 5 %

Beim dichten Lauf 2 fiel die Wirkung weiter (62 % Richtungswechsel statt 94 %): Neben dem einen Gruppenbefehl standen 8 Einzelbefehle derselben Runde in der Schlange. Der Befehl wartete in 18 % der Fälle länger als die 6 Takte, nach denen die Einheit die Feldmitte erreicht und das Ziel liest, im ersten Lauf in 6 % (`zickzack_warteschlange.txt`). Die 8 Einzelbefehle selbst warteten nie länger.

## Der Brandtrupp (B-175)

Auch die Sklaven im Brandtrupp laufen jetzt im Zickzack (derselbe Schalter `zickzack=ja`): jeder einzeln bis 11 Felder vor sein Gebäude, danach kommt der normale Angriffsbefehl. Höchstens 8 Sklaven gleichzeitig, die übrigen laufen wie bisher. Solange der Kern bereit ist, geht jeder Befehl an die Sklaven über ihn.

Probe `brand_g`: 4 Bahnen, je 4 Sklaven, 60 Felder zu 4 Holzfällerhütten (BT_WOODCUTTERSHUT), 8 Bogenschützen stehen seitlich am Weg und schießen von selbst, die echte Klasse `Brandtrupp` führt in Runden von 63 Takten. Die Sklaven haben sehr viel Leben, damit alle ankommen und jeder Treffer zählt.

| | gerade | Zickzack |
|---|---|---|
| Treffer je Sklave bis zur Ankunft | 6,50 | 3,12 |
| wären vor der Ankunft tot | 8 von 8 | 6 von 8 |
| Sklaven ganz ohne Treffer | 0 von 8 | 1 von 8 |
| Pfeile, die jemanden treffen | 94 % von 144 | 76 % von 144 |
| Ankunft im Median, Takte nach dem Start | 753 | 741 |
| Felder je 1.000 Takte | 72,8 | 74,5 |
| Schritte mit neuer Richtung | 1 % | 92 % |
| angezündete Hütten | 8 von 8 | 8 von 8 |

Tot heißt: mindestens drei Treffer. Ein Pfeil nimmt einem Sklaven 7.000 Leben (in 61 Takten genau einer, in 8 Takten zwei auf einmal), er hat auf Instanz 2 15.000 Leben. Im Lauf davor (Kern 22) waren es nach der ersten Zählung, die zwei Pfeile im selben Takt als einen rechnete, 6,12 gegen 2,38 Treffer und 8 von 8 gegen 3 von 8 Tote. Dessen Protokoll ist überschrieben, die Aufnahme liegt lokal.

Die Wirkung ist kleiner als die 4,5 % der Bahnen oben, weil die Schützen seitlich stehen. Das entspricht dem Fall „Zickzack quer“ aus B-173 (bei 12 Feldern 33 % statt 58 %).

Vor dem Lauf gesetzt, von mir und ohne Vorgabe: widerlegt, wenn die Sklaven im Zickzack nicht seltener getroffen werden oder weniger Hütten brennen. Beides trat nicht ein.

Bis der Lauf zählte, brauchte es drei Versuche, und jeder Mangel war einer meines Aufbaus oder des Kerns:

1. Lauf 23:54: Das ältere Spielmodul auf Instanz 2 kennt `samurai_sendetakt` nicht. Sendeten Modul und Kern im selben Takt, verschmolzen die Befehle (S57), und Zickzack-Sklaven bekamen das Ziel einer Nachbarbahn. Dazu blieb je ein Sklave im Nahkampf an den Schützen hängen, die Hütte lag zu nah an ihrer Reihe. Jetzt gehen alle Befehle über den Kern, und die Schützen stehen weiter weg. Das Modul auf dem Laptop (`bridge/snapshots/logik_stand_20261108.lua`) wartet auf den Kern, im Lauf hier fehlt das.
2. Lauf 00:01: 4 Trupps standen je 41 Takte. Zwei Sklaven wollten im selben Takt auf dasselbe Feld, der Kern schickte das als einen Gruppenbefehl, und das Spiel gab dem zweiten einen anderen Platz. Kern 23 vergibt einen Wegpunkt je Takt nur einmal.
3. Lauf 00:07: gewertet, kein Trupp festgelaufen.

## Ganze Partie

Zwei vollständige Partien auf Instanz 2 mit dem echten Lenker: The Killing Plains, 2 KI-Gegner (KI-Nummer 7), Tempo 200, bis Takt 40.000, Einstellungen wie der Vorstoß-Lauf vom Laptop (`kernweg=ja vorstoss=ja`). Geändert ist nur `zickzack=ja` gegen `zickzack=nein`.

| | Zickzack an | Zickzack aus |
|---|---|---|
| Ende | Takt 40.182 | Takt 40.243 |
| vom Brandtrupp angezündete Gebäude | 19 | 13 |
| vom Angriff zerstörte Gebäude | 45 | 37 |
| eigene Verluste beim Angriff | 31 | 24 |
| von der Reiterjagd getötete Arbeiter | 10 | 21 |
| Sklaven (Typ 71): gesehen, tot | 47, 45 | 44, 42 |
| Schützen (Typ 22, 23, 70): gesehen, tot | 14, 5 | 14, 5 |

Das ist **eine Partie je Einstellung**, nur eine erste Richtung. Der Verlauf läuft früh auseinander, darum lässt sich daraus nicht ablesen, ob der Zickzack die Partie verbessert. Belegt ist, dass alles zusammen läuft:

- Das Spiel hielt Tempo 200, ein Takt dauerte im Mittel 5,0 Millisekunden.
- Keine Fehlermeldung im Kern, kein Programmabbruch im Lenker.
- Der Kern setzte 8.826 Wegpunkte. 95 Mal kam ein Trupp am Ziel an.
- 163 Mal lief ein Trupp fest (1,8 % der Wegpunkte, je bis zu 40 Takte Stillstand). Die Ursache in der Partie ist nicht untersucht.

Offen und von Daniel angesprochen (09.11.): Die Sklaven laufen den ganzen Weg im Zickzack, auch wo niemand schießt. Das war meine Vereinfachung. Es bringt dort nichts und kostet Befehle.

Umgebung: Instanz 2 mit dem Liga-Modul (`Mod-KI-Team-Liga 2.0.2`), `logik.lua` = `bridge/snapshots/logik_stand_20261108.lua` (sha256 533d78d156642eec), Kern 23. Die KI-Lords haben dort volle Stärke (150.000 Leben), auf dem Laptop waren sie als Nomade auf 20 % geschwächt. Der erste Startversuch brach deshalb an der Gegnerprüfung ab, danach lief die Partie ohne `gegner_erwartet`. Mit dem Laptop sind die Zahlen also nicht vergleichbar.

## Was gebaut ist

- **Kern** `crates/samurai-kern/src/zickzack.rs`, Version 22: Der Kern führt jeden Trupp Feld für Feld. Er schickt den nächsten Wegpunkt, sobald die Einheit, die ihn als Platz hat, sein Feld betritt und niemand mehr als ein Feld von seinem Platz entfernt ist. Nach 40 Takten ohne Fortschritt setzt der Trupp von seiner Mitte neu an.
- **Python:** Ring-Art 30 (`KL.ZICKZACK`), `Kernweg.zickzack`.
- **Vorstoß:** Schalter `zickzack=ja` (braucht `vorstoss=ja`, aus ist der Standard). Vorrücken und Abziehen laufen im Zickzack in breiter Aufstellung: bis zu 8 Plätze in 2 Reihen, 5 Felder Abstand, je Platz ein Trupp. Alle anderen Befehle geben die Einheiten vorher beim Kern frei. Sind es mehr als 8 Einheiten, teilen sie sich die Plätze.

Bei einem Ziel auf einer Achse wechselt der Querschritt jedes Feld, wie gemessen. Je schräger das Ziel liegt, desto seltener wechselt er. Auf der genauen Diagonalen wechselt er gar nicht, weil dort jeder andere Schritt Strecke kostet.

**Probe mit der echten Klasse `Vorstoss`** (`vorstoss_g_ergebnis.txt`): 6 Bogenschützen. Beim Vorrücken wechseln 95 % der Schritte die Richtung, 100 % sind schräg. Auf den einzelnen Schützen schießen sie (6 Pfeile), danach rücken sie weiter vor. Vor der Überzahl von acht ziehen sie ab, der Abstand zum nächsten Feind wächst von 35 auf 48 Felder. Kein Fehler im Kern. Die Lage ist gestellt, Treffer sind dort nicht gemessen.

## Wie gut das belegt ist

| Prüfung | Ergebnis |
|---|---|
| Rechnung gegen wirkliche Pfeile, Lauf 1 und 2 | 175 von 175 und 264 von 264: Zielpunkt und Ergebnis gleich |
| Eingebaute Fehler im Kern | 6 von 6 rot, einer erst nach Schärfen des Tests |
| Eingebaute Fehler im Vorstoß | 6 von 6 rot |
| Aufzeichnung | 1.669 und 1.670 Takte, nichts fehlt |
| Festgelaufene Trupps | 0 in allen drei gewerteten Läufen |

Zwei Läufe der Probe zählen nicht und sind benannt: Der erste fand keinen Platz auf der Karte (110 mal 31 Felder), im zweiten zählten die Start-Bogenschützen zur Gruppe, weil sie erst bei Takt 202 und 403 erscheinen. Jetzt werden sie vorher abgeräumt.

## Grenzen

- Nur Sklaven gegen Bogenschützen, Ziel auf einer Achse, freies Feld, eine Bahn je Muster, zwei Läufe. Nicht gemessen: Armbrust, Schleuder, Steine, Feuer, Türme, Ziele schräg zur Achse, unebenes Gelände.
- Schützen im Vorstoß bleiben bei 38 Feldern stehen und schießen. Beim Vorrücken laufen sie deshalb selten unter Beschuss, der Nutzen liegt dort beim Abziehen.
- Nahkämpfer laufen noch nicht im Zickzack, die Sklaven im Brandtrupp schon.
- Brandtrupp: je Muster 8 Sklaven in einem gewerteten Lauf, ein Lauf davor mit dem älteren Kern. Die Sklaven laufen mit viel Leben weiter; im Spiel sterben sie beim dritten Treffer, und die Schützen wählen ein neues Ziel. Sklaven über 8 hinaus laufen gerade, die Auswahl ist die Reihenfolge ihrer Nummern, nicht ihre Gefahr.
- Der Kern meldet den Angriffsbefehl der Sklaven als „wirkt nicht“, obwohl die Hütten brennen. Sein Prüffeld passt bei ihnen vermutlich nicht, das ist nicht untersucht.
- Die Probe `vorstoss_g` stellt die Lage, die Runde des Lenkers ist dort fest 63 Takte (Median gemessen). Ganze Partien siehe oben.
- Mehr als 8 Einheiten sind nicht gemessen. Wer sich einen Platz teilt, läuft dicht.
- Die breite Aufstellung braucht Platz: bei 8 Einheiten 15 Felder quer. Hindernisse sind nicht getestet.
- Die Kern-DLL liegt nur auf Instanz 2 (mit `--target i686-pc-windows-gnu` gebaut, auf diesem PC gibt es kein MSVC). Instanz 5 und Daniels App haben den alten Kern.

## Dateien

Alle unter `data/research/auge_plan/zickzack_20261108/`: `zickzack_auswerten.py`, `zickzack_g_ergebnis.txt`, `zickzack2_g_ergebnis.txt` (Bewegung, Pfeile, jeder Takt), `zickzack_abstand.py`, `zickzack_abstand.txt`, `zickzack2_g_abstand.txt` (Nachbarn, Gefahrenkarte), `zickzack_warteschlange.py` und `.txt`, `vorstoss_auswerten.py`, `vorstoss_g_ergebnis.txt`, `brand_auswerten.py`, `brand_g_ergebnis.txt`, `lauf_zickzack_g.log`, `lauf_zickzack2_g.log`, `lauf_vorstoss_g.log`, `lauf_brand_g.log`, `partie_vergleich.py`, `partie_vergleich.txt`. Mitschriften der Partien: `data/research/zickzack_20261109_001758_an_i2_konsole.txt` und `..._002159_aus_i2_konsole.txt`. Die Szenen heißen `zickzack_g`, `zickzack2_g`, `vorstoss_g` und `brand_g` in `src/selfaware/tools/experiments/auge_lauf_s.py`.
