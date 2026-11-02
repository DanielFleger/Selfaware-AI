# Einzelpunkte Lauf F

Lauf F 02.11.2026 21:42, Instanz 2, Burgenbau, Liga-Balance. Geschrieben von SRE aus den Belegen, Rechnungen in `punkte_rechnen*.py`.

**Worte:** bestätigt und widerlegt heißen: Die Lage kam vor und die Rechnung ist gemacht. gemessen: einmal gelesen, Erwartung war "notieren". gesehen: Die Lage kam vor, das Feld änderte sich, nachgerechnet ist es nicht. Lage fehlte: kommt in Lauf K oder S. offen: von hier aus nicht zu beantworten.

| Urteil | Punkte |
|---|---|
| bestaetigt | 74 |
| widerlegt | 7 |
| gemessen | 67 |
| gesehen | 27 |
| Lage fehlte | 58 |
| offen | 8 |

## Widerlegt (7)

| Punkt | Funktion | Beleg |
|---|---|---|
| P117 | `UpdateCampGround` | vclock folgt nicht der Beliebtheit: Es ist die Zuzugsuhr. Sie läuft von 2000 bis 4000, je Takt um gathering_rate/4 (gemessen +9 bei Beliebtheit 90 bis 94, +10 ab 95). Über 4000 kommt ein Bewohner und sie fällt um 2000. Also 1 Bewohner je 8000/gathering_rate Takte. Kein Platz frei: Sie steht auf 4000. |
| P118 | `processPlacementResourceLossForBuildingType` | 4 Pechgräben kosteten 2 Pech, nicht 1: 16 auf 15 beim ersten, 14 beim dritten. |
| P163 | `SetStorageMarketFailState` | Kauf bei vollem Waffenlager über Befehl 38 wird abgelehnt, das Feld bleibt aber 0. Der Grund wird über diesen Weg nicht gesetzt. |
| P174 | `queueCommand` | commandDelay steht im Einzelspiel auf 0, nicht auf 35. Vom Befehl bis zum Gebäude vergehen gemessen 2 bis 6 Takte. |
| P220 | `UpdateInnkeeper` | Füllstand steigt um 120 je Bier, nicht um 160: Die Liga setzt flagons_per_beer 120. |
| P228 | `UpdateHopsFarmer` | Hopfenbauer trägt im Einzelspiel bis 6, nicht 1. |
| P241 | `UpdateSlinger` | countSlingers2 zählt keine Schleuderer: Es steigt seit Takt 16.541 je Takt um 1 auf 32.261, ohne einen einzigen Schleuderer zu Beginn. Der Name ist falsch. |

## Bestätigt (74)

