# Sichtschranke: Ergebnis und Zweifelsfälle (P2)

Erzeugt von `sichtschranke.py` aus `zustand_felder.csv` nach den Regeln in `docs/FAIRNESS.md`.

**3564 Felder.** Eigene Daten: unbekannt 986, erlaubt 971, technik 875, verboten 732. Fremde Daten: verboten 2206, technik 643, erlaubt 520, schaetzen 195.

- **Sicher eingeordnet:** 2578
- **Bedeutung unbekannt** (Ghidra-Platzhalter, im fairen Spiel ungenutzt, bis benannt): 986
- **Feinarbeit** (benannt, aber noch ohne passende Regel; im fairen Spiel vorerst ungenutzt): 0 in 
- **Fragen an Daniel und Krari:** 0 Felder in 0 Gruppen. Je Gruppe reicht eine Entscheidung, sie gilt dann für alle Felder darin.

## Feinarbeit (alle Grundsatzfragen entschieden, Daniel 08.11.2026)

| Bereich | Regel | Felder | eigen | fremd | Beispiele |
|---|---|---|---|---|---|

## Korrekturen nach der Feldliste (B-168, Daniel 08.11.2026)

279 Felder, bei denen die Muster allein eine andere Marke ergeben. Marke als eigen / fremd.

