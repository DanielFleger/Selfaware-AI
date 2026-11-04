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

Editor, Szene Beschuss, im Gefecht ähnlich (`beschuss_g.geschosse.json`). Befehl und Zahlen: `geschosse_beschuss.py`, `geschosse_beschuss.txt`. Der Verlust kommt im Takt der Landung oder bis zu 2 Takte davor. **Die rund 5 Prozent ohne Verlust sind noch nicht erklärt.** Zielwahl: 378 von 795 Schüssen gehen auf den nächsten Feind, 417 nicht.

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

Alle 75 Punkte der Checkliste sind gegen ihre Erwartung gerechnet: `Punkte_Lauf_S.md`. 41 bestätigt, 11 widerlegt, 4 teils, 2 gemessen, 14 Lage fehlte, 3 offen. Der Nachlauf hat dafür die fehlenden Lagen gefahren: `sonder8` (Editor), `sonder8_g`, `sonder9_g`, `lord2_g` (Gefecht), Auswertung `punkte_rechnung6.txt` und `punkte_rechnung7.txt`.

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
| Ritter | 15 | 5 |
| Schwertkämpfer, arabischer Schwertkämpfer | 10 | 8 |
| Pikenier, Keulenträger | 5 | 15 |
| Speerträger | 2 | 36 |
| Sklave, Assassine | 0 | - |

Ein Stück fällt, wenn der Schaden über 70 steigt. Am Ende einer Mauer (1 Nachbar) 1,5-fach, an einer Kreuzung (3 Nachbarn) halb, abgerundet.

**Bestätigt im Nachlauf:** Der Sieger bekommt beim Tod des Lords 25 % des gegnerischen Goldes (+1.000 bei 4.000). Nur die Grenze 39 zählt ums Lager, 41 nicht. Der Belagerungsturm legt mit Anweisung 23 an, es entsteht ein Gebäude der Art 69, die Bemannung geht auf 0. Eine Ramme fährt nur mit 4 Mann. Ein berittener Bogenschütze schießt im Laufen, ein Armbrustschütze nicht. Ein Ziel im Mauerring lässt die Einheit stehen.

**Nachladen (P308):** Laut Code nur für die KI. Beim Menschen blieb die Munition trotz 200 Stein auf 0. **Befehl 86 (P309):** abgesetzt, ohne Wirkung, ungeklärt.

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

## Noch offen

Löschen, Durchgang durchs Tor, Anlegen des Belagerungsturms, ob man durch die Mauerlücke und den eingestürzten Gang laufen kann, warum nur eine Kuh flog, wozu Spielbefehl 74 im echten Spiel dient, die genaue Grenze der Hunde. Lager, Holztor, Mauern als Ziel im Nahkampf. Warum der Truppenbefehl schneller ist. Warum der Pfeil nicht bis 54 reicht. Rund 5 Prozent Schüsse ohne Verlust am stehenden Ziel. Warum der erste Rahmen im Gefecht alt ist. Lauf-K-Stand (Szene 8b im Plan) ist nicht gefahren. 14 Punkte warten auf ihre Lage, 3 sind offen (Liste in `Punkte_Lauf_S.md`). Oben auf einen Turm kommen Einheiten mit dem Laufbefehl nicht.
