# Einzelpunkte Lauf F

Lauf F 02.11.2026 21:42, Instanz 2, Burgenbau, Liga-Balance. Geschrieben von SRE aus den Belegen, Rechnungen in `punkte_rechnen*.py`.

**Worte:** bestätigt und widerlegt heißen: Die Lage kam vor und die Rechnung ist gemacht. gemessen: einmal gelesen, Erwartung war "notieren". gesehen: Die Lage kam vor, das Feld änderte sich, nachgerechnet ist es nicht. Lage fehlte: kommt in Lauf K oder S. offen: von hier aus nicht zu beantworten.

| Urteil | Punkte |
|---|---|
| bestaetigt | 151 |
| widerlegt | 15 |
| gemessen | 75 |
| gesehen | 0 |
| Lage fehlte | 0 |
| offen | 0 |

## Widerlegt (15)

| Punkt | Funktion | Beleg |
|---|---|---|
| P117 | `UpdateCampGround` | vclock folgt nicht der Beliebtheit: Es ist die Zuzugsuhr. Sie läuft von 2000 bis 4000, je Takt um gathering_rate/4 (gemessen +9 bei Beliebtheit 90 bis 94, +10 ab 95). Über 4000 kommt ein Bewohner und sie fällt um 2000. Also 1 Bewohner je 8000/gathering_rate Takte. Kein Platz frei: Sie steht auf 4000. |
| P118 | `processPlacementResourceLossForBuildingType` | 4 Pechgräben kosteten 2 Pech, nicht 1: 16 auf 15 beim ersten, 14 beim dritten. |
| P131 | `UpdateHuntersPost` | Bis 15 statt 6: Im Speicher steht 15 (`UpdateHunter`, UCP3). Gemessen: Jäger trägt bis 18, das ist 15 mal Produktivität. Fleisch im Lager +1 je Stück. |
| P143 | `updateFearFactorProductivity` | Stufe +3 ergibt laut Speicher 76, nicht 70 (UCP3). Gemessen: +5 ergibt 60, +2 ergibt 84, -5 ergibt 180 (sonder10_g), dazu -1: 116, -2: 132, -3: 148 aus Lauf F. |
| P163 | `SetStorageMarketFailState` | Kauf bei vollem Waffenlager über Befehl 38 wird abgelehnt, das Feld bleibt aber 0. Der Grund wird über diesen Weg nicht gesetzt. |
| P174 | `queueCommand` | commandDelay steht im Einzelspiel auf 0, nicht auf 35. Vom Befehl bis zum Gebäude vergehen gemessen 2 bis 6 Takte. |
| P179 | `WindowMsgProcessingFunc` | Die Taste geht als Fensternachricht ohne Maus. + von 20 auf 25 stimmt, die Grenzen nicht: + 88 auf 93, 90 auf 100, 200 auf 300, 1.000 auf 1.100. - 20 auf 15, 11 auf 6, bei 10 und darunter bleibt es. Die Stelle weicht im Speicher ab (13 Befehle). `rufen_*.json`. |
| P183 | `planToBuyWhenLowOnResourceAndSnoozeBuildings` | Direkt gerufen, echte KI: Zähler +1 je Aufruf stimmt. Der Wunsch 5 entsteht aber bei Zähler 3, nicht bei 37. War er schon 3, bleibt er. Die Funktion weicht im Speicher ab (14 Befehle). `rufen_*.json`. |
| P192 | `validateWallPlacementAtTile` | Feindgebäude: nur das angrenzende Feld ist verboten, Turm, Hütte und Lager gleich. 4 Felder Abstand sind erlaubt. Die Grenze 5 gilt für Feind-Einheiten: Abstand 1 bis 4 verboten, ab 5 frei. `rufen_*.json`. |
| P218 | `UpdateOx` | Ladung 12, nicht 8: Im Speicher steht 12 (`UpdateQuarryWorker`, UCP3). |
| P220 | `UpdateInnkeeper` | Füllstand steigt um 120 je Bier, nicht um 160: Die Liga setzt flagons_per_beer 120. |
| P225 | `UpdateQuarryWorker` | Der Bruch füllt bis 12, nicht bis 8, siehe P218. Stein im Lager +1 je Stück (23 Mal), 2 und 3 sind mehrere in einem Rahmen. |
| P228 | `UpdateHopsFarmer` | Hopfenbauer trägt im Einzelspiel bis 6, nicht 1. |
| P234 | `UpdatePoleTurner` | Holz in der Werkstatt 0, 1, 0, fünfmal: 1 Holz je Pike, nicht 2. `punkte_rechnung20.txt`. |
| P241 | `UpdateSlinger` | countSlingers2 zählt keine Schleuderer: Es steigt seit Takt 16.541 je Takt um 1 auf 32.261, ohne einen einzigen Schleuderer zu Beginn. Der Name ist falsch. |

## Bestätigt (151)

