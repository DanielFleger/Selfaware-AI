# Ergebnis Lauf S (B-142)

Plan: `docs/plans/Plan_Lauf_S.md`. Wird je Szene fortgeschrieben. Instanz 2, `Liga_Grumpy Neighbors` im Karteneditor, Spielart `currentGameMode` 0, `gameMode_2` 1.

## Was die erste Szene über den Aufbau gezeigt hat

| Frage aus dem Plan | Antwort |
|---|---|
| Steht die Karte in der Editor-Liste? | Ja, Eintrag 5 von 92, keine Kopie nötig |
| Hängt das Laden? | Nein |
| `currentGameMode` im Editor nach frischem Start | 0, `gameMode_2` 1 |
| Freie Felder im laufenden Spiel | 57.174 (aus der Kartendatei gerechnet: 57.247) |
| Abräumen | Einheiten der Karte 274 Takte, Szene 321 Takte. Steintod, nicht die alte Wartezeit von 400. 132 Einheiten bleiben stehen, sie gehören keinem der 8 Spieler (vermutlich Tiere, die Kontrolle blieb unberührt) |
| Setzen | 381 Einheiten in 1,33 s im angehaltenen Spiel |

## Szene Nahkampf, 03.11. 19:15

190 Paare, je Paar direkt nebeneinander, kein Befehl. 509 Rahmen in 508 Takten, Tempo 40, kein Takt fehlt, keiner gemischt. Kontrolle unberührt. Beleg: `nahkampf.regeln.json`, Befehl `python -m selfaware.tools.analysis.auge_regeln <aufzeichnung>`, Aufzeichnung `laeufe/lauf_s_20261103_191555_nahkampf.auge` (lokal).

| Urteil | Zeilen von 361 | |
|---|---|---|
| Bestätigt: Verlust genau der Tabellenwert | 320 | |
| Schlägt nicht, wie vorhergesagt | 38 | Leiterträger (E_LADDER 29), Ingenieur (E_ENGINEER 30): `DAT_UNIT_CAN_MELEE` 0 |
| Weicht ab, erklärt | 3 | siehe unten |

- **Der Nahkampf trifft jeden Takt, bei allen Arten.** 81.689 Abstände zwischen zwei Treffern, alle genau 1 Takt.
- **Er beginnt sofort.** Erster Treffer nach 1 oder 2 Takten, bei jedem Paar, ohne Befehl und ohne auf die Prüfrunde zu warten. Die Grenze von 507 Takten war viel zu groß.
- **Schützen schlagen direkt nebeneinander zu,** statt zu schießen, mit dem Tabellenwert (112 von 114 Zeilen, die 2 anderen stehen unten).
- **3 Fremdgeschosse** im selben Takt wie ein Schlag (1.420 = 20 + Pfeil 1.400): Vermutlich haben Schützen ein anderes Paar beschossen, der Täter ist nicht nachgewiesen. Der Prüfer rechnet solche Fälle heraus.

Die 3 Abweichungen:

| Paar | Befund | Erklärung |
|---|---|---|
| Tunnelgräber (TUNNELER 5) gegen Berittenen Bogenschützen (A_HARCHER 74), beide Richtungen | 132 und 130 Takte lang 37 mehr je Takt, einmal 75 mehr | Vermutet: Feuer eines benachbarten Feuerwerfers. 17.10. gemessen: Brand rund 37 je Takt (Handbuch). Der Täter ist nicht nachgewiesen |
| Feuerwerfer (A_FIRETHROWER 76) gegen arabischen Bogenschützen (A_ARCHER 70) | Der letzte Treffer nahm mehr als den Tabellenwert: 442 Schläge zu 30, dann der Rest | Offen. Möglich ist der Brandtod, das gehört in die Szene Sonderfälle |

## Szene Laufen, 03.11. 19:30

19 Soldaten nebeneinander, ein Besitzer, 20 Felder, gerade und schräg, Tempo 200. Alle am Ziel nach 626 Takten. Beleg: `laufen.regeln.json`.

| Tempo-Wert der Tabelle | Takte je Feld | Arten |
|---|---|---|
| 1 | 16,0 | Bogenschütze, Speerträger, Streitkolbenkämpfer, Ritter, Leiterträger, Ingenieur, Tunnelgräber, arabischer Bogenschütze, Sklave, Schleuderer, Assassine, Berittener Bogenschütze |
| 2 | 23,95 | Armbrustschütze, Pikenier, Mönch, arabischer Schwertkämpfer, Feuerwerfer, Lord |
| 3 | 31,68 | Schwertkämpfer |

- **Regel: Takte je Feld = 8 x (Tempo-Wert + 1).** Innerhalb jeder Stufe sind alle Arten gleich, gerade und schräg kosten je Feld gleich viel. Gelesen wurde rund jeden 3. Takt, die 23,95 und 31,68 sind also 24 und 32 innerhalb des Ablesefehlers.
- **Das ist Gehen im Einzelspiel, ohne Feind.** Lauf-Werte aus echten Partien (L80) sind kleiner: Bogenschütze 11,5, Speerträger 13,5, Pikenier 24. Ob das Rennen ist, zeigt die Gegenprobe im Gefecht. Noch offen.

## Szene Beschuss, 03.11. 19:30

6 Schützenarten gegen alle 19 Arten, Abstand 8, kein Befehl, 868 Takte auf Tempo 40, kein Takt fehlt. Kontrolle unberührt. Beleg: `beschuss.regeln.json`.

**Mein Aufbau war falsch gedacht:** Schützen schießen nicht nur auf den nächsten Feind, sie treffen auch fremde Ziele, und der erste Treffer kommt spät (Takt 185 bis 787). Eine Wertung je Paar sagt darum nichts. **Die Regel hält trotzdem, gewertet nach dem Opfer:**

| Regel | Ergebnis |
|---|---|
| Jeder Verlust ist eine Summe aus Pfeil, Bolzen, Stein des Opfers und Feuer | 19 von 19 Arten: kein Betrag ungeklärt |
| Geschossarten gegen Arten gesehen | 54 von 57. Es fehlen Pfeil und Bolzen gegen Tunnelgräber und Stein gegen Leiterträger, dessen Stein- und Pfeilwert gleich sind |
| Schleuderer | Trifft mit dem Stein-Wert. Am 17.10. stand im Handbuch 400 gegen Assassine, jetzt ist es 900, vermutlich eine andere Einstellung damals |
| Feuer, gemessen | 37,5 je Flamme und Takt, gegen den Lord 12,5, gegen den Feuerwerfer selbst 5. Betrag abgerundet, mehrere Flammen addieren sich (37, 75, 112) |
| Schusstakt, aus den Abständen abgelesen | Bogenschütze 129, Armbrust 228, arabischer Bogenschütze 90, Schleuderer 56, Berittener Bogenschütze 78. Passt zum 17.10. Täter je Treffer ist hier nicht zugeordnet |

**Noch nicht beantwortet:** Trefferquote und Flugzeit (dafür müssen die Geschosse selbst ausgewertet werden), welches Ziel ein Schütze wählt, Reichweite. Das braucht eine Szene, in der jeder Schütze nur ein Ziel hat.

## Szene Lesen unter Last, 03.11. 19:37

**Daniels Vorgabe hält: Mit 2.412 Einheiten im Nahkampf zieht das Lesen auf keiner Stufe messbar Tempo ab, und das Spiel hält trotz der Einheiten rund 825 Takte je Sekunde.** Im Wechsel ohne und mit Lesen. Der Schaden Pikenier gegen Pikenier stand dabei auf 1 und ist zurück, nachgelesen. Beleg: `last.plan.json`.

| Stufe | ohne Lesen | mit Lesen | Einheiten |
|---|---|---|---|
| 1000 | 810,7, 824,8, 811,7, 824,4, 824,9, 827,8 | 771,2, 821,2, 821,5, 825,1, 813,5 | 2.412 |
| 500 | 499,4, 499,6 | 498,1 | 2.407 |
| 200 | 197,5, 199,1 | 199,1 | 2.407 |
| 100 | 98,7, 98,4 | 98,5 | 2.407 |
| 40 | 39,2, 39,8 | 40,0 | 2.390 |

Auswertung `a4_wechselprobe`: Kein Abzug ueber der Grenze. Stufe 40: Abzug -0.51, haette ab 1.99 Takten je Sekunde angeschlagen; Stufe 100: Abzug 0.02, haette ab 1.96 Takten je Sekunde angeschlagen; Stufe 200: Abzug -0.77, haette ab 1.99 Takten je Sekunde angeschlagen; Stufe 500: Abzug 1.37, haette ab 1.99 Takten je Sekunde angeschlagen; Stufe 1000: Abzug -0.41, haette ab 9.05 Takten je Sekunde angeschlagen