| Punkt | Funktion | Beleg |
|---|---|---|
| P014 | `resetCountsAndStatistics` | armySize fällt mitten im Takt auf 0 und steht danach wieder auf 18, 384 Wechsel. |
| P018 | `getPreviousGoodsFilteringUnallowed` | 20 Einträge vor -1. |
| P019 | `getBatchBuyPrice` | Tabelle gelesen. Kauf aller Waren kostete -3.420 Gold, Verkauf brachte +1.610: beides stimmt auf das Gold mit der Tabelle (Verkauf: Preis je 5 Stück). |
| P020 | `initPopularityAndRecruitableDefaults` | euroRecruitable und mercRecruitable alle 1, someCount44 = storedPopularityPercent = 9000. |
| P023 | `importTradingCosts` | Kopie gleich der Preistabelle. Die Werte sind die der Liga, nicht die Grundwerte. |
| P039 | `setAICParameters_15` | aics[15]: 10, 4000, 1, gleich dem Grundwert. |
| P040 | `setAICParameters_16` | aics[16]: 50, 12, 37, gleich dem Grundwert. |
| P056 | `setMapSize` | 400, 300, 200, 160, 100, -1: absteigend mit Ende -1. |
| P061 | `placeBarracks` | Beträge 0 oder 5. |
| P087 | `chooseProductionItemType` | Zweiter Bogenmacher fertigt wieder Bogen (17): Das neue Gebäude wird mitgezählt. |
| P088 | `countBuildingsForPlayer` | +0x2C8 war in 20.909 Lesungen je Gebäude immer 0. Der Sonderzustand kam nicht vor. |
| P089 | `findClosestInnBuildingID` | Humpen sinken, Lieferung füllt auf, vor der ersten Lieferung 0. |
| P090 | `recomputeAllFearFactors` | Formel stimmt bei allen 7 Stufenwechseln, Stufen -3 bis 0. |
| P091 | `getResourceSpace` | Kauf bei vollem Waffenlager: Speere 11 und 11, Gold 95.255 und 95.255. |
| P094 | `setupBarracksCampgroundPositions` | Total 72. Ob die Einheiten dort stehen, ist nicht nachgerechnet. |
| P095 | `setupMercenaryPostCampgroundPositions` | structureRelated1 72. Ob die Söldner dort stehen, ist nicht nachgerechnet. |
| P097 | `updateNeededEmployeeCount` | Werte 0 bis 3, je Art die Zahl der Plätze. |
| P098 | `updateAllBuildingsSnoozedState` | sleeping 0, 1, 0 bei beiden Bogenmachern. Die Bestände dabei sind nicht geprüft. |
| P099 | `processBuildingIDsNeedPeasantsQueue` | Offene Plätze 0 am Ende der Bauern, einzeln nicht nachgezählt. |
| P101 | `UpdateWoodcuttersHut` | countWoodcutters 1 bei 1 Hütte. |
| P103 | `UpdateMercenaryPost` | someCount04 15 = Söldnerposten 5 + Kaserne 10, je Takt neu. |
| P104 | `UpdateBarracks` | someCount04 15 = Söldnerposten 5 + Kaserne 10, je Takt neu. |
| P105 | `UpdateFletchersWorkshop` | 1 bis 3: zwei Bogenmacher und ein Lanzenmacher. |
| P106 | `UpdateArmorersWorkshop` | 2: eine Schmiede und ein Rüstungsschmied. |
| P107 | `UpdateBakery` | 1 und 1 bei einer Bäckerei. |
| P108 | `UpdateBrewery` | 1 und 1 bei einer Brauerei. |
| P110 | `UpdateInn` | Im Jahr sinken die Humpen in 263 von 273 Schritten genau alle 36 Takte, aleRate 36. |
| P112 | `UpdateWheatFarm` | Zählt je Takt +1 bis 150, dann auf 0 (63 Rücksprünge im Jahr). |
| P113 | `UpdateHopsFarm` | Zählt je Takt +1 bis 400, dann auf 0 (24 Rücksprünge im Jahr). |
| P114 | `UpdateDairyFarm` | Zähler bis 400, dann 0, 3 Kühe. |
| P115 | `UpdateStables` | 4 Pferde im Abstand von zusammen 3 x 551 Takten. |
| P120 | `applyGateOrDrawbridgeOpenCloseChange` | Offen 11 mit Timer 600 und abwärts, zu Timer -1. Danach wird der Zustand 12, siehe P132. |
| P129 | `setupBuildingData` | currentGameMode 0, cooldownTimer höchstens 400. |
| P130 | `giveBackResourceForDestroyedBuilding` | Mit Param1 50 genau die Hälfte: Bogenmacher (Liga 18 Holz, 100 Gold) gab 9 und 50, Galgen (40 Gold) gab 20. |
| P132 | `UpdateGateHouseSmall` | gateState 11 dann 12, pathLinkageRelated2 0, 2, 1. |
| P133 | `SomePopularityRelatedComputation` | Skala bestätigt: 100 angezeigt = 10000, 50 = 5000 (Spielcode). Mitten in der Wochenrechnung steht kurz bis 10375. |
| P136 | `updateDateAndTime` | Monat höchstens 11, danach Jahr +1. |
| P137 | `computeBuildingCategoryEntryPointAndDestroyEarlierBuilding` | Alte Kaserne 44 ist weg, neue 104. |
| P139 | `getSellResourceAmount` | Code: unter 50 Stück 5, unter 100 Stück 10, unter 200 Stück 20, sonst 50. Gemessen: Holz 106 -20, Essen 60 -10, Stein 43 -5. |
| P141 | `processFoodConsumption` | foodClockSpeed je Kopf bei Ration 0 bis 4: 0; 1,5; 3; 4,5; 6. Bei 40 Leuten und Ration 3 also 180. |
| P142 | `updateAleRate` | 36 ab der ersten Woche, davor 30. |
| P144 | `recomputeReligionBonuses` | religionVar1 0 auf 1 bei der Kapelle. |
| P145 | `calculateTaxIncomeForPlayer` | Formel bestätigt: je Woche Leute x Gold-Tabelle x 2,5 aufs Sammelfeld (Stufe 5: 58 Leute, +101), je Monat ein Zehntel aufs Gold. Die erwarteten 80 sind der Grundwert, die Liga gibt 70. |
| P146 | `calculateTaxBribeExpenseForPlayer` | Dieselbe Formel: Stufe 1, 54 Leute, +67 je Woche. Die erwarteten 80 sind der Grundwert, die Liga gibt 50. |
| P148 | `recountStablesAndHorses` | 4 auf 3 beim Ritter. |
| P149 | `computePopulationStatistics` | Statistik[Index-1] = Leute am Monatswechsel: 12 bei Index 3, 16 bei Index 4 und so weiter. |
| P150 | `updatePopularity` | Stufe 10: -750, Stufe 11: -1000 (Liga). Crowding blieb 0. |
| P151 | `updateTaxing` | 3 von 3 Monaten: Gold +38, +111, +116 = lastMonthsIncomeTax. Bei Bestechung +3 -26 = -23. |
| P152 | `processSingleTimeTick` | weekChanged alle 200 Takte. |
| P153 | `processGameTick` | Steigt im Lauf um 1 je Schritt, in der Pause steht er, nachgelesen. |
| P157 | `CheckIfEnoughGoldForMonk` | Mönch 10: Das ganze Anwerben von 18 Einheiten kostete -850, genau die Summe der Tabelle. |
| P158 | `CheckIfEnoughGoldForTunneler` | Liga 25 statt 30: Das ganze Anwerben kostete -850, genau die Summe der Tabelle. |
| P159 | `GateOpenOrClose` | 11 mit Timer 600, zu mit Timer -1. Danach wird der Zustand 12, siehe P132. |
| P161 | `ChangeTaxes` | Rohwerte 0 bis 11. |
| P162 | `ChangeRations` | Rohwerte 0 bis 4. |
| P164 | `ProcessBuyOrSell` | Alle Waren +5, Gold -3.420 = Summe von getBatchBuyPrice. |
| P165 | `ProcessBuildingSleepUpdate` | Byte 0, 1, 0 beim Ein- und Ausschalten. |
| P168 | `ClickRecruitUnit` | Param0 Einheitentyp, Param1 Gebäude: 18 von 18 Einheiten erschienen. |
| P169 | `ClickBuyOrSell` | Param0 0 ist Kauf, 1 ist Verkauf. |
| P173 | `determineGameTicksToPerform` | 39,9 Takte je Sekunde im vollen Dorf. |
| P190 | `updateAIBehaviour` | Tag 50, Woche 200, Monat 800 Takte. |
| P195 | `countUnfinishedMoatTilesForPlayer` | Der Graben wurde fertig: stage 2, fillProgress 4. |
| P196 | `advanceMoatDigProgress` | fillProgress 0 bis 4, dann stage 2. |
| P202 | `placeWorkshopOrHovel` | Sechs Hütten 0, 1, 2, 3, 4, 5 in Bau-Reihenfolge. |
| P203 | `placeQuarry` | Steinbruch 55 zeigt auf Halde 56, Typ 21. |
| P204 | `createMoatData` | stage 2, fillProgress 4. |
| P206 | `placeWheatfarm` | Genau 36 Felder mit Bit 0x1000000 bei einer Getreidefarm. |
| P207 | `placeHopfarm` | Genau 24 Felder mit Bit 0x2000000 bei einer Hopfenfarm. |
| P208 | `placeDairyfarm` | 0, 1, 2, 3 bei drei Milchviehhöfen. |
| P210 | `recountTotalTroopValue` | 0 auf 224 nach dem Anwerben. |
| P212 | `nonEuroRecruit` | Liga 50 statt 30: Das ganze Anwerben kostete -850, genau die Summe der Tabelle. |
| P217 | `UpdatePeasant` | count bis 2, count_2 18 nach 18 Anwerbungen. |
| P219 | `UpdateHealer` | healerCount 1. |
| P240 | `UpdatePriest` | Höchstwert 8000. |

