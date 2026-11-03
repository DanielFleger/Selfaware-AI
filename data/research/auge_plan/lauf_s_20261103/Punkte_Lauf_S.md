# Punkte Lauf S

75 Punkte der Checkliste (Abschnitt Lauf S). Das Werkzeug `auge_punkte` sagt nur, ob sich ein Feld ändert (`punkte_lauf_s.py`, `punkte_lauf_s.txt`, 38 Aufzeichnungen). Die Urteile hier sind je Punkt gegen die Erwartung gerechnet: `punkte_rechnen1.py` bis `punkte_rechnen5.py`, Ausgaben in `punkte_rechnung1.txt` bis `punkte_rechnung5.txt`, dazu `belege_sonderfaelle.txt` und die `.regeln.json`. Die Tabelle erzeugt `punkte_urteile.py`.

**Worte:** bestätigt und widerlegt heißen: Die Lage kam vor und die Rechnung ist gemacht. teils: Ein Teil ist gerechnet, der Rest der Lage fehlte. gemessen: Erwartung war nur „notieren“. Lage fehlte: Die Lage kam in Lauf S nicht vor. offen: Lage kam vor, Feld nicht lesbar oder ungeklärt.

| Urteil | Punkte |
|---|---|
| widerlegt | 6 |
| bestätigt | 28 |
| teils | 17 |
| gemessen | 1 |
| Lage fehlte | 21 |
| offen | 2 |

## Was die Lauf-S-Lagen noch brauchen

| Versuch | Punkte |
|---|---|
| Mauer je Art | P353 bis P357, P366 bis P368, P322 |
| Lord durch echte Gegner | P362 |
| Nachladen mit Stein und Befehl | P308, P309 |
| Trupp aus 6 Schwertkämpfern, einer im Nahkampf | P325, P326 |
| Öl und Haltung | P323 |
| Tor: Feind auf den Feldern, Entwarnung, Durchgang | P303, P304 |
| Turm: anlegen, oben stehen | P344, P302, P338 |
| Grenzen: 39 gegen 41 um die Burg, 1 und 2 Mann an der Ramme | P324, P328 |
| Laufen: bergauf, unerreichbar, über Feuer, an Feinden vorbei | P330, P343, P314, P352, P371 |

## Widerlegt (6)

| Punkt | Funktion | Beleg |
|---|---|---|
| P297 | `UpdateEntity_PoisonCloud` | 7 von 7 Giftwolken: logicalState 3 nach 828 Takten, nicht 808. Im Code läuft ab rng_2 800 eine Ausblendung, sie dauert 28 Takte statt der angenommenen 8. |
| P334 | `getRemainingRequiredEngineers` | Der Zähler steigt nicht je Ingenieur, er springt: Schild 0 auf 1, Katapult 0 auf 2, Trebuchet 0 auf 3, Belagerungsturm 0 auf 4. |
| P337 | `playerMakeUnitSelection` | Mit zu wenig Ingenieuren bleibt das Feld 0, in 5 Gerätearten mit 1 Mann zu wenig. Der Ingenieur wartet 2 Felder daneben. |
| P339 | `tryAttackUnitID` | Beim Angriffsbefehl bleibt huntedBy 0 (19 von 19 Zielen, reichweite). Bei Zielen, die der Hund selbst wählt, geht es von 0 auf 1. |
| P345 | `UpdateBatteringRam` | 125 je Treffer an Hütte, Tor und Turm (je 1 Treffer, belagerung). Der Code übergibt 50. Woher der Faktor kommt, ist nicht nachgesehen. |
| P365 | `UpdateArabianArcher` | Das Feld zählt nicht die lebenden, es summiert sie je Takt: 720 nach 10 Takten mit 72 Bogenschützen, am Ende 22.280 bei 0 lebenden. |

## Bestätigt (28)