**Warum die Zahl sank:** 42 von 2.300 fielen in 16.328 Takten, der erste nach 7.176. Ein Pikenier hat 80.000 Leben, der Schaden stand auf 1, aber es schlagen bis zu 12 zugleich auf einen. Das passt zur Regel unten (Beleg `last_tode.txt`, Befehl oben in `last_tode.py`).

**Mein Satz im Plan stimmte nicht:** Nicht alle ändern ihr Leben je Takt. Im letzten Rahmen verlieren 556 Leben, 1.702 werden von niemandem angegriffen, 490 haben genau 4 Angreifer. Alle schlagen zu, aber wer auf demselben Feld steht, nimmt dasselbe Ziel. Das ist die Lage, nicht das Lesen: Gelesen wird der ganze Block, also bleibt die Aussage zum Lesen gültig.

Grenze der Aussage: Auf Stufe 500 bis 40 je nur eine Phase mit Lesen. Die Stufen 1 und 10 sind nicht gemessen, dort ist das Lesen fertig, bevor der nächste Takt kommt. Die Einheiten stehen im Nahkampf, Wegsuche belastet erst der Marsch.

## Szenen Schlachten, 03.11. 19:37

Schachbrett, 4 Einheiten je Feld, kein Befehl, Tempo 1000. Belege: `schlacht_*.regeln.json` mit dem Verlauf je Seite über die Zeit, Protokoll `schlachten_last.protokoll.jsonl`.

| Szene | Start je Seite | Ende je Seite | Takte | Erster Tod nach | Takte je Sekunde | Plätze belegt |
|---|---|---|---|---|---|---|
| 20 gegen 20, Nahkampf gemischt | 20, 20 | 0, 10 | 1.667 | 245 | 837,5 | 172 |
| 1.000 gegen 1.000, Nahkampf gemischt | 1.000, 1.000 | 31, 170 | 5.666 | 199 | 747,5 | 2.132 |
| 500 Schützen gegen 500 Nahkampf | 500, 500 | 0, 498 | 634 | 137 | 859,3 | 1.132 |
| 500 Europäer gegen 500 Araber | 500, 500 | 420, 0 | 635 | 131 | 742,7 | 1.132 |

- **Regel: Der Schaden mehrerer Angreifer addiert sich.** Verlust eines Opfers = Summe der Tabellenwerte aller, die es als Ziel eingetragen haben, mal Takte. Gewertet nur, wo zwischen zwei Rahmen dieselben Angreifer blieben:

| Szene | Fälle | Gleich | Weniger | Mehr |
|---|---|---|---|---|
| 20 gegen 20 | 296 | 296 | 0 | 0 |
| 1.000 gegen 1.000 | 12.447 | 12.411 | 14 | 22 |
| Schützen | 574 | 574 | 0 | 0 |
| Europäer gegen Araber | 1.547 | 1.547 | 0 | 0 |
| Lastprobe | 511.653 | 505.927 | 2.307 | 3.419 |

- **Die Rahmen liegen hier Takte auseinander,** ein Angreifer kann dazwischen gewechselt haben: Die 1,1 Prozent Abweichung sind so nicht entschieden. Eine Szene auf Tempo 40 mit jedem Takt (`schlacht_streng`) soll das klären.
- **1.000 gegen 1.000 endet durch Ruhe, nicht durch Sieg:** 201 stehen am Ende noch, 2.000 Takte lang fällt keiner. Sie gehen ohne Befehl nicht aufeinander zu (Einzelspiel, ohne Trupp).
- **Das Auge liest bei 2.000 Einheiten rund jeden 4. Takt, einen sauberen Rahmen rund jeden 10. Takt** (1.351 gelesen, 565 rein in 5.666 Takten). Die Warteschlange zum Schreiben war 7.611-mal voll: Die Platte bremst das Lesen, nicht das Spiel. Für jeden Takt braucht es hier Tempo 40.
- Warum die Schützen so schnell fallen, ist nicht einzeln ausgewertet; Feuer ist nicht getrennt gezählt. Die Reihen mit 100 Einheiten sind nicht gefahren, sie sind aus den großen Schlachten gerechnet, sobald A1 bis A3 laufen.

## Szene Schlacht mit jedem Takt, 03.11. 20:30

20 gegen 20, Nahkampf gemischt, Tempo 40 streng. **Die Regel „Schaden mehrerer Angreifer addiert sich“ stimmt in allen 2.417 gewerteten Fällen, keine Abweichung.** Die 1,1 Prozent aus den Schlachten auf Tempo 1000 waren Angreifer, die zwischen zwei Rahmen gewechselt haben. Beleg: `schlacht_streng.regeln.json`.

## Gegenprobe im Gefecht, 03.11. 20:08 bis 20:25

Zwei Mensch-Plätze ohne KI, die Lords stehen, Spielart 99 und 3 nachgelesen. **Feste Startplätze sind nötig:** Ohne sie bekommt Spieler 2 Platz 246, also 6 Bogenschützen, aber weder Burg noch Lord. Der Lord fehlt in diesen Szenen, sein Fall ist eine eigene Szene.

| Szene | Ergebnis gegen den Editor | Beleg |
|---|---|---|
| Laufen, Direktbefehl | 36 von 36 Zeilen gleich, also auch der Streitkolbenkämpfer: 16 Takte je Feld in beiden | `laufen_g.regeln.json` |
| Nahkampf | Tabellen gleich. Bei 169 von 171 Paaren sind die Leben ab Takt 2 je Takt gleich, 2 Paare beginnen 1 Takt versetzt: Streitkolbenkämpfer gegen Streitkolbenkämpfer, Schwertkämpfer gegen Leiterträger | `gefecht_gegen_editor.txt`, Befehl oben in `gefecht_gegen_editor.py` |
| Beschuss | 18 von 18 Arten: kein Betrag ungeklärt, gleiche Geschosswerte | `beschuss_g.regeln.json` |

**Vorhersage widerlegt:** Im Plan stand, der Streitkolbenkämpfer gehe im Editor und renne im Gefecht (`UpdateMaceman`, die Stelle hat UCP umgebaut, Sprung bei 0x560B4F). Er ist in beiden gleich schnell, mit Direktbefehl 16, mit Truppenbefehl 12 Takte je Feld. Die Spielart ändert beim Laufen hier nichts.

**Der erste Rahmen im Gefecht zeigt noch den alten Stand:** Takt 1 nach dem Weiterlaufen sieht aus wie Takt 0, in Takt 2 stehen dann zwei Takte Schaden. Darum sah der Prüfer je Paar einmal den doppelten Wert. Das ist das Lesen, nicht das Spiel: Ab Takt 2 sind die Leben dieselben wie im Editor. Warum es nur im Gefecht so ist, weiß ich nicht. Der Prüfer zählt diesen Fall und versteckt ihn nicht.

## Szene Truppenbefehl, 03.11. 20:23 und 20:30

**Der wichtigste Fund zum Tempo: Mit dem echten Truppenbefehl (Spielbefehle 16 und 17) laufen die meisten Einheiten schneller als mit dem Direktbefehl.** Das erklärt die kleineren Werte aus den echten Partien (L80: Bogenschütze 11,5, Pikenier 24). In Editor und Gefecht gleich.

| Takte je Feld | Arten | Direktbefehl |
|---|---|---|
| 12 | Bogenschütze (E_ARCHER 22), Speerträger (E_SPEAR 24), Streitkolbenkämpfer (E_MACE 26), Leiterträger (E_LADDER 29), Tunnelgräber (TUNNELER 5), arabischer Bogenschütze (A_ARCHER 70), Sklave (A_SLAVE 71), Schleuderer (A_SLINGER 72) | 16 |
| 10,4 bis 12,1 | Ritter (E_KNIGHT 28), Berittener Bogenschütze (A_HARCHER 74) | 16 |
| 16 | Ingenieur (E_ENGINEER 30), Assassine (A_ASSASSIN 73) | 16 |
| 24 | Armbrustschütze (E_XBOW 23), Pikenier (E_PIKE 25), Mönch (E_MONK 37), arabischer Schwertkämpfer (A_SWORDSMAN 75), Feuerwerfer (A_FIRETHROWER 76), Lord (55) | 24 |
| 32 | Schwertkämpfer (E_SWORD 27) | 32 |

Warum der Truppenbefehl schneller ist, steht noch nicht im Code nachgelesen. Gerade und schräg kosten je Feld gleich viel.

## Szene Anlauf, 03.11. 20:25 und 20:30

