# Punkte Lauf S

75 Punkte der Checkliste (Abschnitt Lauf S). Das Werkzeug `auge_punkte` sagt nur, ob sich ein Feld ändert (`punkte_lauf_s.py`, `punkte_lauf_s.txt`, 38 Aufzeichnungen). Die Urteile hier sind je Punkt gegen die Erwartung gerechnet: `punkte_rechnen1.py` bis `punkte_rechnen12.py` und `punkte_rechnen_k.py`, Ausgaben in `punkte_rechnung1.txt` bis `punkte_rechnung13.txt` und `punkte_rechnung_k.txt`, dazu `belege_sonderfaelle.txt` und die `.regeln.json`. Die Tabelle erzeugt `punkte_urteile.py`.

**Worte:** bestätigt und widerlegt heißen: Die Lage kam vor und die Rechnung ist gemacht. teils: Ein Teil ist gerechnet, der Rest der Lage fehlte. gemessen: Erwartung war nur „notieren“. Lage fehlte: Die Lage kam in Lauf S nicht vor. offen: Lage kam vor, Feld nicht lesbar oder ungeklärt.

| Urteil | Punkte |
|---|---|
| widerlegt | 16 |
| bestätigt | 52 |
| teils | 2 |
| gemessen | 4 |
| Lage fehlte | 1 |
| offen | 0 |

## Was die Lauf-S-Lagen noch brauchen

| Versuch | Punkte |
|---|---|
| Feuerkorb: Befehl 69 wirkte nicht, Siege That kommt in unseren Partien nicht vor | P312 |

## Widerlegt (16)