| Punkt | Funktion | Beleg |
|---|---|---|
| P298 | `UpdateFireEntity` | Solange die Hütte brennt: someTracker 1 mit Zähler 0 in 24.785 von 24.785 Rahmen, nie 2. Danach steigt erst der Zähler, dann 2 (1.596 Rahmen), also nicht sofort. Neue Feuer: 240 von 309 haben einen Nachbarn mit Stufe plus 1, 51 einen anderen, 18 keinen. |
| P299 | `UpdateTunnel` | 4 von 4 Gräbern: Flag 2 im selben Takt wie Zustand 3 (1.001, 1.012, 1.003, 1.005). |
| P300 | `processDamageFromKillingPit` | Werkzeug: Zahl passt. Dazu sonder1: 3 Gruben, 3 x 18.000, je 24 Takte auseinander. |
| P301 | `lightUpBuilding` | Abklingzeit der Hütten bis Takt 360. 3 Feuerstrahlen flogen davor, fireDuration blieb 0 bis Takt 553. Beides zugleich in 0 Rahmen. |
| P313 | `checkSkirmishGameDefeat` | 2 von 2 Läufen: Feld des Gegners wird 1, gameOver 1, playerIsAlive[1] = 1 und [2] = 0, rund 305 Takte nach dem Sterben des Lords. Der Lord fiel durch den Testbefehl. |
| P315 | `computeTotalUnitsWithinDistance` | (Wert, Anzahl) = (12, 3) bei 3 Speerträgern, (32, 8) bei 8, (16, 4) bei 4 lebenden. Wert 4 je Speerträger. |
| P316 | `updateUnitDeathHeatmapIn3SpacesAroundTile` | Editor, nahkampf: 45 Felder +3, 356 +2, 705 +1. Gefecht, nahkampf_g: 0 Änderungen bei Toten von Menschen. In beschuss_g 3 Fälle mit genau diesem Muster, wer dort starb, ist nicht zugeordnet. |
| P317 | `UpdateLadderManState01` | 2 von 2 Leitern: Richtung 2, Blick des Trägers 2. |
| P318 | `CheckTribeActivityPercentages` | schlacht_20: Trupp mit Schläger, Anteil über 10 in 1.384 von 1.412 Rahmen, die übrigen 28 mit Anteil 0. |
| P321 | `updatePitchDitches` | sonder5_g, 2 von 2: Zustand 2 bei Takt 501, 3 bei 526, weg bei 729. Auf 25 Takte genau. |
| P327 | `computeTribePercentages` | Anteil zwischen 0 und 100, bei Kampf über 0. |
| P333 | `recomputeTroopValuesForPlayer` | 10 von 10 Wechseln im Fenster (Lastverteiler 12, 13, 14, 103, 163). Der Teil über Fernkämpfer ist nicht getrennt geprüft. |
| P335 | `findClosestLaddermanWithLadderPosition` | 2 von 2: Zustand 3 ab Takt 136. |
| P336 | `unitIsInMoat` | Werkzeug: Zahl passt. |
| P340 | `UpdateBurningMan` | 16 Brennende in 4 Szenen: Besitzer 0 und dying 1 in allen Rahmen. |
| P341 | `UpdateShield` | Takt 39: Zähler 1, Schild von Zustand 6 auf 0, Ingenieur 109 (0x6D). |
| P342 | `harassBuildingsWithSiegeAI` | Eigenes Katapult, nicht gegnerisch: 10 Schüsse, Munition 0, letzter bei Takt 1.695, danach keiner bis 1.978. |
| P346 | `processMeleeInitiation` | 11 von 11 Nahkämpfern: erster Schlag bei 1,6 bis 2,0 Feldern. |
| P347 | `findNearestEnemyAndHeadTowardsIt` | Aggressiv auf 24 Felder: -220 und -221. Defensiv auf 4: -59 und -60. Das passt zu -30 minus Abstand in Mikro (192 und 32), bis auf 3. |
| P348 | `unitClimbing` | 6 von 6 Steigern: climbingState 1 bis 5, je 96 Takte, field219 höchstens 95. |
| P349 | `UpdateTunneler` | Frame steigt bis 23, dann 0. Zustand 4: 5 x 50 Schaden bei Frame 60 bis 64, Ende bei 65. Die Höhe steigt im Gang von 8 auf bis 22, die einzelnen Schritte 6, 12, 18, 24 kann das Raster von 25 Takten nicht zeigen. |
| P351 | `UpdateCrusaderArcher` | Weit weg sitzen sie: 21.411 Rahmen über 400. Fast alle Wechsel zum Hinsetzen liegen an der Grenze (902 bei 390 bis 399, 17 bei 400 bis 409), dort wechselt es ständig. |
| P359 | `UpdateCatapult` | Verbrauch gleich Schüsse: 10 von 10, 7 von 7 bei 5 Katapulten. |
| P360 | `UpdateTrebuchet` | Verbrauch gleich Schüsse: 5 von 5, 3 von 3, 1 von 1. Der Kuhwurf lässt die Munition unverändert. |
| P361 | `UpdateMangonel` | 11 Salven mit je 7 Geschossen. |
| P363 | `UpdateBallista` | Werkzeug: Zahl passt. |
| P364 | `UpdateCageDog` | Bei 8 Feinden wechseln die Hunde bei Takt 8 bis 33 von 0xD2 auf 109, bei 3 Feinden nicht. |
| P369 | `UpdateFireBallista` | Werkzeug: Zahl passt. |