Jeder Nahkämpfer mit Angriffsbefehl auf eine unbemannte Ramme, 60 Felder weit (`reichweite.regeln.json`). **Im Angriff laufen sie so schnell wie mit dem Truppenbefehl,** Editor und Gefecht gleich: Speerträger 11,9, Pikenier 23,9, Streitkolbenkämpfer 11,9, Schwertkämpfer 31,9, Ritter 10,6, Mönch 23,9, Assassine 15,7, arabischer Schwertkämpfer 23,8 Takte je Feld. Sie bleiben 1,8 bis 2,4 Felder vor der Ramme stehen und schlagen dort jeden Takt.

**Mein Aufbau war für die Schützen falsch:** Sie laufen auf einen Angriffsbefehl nicht los. Der Code setzt das Ziel und hält sie an (`giveTribeAnInstruction`, `UIT_UNIT_ATTACK_UNIT`, `makeUnitStopWalkingByClearingPathProgressState`), sie schießen nur, wenn das Ziel schon in Reichweite steht. Darum die Leiter unten.

## Szene Schussweite, 03.11. 20:30 und 20:35

Jede Art mit Angriffsbefehl auf eine Ramme in Abständen rund um den Tabellenwert. Gezählt werden nur Geschosse auf das befohlene Ziel. Belege: `schussweite.regeln.json`, `schussweite_pfeil.regeln.json`.

| Geschoss | Arten | Schießt bis | Schießt nicht mehr auf | Tabelle 0x5B6358 |
|---|---|---|---|---|
| Bolzen | Armbrustschütze | 40 Felder | 41 | 40, stimmt |
| Stein | Schleuderer | 18 | 19 | 18, stimmt |
| Feuer | Feuerwerfer | 11 | 12 | 11, stimmt |
| Pfeil | Bogenschütze, arabischer Bogenschütze, Berittener Bogenschütze | 40 | 42 | **54, stimmt nicht.** 41 ist nicht gefahren |

Abstände hier auf ebener Bahn, ohne Höhe. Warum der Pfeil nicht bis 54 reicht, ist offen: Der Tabellenwert 54 steht beim Geschoss, die Grenze kommt also von anderswo.

## Geschosse, aus den Aufzeichnungen gelesen

Neu auslesbar: Jedes Geschoss steht mit Art, Schütze (`unitID_OR_seaGullID`, 794 von 795 gehören dem Besitzer), Ziel (`unitID`), Zielpunkt und Flugzeit in `DAT_EntityState`.

| Geschoss | Mikro je Takt (8 Mikro = 1 Feld) | Stehendes Ziel, Verlust rund um den Einschlag |
|---|---|---|
| Pfeil | 5,75 | 336 von 353 |
| Bolzen | 6,18 | 68 von 70 |
| Stein | 5,63 | 247 von 251 |
| Feuer | 3,78 | 68 von 82 |

Editor, Szene Beschuss, im Gefecht ähnlich (`beschuss_g.geschosse.json`). Befehl und Zahlen: `geschosse_beschuss.py`, `geschosse_beschuss.txt`. Der Verlust kommt im Takt der Landung oder bis zu 2 Takte davor. **Die rund 5 Prozent ohne Verlust (37 von 795), nachgerechnet am 04.11.: 17 Ziel war schon tot, 3 ein anderer verlor am Ort Leben, 3 Ziel lief 2 Felder oder mehr, 10 Feuerschüsse wirken erst 6 bis 13 Takte nach der Landung, 4 Feuerschüsse zeigen 60 Takte keinen Verlust, das ist offen (`geschosse_ohne_verlust.txt`, `rufen_kurzproben/feuer_rest.py`).** Zielwahl: 378 von 795 Schüssen gehen auf den nächsten Feind, 417 nicht.

## Szene Laufendes Ziel, 03.11. 20:39

Jeder Fußschütze mit Angriffsbefehl auf einen Streitkolbenkämpfer, der 8 Felder entfernt quer hin und her läuft. Tempo 100. **Meine Vorhersage „laufendes Ziel wird verfehlt“ ist widerlegt.** Beleg: `laufziel.regeln.json`.

| Schütze | Getroffen von gelandet | Zielpunkt zum Läufer beim Abschuss, in Mikro | beim Einschlag |
|---|---|---|---|
| Bogenschütze (E_ARCHER 22) | 10 von 10 | 5 | 1 |
| Armbrustschütze (E_XBOW 23) | 6 von 6 | 4 | 3 |
| arabischer Bogenschütze (A_ARCHER 70) | 14 von 14 | 4 | 2 |
| Schleuderer (A_SLINGER 72) | 22 von 23 | 7 | 3 |
| Berittener Bogenschütze (A_HARCHER 74) | 15 von 17 | 5 | 2 |
| Feuerwerfer (A_FIRETHROWER 76) | 4 von 6 | 2 | 7 |

**Das Spiel schießt voraus:** Der Zielpunkt steht beim Abschuss fest und liegt beim Einschlag fast genau beim Läufer (1 bis 3 Mikro, 8 Mikro sind ein Feld). Pfeil, Bolzen und Stein: 67 von 70. Ausweichen hilft also nur, wenn der Läufer während des Flugs die Richtung ändert; ob das die 3 Fehlschüsse sind, ist nicht einzeln geprüft.

## Szene Haltung, 03.11. 20:41

Befehl 70 in der Befehlstabelle der exe (`lauf_s_plan/befehl_nummern.txt`), Werte Gruppe und Haltung, nachgelesen in `tribes[].unitStance`. Erst die Gruppe, dann die Haltung, zuletzt der Feind. Belege: `haltung.regeln.json`, `haltung2.regeln.json`.

| Haltung | Abstand | Ritter (E_KNIGHT 28) | Speerträger (E_SPEAR 24) | Ingenieur (E_ENGINEER 30) |
|---|---|---|---|---|
| aggressiv | 24 Felder | reagiert nach 49 Takten | nach 84 | nein |
| aggressiv | 26 | nein | nein | nein |
| defensiv | 4 | nach 100 | nach 89 | nein |
| defensiv | 6 | nein | nein | nein |
| stehen | 4 | nein | nein | nein |

**Bestätigt für alle, die schlagen können.** Der Ingenieur reagiert nie: Er kann nicht schlagen (`DAT_UNIT_CAN_MELEE` 0), das hatte der Plan nicht bedacht. Schützen sind hier nicht gefahren.

## Szene Besatzung, 03.11. 20:41

Je Gerät volle Besatzung und ein Mann zu wenig, einmal schießen, einmal fahren, Anweisung 16 zum Einsteigen. **20 von 20 Fällen bestätigt:** Mit einem Mann zu wenig steigt keiner ein, das Gerät rührt sich nicht. Beleg: `besatzung.regeln.json`.

| Gerät | Besatzung | Schusstakt | Takte je Feld |
|---|---|---|---|
| Katapult (S_CATAPULT 39) | 2 | 130 (Lauf K: 123) | 77 |
| Trebuchet (S_TREBUCHET 40) | 3 | 296 | fährt nicht |
| Mangonel (S_MANGONEL 41) | 2 | Salve: 77 Geschosse in rund 1.600 Takten | fährt nicht |
| Ballista (S_BALLISTA 61) | 2 | 155 | fährt nicht |
| Feuerballiste (S_FBALLISTA 77) | 2 | 100 | 77 |
| Ramme (S_BATTERINGRAM 59) | 4 | | 77 |
| Belagerungsturm (S_TOWER 58) | 4 | | 77 |
| Schild (S_SHIELD 60) | 1 | | 77 |

Das Tempo ist für alle gleich, mit Truppenbefehl, 20 Felder. Bemannt waren alle nach 356 Takten, das meiste davon Warteschlange meines Moduls (20 Takte je Befehl).

## Szene Reichweite der Geräte, 03.11. 20:49

| Gerät | Tabelle | Gemessen | Beleg in `geraete_weite.regeln.json` |
|---|---|---|---|
| Ballista | 68 | Schießt auf 68, auf 70 nicht | eindeutig |
| Feuerballiste | 39 | Schießt auf 39, auf 41 nicht | eindeutig |
| Katapult | 57 | Auf 59 Felder befohlen, weitester Einschlag 462 Mikro (57,8 Felder) | Der Stein streut, einzelne Stufen sind leer. Passt, nicht scharf |
| Trebuchet | 68 | Auf 70 befohlen, weitester Einschlag 552 Mikro (69 Felder) | wie oben |
| Mangonel | 54 | Auf 54 befohlen, Einschlag 450 Mikro, auf 56 kein Stein aufs Ziel | Er schießt vor allem auf Nachbarn |

Beim Pfeil stimmte die Tabelle nicht, bei den Geräten passt sie. Katapult und Trebuchet zielen aufs Feld, nicht auf die Einheit (`targetingType` wird `UIT_ATTACK_LAND`).

## Szene Belagerung, 03.11. 20:50