## Gemessen (67)

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
| P055 | `setTreeStageRelatedValues` | Einmal gelesen, Werte in punkte.json. |
| P057 | `getBuildingSizeIndexMappingData` | Im ersten gelesenen Rahmen (Takt 1342) nur Nullen. Wann das Spiel sie füllt, ist offen. |
| P060 | `useEraserBrush` | Einmal gelesen, Werte in punkte.json. |
| P062 | `applyTreeBrushToLogicalLayer` | Einmal gelesen, Werte in punkte.json. |
| P063 | `eraseAreaWithBrush` | Einmal gelesen, Werte in punkte.json. |
| P064 | `setTerrain` | Einmal gelesen, Werte in punkte.json. |
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
| P167 | `ClickDestroyBuilding` | Befehl 29 mit Param1 50: Rückgabe genau die Hälfte, siehe P130. |
| P175 | `updateSeparateAreaTileMap` | Zähler läuft 1 bis 50. |

## Gesehen, nicht nachgerechnet (27)

| Punkt | Funktion | Beleg |
|---|---|---|
| P093 | `growWheat` | Stufe 121 kommt vor, farmGrowState fehlt in der Feldkarte. |
| P096 | `growHops` | Stufen kommen vor, farmGrowState fehlt in der Feldkarte. |
| P119 | `processWallBuildingLoss` | Je 13 Felder kosteten -1 und -3 Stein, die Zuordnung zu niedrig und hoch ist nicht geklärt. |
| P121 | `UpdateIronMine` | Eisen kommt an (finalIronProduced 23), Zustände nicht nachgerechnet. |
| P122 | `UpdateQuarry` | Stein kommt an, Zustände nicht nachgerechnet. |
| P131 | `UpdateHuntersPost` | Fleisch kommt an, Zustände nicht nachgerechnet. |
| P176 | `updatePathLinkageTileMapRelatedToGates` | pathLinkageRelated2 wechselt, die Bits sind nicht nachgerechnet. |
| P197 | `updateMoatCountdownTimers` | Immer 0, der Abwärtslauf war nicht zu sehen. |
| P218 | `UpdateOx` | Der Ochse lief über Platz 160 hinaus nicht in der Rechnung. Die Liga-Ladung ist 12, nicht 8. |
| P221 | `UpdateChild` | Mütter und Kinder kommen vor, Höchstzahl nicht nachgerechnet. |
| P222 | `UpdateWoodcutter` | Feld ändert sich, nicht nachgerechnet. |
| P223 | `UpdateFletcher` | Feld ändert sich, nicht nachgerechnet. |
| P224 | `UpdateHunter` | Feld ändert sich, nicht nachgerechnet. |
| P225 | `UpdateQuarryWorker` | Feld ändert sich, nicht nachgerechnet. |
| P226 | `UpdatePitchman` | Feld ändert sich, nicht nachgerechnet. |
| P227 | `UpdateWheatFarmer` | Ladung bis 3, Abfolge nicht nachgerechnet. |
| P229 | `UpdateAppleFarmer` | Ladung bis 4, finalFoodProduced steigt, Abfolge nicht nachgerechnet. |
| P230 | `UpdateDairyFarmer` | Feld ändert sich, nicht nachgerechnet. |
| P231 | `UpdateMiller` | Feld ändert sich, nicht nachgerechnet. |
| P232 | `UpdateBaker` | Feld ändert sich, nicht nachgerechnet. |
| P233 | `UpdateBrewer` | Feld ändert sich, nicht nachgerechnet. |
| P234 | `UpdatePoleTurner` | Feld ändert sich, nicht nachgerechnet. |
| P235 | `UpdateBlacksmith` | Feld ändert sich, nicht nachgerechnet. |
| P236 | `UpdateArmorer` | Feld ändert sich, nicht nachgerechnet. |
| P237 | `UpdateTanner` | Feld ändert sich, nicht nachgerechnet. |
| P238 | `UpdateEngineer` | Feld ändert sich, nicht nachgerechnet. |
| P239 | `UpdateMinerIronFetcher` | Feld ändert sich, nicht nachgerechnet. |