## Teils (17)

| Punkt | Funktion | Beleg |
|---|---|---|
| P304 | `UpdateGateHouseLarge` | 21 Tore: pathLinkageRelated2 0, 1, 2 mit gateState 12, von 1 auf 2 in 27 bis 50 Takten, meist 47 oder 48. Abstand des Feindes beim Wechsel 3 bis 16 Felder, die Grenze 25 ist nicht gefahren. gateState 10 kam in keinem Rahmen vor, nur 0 und 12. Entwarnung und Durchgang fehlen. |
| P308 | `TryAcquireAmmunitionOrPlanToBuyStone` | Ohne Stein kein Nachladen: Katapult bleibt auf 0 (besatzung). Mit Stein nicht gefahren, im Code -10 Stein und +20 Munition. |
| P322 | `processDamageToBuilding` | Mitte der Mauer: Schaden +20, Höhe -20, erster Treffer -40. Ende (1 Nachbar): +30, also 1,5-fach. Mehr als 2 Nachbarn nicht gefahren. |
| P324 | `recomputeTotalTroopValueOfTroopsNearKeep` | 6 Bogenschützen 36, 8 Speerträger 32, Wechsel bei Takt 294 und 495. Die Grenze 39 gegen 41 ist nicht gefahren, im Code unter 41. |
| P328 | `giveTribeAnInstruction` | Ramme mit 4 Mann fährt 20,5 Felder, mit 3 steht sie. Mit 1 und 2 nicht gefahren, Befehl war Fahren, nicht Gebäudeangriff. |
| P329 | `updateTribeCombatStanceBehavior` | Zähler +1 je Takt, field93 läuft ab 51 bis 59 und fällt auf 0. Der Abstand zur Leit-Einheit ist nicht gemessen. |
| P330 | `calculateUnitMovementSpeed` | Eben: 19 Arten, berechnet gleich movementSpeed (Werte 1, 2, 3). Bergauf nicht gefahren. |
| P344 | `UpdateSiegeTower` | Zustand 6, dann 0 mit Bemannung 4, fährt ab Takt 407 bis 710. Das Anlegen an die Mauer und das neue Gebäude fehlen. |
| P353 | `UpdateSpearman` | Speerträger: Hütte 10, Tor 2 je Schlag, alle 48 Takte. Mauer nicht gefahren. |
| P354 | `UpdatePikeman` | Pikenier: Hütte 40, Turm 10, Tor 5 je Schlag, alle 28 Takte. Mauer nicht gefahren. |
| P355 | `UpdateMaceman` | Keulenträger: Hütte 80, Tor 5 je Schlag, alle 48 Takte. Stärker als Tor wie erwartet, die Werte weichen von 35 und 4 ab. |
| P356 | `UpdateSwordsman` | Schwertkämpfer: Hütte 100, Tor und Turm 10 je Schlag, alle 60 Takte. Mauer nicht gefahren, die Werte weichen von 70 und 6 ab. |
| P357 | `UpdateKnight` | Ritter: Hütte 100, Tor und Turm 10 je Schlag, alle 72 Takte. Mauer nicht gefahren. |
| P366 | `UpdateSlave` | Sklave: Tor und Turm 1 je Schlag, alle 93 Takte, an der Hütte kein Schaden. Mauer nicht gefahren. |
| P367 | `UpdateAssassin` | Assassine: Hütte 75, Turm 5, Tor 3 je Schlag, alle 93 Takte. Mauer nicht gefahren. |
| P368 | `UpdateArabianSwordsman` | Arabischer Schwertkämpfer: Hütte 100, Tor und Turm 10 je Schlag, alle 96 Takte. Mauer nicht gefahren. |
| P371 | `UpdateHorseArcher` | Mit Ziel in Reichweite: Zustand 4 nach 7 Takten, dann alle 77 Takte ein Schuss. Im Laufen nicht gefahren. |

## Gemessen (1)

| Punkt | Funktion | Beleg |
|---|---|---|
| P311 | `ClickGiveUnitsInstruction` | Param0 Gruppe, Param1 Anweisung, Param2 und 3 das Ziel (Nummer und uid, x und y oder Feldnummer), Param4 0. In allen Läufen so benutzt, auch Zuschütten wirkte mit 0, das Menü sendet dort 1000. |