**Meine Regel „Katapult 20, Trebuchet 60, Mangonel 5 je Stein“ war falsch gelesen, die neue stimmt.** Das Spiel im Speicher ist nicht die exe: UCP setzt in `processEntityHitBuildingOrUnit` andere Werte ein (Stellen in `lauf_k_20261102/code_aenderungen.csv`). Ein Stein wirkt direkt und auf Nebenfelder, und ein voller Treffer erwischt 6 Nebenfelder.

| Gerät | Direkt (exe, UCP) | Nebenfeld (exe, UCP) | Voller Treffer gerechnet | Gemessen |
|---|---|---|---|---|
| Katapult | 20, **40** | 10, **15** | 40 + 6 x 15 = **130** | 29 x 130, 14 x 100 (4 Nebenfelder), je 1 bis 2 x 75, 60, 45 |
| Trebuchet | 60, **120** | 30, 30 | 120 + 6 x 30 = **300** | 1 x 300 |
| Mangonel | 5 | 0 | 5 | 5 x 5, 1 x 10 |

| Weiter gemessen, ohne Regel | Verlust je Treffer | Fälle |
|---|---|---|
| Ballista | 2 und 5 | 4, nur an der Hütte |
| Feuerballiste | 10 | 4, nur an der Hütte |
| Ramme | 125 | 3, an Hütte, Tor, Turm |

- 53 Gebäudearten standen gegen ein Katapult, 27 davon wurden getroffen, je Ziel 3 Steine (156 insgesamt). **1 Wert ist ungeklärt:** 20 am Marktplatz.
- **Kein Leben:** Burg und Mordgrube (`maxHealth` 0), kein Verlust.
- Nicht setzbar mit meinem Befehl: Farmen, Steinbruch, Lager, Eisenmine, Pechgrube, Pechgraben. Vermutlich brauchen sie besonderen Boden. Für Trebuchet, Mangonel, Ballista und Feuerballiste stehen deshalb nur wenige Ziele drin, die Zeile im Plan „gegen 4 Klassen“ ist nur zum Teil erfüllt.
- 6 Zeilen nahmen wegen eines Fehlers von mir das Gebäude des Nachbarn. Der Prüfer zählt sie als „falsches Gebäude“, das Werkzeug prüft jetzt Art und Ort. Beleg: `belagerung.regeln.json`.

## Szene Nahkampf gegen Gebäude, 03.11. 20:42 und 20:51

Tempo 40, jeder Nahkämpfer direkt daneben, Angriffsbefehl. Verlust je Schlag und Takte zwischen zwei Schlägen. Zwei Läufe, weil nicht jedes Gebäude jedes Mal stand; wo beide einen Wert haben, sind sie gleich. Belege: `gebaeude_nah_erster.regeln.json`, `gebaeude_nah.regeln.json`.

| Art | Takte je Schlag | Hütte (200 Leben) | Großes Tor (3.000) | Kleines Tor (1.500) | Wachturm (500) |
|---|---|---|---|---|---|
| Speerträger (E_SPEAR 24) | 48 | 10 | 2 | 2 | 3 |
| Pikenier (E_PIKE 25) | 28 | 40 | 5 | 5 | 10 |
| Streitkolbenkämpfer (E_MACE 26) | 48 | 80 | 5 | 5 | 15 |
| Schwertkämpfer (E_SWORD 27) | 60 | 100 | 10 | 10 | 10 |
| Ritter (E_KNIGHT 28) | 72 | 100 | 10 | 10 | 10 |
| Mönch (E_MONK 37) | 24 | 20 | 2 | 2 | 3 |
| Lord (55) | 56 | 100 | 10 | 10 | 10 |
| Sklave (A_SLAVE 71) | 93 | **kein Verlust** | 1 | 1 | 1 |
| Assassine (A_ASSASSIN 73) | 93 | 75 | 3 | 3 | 5 |
| arabischer Schwertkämpfer (A_SWORDSMAN 75) | 96 | 100 | 10 | 10 | 10 |

Gegen die Burg (kein Leben) gibt es keinen Verlust, das ist nur an einem Fall gesehen. Warum der Sklave die Hütte nicht beschädigt, ist offen: Vermutlich zündet er sie an, das ist nicht nachgesehen. **Lager, Holztor und Mauern fehlen.**

## Szene Angriff auf einen Punkt, 03.11. 20:51

Liste V6, alle 8 zugleich, Speerträger im Block, 30 Felder bis zum Ziel. Ein Besitzer, die Ziele leer. Ankunft in Takten nach dem Start. Beleg: `punkt.regeln.json`.

| Ziel | Einheiten | Angekommen (innerhalb 3, bei Gebäuden 6 Felder) | 10, 50, 90 Prozent | Letzter | Dichtestes Feld |
|---|---|---|---|---|---|
| Feld | 10 | 10 | 349, 365, 377 | 385 | 4 |
| Feld | 100 | 39 | 352, 398, 431 | 460 | 8 |
| Feld | 500 | 75 | 407, 494, 570 | 604 | 15 |
| Kleines Tor | 100 | 100 | 332, 391, 460 | 510 | 10 |
| Kleines Tor | 500 | 248 | 369, 478, 661 | 740 | 15 |
| Wachturm | 100 | 100 | 332, 396, 500 | 548 | 12 |
| Lücke in der Mauer | 100 | 68 | 395, 484, 571 | 601 | 14 |
| Lücke in der Mauer | 500 | 215 | 473, 649, 794 | 852 | **54** |

- **Einheiten blockieren sich nicht hart:** Durch die Lücke von 3 Feldern laufen sie gestapelt, bis zu 54 auf einem Feld. Die ersten kommen trotzdem später an als ohne Mauer, der Mittelwert von 500 steigt von 494 auf 649 Takte.
- **Ein Befehl auf ein Feld ist kein Treffpunkt:** Von 500 stehen nur 75 innerhalb 3 Feldern, der Rest verteilt sich um den Punkt.
- **Wegwahl:** Von den 100 gingen alle durch die Lücke. Von den 500 gingen 367 durch die Lücke, 127 standen an anderer Stelle der Mauerlinie. Das Letzte heißt: um die Mauer herum oder gestaut, das ist nicht unterschieden.
- Die Mauern gehörten in dieser Szene wegen des Kanalfehlers (unten) Spieler 1 statt 2. Für den Weg macht das keinen Unterschied, eigene Mauern sperren ohne Tor genauso.

## Sonderfälle, 03.11. 20:52 bis 23:17

Liste V7, in mehreren Durchgängen. Belege: `sonder1`, `sonder2`, `sonder_g`, `sonder2_g`, `sonder3`, `sonder3_g` (dazu `_starttruppen`, `_drei_opfer`), `sonder4_g`, `sonder5`, `sonder5_g`, `sonder6_g`, `sonder7_g`, je `.regeln.json`. Zeitpunkte, Höhe, Pech-Zustand und Hunde: `belege_sonderfaelle.txt`.

**Burgbereich, die wichtigste Regel dabei:** Im Gefecht gehen Mauer, Graben, Pechgraben, Käfig und Turm nur nahe der eigenen Burg (`checkBuildingCanBePlacedHere`: `getCastleBuildRangeForMapSize`, `isTileInRangeOfKeepRange`). Weit weg antwortet das Spiel mit `i`, Hütte und Ölschmelze gehen überall. Bis 45 Felder um die Burg war fast alles erlaubt, die Grenze selbst ist nicht ausgemessen. Beim Absetzen meldet der Befehl trotzdem Erfolg. Belege: `probe_befehle_gefecht.txt`, `probe_burgbereich.txt`. Im Karteneditor gilt der Bereich nicht.

**Starttruppen, die zweite Falle:** Im Gefecht kommen je Spieler 6 Bogenschützen bei Takt 202 und 8 Speerträger bei Takt 403 an der Burg dazu. Wer vorher räumt, hat sie danach im Feld. So trafen 17 Pfeile die Opfer der Hunde (Lauf 21:41), und 33 Pfeile die Tunnelgräber (Lauf 22:41). Geräumt wird jetzt erst ab Takt 410, und der Prüfer zeigt je Posten, was nicht vom Plan kommt (`fremd`). Alle Gefecht-Szenen nachgesehen, sonst trifft es keine weitere: `stoerung_starttruppen.txt`.