| Regel | Muster sagten | jetzt | Felder | Beispiele |
|---|---|---|---|---|
| R3/F5 Innenleben der Gegner-KI | erlaubt / schaetzen | verboten / verboten | 69 | `playerDataArray[].attackAssaultDelayRelatedValue`, `playerDataArray[].attackTicker`, `playerDataArray[].attackedPlayerID`, `playerDataArray[].availableBoulderGridTiles`, `playerDataArray[].availableIronGridTiles` |
| Bedeutung unbekannt (Ghidra-Platzhalter) | erlaubt / schaetzen | unbekannt / verboten | 51 | `playerDataArray[].count`, `playerDataArray[].count_2`, `playerDataArray[].counter`, `playerDataArray[].someCount02`, `playerDataArray[].someCount03` |
| Bedeutung unbekannt (Ghidra-Platzhalter) | erlaubt / verboten | unbekannt / verboten | 25 | `buildings[].field_0x2a5`, `buildings[].field_0x314`, `buildings[].flag1`, `buildings[].flag2`, `buildings[].someUID` |
| sichtbar: Ort, Sterben, Bild (B-168) | unbekannt / verboten | erlaubt / erlaubt | 14 | `buildings[].playerColorUnk`, `buildings[].surfaceAreaUnk`, `buildings[].terrainHeightUnk`, `playerDataArray[].jesterIDUnk`, `playerDataArray[].ladyIDUnk` |
| R3/F5 Innenleben der Gegner-KI | erlaubt / verboten | verboten / verboten | 13 | `buildings[].attackWave`, `tribes[].archerRelated`, `tribes[].archerRelated2`, `tribes[].attackInfo_someCounter1`, `tribes[].attackWave` |
| R3/F5 Innenleben der Gegner-KI | unbekannt / verboten | verboten / verboten | 10 | `playerDataArray[].attackedPlayerID_2Unk`, `playerDataArray[].harassingSiegeEnginesCountUnk`, `playerDataArray[].hasMarketUnk`, `playerDataArray[].highestLoadedQuarryUnk`, `playerDataArray[].monkTribeIDUnk` |
| Bedeutung unbekannt (Ghidra-Platzhalter) | erlaubt / erlaubt | unbekannt / verboten | 9 | `SEC_Section1080`, `SEC_Section1081`, `SEC_Section1089[]`, `SEC_Section1090`, `buildings[].someX` |
| Laufzeiger und Bild der Engine (B-168) | unbekannt / verboten | technik / technik | 9 | `DAT_CounterFoodWarningInterval`, `entityArray[].colorUnk`, `entityArray[].graphicRotationUnk`, `entityArray[].hasDoneEffectUnk`, `entityArray[].someCounter_OR_hitGround` |
| F4 fremde Wirtschaft nur schaetzen (B-168) | unbekannt / verboten | erlaubt / schaetzen | 9 | `playerDataArray[].averagePopulationGrowthUnk`, `playerDataArray[].blessedPeopleCountUnk`, `playerDataArray[].fearFactorProductivityUnk`, `playerDataArray[].nonInteractiveCitizenCountUnk`, `playerDataArray[].ownsCathedralUnk` |
| R3 Ziel oder Weg: eigen bekannt, fremd verborgen (B-168) | unbekannt / verboten | erlaubt / verboten | 9 | `units[].destinationX_2Unk`, `units[].destinationY_2Unk`, `units[].digTileY__OR__countLifeCycleEngineersSentToManSiegeEngine`, `units[].lastEncounteredEnemyUnitIDUnk`, `units[].movementType_OR_targetUnitID` |
| R3 Sammelpunkte: eigen bekannt, fremd verborgen (B-168) | erlaubt / erlaubt | erlaubt / verboten | 8 | `playerDataArray[].barracksAssemblyPoints[].x`, `playerDataArray[].barracksAssemblyPoints[].y`, `playerDataArray[].cathedralAssemblyPointX`, `playerDataArray[].cathedralAssemblyPointY`, `playerDataArray[].engineersAssemblyPoints[].x` |
| R4 innerer Zaehler: eigen erlaubt (F8), fremd nicht sichtbar (B-168) | erlaubt / erlaubt | erlaubt / verboten | 6 | `playerDataArray[].keepEnclosementRelatedCountdown`, `units[].banked`, `units[].blessedAmount`, `units[].horseArcherShootCheckInterval`, `units[].horseArcherShootingVariation` |
| F10 fremde Trupps nicht wissbar (B-168) | unbekannt / verboten | erlaubt / verboten | 6 | `tribes[].isRallyingUnk`, `tribes[].percentageAttackingUnk`, `tribes[].percentageDyingUnk`, `tribes[].percentageMovingUnk`, `tribes[].percentageShootingUnk` |
| R4 innerer Zaehler: eigen erlaubt (F8), fremd nicht sichtbar (B-168) | unbekannt / verboten | erlaubt / verboten | 5 | `buildings[].idleTimerUnk`, `units[].assassinsMicroDistanceToEnemyUnk`, `units[].friendlyFireCounterUnk`, `units[].idleCounterUnk`, `units[].unitSpeedMatchingRelatedUnk` |
| Statistik: das Spiel zaehlt hier nur den eigenen Platz (processUnitLossStatistic) (B-168) | unbekannt / verboten | erlaubt / erlaubt | 5 | `DAT_CurrentPlayerUnitLosses`, `DAT_DestroyedBuildingsCountHistory`, `DAT_DestroyedBuildingsCountHistory[]`, `DAT_UnitValueLossesPerEnemyPlayer`, `DAT_UnitValueLossesPerEnemyPlayer[]` |
| R3/F5 Innenleben der Gegner-KI | erlaubt / erlaubt | verboten / verboten | 5 | `playerDataArray[].defWallPatrolRallyTimeHits`, `playerDataArray[].defWallPatrolRallyTimeWaitCounter`, `playerDataArray[].outerPatrolRallyDelayTracker`, `playerDataArray[].relativeStrengthOfTeamComparedToEnemy`, `playerDataArray[].totalTeamTroopValue` |
| Buendnisanfragen: eigene bekannt, fremde verborgen (B-168) | unbekannt / verboten | erlaubt / verboten | 5 | `playerDataArray[].playerID_askerUnk`, `playerDataArray[].requestStateUnk`, `playerDataArray[].requestedAttackTargetUnk`, `playerDataArray[].requestedGoodsArray1Unk[]`, `playerDataArray[].requestedGoodsArray2Unk[]` |
| gemerkter oder kommender Zustand: fremd nicht sichtbar (R3) (B-168) | erlaubt / erlaubt | erlaubt / verboten | 5 | `units[].cachedState`, `units[].state_2`, `units[].state_3`, `units[].unitTypeToChangeInto`, `units[].unitType_3` |
| Spielregel je Art (B-168) | unbekannt / verboten | erlaubt / erlaubt | 3 | `units[].enemyNoticeFrequencyUnk`, `units[].moveableUnk`, `units[].someUnitStat2_meleeDamageUnk` |
| eigene Daten erlaubt (F8), fremdes Innenleben nicht sichtbar (B-168) | unbekannt / verboten | erlaubt / verboten | 3 | `units[].horseOriginStableIDUnk`, `units[].horseOriginStablesBuildingIndexUnk`, `units[].isSelectable_OR_matchTime` |
| sichtbar: Geschoss, Flug (B-168) | unbekannt / verboten | erlaubt / erlaubt | 2 | `entityArray[].speedUnk`, `entityArray[].velocityUnk` |
| Zeit und Friedenszeit (B-168) | unbekannt / verboten | erlaubt / erlaubt | 2 | `mapAndTime.noRushTicksLeftUnk`, `mapAndTime.totalGameTicksUnk` |
| F4 fremde Wirtschaft nur schaetzen (B-168) | erlaubt / erlaubt | erlaubt / schaetzen | 2 | `playerDataArray[].granaryIsAlmostFilledUp`, `playerDataArray[].marketGold` |
| F1 Zufallsstand | erlaubt / erlaubt | verboten / verboten | 1 | `buildings[].fireRelatedRNG1` |
| aus Sichtbarem selbst rechnen, fremd nicht lesen (B-168) | erlaubt / erlaubt | erlaubt / verboten | 1 | `playerDataArray[].closestEnemyDistanceToTheLord` |
| Laufzeiger und Bild der Engine (B-168) | erlaubt / erlaubt | technik / technik | 1 | `playerDataArray[].rallySearchOffset` |
| Auswahl eines anderen Spielers ist nicht sichtbar (B-168) | erlaubt / erlaubt | erlaubt / verboten | 1 | `units[].isSelected` |