## Lage fehlte (21)

| Punkt | Funktion | Beleg |
|---|---|---|
| P302 | `UpdateTower4` | Keine Einheit stand auf einem Turm der Stufe 4. hasUnitsOntop wechselte 4-mal, aber nicht in einem Versuch dafür. |
| P303 | `updateGateDrawBridgeOpenCloseLogic` | Keine feindliche Einheit stand auf den Torfeldern. gateCloseOpenTimer war in allen Toren immer 0, die 1.200 kamen nicht vor. |
| P307 | `areActivePlayersMostlySameTeam` | Kein Gefecht 2 gegen 1. |
| P309 | `SelectionReplenishAmmo` | Kein Befehl zum Auffüllen gegeben. |
| P310 | `ClickMoveUnit` | Kein Mausklick, unser Laufbefehl geht über Anweisung 17. |
| P312 | `CommandSpawnEntity` | Anderer Spielmodus. |
| P314 | `doMoveFromTileToTile` | Keine Einheit lief auf ein brennendes Feld zu, counter blieb 0. |
| P319 | `aiPlaceAIVBuilding` | Keine KI in Lauf S, gehört zu Lauf K. |
| P320 | `resetCountdownInHeatMap` | Keine KI in Lauf S. |
| P323 | `ifNecessaryThrowOilAutomatically` | Haltung gegen Öl nicht gefahren. |
| P325 | `applyMoveCommandOrRallyCommandToTribe` | Kein Trupp mit einem Nahkämpfer bekam einen Marschbefehl. |
| P326 | `giveTribeMoveInstruction` | Kein Trupp aus 6 Schwertkämpfern. Nur 2 Tunnelgräber: Abstand 1. |
| P331 | `shouldUnitsEngageInMelee` | Rush-Schutz nicht eingestellt. |
| P332 | `ComputeDamageFearFactorBonus` | Angstfaktor nicht geändert. |
| P338 | `isTowerTileOvercrowdedByCurrentPlayer` | Niemand auf einem Turm. |
| P343 | `setDestinationForUnit` | Keine Einheit zu einem unerreichbaren Feld geschickt. |
| P350 | `UpdateQuarryMason` | Kein Steinbruch. |
| P352 | `UpdateCrossbowman` | Kein Marsch an einem Feind vorbei. |
| P358 | `UpdateMonk` | Keine Kathedrale. |
| P362 | `UpdateLord` | Der Lord fiel durch den Testbefehl, nicht durch einen Gegner. Das Gold von Spieler 1 blieb gleich. |
| P370 | `updateUnits` | Assassinen standen in vielen Szenen, aber kein KI-Angriff. Die Felder blieben 0. |

## Offen (2)

| Punkt | Funktion | Beleg |
|---|---|---|
| P305 | `UpdateUnitLossData` | Das Feld steht nicht in der Aufzeichnung. |
| P306 | `processUnitLossStatistic` | Einheiten fielen durch Gegner, finalKillMatrix änderte sich in keinem Lauf, auch nicht bei Spielende. Vermutlich erst beim Ergebnisbildschirm, nicht nachgesehen. |

## Gesamtproben an drei Szenen

| Probe | Punkt | Einzel Gefecht | 1.000 gegen 1.000 |
|---|---|---|---|
| A1 Felder außerhalb der Liste | 241 | 10 | 3 |
| A3 Takte | Tempo 200, nicht streng | Tempo 100: 848 fehlen, 782 gemischt. Das Werkzeug schreibt „widerlegt“, weil es Tempo 100 als streng behandelt; die Szene war absichtlich nicht streng | Tempo 1000, nicht streng |
| A4 Lesen je Takt, Median und Höchstwert | 1,2 und 15,3 ms | 2,6 und 14,6 ms | 0,6 und 15,3 ms |
| A7 Zufallsfolge passt zur Tabelle | 2.315 von 2.315 | 5.120 von 5.120 | **2.173 von 2.174** |
| A10 Platzwechsel ohne Verstoß | 7.776 | 17.912 | 9.745 |

A1: Die ersten 14 der 241 Felder gehören zum Befehlsring `DAT_GameCommand...`, weil hier viele Befehle liefen. Alle 241 sind nicht einzeln angesehen. A7: Der eine Fall auf Tempo 1000 ist nicht geklärt, vermutlich ein Rahmen über die Taktgrenze.