| Fall | Ergebnis | Stand |
|---|---|---|
| Feuer an Gebäude | Feuerwerfer zündet eine Hütte. Sie verliert meist 4 Leben auf einmal, im Schnitt alle 20 bis 25 Takte, und ist nach 1.390 Takten weg. Die Hütte daneben fängt 989 Takte nach der ersten Feuer und brennt in 982 Takten ab | gemessen, Löschen nicht |
| Pechgraben | Im Burgbereich mit `baue` gesetzt. **Ein Feuerwerfer zündet ihn:** Zustand 1, 2, 3, nach rund 230 Takten weg (auf 25 Takte genau). Der Bogenschütze zündet ihn nicht: Anweisung 34 wird angenommen, es fliegen nur normale Pfeile. Von 5 Bauten standen 2 | gemessen, Schaden des Brands nicht vom Feuerwerfer getrennt |
| Kochöl | Anweisung 15 schickt Ingenieure zur Ölschmelze, mit Pech in der Schmelze (gesetzt) holt einer das Öl (`resourceToDeposit` 1). Auf Anweisung 20 warf er aus 10 bis 11 Feldern nicht. Nach einem Laufbefehl auf 4 Felder warf er: erste Flamme 69 Takte nach dem Befehl, 49 Flammen, der Speerträger stirbt 165 Takte nach dem ersten Verlust. **Der Werfer verbrennt selbst,** der zweite Ingenieur verliert 2.250. Die Reichweite dazwischen ist nicht gemessen | gemessen |
| Mordgrube | **18.000 Schaden je Grube,** beim Darüberlaufen (Pikenier: 3 Gruben, 3 x 18.000, je 24 Takte auseinander). Die Gruben sind rund 2.100 Takte später weg | gemessen |
| Hunde | **Frühere Aussage falsch:** „Im Gefecht töten sie 3 Speerträger“ stimmte nicht, das waren 17 Pfeile der eigenen Starttruppen (je 3.000). Sauber gefahren: Mit dem Käfig stehen 4 Hunde bereit (Art 67, Besitzer 0). **Sie kommen von selbst, wenn genug Feinde nahe sind:** Bei 8 Speerträgern 6 bis 7 Felder entfernt erster Biss nach 60 bis 90 Takten, 80 Leben je Takt und Hund, alle 8 tot bei Takt 663. Ein Hund starb, drei gingen zurück, der Käfig blieb heil. Bei 3 Speerträgern blieben die Hunde drin, niemand verlor etwas. Laut Code: mehr als 5 Feinde oder Truppenwert über 24 binnen 16 Schritten, die genaue Grenze ist nicht gemessen. **Spielbefehl 74** setzt 4 weitere Hunde auf den Käfig, die sich nicht bewegten. Nach rund 1.040 Takten sind sie weg, dann fällt der Käfig, dann gehen auch die ersten vier | gemessen, Befehl 74 ungeklärt |
| Kuhwurf | Anweisung 22 wirkt nur mit Kuh-Zähler (`playerDataArray[].counter`, sonst Steine), den hat dieser Messlauf gesetzt, normal füllt ihn der Milchhof. 1 Kuh, 7 Giftwolken, Pikeniere verlieren bis zu 8.150 und 150, erster Verlust rund 640 Takte nach dem Befehl. Trotz Zähler 5 flog nur eine Kuh, Grund offen | gesehen, wenige Fälle |
| Graben | Im Burgbereich: Plan mit Spielbefehl 21, Flag 2 = 0 (Bit 0x4000). 3 Sklaven heben alle 9 Felder aus (Bit 0x40000000), in drei Läufen gleich: je 3 Felder bei 351 bis 376, 601 bis 650, 875 bis 903 Takten, **rund 260 Takte je Feld und Sklave** (auf 25 Takte genau). Flag 2 = 2 wäre laut L126 der Editorweg. **Zuschütten geht nur beim Graben eines anderen Teams:** Eigene Sklaven taten auf Anweisung 7 nichts (Code: `findNearestFriendlyMoatTileForDigging`). 2 Sklaven von Spieler 2 schütteten alle 9 Felder zu, Befehl bei Takt 1500, erstes Feld bei 2054, letztes bei 2929, rund 220 Takte je Feld und Sklave (auf 25 Takte genau). Stehen die Gräber noch daneben, erschlagen sie die Zuschütter | gemessen |
| Leiter | Anweisung 24 nimmt die **Feldnummer** der Mauer, nicht x und y. Leiterträger gehen an die Mauer von Spieler 2, Speerträger steigen hinauf: Höhe von 8 auf 98, oben rund 780 Takte nach ihrem Laufbefehl | gemessen |
| Belagerungsturm | Fährt an die Mauer und hält davor. Anlegen nicht geprüft | gesehen |
| Mauerangriff | Anweisung 23 nimmt ebenfalls die Feldnummer. Tunnelgräber gehen hin und schlagen | gesehen |
| Tunnel | **Erreicht.** Der Tunnel ist ein Bauwerk: Bauen mit Mapper 66, Größe 3 und dem Trupp des Gräbers, wie der Knopf beim Menschen. Laut Code erlaubt das Spiel das nur, wenn binnen 76 Schritten eine feindliche Mauer oder ein kleiner Turm (Art 74 bis 76) steht. In der Probe ohne beides gab es bis 95 Felder um die gegnerische Burg keine erlaubte Stelle (`probe_tunnel.txt`). Je Eingang geht **ein** Gräber, der zweite im Trupp blieb stehen. Ablauf: Weg zum Eingang, **rund 572 Takte** Eingang bauen (Art 85 wird Art 50 mit 100 Leben), **rund 223** Vorbereitung, **rund 48 je Feld** unter der Erde (12 Felder 569, 30 Felder 1.434), **65** am Ziel. Vom Befehl bis zum Fall: 12 Felder rund 1.580, 30 Felder 2.440. Dann ist das Ziel weg: Der Wachturm verliert 5 x 50 in 5 Takten und fällt mit 250 von 500 Leben. Von der Mauer fällt **ein** Stück (Höhe 98 auf 6). Der Gang wird zur Grube (Höhe 8 auf 0), Eingang und Gräber sind weg. **Abbruch:** Ein Speerträger nimmt dem Eingang 10 Leben je 48 Takte. Bei 0 (Takt 1710) verschwindet der Gräber, der Gang stürzt ein, der Turm bleibt heil, obwohl der Gräber nur noch 2 Felder entfernt war | gemessen, große Türme nur laut Code nicht |
| Schild | **Pfeile mit Befehl auf den Mann hinter dem Schild:** Er verliert nichts, der Schild verliert 1.200, der Mann ohne Schild 48.000 | bestätigt |
| Höhe | Bogenschützen über die Leiter auf der Mauer (Höhe 98): Sie schießen auf 38 Felder, auf 42, 46, 50 nicht. Schaden 1.500 je Pfeil an der Ramme wie am Boden. **Die Mauer bringt in dieser Probe keine Mehrreichweite.** Die Abstände 39 bis 41 sind nicht gefahren | gemessen |
| Tor | Befehl 45 wirkt, `gateState` wechselt von 257 auf 268. Durchgang nicht geprüft, das Tor stand ohne Mauer | gesehen |

## Einzelpunkte und Nachlauf, 04.11.

Alle 75 Punkte der Checkliste sind gegen ihre Erwartung gerechnet: `Punkte_Lauf_S.md`. Stand nach dem ersten Nachlauf: 41 bestätigt, 11 widerlegt, 4 teils, 2 gemessen, 14 Lage fehlte, 3 offen. Stand nach dem zweiten: 52 bestätigt, 16 widerlegt, 4 gemessen, 2 teils, 1 Lage fehlt, 0 offen. Der Nachlauf hat dafür die fehlenden Lagen gefahren: `sonder8` (Editor), `sonder8_g`, `sonder9_g`, `lord2_g` (Gefecht), Auswertung `punkte_rechnung6.txt` und `punkte_rechnung7.txt`.

**Widerlegt:**

- **Besatzung (P334, P337):** Der Zähler springt von 0 auf die Sollzahl, mit zu wenig Leuten bleibt er 0.
- **Tor (P303):** Bei einem Feind auf 24 und 26 Feldern geschah nichts, Reaktion kam bei 3 bis 16 Feldern. gateState2 springt auf 100, nicht auf 1.200.
- **Öl (P323):** Der Träger warf in keiner Haltung von selbst, der Feind erschlug ihn.
- **Trupp (P326):** Die Zielfelder liegen schräg 1 auseinander, nicht 2.
- **huntedBy (P339), countArabianArcher (P365), Giftwolke 828 Takte (P297), Ramme 125 je Treffer (P345):** wie in `Punkte_Lauf_S.md`.
- **Sklave und Assassine an der Mauer (P366, P367):** kein Schaden.

**Mauer je Schlag (2 Nachbarn):**

| Einheit | Schaden | Schläge je Stück |
|---|---|---|
| Ritter | 10 | 8 |
| Schwertkämpfer, arabischer Schwertkämpfer | 10 | 8 |
| Pikenier, Keulenträger | 5 | 15 |
| Speerträger | 2 | 36 |
| Sklave, Assassine | 0 | - |