| Punkt | Funktion | Beleg |
|---|---|---|
| P297 | `UpdateEntity_PoisonCloud` | 7 von 7 Giftwolken: logicalState 3 nach 828 Takten, nicht 808. Im Code läuft ab rng_2 800 eine Ausblendung, sie dauert 28 Takte statt der angenommenen 8. |
| P302 | `UpdateTower4` | Großer Turm, Einheit geht über Treppe und Mauer hinein und später wieder hinaus (sonder17). hasUnitsOntop wird 1 sofort beim Betreten (Takt 573), nicht erst bei Zähler 0: Das setzt `processUnitMove`, samt Zähler 100. Der Zähler läuft dann alle 100 Takte von 100 auf 0 (42 Sprünge, Abstände meist 99 bis 101). Auf 0 geht hasUnitsOntop erst beim nächsten Durchlauf: Abgang Takt 1.849, 0 bei Takt 1.939. Wer gesetzt statt gegangen ist, startet den Zähler nicht (sonder12: Zähler blieb 0). |
| P303 | `updateGateDrawBridgeOpenCloseLogic` | Im Speicher steht 140 Mikro und 100 Takte, im Export 200 und 1.200 (`code_abgleich.txt`, UCP3). Gemessen: Feind auf 136 Mikro (17 Felder): Tor reagiert nach 41 Takten (sonder13). Feind auf 144 Mikro (18 Felder): in 4.500 Takten nichts (sonder12). Das passt genau auf 140. gateState2 springt auf 100. |
| P308 | `TryAcquireAmmunitionOrPlanToBuyStone` | Stein -10, Munition +10, nicht +20: Im Speicher steht +10 (UCP3). KI in Lauf K: 21 von 22 Sprüngen +10, Stein -10 in den 4 Fällen, die zwischen zwei Rahmen sichtbar sind. Die Funktion selbst fragt nicht nach der KI, nur ihr Aufrufer: Spielbefehl 86 mit Wert 0 lädt auch beim Menschen, 5 auf 15 (sonder10_g). |
| P309 | `SelectionReplenishAmmo` | Nicht Stein -10 und Munition auf 20. Spielbefehl 86 hat zwei Werte: Wert 1 füllt den Trupp auf, und zwar bis 10: 6 auf 10 (sonder10_g). Mit 2 Stein gibt es +2, also 1 Stein je Schuss: 6 auf 8 (sonder18_g), laut Export wären es +4. Das ist UCP3 (`code_abgleich.txt`). Wert 0 ist der Zweig von P308. Berichtigt: Der ungeklärte Versuch aus dem ersten Nachlauf schickte den Trupp mit Wert 0, also in den falschen Zweig. |
| P323 | `ifNecessaryThrowOilAutomatically` | Öl beim Träger ab Takt 361 bis 370, eigener Trupp, Haltung aggressiv, defensiv und stehen, ein Feind 2 bis 3 Felder daneben: In keiner Haltung ein Wurf, Anweisung blieb 3. Der Feind erschlug den Träger (Trupp weg ab Takt 1.182 bis 1.190). Ob der Code beim Menschen überhaupt gerufen wird, ist nicht nachgelesen. |
| P326 | `giveTribeMoveInstruction` | 6 Schwertkämpfer: Zielfelder eng um den Punkt, kleinster Abstand 1 (schräg), größter 3. Nicht 2 auseinander. |
| P332 | `ComputeDamageFearFactorBonus` | Nicht 5 Prozent je Stufe. Im Speicher steht eine Tabelle (UCP3): Stufe -5 bis +5 gibt 80, 84, 88, 92, 96, 100, 108, 116, 124, 132, 140 Prozent. Gemessen Schwert gegen Schwert, Grund 75: Stufe +5 (5 Gärten) 105, Stufe +2 (Bevölkerung wuchs) 87, Stufe -5 (5 Galgen) 60 (sonder10_g). Das sind genau 140, 116 und 80 Prozent. |
| P334 | `getRemainingRequiredEngineers` | Der Zähler steigt nicht je Ingenieur, er springt: Schild 0 auf 1, Katapult 0 auf 2, Trebuchet 0 auf 3, Belagerungsturm 0 auf 4. |
| P337 | `playerMakeUnitSelection` | Mit zu wenig Ingenieuren bleibt das Feld 0, in 5 Gerätearten mit 1 Mann zu wenig. Der Ingenieur wartet 2 Felder daneben. |
| P338 | `isTowerTileOvercrowdedByCurrentPlayer` | Die Grenze 5 gilt nur beim Mausklick (`MenuItemActionHandler`, sie sperrt dort den Befehl). Mit dem Befehl selbst: 8 von 8 auf dem Wachturm, Takt 541 bis 614 (sonder17). Daniel hat am 04.11. entschieden: SamurAI darf das. |
| P339 | `tryAttackUnitID` | Beim Angriffsbefehl bleibt huntedBy 0 (19 von 19 Zielen, reichweite). Bei Zielen, die der Hund selbst wählt, geht es von 0 auf 1. |
| P345 | `UpdateBatteringRam` | 125 je Treffer, 12 von 12 Treffern am Tor (1.500 Leben), rund alle 80 Takte, dazu Hütte und Turm. Der Export übergibt 50, im Speicher steht 125 (`code_abgleich.txt`, UCP3). |
| P365 | `UpdateArabianArcher` | Das Feld zählt nicht die lebenden, es summiert sie je Takt: 720 nach 10 Takten mit 72 Bogenschützen, am Ende 22.280 bei 0 lebenden. |
| P366 | `UpdateSlave` | Sklave: geht an die Mauer, kein Schaden in 4.500 Takten. Tor und Turm 1 je Schlag, Hütte nichts. |
| P367 | `UpdateAssassin` | Assassine: nimmt den Mauerbefehl nicht an, geht nicht hin, kein Schaden. Hütte 75, Turm 5, Tor 3 je Schlag. |

## Bestätigt (52)