## Lage fehlte (58)

| Punkt | Funktion | Beleg |
|---|---|---|
| P001 | `isSameTeam` | Kein Bündnis im Burgenbau. Lauf K. |
| P021 | `initializeGameStateAfterMapLoad` | Gefechtspreise, kein Gefecht. Lauf K. |
| P052 | `recomputeAIAvailableGridTiles` | Keine KI. Lauf K. |
| P053 | `applyAIV` | Keine KI mit Burgvorlage. Lauf K. |
| P054 | `recomputeHeatmaps` | Zellen im Burgenbau leer. Lauf K. |
| P086 | `convertCommandBuildingTypeToBuildingType` | Kein Belagerungsgerät gebaut. Lauf S. |
| P092 | `getPriceForDisbandedUnitType` | Niemand entlassen. |
| P100 | `updateRepairCostAndReturnIfDamaged` | Kein Gebäude beschädigt, die Felder gehören zur Anzeige. |
| P102 | `UpdatePitchRig` | Karte ohne Pechvorkommen. |
| P109 | `UpdateGranary` | Keine Nahrungsart gesperrt. |
| P111 | `UpdateOilSmelter` | Ölbrennerei steht, aber kein Ingenieur wurde zugewiesen. |
| P116 | `UpdateKeepStronghold` | Gold kam direkt, nicht über Startgold. |
| P123 | `UpdateFireBallistaBuilding` | Kein Belagerungszelt. Lauf S. |
| P124 | `UpdateCatapultBuilding` | Kein Belagerungszelt. Lauf S. |
| P125 | `UpdateTrebutchetBuilding` | Kein Belagerungszelt. Lauf S. |
| P126 | `UpdateSiegeTowerBuilding` | Kein Belagerungszelt. Lauf S. |
| P127 | `UpdateBatteringRamBuilding` | Kein Belagerungszelt. Lauf S. |
| P128 | `UpdateShieldBuilding` | Kein Belagerungszelt. Lauf S. |
| P135 | `ComputePlayerPoints1` | Anzeige, nicht gemessen. |
| P138 | `getWallTilesThatCanBeBuilt` | Bauanzeige, nicht gemessen. |
| P140 | `updateFoodTypesInStockForAllPlayers` | Immer 0, 1 oder 4 Sorten. Das Werkzeug fand die 2 zufällig im Warenfeld. |
| P143 | `updateFearFactorProductivity` | Stufe +3 kam nicht vor. Gemessen -1: 116, -2: 132, -3: 148; die Liga hätte bei +3: 76, nicht 70. |
| P147 | `despawnPeasantOrWorker` | Bevölkerung nicht verringert. |
| P154 | `IsEuroUnitRecruitableUnk` | armySizeLimit 10000, nicht erreicht. |
| P155 | `ProcessRecruitUnit` | Heer nicht am Limit. |
| P156 | `CheckIfEnoughGoldForLadderman` | Nicht mit 3 und 4 Gold versucht. Die Liga verlangt 20. |
| P160 | `QueueChangeTaxes` | Schieber nicht benutzt, Steuer kam als Befehl. |
| P166 | `ProcessTowerRepair` | Kein Turm beschädigt. |
| P170 | `ClickUnitStance` | Keine Haltung geändert. |
| P171 | `RemoveTowerSiegeEngine` | Kein Gerät entfernt. |
| P172 | `SetUnitAssemblyPoint` | Kein Sammelpunkt gesetzt. |
| P177 | `algTunnelerFindTarget` | Kein Tunnel. Lauf S. |
| P178 | `isTileInRangeOfKeepRange` | Gründe 22, 3, 5 kamen vor, 0x12 nicht. |
| P179 | `WindowMsgProcessingFunc` | Keine Taste gedrückt, das Tempo kam über das Modul. |
| P180 | `isMapperAvailable` | Karte mit Wild. |
| P181 | `aiUpdateTaxesAndRations` | Keine KI. Das Werkzeug fand die 2 im eigenen Feld. Lauf K. |
| P182 | `aiShouldBuildWoodcutter` | Keine KI. Lauf K. |
| P183 | `planToBuyWhenLowOnResourceAndSnoozeBuildings` | Keine KI. Lauf K. |
| P184 | `addBuildingToTargetableBuildings` | Feld blieb im Burgenbau 0. Lauf K. |
| P185 | `shareGoldAmongTeamMembers` | Kein Verbündeter. Lauf K. |
| P186 | `sellExcessGoods` | Keine KI. Lauf K. |
| P187 | `requestGoods` | Kein Verbündeter. Lauf K. |
| P188 | `aiRecruitUnits` | Keine KI. Lauf K. |
| P189 | `aiBuyAndSellGoods` | Keine KI. Lauf K. |
| P191 | `aiDecideOnNewBuildings` | Keine KI. Lauf K. |
| P192 | `validateWallPlacementAtTile` | Kein Feindgebäude. Lauf K. |
| P193 | `isBuildingPlacementAllowedAtTile` | Nicht versucht, Grenze 200 gelesen. |
| P194 | `countMoatsOwnedByEachPlayer` | moatsOwned blieb trotz Graben 0: Nur updateAIBehaviour ruft die Zählung. Lauf K. |
| P198 | `destroyWall` | Keine Mauer abgerissen. |
| P199 | `validateWallBuildPath` | Kein Feindgebäude. Lauf K. |
| P200 | `placeWalls` | Stein reichte. |
| P201 | `checkBuildingCanBePlacedHere` | Nicht im Gefecht versucht. Lauf K. |
| P205 | `confirmAndQueueDestructionCommand` | Abriss kam als Befehl, nicht über die Abfrage. |
| P209 | `placeBuilding` | Holz reichte. |
| P211 | `setUnitStance` | Keine Haltung geändert. |
| P213 | `ComputeGoodsProduced` | Produktivität 120 gibt es in der Liga-Tabelle nicht. |
| P214 | `findTunnelTarget` | Kein Tunnel. Lauf S. |
| P216 | `spawnUnit` | Kein Katapult. Lauf S. |

## Offen (8)

| Punkt | Funktion | Beleg |
|---|---|---|
| P041 | `unitIDIsRangedOrArmored` | Die Tabelle hat keine Marke in der Feldkarte, nicht gelesen. |
| P058 | `getBuildingSizeForCommandBuildingType` | Die Sprungtabelle liegt im Codebereich, die Aufzeichnung enthält sie nicht. |
| P059 | `updateMacroLayerRelated` | Kein Sumpffeld ausgewählt, nicht nachgerechnet. |
| P065 | `placeKeep` | Tabellen ohne Marke, nicht ausgelesen. |
| P070 | `sortAttackInfoTribeIDArrayBasedOn` | Tabellen ohne Marke, nicht ausgelesen. |
| P071 | `placeSiegeTentsAndAssignEngineers` | Tabellen ohne Marke, nicht ausgelesen. |
| P134 | `CountPlayerUnitsByType` | Der Zähler hat keine Marke in der Feldkarte. |
| P215 | `getWorkerBlockingStateIfStuck` | Rückgabewert, nicht in der Aufzeichnung. |