Ein Stück fällt, wenn der Schaden über 70 steigt. Am Ende einer Mauer (1 Nachbar) 1,5-fach, an einer Kreuzung (3 Nachbarn) halb, abgerundet.

**Bestätigt im Nachlauf:** Der Sieger bekommt beim Tod des Lords 25 % des gegnerischen Goldes (+1.000 bei 4.000). Nur die Grenze 39 zählt ums Lager, 41 nicht. Der Belagerungsturm legt mit Anweisung 23 an, es entsteht ein Gebäude der Art 69, die Bemannung geht auf 0. Eine Ramme fährt nur mit 4 Mann. Ein berittener Bogenschütze schießt im Laufen, ein Armbrustschütze nicht. Ein Ziel im Mauerring lässt die Einheit stehen.

**Nachladen (P308):** Laut Code nur für die KI. Beim Menschen blieb die Munition trotz 200 Stein auf 0. **Befehl 86 (P309):** abgesetzt, ohne Wirkung, ungeklärt.

## Code-Abgleich und zweiter Nachlauf, 04.11. 16:50 bis 17:54

**Der wichtigste Fund des Tages: Das laufende Spiel ist nicht der Export.** Ich habe jeden Befehl aus dem Ghidra-Export mit dem Speicher von Instanz 2 verglichen, nur lesend: 814 von 428.114 Befehlen weichen ab, in 157 Funktionen. Dazu Tausende Werte in den Daten-Tabellen. Gemessen am Speicher: Die Programmdatei auf der Platte hat die Export-Werte (Tor 200, Ramme 50, Hunde 25), erst im Speicher stehen die neuen. Die Konfiguration nennt `o_responsivegates` und `rebalancer` (Liga), darum sage ich UCP3. Den Code von UCP3 selbst habe ich nicht gelesen. Beleg: `code_abgleich.py`, `code_abgleich.txt`, `code_abgleich.json`, `daten_abgleich.py`, `daten_abgleich.txt`.

Damit lösen sich meine „unerklärten“ Messwerte auf:

| Was | Export | Im Speicher | Gemessen |
|---|---|---|---|
| Tor reagiert unter | 200 Mikro (25 Felder) | 140 Mikro (17,5 Felder) | reagiert bei 17, nicht bei 18 |
| Tor bleibt zu nach Feind | 1.200 Takte | 100 Takte | gateState2 springt auf 100 |
| Ramme je Treffer | 50 | 125 | 125 |
| Pfeil, Bolzen, weiteste Stufe | 432 Mikro (54 Felder) | 320 Mikro (40 Felder) | Pfeil trifft bis 40, nicht mehr auf 42 |
| Munition auffüllen bis, und von mir gesetzte Geräte | 20 | 10 | 6 auf 10. Aus dem Zelt: 20 (Lauf K) |
| Nachladen je Einheit | +20 | +10 | 5 auf 15, KI in Lauf K +10 |
| Stein je Schuss beim Auffüllen | 1 Stein, 2 Schuss | 1 Stein, 1 Schuss | 2 Stein gaben +2 |
| Angst | 5 Prozent je Stufe | Tabelle 80 bis 140 Prozent | 105, 87 und 60 bei Grund 75 |
| Mauer je Schlag Speer, Pike, Keule, Tunnel | 4, 6, 6, 6 | 2, 5, 5, 20 | 2, 5, 5, 20 |
| Gebäude je Schlag Schwert, Ritter | 70 oder 6 | 100 oder 10 | Hütte 100, Tor und Turm 10 |
| Gebäude je Schlag Keule | 35 oder 4 | 80 oder 15 | Hütte 80 |
| Hunde kommen ab Wert | 25 | 16 | 3 Speerträger (Wert 12) nein, 4 (Wert 16) ja |

**Regel für alles Weitere:** Eine Zahl aus dem Export ist ein Grundwert. Vor jeder Aussage „der Code sagt“ steht der Blick in `code_abgleich.json`.

**Weg auf den Turm (sonder10, 12, 13, 14, 17, 21):** Sechs Läufe, drei Fehler von mir und eine falsche Erklärung:

1. Eine Mauerlinie, die auf ein Gebäude reicht, baut das Spiel gar nicht (gemessen sonder10). Laut Code (`validateWallBuildPath`) genügt auch eine Einheit auf der Linie. In sonder12 fehlten 2 von 4 Seiten eines Rings, die Ursache ist nicht belegt. Das Werkzeug liest jetzt nach, wiederholt bis zu 5 Mal und schreibt `mauer_fehlt` in den Plan, ein offener Ring fällt so auf.
2. Eine Treppe aus einem Feld springt von 8 auf 82. Die Treppe ist eine Linie weg von der Mauer: 82, 66, 50, 34, 18.
3. Die vier Turmecken sind gesperrt (Fläche 0, Bit 0x400), nicht der Eingang, wie ich gelesen hatte. Die Mitte ist begehbar.
4. **Falsche Erklärung, berichtigt:** Ich behauptete, der Laufbefehl müsse nach dem Bau warten, bis die Flächenkarte neu ist. In sonder14 hatte ich aber Zeit und Ziel zugleich geändert. Die Gegenprobe sonder21 zeigt: Der Befehl wirkt sofort, die Mauer hat schon bei Takt 0 Fläche 1. Es lag nur am Ziel.

Danach: 8 von 8 auf dem Wachturm. Die Grenze 5 gilt nur beim Mausklick. Beim Klettern steigt das Tempo um 4 und 5. Der Turm hat auf der Karte Höhe 8, das ist richtig so.

**Tor:** Die Kette 0, 1, 2, 3, 0 stimmt. Entwarnung: Feind geht ab Takt 1.000 weg, Tor öffnet ab Takt 1.185. Durch ein offenes Tor geht der Besitzer hindurch, um ein geschlossenes läuft er außen herum, bis ans Ende der Mauer.

**Löschen (sonder10_g):** Mit Brunnen brennt die Hütte 254 und beim zweiten Mal 221 Takte, ohne Brunnen waren es 960 bis 980 (sonder1). Die Feuerwache (Art 53, Arbeitsplatz der Brunnen) kommt von selbst und geht zum Feuer. Die Hütte verlor dabei 53 und 45 Leben.

**Angst (sonder10_g):** 5 Gärten geben Stufe +5, Schaden 140 Prozent. 5 Galgen geben Stufe -5, Schaden 80 Prozent. Wächst die Bevölkerung, sinkt die Stufe: von +5 auf +2 bei Takt 303. Die Stufe rechnet das Spiel aus den Bauten neu, ein gesetzter Wert hielte nicht.

**Warum der Truppenbefehl schneller ist:** Der Direktbefehl läuft im Zustand 2 mit Tempo-Zuschlag 0, der Truppenbefehl im Zustand 101 mit Zuschlag 1 (`laufen`, `laufen_trupp`, `updateUnits`).

**Zwei Aussagen von mir waren falsch und sind berichtigt:**

- „finalKillMatrix ändert sich nie“: Das Feld stand gar nicht in der Aufzeichnung, ich hatte nichts gelesen. Aus dem Speicher gelesen stimmt es: [Töter][Opfer] +1.
- „Spielbefehl 86 ohne Wirkung, ungeklärt“: Mein Befehl hatte den falschen zweiten Wert.

**Beim Melden hat mich mein eigener Ablauf aufgehalten:** Ein Lauf hängt an der Gegenprobe. Sie schlug an, also fuhr nichts, und ich meldete fälschlich „Szenen zu Ende“. Das Werkzeug war richtig, meine Meldung nicht.

**KI aus Lauf K (`punkte_rechnen_k.py`):** Kein Wiederaufbau, solange ein Feind unter 120 am Lord steht: 1 von 117 Fällen. Sperre nach Zerstörung: 10, dann -1 alle rund 800 Takte. Steinbruch: 4.000, sobald der Steinmetz fällt. Mönche der Kathedrale: Zustand 0x69 gesehen.

## Befehle aus Lauf F, 04.11. 18:05 bis 18:14

Szenen `sonder19`, `sonder19_g`, `sonder20_g`, Rechnung `punkte_rechnung14.txt`, `punkte_rechnung15.txt`. Zelte aus Lauf K: `punkte_rechnung_k.txt`.