| Punkt | Funktion | Beleg |
|---|---|---|
| P298 | `UpdateFireEntity` | Solange die Hütte brennt: someTracker 1 mit Zähler 0 in 24.785 von 24.785 Rahmen, nie 2. Danach steigt erst der Zähler, dann 2 (1.596 Rahmen), also nicht sofort. Neue Feuer: 240 von 309 haben einen Nachbarn mit Stufe plus 1, 51 einen anderen, 18 keinen. |
| P299 | `UpdateTunnel` | 4 von 4 Gräbern: Flag 2 im selben Takt wie Zustand 3 (1.001, 1.012, 1.003, 1.005). |
| P300 | `processDamageFromKillingPit` | Werkzeug: Zahl passt. Dazu sonder1: 3 Gruben, 3 x 18.000, je 24 Takte auseinander. |
| P301 | `lightUpBuilding` | Abklingzeit der Hütten bis Takt 360. 3 Feuerstrahlen flogen davor, fireDuration blieb 0 bis Takt 553. Beides zugleich in 0 Rahmen. |
| P304 | `UpdateGateHouseLarge` | pathLinkageRelated2 0, 1, 2, nach Entwarnung 3, dann 0: Der Feind geht ab Takt 1.000 weg, 3 kommt bei Takt 1.185, 0 bei Takt 1.233 (sonder10). gateState 10 und 11 setzt der Code nur innerhalb eines Takts, von außen steht dort 12 oder 0. Durchgang: Offenes Tor: Der Besitzer geht hindurch, Höhe 98. Geschlossenes Tor mit Mauer rechts und links: Er geht außen um die Mauer herum (sonder12). |
| P306 | `processUnitLossStatistic` | finalKillMatrix steht nicht in der Aufzeichnung, darum direkt aus dem Speicher gelesen, vorher und nachher: [1][2] = 2, [2][1] = 1 (sonder10_g), also [Töter][Opfer]. Berichtigt: Hier stand, die Matrix ändere sich nie. Das war falsch, das Feld wurde gar nicht gelesen. |
| P310 | `ClickMoveUnit` | Unser Laufbefehl ist genau dieser Befehl: Spielbefehl 17 (Modul), Parameter Gruppe, x, y, Schalter, Tempo laut Code. Er wirkte in allen Läufen. Ein echter Mausklick ist nicht gefahren. |
| P313 | `checkSkirmishGameDefeat` | 3 von 3 Läufen, davon einer mit echtem Töter: Feld des Gegners wird 1, gameOver 1, playerIsAlive[1] = 1 und [2] = 0, rund 305 Takte nach dem Sterben des Lords. |
| P314 | `doMoveFromTileToTile` | 5 von 5 Gegnern auf einem Feld des brennenden Pechs: counter 1 und field312 1 im Takt des Betretens (Takt 547 bis 581). counter fällt 15 bis 20 Takte später wieder auf 0, field312 bleibt 1 (sonder11_g). |
| P315 | `computeTotalUnitsWithinDistance` | (Wert, Anzahl) = (12, 3) bei 3 Speerträgern, (32, 8) bei 8, (16, 4) bei 4 lebenden. Wert 4 je Speerträger. |
| P316 | `updateUnitDeathHeatmapIn3SpacesAroundTile` | Editor, nahkampf: 45 Felder +3, 356 +2, 705 +1. Gefecht, nahkampf_g: 0 Änderungen bei Toten von Menschen. In beschuss_g 3 Fälle mit genau diesem Muster, wer dort starb, ist nicht zugeordnet. |
| P317 | `UpdateLadderManState01` | 2 von 2 Leitern: Richtung 2, Blick des Trägers 2. |
| P318 | `CheckTribeActivityPercentages` | schlacht_20: Trupp mit Schläger, Anteil über 10 in 1.384 von 1.412 Rahmen, die übrigen 28 mit Anteil 0. |
| P319 | `aiPlaceAIVBuilding` | Lauf K: 117 Bauten an einer Stelle, an der schon dasselbe stand. 116 davon, während der nächste Feind 120 oder weiter vom Lord weg war, 1 darunter (Holzfällerhütte). wait fällt unter 120 kaum, 284 gegen 278.798 Mal; die KI-Ebene ist nur jeden 25. Rahmen aufgezeichnet, die Zuordnung am Rand also ungenau. |
| P320 | `resetCountdownInHeatMap` | Lauf K: 139 Felder springen von 0 auf 10, dann -1 rund alle 800 Takte, z. B. Takt 472 auf 10, 582 auf 9, 1.399 auf 8, 2.182 auf 7. |
| P321 | `updatePitchDitches` | sonder5_g, 2 von 2: Zustand 2 bei Takt 501, 3 bei 526, weg bei 729. Auf 25 Takte genau. |
| P322 | `processDamageToBuilding` | Mitte der Mauer: Schaden +20, Höhe -20, erster Treffer -40. Ende (1 Nachbar): +30, 1,5-fach. Kreuzung (3 Nachbarn): Pikenier 2 statt 5, also halb, abgerundet. |
| P324 | `recomputeTotalTroopValueOfTroopsNearKeep` | Speerträger auf 39 Feldern zählt, Bogenschütze auf 41 nicht: Wert 4 ab Takt 195 (sonder8_g, 2 Läufe). Vorher: 6 Bogenschützen 36, 8 Speerträger 32. |
| P325 | `applyMoveCommandOrRallyCommandToTribe` | Trifft genau zu, aber nur in einem Sonderfall: Die erste Einheit des Trupps steht auf einer Fläche 0, hier einer Turmecke. Dann bleibt der Kämpfer im Zustand 106, sein Ziel 0,0, die übrigen vier bekommen genau die Zielkachel und stehen später alle auf einem Feld (sonder17). Im Normalfall rechnet `giveTribeMoveInstruction` selbst: Dann bekommt jeder ein eigenes Zielfeld, und der Kämpfer verlässt den Kampf und läuft mit (sonder10, sonder12). |
| P327 | `computeTribePercentages` | Anteil zwischen 0 und 100, bei Kampf über 0. |
| P328 | `giveTribeAnInstruction` | Gebäudeangriff: Rammen mit 1, 2, 3 Mann bleiben stehen, nur die mit 4 fährt und schlägt (sonder8). |
| P330 | `calculateUnitMovementSpeed` | Eben: berechnet gleich Grundwert. Bergauf: Stufe 4 auf ein Feld (Hang der Karte): +3 für rund 47 Takte (sonder12). Treppe (Stufen 16): +4 und +5 (sonder14). Das deckt den Code: Abstand 4 bis 7 gibt +3, 8 bis 11 gibt +4, 12 bis 16 gibt +5. |
| P331 | `shouldUnitsEngageInMelee` | Spielart Mehrspieler und totalNoRushTicks 1.000 gesetzt, bei Takt 100. Der Wert fällt 1 je Takt. Schwertkämpfer steht ab Takt 441 neben dem Gegner, beide kämpfen nicht. Bei Takt 1.105, als der Wert 0 erreicht, fängt der Kampf an (sonder16_g). In der Spielart Einzelspieler gilt der Schutz laut Code nicht. Das Spiel lief mit der gesetzten Spielart weiter. |
| P333 | `recomputeTroopValuesForPlayer` | 10 von 10 Wechseln im Fenster (Lastverteiler 12, 13, 14, 103, 163). Der Teil über Fernkämpfer ist nicht getrennt geprüft. |
| P335 | `findClosestLaddermanWithLadderPosition` | 2 von 2: Zustand 3 ab Takt 136. |
| P336 | `unitIsInMoat` | Werkzeug: Zahl passt. |
| P340 | `UpdateBurningMan` | 16 Brennende in 4 Szenen: Besitzer 0 und dying 1 in allen Rahmen. |
| P341 | `UpdateShield` | Takt 39: Zähler 1, Schild von Zustand 6 auf 0, Ingenieur 109 (0x6D). |
| P342 | `harassBuildingsWithSiegeAI` | Eigenes Katapult, nicht gegnerisch: 10 Schüsse, Munition 0, letzter bei Takt 1.695, danach keiner bis 1.978. |
| P343 | `setDestinationForUnit` | Ziel im geschlossenen Mauerring: Die Einheit bleibt stehen, sie verschwindet nicht (sonder8). |
| P344 | `UpdateSiegeTower` | Mit Anweisung 23: Zustand 6, dann 0 mit Bemannung 4, fährt Takt 415 bis 698, dann Zustand 8 und 9, Bemannung 0, neues Gebäude Art 69 bei Takt 699 (sonder8). |
| P346 | `processMeleeInitiation` | 11 von 11 Nahkämpfern: erster Schlag bei 1,6 bis 2,0 Feldern. |
| P347 | `findNearestEnemyAndHeadTowardsIt` | Aggressiv auf 24 Felder: -220 und -221. Defensiv auf 4: -59 und -60. Das passt zu -30 minus Abstand in Mikro (192 und 32), bis auf 3. |
| P348 | `unitClimbing` | 6 von 6 Steigern: climbingState 1 bis 5, je 96 Takte, field219 höchstens 95. |
| P349 | `UpdateTunneler` | Frame steigt bis 23, dann 0. Zustand 4: 5 x 50 Schaden bei Frame 60 bis 64, Ende bei 65. Die Höhe steigt im Gang von 8 auf bis 22, die einzelnen Schritte 6, 12, 18, 24 kann das Raster von 25 Takten nicht zeigen. |
| P350 | `UpdateQuarryMason` | Lauf K: 4 Steinbrüche springen von 0 auf 4.000, je 11 bis 33 Takte danach fehlt der Steinmetz dieses Bruchs in der Aufzeichnung. Der Code setzt 4.000 bei allen Arbeitern in dieser Lage, nicht nur beim Steinmetz. |
| P351 | `UpdateCrusaderArcher` | Weit weg sitzen sie: 21.411 Rahmen über 400. Fast alle Wechsel zum Hinsetzen liegen an der Grenze (902 bei 390 bis 399, 17 bei 400 bis 409), dort wechselt es ständig. |
| P353 | `UpdateSpearman` | Speerträger: Mauer 2 je Schlag, alle 100 Takte. Hütte 10, Tor 2. Zu 8 und 3 aus dem Code passt das nicht, die Rangfolge schon. |
| P354 | `UpdatePikeman` | Pikenier: Mauer 5 je Schlag, 15 Schläge je Stück. Turm 10 (50 Schläge), Tor 5 (300 Schläge). Die Mauer fällt also am schnellsten. |
| P355 | `UpdateMaceman` | Keulenträger: Mauer 5 je Schlag, Hütte 80, Tor 5. Die Werte weichen von 35 und 4 ab. |
| P356 | `UpdateSwordsman` | Schwertkämpfer: Mauer 10 je Schlag (8 Schläge je Stück), Hütte 100, Tor und Turm 10. Die Werte weichen von 70 und 6 ab. |
| P357 | `UpdateKnight` | Ritter: Mauer 10 je Schlag, 8 Schläge je Stück, wie im Code. Hütte 100, Tor und Turm 10. Berichtigt: Hier stand 15. Das war das Mauerende: Der Ritter brach erst das Nachbarstück bei +10, danach hatte das Zielstück nur noch 1 Nachbarn (sonder8), und in sonder19 machten 3 Ritter je +10. |
| P359 | `UpdateCatapult` | Verbrauch gleich Schüsse: 10 von 10, 7 von 7 bei 5 Katapulten. |
| P360 | `UpdateTrebuchet` | Verbrauch gleich Schüsse: 5 von 5, 3 von 3, 1 von 1. Der Kuhwurf lässt die Munition unverändert. |
| P361 | `UpdateMangonel` | 11 Salven mit je 7 Geschossen. |
| P362 | `UpdateLord` | 8 Ritter töten den Lord (Takt 889): Spieler 1 bekommt 1.000 Gold, 25 % von 4.000, bei Takt 890. Das Gold von Spieler 2 bleibt gleich (lord2_g). |
| P363 | `UpdateBallista` | Werkzeug: Zahl passt. |
| P364 | `UpdateCageDog` | Bei 8 Feinden wechseln die Hunde bei Takt 8 bis 33 von 0xD2 auf 109, bei 3 Feinden nicht. |
| P368 | `UpdateArabianSwordsman` | Arabischer Schwertkämpfer: Mauer 10 je Schlag, alle rund 190 Takte. Hütte 100, Tor und Turm 10. |
| P369 | `UpdateFireBallista` | Werkzeug: Zahl passt. |
| P370 | `updateUnits` | totalAssassinTroops zählt nur Einheiten mit aiUnitBehaviourType 12, in Lauf K hatten alle Assassinen 1 und der Zähler blieb 0. Gesetzt in sonder15_g: 2 Assassinen: beide Zähler 0 auf 2 bei Takt 210, nach ihrem Tod bei Takt 1.386 wieder 0. |
| P371 | `UpdateHorseArcher` | Schießt auch im Laufen: Schüsse bei Takt 120, 218, 320, alle 92 bis 102 Takte. Im Stand alle 77 bis 79 (sonder8). |