| Punkt | Funktion | Beleg |
|---|---|---|
| P001 | `isSameTeam` | Gesetzt im Messlauf, 4 Paare: playerTeams 1, 1, 2, 2, 3, 3, 4, 4, das Spiel zeigt Teamwappen. Der Startbefehl `teams` allein wirkte auf diesem Weg nicht. Das Spiel endete mit gameOver 1 bei Takt 161.812, beide Lords von Team 1 lebten noch. `punkte_rechnung_b.txt`. |
| P014 | `resetCountsAndStatistics` | armySize fällt mitten im Takt auf 0 und steht danach wieder auf 18, 384 Wechsel. |
| P018 | `getPreviousGoodsFilteringUnallowed` | 20 Einträge vor -1. |
| P019 | `getBatchBuyPrice` | Tabelle gelesen. Kauf aller Waren kostete -3.420 Gold, Verkauf brachte +1.610: beides stimmt auf das Gold mit der Tabelle (Verkauf: Preis je 5 Stück). |
| P020 | `initPopularityAndRecruitableDefaults` | euroRecruitable und mercRecruitable alle 1, someCount44 = storedPopularityPercent = 9000. |
| P021 | `initializeGameStateAfterMapLoad` | Lauf K: 25 von 25 Preisen gleich dem Burgenbau aus Lauf F, also nicht aus der Karte. Es sind die Liga-Preise. |
| P023 | `importTradingCosts` | Kopie gleich der Preistabelle. Die Werte sind die der Liga, nicht die Grundwerte. |
| P039 | `setAICParameters_15` | aics[15]: 10, 4000, 1, gleich dem Grundwert. |
| P040 | `setAICParameters_16` | aics[16]: 50, 12, 37, gleich dem Grundwert. |
| P052 | `recomputeAIAvailableGridTiles` | Lauf K: Alle 8 KI: Zähler 11 bis 24, Cooldown 0. Der Zweig ohne Eisen in Reichweite kam nicht vor. |
| P053 | `applyAIV` | Lauf K: Nur Status 0 und 1. 1.634 von 1.634 Bau-Schritten liegen im 100x100-Feld ab dem Versatz. Bei den 593 Wand-Schritten ist `location` keine Kachel, sondern der Anfang in `locationsArray`; davon je Spieler 9 Felder geprüft, alle im Feld. |
| P056 | `setMapSize` | 400, 300, 200, 160, 100, -1: absteigend mit Ende -1. |
| P058 | `getBuildingSizeForCommandBuildingType` | Die Sprungtabelle ab 0x4fa5e8 ist im Speicher gleich wie in der Programmdatei, UCP3 ändert hier nichts. `punkte_rechnung5.txt`. |
| P059 | `updateMacroLayerRelated` | Im Editor gesetzt (Spielbefehl 21, Pinsel 1, Flag 0x20000000): Randfelder `MacroLayer & 0x3f` = 1, innere 2, 4, 8. 0x10 kam nicht vor. Mit Pinsel 0 setzt der Befehl nichts, nur der Graben setzt seine Größe selbst. `rufen_*.json`. |
| P061 | `placeBarracks` | Beträge 0 oder 5. |
| P070 | `sortAttackInfoTribeIDArrayBasedOn` | Ganze Rangtabelle (2160 Byte) gleich wie in der Programmdatei, 0xb4c880 beginnt mit 10, 9, 5, 3 wie erwartet. |
| P071 | `placeSiegeTentsAndAssignEngineers` | Zeltart 190, 191, 193, 192, 194, an Platz 8: 358. Ingenieure 2, 3, 4, 4, 1, an Platz 8: 2. Gleich wie in der Programmdatei. |
| P086 | `convertCommandBuildingTypeToBuildingType` | Lauf K: Art 83 ergibt die Ramme (9 Mal Art 59), Art 84 den Schild (8 Mal Art 60). Der Name BT_SIEGETOWER für 83 im Typ-Verzeichnis stimmt also nicht, BT_S_BATTERINGRAM schon. Art 82 baute keine KI. `punkte_rechnung_k.txt`. |
| P087 | `chooseProductionItemType` | Zweiter Bogenmacher fertigt wieder Bogen (17): Das neue Gebäude wird mitgezählt. |
| P088 | `countBuildingsForPlayer` | +0x2C8 war in 20.909 Lesungen je Gebäude immer 0. Der Sonderzustand kam nicht vor. |
| P089 | `findClosestInnBuildingID` | Humpen sinken, Lieferung füllt auf, vor der ersten Lieferung 0. |
| P090 | `recomputeAllFearFactors` | Formel stimmt bei allen 7 Stufenwechseln, Stufen -3 bis 0. |
| P091 | `getResourceSpace` | Kauf bei vollem Waffenlager: Speere 11 und 11, Gold 95.255 und 95.255. |
| P092 | `getPriceForDisbandedUnitType` | Tafel direkt aus der Funktion: Bogenschütze 12 wie erwartet, Speerträger 8, Armbrust, Pikenier, Keule, Tunnelgräber 20, Schwert, Ritter 40, Leiter 1, Ingenieur 30, Mönch 10, Art 39: 150, Art 40: 200, Art 41 und 61: 80, Art 77: 100. Gold gibt es laut Code nur in Siege That, das ist nicht gefahren. `rufen_*.json`. |
| P093 | `growWheat` | Wechsel auf 8: 11 von 13 mit 4 Feldern auf 121, 2 mit 3 Feldern, dafür hat der Code einen zweiten Weg. Es zählt nur beim Wachstumsschritt. `punkte_rechnung26.txt`. |
| P094 | `setupBarracksCampgroundPositions` | Total 72. Ob die Einheiten dort stehen, ist nicht nachgerechnet. |
| P095 | `setupMercenaryPostCampgroundPositions` | structureRelated1 72. Ob die Söldner dort stehen, ist nicht nachgerechnet. |
| P096 | `growHops` | Stand 5 mit mindestens 6 Feldern auf Stufe 14 bis 27 in 334 Kartenrahmen, in keinem anderen Stand. `punkte_rechnung21.txt`. |
| P097 | `updateNeededEmployeeCount` | Werte 0 bis 3, je Art die Zahl der Plätze. |
| P098 | `updateAllBuildingsSnoozedState` | sleeping 0, 1, 0 bei beiden Bogenmachern. Die Bestände dabei sind nicht geprüft. |
| P099 | `processBuildingIDsNeedPeasantsQueue` | Offene Plätze 0 am Ende der Bauern, einzeln nicht nachgezählt. |
| P100 | `updateRepairCostAndReturnIfDamaged` | Direkt gerufen, Wachturm 500 Leben: voll Rückgabe 0, Kosten ungeschrieben. Leben 499: Stein 1, 250: 6, 125: 9, 1: 11, Holz 0. Das passt zu (max-akt)*12/max, mindestens 1. `rufen_*.json`. |
| P101 | `UpdateWoodcuttersHut` | countWoodcutters 1 bei 1 Hütte. |
| P102 | `UpdatePitchRig` | Pechgrube ohne Vorkommen gesetzt (Prüfung umgangen): countPitchRigs 1 in 200 Lesungen über 4.000 Takte, also je Durchlauf neu gezählt. `rufen_*.json`. |
| P103 | `UpdateMercenaryPost` | someCount04 15 = Söldnerposten 5 + Kaserne 10, je Takt neu. |
| P104 | `UpdateBarracks` | someCount04 15 = Söldnerposten 5 + Kaserne 10, je Takt neu. |
| P105 | `UpdateFletchersWorkshop` | 1 bis 3: zwei Bogenmacher und ein Lanzenmacher. |
| P106 | `UpdateArmorersWorkshop` | 2: eine Schmiede und ein Rüstungsschmied. |
| P107 | `UpdateBakery` | 1 und 1 bei einer Bäckerei. |
| P108 | `UpdateBrewery` | 1 und 1 bei einer Brauerei. |
| P109 | `UpdateGranary` | Kornkammer gesetzt, Brot gesperrt: totalFood 25 auf 16, Zähler Brot 0, die Kammer behält ihre 13. Frei: Es zählt wieder. Sperren ist kein Spielbefehl, sondern ein Knopf der Oberfläche, der nur im Einzelspiel wirkt. `rufen_*.json`. |
| P110 | `UpdateInn` | Im Jahr sinken die Humpen in 263 von 273 Schritten genau alle 36 Takte, aleRate 36. |
| P111 | `UpdateOilSmelter` | Schmelze mit 2 Ingenieuren und Lager: Pech +1 in Zustand 4 (Takt 1.335), -1 beim Übergang 7 nach 8 (Takt 1.750), im selben Takt hat der zweite Ingenieur Traglast 1. Zustand 1 verlässt sie, wenn ein Ingenieur einsteigt: mit Pech nach 6, ohne nach 2. `punkte_rechnung24.txt`. |
| P112 | `UpdateWheatFarm` | Zählt je Takt +1 bis 150, dann auf 0 (63 Rücksprünge im Jahr). |
| P113 | `UpdateHopsFarm` | Zählt je Takt +1 bis 400, dann auf 0 (24 Rücksprünge im Jahr). |
| P114 | `UpdateDairyFarm` | Zähler bis 400, dann 0, 3 Kühe. |
| P115 | `UpdateStables` | 4 Pferde im Abstand von zusammen 3 x 551 Takten. |
| P116 | `UpdateKeepStronghold` | Startgold 2.000 (Lauf K, Bündnislauf): Rest und Konto gehen gleich, alle 4 Takte: über 1.000 um 100, über 100 um 10, darunter um 1. Bei Takt 800 bis 802 ist der Rest 0. `punkte_rechnung18.txt`. |
| P119 | `processWallBuildingLoss` | Direkt gerufen: 8 niedere 2 Stein, 8 hohe 4, 13 niedere 3, 13 hohe 6. Im echten Befehl gleich: Art 25 mit 13 Feldern 6, Art 46 mit 13 Feldern 3, Art 46 mit 8 Feldern 2, Art 25 mit 8 Feldern 4 (sonder24_g). Die -1 aus Lauf F erklärt das nicht. `rufen_*.json`. |
| P120 | `applyGateOrDrawbridgeOpenCloseChange` | Offen 11 mit Timer 600 und abwärts, zu Timer -1. Danach wird der Zustand 12, siehe P132. |
| P121 | `UpdateIronMine` | Menge 7 gesetzt: Am Ende von Zustand 5 geht die Mine mit 6 nach 0, mit 7 nach 6 (Takt 6.564). Guss +1, Stand 8 gelesen. In Lauf F höchstens 3. `rufen_*.json`. |
| P122 | `UpdateQuarry` | 46 von 50 Steinen kommen bis 9 Takte nach dem Wechsel von 1 auf 0. Der Stapel steht höchstens auf 47. Bei 47 endet der laufende Zyklus (Zustand 0 bei Takt 34.069). `punkte_rechnung26.txt`. |
| P124 | `UpdateCatapultBuilding` | Lauf K: 9 Zelte, Art 80, Fortschritt höchstens 319, dann Katapult (6 Mal bis 40 Takte danach gesehen). +1 oder +2 je Takt. |
| P125 | `UpdateTrebutchetBuilding` | Lauf K: 12 Zelte, Art 81, Fortschritt höchstens 639, +1 je Takt, dann Trebuchet (9 Mal gesehen). |
| P126 | `UpdateSiegeTowerBuilding` | Zelt Art 82 (Mapper 192, Mapper 94 baut Art 69, kein Zelt): 4 Ingenieure +4 je Takt, Turm bei Takt 540 über 1.280, Zählfeld 4. 2 Ingenieure +2 je Takt, Turm bei Takt 854, Zählfeld 0. `punkte_rechnung25.txt`. |
| P127 | `UpdateBatteringRamBuilding` | Lauf K: 10 Zelte, Art 83, Fortschritt höchstens 644, +2 je Takt, dann Ramme (9 Mal gesehen). |
| P128 | `UpdateShieldBuilding` | Lauf K: 12 Zelte, Art 84, Fortschritt höchstens 121, +1 je Takt, dann Schild (8 Mal gesehen). |
| P129 | `setupBuildingData` | currentGameMode 0, cooldownTimer höchstens 400. |
| P130 | `giveBackResourceForDestroyedBuilding` | Mit Param1 50 genau die Hälfte: Bogenmacher (Liga 18 Holz, 100 Gold) gab 9 und 50, Galgen (40 Gold) gab 20. |
| P132 | `UpdateGateHouseSmall` | gateState 11 dann 12, pathLinkageRelated2 0, 2, 1. |
| P133 | `SomePopularityRelatedComputation` | Skala bestätigt: 100 angezeigt = 10000, 50 = 5000 (Spielcode). Mitten in der Wochenrechnung steht kurz bis 10375. |
| P135 | `ComputePlayerPoints1` | Direkt gerufen: Rückgabe gleich der Formel für alle Spieler (754, 540, Rest 0). 1.000 Gold mehr geben 100 Punkte mehr. Die Anzeige im Spiel ist nicht verglichen. `rufen_*.json`. |
| P136 | `updateDateAndTime` | Monat höchstens 11, danach Jahr +1. |
| P137 | `computeBuildingCategoryEntryPointAndDestroyEarlierBuilding` | Alte Kaserne 44 ist weg, neue 104. |
| P138 | `getWallTilesThatCanBeBuilt` | Direkt gerufen: Stein 20 gibt 40, mit Rest 39, Stein 1 gibt 2, mit Rest 1, ab Stein 125 Decke 250. Holz genauso. `rufen_*.json`. |
| P139 | `getSellResourceAmount` | Code: unter 50 Stück 5, unter 100 Stück 10, unter 200 Stück 20, sonst 50. Gemessen: Holz 106 -20, Essen 60 -10, Stein 43 -5. |
| P140 | `updateFoodTypesInStockForAllPlayers` | Lauf K: Das Feld ist die Zahl der Sorten, 2 Sorten in 31.876 Rahmen. Zusatz: Das Feld steht rund 5 bis 9 Prozent der Rahmen kurz auf 0 (2 bis 7 Takte, einmal 18), obwohl Essen da ist, nie auf einem anderen falschen Wert. Warum, ist offen. `punkte_rechnung18.txt`, `punkte_rechnung21.txt`. |
| P141 | `processFoodConsumption` | foodClockSpeed je Kopf bei Ration 0 bis 4: 0; 1,5; 3; 4,5; 6. Bei 40 Leuten und Ration 3 also 180. |
| P142 | `updateAleRate` | 36 ab der ersten Woche, davor 30. |
| P144 | `recomputeReligionBonuses` | religionVar1 0 auf 1 bei der Kapelle. |
| P145 | `calculateTaxIncomeForPlayer` | Formel bestätigt: je Woche Leute x Gold-Tabelle x 2,5 aufs Sammelfeld (Stufe 5: 58 Leute, +101), je Monat ein Zehntel aufs Gold. Die erwarteten 80 sind der Grundwert, die Liga gibt 70. |
| P146 | `calculateTaxBribeExpenseForPlayer` | Dieselbe Formel: Stufe 1, 54 Leute, +67 je Woche. Die erwarteten 80 sind der Grundwert, die Liga gibt 50. |
| P147 | `despawnPeasantOrWorker` | Direkt gerufen, ohne Bauern: UT_HEALER 34, UT_PRIEST 33, UT_INNKEEPER 36, dann UT_BREWER 17, UT_TANNER 21, UT_ARMORER 20, Art 19, UT_POLETURNER 18, UT_FLETCHER 4, Art 12. Danach nahm die Funktion einen echten Arbeiter, dort endete die Probe. `rufen_*.json`. |
| P148 | `recountStablesAndHorses` | 4 auf 3 beim Ritter. |
| P149 | `computePopulationStatistics` | Statistik[Index-1] = Leute am Monatswechsel: 12 bei Index 3, 16 bei Index 4 und so weiter. |
| P150 | `updatePopularity` | Stufe 10: -750, Stufe 11: -1000 (Liga). Crowding blieb 0. |
| P151 | `updateTaxing` | 3 von 3 Monaten: Gold +38, +111, +116 = lastMonthsIncomeTax. Bei Bestechung +3 -26 = -23. |
| P152 | `processSingleTimeTick` | weekChanged alle 200 Takte. |
| P153 | `processGameTick` | Steigt im Lauf um 1 je Schritt, in der Pause steht er, nachgelesen. |
| P154 | `IsEuroUnitRecruitableUnk` | Direkt gerufen: normal 1, ein Platz frei 1, am Limit 3 (Heer voll), ohne Gold 0, ohne Speer 0. Das Limit ist 1.160, ein gesetzter Wert ist nach 3 Takten wieder 1.160. `rufen_*.json`. |
| P155 | `ProcessRecruitUnit` | armySize knapp davor aufs Limit gesetzt: Gold 500 auf 502, also kein Abzug. Gegenprobe davor: 500 auf 491, count_2 1. Nach einem Takt steht armySize wieder richtig. `rufen_*.json`. |
| P156 | `CheckIfEnoughGoldForLadderman` | Die Prüfung: 0 bei 3 Gold, 1 bei 4, auch im Speicher. Der echte Befehl verlangt 20 (Liga): bei 3, 4, 19 kein Abzug, bei 20 und 21 sinkt das Gold um 20. Die Oberfläche passt also nicht zum Preis. `rufen_*.json`. |
| P157 | `CheckIfEnoughGoldForMonk` | Mönch 10: Das ganze Anwerben von 18 Einheiten kostete -850, genau die Summe der Tabelle. |
| P158 | `CheckIfEnoughGoldForTunneler` | Liga 25 statt 30: Das ganze Anwerben kostete -850, genau die Summe der Tabelle. |
| P159 | `GateOpenOrClose` | 11 mit Timer 600, zu mit Timer -1. Danach wird der Zustand 12, siehe P132. |
| P161 | `ChangeTaxes` | Rohwerte 0 bis 11. |
| P162 | `ChangeRations` | Rohwerte 0 bis 4. |
| P164 | `ProcessBuyOrSell` | Alle Waren +5, Gold -3.420 = Summe von getBatchBuyPrice. |
| P165 | `ProcessBuildingSleepUpdate` | Byte 0, 1, 0 beim Ein- und Ausschalten. |
| P166 | `ProcessTowerRepair` | Turm von 200 zurück auf 500 bei Takt 293, Holz -5 wie der Befehlswert (sonder19_g). Stein ist nicht zu sehen, der Bestand wird aus dem Lager neu gerechnet. |
| P168 | `ClickRecruitUnit` | Param0 Einheitentyp, Param1 Gebäude: 18 von 18 Einheiten erschienen. |
| P169 | `ClickBuyOrSell` | Param0 0 ist Kauf, 1 ist Verkauf. |
| P170 | `ClickUnitStance` | Spielbefehl 70, Werte Gruppe und Haltung, wirkt (Lauf S, Szene Haltung). |
| P171 | `RemoveTowerSiegeEngine` | Befehl 42 setzt Art 41 und Art 61 auf den Turm, das Konto sinkt um 79, Befehl 75 Art 2 gibt 81: Das sind 80 Gold hin und her, dazu Einkommen. Turmfeld 1 und 2, danach 0. Holz und Stein 0. `rufen_*.json`. |
| P172 | `SetUnitAssemblyPoint` | Spielbefehl 102 (0, x, y): barracksAssemblyPoints[0].x auf den Befehlswert bei Takt 209 (sonder19_g). |
| P173 | `determineGameTicksToPerform` | 39,9 Takte je Sekunde im vollen Dorf. |
| P176 | `updatePathLinkageTileMapRelatedToGates` | Tor schließt: Außenfeld oben verliert Bit 0x10, unten Bit 1. Tor öffnet: Beide kommen wieder (sonder10, Takt 100 und 1.253). |
| P177 | `algTunnelerFindTarget` | Direkt gerufen: Ohne Ziel findet die Suche auch mit 150 Feldern nichts, Bauplatz Fehler 1. Mit Feindturm Art 74: Ziel genau dieser Turm, Bauplatz 8 bis 60 Felder entfernt geht. In sonder6_g auch Mauerfeld 0x100 ohne Bit 2. `rufen_*.json`. |
| P178 | `isTileInRangeOfKeepRange` | Platzkarte in der Probe: Käfig und Wachturm außerhalb des Burgbereichs zeigen Zeichen i, das ist Grund 18 = 0x12 (`probe_befehle_gefecht.txt`). |
| P180 | `isMapperAvailable` | Direkt gerufen: Jäger 1, bei Wild 0: 0, bei Wild 5: 1. Käfig 1, auch bei noDogs 1, das gilt laut Code nicht im Gefecht. Geprüft ist die Oberfläche, nicht ein Baubefehl. `rufen_*.json`. |
| P181 | `aiUpdateTaxesAndRations` | Lauf K: Unter der kritischen Beliebtheit steht die Steuer im Wochentakt auf 2: 1.056 von 1.058 Lesungen (Spieler 6 und 8, die einzigen unter ihrer Grenze). Die 2 anderen zeigen 3 bei Spieler 8, nicht einzeln nachgesehen. |
| P182 | `aiShouldBuildWoodcutter` | Direkt gerufen, echte KI: 5 Hütten: Wert 30 nein, 31 ja. 6 und 7 Hütten: 90 nein, 91 ja. Gezählt wird mit Filter: Spieler 1 hat 7, gezählt 5. Decke je KI 1 bis 10. `rufen_*.json`. |
| P184 | `addBuildingToTargetableBuildings` | Lauf K: Schritt +1 (52 von 60 Wechseln), Höchstwert 100. Dazu -1 (8 Wechsel): `getTargetableBuildingForPlayerID` zieht ab. |
| P185 | `shareGoldAmongTeamMembers` | Gold geht genau von Partner zu Partner: Spieler 4 an 3: 332 und 272, Spieler 2 an 1: 60. Laut Code ruft es die KI ab 2.500 Gold (`updateAIStrengthState`). |
| P186 | `sellExcessGoods` | Lauf K: Stichprobe: Spieler 3 verkauft Ware 13 bei 56 auf 50, Grenze 52 mit Spielraum. In 54 Fällen fiel eine Ware über ihrer Grenze im Verkaufstakt; je Aufruf wird nur eine Ware verkauft, die übrigen gezählten Fälle sind Verbrauch im selben Takt. |
| P187 | `requestGoods` | Direkt gerufen: Ware und Menge stehen beim Partner (Holz 7, Stein 9). Hopfen und Bier nicht, ohne gleiches Team nicht. Der Partner braucht eine Kennung ungleich -1, die hat nur ein Mensch: Darum gab es zwischen KI und KI keine Bitte. `rufen_bitte_20261104.json`. |
| P189 | `aiBuyAndSellGoods` | Lauf K: `willBuy` wechselt nur im Tagestakt des Spielers: 764 von 768, sonst 0 von 38.065. Die 4 ohne Wechsel sind nicht einzeln nachgesehen. |
| P190 | `updateAIBehaviour` | Tag 50, Woche 200, Monat 800 Takte. |
| P191 | `aiDecideOnNewBuildings` | Im Lauf, Gold alle 5 Takte gesetzt: 20.000: +2 (17 Sprünge), 10.000: +1 (19), je rund alle 50 Takte. 3.000: +1 nur rund alle 100 Takte (Wartezeit 2). Direkt gerufen endete das Spiel mit Absturz bei 0x42E812, Ursache nicht geklärt. `rufen_*.json`. |
| P193 | `isBuildingPlacementAllowedAtTile` | Direkt gerufen: Über der Grenze Rückgabe 1 und Warnung Weizen 4, Hopfen 3, Apfel 2, Vieh 1. Genau an der Grenze 0. `rufen_*.json`. |
| P194 | `countMoatsOwnedByEachPlayer` | Lauf K: `moatsOwned` gleich eigener Zählung der Grabenfelder in `moats[]`: 448 von 448 Monatstakten. |
| P195 | `countUnfinishedMoatTilesForPlayer` | Der Graben wurde fertig: stage 2, fillProgress 4. |
| P196 | `advanceMoatDigProgress` | fillProgress 0 bis 4, dann stage 2. |
| P197 | `updateMoatCountdownTimers` | Zähler auf 3 gesetzt: 2 bei Takt 841, 1 bei 1.050, 0 bei 1.249, bleibt 0. Einmal je 200 Takte, bei Stand 40 des Balancers. `rufen_*.json`. |
| P199 | `validateWallBuildPath` | Direkt, Einzelfeld: Lager des Gegners (Art 10): unter 7 Felder vom Rand verboten mit Grund 0x13. Hütte und Turm zählen nicht. Feind-Einheit: unter 15 Felder verboten, Grund 0x11. Außerhalb der Reichweite: Grund 0x12. `rufen_*.json`. |
| P200 | `placeWalls` | 3 Stein, 15 Felder verlangt: 7 Felder gebaut, also 2S+1 (sonder19_g). |
| P201 | `checkBuildingCanBePlacedHere` | Direkt gerufen: Reichweite 45, 50, 60, 70 je Kartengröße 160, 200, 300, 400, um den Punkt 140, 268 bei Burg 138, 262. Karte 200: entferntestes Feld 50 geht, 51 Grund 0x12. Käfige ab 10 Grund 1000. Farm: Grund 0x16 an 742 Stellen, 0x17 (unter 50 Gras) an einer. `rufen_*.json`. |
| P202 | `placeWorkshopOrHovel` | Sechs Hütten 0, 1, 2, 3, 4, 5 in Bau-Reihenfolge. |
| P203 | `placeQuarry` | Steinbruch 55 zeigt auf Halde 56, Typ 21. |
| P204 | `createMoatData` | stage 2, fillProgress 4. |
| P205 | `confirmAndQueueDestructionCommand` | Spielbefehl 29 (Nummer, 100, uid): Hütte weg bei Takt 295 (sonder19_g). |
| P206 | `placeWheatfarm` | Genau 36 Felder mit Bit 0x1000000 bei einer Getreidefarm. |
| P207 | `placeHopfarm` | Genau 24 Felder mit Bit 0x2000000 bei einer Hopfenfarm. |
| P208 | `placeDairyfarm` | 0, 1, 2, 3 bei drei Milchviehhöfen. |
| P209 | `placeBuilding` | Erste Hütte ohne Holz: Holz bleibt 0, Feld 0x288 = 1. Mit eigener Einheit im Grundriss lehnt die Prüfung ab (Fehler 1). Ohne Prüfung gesetzt ist die Einheit weg. `rufen_*.json`. |
| P210 | `recountTotalTroopValue` | 0 auf 224 nach dem Anwerben. |
| P211 | `setUnitStance` | tribes[].unitStance folgt dem Befehl (Lauf S, Szene Haltung): Werte 1 und 2 gesehen. |
| P212 | `nonEuroRecruit` | Liga 50 statt 30: Das ganze Anwerben kostete -850, genau die Summe der Tabelle. |
| P213 | `ComputeGoodsProduced` | Direkt gerufen, 10 Durchgänge je 1 Ware: Produktivität 120 gibt 12, bis 100 gibt 10, 116: 11, 132: 13, 148: 14, 180: 18. Mit Zuschlag im Gefecht 5 mehr. `rufen_*.json`. |
| P214 | `findTunnelTarget` | Direkt ohne Ziel: Stand 1, 2, 3, 4, 5, 6, dann -1, Rückgabe 0. In sonder6_g mit Turm: 0, 1, 2, -1 und 0, -1. `rufen_*.json`, `punkte_rechnung18.txt`. |
| P215 | `getWorkerBlockingStateIfStuck` | Direkt gerufen, Tafel je Arbeiterart und Zustand: Art 19 und 20 in Zustand 1 und 9: 0x38, wie erwartet. Dazu 47, 48, 49, 53 bis 58. `rufen_*.json`. |
| P216 | `spawnUnit` | Aus dem Zelt 20: Lauf K, 15 von 15 Katapulten und Trebuchets. Von mir gesetzte Katapulte haben 10 (sonder10_g). |
| P217 | `UpdatePeasant` | count bis 2, count_2 18 nach 18 Anwerbungen. |
| P219 | `UpdateHealer` | healerCount 1. |
| P221 | `UpdateChild` | Kinder mit gesetztem Zuhause: 60 bleiben. Von 90 gehen genau 15 in Zustand 110, 75 bleiben. Ohne Zuhause verschwinden alle. `rufen_*.json`. |
| P222 | `UpdateWoodcutter` | Holz steigt je Stück um 1 (68 Mal, 2 und 3 sind mehrere in einem Rahmen). Der Holzfäller trägt 13 bis 15. |
| P223 | `UpdateFletcher` | Holz in der Werkstatt 0, 1, 2, 0, viermal: 2 Holz je Bogen. `punkte_rechnung20.txt`. |
| P224 | `UpdateHunter` | Fleisch +1 je Stück (32 Mal). Ladung bis 18, siehe P131. |
| P226 | `UpdatePitchman` | Pechgrube ohne Vorkommen gesetzt: rund alle 2.380 Takte 1 Pech, finalPitchProduced 4, im Lager 4. `rufen_*.json`. |
| P227 | `UpdateWheatFarmer` | Ladung 2 und 3, wie erwartet ab 2 bei Produktivität 100. Weizen +1 je Stück (21 Mal). |
| P229 | `UpdateAppleFarmer` | Ladung 3 und 4, im Burgenbau wie erwartet ab 3. Apfel +1 je Stück (66 Mal). |
| P230 | `UpdateDairyFarmer` | Käse +1 je Stück (42 Mal). Ladung 4 und 5: Im Speicher steht 4 statt 3 (`UpdateDairyFarmer`, UCP3). |
| P231 | `UpdateMiller` | Weizen -1 (60 Mal), Mehl +1 (61 Mal). |
| P232 | `UpdateBaker` | Mehl -1 (8 Mal), Brot +1 je Stück (36 Mal). Der Bäcker trägt 8 bis 10. |
| P233 | `UpdateBrewer` | Hopfen -1 (8 Mal), Ale +1 (8 Mal). |
| P235 | `UpdateBlacksmith` | Schwert +1 je Stück (8 Mal), Keule 2 Mal. |
| P236 | `UpdateArmorer` | Eisenrüstung +1 (6 Mal), Eisen -1 (9 Mal). |
| P237 | `UpdateTanner` | Lederrüstung +1 je Stück, 2 sind mehrere in einem Rahmen. Der Gerber trägt 2 und 3. |
| P238 | `UpdateEngineer` | Anweisung 20: Zustand 10 ab Takt 584 mit Traglast 1, bei Takt 607 Traglast 0, der Feind verliert ab Takt 637 Leben. Holen aus dem Lager: Pech sinkt im selben Takt um 1 (658, 2.278, 3.636). `punkte_rechnung24.txt`. |
| P239 | `UpdateMinerIronFetcher` | Eisen +1 je Stück (15 Mal). Der Träger trägt 2 und 3. |
| P240 | `UpdatePriest` | Höchstwert 8000. |