| Was | Ergebnis |
|---|---|
| Mauerlücke | 3 Ritter brechen ein Stück auf (Takt 1.478). Der Laufbefehl vorher wirkt nicht, der bei Takt 2.500 führt durch die Lücke in den Ring |
| Ritter an der Mauer | **Berichtigt: 10 je Schlag, nicht 15.** Die 15 aus sonder8 war ein Mauerende: Er brach erst das Nachbarstück. Code und sonder19 sagen 10 |
| Hunde | Täter belegt (Art 67, Besitzer 0). 3 Speerträger nein, 4, 5, 6 ja. Grenze Wert 16 wie im Speicher, im Export 25 |
| Lager als Ziel | 3 Schwertkämpfer daneben, Angriffsbefehl: Zustand 107 für einen Augenblick, dann nichts. Das Lager verlor in 3.000 Takten kein Leben |
| Steuer | Spielbefehl 34 setzt taxesSetting, 2 auf 7 |
| Sammelpunkt | Spielbefehl 102 setzt den Punkt der Kaserne |
| Turm reparieren | Spielbefehl 68: 200 auf 500 Leben, Holz -5 wie der Befehlswert |
| Abreißen | Spielbefehl 41: Mauerstück weg. Spielbefehl 29: Hütte weg |
| Mauer mit zu wenig Stein | 3 Stein, 15 Felder verlangt: 7 gebaut, also 2S+1 |
| Heer am Limit | Das Limit ist 1.160. Der gesetzte Wert blieb in der Aufzeichnung unsichtbar, geworben wurde weiter. Nicht erreicht |
| Zelte der KI | Katapult bis 319, Trebuchet bis 639, Ramme bis 644, Schild bis 121, Feuerballiste bis 312. Art 83 ergibt die Ramme: Der Name BT_SIEGETOWER im Typ-Verzeichnis ist falsch |
| Produktivität | Stufe -5 bis +5 laut Speicher 180, 164, 148, 132, 116, 100, 92, 84, 76, 68, 60. Gemessen +5: 60, +2: 84, -5: 180 |

**Lauf F steht damit bei 103 bestätigt, 11 widerlegt, 73 gemessen, 11 gesehen, 42 Lage fehlt, 1 offen.** Die übrigen fehlenden Lagen sind Einzelfälle: Bündnis, Grenzen, die nur beim echten Klick oder bei 1.160 Mann greifen, und reine Anzeige.

## Fall des Lords, 03.11. 20:59

Im Gefecht. Der Lord geht am Anfang von selbst auf die Burg, Ritter finden dorthin keinen Weg. Mit Truppenbefehl kommt er herunter, schaffte es aber nicht in 600 Takten zum Ring aus Rittern. Er fiel darum per Befehl (`per_befehl` in `lord_g.plan.json`). **Spätestens 13 und 5 Takte nach seinem Verschwinden meldet das Spiel das Ende** (`GAMEOVER`, zwei Läufe, die Zahl enthält das Anhalten), die Ansicht bleibt 14. Der Steintod dauert rund 306 Takte. Das Ende nach einem echten Kampf zeigt Lauf K.

## Meine Fehler in diesem Lauf

- **Der Kanal überschrieb den Spieler.** `liste` setzte bei jedem Befehl Spieler 1. Alle Befehle für Spieler 2 liefen als Spieler 1 oder wurden abgelehnt, die Mauern gehörten dem falschen Spieler. Erst die Sonderfälle zeigten es. Das erste Schild-Ergebnis war deshalb wertlos, es ist neu gefahren. Behoben, mit Test.
- **Prüffall startete echte Szenen.** Beim Prüfen meiner Tests (ein absichtlich eingebauter Fehler) liefen um 19:57 und 20:01 echte Szenen auf Instanz 2. Instanz 5 war nie betroffen. `los` bricht jetzt aus Tests heraus ab. Die Aufzeichnungen liegen in `laeufe/versehen_20261103/`.
- **Schützen im Angriffsbefehl:** Ich hatte angenommen, sie laufen los. Der Code hält sie an.
- **Schaden am Gebäude:** Ich hatte die Werte der exe genommen, UCP ändert sie.
- **Lord:** Ich hatte nicht geprüft, wo er steht.
- **Höhe, falsche Zwischenaussage:** Im ersten Durchgang stand die Mauer gar nicht, der Befehl meldet auch ohne Burgbereich Erfolg. „Der Pfeil trifft von der Mauer auf 46 Felder“ stimmte nicht, das stand kurz in Ergebnis, Handbuch und Register und in meiner Nachricht. Vermutlich flogen Pfeile in der Reihe zu weit, nachgeprüft ist das nicht.
- **Vermutung widerlegt:** Ich hielt zuerst das angehaltene Spiel für die Ursache, die Probe zeigte: Es ist der Burgbereich.
- **Hunde falsch zugeschrieben:** „Im Gefecht töten sie 3 Speerträger“ stand in Ergebnis, Handbuch, Register und Wissensstand und in meiner Zwischenmeldung. Es waren 17 Pfeile der eigenen Starttruppen. Ich hatte die Verluste der Opfer gelesen, aber nicht nachgesehen, wer traf. Der Prüfer zeigt das jetzt je Posten.
- **Tunnel zu früh aufgegeben:** „Auslöser nicht gefunden“ stand kurz im Ergebnis. Der Eingang ist ein Bauwerk, das stand im Code, ich hatte nur beim Gräber gesucht.
- **Zwei Prüffälle griffen ins Leere:** Nach dem Kopieren zweier Zeilen fanden die Sabotagen ihre Stelle nicht mehr eindeutig. Das Werkzeug meldete es, ich sah es erst nach dem Sichern. Die Zeilen sind jetzt je eine Hilfsfunktion.

## Kleine Reste, 04.11. 18:25

Beleg: `punkte_rechnung17.txt`.

- **Kuh:** Anweisung 22 wirft je Befehl eine Kuh. Zähler 5 auf 4 bei Takt 665, im selben Takt fällt die Anweisung auf 3 zurück (sonder2_g). Darum flog nur eine.
- **Eingestürzter Gang:** Die 35 Felder unter Bodenhöhe haben Fläche 1 und keine Sperr-Bits, laut Karte also begehbar. Belaufen habe ich sie nicht.
- **Spielbefehl 74:** heißt in der Befehlstabelle `ReleaseDogs`, Hunde loslassen.
- **Holztor:** Mapper 103 mit Größe 3 setzte das Spiel nicht (sonder22). Art und Größe passen also noch nicht, als Ziel ist es nicht geprüft.
- **Schüsse ohne Verlust:** Sie landen, aber es gibt keinen Verlust: Pfeil 17 von 331, Feuer 14 von 75, Bolzen 3 von 69, Schleuderstein 1 von 232. Das Ziel war in keinem Fall weg. Die Ursache ist nicht geklärt.

## Einheiten auf einen Punkt und Bündnis, 04.11. 19:15 bis 19:34

Belege: `sonder23`, `punkte_rechnung_b.txt`. Daniel hat entschieden: SamurAI darf alles, was ein Mensch auch kann, also auch Einheiten auf einen Punkt packen, und per Befehl mehr als 5 Mann auf einen Wachturm schicken.

**Packen, offener Boden, 8 Speerträger auf ein Feld:** Jeder mit eigenem Befehl: Alle 8 stehen ab Takt 135 auf einem Feld. Das hält bis Takt 376, ab dann gehen sie auseinander, bei Takt 677 steht jeder auf einem eigenen Feld. Ob ein neuer Befehl den Stapel hält, ist nicht gefahren. Als ein Trupp: Sie verteilen sich auf Zielfelder um den Punkt, nur im Laufen standen kurz bis zu 4 auf einem Feld.

**Bündnis, 8 KI in 4 Paaren, Green Haven:** Der Startbefehl `teams` wirkte auf diesem Weg nicht (Lauf 19:18). Im angehaltenen Spiel gesetzt hielten die Teams, das Spiel zeigte Teamwappen. Gold geht genau von Partner zu Partner: 332, 272 und 60. Das Spiel endete bei Takt 161.812 mit gameOver 1, beide Lords von Team 1 lebten. Warum der Abstand zum letzten gefallenen Lord (Takt 155.202) so groß ist, ist nicht geklärt. Mein Werkzeug kennt als Ende nur den letzten Lord und meldete deshalb „kein neuer Takt“, das ist eine Lücke im Werkzeug. Warenbitten gab es zwischen KI und KI nicht.

**Lauf F steht damit bei 113 bestätigt, 11 widerlegt, 75 gemessen, 11 gesehen, 30 Lage fehlt, 1 offen.**

## Direkt gerufen, 04.11. 20:00 bis 20:40

Viele offene Punkte sind Prüfungen der Oberfläche: Sie laufen nur, wenn ein Mensch klickt, ihr Ergebnis steht in keinem Feld. `spielcode_rufen.py` ruft die Funktion im angehaltenen Spiel direkt auf, nur Instanz 2, nur Messlauf, nichts davon geht in SamurAI. Proben: `auge_rufen.py`, Ergebnisse: `rufen_*.json`. Zweimal stürzte das Spiel ab, weil ich der Funktion kein `this` gab (Export zeigt es nicht, Maschinencode nimmt ECX), einmal bei `aiDecideOnNewBuildings` direkt gerufen, Ursache dort nicht geklärt. Die Regel lief dann im echten Lauf.