## Teils (2)

| Punkt | Funktion | Beleg |
|---|---|---|
| P329 | `updateTribeCombatStanceBehavior` | Zähler +1 je Takt, field93 läuft ab 51 bis 59 und fällt auf 0. Der Abstand zur Leit-Einheit ist nicht gemessen. |
| P358 | `UpdateMonk` | Lauf K: 301 Mönche mit Arbeitsplatz Kathedrale im Zustand 0x69, 2.715 Rahmen. Der Zielwechsel alle 40 Takte ist nur im Code gelesen (Spielzeit plus Platz teilbar durch 40, und nur, wenn ein Feld frei ist), mein gelesenes Feld zeigte ihn nicht. |

## Gemessen (4)

| Punkt | Funktion | Beleg |
|---|---|---|
| P305 | `UpdateUnitLossData` | Die Liste blieb in sonder10_g auf 0, obwohl Spieler 1 einen Mann verlor. Sie gehört zur Sprachausgabe (`UpdateUnitLossSpeechFeedback` schiebt sie weiter), auf das Spiel wirkt sie laut Code nicht. Was das Auge braucht, steht in troopsLost und weightedLosses: +1 und +Truppenwert (4 für den Speerträger). |
| P307 | `areActivePlayersMostlySameTeam` | Laut Code nur von `RenderStartingGoodDisplayElement` gerufen, also Anzeige, nicht Spielende. Ergebnis: weniger als 2 Spieler in fremden Teams. Nicht gefahren, im Zustand hinterlässt es nichts. |
| P311 | `ClickGiveUnitsInstruction` | Param0 Gruppe, Param1 Anweisung, Param2 und 3 das Ziel (Nummer und uid, x und y oder Feldnummer), Param4 0. In allen Läufen so benutzt, auch Zuschütten wirkte mit 0, das Menü sendet dort 1000. |
| P352 | `UpdateCrossbowman` | Im Marsch kein Schuss, bei beiden Armbrustschützen. Am Ziel je 6 Schüsse, alle 228 Takte, auch mit Haltung stehen (sonder8). |

