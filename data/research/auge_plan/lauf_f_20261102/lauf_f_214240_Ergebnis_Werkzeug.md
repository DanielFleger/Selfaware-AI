# Ergebnis Lauf F

Basis: `lauf_f_20261102_214240`

**Der Lauf ist gültig:** Er konnte die Frage beantworten. Widerlegte Punkte sind Funde, kein Scheitern.

## Gesamtproben

| Probe | Ergebnis | Aussage |
|---|---|---|
| A1 | widerlegt | 655 geaenderte Felder stehen nicht in der Feldliste |
| A1 | widerlegt | 1224 geaenderte Felder stehen nicht in der Feldliste |
| A2 | gemessen | 1482 von 2694 Feldern der Liste haben sich in den ausgewerteten Laeufen nie geaendert; das heisst nur: nicht gesehen |
| A3 | gemessen | Auf Tempo 1000 geht das Tempo vor: 32821 Takte ausgelassen, 13704 Rahmen gemischt. Wie viele Takte je Stufe lesbar sind, zeigt die Tempotreppe |
| A4 | gemessen | Lesen je Takt: Median 0.6 ms, Hoechstwert 15.1 ms; 806.3 Takte/s gesamt, Median-Abstand 1823.5, ohne Lesen 829.0 |
| A3 | bestaetigt | kein Takt fehlt und kein Rahmen ist gemischt in dieser Aufzeichnung (107234 Rahmen) |
| A4 | gemessen | Lesen je Takt: Median 2.5 ms, Hoechstwert 15.3 ms; 39.9 Takte/s gesamt, Median-Abstand 37.5, ohne Lesen 40.1 |
| A4 | bestaetigt | kein Tempoabzug ueber das Messrauschen hinaus in dieser Messung. Stufen [1, 10, 40, 100, 200, 500, 1000]; Takte ausgelassen auf [100, 200, 500, 1000] |
| A7 | bestaetigt | 19208 Lesungen passen zur Tabelle in dieser Aufzeichnung |
| A8 | widerlegt | 6 von 273 Bestandsaenderungen ohne Ursache, zuerst [39806, 'Mehl', 1] |
| A9 | gemessen | 0 Plaetze geaendert, ohne Liste der eigenen Befehle nicht vergleichbar |
| A10 | bestaetigt | 7565 Platzwechsel ohne Verstoss in dieser Aufzeichnung |
| A12 | gemessen | Wechsel am Taktende: {'DAT_CurrentUnitSlotID': 5} |
| A13 | gemessen | Spielart: {'F': {'currentGameMode': 0, 'gameMode_2': 2}} |

## Abschnitte

| Abschnitt | Takte | Sekunden | Takte je Sekunde |
|---|---|---|---|
| grundstock | 1890 | 2.4 | 779.0 |
| bauen | 3930 | 5.6 | 702.7 |
| bauern | 4443 | 5.4 | 824.5 |
| schalten | 4923 | 6.0 | 814.8 |
| ketten | 22237 | 27.0 | 824.5 |
| jahr_tempo40 | 9904 | 242.0 | 40.9 |
| treppe | 15498 | 224.0 | 69.2 |

## Schaltungen ohne Wirkung

- Tor 45 auf 10: {"ist": 12}
- Tor 46 auf 10: {"ist": 12}

## Einzelpunkte

| Urteil | Punkte |
|---|---|
| gemessen | 72 |
| gesehen | 130 |
| nicht gesehen | 12 |
| nicht zuordenbar | 21 |
| zahl passt | 4 |
| zahl weicht ab | 2 |

**Zahl weicht ab (von Hand lesen):** P143 updateFearFactorProductivity, P216 spawnUnit

**Nicht gesehen:** P085 IgniteFireAtMiniTile, P100 updateRepairCostAndReturnIfDamaged, P160 QueueChangeTaxes, P163 SetStorageMarketFailState, P179 WindowMsgProcessingFunc, P184 addBuildingToTargetableBuildings, P187 requestGoods, P188 aiRecruitUnits, P189 aiBuyAndSellGoods, P192 validateWallPlacementAtTile, P194 countMoatsOwnedByEachPlayer, P211 setUnitStance

**Nicht zuordenbar:** P001 isSameTeam, P020 initPopularityAndRecruitableDefaults, P023 importTradingCosts, P041 unitIDIsRangedOrArmored, P042 getDefensiveTribeForUnit, P046 useAITribe_0x12_toPlaceSiegeTentsAndAssignEngineers, P048 setInitialAIC, P057 getBuildingSizeIndexMappingData, P058 getBuildingSizeForCommandBuildingType, P065 placeKeep, P070 sortAttackInfoTribeIDArrayBasedOn, P071 placeSiegeTentsAndAssignEngineers, P088 countBuildingsForPlayer, P131 UpdateHuntersPost, P134 CountPlayerUnitsByType, P147 despawnPeasantOrWorker, P165 ProcessBuildingSleepUpdate, P170 ClickUnitStance, P172 SetUnitAssemblyPoint, P180 isMapperAvailable, P205 confirmAndQueueDestructionCommand