| Punkt | Gemessen |
|---|---|
| Bau-Reichweite | 45, 50, 60, 70 je Kartengröße 160, 200, 300, 400, um einen Punkt bei der Burg (Burg 138, 262, Punkt 140, 268). Das entfernteste Feld zählt: Karte 200: 50 geht, 51 Grund 0x12 |
| Mauer nahe am Feind | Einheit: Mauerfeld unter 5 verboten, Weg unter 15 (Grund 0x11). Gebäude: nur angrenzend. Weg unter 7 nur bei Arten wie Lager (Grund 0x13), Hütte und Turm zählen nicht |
| Mauerkosten | Art 25: 13 Felder 6 Stein, 8 Felder 4. Art 46: 13 Felder 3, 8 Felder 2 |
| Leiterträger | Prüfung der Oberfläche ab 4 Gold, der Befehl verlangt 20 |
| Geräte auf dem Turm | Befehl 42, Befehl 75 Art 2: 80 Gold hin, 80 zurück |
| Belagerungsturm | Mapper 192 (94 baut Art 69, kein Zelt). Fortschritt +Mann je Takt, über 1.280 kommt der Turm. Zählfeld 4 nur bei 4 Mann |
| Öl | Anweisung 20: Zustand 10, Wurf 23 Takte später. Pech im Lager sinkt beim Holen um 1. Die Schmelze nimmt +1 in Zustand 4, gibt -1 von 7 nach 8 |
| Holz je Waffe | Bogen 2, Pike 1 (Export sagte 2) |
| Mine, Stein | Mine: Menge 7 führt von Zustand 5 nach 6, Stand 8 gelesen. Stapel bis 47 |
| Pechgrube | Ohne Vorkommen gesetzt läuft sie: rund alle 2.380 Takte 1 Pech |
| Kinder | Mit Zuhause: 60 bleiben, von 90 gehen genau 15. Ohne Zuhause gehen alle |
| Entlassen ohne Bauern | UT_HEALER 34, UT_PRIEST 33, UT_INNKEEPER 36, UT_BREWER 17, UT_TANNER 21, UT_ARMORER 20, Art 19, UT_POLETURNER 18, UT_FLETCHER 4, Art 12 |
| KI Holzfäller | 3 Hütten: Wert ab 31, 6 Hütten: ab 91. Gezählt wird mit Filter |
| KI Holz kaufen | Wunsch 5 ab Zähler 3, Export sagt 37 |
| KI Bau-Ziel | Gold über 16.000: +2, bis 16.000: +1, je rund 50 Takte. Bis 5.000: +1 rund alle 100 Takte |
| KI bittet um Ware | Holz und Stein ja, Hopfen und Bier nein. Nur an einen Partner im selben Team mit Kennung, also an einen Menschen |
| Essen sperren | Kein Spielbefehl, ein Knopf: Der Zähler der Art geht auf 0, die Ware bleibt in der Kammer |
| Graben-Zähler | -1 einmal je 200 Takte |
| Tempotasten | Unter 90: 5er-Schritte. 90 bis unter 200: 10er. Ab 200: 100er. Bei 10 und darunter tut Minus nichts. Export sagte 20 bis 90 |
| Stapel | Wiederholter Befehl alle 50 Takte: 8 Mann stehen von Takt 138 bis 1.275 auf einem Feld, der letzte Befehl kam bei Takt 1.000. Jeder allein ab Takt 1.938 |
| Holztor | Mapper 103 und 140 bis 143: Die Prüfung sagt ja, es entsteht kein Gebäude. Als Ziel nicht gefahren |

**Lauf F steht damit bei 151 bestätigt, 15 widerlegt, 75 gemessen, 0 gesehen, 0 Lage fehlt, 0 offen.**

## Daniels Angaben geprüft, 04.11. 21:00

| Angabe | Geprüft |
|---|---|
| Tempo: mit UCP bis 1.000, mehr als rund 830 wird nicht genommen | Stimmt. Tempo 100: 100 Takte je Sekunde, 500: 500, 830: 824, 1.000: 825, 2.000: 824 (KI-Gefecht, je 4 Sekunden, `rufen_tempo_20261104.json`). Normal 10 bis 90: Im Export gehen die Tasten von 20 bis 90, Minus von 25 auf 20, bei 20 bleibt es. Das Menü ist nicht geprüft |
| Der Stapel entwirrt sich nach rund 1.000 Takten | Fast. Ohne neuen Befehl hält er 275 bis 375 Takte, dann zerfällt er, jeder allein nach 677 bis 938 Takten. Wiederholter Befehl hält ihn, gemessen bis Takt 1.275 |
| Können sich KI etwas schicken? | Von selbst nur Gold an den Partner. Die Warenbitte geht nur an einen Partner mit Kennung, also einen Menschen. Spielbefehl 113 Unterart 2 verschiebt Gold und Waren zwischen zwei Spielern: 100 Gold und 5 Holz kamen an, auch ohne gleiches Team (`rufen_korb_waren_20261104.json`). Das Menü heißt `AlliesSendGoods`, ein Mensch kommt so nur an Verbündete, das ist nicht gemessen |
| Projektile und Feuer haben Zufall | Stimmt. Im Code: `spawnProjectileEntity`, `prepareProjectileTarget` (`setRandomShootLocation`), die Feuerausbreitung, `processFireDamageToUnit`. Geschosse und Ausbreitung ziehen aus dem Spielstrom, der läuft festgelegt mit (Lauf K). Der Feuerschaden an Einheiten zieht aus dem ersten Strom, der hängt an der echten Zeit. Ob die 4 Feuerschüsse daher kommen, ist nicht nachgerechnet |
| Feuerkorb nur auf Bergfried, Türmen, Torhäusern, Mauern, keine Zinnen | Stimmt mit der Prüfung der Oberfläche (`getHeightAtTileIncludingOwnersBuildings`). Alle Gebäude durchgegangen: Art 41, 46, 74, 76, 77, 78 haben Felder mit Ja, alle anderen Arten keines. Mauer 3.089 Felder ja, 488 nein. Zinne 169 ja, 683 nein. Nur der Besitzer, nie ein anderer. Befehl 69 siehe P312 |
| Holztor gibt es im SHC nicht | Passt. `placeBuilding` kennt keinen Fall dafür, in 17 Versuchen mit Größe und Drehung entstand keines (`rufen_mapper_20261104.txt`). Geprüft auf freiem Boden. Stufe Daniel |
| Waldsterben nur als Ton | Die Suche nach blight, treeDeath, forestDeath, treeDisease, woodDisease, deadTree im Code traf nur einen Satz aus einer Mission. Der Ton ist nicht geprüft. Stufe Daniel |

## Rest der Checkliste P372 bis P376

Mein Bericht von 20:45 sagte, die Checkliste sei durch. Das stimmte nicht ganz: Diese 5 Punkte hatten in keiner Liste eine Zeile. Stand jetzt 373 von 376 mit Urteil.

| Punkt | Funktion | Urteil | Beleg |
|---|---|---|---|
| P372 | `teamToBitFlagsUnk` | bestätigt | Direkt: jeder allein 0b11111011, Spieler 3 und 4 zusammen 0b11110011 |
| P375 | `getCastleBuildRangeForMapSize` | bestätigt | 45, 50, 60, 70, siehe P201 |
| P374 | `renderWallDragPreview` | Lage fehlte | Braucht Ziehen mit der Maus. Die Formel aus P119 ergibt 5 Stein für 10 Felder, gelesen ist es nicht |
| P373 | `commitBuildingAvailability` | Lage fehlte | Braucht eine Karte mit gesperrtem Gebäude |
| P376 | `updateTribeBehaviorBasedOnBehaviorType` | Lage fehlte | Nur in der Einzelspieler-Mission, die kommt in unseren Partien nicht vor |

## Noch offen

Warum 4 von 82 Feuerschüssen 60 Takte keinen Verlust zeigen. Warum der erste Rahmen im Gefecht alt ist. Feuerkorb: Warum Befehl 69 auf Bergfried, Turm und niedriger Mauer in der Kurzprobe keinen Korb setzte, und was er in Siege That kostet (P312). Warum das Spiel beim Direktaufruf von `aiDecideOnNewBuildings` abstürzt. Die -1 aus P119 und das kurze 0 in P140. Lauf-K-Stand (Szene 8b im Plan) ist nicht gefahren, die KI-Punkte kamen aus der Aufzeichnung von Lauf K. Lauf F: siehe `Punkte_Lauf_F.md`.