## Lage fehlte (1)

| Punkt | Funktion | Beleg |
|---|---|---|
| P312 | `CommandSpawnEntity` | Spielbefehl 69 abgesetzt (Log), in Spielart 3 und mit gesetzter Spielart 6: Es entstand kein Korb, Gold blieb gleich (sonder15_g). Auch im KI-Gefecht entstand mit Befehl 69 (Spielart 3 und 6) und Befehl 97 kein neuer Korb (`rufen_korb_20261104.json`). Warum, ist ungeklärt. Siege That kommt in unseren Partien nicht vor. |

## Offen (0)

| Punkt | Funktion | Beleg |
|---|---|---|

## Gesamtproben an drei Szenen

| Probe | Punkt | Einzel Gefecht | 1.000 gegen 1.000 |
|---|---|---|---|
| A1 Felder außerhalb der Liste | 241 | 10 | 3 |
| A3 Takte | Tempo 200, nicht streng | Tempo 100: 848 fehlen, 782 gemischt. Das Werkzeug schreibt „widerlegt“, weil es Tempo 100 als streng behandelt; die Szene war absichtlich nicht streng | Tempo 1000, nicht streng |
| A4 Lesen je Takt, Median und Höchstwert | 1,2 und 15,3 ms | 2,6 und 14,6 ms | 0,6 und 15,3 ms |
| A7 Zufallsfolge passt zur Tabelle | 2.315 von 2.315 | 5.120 von 5.120 | **2.173 von 2.174** |
| A10 Platzwechsel ohne Verstoß | 7.776 | 17.912 | 9.745 |

A1: Die ersten 14 der 241 Felder gehören zum Befehlsring `DAT_GameCommand...`, weil hier viele Befehle liefen. Alle 241 sind nicht einzeln angesehen. A7: Der eine Fall auf Tempo 1000 ist nicht geklärt, vermutlich ein Rahmen über die Taktgrenze.