## Gemessen (75)

| Punkt | Funktion | Beleg |
|---|---|---|
| P002 | `initializeProjectileVelocities` | Einmal gelesen, Werte in punkte.json. |
| P003 | `buildingHasSpaceForResource` | Einmal gelesen, Werte in punkte.json. |
| P004 | `getBuildingStorageTypeForResourceType` | Einmal gelesen, Werte in punkte.json. |
| P005 | `getBuildingCost` | Einmal gelesen, Werte in punkte.json. |
| P006 | `getBuildingPriority` | Einmal gelesen, Werte in punkte.json. |
| P007 | `updateLordLadyJesterAndGhostUnits` | Tabelle gelesen; Vergleich mit der KI braucht Lauf K. |
| P008 | `initBuildingCosts` | Einmal gelesen, Werte in punkte.json. |
| P009 | `rebuildTileLogicLayerForKeeps` | Einmal gelesen, Werte in punkte.json. |
| P010 | `SetBuildingsEmployeeCountToValue` | Einmal gelesen, Werte in punkte.json. |
| P011 | `determineBuildingEntranceFromKeepArea` | Einmal gelesen, Werte in punkte.json. |
| P012 | `processResourceGain` | Einmal gelesen, Werte in punkte.json. |
| P013 | `SetupSkirmishBalanceAndOrIntensity` | Einmal gelesen, Werte in punkte.json. |
| P015 | `checkRequiredResourcesForBuildingOrPlanToBuy` | Einmal gelesen, Werte in punkte.json. |
| P016 | `isResourceTypeTradeable` | Alle 25 Waren handelbar. Mit dem Marktfenster nicht verglichen. |
| P017 | `getNextGoodFilteringUnallowed` | Reihenfolge 12, 11, 13, 10, 9, 16, 2, 4, 6, 8, 19, 17, 21, 18, 20, 22, 23, 24, 14, 3, Ende -1. |
| P022 | `updateTrader` | Einmal gelesen, Werte in punkte.json. |
| P024 | `GetDifficultyMultipliedValue` | Einmal gelesen, Werte in punkte.json. |
| P025 | `setAICParameters_01` | Satz gelesen, die Liga hat ihn ersetzt. |
| P026 | `setAICParameters_02` | Satz gelesen, die Liga hat ihn ersetzt. |
| P027 | `setAICParameters_03` | aics[3]: 75, 110, 52, 1 statt Grundwert 10, 40, 0, 0. Liga-KI. |
| P028 | `setAICParameters_04` | aics[4]: 42, 130, 100, 2 statt 40, 100, 8, 2. Liga-KI. |
| P029 | `setAICParameters_05` | aics[5]: 0, 60, 40, 2 statt 5, 50, 50, 0. Liga-KI. |
| P030 | `setAICParameters_06` | aics[6]: 5, 0, 1, 1 statt 30, 30, 5, 1. Liga-KI. |
| P031 | `setAICParameters_07` | aics[7]: 39, 8, 9, 1 statt 0, 0, 120, 2. Liga-KI. |
| P032 | `setAICParameters_08` | aics[8]: 60, 0, 52, 1 statt 90, 3, 0, 2. Liga-KI. |
| P033 | `setAICParameters_09` | aics[9]: 84, 0, 17, 2 statt 30, 18, -999, 0. Liga-KI. |
| P034 | `setAICParameters_10` | aics[10]: 80, 107, 39 statt 10, 20, 0. Liga-KI. |
| P035 | `setAICParameters_11` | aics[11]: 74, 70, 190 statt 40, 90, 358. Liga-KI. |
| P036 | `setAICParameters_12` | aics[12]: 8, 1, 2 statt 16, 0, 0. Liga-KI. |
| P037 | `setAICParameters_13` | aics[13]: 20, 2, 1 statt 40, 0, 2. Liga-KI. |
| P038 | `setAICParameters_14` | aics[14]: 58, 100, 0 statt 50, 6, 10. Liga-KI. |
| P041 | `unitIDIsRangedOrArmored` | Aus dem Speicher gelesen (Tabelle 0xb3eb34): UT_E_ARCHER, UT_E_XBOW, UT_E_PIKE, UT_E_SWORD, UT_A_ARCHER, UT_A_FIRETHROWER, UT_A_SWORDSMAN, gleich wie in der Programmdatei: ja. `punkte_rechnung5.txt`. |
| P042 | `getDefensiveTribeForUnit` | 28, 74, 22, 23, 70, 72, 76, 24, 26, 37, 71, 73, 25, 27, 75, 39, 58, 59, 60, 77. |
| P043 | `addUnitToSmallestBehaviourTypeTribe` | Einmal gelesen, Werte in punkte.json. |
| P044 | `aiChoiceAttForceRallyPercentage` | Einmal gelesen, Werte in punkte.json. |
| P045 | `percentageNonMovingTribesGTEAICSpecified` | Einmal gelesen, Werte in punkte.json. |
| P046 | `useAITribe_0x12_toPlaceSiegeTentsAndAssignEngineers` | Ingenieure je Gerät 2, 3, 4, 4, 1, 2; Gerätetypen 39, 40, 58, 59, 60, 77. |
| P047 | `isResourceLargerOrEqualThanMinimumGoodsRequiredAfterTrade` | Einmal gelesen, Werte in punkte.json. |
| P048 | `setInitialAIC` | Tabelle gelesen. Der Vergleich zeigt: Die Liga ersetzt fast alle Sätze, siehe P027 bis P040. |
| P049 | `buyRequiredGoods` | Einmal gelesen, Werte in punkte.json. |
| P050 | `updateTribeLocations` | Einmal gelesen, Werte in punkte.json. |
| P051 | `convertAIVBuildingTypeToCommandBuildingType` | Einmal gelesen, Werte in punkte.json. |
| P054 | `recomputeHeatmaps` | Lauf K: Eisen in 62 Zellen, Summe 595; Felsbrocken in 147 Zellen, Summe 1.729; Öl 0. Mit den Vorkommen der Karte nicht verglichen. |
| P055 | `setTreeStageRelatedValues` | Einmal gelesen, Werte in punkte.json. |
| P057 | `getBuildingSizeIndexMappingData` | Im ersten gelesenen Rahmen (Takt 1342) nur Nullen. Wann das Spiel sie füllt, ist offen. |
| P060 | `useEraserBrush` | Einmal gelesen, Werte in punkte.json. |
| P062 | `applyTreeBrushToLogicalLayer` | Einmal gelesen, Werte in punkte.json. |
| P063 | `eraseAreaWithBrush` | Einmal gelesen, Werte in punkte.json. |
| P064 | `setTerrain` | Einmal gelesen, Werte in punkte.json. |
| P065 | `placeKeep` | Gelesen, gleich wie in der Programmdatei. Türen 2,7 / 3,7 / 4,7 / 7,4 / 7,3 / 7,2 und gegenüber. Lagerstelle 0,8 / 8,0 / 0,-8 / -8,0. Lagerplatz 7,2 / 2,-5 / -5,0 / 0,7. |
| P066 | `placeApplefarm` | Einmal gelesen, Werte in punkte.json. |
| P067 | `createWaterForDrawBridge` | Einmal gelesen, Werte in punkte.json. |
| P068 | `placeTree` | Einmal gelesen, Werte in punkte.json. |
| P069 | `processEntityDamageToBuildingCollateral` | Einmal gelesen, Werte in punkte.json. |
| P072 | `getValueOfTroopType` | Einmal gelesen, Werte in punkte.json. |
| P073 | `initializeOrAdvanceAttackWave` | Einmal gelesen, Werte in punkte.json. |
| P074 | `updateInProgressAttackWave` | Einmal gelesen, Werte in punkte.json. |
| P075 | `executeAttackWaveTargetAssignment` | Einmal gelesen, Werte in punkte.json. |
| P076 | `euroRecruit` | Einmal gelesen, Werte in punkte.json. |
| P077 | `checkUnitHasPropertyBasedOnUnitType` | Einmal gelesen, Werte in punkte.json. |
| P078 | `isComputerManagedNonPeasant` | Einmal gelesen, Werte in punkte.json. |
| P079 | `processUnitAttackOtherUnit` | Einmal gelesen, Werte in punkte.json. |
| P080 | `processEntityDamageToUnit` | Einmal gelesen, Werte in punkte.json. |
| P081 | `UpgradeMapUnitsTo_UnknownVersion1` | Einmal gelesen, Werte in punkte.json. |
| P082 | `UpgradeMapUnitsLordHealthTo_169` | Einmal gelesen, Werte in punkte.json. |
| P083 | `setUnitValues` | Einmal gelesen, Werte in punkte.json. |
| P084 | `acquireShootTarget` | Einmal gelesen, Werte in punkte.json. |
| P085 | `IgniteFireAtMiniTile` | Tabelle gelesen: 0, 0, 1, 0, 2, 0, 3, 0, ... Keine Flamme im Lauf. |
| P123 | `UpdateFireBallistaBuilding` | Lauf K: 2 Zelte der Feuerballiste, Art 54, Fortschritt bis 312, +1 je Takt. |
| P134 | `CountPlayerUnitsByType` | Der Zähler liegt bei 0xb95f70 und wird nur von dieser Anzeige-Funktion gefüllt (`CountPlayerUnitsByType`, sie löscht ihn zuerst). Einträge 67 bis 69 sind 0. Der Vergleich mit einem bekannten Heer ist nicht gefahren. |
| P160 | `QueueChangeTaxes` | Spielbefehl 34 setzt taxesSetting: 2 auf 7, Takt 205 (sonder19_g). Die beiden Felder der Erwartung gehören zum Schieber, der nicht benutzt wurde, sie blieben 0. |
| P167 | `ClickDestroyBuilding` | Befehl 29 mit Param1 50: Rückgabe genau die Hälfte, siehe P130. |
| P175 | `updateSeparateAreaTileMap` | Zähler läuft 1 bis 50. |
| P188 | `aiRecruitUnits` | Lauf K: 12 von 47 neuen Warenwünschen im Wert +0x9c der KI, 15 weitere gehören zum Holz. Die anderen stammen aus anderen Wegen; `euroUnitAcquisitionFailReason` ist nicht mitgelesen, die Lage ist daher nicht eindeutig. |
| P198 | `destroyWall` | Spielbefehl 41 (Feldnummer, 100): Das Mauerstück ist bei Takt 225 weg (sonder19_g). Der Stein ist nicht zu sehen, der Bestand wird aus dem Lager neu gerechnet. |

## Gesehen, nicht nachgerechnet (0)

| Punkt | Funktion | Beleg |
|---|---|---|

## Lage fehlte (0)

| Punkt | Funktion | Beleg |
|---|---|---|

## Offen (0)

| Punkt | Funktion | Beleg |
|---|---|---|
